# -*- coding: utf-8 -*-

import ckan.plugins as p

import ckanext.dcat.cli as cli
import ckanext.dcat.blueprints as blueprints


class MixinDCATPlugin(p.SingletonPlugin):
    p.implements(p.IClick)
    p.implements(p.IBlueprint)

    # IClick

    def get_commands(self):
        return cli.get_commands()

    # IBlueprint

    def get_blueprint(self):
        return [blueprints.dcat]


class MixinDCATJSONInterface(p.SingletonPlugin):
    p.implements(p.IBlueprint)

    # IBlueprint

    def get_blueprint(self):
        return [blueprints.dcat_json_interface]
