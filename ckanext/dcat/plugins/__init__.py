# -*- coding: utf-8 -*-

from builtins import object
import os

import six

from ckantoolkit import config

from ckan import plugins as p
try:
    from ckan.lib.plugins import DefaultTranslation
except ImportError:
    class DefaultTranslation(object):
        pass


from ckanext.dcat.logic import (dcat_dataset_show,
                                dcat_catalog_show,
                                dcat_catalog_search,
                                dcat_datasets_list,
                                dcat_auth,
                                sparql_query,
                                sparql_update,
                                sparql_clear,
                                sparql_query_auth,
                                sparql_update_auth,
                                sparql_clear_auth
                                )
from ckanext.dcat import utils, sparql
import logging

log = logging.getLogger(__name__)

if p.toolkit.check_ckan_version('2.9'):
    from ckanext.dcat.plugins.flask_plugin import (
        MixinDCATPlugin, MixinDCATJSONInterface, MixinSPARQLPlugin
    )
else:
    from ckanext.dcat.plugins.pylons_plugin import (
        MixinDCATPlugin, MixinDCATJSONInterface, MixinSPARQLPlugin
    )


CUSTOM_ENDPOINT_CONFIG = 'ckanext.dcat.catalog_endpoint'
TRANSLATE_KEYS_CONFIG = 'ckanext.dcat.translate_keys'

HERE = os.path.abspath(os.path.dirname(__file__))
I18N_DIR = os.path.join(HERE, u"../i18n")


class DCATPlugin(MixinDCATPlugin, p.SingletonPlugin, DefaultTranslation):

    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.ITemplateHelpers, inherit=True)
    p.implements(p.IActions, inherit=True)
    p.implements(p.IAuthFunctions, inherit=True)
    p.implements(p.IPackageController, inherit=True)
    if p.toolkit.check_ckan_version(min_version='2.5.0'):
        p.implements(p.ITranslation, inherit=True)

    # ITranslation

    def i18n_directory(self):
        return I18N_DIR

    # IConfigurer

    def update_config(self, config):
        p.toolkit.add_template_directory(config, '../templates')
        p.toolkit.add_resource('../assets', 'ckanext-dcat')

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

    def after_show(self, context, data_dict):

        # check if config is enabled to translate keys (default: True)
        if not p.toolkit.asbool(config.get(TRANSLATE_KEYS_CONFIG, True)):
            return data_dict

        if context.get('for_view'):
            field_labels = utils.field_labels()

            def set_titles(object_dict):
                for key, value in six.iteritems(object_dict.copy()):
                    if key in field_labels:
                        object_dict[field_labels[key]] = object_dict[key]
                        del object_dict[key]

            for resource in data_dict.get('resources', []):
                set_titles(resource)

            for extra in data_dict.get('extras', []):
                if extra['key'] in field_labels:
                    extra['key'] = field_labels[extra['key']]

        return data_dict


class DCATJSONInterface(MixinDCATJSONInterface, p.SingletonPlugin):
    p.implements(p.IActions)
    p.implements(p.IAuthFunctions, inherit=True)

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


class SPARQLPlugin(MixinSPARQLPlugin, p.SingletonPlugin):
    p.implements(p.IConfigurable, inherit=True)
    p.implements(p.IPackageController, inherit=True)
    p.implements(p.IActions)
    p.implements(p.IAuthFunctions, inherit=True)

    # IConfigurable

    def configure(self, config):
        self.sparql = sparql.SPARQLClient(config.get('ckanext.dcat.sparql.query_endpoint'),
                                          update_endpoint=config.get('ckanext.dcat.sparql.update_endpoint'),
                                          username=config.get('ckanext.dcat.sparql.username'),
                                          password=config.get('ckanext.dcat.sparql.password'))
        self.profiles = p.toolkit.aslist(config.get('ckanext.dcat.sparql.profiles', []))

    # IPackageController

    def before_index(self, pkg_dict):
        try:
            self.sparql.update_dataset(pkg_dict, self.profiles)
        except Exception as e:
            log.error('Could not update dataset %s to SPARQL server: %s', pkg_dict['id'], e)

        return pkg_dict

    def after_delete(self, context, pkg_dict):
        try:
            self.sparql.remove_dataset(pkg_dict['id'])
        except Exception as e:
            log.error('Could not remove dataset %s from SPARQL server: %s', pkg_dict['id'], e)

    # IActions

    def get_actions(self):
        return {
            'sparql_query': sparql_query,
            'sparql_update': sparql_update,
            'sparql_clear': sparql_clear,
        }

    # IAuthFunctions

    def get_auth_functions(self):
        return {
            'sparql_query': sparql_query_auth,
            'sparql_update': sparql_update_auth,
            'sparql_clear': sparql_clear_auth,
        }
