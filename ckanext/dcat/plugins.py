import json

from pylons import config
from dateutil.parser import parse as dateutil_parse

from ckan import plugins as p

import ckanext.dcat.converters as converters


class DCATJSONInterface(p.SingletonPlugin):

    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IActions)

    ## IRoutes
    def after_map(self, map):

        controller = 'ckanext.dcat.plugins:DCATController'
        route = config.get('ckanext.dcat.json_endpoint', '/dcat.json')
        map.connect(route, controller=controller, action='dcat_json')

        return map

    ## IActions
    def get_actions(self):
        return {
            'dcat_datasets_list': dcat_datasets_list,
        }


class DCATController(p.toolkit.BaseController):

    def dcat_json(self):

        data_dict = {
            'page': p.toolkit.request.params.get('page'),
            'modified_since': p.toolkit.request.params.get('modified_since'),
        }

        try:
            datasets = p.toolkit.get_action('dcat_datasets_list')({},
                                                                  data_dict)
        except p.toolkit.ValidationError, e:
            p.toolkit.abort(409, str(e))

        content = json.dumps(datasets)

        p.toolkit.response.headers['Content-Type'] = 'application/json'
        p.toolkit.response.headers['Content-Length'] = len(content)

        return content


def dcat_datasets_list(context, data_dict):

    ckan_datasets = _search_ckan_datasets(context, data_dict)

    return [converters.ckan_to_dcat(ckan_dataset)
            for ckan_dataset in ckan_datasets]


def _search_ckan_datasets(context, data_dict):

    n = int(config.get('ckanext.dcat.datasets_per_page', 100))
    page = data_dict.get('page', 1) or 1

    wrong_page_exception = p.toolkit.ValidationError(
        'Page param must be a positive integer starting in 1')
    try:
        page = int(page)
        if page < 1:
            raise wrong_page_exception
    except ValueError:
        raise wrong_page_exception

    modified_since = data_dict.get('modified_since')
    if modified_since:
        try:
            modified_since = dateutil_parse(modified_since).isoformat() + 'Z'
        except (ValueError, AttributeError):
            raise p.toolkit.ValidationError(
                'Wrong modified date format. Use ISO-8601 format')

    search_data_dict = {
        'q': '*:*',
        'fq': 'dataset_type:dataset',
        'rows': n,
        'start': n * (page - 1),
    }

    if modified_since:
        search_data_dict.update({
            'fq': 'metadata_modified:[{0} TO NOW]'.format(modified_since),
            'sort': 'metadata_modified desc',
        })

    query = p.toolkit.get_action('package_search')(context, search_data_dict)

    return query['results']
