from pylons import config

from ckan import plugins as p
try:
    from ckan.lib.plugins import DefaultTranslation
except ImportError:
    class DefaultTranslation():
        pass


from ckanext.dcat.logic import (dcat_dataset_show,
                                dcat_catalog_show,
                                dcat_catalog_search,
                                dcat_datasets_list,
                                dcat_auth,
                                )
from ckanext.dcat import utils

DEFAULT_CATALOG_ENDPOINT = '/catalog.{_format}'
CUSTOM_ENDPOINT_CONFIG = 'ckanext.dcat.catalog_endpoint'
ENABLE_RDF_ENDPOINTS_CONFIG = 'ckanext.dcat.enable_rdf_endpoints'
ENABLE_CONTENT_NEGOTIATION_CONFIG = 'ckanext.dcat.enable_content_negotiation'
TRANSLATE_KEYS_CONFIG = 'ckanext.dcat.translate_keys'


class DCATPlugin(p.SingletonPlugin, DefaultTranslation):

    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.ITemplateHelpers, inherit=True)
    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IActions, inherit=True)
    p.implements(p.IAuthFunctions, inherit=True)
    p.implements(p.IPackageController, inherit=True)
    if p.toolkit.check_ckan_version(min_version='2.5.0'):
        p.implements(p.ITranslation, inherit=True)

    # IConfigurer
    def update_config(self, config):
        p.toolkit.add_template_directory(config, 'templates')

        # Check catalog URI on startup to emit a warning if necessary
        utils.catalog_uri()

        # Check custom catalog endpoint
        custom_endpoint = config.get(CUSTOM_ENDPOINT_CONFIG)
        if custom_endpoint:
            if not custom_endpoint[:1] == '/':
                raise Exception(
                    '"{0}" should start with a backslash (/)'.format(
                        CUSTOM_ENDPOINT_CONFIG))
            if '{_format}' not in custom_endpoint:
                raise Exception(
                    '"{0}" should contain {{_format}}'.format(
                        CUSTOM_ENDPOINT_CONFIG))

    # ITemplateHelpers
    def get_helpers(self):
        return {
            'helper_available': utils.helper_available,
        }

    # IRoutes
    def before_map(self, _map):

        controller = 'ckanext.dcat.controllers:DCATController'

        if p.toolkit.asbool(config.get(ENABLE_RDF_ENDPOINTS_CONFIG, True)):

            _map.connect('dcat_catalog',
                         config.get('ckanext.dcat.catalog_endpoint',
                                    DEFAULT_CATALOG_ENDPOINT),
                         controller=controller, action='read_catalog',
                         requirements={'_format': 'xml|rdf|n3|ttl|jsonld'})

            _map.connect('dcat_dataset', '/dataset/{_id}.{_format}',
                         controller=controller, action='read_dataset',
                         requirements={'_format': 'xml|rdf|n3|ttl|jsonld'})

        if p.toolkit.asbool(config.get(ENABLE_CONTENT_NEGOTIATION_CONFIG)):

            _map.connect('home', '/', controller=controller,
                         action='read_catalog')

            _map.connect('add dataset', '/dataset/new', controller='package', action='new')
            _map.connect('dataset_read', '/dataset/{_id}',
                         controller=controller, action='read_dataset',
                         ckan_icon='sitemap')

        return _map

    # IActions
    def get_actions(self):
        return {
            'dcat_dataset_show': dcat_dataset_show,
            'dcat_catalog_show': dcat_catalog_show,
            'dcat_catalog_search': dcat_catalog_search,
        }

    # IAuthFunctions
    def get_auth_functions(self):
        return {
            'dcat_dataset_show': dcat_auth,
            'dcat_catalog_show': dcat_auth,
            'dcat_catalog_search': dcat_auth,
        }

    # IPackageController
    def after_show(self, context, data_dict):

        # check if config is enabled to translate keys (default: True)
        if not p.toolkit.asbool(config.get(TRANSLATE_KEYS_CONFIG, True)):
            return data_dict

        if context.get('for_view'):
            field_labels = utils.field_labels()

            def set_titles(object_dict):
                for key, value in object_dict.iteritems():
                    if key in field_labels:
                        object_dict[field_labels[key]] = object_dict[key]
                        del object_dict[key]

            for resource in data_dict.get('resources', []):
                set_titles(resource)

            for extra in data_dict.get('extras', []):
                if extra['key'] in field_labels:
                    extra['key'] = field_labels[extra['key']]

        return data_dict


class DCATJSONInterface(p.SingletonPlugin):

    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IActions)
    p.implements(p.IAuthFunctions, inherit=True)

    # IRoutes
    def after_map(self, map):

        controller = 'ckanext.dcat.controllers:DCATController'
        route = config.get('ckanext.dcat.json_endpoint', '/dcat.json')
        map.connect(route, controller=controller, action='dcat_json')

        return map

    # IActions
    def get_actions(self):
        return {
            'dcat_datasets_list': dcat_datasets_list,
        }

    # IAuthFunctions
    def get_auth_functions(self):
        return {
            'dcat_datasets_list': dcat_auth,
        }


class StructuredDataPlugin(p.SingletonPlugin):
    p.implements(p.ITemplateHelpers, inherit=True)

    # ITemplateHelpers
    def get_helpers(self):
        return {
            'structured_data': utils.structured_data,
        }

