import json
import logging

from pylons import config
from dateutil.parser import parse as dateutil_parse

from ckan import plugins as p

if p.toolkit.check_ckan_version(min_version='2.1'):
    BaseController = p.toolkit.BaseController
    response = p.toolkit.response
else:
    from ckan.lib.base import BaseController
    from pylons import response

import ckanext.dcat.converters as converters

log = logging.getLogger(__name__)


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
            'dcat_catalog_info': dcat_catalog_info,
            'dcat_latest_revision': dcat_latest_revision
        }


class DCATController(BaseController):

    def dcat_json(self):

        data_dict = {
            'page': p.toolkit.request.params.get('page'),
            'modified_since': p.toolkit.request.params.get('modified_since'),
        }

        try:
            # Generate the dcat:catalog elements for the result.
            catalog = p.toolkit.get_action('dcat_catalog_info')({},
                                                            data_dict)
        except p.toolkit.ValidationError, e:
            p.toolkit.abort(409, str(e))

        try:
            datasets = p.toolkit.get_action('dcat_datasets_list')({},
                                                                  data_dict)
        except p.toolkit.ValidationError, e:
            p.toolkit.abort(409, str(e))

        # We don't want to ever use json.dumps as it means we have the
        # original dicts AND the JSON string in memory. Ideally we'd use
        # json.dump(response, datasets) which will write straight to the
        # stream, but then we'd lose the Content-length
        catalog["dataset"] = datasets
        content = json.dumps(catalog)

        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Length'] = len(content)

        return content


def dcat_latest_revision(context, data_dict):
    import ckan.model as model
    rev = model.Session.query(model.Revision).order_by("timestamp desc").first()
    if rev:
        return rev.timestamp.isoformat()
    return ''


def dcat_datasets_list(context, data_dict):

    ckan_datasets = _search_ckan_datasets(context, data_dict)

    return [converters.ckan_to_dcat(ckan_dataset)
            for ckan_dataset in ckan_datasets]


def dcat_catalog_info(context, data_dict):
    """
    Returns a dict containing the fields needed for the catalog element

    Some fields are missing:
        'issued' is missing as now obvious way to determine when the
        catalog went live.
        'license' is missing as it isn't clear that the catalog has a
        license.
    """
    try:
        revision = p.toolkit.get_action('dcat_latest_revision')({},{})
    except Exception, e:
        log.exception(e)
        revision = ''

    return {
        'title': config.get('ckan.site_title', 'CKAN'),
        'description': config.get('ckan.site_description', ''),
        'homepage': config.get('ckan.site_url', ''),
        'language': config.get('ckan.locale_default', 'en'),
        'modified': revision,
    }


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
