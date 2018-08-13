import json

from ckan import model
from ckan.plugins import toolkit

if toolkit.check_ckan_version(min_version='2.1'):
    BaseController = toolkit.BaseController
else:
    from ckan.lib.base import BaseController

if toolkit.check_ckan_version(max_version='2.8.99'):
    from ckan.controllers.package import PackageController
    from ckan.controllers.home import HomeController
    read_endpoint = PackageController().read
    index_endpoint = HomeController().index
else:
    from ckan.views.home import index as index_endpoint
    from ckan.views.dataset import read as read_endpoint

from ckanext.dcat.utils import CONTENT_TYPES, parse_accept_header


def _get_package_type(id):
    """
    Given the id of a package this method will return the type of the
    package, or 'dataset' if no type is currently set
    """
    pkg = model.Package.get(id)
    if pkg:
        return pkg.type or u'dataset'
    return None


def check_access_header():
    _format = None

    # Check Accept headers
    accept_header = toolkit.request.headers.get('Accept', '')
    if accept_header:
        _format = parse_accept_header(accept_header)
    return _format


class DCATController(BaseController):

    def read_catalog(self, _format=None):

        if not _format:
            _format = check_access_header()

        if not _format:
            return index_endpoint()

        _profiles = toolkit.request.params.get('profiles')
        if _profiles:
            _profiles = _profiles.split(',')

        data_dict = {
            'page': toolkit.request.params.get('page'),
            'modified_since': toolkit.request.params.get('modified_since'),
            'format': _format,
            'profiles': _profiles,
        }

        toolkit.response.headers.update(
            {'Content-type': CONTENT_TYPES[_format]})
        try:
            return toolkit.get_action('dcat_catalog_show')({}, data_dict)
        except toolkit.ValidationError, e:
            toolkit.abort(409, str(e))

    def read_dataset(self, _id, _format=None):

        if not _format:
            _format = check_access_header()

        if not _format:
            if toolkit.check_ckan_version(max_version='2.8.99'):
                return read_endpoint(_id)
            else:
                return read_endpoint(_get_package_type(_id), _id)

        _profiles = toolkit.request.params.get('profiles')
        if _profiles:
            _profiles = _profiles.split(',')

        toolkit.response.headers.update(
            {'Content-type': CONTENT_TYPES[_format]})

        try:
            result = toolkit.get_action('dcat_dataset_show')({}, {'id': _id,
                'format': _format, 'profiles': _profiles})
        except toolkit.ObjectNotFound:
            toolkit.abort(404)

        return result

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



