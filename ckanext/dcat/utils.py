# -*- coding: utf-8 -*-

from builtins import str
import logging
import uuid
import simplejson as json
import re
import operator


from ckantoolkit import config, h

from ckan.exceptions import HelperError

from ckan import model
import ckan.plugins.toolkit as toolkit

from ckanext.dcat.exceptions import RDFProfileException

from ckan.views.home import index as index_endpoint
from ckan.views.dataset import read as read_endpoint

_ = toolkit._

log = logging.getLogger(__name__)

DCAT_EXPOSE_SUBCATALOGS = 'ckanext.dcat.expose_subcatalogs'

CONTENT_TYPES = {
    'rdf': 'application/rdf+xml',
    'xml': 'application/rdf+xml',
    'n3': 'text/n3',
    'ttl': 'text/turtle',
    'jsonld': 'application/ld+json',
}

DCAT_CLEAN_TAGS = 'ckanext.dcat.clean_tags'

DEFAULT_CATALOG_ENDPOINT = '/catalog.{_format}'
ENABLE_RDF_ENDPOINTS_CONFIG = 'ckanext.dcat.enable_rdf_endpoints'
ENABLE_CONTENT_NEGOTIATION_CONFIG = 'ckanext.dcat.enable_content_negotiation'


def _get_package_type(id):
    """
    Given the id of a package this method will return the type of the
    package, or 'dataset' if no type is currently set
    """
    pkg = model.Package.get(id)
    if pkg:
        return pkg.type or u'dataset'
    return None


def field_labels():
    '''
    Returns a dict with the user friendly translatable field labels that
    can be used in the frontend.
    '''

    return {
        'uri': _('URI'),
        'guid': _('GUID'),
        'theme': _('Theme'),
        'identifier': _('Identifier'),
        'alternate_identifier': _('Alternate identifier'),
        'issued': _('Issued'),
        'modified': _('Modified'),
        'version_notes': _('Version notes'),
        'language': _('Language'),
        'frequency': _('Frequency'),
        'conforms_to': _('Conforms to'),
        'spatial_uri': _('Spatial URI'),
        'temporal_start': _('Start of temporal extent'),
        'temporal_end': _('End of temporal extent'),
        'publisher_uri': _('Publisher URI'),
        'publisher_name': _('Publisher name'),
        'publisher_email': _('Publisher email'),
        'publisher_url': _('Publisher URL'),
        'publisher_type': _('Publisher type'),
        'contact_name': _('Contact name'),
        'contact_email': _('Contact email'),
        'contact_uri': _('Contact URI'),
        'download_url': _('Download URL'),
        'mimetype': _('Media type'),
        'size': _('Size'),
        'rights': _('Rights'),
        'created': _('Created'),
    }

def helper_available(helper_name):
    '''
    Checks if a given helper name is available on `h`
    '''
    try:
        getattr(h, helper_name)
    except (AttributeError, HelperError):
        return False
    return True

def structured_data(dataset_id, profiles=None, _format='jsonld'):
    '''
    Returns a string containing the structured data of the given
    dataset id and using the given profiles (if no profiles are supplied
    the default profiles are used).

    This string can be used in the frontend.
    '''
    if not profiles:
        profiles = ['schemaorg']

    data = toolkit.get_action('dcat_dataset_show')(
        {},
        {
            'id': dataset_id,
            'profiles': profiles,
            'format': _format,
        }
    )
    # parse result again to prevent UnicodeDecodeError and add formatting
    try:
        json_data = json.loads(data)
        return json.dumps(json_data, sort_keys=True,
                          indent=4, separators=(',', ': '), cls=json.JSONEncoderForHTML)
    except ValueError:
        # result was not JSON, return anyway
        return data

def catalog_uri():
    '''
    Returns an URI for the whole catalog

    This will be used to uniquely reference the CKAN instance on the RDF
    serializations and as a basis for eg datasets URIs (if not present on
    the metadata).

    The value will be the first found of:

        1. The `ckanext.dcat.base_uri` config option (recommended)
        2. The `ckan.site_url` config option
        3. `http://` + the `app_instance_uuid` config option (minus brackets)

    A warning is emited if the third option is used.

    Returns a string with the catalog URI.
    '''

    uri = config.get('ckanext.dcat.base_uri')
    if not uri:
        uri = config.get('ckan.site_url')
    if not uri:
        app_uuid = config.get('app_instance_uuid')
        if app_uuid:
            uri = 'http://' + app_uuid.replace('{', '').replace('}', '')
            log.critical('Using app id as catalog URI, you should set the ' +
                         '`ckanext.dcat.base_uri` or `ckan.site_url` option')
        else:
            uri = 'http://' + str(uuid.uuid4())
            log.critical('Using a random id as catalog URI, you should set ' +
                         'the `ckanext.dcat.base_uri` or `ckan.site_url` ' +
                         'option')

    return uri


