from pylons import config
from dateutil.parser import parse as dateutil_parse

from ckan.plugins import toolkit

import ckanext.dcat.converters as converters

from ckanext.dcat.processors import RDFSerializer


def dcat_dataset_show(context, data_dict):

    dataset_dict = toolkit.get_action('package_show')(context, data_dict)

    serializer = RDFSerializer()

    output = serializer.serialize_dataset(dataset_dict,
                                          _format=data_dict.get('format'))

    return output


@toolkit.side_effect_free
def dcat_catalog_show(context, data_dict):

    dataset_dicts = _search_ckan_datasets(context, data_dict)

    serializer = RDFSerializer()

    output = serializer.serialize_catalog({}, dataset_dicts,
                                          _format=data_dict.get('format'))

    return output


@toolkit.side_effect_free
def dcat_datasets_list(context, data_dict):

    ckan_datasets = _search_ckan_datasets(context, data_dict)

    return [converters.ckan_to_dcat(ckan_dataset)
            for ckan_dataset in ckan_datasets]


def _search_ckan_datasets(context, data_dict):

    n = int(config.get('ckanext.dcat.datasets_per_page', 100))
    page = data_dict.get('page', 1) or 1

    wrong_page_exception = toolkit.ValidationError(
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
            raise toolkit.ValidationError(
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

    query = toolkit.get_action('package_search')(context, search_data_dict)

    return query['results']
