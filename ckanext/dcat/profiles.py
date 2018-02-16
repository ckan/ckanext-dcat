import datetime
import json

from dateutil.parser import parse as parse_date

from ckantoolkit import config

import rdflib
from rdflib import URIRef, BNode, Literal
from rdflib.namespace import Namespace, RDF, XSD, SKOS, RDFS

from geomet import wkt, InvalidGeoJSONException

from ckan.model.license import LicenseRegister
from ckan.plugins import toolkit
from ckan.lib.munge import munge_tag

from ckanext.dcat.utils import resource_uri, publisher_uri_from_dataset_dict, DCAT_EXPOSE_SUBCATALOGS, DCAT_CLEAN_TAGS

DCT = Namespace("http://purl.org/dc/terms/")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
ADMS = Namespace("http://www.w3.org/ns/adms#")
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
SCHEMA = Namespace('http://schema.org/')
TIME = Namespace('http://www.w3.org/2006/time')
LOCN = Namespace('http://www.w3.org/ns/locn#')
GSP = Namespace('http://www.opengis.net/ont/geosparql#')
OWL = Namespace('http://www.w3.org/2002/07/owl#')
SPDX = Namespace('http://spdx.org/rdf/terms#')

GEOJSON_IMT = 'https://www.iana.org/assignments/media-types/application/vnd.geo+json'

namespaces = {
    'dct': DCT,
    'dcat': DCAT,
    'adms': ADMS,
    'vcard': VCARD,
    'foaf': FOAF,
    'schema': SCHEMA,
    'time': TIME,
    'skos': SKOS,
    'locn': LOCN,
    'gsp': GSP,
    'owl': OWL,
}


