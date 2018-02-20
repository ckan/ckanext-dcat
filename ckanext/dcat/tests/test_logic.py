import nose
import mock

from ckantoolkit import config

from ckan.plugins import toolkit

from ckantoolkit.tests import helpers, factories

from ckanext.dcat.logic import _pagination_info
from ckanext.dcat.processors import RDFParser

eq_ = nose.tools.eq_
assert_raises = nose.tools.assert_raises


class TestPagination(object):

    @helpers.change_config('ckanext.dcat.datasets_per_page', 10)
    @helpers.change_config('ckan.site_url', 'http://example.com')
    @mock.patch('ckan.plugins.toolkit.request')
    def test_pagination(self, mock_request):

        mock_request.params = {}
        mock_request.host_url = 'http://ckan.example.com'
        mock_request.path = ''

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
        eq_(pagination['current'], 'http://example.com?page=1')
        eq_(pagination['first'], 'http://example.com?page=1')
        eq_(pagination['last'], 'http://example.com?page=2')
        eq_(pagination['next'], 'http://example.com?page=2')
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
        eq_(pagination['current'], 'http://example.com?page=1')
        eq_(pagination['first'], 'http://example.com?page=1')
        eq_(pagination['last'], 'http://example.com?page=2')
        eq_(pagination['next'], 'http://example.com?page=2')
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
        eq_(pagination['current'], 'http://example.com?page=2')
        eq_(pagination['first'], 'http://example.com?page=1')
        eq_(pagination['last'], 'http://example.com?page=2')
        eq_(pagination['previous'], 'http://example.com?page=1')
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
        eq_(pagination['current'], 'http://example.com?page=3')
        eq_(pagination['first'], 'http://example.com?page=1')
        eq_(pagination['last'], 'http://example.com?page=2')
        eq_(pagination['previous'], 'http://example.com?page=2')
        assert 'next' not in pagination

    @helpers.change_config('ckanext.dcat.datasets_per_page', 100)
    @helpers.change_config('ckan.site_url', 'http://example.com')
    @mock.patch('ckan.plugins.toolkit.request')
    def test_pagination_less_results_than_page_size(self, mock_request):

        mock_request.params = {}
        mock_request.host_url = 'http://ckan.example.com'
        mock_request.path = ''

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
        eq_(pagination['current'], 'http://example.com?page=1')
        eq_(pagination['first'], 'http://example.com?page=1')
        eq_(pagination['last'], 'http://example.com?page=1')
        assert 'next' not in pagination
        assert 'previous' not in pagination

    @helpers.change_config('ckanext.dcat.datasets_per_page', 10)
    @helpers.change_config('ckan.site_url', 'http://example.com')
    @mock.patch('ckan.plugins.toolkit.request')
    def test_pagination_same_results_than_page_size(self, mock_request):

        mock_request.params = {}
        mock_request.host_url = 'http://ckan.example.com'
        mock_request.path = ''

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
        eq_(pagination['current'], 'http://example.com?page=1')
        eq_(pagination['first'], 'http://example.com?page=1')
        eq_(pagination['last'], 'http://example.com?page=1')
        assert 'next' not in pagination
        assert 'previous' not in pagination

    @helpers.change_config('ckanext.dcat.datasets_per_page', 10)
    @helpers.change_config('ckan.site_url', 'http://example.com')
    @mock.patch('ckan.plugins.toolkit.request')
    def test_pagination_keeps_params(self, mock_request):

        mock_request.params = {'a': 1, 'b': 2}
        mock_request.host_url = 'http://ckan.example.com'
        mock_request.path = '/feed/catalog.xml'

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
        eq_(pagination['current'], 'http://example.com/feed/catalog.xml?a=1&b=2&page=1')
        eq_(pagination['first'], 'http://example.com/feed/catalog.xml?a=1&b=2&page=1')
        eq_(pagination['last'], 'http://example.com/feed/catalog.xml?a=1&b=2&page=2')
        eq_(pagination['next'], 'http://example.com/feed/catalog.xml?a=1&b=2&page=2')
        assert 'previous' not in pagination

    @helpers.change_config('ckanext.dcat.datasets_per_page', 10)
    @helpers.change_config('ckan.site_url', '')
    @mock.patch('ckan.plugins.toolkit.request')
    def test_pagination_without_site_url(self, mock_request):

        mock_request.params = {}
        mock_request.host_url = 'http://ckan.example.com'
        mock_request.path = '/feed/catalog.xml'

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
        eq_(pagination['current'], 'http://ckan.example.com/feed/catalog.xml?page=1')
        eq_(pagination['first'], 'http://ckan.example.com/feed/catalog.xml?page=1')
        eq_(pagination['last'], 'http://ckan.example.com/feed/catalog.xml?page=2')
        eq_(pagination['next'], 'http://ckan.example.com/feed/catalog.xml?page=2')
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


class TestActions(helpers.FunctionalTestBase):
   def test_dataset_show_with_format(self):
        dataset = factories.Dataset(
            notes='Test dataset'
        )

        content = helpers.call_action('dcat_dataset_show', id=dataset['id'], _format='xml')

        # Parse the contents to check it's an actual serialization
        p = RDFParser()

        p.parse(content, _format='xml')

        dcat_datasets = [d for d in p.datasets()]

        eq_(len(dcat_datasets), 1)

        dcat_dataset = dcat_datasets[0]

        eq_(dcat_dataset['title'], dataset['title'])
        eq_(dcat_dataset['notes'], dataset['notes'])

   def test_dataset_show_without_format(self):
        dataset = factories.Dataset(
            notes='Test dataset'
        )

        content = helpers.call_action('dcat_dataset_show', id=dataset['id'])

        # Parse the contents to check it's an actual serialization
        p = RDFParser()

        p.parse(content)

        dcat_datasets = [d for d in p.datasets()]

        eq_(len(dcat_datasets), 1)

        dcat_dataset = dcat_datasets[0]

        eq_(dcat_dataset['title'], dataset['title'])
        eq_(dcat_dataset['notes'], dataset['notes'])
