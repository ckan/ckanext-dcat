# -*- coding: utf-8 -*-

from builtins import object
import os

from ckantoolkit import config

from ckan import plugins as p

from ckan.lib.plugins import DefaultTranslation

import ckanext.dcat.blueprints as blueprints
import ckanext.dcat.cli as cli

from ckanext.dcat.logic import (dcat_dataset_show,
                                dcat_catalog_show,
                                dcat_catalog_search,
                                dcat_datasets_list,
                                dcat_auth,
                                )
from ckanext.dcat import utils


CUSTOM_ENDPOINT_CONFIG = 'ckanext.dcat.catalog_endpoint'
TRANSLATE_KEYS_CONFIG = 'ckanext.dcat.translate_keys'

HERE = os.path.abspath(os.path.dirname(__file__))
I18N_DIR = os.path.join(HERE, u"../i18n")


class DCATPlugin(p.SingletonPlugin, DefaultTranslation):

    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.ITemplateHelpers, inherit=True)
    p.implements(p.IActions, inherit=True)
    p.implements(p.IAuthFunctions, inherit=True)
    p.implements(p.IPackageController, inherit=True)
    p.implements(p.ITranslation, inherit=True)
    p.implements(p.IClick)
    p.implements(p.IBlueprint)

    # IClick

    def get_commands(self):
        return cli.get_commands()

    # IBlueprint

    def get_blueprint(self):
        return [blueprints.dcat]

    # ITranslation

    def i18n_directory(self):
        return I18N_DIR

    # IConfigurer

    def update_config(self, config):
        p.toolkit.add_template_directory(config, '../templates')

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
            'dcat_get_endpoint': utils.get_endpoint,
            'dcat_endpoints_enabled': utils.endpoints_enabled,
        }

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

    # CKAN < 2.10 hooks
    def after_show(self, context, data_dict):
        return self.after_dataset_show(context, data_dict)

    def before_index(self, dataset_dict):
        return self.before_dataset_index(dataset_dict)

    # CKAN >= 2.10 hooks
    def after_dataset_show(self, context, data_dict):

        # check if config is enabled to translate keys (default: True)
        if not p.toolkit.asbool(config.get(TRANSLATE_KEYS_CONFIG, True)):
            return data_dict

        if context.get('for_view'):
            field_labels = utils.field_labels()

            def set_titles(object_dict):
                for key, value in object_dict.copy().items():
                    if key in field_labels:
                        object_dict[field_labels[key]] = object_dict[key]
                        del object_dict[key]

            for resource in data_dict.get('resources', []):
                set_titles(resource)

            for extra in data_dict.get('extras', []):
                if extra['key'] in field_labels:
                    extra['key'] = field_labels[extra['key']]

        return data_dict

    def before_dataset_index(self, dataset_dict):
        schema = None
        try:
            schema_show = p.toolkit.get_action("scheming_dataset_schema_show")
            try:
                schema = schema_show({}, {"type": dataset_dict["type"]})
            except p.toolkit.ObjectNotFound:
                pass
        except KeyError:
            pass

        if schema:
            for field in schema['dataset_fields']:
                if field['field_name'] in dataset_dict and 'repeating_subfields' in field:
                    for index, item in enumerate(dataset_dict[field['field_name']]):
                        for key in item:
                            # Index a flattened version
                            new_key = f'{field["field_name"]}_{index}_{key}'

                            dataset_dict[new_key] = dataset_dict[field['field_name']][index][key]
                    dataset_dict.pop(field['field_name'], None)

        return dataset_dict


class DCATJSONInterface(p.SingletonPlugin):
    p.implements(p.IActions)
    p.implements(p.IAuthFunctions, inherit=True)
    p.implements(p.IBlueprint)

    # IBlueprint

    def get_blueprint(self):
        return [blueprints.dcat_json_interface]

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