class RDFProfile(object):
    '''Base class with helper methods for implementing RDF parsing profiles

       This class should not be used directly, but rather extended to create
       custom profiles
    '''

    def __init__(self, graph, compatibility_mode=False):
        '''Class constructor

        Graph is an rdflib.Graph instance.

        In compatibility mode, some fields are modified to maintain
        compatibility with previous versions of the ckanext-dcat parsers
        (eg adding the `dcat_` prefix or storing comma separated lists instead
        of JSON dumps).
        '''

        self.g = graph

        self.compatibility_mode = compatibility_mode

        # Cache for mappings of licenses URL/title to ID built when needed in
        # _license().
        self._licenceregister_cache = None

    def _datasets(self):
        '''
        Generator that returns all DCAT datasets on the graph

        Yields rdflib.term.URIRef objects that can be used on graph lookups
        and queries
        '''
        for dataset in self.g.subjects(RDF.type, DCAT.Dataset):
            yield dataset

    def _distributions(self, dataset):
        '''
        Generator that returns all DCAT distributions on a particular dataset

        Yields rdflib.term.URIRef objects that can be used on graph lookups
        and queries
        '''
        for distribution in self.g.objects(dataset, DCAT.distribution):
            yield distribution

    def _object(self, subject, predicate):
        '''
        Helper for returning the first object for this subject and predicate

        Both subject and predicate must be rdflib URIRef or BNode objects

        Returns an rdflib reference (URIRef or BNode) or None if not found
        '''
        for _object in self.g.objects(subject, predicate):
            return _object
        return None

    def _object_value(self, subject, predicate):
        '''
        Given a subject and a predicate, returns the value of the object

        Both subject and predicate must be rdflib URIRef or BNode objects

        If found, the unicode representation is returned, else an empty string
        '''
        for o in self.g.objects(subject, predicate):
            return unicode(o)
        return ''

    def _object_value_int(self, subject, predicate):
        '''
        Given a subject and a predicate, returns the value of the object as an
        integer

        Both subject and predicate must be rdflib URIRef or BNode objects

        If the value can not be parsed as intger, returns None
        '''
        object_value = self._object_value(subject, predicate)
        if object_value:
            try:
                return int(object_value)
            except ValueError:
                pass
        return None

    def _object_value_list(self, subject, predicate):
        '''
        Given a subject and a predicate, returns a list with all the values of
        the objects

        Both subject and predicate must be rdflib URIRef or BNode  objects

        If no values found, returns an empty string
        '''
        return [unicode(o) for o in self.g.objects(subject, predicate)]

    def _time_interval(self, subject, predicate):
        '''
        Returns the start and end date for a time interval object

        Both subject and predicate must be rdflib URIRef or BNode objects

        It checks for time intervals defined with both schema.org startDate &
        endDate and W3C Time hasBeginning & hasEnd.

        Note that partial dates will be expanded to the first month / day
        value, eg '1904' -> '1904-01-01'.

        Returns a tuple with the start and end date values, both of which
        can be None if not found
        '''

        start_date = end_date = None

        for interval in self.g.objects(subject, predicate):
            # Fist try the schema.org way
            start_date = self._object_value(interval, SCHEMA.startDate)
            end_date = self._object_value(interval, SCHEMA.endDate)

            if start_date or end_date:
                return start_date, end_date

            # If no luck, try the w3 time way
            start_nodes = [t for t in self.g.objects(interval,
                                                     TIME.hasBeginning)]
            end_nodes = [t for t in self.g.objects(interval,
                                                   TIME.hasEnd)]
            if start_nodes:
                start_date = self._object_value(start_nodes[0],
                                                TIME.inXSDDateTime)
            if end_nodes:
                end_date = self._object_value(end_nodes[0],
                                              TIME.inXSDDateTime)

        return start_date, end_date

    def _publisher(self, subject, predicate):
        '''
        Returns a dict with details about a dct:publisher entity, a foaf:Agent

        Both subject and predicate must be rdflib URIRef or BNode objects

        Examples:

        <dct:publisher>
            <foaf:Organization rdf:about="http://orgs.vocab.org/some-org">
                <foaf:name>Publishing Organization for dataset 1</foaf:name>
                <foaf:mbox>contact@some.org</foaf:mbox>
                <foaf:homepage>http://some.org</foaf:homepage>
                <dct:type rdf:resource="http://purl.org/adms/publishertype/NonProfitOrganisation"/>
            </foaf:Organization>
        </dct:publisher>

        {
            'uri': 'http://orgs.vocab.org/some-org',
            'name': 'Publishing Organization for dataset 1',
            'email': 'contact@some.org',
            'url': 'http://some.org',
            'type': 'http://purl.org/adms/publishertype/NonProfitOrganisation',
        }

        <dct:publisher rdf:resource="http://publications.europa.eu/resource/authority/corporate-body/EURCOU" />

        {
            'uri': 'http://publications.europa.eu/resource/authority/corporate-body/EURCOU'
        }

        Returns keys for uri, name, email, url and type with the values set to
        an empty string if they could not be found
        '''

        publisher = {}

        for agent in self.g.objects(subject, predicate):

            publisher['uri'] = (unicode(agent) if isinstance(agent,
                                rdflib.term.URIRef) else '')

            publisher['name'] = self._object_value(agent, FOAF.name)

            publisher['email'] = self._object_value(agent, FOAF.mbox)

            publisher['url'] = self._object_value(agent, FOAF.homepage)

            publisher['type'] = self._object_value(agent, DCT.type)

        return publisher

    def _contact_details(self, subject, predicate):
        '''
        Returns a dict with details about a vcard expression

        Both subject and predicate must be rdflib URIRef or BNode objects

        Returns keys for uri, name and email with the values set to
        an empty string if they could not be found
        '''

        contact = {}

        for agent in self.g.objects(subject, predicate):

            contact['uri'] = (unicode(agent) if isinstance(agent,
                              rdflib.term.URIRef) else '')

            contact['name'] = self._object_value(agent, VCARD.fn)

            contact['email'] = self._object_value(agent, VCARD.hasEmail)

        return contact

    def _spatial(self, subject, predicate):
        '''
        Returns a dict with details about the spatial location

        Both subject and predicate must be rdflib URIRef or BNode objects

        Returns keys for uri, text or geom with the values set to
        None if they could not be found.

        Geometries are always returned in GeoJSON. If only WKT is provided,
        it will be transformed to GeoJSON.

        Check the notes on the README for the supported formats:

        https://github.com/ckan/ckanext-dcat/#rdf-dcat-to-ckan-dataset-mapping
        '''

        uri = None
        text = None
        geom = None

        for spatial in self.g.objects(subject, predicate):

            if isinstance(spatial, URIRef):
                uri = unicode(spatial)

            if isinstance(spatial, Literal):
                text = unicode(spatial)

            if (spatial, RDF.type, DCT.Location) in self.g:
                for geometry in self.g.objects(spatial, LOCN.geometry):
                    if (geometry.datatype == URIRef(GEOJSON_IMT) or
                            not geometry.datatype):
                        try:
                            json.loads(unicode(geometry))
                            geom = unicode(geometry)
                        except (ValueError, TypeError):
                            pass
                    if not geom and geometry.datatype == GSP.wktLiteral:
                        try:
                            geom = json.dumps(wkt.loads(unicode(geometry)))
                        except (ValueError, TypeError):
                            pass
                for label in self.g.objects(spatial, SKOS.prefLabel):
                    text = unicode(label)
                for label in self.g.objects(spatial, RDFS.label):
                    text = unicode(label)

        return {
            'uri': uri,
            'text': text,
            'geom': geom,
        }

    def _license(self, dataset_ref):
        '''
        Returns a license identifier if one of the distributions license is
        found in CKAN license registry. If no distribution's license matches,
        an empty string is returned.

        The first distribution with a license found in the registry is used so
        that if distributions have different licenses we'll only get the first
        one.
        '''
        if self._licenceregister_cache is not None:
            license_uri2id, license_title2id = self._licenceregister_cache
        else:
            license_uri2id = {}
            license_title2id = {}
            for license_id, license in LicenseRegister().items():
                license_uri2id[license.url] = license_id
                license_title2id[license.title] = license_id
            self._licenceregister_cache = license_uri2id, license_title2id

        for distribution in self._distributions(dataset_ref):
            # If distribution has a license, attach it to the dataset
            license = self._object(distribution, DCT.license)
            if license:
                # Try to find a matching license comparing URIs, then titles
                license_id = license_uri2id.get(license.toPython())
                if not license_id:
                    license_id = license_title2id.get(
                        self._object_value(license, DCT.title))
                if license_id:
                    return license_id
        return ''

    def _distribution_format(self, distribution, normalize_ckan_format=True):
        '''
        Returns the Internet Media Type and format label for a distribution

        Given a reference (URIRef or BNode) to a dcat:Distribution, it will
        try to extract the media type (previously knowm as MIME type), eg
        `text/csv`, and the format label, eg `CSV`

        Values for the media type will be checked in the following order:

        1. literal value of dcat:mediaType
        2. literal value of dct:format if it contains a '/' character
        3. value of dct:format if it is an instance of dct:IMT, eg:

            <dct:format>
                <dct:IMT rdf:value="text/html" rdfs:label="HTML"/>
            </dct:format>

        Values for the label will be checked in the following order:

        1. literal value of dct:format if it not contains a '/' character
        2. label of dct:format if it is an instance of dct:IMT (see above)

        If `normalize_ckan_format` is True and using CKAN>=2.3, the label will
        be tried to match against the standard list of formats that is included
        with CKAN core
        (https://github.com/ckan/ckan/blob/master/ckan/config/resource_formats.json)
        This allows for instance to populate the CKAN resource format field
        with a format that view plugins, etc will understand (`csv`, `xml`,
        etc.)

        Return a tuple with the media type and the label, both set to None if
        they couldn't be found.
        '''

        imt = None
        label = None

        imt = self._object_value(distribution, DCAT.mediaType)

        _format = self._object(distribution, DCT['format'])
        if isinstance(_format, Literal):
            if not imt and '/' in _format:
                imt = unicode(_format)
            else:
                label = unicode(_format)
        elif isinstance(_format, (BNode, URIRef)):
            if self._object(_format, RDF.type) == DCT.IMT:
                if not imt:
                    imt = unicode(self.g.value(_format, default=None))
                label = unicode(self.g.label(_format, default=None))

        if ((imt or label) and normalize_ckan_format and
                toolkit.check_ckan_version(min_version='2.3')):
            import ckan.config
            from ckan.lib import helpers

            format_registry = helpers.resource_formats()

            if imt in format_registry:
                label = format_registry[imt][1]
            elif label in format_registry:
                label = format_registry[label][1]

        return imt, label

    def _get_dict_value(self, _dict, key, default=None):
        '''
        Returns the value for the given key on a CKAN dict

        By default a key on the root level is checked. If not found, extras
        are checked, both with the key provided and with `dcat_` prepended to
        support legacy fields.

        If not found, returns the default value, which defaults to None
        '''

        if key in _dict:
            return _dict[key]

        for extra in _dict.get('extras', []):
            if extra['key'] == key or extra['key'] == 'dcat_' + key:
                return extra['value']

        return default

    def _get_dataset_value(self, dataset_dict, key, default=None):
        '''
        Returns the value for the given key on a CKAN dict

        Check `_get_dict_value` for details
        '''
        return self._get_dict_value(dataset_dict, key, default)

    def _get_resource_value(self, resource_dict, key, default=None):
        '''
        Returns the value for the given key on a CKAN dict

        Check `_get_dict_value` for details
        '''
        return self._get_dict_value(resource_dict, key, default)

    def _add_date_triples_from_dict(self, _dict, subject, items):
        self._add_triples_from_dict(_dict, subject, items,
                                    date_value=True)

    def _add_list_triples_from_dict(self, _dict, subject, items):
        self._add_triples_from_dict(_dict, subject, items,
                                    list_value=True)

    def _add_triples_from_dict(self, _dict, subject, items,
                               list_value=False,
                               date_value=False):
        for item in items:
            key, predicate, fallbacks, _type = item
            self._add_triple_from_dict(_dict, subject, predicate, key,
                                       fallbacks=fallbacks,
                                       list_value=list_value,
                                       date_value=date_value,
                                       _type=_type)

    def _add_triple_from_dict(self, _dict, subject, predicate, key,
                              fallbacks=None,
                              list_value=False,
                              date_value=False,
                              _type=Literal):
        '''
        Adds a new triple to the graph with the provided parameters

        The subject and predicate of the triple are passed as the relevant
        RDFLib objects (URIRef or BNode). The object is always a literal value,
        which is extracted from the dict using the provided key (see
        `_get_dict_value`). If the value for the key is not found, then
        additional fallback keys are checked.

        If `list_value` or `date_value` are True, then the value is treated as
        a list or a date respectively (see `_add_list_triple` and
        `_add_date_triple` for details.
        '''
        value = self._get_dict_value(_dict, key)
        if not value and fallbacks:
            for fallback in fallbacks:
                value = self._get_dict_value(_dict, fallback)
                if value:
                    break

        if value and list_value:
            self._add_list_triple(subject, predicate, value, _type)
        elif value and date_value:
            self._add_date_triple(subject, predicate, value, _type)
        elif value:
            # Normal text value
            self.g.add((subject, predicate, _type(value)))

    def _add_list_triple(self, subject, predicate, value, _type=Literal):
        '''
        Adds as many triples to the graph as values

        Values are literal strings, if `value` is a list, one for each
        item. If `value` is a string there is an attempt to split it using
        commas, to support legacy fields.
        '''
        items = []
        # List of values
        if isinstance(value, list):
            items = value
        elif isinstance(value, basestring):
            try:
                # JSON list
                items = json.loads(value)
                if isinstance(items, ((int, long, float, complex))):
                    items = [items]
            except ValueError:
                if ',' in value:
                    # Comma-separated list
                    items = value.split(',')
                else:
                    # Normal text value
                    items = [value]

        for item in items:
            self.g.add((subject, predicate, _type(item)))

    def _add_date_triple(self, subject, predicate, value, _type=Literal):
        '''
        Adds a new triple with a date object

        Dates are parsed using dateutil, and if the date obtained is correct,
        added to the graph as an XSD.dateTime value.

        If there are parsing errors, the literal string value is added.
        '''
        if not value:
            return
        try:
            default_datetime = datetime.datetime(1, 1, 1, 0, 0, 0)
            _date = parse_date(value, default=default_datetime)

            self.g.add((subject, predicate, _type(_date.isoformat(),
                                                  datatype=XSD.dateTime)))
        except ValueError:
            self.g.add((subject, predicate, _type(value)))

    def _last_catalog_modification(self):
        '''
        Returns the date and time the catalog was last modified

        To be more precise, the most recent value for `metadata_modified` on a
        dataset.

        Returns a dateTime string in ISO format, or None if it could not be
        found.
        '''
        context = {
            'user': toolkit.get_action('get_site_user')(
                {'ignore_auth': True})['name']
        }
        result = toolkit.get_action('package_search')(context, {
            'sort': 'metadata_modified desc',
            'rows': 1,
        })
        if result and result.get('results'):
            return result['results'][0]['metadata_modified']
        return None

    def _get_source_catalog(self, dataset_ref):
        '''
        Returns Catalog reference that is source for this dataset. 

        Catalog referenced in dct:hasPart is returned, 
        if dataset is linked there, otherwise main catalog 
        will be returned.

        This will not be used if ckanext.dcat.expose_subcatalogs
        configuration option is set to False.
        '''
        if not toolkit.asbool(config.get(DCAT_EXPOSE_SUBCATALOGS, False)):
            return
        catalogs = set(self.g.subjects(DCAT.dataset, dataset_ref))
        root = self._get_root_catalog_ref()
        try:
            catalogs.remove(root)
        except KeyError:
            pass
        assert len(catalogs) in (0, 1,), "len %s" %catalogs
        if catalogs:
            return catalogs.pop()
        return root
    
    def _get_root_catalog_ref(self):
        roots = list(self.g.subjects(DCT.hasPart))
        if not roots:
            roots = list(self.g.subjects(RDF.type, DCAT.Catalog))
        return roots[0]

    # Public methods for profiles to implement

    def parse_dataset(self, dataset_dict, dataset_ref):
        '''
        Creates a CKAN dataset dict from the RDF graph

        The `dataset_dict` is passed to all the loaded profiles before being
        yielded, so it can be further modified by each one of them.
        `dataset_ref` is an rdflib URIRef object
        that can be used to reference the dataset when querying the graph.

        Returns a dataset dict that can be passed to eg `package_create`
        or `package_update`
        '''
        return dataset_dict

    def _extract_catalog_dict(self, catalog_ref):
        '''
        Returns list of key/value dictionaries with catalog
        '''

        out = []
        sources = (('source_catalog_title', DCT.title,),
                   ('source_catalog_description', DCT.description,),
                   ('source_catalog_homepage', FOAF.homepage,),
                   ('source_catalog_language', DCT.language,),
                   ('source_catalog_modified', DCT.modified,),)

        for key, predicate in sources:
            val = self._object_value(catalog_ref, predicate)
            if val:
                out.append({'key': key, 'value': val})

        out.append({'key': 'source_catalog_publisher', 'value': json.dumps(self._publisher(catalog_ref, DCT.publisher))})
        return out

    def graph_from_catalog(self, catalog_dict, catalog_ref):
        '''
        Creates an RDF graph for the whole catalog (site)

        The class RDFLib graph (accessible via `self.g`) should be updated on
        this method

        `catalog_dict` is a dict that can contain literal values for the
        dcat:Catalog class like `title`, `homepage`, etc. `catalog_ref` is an
        rdflib URIRef object that must be used to reference the catalog when
        working with the graph.
        '''
        pass

    def graph_from_dataset(self, dataset_dict, dataset_ref):
        '''
        Given a CKAN dataset dict, creates an RDF graph

        The class RDFLib graph (accessible via `self.g`) should be updated on
        this method

        `dataset_dict` is a dict with the dataset metadata like the one
        returned by `package_show`. `dataset_ref` is an rdflib URIRef object
        that must be used to reference the dataset when working with the graph.
        '''
        pass