def dataset_uri(dataset_dict):
    '''
    Returns an URI for the dataset

    This will be used to uniquely reference the dataset on the RDF
    serializations.

    The value will be the first found of:

        1. The value of the `uri` field
        2. The value of an extra with key `uri`
        3. `catalog_uri()` + '/dataset/' + `id` field

    Check the documentation for `catalog_uri()` for the recommended ways of
    setting it.

    Returns a string with the dataset URI.
    '''

    uri = dataset_dict.get('uri')
    if not uri:
        for extra in dataset_dict.get('extras', []):
            if extra['key'] == 'uri' and extra['value'] != 'None':
                uri = extra['value']
                break
    if not uri and dataset_dict.get('id'):
        uri = '{0}/dataset/{1}'.format(catalog_uri().rstrip('/'),
                                       dataset_dict['id'])
    if not uri:
        uri = '{0}/dataset/{1}'.format(catalog_uri().rstrip('/'),
                                       str(uuid.uuid4()))
        log.warning('Using a random id for dataset URI')

    return uri


def resource_uri(resource_dict):
    '''
    Returns an URI for the resource

    This will be used to uniquely reference the resource on the RDF
    serializations.

    The value will be the first found of:

        1. The value of the `uri` field
        2. `catalog_uri()` + '/dataset/' + `package_id` + '/resource/'
            + `id` field

    Check the documentation for `catalog_uri()` for the recommended ways of
    setting it.

    Returns a string with the resource URI.
    '''

    uri = resource_dict.get('uri')
    if not uri or uri == 'None':
        dataset_id = dataset_id_from_resource(resource_dict)

        uri = '{0}/dataset/{1}/resource/{2}'.format(catalog_uri().rstrip('/'),
                                                    dataset_id,
                                                    resource_dict['id'])

    return uri


def publisher_uri_organization_fallback(dataset_dict):
    '''
    Builds a fallback dataset URI of the form
    `catalog_uri()` + '/organization/' + `organization id` field

    Check the documentation for `catalog_uri()` for the recommended ways of
    setting it.

    Returns a string with the publisher URI, or None if no URI could be
    generated.
    '''
    if dataset_dict.get('organization'):
        return '{0}/organization/{1}'.format(catalog_uri().rstrip('/'),
                                            dataset_dict['organization']['id'])

    return None

def dataset_id_from_resource(resource_dict):
    '''
    Finds the id for a dataset if not present on the resource dict
    '''
    dataset_id = resource_dict.get('package_id')
    if dataset_id:
        return dataset_id

    # CKAN < 2.3
    resource = model.Resource.get(resource_dict['id'])
    if resource:
        return resource.get_package_id()


def url_to_rdflib_format(_format):
    '''
    Translates the RDF formats used on the endpoints to rdflib ones
    '''
    if _format == 'ttl':
        _format = 'turtle'
    elif _format in ('rdf', 'xml'):
        _format = 'pretty-xml'
    elif _format == 'jsonld':
        _format = 'json-ld'

    return _format


def rdflib_to_url_format(_format):
    '''
    Translates RDF formats used by rdflib to the ones used on the endpoints
    '''
    if _format == 'turtle':
        _format = 'ttl'
    elif _format == 'pretty-xml':
        _format = 'xml'
    elif _format == 'json-ld':
        _format = 'jsonld'

    return _format


# For parsing {name};q=x and {name} style fields from the accept header
accept_re = re.compile("^(?P<ct>[^;]+)[ \t]*(;[ \t]*q=(?P<q>[0-9.]+)){0,1}$")


