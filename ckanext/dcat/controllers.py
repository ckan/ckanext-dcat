import json

from ckan.plugins import toolkit

if toolkit.check_ckan_version(min_version='2.1'):
    BaseController = toolkit.BaseController
else:
    from ckan.lib.base import BaseController


class DCATController(BaseController):

    def read(self, _id, _format='rdf'):

        if _format == 'ttl':
            _format = 'turtle'
        if _format == 'rdf':
            _format = 'xml'

        content_types = {
            'xml': 'application/rdf+xml',
            'n3': 'text/n3',
            'turtle': 'text/turtle',
        }

        toolkit.response.headers.update({'Content-type': content_types[_format]})
        return toolkit.get_action('dcat_dataset_show')({}, {'id': _id, 'format': _format})

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
