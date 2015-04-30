import json

from ckan.plugins import toolkit

if toolkit.check_ckan_version(min_version='2.1'):
    BaseController = toolkit.BaseController
else:
    from ckan.lib.base import BaseController

CONTENT_TYPES = {
    'rdf': 'application/rdf+xml',
    'xml': 'application/rdf+xml',
    'n3': 'text/n3',
    'ttl': 'text/turtle',
}


class DCATController(BaseController):

    def read_catalog(self, _format='rdf'):

        data_dict = {
            'page': toolkit.request.params.get('page'),
            'modified_since': toolkit.request.params.get('modified_since'),
            'format': _format,
        }

        toolkit.response.headers.update(
            {'Content-type': CONTENT_TYPES[_format]})
        return toolkit.get_action('dcat_catalog_show')({}, data_dict)

    def read_dataset(self, _id, _format='rdf'):

        toolkit.response.headers.update(
            {'Content-type': CONTENT_TYPES[_format]})
        return toolkit.get_action('dcat_dataset_show')({}, {'id': _id,
                                                            'format': _format})

    def dcat_json(self):

        data_dict = {
            'page': toolkit.request.params.get('page'),
            'modified_since': toolkit.request.params.get('modified_since'),
        }

        try:
            datasets = toolkit.get_action('dcat_datasets_list')({},
                                                                data_dict)
        except toolkit.ValidationError, e:
            toolkit.abort(409, str(e))

        content = json.dumps(datasets)

        toolkit.response.headers['Content-Type'] = 'application/json'
        toolkit.response.headers['Content-Length'] = len(content)

        return content



