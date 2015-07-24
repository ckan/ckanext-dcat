from pylons import config

from ckan import plugins as p

from ckanext.dcat.logic import (dcat_dataset_show,
                                dcat_catalog_show,
                                dcat_catalog_search,
                                dcat_datasets_list,
                                dcat_auth,
                                )
from ckanext.dcat.utils import catalog_uri


class DCATPlugin(p.SingletonPlugin):

    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IActions, inherit=True)
    p.implements(p.IAuthFunctions, inherit=True)

    # IConfigurer
    def update_config(self, config):
        p.toolkit.add_template_directory(config, 'templates')

        # Check catalog URI on startup to emit a warning if necessary
        catalog_uri()

    # IRoutes
    def before_map(self, _map):

        controller = 'ckanext.dcat.controllers:DCATController'

        _map.connect('dcat_catalog', '/catalog.{_format}',
                     controller=controller, action='read_catalog',
                     requirements={'_format': 'xml|rdf|n3|ttl|jsonld'})

        _map.connect('dcat_dataset', '/dataset/{_id}.{_format}',
                     controller=controller, action='read_dataset',
                     requirements={'_format': 'xml|rdf|n3|ttl|jsonld'})
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
