import json
from ckan.plugins import toolkit

import ckanext.dcat.utils as utils


if toolkit.check_ckan_version(min_version='2.1'):
    BaseController = toolkit.BaseController
else:
    from ckan.lib.base import BaseController


class DCATController(BaseController):

    def read_catalog(self, _format=None):
        return utils.read_catalog_page(_format)

    def read_dataset(self, _id, _format=None):
        return utils.read_dataset_page(_id, _format)

    def dcat_json(self):
       datasets =  utils.dcat_json_page()
       content = json.dumps(datasets)

       toolkit.response.headers['Content-Type'] = 'application/json'
       toolkit.response.headers['Content-Length'] = len(content)

       return content
