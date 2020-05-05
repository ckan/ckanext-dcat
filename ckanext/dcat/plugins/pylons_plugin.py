# -*- coding: utf-8 -*-

from ckantoolkit import config
import ckan.plugins as p

import ckanext.dcat.utils as utils

class MixinDCATPlugin(p.SingletonPlugin):
    p.implements(p.IRoutes, inherit=True)

    # IRoutes

    def before_map(self, _map):

        controller = 'ckanext.dcat.controllers:DCATController'

        if p.toolkit.asbool(config.get(utils.ENABLE_RDF_ENDPOINTS_CONFIG, True)):

            _map.connect('dcat_catalog',
                         config.get('ckanext.dcat.catalog_endpoint',
                                    utils.DEFAULT_CATALOG_ENDPOINT),
                         controller=controller, action='read_catalog',
                         requirements={'_format': 'xml|rdf|n3|ttl|jsonld'})

            _map.connect('dcat_dataset', '/dataset/{_id}.{_format}',
                         controller=controller, action='read_dataset',
                         requirements={'_format': 'xml|rdf|n3|ttl|jsonld'})

        if p.toolkit.asbool(config.get(utils.ENABLE_CONTENT_NEGOTIATION_CONFIG)):

            _map.connect('home', '/', controller=controller,
                         action='read_catalog')

            _map.connect('add dataset', '/dataset/new', controller='package', action='new')
            _map.connect('dataset_read', '/dataset/{_id}',
                         controller=controller, action='read_dataset',
                         ckan_icon='sitemap')

        return _map

class MixinDCATJSONInterface(p.SingletonPlugin):
    p.implements(p.IRoutes, inherit=True)

    # IRoutes

    def after_map(self, map):

        controller = 'ckanext.dcat.controllers:DCATController'
        route = config.get('ckanext.dcat.json_endpoint', '/dcat.json')
        map.connect(route, controller=controller, action='dcat_json')

        return map
