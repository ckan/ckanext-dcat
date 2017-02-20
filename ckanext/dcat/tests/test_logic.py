import nose
import mock

from pylons import config

from ckan.plugins import toolkit

try:
    from ckan.tests import helpers
except ImportError:
    from ckan.new_tests import helpers

from ckanext.dcat.logic import _pagination_info

eq_ = nose.tools.eq_
assert_raises = nose.tools.assert_raises


class TestPagination(object):

    @helpers.change_config('ckanext.dcat.datasets_per_page', 10)
    @mock.patch('ckan.plugins.toolkit.request')
    def test_pagination(self, mock_request):

        mock_request.params = {}
        mock_request.path = '/catalog.rdf'

        # No page defined (defaults to 1)
        query = {
            'count': 12,
            'results': [x for x in xrange(10)],
        }
        data_dict = {
            'page': None
        }

        pagination = _pagination_info(query, data_dict)

        eq_(pagination['count'], 12)
        eq_(pagination['items_per_page'],
            config.get('ckanext.dcat.datasets_per_page'))
        eq_(pagination['current'], 'http://test.ckan.net/catalog.rdf?page=1')
        eq_(pagination['first'], 'http://test.ckan.net/catalog.rdf?page=1')
        eq_(pagination['last'], 'http://test.ckan.net/catalog.rdf?page=2')
        eq_(pagination['next'], 'http://test.ckan.net/catalog.rdf?page=2')
        assert 'previous' not in pagination

        # Page 1
        query = {
            'count': 12,
            'results': [x for x in xrange(10)],
        }
        data_dict = {
            'page': 1
        }

        pagination = _pagination_info(query, data_dict)

        eq_(pagination['count'], 12)
        eq_(pagination['items_per_page'],
            config.get('ckanext.dcat.datasets_per_page'))
        eq_(pagination['current'], 'http://test.ckan.net/catalog.rdf?page=1')
        eq_(pagination['first'], 'http://test.ckan.net/catalog.rdf?page=1')
        eq_(pagination['last'], 'http://test.ckan.net/catalog.rdf?page=2')
        eq_(pagination['next'], 'http://test.ckan.net/catalog.rdf?page=2')
        assert 'previous' not in pagination

        # Page 2
        query = {
            'count': 12,
            'results': [x for x in xrange(2)],
        }
        data_dict = {
            'page': 2
        }

        pagination = _pagination_info(query, data_dict)

        eq_(pagination['count'], 12)
        eq_(pagination['items_per_page'],
            config.get('ckanext.dcat.datasets_per_page'))
        eq_(pagination['current'], 'http://test.ckan.net/catalog.rdf?page=2')
        eq_(pagination['first'], 'http://test.ckan.net/catalog.rdf?page=1')
        eq_(pagination['last'], 'http://test.ckan.net/catalog.rdf?page=2')
        eq_(pagination['previous'], 'http://test.ckan.net/catalog.rdf?page=1')
        assert 'next' not in pagination

        # Page 3
        query = {
            'count': 12,
            'results': [x for x in xrange(2)],
        }
        data_dict = {
            'page': 3
        }

        pagination = _pagination_info(query, data_dict)

        eq_(pagination['count'], 12)
        eq_(pagination['items_per_page'],
            config.get('ckanext.dcat.datasets_per_page'))
        eq_(pagination['current'], 'http://test.ckan.net/catalog.rdf?page=3')
        eq_(pagination['first'], 'http://test.ckan.net/catalog.rdf?page=1')
        eq_(pagination['last'], 'http://test.ckan.net/catalog.rdf?page=2')
        eq_(pagination['previous'], 'http://test.ckan.net/catalog.rdf?page=2')
        assert 'next' not in pagination

    @helpers.change_config('ckanext.dcat.datasets_per_page', 100)
    @mock.patch('ckan.plugins.toolkit.request')
    def test_pagination_less_results_than_page_size(self, mock_request):

        mock_request.params = {}
        mock_request.path = '/catalog.rdf'

        # No page defined (defaults to 1)
        query = {
            'count': 12,
            'results': [x for x in xrange(12)],
        }
        data_dict = {
            'page': None
        }

        pagination = _pagination_info(query, data_dict)

        eq_(pagination['count'], 12)
        eq_(pagination['items_per_page'],
            config.get('ckanext.dcat.datasets_per_page'))
        eq_(pagination['current'], 'http://test.ckan.net/catalog.rdf?page=1')
        eq_(pagination['first'], 'http://test.ckan.net/catalog.rdf?page=1')
        eq_(pagination['last'], 'http://test.ckan.net/catalog.rdf?page=1')
        assert 'next' not in pagination
        assert 'previous' not in pagination

    @helpers.change_config('ckanext.dcat.datasets_per_page', 10)
    @mock.patch('ckan.plugins.toolkit.request')
    def test_pagination_same_results_than_page_size(self, mock_request):

        mock_request.params = {}
        mock_request.path = '/catalog.rdf'

        # No page defined (defaults to 1)
        query = {
            'count': 10,
            'results': [x for x in xrange(10)],
        }
        data_dict = {
            'page': None
        }

        pagination = _pagination_info(query, data_dict)

        eq_(pagination['count'], 10)
        eq_(pagination['items_per_page'],
            config.get('ckanext.dcat.datasets_per_page'))
        eq_(pagination['current'], 'http://test.ckan.net/catalog.rdf?page=1')
        eq_(pagination['first'], 'http://test.ckan.net/catalog.rdf?page=1')
        eq_(pagination['last'], 'http://test.ckan.net/catalog.rdf?page=1')
        assert 'next' not in pagination
        assert 'previous' not in pagination

    @helpers.change_config('ckanext.dcat.datasets_per_page', 10)
    @mock.patch('ckan.plugins.toolkit.request')
    def test_pagination_keeps_params(self, mock_request):

        mock_request.params = {'a': 1, 'b': 2}
        mock_request.path = '/catalog.rdf'

        # No page defined (defaults to 1)
        query = {
            'count': 12,
            'results': [x for x in xrange(10)],
        }
        data_dict = {
            'page': None
        }

        pagination = _pagination_info(query, data_dict)

        eq_(pagination['count'], 12)
        eq_(pagination['items_per_page'],
            config.get('ckanext.dcat.datasets_per_page'))
        eq_(pagination['current'], 'http://test.ckan.net/catalog.rdf?a=1&b=2&page=1')
        eq_(pagination['first'], 'http://test.ckan.net/catalog.rdf?a=1&b=2&page=1')
        eq_(pagination['last'], 'http://test.ckan.net/catalog.rdf?a=1&b=2&page=2')
        eq_(pagination['next'], 'http://test.ckan.net/catalog.rdf?a=1&b=2&page=2')
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

        eq_(pagination, {})

    def test_pagination_wrong_page(self):
        query = {
            'count': 10,
            'results': [x for x in xrange(10)],
        }
        data_dict = {
            'page': 'a'
        }

        assert_raises(toolkit.ValidationError,
                      _pagination_info, query, data_dict)

    def test_pagination_wrong_page_number(self):
        query = {
            'count': 10,
            'results': [x for x in xrange(10)],
        }
        data_dict = {
            'page': '-1'
        }

        assert_raises(toolkit.ValidationError,
                      _pagination_info, query, data_dict)