def parse_accept_header(accept_header=''):
    '''
    Parses the supplied accept header and tries to determine
    which content types we can provide in the response.

    We will always provide html as the default if we can't see anything else
    but we will also need to take into account the q score.

    Returns the format string if there is a suitable RDF format to return, None
    otherwise.
    '''
    if accept_header is None:
        accept_header = ''

    # For compatibility, use 'rdf' for application/rdf+xml
    content_types = CONTENT_TYPES.copy()
    content_types.pop('xml')

    accepted_media_types = dict((value, key)
                                for key, value
                                in content_types.items())

    accepted_media_types_wildcard = {}
    for media_type, _format in accepted_media_types.items():
        _type = media_type.split('/')[0]
        if _type not in accepted_media_types_wildcard:
            accepted_media_types_wildcard[_type] = _format

    acceptable = {}
    for typ in accept_header.split(','):
        m = accept_re.match(typ)
        if m:
            key = m.groups(0)[0].strip()
            qscore = m.groups(0)[2] or 1.0
            acceptable[key] = float(qscore)

    for media_type in sorted(iter(acceptable.items()),
                             key=operator.itemgetter(1),
                             reverse=True):

        if media_type[0] == 'text/html':
            return None

        if media_type[0] in accepted_media_types:
            return accepted_media_types[media_type[0]]

        if '/' in media_type[0] and media_type[0].split('/')[1] == '*':
            _type = media_type[0].split('/')[0]
            if _type in accepted_media_types_wildcard:
                return accepted_media_types_wildcard[_type]

    return None


def generate_static_json(output):
    data_dict = {'page': 0}

    output.write(u"[")

    while True:
        try:
            data_dict['page'] = data_dict['page'] + 1
            datasets = \
                toolkit.get_action('dcat_datasets_list')({},
                                                           data_dict)
        except toolkit.ValidationError as e:
            log.exception(e)
            break

        if not datasets:
            break

        for dataset in datasets:
            output.write(json.dumps(dataset))

    output.write(u"]")


def check_access_header():
    _format = None

    # Check Accept headers
    accept_header = toolkit.request.headers.get('Accept', '')
    if accept_header:
        _format = parse_accept_header(accept_header)
    return _format


def dcat_json_page():
     data_dict = {
         'page': toolkit.request.params.get('page'),
         'modified_since': toolkit.request.params.get('modified_since'),
     }

     try:
         datasets = toolkit.get_action('dcat_datasets_list')({},
                                                             data_dict)
     except toolkit.ValidationError as e:
         return toolkit.abort(409, str(e))

     return datasets


def read_dataset_page(_id, _format):
    if not _format:
        _format = check_access_header()

    if not _format:
        return read_endpoint(_get_package_type(_id), _id)

    _profiles = toolkit.request.params.get('profiles')
    if _profiles:
        _profiles = _profiles.split(',')

    try:
        response = toolkit.get_action('dcat_dataset_show')({}, {'id': _id,
            'format': _format, 'profiles': _profiles})
    except toolkit.ObjectNotFound:
        toolkit.abort(404)
    except (toolkit.ValidationError, RDFProfileException) as e:
        toolkit.abort(409, str(e))

    from flask import make_response
    response = make_response(response)
    response.headers['Content-type'] = CONTENT_TYPES[_format]

    return response

def read_catalog_page(_format):
    if not _format:
        _format = check_access_header()

    if not _format:
        return index_endpoint()

    _profiles = toolkit.request.params.get('profiles')
    if _profiles:
        _profiles = _profiles.split(',')

    fq = toolkit.request.params.get('fq')
    if _profiles and 'euro_dcat_ap_hvd_220' in _profiles:
        fq = 'extras_applicable_legislation:"http://data.europa.eu/eli/reg_impl/2023/138/oj"'

    data_dict = {
        'page': toolkit.request.params.get('page'),
        'modified_since': toolkit.request.params.get('modified_since'),
        'q': toolkit.request.params.get('q'),
        'fq': fq,
        'format': _format,
        'profiles': _profiles,
    }

    try:
        response = toolkit.get_action('dcat_catalog_show')({}, data_dict)
    except (toolkit.ValidationError, RDFProfileException) as e:
        toolkit.abort(409, str(e))

    from flask import make_response
    response = make_response(response)
    response.headers['Content-type'] = CONTENT_TYPES[_format]

    return response


def endpoints_enabled():
    return toolkit.asbool(config.get(ENABLE_RDF_ENDPOINTS_CONFIG, True))


def get_endpoint(_type='dataset'):
    return 'dcat.read_dataset' if _type == 'dataset' else 'dcat.read_catalog'
