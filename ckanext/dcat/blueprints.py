# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, make_response

from ckantoolkit import config

from ckan.views.dataset import CreateView

import ckan.plugins.toolkit as toolkit
import ckanext.dcat.utils as utils

dcat = Blueprint(
    'dcat',
    __name__,
    url_defaults={u'package_type': u'dataset'}
)


def read_catalog(_format=None, package_type=None):
    return utils.read_catalog_page(_format)


def read_dataset(_id, _format=None, package_type=None):
    return utils.read_dataset_page(_id, _format)

if toolkit.asbool(config.get(utils.ENABLE_RDF_ENDPOINTS_CONFIG, True)):

    # requirements={'_format': 'xml|rdf|n3|ttl|jsonld'}
    dcat.add_url_rule(config.get('ckanext.dcat.catalog_endpoint',
                                 utils.DEFAULT_CATALOG_ENDPOINT).replace(
                                     '{_format}', '<_format>'),
                      view_func=read_catalog)
    dcat.add_url_rule('/dataset/<_id>.<_format>', view_func=read_dataset)

if toolkit.asbool(config.get(utils.ENABLE_CONTENT_NEGOTIATION_CONFIG)):
    dcat.add_url_rule('/', view_func=read_catalog)

    dcat.add_url_rule('/dataset/new', view_func=CreateView.as_view(str(u'new')))
    dcat.add_url_rule('/dataset/<_id>', view_func=read_dataset)

dcat_json_interface = Blueprint('dcat_json_interface', __name__)


def dcat_json():
    datasets = utils.dcat_json_page()
    return jsonify(datasets)


dcat_json_interface.add_url_rule(config.get('ckanext.dcat.json_endpoint',
                                            '/dcat.json'),
                                 view_func=dcat_json)
