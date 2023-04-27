import json
from ckan.plugins import toolkit

import ckanext.dcat.utils as utils


class DCATController(toolkit.BaseController):

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