class EuropeanDCATAPProfile(RDFProfile):
    '''
    An RDF profile based on the DCAT-AP for data portals in Europe

    More information and specification:

    https://joinup.ec.europa.eu/asset/dcat_application_profile

    '''

    def parse_dataset(self, dataset_dict, dataset_ref):

        dataset_dict['extras'] = []
        dataset_dict['resources'] = []

        # Basic fields
        for key, predicate in (
                ('title', DCT.title),
                ('notes', DCT.description),
                ('url', DCAT.landingPage),
                ('version', OWL.versionInfo),
                ):
            value = self._object_value(dataset_ref, predicate)
            if value:
                dataset_dict[key] = value

        if not dataset_dict.get('version'):
            # adms:version was supported on the first version of the DCAT-AP
            value = self._object_value(dataset_ref, ADMS.version)
            if value:
                dataset_dict['version'] = value

        # Tags
        keywords = self._object_value_list(dataset_ref, DCAT.keyword) or []
        # Split keywords with commas
        keywords_with_commas = [k for k in keywords if ',' in k]
        for keyword in keywords_with_commas:
            keywords.remove(keyword)
            keywords.extend([k.strip() for k in keyword.split(',')])

        # replace munge_tag to noop if there's no need to clean tags
        do_clean = toolkit.asbool(config.get(DCAT_CLEAN_TAGS, False))
        tags_val = [munge_tag(tag) if do_clean else tag for tag in keywords]
        tags = [{'name': tag} for tag in tags_val]
        dataset_dict['tags'] = tags

        # Extras

        #  Simple values
        for key, predicate in (
                ('issued', DCT.issued),
                ('modified', DCT.modified),
                ('identifier', DCT.identifier),
                ('version_notes', ADMS.versionNotes),
                ('frequency', DCT.accrualPeriodicity),
                ('access_rights', DCT.accessRights),
                ('provenance', DCT.provenance),
                ('dcat_type', DCT.type),
                ):
            value = self._object_value(dataset_ref, predicate)
            if value:
                dataset_dict['extras'].append({'key': key, 'value': value})

        #  Lists
        for key, predicate, in (
                ('language', DCT.language),
                ('theme', DCAT.theme),
                ('alternate_identifier', ADMS.identifier),
                ('conforms_to', DCT.conformsTo),
                ('documentation', FOAF.page),
                ('related_resource', DCT.relation),
                ('has_version', DCT.hasVersion),
                ('is_version_of', DCT.isVersionOf),
                ('source', DCT.source),
                ('sample', ADMS.sample),
                ):
            values = self._object_value_list(dataset_ref, predicate)
            if values:
                dataset_dict['extras'].append({'key': key,
                                               'value': json.dumps(values)})

        # Contact details
        contact = self._contact_details(dataset_ref, DCAT.contactPoint)
        if not contact:
            # adms:contactPoint was supported on the first version of DCAT-AP
            contact = self._contact_details(dataset_ref, ADMS.contactPoint)

        if contact:
            for key in ('uri', 'name', 'email'):
                if contact.get(key):
                    dataset_dict['extras'].append(
                        {'key': 'contact_{0}'.format(key),
                         'value': contact.get(key)})

        # Publisher
        publisher = self._publisher(dataset_ref, DCT.publisher)
        for key in ('uri', 'name', 'email', 'url', 'type'):
            if publisher.get(key):
                dataset_dict['extras'].append(
                    {'key': 'publisher_{0}'.format(key),
                     'value': publisher.get(key)})

        # Temporal
        start, end = self._time_interval(dataset_ref, DCT.temporal)
        if start:
            dataset_dict['extras'].append(
                {'key': 'temporal_start', 'value': start})
        if end:
            dataset_dict['extras'].append(
                {'key': 'temporal_end', 'value': end})

        # Spatial
        spatial = self._spatial(dataset_ref, DCT.spatial)
        for key in ('uri', 'text', 'geom'):
            if spatial.get(key):
                dataset_dict['extras'].append(
                    {'key': 'spatial_{0}'.format(key) if key != 'geom' else 'spatial',
                     'value': spatial.get(key)})

        # Dataset URI (explicitly show the missing ones)
        dataset_uri = (unicode(dataset_ref)
                       if isinstance(dataset_ref, rdflib.term.URIRef)
                       else '')
        dataset_dict['extras'].append({'key': 'uri', 'value': dataset_uri})

        # License
        if 'license_id' not in dataset_dict:
            dataset_dict['license_id'] = self._license(dataset_ref)

        # Source Catalog
        if toolkit.asbool(config.get(DCAT_EXPOSE_SUBCATALOGS, False)):
            catalog_src = self._get_source_catalog(dataset_ref)
            if catalog_src is not None:
                src_data = self._extract_catalog_dict(catalog_src)
                dataset_dict['extras'].extend(src_data)

        # Resources
        for distribution in self._distributions(dataset_ref):

            resource_dict = {}

            #  Simple values
            for key, predicate in (
                    ('name', DCT.title),
                    ('description', DCT.description),
                    ('download_url', DCAT.downloadURL),
                    ('issued', DCT.issued),
                    ('modified', DCT.modified),
                    ('status', ADMS.status),
                    ('rights', DCT.rights),
                    ('license', DCT.license),
                    ):
                value = self._object_value(distribution, predicate)
                if value:
                    resource_dict[key] = value

            resource_dict['url'] = (self._object_value(distribution,
                                                       DCAT.accessURL) or
                                    self._object_value(distribution,
                                                       DCAT.downloadURL))
            #  Lists
            for key, predicate in (
                    ('language', DCT.language),
                    ('documentation', FOAF.page),
                    ('conforms_to', DCT.conformsTo),
                    ):
                values = self._object_value_list(distribution, predicate)
                if values:
                    resource_dict[key] = json.dumps(values)

            # Format and media type
            normalize_ckan_format = config.get(
                'ckanext.dcat.normalize_ckan_format', True)
            imt, label = self._distribution_format(distribution,
                                                   normalize_ckan_format)

            if imt:
                resource_dict['mimetype'] = imt

            if label:
                resource_dict['format'] = label
            elif imt:
                resource_dict['format'] = imt

            # Size
            size = self._object_value_int(distribution, DCAT.byteSize)
            if size is not None:
                resource_dict['size'] = size

            # Checksum
            for checksum in self.g.objects(distribution, SPDX.checksum):
                algorithm = self._object_value(checksum, SPDX.algorithm)
                checksum_value = self._object_value(checksum, SPDX.checksumValue)
                if algorithm:
                    resource_dict['hash_algorithm'] = algorithm
                if checksum_value:
                    resource_dict['hash'] = checksum_value

            # Distribution URI (explicitly show the missing ones)
            resource_dict['uri'] = (unicode(distribution)
                                    if isinstance(distribution,
                                                  rdflib.term.URIRef)
                                    else '')

            dataset_dict['resources'].append(resource_dict)

        if self.compatibility_mode:
            # Tweak the resulting dict to make it compatible with previous
            # versions of the ckanext-dcat parsers
            for extra in dataset_dict['extras']:
                if extra['key'] in ('issued', 'modified', 'publisher_name',
                                    'publisher_email',):

                    extra['key'] = 'dcat_' + extra['key']

                if extra['key'] == 'language':
                    extra['value'] = ','.join(
                        sorted(json.loads(extra['value'])))

        return dataset_dict

    def graph_from_dataset(self, dataset_dict, dataset_ref):

        g = self.g

        for prefix, namespace in namespaces.iteritems():
            g.bind(prefix, namespace)

        g.add((dataset_ref, RDF.type, DCAT.Dataset))

        # Basic fields
        items = [
            ('title', DCT.title, None, Literal),
            ('notes', DCT.description, None, Literal),
            ('url', DCAT.landingPage, None, URIRef),
            ('identifier', DCT.identifier, ['guid', 'id'], Literal),
            ('version', OWL.versionInfo, ['dcat_version'], Literal),
            ('version_notes', ADMS.versionNotes, None, Literal),
            ('frequency', DCT.accrualPeriodicity, None, Literal),
            ('access_rights', DCT.accessRights, None, Literal),
            ('dcat_type', DCT.type, None, Literal),
            ('provenance', DCT.provenance, None, Literal),
        ]
        self._add_triples_from_dict(dataset_dict, dataset_ref, items)

        # Tags
        for tag in dataset_dict.get('tags', []):
            g.add((dataset_ref, DCAT.keyword, Literal(tag['name'])))

        # Dates
        items = [
            ('issued', DCT.issued, ['metadata_created'], Literal),
            ('modified', DCT.modified, ['metadata_modified'], Literal),
        ]
        self._add_date_triples_from_dict(dataset_dict, dataset_ref, items)

        #  Lists
        items = [
            ('language', DCT.language, None, Literal),
            ('theme', DCAT.theme, None, URIRef),
            ('conforms_to', DCT.conformsTo, None, Literal),
            ('alternate_identifier', ADMS.identifier, None, Literal),
            ('documentation', FOAF.page, None, Literal),
            ('related_resource', DCT.relation, None, Literal),
            ('has_version', DCT.hasVersion, None, Literal),
            ('is_version_of', DCT.isVersionOf, None, Literal),
            ('source', DCT.source, None, Literal),
            ('sample', ADMS.sample, None, Literal),
        ]
        self._add_list_triples_from_dict(dataset_dict, dataset_ref, items)

        # Contact details
        if any([
            self._get_dataset_value(dataset_dict, 'contact_uri'),
            self._get_dataset_value(dataset_dict, 'contact_name'),
            self._get_dataset_value(dataset_dict, 'contact_email'),
            self._get_dataset_value(dataset_dict, 'maintainer'),
            self._get_dataset_value(dataset_dict, 'maintainer_email'),
            self._get_dataset_value(dataset_dict, 'author'),
            self._get_dataset_value(dataset_dict, 'author_email'),
        ]):

            contact_uri = self._get_dataset_value(dataset_dict, 'contact_uri')
            if contact_uri:
                contact_details = URIRef(contact_uri)
            else:
                contact_details = BNode()

            g.add((contact_details, RDF.type, VCARD.Organization))
            g.add((dataset_ref, DCAT.contactPoint, contact_details))

            items = [
                ('contact_name', VCARD.fn, ['maintainer', 'author'], Literal),
                ('contact_email', VCARD.hasEmail, ['maintainer_email',
                                                   'author_email'], Literal),
            ]

            self._add_triples_from_dict(dataset_dict, contact_details, items)

        # Publisher
        if any([
            self._get_dataset_value(dataset_dict, 'publisher_uri'),
            self._get_dataset_value(dataset_dict, 'publisher_name'),
            dataset_dict.get('organization'),
        ]):

            publisher_uri = publisher_uri_from_dataset_dict(dataset_dict)
            if publisher_uri:
                publisher_details = URIRef(publisher_uri)
            else:
                # No organization nor publisher_uri
                publisher_details = BNode()

            g.add((publisher_details, RDF.type, FOAF.Organization))
            g.add((dataset_ref, DCT.publisher, publisher_details))

            publisher_name = self._get_dataset_value(dataset_dict, 'publisher_name')
            if not publisher_name and dataset_dict.get('organization'):
                publisher_name = dataset_dict['organization']['title']

            g.add((publisher_details, FOAF.name, Literal(publisher_name)))
            # TODO: It would make sense to fallback these to organization
            # fields but they are not in the default schema and the
            # `organization` object in the dataset_dict does not include
            # custom fields
            items = [
                ('publisher_email', FOAF.mbox, None, Literal),
                ('publisher_url', FOAF.homepage, None, URIRef),
                ('publisher_type', DCT.type, None, Literal),
            ]

            self._add_triples_from_dict(dataset_dict, publisher_details, items)

        # Temporal
        start = self._get_dataset_value(dataset_dict, 'temporal_start')
        end = self._get_dataset_value(dataset_dict, 'temporal_end')
        if start or end:
            temporal_extent = BNode()

            g.add((temporal_extent, RDF.type, DCT.PeriodOfTime))
            if start:
                self._add_date_triple(temporal_extent, SCHEMA.startDate, start)
            if end:
                self._add_date_triple(temporal_extent, SCHEMA.endDate, end)
            g.add((dataset_ref, DCT.temporal, temporal_extent))

        # Spatial
        spatial_uri = self._get_dataset_value(dataset_dict, 'spatial_uri')
        spatial_text = self._get_dataset_value(dataset_dict, 'spatial_text')
        spatial_geom = self._get_dataset_value(dataset_dict, 'spatial')

        if spatial_uri or spatial_text or spatial_geom:
            if spatial_uri:
                spatial_ref = URIRef(spatial_uri)
            else:
                spatial_ref = BNode()

            g.add((spatial_ref, RDF.type, DCT.Location))
            g.add((dataset_ref, DCT.spatial, spatial_ref))

            if spatial_text:
                g.add((spatial_ref, SKOS.prefLabel, Literal(spatial_text)))

            if spatial_geom:
                # GeoJSON
                g.add((spatial_ref,
                       LOCN.geometry,
                       Literal(spatial_geom, datatype=GEOJSON_IMT)))
                # WKT, because GeoDCAT-AP says so
                try:
                    g.add((spatial_ref,
                           LOCN.geometry,
                           Literal(wkt.dumps(json.loads(spatial_geom),
                                             decimals=4),
                                   datatype=GSP.wktLiteral)))
                except (TypeError, ValueError, InvalidGeoJSONException):
                    pass

        # Resources
        for resource_dict in dataset_dict.get('resources', []):

            distribution = URIRef(resource_uri(resource_dict))

            g.add((dataset_ref, DCAT.distribution, distribution))

            g.add((distribution, RDF.type, DCAT.Distribution))

            #  Simple values
            items = [
                ('name', DCT.title, None, Literal),
                ('description', DCT.description, None, Literal),
                ('status', ADMS.status, None, Literal),
                ('rights', DCT.rights, None, Literal),
                ('license', DCT.license, None, Literal),
            ]

            self._add_triples_from_dict(resource_dict, distribution, items)

            #  Lists
            items = [
                ('documentation', FOAF.page, None, Literal),
                ('language', DCT.language, None, Literal),
                ('conforms_to', DCT.conformsTo, None, Literal),
            ]
            self._add_list_triples_from_dict(resource_dict, distribution, items)

            # Format
            if '/' in resource_dict.get('format', ''):
                g.add((distribution, DCAT.mediaType,
                       Literal(resource_dict['format'])))
            else:
                if resource_dict.get('format'):
                    g.add((distribution, DCT['format'],
                           Literal(resource_dict['format'])))

                if resource_dict.get('mimetype'):
                    g.add((distribution, DCAT.mediaType,
                           Literal(resource_dict['mimetype'])))

            # URL
            url = resource_dict.get('url')
            download_url = resource_dict.get('download_url')
            if download_url:
                g.add((distribution, DCAT.downloadURL, URIRef(download_url)))
            if (url and not download_url) or (url and url != download_url):
                g.add((distribution, DCAT.accessURL, URIRef(url)))

            # Dates
            items = [
                ('issued', DCT.issued, None, Literal),
                ('modified', DCT.modified, None, Literal),
            ]

            self._add_date_triples_from_dict(resource_dict, distribution, items)

            # Numbers
            if resource_dict.get('size'):
                try:
                    g.add((distribution, DCAT.byteSize,
                           Literal(float(resource_dict['size']),
                                   datatype=XSD.decimal)))
                except (ValueError, TypeError):
                    g.add((distribution, DCAT.byteSize,
                           Literal(resource_dict['size'])))
            # Checksum
            if resource_dict.get('hash'):
                checksum = BNode()
                g.add((checksum, SPDX.checksumValue,
                       Literal(resource_dict['hash'],
                               datatype=XSD.hexBinary)))

                if resource_dict.get('hash_algorithm'):
                    if resource_dict['hash_algorithm'].startswith('http'):
                        g.add((checksum, SPDX.algorithm,
                               URIRef(resource_dict['hash_algorithm'])))
                    else:
                        g.add((checksum, SPDX.algorithm,
                               Literal(resource_dict['hash_algorithm'])))
                g.add((distribution, SPDX.checksum, checksum))

    def graph_from_catalog(self, catalog_dict, catalog_ref):

        g = self.g

        for prefix, namespace in namespaces.iteritems():
            g.bind(prefix, namespace)

        g.add((catalog_ref, RDF.type, DCAT.Catalog))

        # Basic fields
        items = [
            ('title', DCT.title, config.get('ckan.site_title'), Literal),
            ('description', DCT.description, config.get('ckan.site_description'), Literal),
            ('homepage', FOAF.homepage, config.get('ckan.site_url'), URIRef),
            ('language', DCT.language, config.get('ckan.locale_default', 'en'), Literal),
        ]
        for item in items:
            key, predicate, fallback, _type = item
            if catalog_dict:
                value = catalog_dict.get(key, fallback)
            else:
                value = fallback
            if value:
                g.add((catalog_ref, predicate, _type(value)))

        # Dates
        modified = self._last_catalog_modification()
        if modified:
            self._add_date_triple(catalog_ref, DCT.modified, modified)


