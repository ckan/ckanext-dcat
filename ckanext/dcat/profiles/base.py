import datetime
import json
from urllib.parse import quote

from ckan.lib.helpers import resource_formats
from ckan.model.license import LicenseRegister
from ckantoolkit import ObjectNotFound, asbool, aslist, config, get_action, url_for
from dateutil.parser import parse as parse_date
from geomet import InvalidGeoJSONException, wkt
from rdflib import BNode, Literal, URIRef, term
from rdflib.namespace import ORG, RDF, RDFS, SKOS, XSD, Namespace

from ckanext.dcat.utils import DCAT_EXPOSE_SUBCATALOGS
from ckanext.dcat.validators import is_date, is_year, is_year_month

CNT = Namespace("http://www.w3.org/2011/content#")
CR = Namespace("http://mlcommons.org/croissant/")
DCT = Namespace("http://purl.org/dc/terms/")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
DCATAP = Namespace("http://data.europa.eu/r5r/")
DCATUS = Namespace("http://resources.data.gov/ontology/dcat-us#")
ADMS = Namespace("http://www.w3.org/ns/adms#")
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
SCHEMA = Namespace("http://schema.org/")
TIME = Namespace("http://www.w3.org/2006/time#")
LOCN = Namespace("http://www.w3.org/ns/locn#")
GSP = Namespace("http://www.opengis.net/ont/geosparql#")
OWL = Namespace("http://www.w3.org/2002/07/owl#")
SPDX = Namespace("http://spdx.org/rdf/terms#")

namespaces = {
    "cnt": CNT,
    "cr": CR,
    "dct": DCT,
    "dcat": DCAT,
    "dcatap": DCATAP,
    "dcatus": DCATUS,
    "adms": ADMS,
    "vcard": VCARD,
    "foaf": FOAF,
    "schema": SCHEMA,
    "time": TIME,
    "skos": SKOS,
    "locn": LOCN,
    "gsp": GSP,
    "owl": OWL,
    "org": ORG,
    "spdx": SPDX,
}

PREFIX_MAILTO = "mailto:"

GEOJSON_IMT = "https://www.iana.org/assignments/media-types/application/vnd.geo+json"

DEFAULT_SPATIAL_FORMATS = ["wkt"]

ROOT_DATASET_FIELDS = [
    'name',
    'title',
    'url',
    'version',
    'tags',
    'license_id',
    'maintainer',
    'maintainer_email',
    'author',
    'author_email',
]


class URIRefOrLiteral(object):
    """Helper which creates an URIRef if the value appears to be an http URL,
    or a Literal otherwise. URIRefs are also cleaned using CleanedURIRef.

    Like CleanedURIRef, this is a factory class.
    """

    def __new__(cls, value, lang=None):
        try:
            stripped_value = value.strip()
            if isinstance(value, str) and (
                stripped_value.startswith("http://")
                or stripped_value.startswith("https://")
            ):
                uri_obj = CleanedURIRef(value)
                # although all invalid chars checked by rdflib should have been quoted, try to serialize
                # the object. If it breaks, use Literal instead.
                uri_obj.n3()
                # URI is fine, return the object
                return uri_obj
            else:
                return Literal(value, lang=lang)
        except Exception:
            # In case something goes wrong: use Literal
            return Literal(value, lang=lang)


class CleanedURIRef(object):
    """Performs some basic URL encoding on value before creating an URIRef object.

    This is a factory for URIRef objects, which allows usage as type in graph.add()
    without affecting the resulting node types. That is,
    g.add(..., URIRef) and g.add(..., CleanedURIRef) will result in the exact same node type.
    """

    @staticmethod
    def _careful_quote(value):
        # only encode this limited subset of characters to avoid more complex URL parsing
        # (e.g. valid ? in query string vs. ? as value).
        # can be applied multiple times, as encoded %xy is left untouched. Therefore, no
        # unquote is necessary beforehand.
        quotechars = " !\"$'()*,;<>[]{|}\\^`"
        for c in quotechars:
            value = value.replace(c, quote(c))
        return value

    def __new__(cls, value):
        if isinstance(value, str):
            value = CleanedURIRef._careful_quote(value.strip())
        return URIRef(value)


