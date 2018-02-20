import sys
import argparse
import xml
import json
from pkg_resources import iter_entry_points

from pylons import config

import rdflib
import rdflib.parser
from rdflib import URIRef, BNode, Literal
from rdflib.namespace import Namespace, RDF

import ckan.plugins as p

from ckanext.dcat.utils import catalog_uri, dataset_uri, url_to_rdflib_format, DCAT_EXPOSE_SUBCATALOGS
from ckanext.dcat.profiles import DCAT, DCT, FOAF


HYDRA = Namespace('http://www.w3.org/ns/hydra/core#')
DCAT = Namespace("http://www.w3.org/ns/dcat#")

RDF_PROFILES_ENTRY_POINT_GROUP = 'ckan.rdf.profiles'
RDF_PROFILES_CONFIG_OPTION = 'ckanext.dcat.rdf.profiles'
COMPAT_MODE_CONFIG_OPTION = 'ckanext.dcat.compatibility_mode'

DEFAULT_RDF_PROFILES = ['euro_dcat_ap']


class RDFParserException(Exception):
    pass


class RDFProfileException(Exception):
    pass


class RDFProcessor(object):

    def __init__(self, profiles=None, compatibility_mode=False):
        '''
        Creates a parser or serializer instance

        You can optionally pass a list of profiles to be used.

        In compatibility mode, some fields are modified to maintain
        compatibility with previous versions of the ckanext-dcat parsers
        (eg adding the `dcat_` prefix or storing comma separated lists instead
        of JSON dumps).

        '''
        if not profiles:
            profiles = config.get(RDF_PROFILES_CONFIG_OPTION, None)
            if profiles:
                profiles = profiles.split(' ')
            else:
                profiles = DEFAULT_RDF_PROFILES
        self._profiles = self._load_profiles(profiles)
        if not self._profiles:
            raise RDFProfileException(
                'No suitable RDF profiles could be loaded')

        if not compatibility_mode:
            compatibility_mode = p.toolkit.asbool(
                config.get(COMPAT_MODE_CONFIG_OPTION, False))
        self.compatibility_mode = compatibility_mode

        self.g = rdflib.Graph()

    def _load_profiles(self, profile_names):
        '''
        Loads the specified RDF parser profiles

        These are registered on ``entry_points`` in setup.py, under the
        ``[ckan.rdf.profiles]`` group.
        '''
        profiles = []
        loaded_profiles_names = []

        for profile_name in profile_names:
            for profile in iter_entry_points(
                    group=RDF_PROFILES_ENTRY_POINT_GROUP,
                    name=profile_name):
                profile_class = profile.load()
                # Set a reference to the profile name
                profile_class.name = profile.name
                profiles.append(profile_class)
                loaded_profiles_names.append(profile.name)
                break

        unknown_profiles = set(profile_names) - set(loaded_profiles_names)
        if unknown_profiles:
            raise RDFProfileException(
                'Unknown RDF profiles: {0}'.format(
                    ', '.join(sorted(unknown_profiles))))

        return profiles


class RDFParser(RDFProcessor):
    '''
    An RDF to CKAN parser based on rdflib

    Supports different profiles which are the ones that will generate
    CKAN dicts from the RDF graph.
    '''

    def _datasets(self):
        '''
        Generator that returns all DCAT datasets on the graph

        Yields rdflib.term.URIRef objects that can be used on graph lookups
        and queries
        '''
        for dataset in self.g.subjects(RDF.type, DCAT.Dataset):
            yield dataset

    def next_page(self):
        '''
        Returns the URL of the next page or None if there is no next page
        '''
        for pagination_node in self.g.subjects(RDF.type, HYDRA.PagedCollection):
            for o in self.g.objects(pagination_node, HYDRA.nextPage):
                return unicode(o)
        return None


    def parse(self, data, _format=None):
        '''
        Parses and RDF graph serialization and into the class graph

        It calls the rdflib parse function with the provided data and format.

        Data is a string with the serialized RDF graph (eg RDF/XML, N3
        ... ). By default RF/XML is expected. The optional parameter _format
        can be used to tell rdflib otherwise.

        It raises a ``RDFParserException`` if there was some error during
        the parsing.

        Returns nothing.
        '''

        _format = url_to_rdflib_format(_format)
        if not _format or _format == 'pretty-xml':
            _format = 'xml'

        try:
            self.g.parse(data=data, format=_format)
        # Apparently there is no single way of catching exceptions from all
        # rdflib parsers at once, so if you use a new one and the parsing
        # exceptions are not cached, add them here.
        # PluginException indicates that an unknown format was passed.
        except (SyntaxError, xml.sax.SAXParseException,
                rdflib.plugin.PluginException, TypeError), e:

            raise RDFParserException(e)

    def supported_formats(self):
        '''
        Returns a list of all formats supported by this processor.
        '''
        return sorted([plugin.name
                       for plugin
                       in rdflib.plugin.plugins(kind=rdflib.parser.Parser)])

    def datasets(self):
        '''
        Generator that returns CKAN datasets parsed from the RDF graph

        Each dataset is passed to all the loaded profiles before being
        yielded, so it can be further modified by each one of them.

        Returns a dataset dict that can be passed to eg `package_create`
        or `package_update`
        '''
        for dataset_ref in self._datasets():
            dataset_dict = {}
            for profile_class in self._profiles:
                profile = profile_class(self.g, self.compatibility_mode)
                profile.parse_dataset(dataset_dict, dataset_ref)

            yield dataset_dict