class SchemaOrgProfile(RDFProfile):
    '''
    An RDF profile based on the schema.org Dataset

    More information and specification:

    http://schema.org/Dataset

    Mapping between schema.org Dataset and DCAT:

    https://www.w3.org/wiki/WebSchemas/Datasets
    '''
    def graph_from_dataset(self, dataset_dict, dataset_ref):

        g = self.g

        # Namespaces
        self._bind_namespaces()

        g.add((dataset_ref, RDF.type, SCHEMA.Dataset))

        # Basic fields
        self._basic_fields_graph(dataset_ref, dataset_dict)

        # Tags
        self._tags_graph(dataset_ref, dataset_dict)

        #  Lists
        self._list_fields_graph(dataset_ref, dataset_dict)

        # Publisher
        self._publisher_graph(dataset_ref, dataset_dict)

        # Temporal
        self._temporal_graph(dataset_ref, dataset_dict)

        # Spatial
        self._spatial_graph(dataset_ref, dataset_dict)

        # Resources
        self._resources_graph(dataset_ref, dataset_dict)

    def _add_date_triple(self, subject, predicate, value, _type=Literal):
        '''
        Adds a new triple with a date object

        Dates are parsed using dateutil, and if the date obtained is correct,
        added to the graph as an SCHEMA.DateTime value.

        If there are parsing errors, the literal string value is added.
        '''
        if not value:
            return
        try:
            default_datetime = datetime.datetime(1, 1, 1, 0, 0, 0)
            _date = parse_date(value, default=default_datetime)

            self.g.add((subject, predicate, _type(_date.isoformat())))
        except ValueError:
            self.g.add((subject, predicate, _type(value)))

    def _bind_namespaces(self):
        self.g.bind('schema', namespaces['schema'])

    def _basic_fields_graph(self, dataset_ref, dataset_dict):
        items = [
            ('identifier', SCHEMA.identifier, None, Literal),
            ('title', SCHEMA.name, None, Literal),
            ('notes', SCHEMA.description, None, Literal),
            ('version', SCHEMA.version, ['dcat_version'], Literal),
            ('issued', SCHEMA.datePublished, ['metadata_created'], Literal),
            ('modified', SCHEMA.dateModified, ['metadata_modified'], Literal),
        ]
        self._add_triples_from_dict(dataset_dict, dataset_ref, items)

        items = [
            ('issued', SCHEMA.datePublished, ['metadata_created'], Literal),
            ('modified', SCHEMA.dateModified, ['metadata_modified'], Literal),
        ]

        self._add_date_triples_from_dict(dataset_dict, dataset_ref, items)

    def _tags_graph(self, dataset_ref, dataset_dict):
        for tag in dataset_dict.get('tags', []):
            self.g.add((dataset_ref, SCHEMA.keywords, Literal(tag['name'])))

    def _list_fields_graph(self, dataset_ref, dataset_dict):
        items = [
            ('language', SCHEMA.inLanguage, None, Literal),
            ('theme', SCHEMA.about, None, URIRef),
        ]
        self._add_list_triples_from_dict(dataset_dict, dataset_ref, items)

    def _publisher_graph(self, dataset_ref, dataset_dict):
        if any([
            self._get_dataset_value(dataset_dict, 'publisher_uri'),
            self._get_dataset_value(dataset_dict, 'publisher_name'),
            dataset_dict.get('organization'),
        ]):

            publisher_uri = publisher_uri_from_dataset_dict(dataset_dict)
            if publisher_uri:
                publisher_details = URIRef(publisher_uri)
            else:
                # No organization nor publisher_uri
                publisher_details = BNode()

            self.g.add((publisher_details, RDF.type, SCHEMA.Organization))
            self.g.add((dataset_ref, SCHEMA.publisher, publisher_details))


            publisher_name = self._get_dataset_value(dataset_dict, 'publisher_name')
            if not publisher_name and dataset_dict.get('organization'):
                publisher_name = dataset_dict['organization']['title']
            self.g.add((publisher_details, SCHEMA.name, Literal(publisher_name)))

            contact_point = BNode()
            self.g.add((contact_point, RDF.type, SCHEMA.ContactPoint))
            self.g.add((publisher_details, SCHEMA.contactPoint, contact_point))

            self.g.add((contact_point, SCHEMA.contactType, Literal('customer service')))

            publisher_url = self._get_dataset_value(dataset_dict, 'publisher_url')
            if not publisher_url and dataset_dict.get('organization'):
                publisher_url = dataset_dict['organization'].get('url') or config.get('ckan.site_url')

            self.g.add((contact_point, SCHEMA.url, Literal(publisher_url)))
            items = [
                ('publisher_email', SCHEMA.email, ['contact_email', 'maintainer_email', 'author_email'], Literal),
                ('publisher_name', SCHEMA.name, ['contact_name', 'maintainer', 'author'], Literal),
            ]

            self._add_triples_from_dict(dataset_dict, contact_point, items)

    def _temporal_graph(self, dataset_ref, dataset_dict):
        start = self._get_dataset_value(dataset_dict, 'temporal_start')
        end = self._get_dataset_value(dataset_dict, 'temporal_end')
        if start or end:
            if start and end:
                self.g.add((dataset_ref, SCHEMA.temporalCoverage, Literal('%s/%s' % (start, end))))
            elif start:
                self._add_date_triple(dataset_ref, SCHEMA.temporalCoverage, start)
            elif end:
                self._add_date_triple(dataset_ref, SCHEMA.temporalCoverage, end)

    def _spatial_graph(self, dataset_ref, dataset_dict):
        spatial_uri = self._get_dataset_value(dataset_dict, 'spatial_uri')
        spatial_text = self._get_dataset_value(dataset_dict, 'spatial_text')
        spatial_geom = self._get_dataset_value(dataset_dict, 'spatial')

        if spatial_uri or spatial_text or spatial_geom:
            if spatial_uri:
                spatial_ref = URIRef(spatial_uri)
            else:
                spatial_ref = BNode()

            self.g.add((spatial_ref, RDF.type, SCHEMA.Place))
            self.g.add((dataset_ref, SCHEMA.spatialCoverage, spatial_ref))

            if spatial_text:
                self.g.add((spatial_ref, SCHEMA.description, Literal(spatial_text)))

            if spatial_geom:
                geo_shape = BNode()
                self.g.add((geo_shape, RDF.type, SCHEMA.GeoShape))
                self.g.add((spatial_ref, SCHEMA.geo, geo_shape))

                # the spatial_geom typically contains GeoJSON
                self.g.add((geo_shape,
                       SCHEMA.polygon,
                       Literal(spatial_geom)))

    def _resources_graph(self, dataset_ref, dataset_dict):
        g = self.g
        for resource_dict in dataset_dict.get('resources', []):
            distribution = URIRef(resource_uri(resource_dict))
            g.add((dataset_ref, SCHEMA.distribution, distribution))
            g.add((distribution, RDF.type, SCHEMA.DataDownload))

            self._distribution_graph(distribution, resource_dict)

    def _distribution_graph(self, distribution, resource_dict):
        #  Simple values
        self._distribution_basic_fields_graph(distribution, resource_dict)

        # Lists
        self._distribution_list_fields_graph(distribution, resource_dict)

        # Format
        self._distribution_format_graph(distribution, resource_dict)

        # URL
        self._distribution_url_graph(distribution, resource_dict)

        # Numbers
        self._distribution_numbers_graph(distribution, resource_dict)

    def _distribution_basic_fields_graph(self, distribution, resource_dict):
        items = [
            ('name', SCHEMA.name, None, Literal),
            ('description', SCHEMA.description, None, Literal),
            ('license', SCHEMA.license, ['rights'], Literal),
        ]

        self._add_triples_from_dict(resource_dict, distribution, items)

        items = [
            ('issued', SCHEMA.datePublished, None, Literal),
            ('modified', SCHEMA.dateModified, None, Literal),
        ]

        self._add_date_triples_from_dict(resource_dict, distribution, items)

    def _distribution_list_fields_graph(self, distribution, resource_dict):
        items = [
            ('language', SCHEMA.inLanguage, None, Literal),
        ]
        self._add_list_triples_from_dict(resource_dict, distribution, items)

    def _distribution_format_graph(self, distribution, resource_dict):
        if '/' in resource_dict.get('format', ''):
            self.g.add((distribution, SCHEMA.fileType,
                   Literal(resource_dict['format'])))
            self.g.add((distribution, SCHEMA.encodingFormat,
                   Literal(resource_dict['format'])))
        else:
            if resource_dict.get('format'):
                self.g.add((distribution, SCHEMA.encodingFormat,
                       Literal(resource_dict['format'])))

            if resource_dict.get('mimetype'):
                self.g.add((distribution, SCHEMA.fileType,
                       Literal(resource_dict['mimetype'])))

    def _distribution_url_graph(self, distribution, resource_dict):
        url = resource_dict.get('url')
        download_url = resource_dict.get('download_url')
        if download_url:
            self.g.add((distribution, SCHEMA.contentUrl, Literal(download_url)))
        if (url and not download_url) or (url and url != download_url):
            self.g.add((distribution, SCHEMA.url, Literal(url)))

    def _distribution_numbers_graph(self, distribution, resource_dict):
        if resource_dict.get('size'):
            self.g.add((distribution, SCHEMA.contentSize, Literal(resource_dict['size'])))