class RDFProfile(object):
    """Base class with helper methods for implementing RDF parsing profiles

    This class should not be used directly, but rather extended to create
    custom profiles
    """

    _dataset_schema = None

    _form_languages = None

    # Cache for mappings of licenses URL/title to ID built when needed in
    # _license().
    _licenceregister_cache = None

    # Cache for organization_show details (used for publisher fallback)
    _org_cache: dict = {}

    def __init__(self, graph, dataset_type="dataset", compatibility_mode=False):
        """Class constructor
        Graph is an rdflib.Graph instance.
        A scheming dataset type can be provided, in which case the scheming schema
        will be loaded so it can be used by profiles.
        In compatibility mode, some fields are modified to maintain
        compatibility with previous versions of the ckanext-dcat parsers
        (eg adding the `dcat_` prefix or storing comma separated lists instead
        of JSON dumps).
        """

        self.g = graph

        self.compatibility_mode = compatibility_mode

        self._default_lang = config.get("ckan.locale_default", "en")


        try:
            schema_show = get_action("scheming_dataset_schema_show")
            try:
                schema = schema_show({}, {"type": dataset_type})
            except ObjectNotFound:
                raise ObjectNotFound(f"Unknown dataset schema: {dataset_type}")

            self._dataset_schema = schema

        except KeyError:
            pass

        if self._dataset_schema:
            self._form_languages = self._dataset_schema.get("form_languages")

    def _datasets(self):
        """
        Generator that returns all DCAT datasets on the graph

        Yields term.URIRef objects that can be used on graph lookups
        and queries
        """
        for dataset in self.g.subjects(RDF.type, DCAT.Dataset):
            yield dataset

    def _distributions(self, dataset):
        """
        Generator that returns all DCAT distributions on a particular dataset

        Yields term.URIRef objects that can be used on graph lookups
        and queries
        """
        for distribution in self.g.objects(dataset, DCAT.distribution):
            yield distribution

    def _keywords(self, dataset_ref):
        """
        Returns all DCAT keywords on a particular dataset
        """
        keywords = self._object_value_list(dataset_ref, DCAT.keyword) or []
        # Split keywords with commas
        keywords_with_commas = [k for k in keywords if "," in k]
        for keyword in keywords_with_commas:
            keywords.remove(keyword)
            keywords.extend([k.strip() for k in keyword.split(",")])
        return keywords

    def _object(self, subject, predicate):
        """
        Helper for returning the first object for this subject and predicate

        Both subject and predicate must be rdflib URIRef or BNode objects

        Returns an rdflib reference (URIRef or BNode) or None if not found
        """
        for _object in self.g.objects(subject, predicate):
            return _object
        return None

    def _object_value(self, subject, predicate, multilingual=False):
        """
        Given a subject and a predicate, returns the value of the object

        Both subject and predicate must be rdflib URIRef or BNode objects

        If found, the string representation is returned, else an empty string

        If multilingual is True, a dict with the language codes as keys will be
        returned for each language found. e.g.

            {
                "en": "Dataset title",
                "es": "Título del conjunto de datos"
            }

        If one of the languages defined in `form_languages` in the schema is not
        found in the graph, an empty string will be returned.

            {
                "en": "Dataset title",
                "es": ""
            }

        """
        if multilingual:
            return self._object_value_multilingual(subject, predicate)
        fallback = ""
        for o in self.g.objects(subject, predicate):
            if isinstance(o, Literal):
                if o.language and o.language == self._default_lang:
                    return str(o)
                # Use first object as fallback if no object with the default
                # language is available
                elif fallback == "":
                    fallback = str(o)
            elif len(list(self.g.objects(o, RDFS.label))):
                return str(next(self.g.objects(o, RDFS.label)))
            else:
                return str(o)
        return fallback

    def _object_value_multilingual(self, subject, predicate):
        out = {}
        for o in self.g.objects(subject, predicate):

            if isinstance(o, Literal):
                if o.language:
                    out[o.language] = str(o)
                else:
                    out[self._default_lang] = str(o)
            elif len(list(self.g.objects(o, RDFS.label))):
                for label in self.g.objects(o, RDFS.label):
                    if label.language:
                        out[label.language] = str(label)
                    else:
                        out[self._default_lang] = str(label)
            else:
                out[self._default_lang] = str(o)

        if self._form_languages:
            for lang in self._form_languages:
                if lang not in out:
                    out[lang] = ""

        return out

    def _object_value_multiple_predicate(self, subject, predicates):
        """
        Given a subject and a list of predicates, returns the value of the object
        according to the order in which it was specified.

        Both subject and predicates must be rdflib URIRef or BNode objects

        If found, the string representation is returned, else an empty string
        """
        object_value = ""
        for predicate in predicates:
            object_value = self._object_value(subject, predicate)
            if object_value:
                break

        return object_value

    def _object_value_int(self, subject, predicate):
        """
        Given a subject and a predicate, returns the value of the object as an
        integer

        Both subject and predicate must be rdflib URIRef or BNode objects

        If the value can not be parsed as intger, returns None
        """
        object_value = self._object_value(subject, predicate)
        if object_value:
            try:
                return int(float(object_value))
            except ValueError:
                pass
        return None

    def _object_value_int_list(self, subject, predicate):
        """
        Given a subject and a predicate, returns the value of the object as a
        list of integers

        Both subject and predicate must be rdflib URIRef or BNode objects

        If the value can not be parsed as integer, returns an empty list
        """
        object_values = []
        for object in self.g.objects(subject, predicate):
            if object:
                try:
                    object_values.append(int(float(object)))
                except ValueError:
                    pass
        return object_values

    def _object_value_float_list(self, subject, predicate):
        """
        Given a subject and a predicate, returns the value of the object as a
        list of floats

        Both subject and predicate must be rdflib URIRef or BNode objects

        If the value can not be parsed as a float, returns an empty list
        """
        object_values = []
        for object in self.g.objects(subject, predicate):
            if object:
                try:
                    object_values.append(float(object))
                except ValueError:
                    pass
        return object_values

    def _object_value_list(self, subject, predicate):
        """
        Given a subject and a predicate, returns a list with all the values of
        the objects

        Both subject and predicate must be rdflib URIRef or BNode  objects

        If no values found, returns an empty list
        """
        return [str(o) for o in self.g.objects(subject, predicate)]

    def _object_value_list_multilingual(self, subject, predicate):
        """
        Given a subject and a predicate, returns a dict with the language codes
        as keys and the list of object values as values. e.g.

            {
                "en": ["Oaks", "Pines"],
                "es": ["Robles", "Pinos"],
            }

        If one of the languages defined in `form_languages` in the schema is not
        found in the graph, an empty list will be returned.

            {
                "en": ["Oaks", "Pines"],
                "es": [],
            }

        Both subject and predicate must be rdflib URIRef or BNode  objects

        If no values found, returns an empty list
        """
        out = {}
        for o in self.g.objects(subject, predicate):
            lang = o.language or self._default_lang
            if lang not in out:
                out[lang] = []
            out[lang].append(str(o))

        if self._form_languages:
            for lang in self._form_languages:
                if lang not in out:
                    out[lang] = []
        return out

    def _get_vcard_property_value(
        self, subject, predicate, predicate_string_property=None
    ):
        """
        Given a subject, a predicate and a predicate for the simple string property (optional),
        returns the value of the object. Trying to read the value in the following order
            * predicate_string_property
            * predicate

        All subject, predicate and predicate_string_property must be rdflib URIRef or BNode  objects

        If no value is found, returns an empty string
        """

        result = ""
        if predicate_string_property:
            result = self._object_value(subject, predicate_string_property)

        if not result:
            obj = self._object(subject, predicate)
            if isinstance(obj, BNode):
                result = self._object_value(obj, VCARD.hasValue)
            else:
                result = self._object_value(subject, predicate)

        return result

    def _time_interval(self, subject, predicate, dcat_ap_version=1):
        """
        Returns the start and end date for a time interval object

        Both subject and predicate must be rdflib URIRef or BNode objects

        It checks for time intervals defined with DCAT, W3C Time hasBeginning & hasEnd
        and schema.org startDate & endDate.

        Returns a tuple with the start and end date values, both of which
        can be None if not found
        """

        start_date = end_date = None

        if dcat_ap_version == 1:
            start_date, end_date = self._read_time_interval_schema_org(
                subject, predicate
            )
            if start_date or end_date:
                return start_date, end_date
            return self._read_time_interval_time(subject, predicate)
        elif dcat_ap_version == 2:
            start_date, end_date = self._read_time_interval_dcat(subject, predicate)
            if start_date or end_date:
                return start_date, end_date
            start_date, end_date = self._read_time_interval_time(subject, predicate)
            if start_date or end_date:
                return start_date, end_date
            return self._read_time_interval_schema_org(subject, predicate)

    def _read_time_interval_schema_org(self, subject, predicate):
        start_date = end_date = None

        for interval in self.g.objects(subject, predicate):
            start_date = self._object_value(interval, SCHEMA.startDate)
            end_date = self._object_value(interval, SCHEMA.endDate)

            if start_date or end_date:
                return start_date, end_date

        return start_date, end_date

    def _read_time_interval_dcat(self, subject, predicate):
        start_date = end_date = None

        for interval in self.g.objects(subject, predicate):
            start_date = self._object_value(interval, DCAT.startDate)
            end_date = self._object_value(interval, DCAT.endDate)

            if start_date or end_date:
                return start_date, end_date

        return start_date, end_date

    def _read_time_interval_time(self, subject, predicate):
        start_date = end_date = None

        for interval in self.g.objects(subject, predicate):
            start_nodes = [t for t in self.g.objects(interval, TIME.hasBeginning)]
            end_nodes = [t for t in self.g.objects(interval, TIME.hasEnd)]
            if start_nodes:
                start_date = self._object_value_multiple_predicate(
                    start_nodes[0],
                    [TIME.inXSDDateTimeStamp, TIME.inXSDDateTime, TIME.inXSDDate],
                )
            if end_nodes:
                end_date = self._object_value_multiple_predicate(
                    end_nodes[0],
                    [TIME.inXSDDateTimeStamp, TIME.inXSDDateTime, TIME.inXSDDate],
                )

            if start_date or end_date:
                return start_date, end_date

        return start_date, end_date

    def _insert_or_update_temporal(self, dataset_dict, key, value):
        temporal = next(
            (item for item in dataset_dict["extras"] if (item["key"] == key)), None
        )
        if temporal:
            temporal["value"] = value
        else:
            dataset_dict["extras"].append({"key": key, "value": value})

    def _agents_details(self, subject, predicate):
        """
        Returns a list of dicts with details about a foaf:Agent property, e.g.
        dct:publisher or dct:creator entity.

        Both subject and predicate must be rdflib URIRef or BNode objects

        Examples:

        <dct:publisher> or <dct:creator>
            <foaf:Organization rdf:about="http://orgs.vocab.org/some-org">
                <foaf:name>Publishing Organization for dataset 1</foaf:name>
                <foaf:mbox>contact@some.org</foaf:mbox>
                <foaf:homepage>http://some.org</foaf:homepage>
                <dct:type rdf:resource="http://purl.org/adms/publishertype/NonProfitOrganisation"/>
            </foaf:Organization>

        Returns keys for uri, name, email, url, type, and identifier with the values set to
        an empty string if they could not be found.
        """

        agents = []
        for agent in self.g.objects(subject, predicate):
            agent_details = {}
            agent_details["uri"] = str(agent) if isinstance(agent, term.URIRef) else ""
            agent_details["name"] = self._object_value(agent, FOAF.name)
            agent_details["email"] = self._without_mailto(
                self._object_value(agent, FOAF.mbox)
            )
            if not agent_details["email"]:
                agent_details["email"] = self._without_mailto(
                    self._object_value(agent, VCARD.hasEmail)
                )
            agent_details["url"] = self._object_value(agent, FOAF.homepage)
            agent_details["type"] = self._object_value(agent, DCT.type)
            agent_details['identifier'] = self._object_value(agent, DCT.identifier)
            agents.append(agent_details)

        return agents

    def _contact_details(self, subject, predicate):
        """
        Returns a list of dicts with details about vcard expressions

        Both subject and predicate must be rdflib URIRef or BNode objects

        Returns keys for uri, name and email with the values set to
        an empty string if they could not be found
        """

        contacts = []
        for agent in self.g.objects(subject, predicate):

            contact = {}
            contact["uri"] = str(agent) if isinstance(agent, URIRef) else ""

            contact["name"] = self._get_vcard_property_value(
                agent, VCARD.hasFN, VCARD.fn
            )

            contact["email"] = self._without_mailto(
                self._get_vcard_property_value(agent, VCARD.hasEmail)
            )

            contact["identifier"] = self._get_vcard_property_value(agent, VCARD.hasUID)

            contact["url"] = self._get_vcard_property_value(agent, VCARD.hasURL)

            contacts.append(contact)

        return contacts

    def _parse_geodata(self, spatial, datatype, cur_value):
        """
        Extract geodata with the given datatype from the spatial data and check if it contains a valid GeoJSON
        or WKT geometry.

        Returns the String or None if the value is no valid GeoJSON or WKT geometry.
        """
        for geometry in self.g.objects(spatial, datatype):
            if geometry.datatype == URIRef(GEOJSON_IMT) or not geometry.datatype:
                try:
                    json.loads(str(geometry))
                    cur_value = str(geometry)
                except (ValueError, TypeError):
                    pass
            if not cur_value and geometry.datatype == GSP.wktLiteral:
                try:
                    cur_value = json.dumps(wkt.loads(str(geometry)))
                except (ValueError, TypeError):
                    pass
        return cur_value

    def _spatial(self, subject, predicate):
        """
        Returns a dict with details about the spatial location

        Both subject and predicate must be rdflib URIRef or BNode objects

        Returns keys for uri, text or geom with the values set to
        None if they could not be found.

        Geometries are always returned in GeoJSON. If only WKT is provided,
        it will be transformed to GeoJSON.

        Check the notes on the README for the supported formats:

        https://github.com/ckan/ckanext-dcat/#rdf-dcat-to-ckan-dataset-mapping
        """

        uri = None
        text = None
        geom = None
        bbox = None
        cent = None

        for spatial in self.g.objects(subject, predicate):

            if isinstance(spatial, URIRef):
                uri = str(spatial)

            if isinstance(spatial, Literal):
                text = str(spatial)

            if (spatial, RDF.type, DCT.Location) in self.g:
                geom = self._parse_geodata(spatial, LOCN.geometry, geom)
                bbox = self._parse_geodata(spatial, DCAT.bbox, bbox)
                cent = self._parse_geodata(spatial, DCAT.centroid, cent)
                for label in self.g.objects(spatial, SKOS.prefLabel):
                    text = str(label)
                for label in self.g.objects(spatial, RDFS.label):
                    text = str(label)

        return {
            "uri": uri,
            "text": text,
            "geom": geom,
            "bbox": bbox,
            "centroid": cent,
        }

    def _license(self, dataset_ref):
        """
        Returns a license identifier if one of the distributions license is
        found in CKAN license registry. If no distribution's license matches,
        an empty string is returned.

        The first distribution with a license found in the registry is used so
        that if distributions have different licenses we'll only get the first
        one.
        """
        if self._licenceregister_cache is not None:
            license_uri2id, license_title2id = self._licenceregister_cache
        else:
            license_uri2id = {}
            license_title2id = {}
            for license_id, license in list(LicenseRegister().items()):
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
                        self._object_value(license, DCT.title)
                    )
                if license_id:
                    return license_id
        return ""

    def _access_rights(self, subject, predicate):
        """
        Returns the rights statement or an empty string if no one is found.
        """

        result = ""
        obj = self._object(subject, predicate)
        if obj:
            if (
                isinstance(obj, BNode)
                and self._object(obj, RDF.type) == DCT.RightsStatement
            ):
                result = self._object_value(obj, RDFS.label)
            elif isinstance(obj, Literal) or isinstance(obj, URIRef):
                # unicode_safe not include Literal or URIRef
                result = str(obj)
        return result

    def _distribution_format(self, distribution, normalize_ckan_format=True):
        """
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
        4. value of dct:format if it is an URIRef and appears to be an IANA type

        Values for the label will be checked in the following order:

        1. literal value of dct:format if it not contains a '/' character
        2. label of dct:format if it is an instance of dct:IMT (see above)
        3. value of dct:format if it is an URIRef and doesn't look like an IANA type

        If `normalize_ckan_format` is True the label will
        be tried to match against the standard list of formats that is included
        with CKAN core
        (https://github.com/ckan/ckan/blob/master/ckan/config/resource_formats.json)
        This allows for instance to populate the CKAN resource format field
        with a format that view plugins, etc will understand (`csv`, `xml`,
        etc.)

        Return a tuple with the media type and the label, both set to None if
        they couldn't be found.
        """

        imt = None
        label = None

        imt = self._object_value(distribution, DCAT.mediaType)

        _format = self._object(distribution, DCT["format"])
        if isinstance(_format, Literal):
            if not imt and "/" in _format:
                imt = str(_format)
            else:
                label = str(_format)
        elif isinstance(_format, (BNode, URIRef)):
            if self._object(_format, RDF.type) == DCT.IMT:
                if not imt:
                    imt = str(self.g.value(_format, default=None))
                label = self._object_value(_format, RDFS.label)
            elif isinstance(_format, URIRef):
                # If the URIRef does not reference a BNode, it could reference an IANA type.
                # Otherwise, use it as label.
                format_uri = str(_format)
                if "iana.org/assignments/media-types" in format_uri and not imt:
                    imt = format_uri
                else:
                    label = format_uri

        if (imt or label) and normalize_ckan_format:

            format_registry = resource_formats()

            if imt in format_registry:
                label = format_registry[imt][1]
            elif label in format_registry:
                label = format_registry[label][1]

        return imt, label

    def _get_dict_value(self, _dict, key, default=None):
        """
        Returns the value for the given key on a CKAN dict

        By default a key on the root level is checked. If not found, extras
        are checked, both with the key provided and with `dcat_` prepended to
        support legacy fields.

        If not found, returns the default value, which defaults to None
        """

        if key in _dict:
            return _dict[key]

        for extra in _dict.get("extras", []):
            if extra["key"] == key or extra["key"] == "dcat_" + key:
                return extra["value"]

        return default

    def _read_list_value(self, value):
        items = []
        # List of values
        if isinstance(value, list):
            items = value
        elif value and isinstance(value, str):
            try:
                items = json.loads(value)
                if isinstance(items, ((int, float, complex))):
                    items = [items]  # JSON list
            except ValueError:
                if "," in value:
                    # Comma-separated list
                    items = value.split(",")
                else:
                    items = [value]  # Normal text value
        elif isinstance(value, ((int, float, complex))):
            items = [value]  # number

        return items

    def _add_spatial_value_to_graph(self, spatial_ref, predicate, value):
        """
        Adds spatial triples to the graph. Assumes that value is a GeoJSON string
        or object.
        """
        spatial_formats = aslist(
            config.get("ckanext.dcat.output_spatial_format", DEFAULT_SPATIAL_FORMATS)
        )

        if isinstance(value, str):
            try:
                value = json.loads(value)
            except (TypeError, ValueError):
                return

        if "wkt" in spatial_formats:
            # WKT, because GeoDCAT-AP says so
            try:
                self.g.add(
                    (
                        spatial_ref,
                        predicate,
                        Literal(
                            wkt.dumps(value, decimals=4),
                            datatype=GSP.wktLiteral,
                        ),
                    )
                )
            except (TypeError, ValueError, InvalidGeoJSONException):
                pass

        if "geojson" in spatial_formats:
            # GeoJSON
            self.g.add((spatial_ref, predicate, Literal(json.dumps(value), datatype=GEOJSON_IMT)))


    def _add_spatial_to_dict(self, dataset_dict, key, spatial):
        if spatial.get(key):
            dataset_dict["extras"].append(
                {
                    "key": "spatial_{0}".format(key) if key != "geom" else "spatial",
                    "value": spatial.get(key),
                }
            )

    def _add_statement_to_graph(self, data_dict, key, subject, predicate, _class=None):
        """
        Adds a statement property to the graph.
        If it is a Literal value, it is added as a node (with a class if provided)
        with a RDFS.label property, eg:

            dct:accessRights [ a dct:RightsStatement ;
                rdfs:label "Statement about access rights" ] ;

        An URI can also be used:

            dct:accessRights <https://example.org/vocab/access-right/TODO/PUBLIC> ;

            [...]

            <https://example.org/vocab/access-right/TODO/PUBLIC> a dct:RightsStatement .
        """
        value = self._get_dict_value(data_dict, key)
        if value:
            if isinstance(value, dict):
                _objects = []
                for lang in value:
                    _objects.append(URIRefOrLiteral(value[lang], lang))
            else:
                _objects = [URIRefOrLiteral(value)]
            statement_ref = None
            for _object in _objects:
                if isinstance(_object, Literal):
                    if not statement_ref:
                        statement_ref = BNode()
                        self.g.add((subject, predicate, statement_ref))
                        if _class:
                            self.g.add((statement_ref, RDF.type, _class))
                    self.g.add((statement_ref, RDFS.label, _object))
                else:
                    self.g.add((subject, predicate, _object))
                    if _class:
                        self.g.add((_object, RDF.type, _class))

    def _schema_field(self, key):
        """
        Returns the schema field information if the provided key exists as a field in
        the dataset schema (if one was provided)
        """
        if not self._dataset_schema:
            return None

        for field in self._dataset_schema["dataset_fields"]:
            if field["field_name"] == key:
                return field

    def _schema_resource_field(self, key):
        """
        Returns the schema field information if the provided key exists as a field in
        the resources fields of the dataset schema (if one was provided)
        """
        if not self._dataset_schema:
            return None

        for field in self._dataset_schema["resource_fields"]:
            if field["field_name"] == key:
                return field

    def _multilingual_dataset_fields(self):
        """
        Return a list of field names in the dataset shema that have multilingual
        values (i.e. that use one of the fluent presets)
        """
        return self._multilingual_fields(entity="dataset")

    def _multilingual_resource_fields(self):
        """
        Return a list of field names in the resource schema that have multilingual
        values (i.e. that use one of the fluent presets)
        """
        return self._multilingual_fields(entity="resource")

    def _multilingual_fields(self, entity="dataset"):
        if not self._dataset_schema:
            return []

        out = []
        for field in self._dataset_schema[f"{entity}_fields"]:
            if field.get("validators") and any(
                v for v in field["validators"].split() if v.startswith("fluent")
            ):
                out.append(field["field_name"])
        return out

    def _set_dataset_value(self, dataset_dict, key, value):
        """
        Sets the value for a given key in a CKAN dataset dict
        If a dataset schema was provided, the schema will be checked to see if
        a custom field is present for the key. If so the key will be stored at
        the dict root level, otherwise it will be stored as an extra.
        Standard CKAN fields (defined in ROOT_DATASET_FIELDS) are always stored
        at the root level.
        """
        if self._schema_field(key) or key in ROOT_DATASET_FIELDS:
            dataset_dict[key] = value
        else:
            if not dataset_dict.get("extras"):
                dataset_dict["extras"] = []
            dataset_dict["extras"].append({"key": key, "value": value})

        return dataset_dict

    def _set_list_dataset_value(self, dataset_dict, key, value):
        schema_field = self._schema_field(key)
        if schema_field and "scheming_multiple_text" in schema_field["validators"]:
            return self._set_dataset_value(dataset_dict, key, value)
        else:
            return self._set_dataset_value(dataset_dict, key, json.dumps(value))

    def _set_list_resource_value(self, resource_dict, key, value):
        schema_field = self._schema_resource_field(key)
        if schema_field and "scheming_multiple_text" in schema_field["validators"]:
            resource_dict[key] = value
        else:
            resource_dict[key] = json.dumps(value)

        return resource_dict

    def _get_dataset_value(self, dataset_dict, key, default=None):
        """
        Returns the value for the given key on a CKAN dict

        Check `_get_dict_value` for details
        """
        return self._get_dict_value(dataset_dict, key, default)

    def _get_resource_value(self, resource_dict, key, default=None):
        """
        Returns the value for the given key on a CKAN dict

        Check `_get_dict_value` for details
        """
        return self._get_dict_value(resource_dict, key, default)

    def _add_date_triples_from_dict(self, _dict, subject, items):
        self._add_triples_from_dict(_dict, subject, items, date_value=True)

    def _add_list_triples_from_dict(self, _dict, subject, items):
        self._add_triples_from_dict(_dict, subject, items, list_value=True)

    def _add_triples_from_dict(
        self, _dict, subject, items, list_value=False, date_value=False
    ):

        for item in items:
            try:
                key, predicate, fallbacks, _type, _class = item
            except ValueError:
                key, predicate, fallbacks, _type = item
                _class = None
            self._add_triple_from_dict(
                _dict,
                subject,
                predicate,
                key,
                fallbacks=fallbacks,
                list_value=list_value,
                date_value=date_value,
                _type=_type,
                _class=_class,
            )

    def _add_triple_from_dict(
        self,
        _dict,
        subject,
        predicate,
        key,
        fallbacks=None,
        list_value=False,
        date_value=False,
        _type=Literal,
        _datatype=None,
        _class=None,
        value_modifier=None,
    ):
        """
        Adds a new triple to the graph with the provided parameters

        The subject and predicate of the triple are passed as the relevant
        RDFLib objects (URIRef or BNode). As default, the object is a
        literal value, which is extracted from the dict using the provided key
        (see `_get_dict_value`). If the value for the key is not found, then
        additional fallback keys are checked.
        Using `value_modifier`, a function taking the extracted value and
        returning a modified value can be passed.
        If a value was found, the modifier is applied before adding the value.

        `_class` is the optional RDF class of the entity being added.

        If `list_value` or `date_value` are True, then the value is treated as
        a list or a date respectively (see `_add_list_triple` and
        `_add_date_triple` for details.
        """
        value = self._get_dict_value(_dict, key)
        if not value and fallbacks:
            for fallback in fallbacks:
                value = self._get_dict_value(_dict, fallback)
                if value:
                    break

        # if a modifying function was given, apply it to the value
        if value and callable(value_modifier):
            value = value_modifier(value)

        if value and list_value:
            self._add_list_triple(subject, predicate, value, _type, _datatype, _class)
        elif value and date_value:
            self._add_date_triple(subject, predicate, value, _type)
        elif value:
            # If it is a dict, we assume it's a fluent multilingual field
            if isinstance(value, dict):
                # We assume that all translated field values are Literals
                for lang, translated_value in value.items():
                    object = Literal(translated_value, datatype=_datatype, lang=lang)
                    self.g.add((subject, predicate, object))
                return

            # Normal text value

            # ensure URIRef items are preprocessed (space removal/url encoding)
            if _type == URIRef:
                _type = CleanedURIRef
            if _datatype:
                object = _type(value, datatype=_datatype)
            else:
                object = _type(value)
            self.g.add((subject, predicate, object))

            if _class and isinstance(object, URIRef):
                self.g.add((object, RDF.type, _class))

    def _add_list_triple(
        self, subject, predicate, value, _type=Literal, _datatype=None, _class=None
    ):
        """
        Adds as many triples to the graph as values

        Values are literal strings, if `value` is a list, one for each
        item. If `value` is a string there is an attempt to split it using
        commas, to support legacy fields.
        """
        items = self._read_list_value(value)

        for item in items:
            # ensure URIRef items are preprocessed (space removal/url encoding)
            if _type == URIRef:
                _type = CleanedURIRef
            if _datatype:
                object = _type(item, datatype=_datatype)
            else:
                object = _type(item)
            self.g.add((subject, predicate, object))

            if _class and isinstance(object, URIRef):
                self.g.add((object, RDF.type, _class))

    def _add_date_triple(self, subject, predicate, value, _type=Literal):
        """
        Adds a new triple with a date object

        If the value is one of xsd:gYear, xsd:gYearMonth or xsd:date. If not
        the value will be parsed using dateutil, and if the date obtained is correct,
        added to the graph as an xsd:dateTime value.

        If there are parsing errors, the literal string value is added.
        """
        if not value:
            return

        if is_year(value):
            self.g.add((subject, predicate, _type(value, datatype=XSD.gYear)))
        elif is_year_month(value):
            self.g.add((subject, predicate, _type(value, datatype=XSD.gYearMonth)))
        elif is_date(value):
            self.g.add((subject, predicate, _type(value, datatype=XSD.date)))
        else:
            try:
                default_datetime = datetime.datetime(1, 1, 1, 0, 0, 0)
                _date = parse_date(value, default=default_datetime)

                self.g.add(
                    (subject, predicate, _type(_date.isoformat(), datatype=XSD.dateTime))
                )
            except ValueError:
                self.g.add((subject, predicate, _type(value)))

    def _last_catalog_modification(self):
        """
        Returns the date and time the catalog was last modified

        To be more precise, the most recent value for `metadata_modified` on a
        dataset.

        Returns a dateTime string in ISO format, or None if it could not be
        found.
        """
        context = {"ignore_auth": True}
        result = get_action("package_search")(
            context,
            {
                "sort": "metadata_modified desc",
                "rows": 1,
            },
        )
        if result and result.get("results"):
            return result["results"][0]["metadata_modified"]
        return None

    def _add_mailto(self, mail_addr):
        """
        Ensures that the mail address has an URIRef-compatible mailto: prefix.
        Can be used as modifier function for `_add_triple_from_dict`.
        """
        if mail_addr:
            return PREFIX_MAILTO + self._without_mailto(mail_addr)
        else:
            return mail_addr

    def _without_mailto(self, mail_addr):
        """
        Ensures that the mail address string has no mailto: prefix.
        """
        if mail_addr:
            return str(mail_addr).replace(PREFIX_MAILTO, "")
        else:
            return mail_addr

    def _get_source_catalog(self, dataset_ref):
        """
        Returns Catalog reference that is source for this dataset.

        Catalog referenced in dct:hasPart is returned,
        if dataset is linked there, otherwise main catalog
        will be returned.

        This will not be used if ckanext.dcat.expose_subcatalogs
        configuration option is set to False.
        """
        if not asbool(config.get(DCAT_EXPOSE_SUBCATALOGS, False)):
            return
        catalogs = set(self.g.subjects(DCAT.dataset, dataset_ref))
        root = self._get_root_catalog_ref()
        try:
            catalogs.remove(root)
        except KeyError:
            pass
        assert len(catalogs) in (0, 1,), (
            "len %s" % catalogs
        )
        if catalogs:
            return catalogs.pop()
        return root

    def _get_root_catalog_ref(self):
        roots = list(self.g.subjects(DCT.hasPart))
        if not roots:
            roots = list(self.g.subjects(RDF.type, DCAT.Catalog))
        return roots[0]

    def _get_or_create_spatial_ref(self, dataset_dict, dataset_ref):
        for spatial_ref in self.g.objects(dataset_ref, DCT.spatial):
            if spatial_ref:
                return spatial_ref

        # Create new spatial_ref
        spatial_uri = self._get_dataset_value(dataset_dict, "spatial_uri")
        if spatial_uri:
            spatial_ref = CleanedURIRef(spatial_uri)
        else:
            spatial_ref = BNode()
        self.g.add((spatial_ref, RDF.type, DCT.Location))
        self.g.add((dataset_ref, DCT.spatial, spatial_ref))
        return spatial_ref

    # Public methods for profiles to implement

    def parse_dataset(self, dataset_dict, dataset_ref):
        """
        Creates a CKAN dataset dict from the RDF graph

        The `dataset_dict` is passed to all the loaded profiles before being
        yielded, so it can be further modified by each one of them.
        `dataset_ref` is an rdflib URIRef object
        that can be used to reference the dataset when querying the graph.

        Returns a dataset dict that can be passed to eg `package_create`
        or `package_update`
        """
        return dataset_dict

    def _extract_catalog_dict(self, catalog_ref):
        """
        Returns list of key/value dictionaries with catalog
        """

        out = []
        sources = (
            (
                "source_catalog_title",
                DCT.title,
            ),
            (
                "source_catalog_description",
                DCT.description,
            ),
            (
                "source_catalog_homepage",
                FOAF.homepage,
            ),
            (
                "source_catalog_language",
                DCT.language,
            ),
            (
                "source_catalog_modified",
                DCT.modified,
            ),
        )

        for key, predicate in sources:
            val = self._object_value(catalog_ref, predicate)
            if val:
                out.append({"key": key, "value": val})

        publishers = self._agents_details(catalog_ref, DCT.publisher)
        if publishers:
            publisher = publishers[0]
        out.append(
            {
                "key": "source_catalog_publisher",
                "value": json.dumps(publisher),
            }
        )
        return out

    def graph_from_catalog(self, catalog_dict, catalog_ref):
        """
        Creates an RDF graph for the whole catalog (site)

        The class RDFLib graph (accessible via `self.g`) should be updated on
        this method

        `catalog_dict` is a dict that can contain literal values for the
        dcat:Catalog class like `title`, `homepage`, etc. `catalog_ref` is an
        rdflib URIRef object that must be used to reference the catalog when
        working with the graph.
        """
        pass

    def graph_from_dataset(self, dataset_dict, dataset_ref):
        """
        Given a CKAN dataset dict, creates an RDF graph

        The class RDFLib graph (accessible via `self.g`) should be updated on
        this method

        `dataset_dict` is a dict with the dataset metadata like the one
        returned by `package_show`. `dataset_ref` is an rdflib URIRef object
        that must be used to reference the dataset when working with the graph.
        """
        pass