class RDFSerializer(RDFProcessor):
    '''
    A CKAN to RDF serializer based on rdflib

    Supports different profiles which are the ones that will generate
    the RDF graph.
    '''
    def _add_pagination_triples(self, paging_info):
        '''
        Adds pagination triples to the graph using the paging info provided

        The pagination info dict can have the following keys:
        `count`, `items_per_page`, `current`, `first`, `last`, `next` or
        `previous`.

        It uses members from the hydra:PagedCollection class

        http://www.hydra-cg.com/spec/latest/core/

        Returns the reference to the pagination info, which will be an rdflib
        URIRef or BNode object.
        '''
        self.g.bind('hydra', HYDRA)

        if paging_info.get('current'):
            pagination_ref = URIRef(paging_info['current'])
        else:
            pagination_ref = BNode()
        self.g.add((pagination_ref, RDF.type, HYDRA.PagedCollection))

        items = [
            ('next', HYDRA.nextPage),
            ('previous', HYDRA.previousPage),
            ('first', HYDRA.firstPage),
            ('last', HYDRA.lastPage),
            ('count', HYDRA.totalItems),
            ('items_per_page', HYDRA.itemsPerPage),
        ]
        for item in items:
            key, predicate = item
            if paging_info.get(key):
                self.g.add((pagination_ref, predicate,
                            Literal(paging_info[key])))

        return pagination_ref

    def graph_from_dataset(self, dataset_dict):
        '''
        Given a CKAN dataset dict, creates a graph using the loaded profiles

        The class RDFLib graph (accessible via `serializer.g`) will be updated
        by the loaded profiles.

        Returns the reference to the dataset, which will be an rdflib URIRef.
        '''

        uri_value = dataset_dict.get('uri')
        if not uri_value:
            for extra in dataset_dict.get('extras', []):
                if extra['key'] == 'uri':
                    uri_value = extra['value']
                    break

        dataset_ref = URIRef(dataset_uri(dataset_dict))

        for profile_class in self._profiles:
            profile = profile_class(self.g, self.compatibility_mode)
            profile.graph_from_dataset(dataset_dict, dataset_ref)

        return dataset_ref

    def graph_from_catalog(self, catalog_dict=None):
        '''
        Creates a graph for the catalog (CKAN site) using the loaded profiles

        The class RDFLib graph (accessible via `serializer.g`) will be updated
        by the loaded profiles.

        Returns the reference to the catalog, which will be an rdflib URIRef.
        '''

        catalog_ref = URIRef(catalog_uri())

        for profile_class in self._profiles:
            profile = profile_class(self.g, self.compatibility_mode)
            profile.graph_from_catalog(catalog_dict, catalog_ref)

        return catalog_ref

    def serialize_dataset(self, dataset_dict, _format='xml'):
        '''
        Given a CKAN dataset dict, returns an RDF serialization

        The serialization format can be defined using the `_format` parameter.
        It must be one of the ones supported by RDFLib, defaults to `xml`.

        Returns a string with the serialized dataset
        '''

        self.graph_from_dataset(dataset_dict)

        if not _format:
            _format = 'xml'
        _format = url_to_rdflib_format(_format)

        if _format == 'json-ld':
            output = self.g.serialize(format=_format, auto_compact=True)
        else:
            output = self.g.serialize(format=_format)

        return output

    def serialize_catalog(self, catalog_dict=None, dataset_dicts=None,
                          _format='xml', pagination_info=None):
        '''
        Returns an RDF serialization of the whole catalog

        `catalog_dict` can contain literal values for the dcat:Catalog class
        like `title`, `homepage`, etc. If not provided these would get default
        values from the CKAN config (eg from `ckan.site_title`).

        If passed a list of CKAN dataset dicts, these will be also serializsed
        as part of the catalog.
        **Note:** There is no hard limit on the number of datasets at this
        level, this should be handled upstream.

        The serialization format can be defined using the `_format` parameter.
        It must be one of the ones supported by RDFLib, defaults to `xml`.

        `pagination_info` may be a dict containing keys describing the results
        pagination. See the `_add_pagination_triples()` method for details.

        Returns a string with the serialized catalog
        '''

        catalog_ref = self.graph_from_catalog(catalog_dict)
        if dataset_dicts:
            for dataset_dict in dataset_dicts:
                dataset_ref = self.graph_from_dataset(dataset_dict)

                cat_ref = self._add_source_catalog(catalog_ref, dataset_dict, dataset_ref)
                if not cat_ref:
                    self.g.add((catalog_ref, DCAT.dataset, dataset_ref))

        if pagination_info:
            self._add_pagination_triples(pagination_info)

        if not _format:
            _format = 'xml'
        _format = url_to_rdflib_format(_format)
        output = self.g.serialize(format=_format)

        return output

    def _add_source_catalog(self, root_catalog_ref, dataset_dict, dataset_ref):
        if not p.toolkit.asbool(config.get(DCAT_EXPOSE_SUBCATALOGS, False)):
            return

        def _get_from_extra(key):
            for ex in dataset_dict.get('extras', []):
                if ex['key'] == key:
                    return ex['value']

        source_uri = _get_from_extra('source_catalog_homepage')
        if not source_uri:
            return
        
        g = self.g
        catalog_ref = URIRef(source_uri)

        # we may have multiple subcatalogs, let's check if this one has been already added
        if (root_catalog_ref, DCT.hasPart, catalog_ref) not in g:

            g.add((root_catalog_ref, DCT.hasPart, catalog_ref))
            g.add((catalog_ref, RDF.type, DCAT.Catalog))
            g.add((catalog_ref, DCAT.dataset, dataset_ref))

            sources = (('source_catalog_title', DCT.title, Literal,),
                       ('source_catalog_description', DCT.description, Literal,),
                       ('source_catalog_homepage', FOAF.homepage, URIRef,),
                       ('source_catalog_language', DCT.language, Literal,),
                       ('source_catalog_modified', DCT.modified, Literal,),)

            # base catalog struct
            for item in sources:
                key, predicate, _type = item
                value = _get_from_extra(key)
                if value:
                    g.add((catalog_ref, predicate, _type(value)))

            publisher_sources = (
                                 ('name', Literal, FOAF.name, True,),
                                 ('email', Literal, FOAF.mbox, False,),
                                 ('url', URIRef, FOAF.homepage,False,),
                                 ('type', Literal, DCT.type, False,))

            _pub = _get_from_extra('source_catalog_publisher')
            if _pub:
                pub = json.loads(_pub)

                #pub_uri = URIRef(pub.get('uri'))

                agent = BNode()
                g.add((agent, RDF.type, FOAF.Agent))
                g.add((catalog_ref, DCT.publisher, agent))

                for src_key, _type, predicate, required in publisher_sources:
                    val = pub.get(src_key)
                    if val is None and required:
                        raise ValueError("Value for %s (%s) is required" % (src_key, predicate))
                    elif val is None:
                        continue
                    g.add((agent, predicate, _type(val)))
        
        return catalog_ref
        

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='DCAT RDF - CKAN operations')
    parser.add_argument('mode',
                        default='consume',
                        help='''
Operation mode.
`consume` parses DCAT RDF graphs to CKAN dataset JSON objects.
`produce` serializes CKAN dataset JSON objects into DCAT RDF.
                        ''')
    parser.add_argument('file', nargs='?', type=argparse.FileType('r'),
                        default=sys.stdin,
                        help='Input file. If omitted will read from stdin')
    parser.add_argument('-f', '--format',
                        default='xml',
                        help='''Serialization format (as understood by rdflib)
                                eg: xml, n3 ... Defaults to \'xml\'.''')
    parser.add_argument('-P', '--pretty',
                        action='store_true',
                        help='Make the output more human readable')
    parser.add_argument('-p', '--profile', nargs='*',
                        action='store',
                        help='RDF Profiles to use, defaults to euro_dcat_ap')
    parser.add_argument('-m', '--compat-mode',
                        action='store_true',
                        help='Enable compatibility mode')

    parser.add_argument('-s', '--subcatalogs', action='store_true', dest='subcatalogs',
                        default=False,
                        help="Enable subcatalogs handling (dct:hasPart support)")
    args = parser.parse_args()

    contents = args.file.read()

    config.update({DCAT_EXPOSE_SUBCATALOGS: args.subcatalogs})

    if args.mode == 'produce':
        serializer = RDFSerializer(profiles=args.profile,
                                   compatibility_mode=args.compat_mode)

        dataset = json.loads(contents)
        out = serializer.serialize_dataset(dataset, _format=args.format)
        print out
    else:
        parser = RDFParser(profiles=args.profile,
                           compatibility_mode=args.compat_mode)

        parser.parse(contents, _format=args.format)

        ckan_datasets = [d for d in parser.datasets()]

        indent = 4 if args.pretty else None
        print json.dumps(ckan_datasets, indent=indent)
