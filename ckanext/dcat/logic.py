from __future__ import division
import math

from pylons import config
from dateutil.parser import parse as dateutil_parse

from ckan.plugins import toolkit

import ckanext.dcat.converters as converters

from ckanext.dcat.processors import RDFSerializer


DATASETS_PER_PAGE = 100

wrong_page_exception = toolkit.ValidationError(
    'Page param must be a positive integer starting in 1')


def dcat_dataset_show(context, data_dict):

    toolkit.check_access('dcat_dataset_show', context, data_dict)

    dataset_dict = toolkit.get_action('package_show')(context, data_dict)

    serializer = RDFSerializer(profiles=data_dict.get('profiles'))

    output = serializer.serialize_dataset(dataset_dict,
                                          _format=data_dict.get('format'))

    return output


@toolkit.side_effect_free
def dcat_catalog_show(context, data_dict):

    toolkit.check_access('dcat_catalog_show', context, data_dict)

    query = _search_ckan_datasets(context, data_dict)
    dataset_dicts = query['results']
    pagination_info = _pagination_info(query, data_dict)

    serializer = RDFSerializer(profiles=data_dict.get('profiles'))

    output = serializer.serialize_catalog({}, dataset_dicts,
                                          _format=data_dict.get('format'),
                                          pagination_info=pagination_info)

    return output


@toolkit.side_effect_free
def dcat_catalog_search(context, data_dict):

    toolkit.check_access('dcat_catalog_search', context, data_dict)

    query = _search_ckan_datasets(context, data_dict)

    dataset_dicts = query['results']
    pagination_info = _pagination_info(query, data_dict)

    serializer = RDFSerializer(profiles=data_dict.get('profiles'))

    output = serializer.serialize_catalog({}, dataset_dicts,
                                          _format=data_dict.get('format'),
                                          pagination_info=pagination_info)

    return output


@toolkit.side_effect_free
def dcat_datasets_list(context, data_dict):

    toolkit.check_access('dcat_datasets_list', context, data_dict)

    ckan_datasets = _search_ckan_datasets(context, data_dict)['results']

    return [converters.ckan_to_dcat(ckan_dataset)
            for ckan_dataset in ckan_datasets]


def _search_ckan_datasets(context, data_dict):

    n = int(config.get('ckanext.dcat.datasets_per_page', DATASETS_PER_PAGE))
    page = data_dict.get('page', 1) or 1

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
            raise toolkit.ValidationError(
                'Wrong modified date format. Use ISO-8601 format')

    search_data_dict = {
        'rows': n,
        'start': n * (page - 1),
        'sort': 'metadata_modified desc',
    }

    search_data_dict['q'] = data_dict.get('q', '*:*')
    search_data_dict['fq'] = data_dict.get('fq')
    search_data_dict['fq_list'] = []

    # Exclude certain dataset types
    search_data_dict['fq_list'].append('-dataset_type:harvest')
    search_data_dict['fq_list'].append('-dataset_type:showcase')

    if modified_since:
        search_data_dict['fq_list'].append(
            'metadata_modified:[{0} TO NOW]'.format(modified_since))

    query = toolkit.get_action('package_search')(context, search_data_dict)

    return query


def _pagination_info(query, data_dict):
    '''
    Creates a pagination_info dict to be passed to the serializers

    `query` is the output of `package_search` and `data_dict`
    contains the request params.

    The keys for the dictionary are:

    * `count` (total elements)
    * `items_per_page` (`ckanext.dcat.datasets_per_page` or 100)
    * `current`
    * `first`
    * `last`
    * `next`
    * `previous`

    Returns a dict
    '''

    def _page_url(page):

        base_url = config.get('ckan.site_url', '').strip('/')
        if not base_url:
            base_url = toolkit.request.host_url
        base_url = '%s%s' % (
            base_url, toolkit.request.path)

        params = [p for p in toolkit.request.params.iteritems()
                  if p[0] != 'page']
        if params:
            qs = '&'.join(['{0}={1}'.format(p[0], p[1]) for p in params])
            return '{0}?{1}&page={2}'.format(
                base_url,
                qs,
                page
            )
        else:
            return '{0}?page={1}'.format(
                base_url,
                page
            )

    try:
        page = int(data_dict.get('page', 1) or 1)
        if page < 1:
            raise wrong_page_exception
    except ValueError:
        raise wrong_page_exception

    if query['count'] == 0:
        return {}

    items_per_page = int(config.get('ckanext.dcat.datasets_per_page',
                                    DATASETS_PER_PAGE))
    pagination_info = {
        'count': query['count'],
        'items_per_page': items_per_page,
    }

    pagination_info['current'] = _page_url(page)
    pagination_info['first'] = _page_url(1)

    last_page = int(math.ceil(query['count'] / items_per_page)) or 1
    pagination_info['last'] = _page_url(last_page)

    if page > 1:
        if ((page - 1) * items_per_page
                + len(query['results'])) <= query['count']:
            previous_page = page - 1
        else:
            previous_page = last_page

        pagination_info['previous'] = _page_url(previous_page)

    if page * items_per_page < query['count']:
        pagination_info['next'] = _page_url(page + 1)

    return pagination_info


@toolkit.auth_allow_anonymous_access
def dcat_auth(context, data_dict):
    '''
    All users can access DCAT endpoints by default
    '''
    return {'success': True}
