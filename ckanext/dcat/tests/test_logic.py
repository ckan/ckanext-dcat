from builtins import range
from builtins import object

import mock
import pytest


from ckan.plugins import toolkit

from ckantoolkit import config
from ckantoolkit.tests import helpers, factories


from ckanext.dcat.logic import _pagination_info
from ckanext.dcat.processors import RDFParser


# Custom actions


@pytest.mark.usefixtures('with_plugins', 'clean_db')
def test_dataset_show_with_format():
    dataset = factories.Dataset(
        notes='Test dataset'
    )

    content = helpers.call_action('dcat_dataset_show', id=dataset['id'], _format='xml')

    # Parse the contents to check it's an actual serialization
    p = RDFParser()

    p.parse(content, _format='xml')

    dcat_datasets = [d for d in p.datasets()]

    assert len(dcat_datasets) == 1

    dcat_dataset = dcat_datasets[0]

    assert dcat_dataset['title'] == dataset['title']
    assert dcat_dataset['notes'] == dataset['notes']


@pytest.mark.usefixtures('with_plugins', 'clean_db')
def test_dataset_show_without_format():
    dataset = factories.Dataset(
        notes='Test dataset'
    )

    content = helpers.call_action('dcat_dataset_show', id=dataset['id'])

    # Parse the contents to check it's an actual serialization
    p = RDFParser()

    p.parse(content)

    dcat_datasets = [d for d in p.datasets()]

    assert len(dcat_datasets) == 1

    dcat_dataset = dcat_datasets[0]

    assert dcat_dataset['title'] == dataset['title']
    assert dcat_dataset['notes'] == dataset['notes']


# Pagination


