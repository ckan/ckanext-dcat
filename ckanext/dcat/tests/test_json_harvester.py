from __future__ import absolute_import
from builtins import object

import responses
import pytest
from mock import patch

from ckantoolkit.tests import helpers

import ckan.tests.factories as factories

from ckanext.dcat.harvesters._json import copy_across_resource_ids, DCATJSONHarvester

from .test_harvester import FunctionalHarvestTest, harvest_setup, clean_queues


@pytest.mark.usefixtures('with_plugins', 'clean_db', 'clean_index', 'harvest_setup', 'clean_queues')
@pytest.mark.ckan_config('ckan.plugins', 'dcat harvest dcat_json_harvester')
class TestDCATJSONHarvestFunctional(FunctionalHarvestTest):

    # invalid tags dataset
    json_content_invalid_tags = '''
        {
        "@type": "dcat:Dataset",
        "name": "Invalid tags",
        "identifier": "http://example.com/datasets/invalid_example",
        "title": "Example dataset with invalid tags",
        "description": "Invalid keywords",
        "publisher": {"name":"Example Department of Wildlife"},
        "license": "https://example.com/license",
        "keyword": ["example", "test's", "invalid & wrong"]
        }
    '''

    @classmethod
    def setup_class(cls):

        super(TestDCATJSONHarvestFunctional, cls).setup_class()

        # Remote DCAT JSON / data.json file
        cls.json_mock_url = 'http://some.dcat.file.json'
        cls.json_content_type = 'application/json'

        # minimal dataset
        cls.json_content = '''
{
  "dataset":[
    {"@type": "dcat:Dataset",
     "identifier": "http://example.com/datasets/example1",
     "title": "Example dataset 1",
     "description": "Lots of species",
     "publisher": {"name": "Example Department of Wildlife"},
     "license": "https://example.com/license"
    },
    {"@type": "dcat:Dataset",
     "identifier": "http://example.com/datasets/example1",
     "title": "Example dataset 2",
     "description": "More species",
     "publisher": {"name":"Example Department of Wildlife"},
     "license": "https://example.com/license"
    }
  ]
}
        '''

        cls.json_content_with_distribution = '''
{
  "dataset":[
    {"@type": "dcat:Dataset",
     "identifier": "http://example.com/datasets/example1",
     "title": "Example dataset 1",
     "description": "Lots of species",
     "publisher": {"name": "Example Department of Wildlife"},
     "license": "https://example.com/license",
     "distribution":[
       {"@type":"dcat:Distribution",
        "title":"Example resource 1",
        "format":"Web page",
        "mediaType":"text/html",
        "accessURL":"http://example.com/datasets/example1"}
      ]
    }
  ]
}
        '''

        # invalid_tags dataset
        cls.json_content_invalid_tags_dataset = '{"dataset":[%s]}' % cls.json_content_invalid_tags

    def test_harvest_create(self):

        self._test_harvest_create(self.json_mock_url,
                                  self.json_content,
                                  self.json_content_type,
                                  exp_titles=['Example dataset 1', 'Example dataset 2'])

    @responses.activate
    def _test_harvest_create(
        self, url, content, content_type, num_datasets=2,
        exp_num_datasets=2, exp_titles=[],
        **kwargs
    ):

        # Mock the GET request to get the file
        responses.add(responses.GET, url,
                               body=content, content_type=content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # this as well
        responses.add(responses.HEAD, url,
                               status=405, content_type=content_type)

        kwargs['source_type'] = 'dcat_json'
        harvest_source = self._create_harvest_source(url, **kwargs)

        self._run_full_job(harvest_source['id'], num_objects=num_datasets)

        fq = "+type:dataset harvest_source_id:{0}".format(harvest_source['id'])
        results = helpers.call_action('package_search', {}, fq=fq)

        assert results['count'] == exp_num_datasets

        if exp_titles:
            for result in results['results']:
                assert result['title'] in exp_titles

    def test_harvest_update_existing_resources(self):

        content = self.json_content_with_distribution
        existing_resources, new_resources = \
            self._test_harvest_twice(content, content)

        # number of resources unchanged
        assert len(existing_resources) == 1
        assert len(new_resources) == 1
        # because the resource metadata is unchanged, the ID is kept the same
        assert new_resources[0]['id'] == existing_resources[0]['id']

    def test_harvest_update_new_resources(self):

        content = self.json_content_with_distribution
        content_modified = content.replace(
            '"accessURL":"http://example.com/datasets/example1"',
            '"accessURL":"http://example.com/datasets/new"')
        existing_resources, new_resources = \
            self._test_harvest_twice(content, content)

        # number of resources unchanged
        assert len(existing_resources) == 1
        assert len(new_resources) == 1
        # because the resource metadata has a new URL, the ID is new
        assert new_resources[0]['id'] is not existing_resources[0]['id']

    @responses.activate
    def _test_harvest_twice(self, content_first_harvest,
                            content_second_harvest):
        '''Based on _test_harvest_update_resources'''
        url = self.json_mock_url
        content_type = self.json_content_type
        # Mock the GET request to get the file
        responses.add(responses.GET, url,
                               body=content_first_harvest,
                               content_type=content_type)

        # Mock an update in the remote dataset.
        # Change title just to be sure we harvest ok
        content_second_harvest = \
            content_second_harvest.replace('Example dataset 1',
                                           'Example dataset 1 (updated)')
        responses.add(responses.GET, url,
                               body=content_second_harvest,
                               content_type=content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # this as well
        responses.add(responses.HEAD, url,
                               status=405, content_type=content_type)

        kwargs = {'source_type': 'dcat_json'}
        harvest_source = self._create_harvest_source(url, **kwargs)

        # First run, create the dataset with the resource
        self._run_full_job(harvest_source['id'], num_objects=1)

        # Run the jobs to mark the previous one as Finished
        self._run_jobs()

        # get the created dataset
        fq = "+type:dataset harvest_source_id:{0}".format(harvest_source['id'])
        results = helpers.call_action('package_search', {}, fq=fq)
        assert results['count'] == 1

        existing_dataset = results['results'][0]
        existing_resources = existing_dataset.get('resources')


        # Run a second job
        self._run_full_job(harvest_source['id'])

        # get the updated dataset
        new_results = helpers.call_action('package_search', {}, fq=fq)
        assert new_results['count'] == 1

        new_dataset = new_results['results'][0]
        new_resources = new_dataset.get('resources')

        assert existing_dataset['title'] == 'Example dataset 1'
        assert new_dataset['title'] == 'Example dataset 1 (updated)'

        return (existing_resources, new_resources)

    def test_harvest_does_not_create_with_invalid_tags(self):
        self._test_harvest_create(
            'http://some.dcat.file.invalid.json',
            self.json_content_invalid_tags_dataset,
            self.json_content_type,
            num_datasets=1,
            exp_num_datasets=0)


class TestCopyAcrossResourceIds(object):
    def test_copied_because_same_uri(self):
        harvested_dataset = {'resources': [
            {'uri': 'http://abc', 'url': 'http://abc'}]}
        copy_across_resource_ids({'resources': [
            {'uri': 'http://abc', 'url': 'http://def', 'id': '1'}]},
            harvested_dataset,
        )
        assert harvested_dataset['resources'][0].get('id') == '1'
        assert harvested_dataset['resources'][0].get('url') == 'http://abc'

    def test_copied_because_same_url(self):
        harvested_dataset = {'resources': [
            {'url': 'http://abc'}]}
        copy_across_resource_ids({'resources': [
            {'url': 'http://abc', 'id': '1'}]},
            harvested_dataset,
        )
        assert harvested_dataset['resources'][0].get('id') == '1'

    def test_copied_with_same_url_and_changed_title(self):
        harvested_dataset = {'resources': [
            {'url': 'http://abc', 'title': 'link updated'}]}
        copy_across_resource_ids({'resources': [
            {'url': 'http://abc', 'title': 'link', 'id': '1'}]},
            harvested_dataset,
        )
        assert harvested_dataset['resources'][0].get('id') == '1'

    def test_copied_with_repeated_urls_but_unique_titles(self):
        harvested_dataset = {'resources': [
            {'url': 'http://abc', 'title': 'link1'},
            {'url': 'http://abc', 'title': 'link5'},
            {'url': 'http://abc', 'title': 'link3'},
            {'url': 'http://abc', 'title': 'link2'},
            {'url': 'http://abc', 'title': 'link4'},
            {'url': 'http://abc', 'title': 'link new'},
            ]}
        copy_across_resource_ids({'resources': [
            {'url': 'http://abc', 'title': 'link1', 'id': '1'},
            {'url': 'http://abc', 'title': 'link2', 'id': '2'},
            {'url': 'http://abc', 'title': 'link3', 'id': '3'},
            {'url': 'http://abc', 'title': 'link4', 'id': '4'},
            {'url': 'http://abc', 'title': 'link5', 'id': '5'},
            ]},
            harvested_dataset,
        )
        assert ([(r.get('id'), r['title']) for r in harvested_dataset['resources']] ==
            [('1', 'link1'), ('5', 'link5'), ('3', 'link3'), ('2', 'link2'),
             ('4', 'link4'), (None, 'link new')])

    def test_not_copied_because_completely_different(self):
        harvested_dataset = {'resources': [
            {'url': 'http://def', 'title': 'link other'}]}
        copy_across_resource_ids({'resources': [
            {'url': 'http://abc', 'title': 'link', 'id': '1'}]},
            harvested_dataset,
        )
        assert harvested_dataset['resources'][0].get('id') == None

@pytest.mark.usefixtures('clean_db', 'clean_index', 'harvest_setup', 'clean_queues')
class TestImportStage(object):

    class MockHarvestObject(object):
        guid = 'test_guid'
        content = TestDCATJSONHarvestFunctional.json_content_invalid_tags

        class MockStatus(object):
            key = 'status'
            value = 'new'

        extras = [MockStatus()]
        package = None

        class MockSource(object):
            id = 'test_id'

        source = MockSource()

        def add(self):
            pass

    class MockSourceDataset(object):
        def __init__(self, owner_org=None):
            self.owner_org = owner_org['id']

    @patch('ckanext.dcat.harvesters._json.model.Package.get')
    @patch('ckanext.dcat.harvesters._json.DCATJSONHarvester._save_object_error')
    def test_import_invalid_tags(
        self, mock_save_object_error, mock_model_package_get
    ):
        user = factories.User()
        owner_org = factories.Organization(
            users=[{'name': user['id'], 'capacity': 'admin'}]
        )

        mock_model_package_get.return_value = self.MockSourceDataset(owner_org)

        harvester = DCATJSONHarvester()

        mock_harvest_object = self.MockHarvestObject()
        harvester.import_stage(mock_harvest_object)

        args, _ = mock_save_object_error.call_args_list[0]

        assert 'Error importing dataset Invalid tags: ValidationError' in args[0]
        assert 'Tag "invalid & wrong"' in args[0]
