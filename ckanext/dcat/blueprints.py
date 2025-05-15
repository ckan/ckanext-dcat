# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, make_response

import ckantoolkit as toolkit

from ckan.views.dataset import CreateView

import ckan.plugins.toolkit as toolkit
import ckanext.dcat.utils as utils
from ckanext.dcat.helpers import endpoints_enabled, croissant as croissant_serialization

config = toolkit.config


dcat = Blueprint(
    'dcat',
    __name__,
    url_defaults={u'package_type': u'dataset'}
)


def read_catalog(_format=None, package_type=None):
    return utils.read_catalog_page(_format)


def read_dataset(_id, _format=None, package_type=None):
    return utils.read_dataset_page(_id, _format)


if endpoints_enabled():

    # requirements={'_format': 'xml|rdf|n3|ttl|jsonld'}
    dcat.add_url_rule(config.get('ckanext.dcat.catalog_endpoint',
                                 utils.DEFAULT_CATALOG_ENDPOINT).replace(
                                     '{_format}', '<_format>'),
                      view_func=read_catalog)

    # TODO: Generalize for all dataset types
    dcat.add_url_rule('/dataset_series/<_id>.<_format>', view_func=read_dataset)
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


croissant = Blueprint('croissant', __name__)


def read_dataset_croissant(_id):

    try:
        user_name = (
            toolkit.current_user.name
            if hasattr(toolkit, "current_user")
            else toolkit.g.user
        )

        context = {
            'user': user_name,
        }
        data_dict = {'id': _id}

        dataset_dict = toolkit.get_action("package_show")(context, data_dict)
    except (toolkit.ObjectNotFound, toolkit.NotAuthorized):
        return toolkit.abort(
            404,
            toolkit._("Dataset not found or you have no permission to view it")
        )

    response = make_response(croissant_serialization(dataset_dict))
    response.headers["Content-type"] = "application/ld+json"

    return response

croissant.add_url_rule('/dataset/<_id>/croissant.jsonld', view_func=read_dataset_croissant)