class TestPagination(object):

    @pytest.mark.ckan_config('ckanext.dcat.datasets_per_page', 10)
    @pytest.mark.ckan_config('ckan.site_url', 'http://example.com')
    @mock.patch('ckan.plugins.toolkit.request')
    def test_pagination(self, mock_request):

        mock_request.params = {}
        mock_request.host_url = 'http://ckan.example.com'
        mock_request.path = ''

        # No page defined (defaults to 1)
        query = {
            'count': 12,
            'results': [x for x in range(10)],
        }
        data_dict = {
            'page': None
        }

        pagination = _pagination_info(query, data_dict)

        assert pagination['count'] == 12
        assert pagination['items_per_page'] == config.get('ckanext.dcat.datasets_per_page')
        assert pagination['current'] == 'http://example.com?page=1'
        assert pagination['first'] == 'http://example.com?page=1'
        assert pagination['last'] == 'http://example.com?page=2'
        assert pagination['next'] == 'http://example.com?page=2'
        assert 'previous' not in pagination

        # Page 1
        query = {
            'count': 12,
            'results': [x for x in range(10)],
        }
        data_dict = {
            'page': 1
        }

        pagination = _pagination_info(query, data_dict)

        assert pagination['count'] == 12
        assert pagination['items_per_page'] == config.get('ckanext.dcat.datasets_per_page')
        assert pagination['current'] == 'http://example.com?page=1'
        assert pagination['first'] == 'http://example.com?page=1'
        assert pagination['last'] == 'http://example.com?page=2'
        assert pagination['next'] == 'http://example.com?page=2'
        assert 'previous' not in pagination

        # Page 2
        query = {
            'count': 12,
            'results': [x for x in range(2)],
        }
        data_dict = {
            'page': 2
        }

        pagination = _pagination_info(query, data_dict)

        assert pagination['count'] == 12

        assert pagination['items_per_page'] == config.get('ckanext.dcat.datasets_per_page')
        assert pagination['current'] == 'http://example.com?page=2'
        assert pagination['first'] == 'http://example.com?page=1'
        assert pagination['last'] == 'http://example.com?page=2'
        assert pagination['previous'] == 'http://example.com?page=1'
        assert 'next' not in pagination

        # Page 3
        query = {
            'count': 12,
            'results': [x for x in range(2)],
        }
        data_dict = {
            'page': 3
        }

        pagination = _pagination_info(query, data_dict)

        assert pagination['count'] == 12
        assert pagination['items_per_page'] == config.get('ckanext.dcat.datasets_per_page')
        assert pagination['current'] == 'http://example.com?page=3'
        assert pagination['first'] == 'http://example.com?page=1'
        assert pagination['last'] == 'http://example.com?page=2'
        assert pagination['previous'] == 'http://example.com?page=2'
        assert 'next' not in pagination

    @pytest.mark.ckan_config('ckanext.dcat.datasets_per_page', 100)
    @pytest.mark.ckan_config('ckan.site_url', 'http://example.com')
    @mock.patch('ckan.plugins.toolkit.request')
    def test_pagination_less_results_than_page_size(self, mock_request):

        mock_request.params = {}
        mock_request.host_url = 'http://ckan.example.com'
        mock_request.path = ''

        # No page defined (defaults to 1)
        query = {
            'count': 12,
            'results': [x for x in range(12)],
        }
        data_dict = {
            'page': None
        }

        pagination = _pagination_info(query, data_dict)

        assert pagination['count'] == 12
        assert pagination['items_per_page'] == config.get('ckanext.dcat.datasets_per_page')
        assert pagination['current'] == 'http://example.com?page=1'
        assert pagination['first'] == 'http://example.com?page=1'
        assert pagination['last'] == 'http://example.com?page=1'
        assert 'next' not in pagination
        assert 'previous' not in pagination

    @pytest.mark.ckan_config('ckanext.dcat.datasets_per_page', 10)
    @pytest.mark.ckan_config('ckan.site_url', 'http://example.com')
    @mock.patch('ckan.plugins.toolkit.request')
    def test_pagination_same_results_than_page_size(self, mock_request):

        mock_request.params = {}
        mock_request.host_url = 'http://ckan.example.com'
        mock_request.path = ''

        # No page defined (defaults to 1)
        query = {
            'count': 10,
            'results': [x for x in range(10)],
        }
        data_dict = {
            'page': None
        }

        pagination = _pagination_info(query, data_dict)

        assert pagination['count'] == 10

        assert pagination['items_per_page'] == config.get('ckanext.dcat.datasets_per_page')
        assert pagination['current'] == 'http://example.com?page=1'
        assert pagination['first'] == 'http://example.com?page=1'
        assert pagination['last'] == 'http://example.com?page=1'
        assert 'next' not in pagination
        assert 'previous' not in pagination

    @pytest.mark.ckan_config('ckanext.dcat.datasets_per_page', 10)
    @pytest.mark.ckan_config('ckan.site_url', 'http://example.com')
    @mock.patch('ckan.plugins.toolkit.request')
    def test_pagination_keeps_only_supported_params(self, mock_request):

        mock_request.params = {'a': 1, 'b': 2, 'modified_since': '2018-03-22', 'profiles': 'schemaorg'}
        mock_request.host_url = 'http://ckan.example.com'
        mock_request.path = '/feed/catalog.xml'

        # No page defined (defaults to 1)
        query = {
            'count': 12,
            'results': [x for x in range(10)],
        }
        data_dict = {
            'page': None
        }

        pagination = _pagination_info(query, data_dict)

        assert pagination['count'] == 12
        assert pagination['items_per_page'] == config.get('ckanext.dcat.datasets_per_page')
        assert pagination['current'] == 'http://example.com/feed/catalog.xml?modified_since=2018-03-22&profiles=schemaorg&page=1'
        assert pagination['first'] == 'http://example.com/feed/catalog.xml?modified_since=2018-03-22&profiles=schemaorg&page=1'
        assert pagination['last'] == 'http://example.com/feed/catalog.xml?modified_since=2018-03-22&profiles=schemaorg&page=2'
        assert pagination['next'] == 'http://example.com/feed/catalog.xml?modified_since=2018-03-22&profiles=schemaorg&page=2'
        assert 'previous' not in pagination

    @pytest.mark.ckan_config('ckanext.dcat.datasets_per_page', 10)
    @pytest.mark.ckan_config('ckanext.dcat.base_uri', 'http://example.com/data')
    @mock.patch('ckan.plugins.toolkit.request')
    def test_pagination_with_dcat_base_uri(self, mock_request):

        mock_request.params = {}
        mock_request.host_url = 'http://ckan.example.com'
        mock_request.path = '/feed/catalog.xml'

        # No page defined (defaults to 1)
        query = {
            'count': 12,
            'results': [x for x in range(10)],
        }
        data_dict = {
            'page': None
        }

        pagination = _pagination_info(query, data_dict)

        assert pagination['count'] == 12
        assert pagination['items_per_page'] == config.get('ckanext.dcat.datasets_per_page')
        assert pagination['current'] == 'http://example.com/data/feed/catalog.xml?page=1'
        assert pagination['first'] == 'http://example.com/data/feed/catalog.xml?page=1'
        assert pagination['last'] == 'http://example.com/data/feed/catalog.xml?page=2'
        assert pagination['next'] == 'http://example.com/data/feed/catalog.xml?page=2'
        assert 'previous' not in pagination

    def test_pagination_no_results_empty_dict(self):
        query = {
            'count': 0,
            'results': [],
        }
        data_dict = {
            'page': None
        }

        pagination = _pagination_info(query, data_dict)

        assert pagination == {}

    def test_pagination_wrong_page(self):
        query = {
            'count': 10,
            'results': [x for x in range(10)],
        }
        data_dict = {
            'page': 'a'
        }

        with pytest.raises(toolkit.ValidationError):
            _pagination_info(query, data_dict)

    def test_pagination_wrong_page_number(self):
        query = {
            'count': 10,
            'results': [x for x in range(10)],
        }
        data_dict = {
            'page': '-1'
        }

        with pytest.raises(toolkit.ValidationError):
            _pagination_info(query, data_dict)
