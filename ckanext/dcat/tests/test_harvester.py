# -*- coding: utf-8 -*-

from builtins import str
from builtins import range
from builtins import object
from collections import defaultdict

import pytest
import responses
from mock import patch

import ckan.plugins as p
from ckantoolkit import config
from ckantoolkit.tests import helpers

import ckanext.harvest.model as harvest_model
from ckanext.harvest import queue

from ckanext.dcat.harvesters import DCATRDFHarvester
from ckanext.dcat.interfaces import IDCATRDFHarvester
import ckanext.dcat.harvesters.rdf


responses.add_passthru(config.get('solr_url', 'http://127.0.0.1:8983/solr'))


# TODO move to ckanext-harvest
@pytest.fixture
def harvest_setup():
    harvest_model.setup()


@pytest.fixture
def clean_queues():
    queue.purge_queues()


@pytest.fixture
def reset_calls_counter():
    def wrapper(plugin_name):
        plugin = p.get_plugin(plugin_name)
        plugin.calls = defaultdict(int)
    return wrapper


class TestRDFHarvester(p.SingletonPlugin):

    p.implements(IDCATRDFHarvester)

    calls = defaultdict(int)
    # change return values of after_parsing via this parameter
    after_parsing_mode = ''

    def before_download(self, url, harvest_job):

        self.calls['before_download'] += 1

        if url == 'http://return.none':
            return None, []
        elif url == 'http://return.errors':
            return None, ['Error 1', 'Error 2']
        else:
            return url, []

    def update_session(self, session):
        self.calls['update_session'] += 1
        session.headers.update({'x-test': 'true'})
        return session

    def after_download(self, content, harvest_job):

        self.calls['after_download'] += 1

        if content == 'return.empty.content':
            return None, []
        elif content == 'return.errors':
            return None, ['Error 1', 'Error 2']
        else:
            return content, []

    def after_parsing(self, rdf_parser, harvest_job):

        self.calls['after_parsing'] += 1

        if self.after_parsing_mode == 'return.empty.rdf_parser':
            return None, []
        elif self.after_parsing_mode == 'return.errors':
            return None, ['Error 1', 'Error 2']
        else:
            return rdf_parser, []

    def before_update(self, harvest_object, dataset_dict, temp_dict):
        self.calls['before_update'] += 1

    def after_update(self, harvest_object, dataset_dict, temp_dict):
        self.calls['after_update'] += 1
        return None

    def before_create(self, harvest_object, dataset_dict, temp_dict):
        self.calls['before_create'] += 1

    def after_create(self, harvest_object, dataset_dict, temp_dict):
        self.calls['after_create'] += 1
        return None

    def update_package_schema_for_create(self, package_schema):
        self.calls['update_package_schema_for_create'] += 1
        package_schema['new_key'] = 'test'
        return package_schema

    def update_package_schema_for_update(self, package_schema):
        self.calls['update_package_schema_for_update'] += 1
        package_schema['new_key'] = 'test'
        return package_schema


class TestRDFNullHarvester(TestRDFHarvester):
    p.implements(IDCATRDFHarvester)
    def before_update(self, harvest_object, dataset_dict, temp_dict):
        super(TestRDFNullHarvester, self).before_update(harvest_object, dataset_dict, temp_dict)
        dataset_dict.clear()

    def before_create(self, harvest_object, dataset_dict, temp_dict):
        super(TestRDFNullHarvester, self).before_create(harvest_object, dataset_dict, temp_dict)
        dataset_dict.clear()


class TestRDFExceptionHarvester(TestRDFHarvester):
    p.implements(IDCATRDFHarvester)

    raised_exception = False

    def before_create(self, harvest_object, dataset_dict, temp_dict):
        super(TestRDFExceptionHarvester, self).before_create(harvest_object, dataset_dict, temp_dict)
        if not self.raised_exception:
            self.raised_exception = True
            raise Exception("raising exception in before_create")


class TestDCATHarvestUnit(object):

    def test_get_guid_uri_root(self):

        dataset = {
            'name': 'test-dataset',
            'uri': 'http://dataset/uri',
        }

        guid = DCATRDFHarvester()._get_guid(dataset)

        assert guid == 'http://dataset/uri'

    def test_get_guid_identifier_root(self):

        dataset = {
            'name': 'test-dataset',
            'identifier': 'http://dataset/uri',
        }

        guid = DCATRDFHarvester()._get_guid(dataset)

        assert guid == 'http://dataset/uri'

    def test_get_guid_uri(self):

        dataset = {
            'name': 'test-dataset',
            'extras': [
                {'key': 'uri', 'value': 'http://dataset/uri'},
                {'key': 'dcat_identifier', 'value': 'dataset_dcat_id'},
            ]
        }

        guid = DCATRDFHarvester()._get_guid(dataset)

        assert guid == 'http://dataset/uri'

    def test_get_guid_identifier(self):

        dataset = {
            'name': 'test-dataset',
            'extras': [
                {'key': 'identifier', 'value': 'dataset_dcat_id'},
            ]
        }

        guid = DCATRDFHarvester()._get_guid(dataset)

        assert guid == 'dataset_dcat_id'

    def test_get_guid_dcat_identifier(self):

        dataset = {
            'name': 'test-dataset',
            'extras': [
                {'key': 'dcat_identifier', 'value': 'dataset_dcat_id'},
            ]
        }

        guid = DCATRDFHarvester()._get_guid(dataset)

        assert guid == 'dataset_dcat_id'

    def test_get_guid_uri_none(self):

        dataset = {
            'name': 'test-dataset',
            'extras': [
                {'key': 'uri', 'value': None},
                {'key': 'dcat_identifier', 'value': 'dataset_dcat_id'},
            ]
        }

        guid = DCATRDFHarvester()._get_guid(dataset)

        assert guid == 'dataset_dcat_id'

    def test_get_guid_dcat_identifier_none(self):

        dataset = {
            'name': 'test-dataset',
            'extras': [
                {'key': 'dcat_identifier', 'value': None},
            ]
        }

        guid = DCATRDFHarvester()._get_guid(dataset)

        assert guid == 'test-dataset'

    def test_get_guid_source_url_name(self):

        dataset = {
            'name': 'test-dataset',
            'extras': [
            ]
        }

        guid = DCATRDFHarvester()._get_guid(dataset, 'http://source_url')

        assert guid == 'http://source_url/test-dataset'

        guid = DCATRDFHarvester()._get_guid(dataset, 'http://source_url/')

        assert guid == 'http://source_url/test-dataset'

    def test_get_guid_name(self):

        dataset = {
            'name': 'test-dataset',
            'extras': [
            ]
        }

        guid = DCATRDFHarvester()._get_guid(dataset)

        assert guid == 'test-dataset'

    def test_get_guid_none(self):

        dataset = {
            'extras': [
            ]
        }

        guid = DCATRDFHarvester()._get_guid(dataset)

        assert guid == None


class FunctionalHarvestTest(object):

    @classmethod
    def setup_class(cls):

        cls.gather_consumer = queue.get_gather_consumer()
        cls.fetch_consumer = queue.get_fetch_consumer()

        # Minimal remote RDF file
        cls.rdf_mock_url = 'http://some.dcat.file.rdf'
        cls.rdf_content_type = 'application/rdf+xml'
        cls.rdf_content = '''<?xml version="1.0" encoding="utf-8" ?>
        <rdf:RDF
         xmlns:dct="http://purl.org/dc/terms/"
         xmlns:dcat="http://www.w3.org/ns/dcat#"
         xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <dcat:Catalog rdf:about="https://data.some.org/catalog">
          <dcat:dataset>
            <dcat:Dataset rdf:about="https://data.some.org/catalog/datasets/1">
              <dct:title>Example dataset 1</dct:title>
            </dcat:Dataset>
          </dcat:dataset>
          <dcat:dataset>
            <dcat:Dataset rdf:about="https://data.some.org/catalog/datasets/2">
              <dct:title>Example dataset 2</dct:title>
            </dcat:Dataset>
          </dcat:dataset>
        </dcat:Catalog>
        </rdf:RDF>
        '''

        # Minimal remote RDF file with pagination (1)
        cls.rdf_mock_url_pagination_1 = 'http://some.dcat.file.pagination.rdf'
        cls.rdf_content_pagination_1 = '''<?xml version="1.0" encoding="utf-8" ?>
        <rdf:RDF
         xmlns:dct="http://purl.org/dc/terms/"
         xmlns:dcat="http://www.w3.org/ns/dcat#"
         xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:hydra="http://www.w3.org/ns/hydra/core#">
        <dcat:Catalog rdf:about="https://data.some.org/catalog">
          <dcat:dataset>
            <dcat:Dataset rdf:about="https://data.some.org/catalog/datasets/1">
              <dct:title>Example dataset 1</dct:title>
            </dcat:Dataset>
          </dcat:dataset>
          <dcat:dataset>
            <dcat:Dataset rdf:about="https://data.some.org/catalog/datasets/2">
              <dct:title>Example dataset 2</dct:title>
            </dcat:Dataset>
          </dcat:dataset>
        </dcat:Catalog>
        <hydra:PagedCollection rdf:about="http://some.dcat.file.pagination.rdf/page/1">
            <hydra:totalItems rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">4</hydra:totalItems>
            <hydra:lastPage>http://some.dcat.file.pagination.rdf/page/2</hydra:lastPage>
            <hydra:itemsPerPage rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">2</hydra:itemsPerPage>
            <hydra:nextPage>http://some.dcat.file.pagination.rdf/page/2</hydra:nextPage>
            <hydra:firstPage>http://some.dcat.file.pagination.rdf/page/1</hydra:firstPage>
        </hydra:PagedCollection>
        </rdf:RDF>
        '''

        # Minimal remote RDF file with pagination (2)
        cls.rdf_mock_url_pagination_2 = 'http://some.dcat.file.pagination.rdf/page/2'
        cls.rdf_content_pagination_2 = '''<?xml version="1.0" encoding="utf-8" ?>
        <rdf:RDF
         xmlns:dct="http://purl.org/dc/terms/"
         xmlns:dcat="http://www.w3.org/ns/dcat#"
         xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:hydra="http://www.w3.org/ns/hydra/core#">
        <dcat:Catalog rdf:about="https://data.some.org/catalog">
          <dcat:dataset>
            <dcat:Dataset rdf:about="https://data.some.org/catalog/datasets/3">
              <dct:title>Example dataset 3</dct:title>
            </dcat:Dataset>
          </dcat:dataset>
          <dcat:dataset>
            <dcat:Dataset rdf:about="https://data.some.org/catalog/datasets/4">
              <dct:title>Example dataset 4</dct:title>
            </dcat:Dataset>
          </dcat:dataset>
        </dcat:Catalog>
        <hydra:PagedCollection rdf:about="http://some.dcat.file.pagination.rdf/page/1">
            <hydra:totalItems rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">4</hydra:totalItems>
            <hydra:lastPage>http://some.dcat.file.pagination.rdf/page/2</hydra:lastPage>
            <hydra:itemsPerPage rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">2</hydra:itemsPerPage>
            <hydra:previousPage>http://some.dcat.file.pagination.rdf/page/1</hydra:previousPage>
            <hydra:firstPage>http://some.dcat.file.pagination.rdf/page/1</hydra:firstPage>
        </hydra:PagedCollection>
        </rdf:RDF>
        '''

        # Minimal remote RDF file
        cls.rdf_mock_url = 'http://some.dcat.file.rdf'
        cls.rdf_content_type = 'application/rdf+xml'
        cls.rdf_content = '''<?xml version="1.0" encoding="utf-8" ?>
        <rdf:RDF
         xmlns:dct="http://purl.org/dc/terms/"
         xmlns:dcat="http://www.w3.org/ns/dcat#"
         xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <dcat:Catalog rdf:about="https://data.some.org/catalog">
          <dcat:dataset>
            <dcat:Dataset rdf:about="https://data.some.org/catalog/datasets/1">
              <dct:title>Example dataset 1</dct:title>
            </dcat:Dataset>
          </dcat:dataset>
          <dcat:dataset>
            <dcat:Dataset rdf:about="https://data.some.org/catalog/datasets/2">
              <dct:title>Example dataset 2</dct:title>
            </dcat:Dataset>
          </dcat:dataset>
        </dcat:Catalog>
        </rdf:RDF>
        '''

        cls.rdf_mock_url_duplicates = 'http://some.dcat.file.duplicates.rdf'
        cls.rdf_duplicate_titles = '''<?xml version="1.0" encoding="utf-8" ?>
        <rdf:RDF
         xmlns:dct="http://purl.org/dc/terms/"
         xmlns:dcat="http://www.w3.org/ns/dcat#"
         xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <dcat:Catalog rdf:about="https://data.some.org/catalog">
          <dcat:dataset>
            <dcat:Dataset rdf:about="https://data.some.org/catalog/datasets/1">
              <dct:title>Example dataset</dct:title>
            </dcat:Dataset>
          </dcat:dataset>
          <dcat:dataset>
            <dcat:Dataset rdf:about="https://data.some.org/catalog/datasets/2">
              <dct:title>Example dataset</dct:title>
            </dcat:Dataset>
          </dcat:dataset>
        </dcat:Catalog>
        </rdf:RDF>
        '''

        cls.rdf_remote_file_small = '''<?xml version="1.0" encoding="utf-8" ?>
        <rdf:RDF
         xmlns:dct="http://purl.org/dc/terms/"
         xmlns:dcat="http://www.w3.org/ns/dcat#"
         xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <dcat:Catalog rdf:about="https://data.some.org/catalog">
          <dcat:dataset>
            <dcat:Dataset rdf:about="https://data.some.org/catalog/datasets/1">
              <dct:title>Example dataset 1</dct:title>
            </dcat:Dataset>
          </dcat:dataset>
        </dcat:Catalog>
        </rdf:RDF>
        '''

        # RDF with minimal distribution
        cls.rdf_content_with_distribution_uri = '''<?xml version="1.0" encoding="utf-8" ?>
        <rdf:RDF
         xmlns:dct="http://purl.org/dc/terms/"
         xmlns:dcat="http://www.w3.org/ns/dcat#"
         xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <dcat:Catalog rdf:about="https://data.some.org/catalog">
          <dcat:dataset>
            <dcat:Dataset rdf:about="https://data.some.org/catalog/datasets/1">
              <dct:title>Example dataset 1</dct:title>
              <dcat:distribution>
                <dcat:Distribution rdf:about="https://data.some.org/catalog/datasets/1/resource/1">
                  <dct:title>Example resource 1</dct:title>
                  <dcat:accessURL>http://data.some.org/download.zip</dcat:accessURL>
                </dcat:Distribution>
              </dcat:distribution>
            </dcat:Dataset>
          </dcat:dataset>
        </dcat:Catalog>
        </rdf:RDF>
        '''
        cls.rdf_content_with_distribution = '''<?xml version="1.0" encoding="utf-8" ?>
        <rdf:RDF
         xmlns:dct="http://purl.org/dc/terms/"
         xmlns:dcat="http://www.w3.org/ns/dcat#"
         xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <dcat:Catalog rdf:about="https://data.some.org/catalog">
          <dcat:dataset>
            <dcat:Dataset rdf:about="https://data.some.org/catalog/datasets/1">
              <dct:title>Example dataset 1</dct:title>
              <dcat:distribution>
                <dcat:Distribution>
                  <dct:title>Example resource 1</dct:title>
                  <dcat:accessURL>http://data.some.org/download.zip</dcat:accessURL>
                </dcat:Distribution>
              </dcat:distribution>
            </dcat:Dataset>
          </dcat:dataset>
        </dcat:Catalog>
        </rdf:RDF>
        '''

        cls.rdf_remote_file_invalid = '''<?xml version="1.0" encoding="utf-8" ?>
        <rdf:RDF
         xmlns:dcat="http://www.w3.org/ns/dcat#"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <dcat:Catalog
        </rdf:RDF>
        '''

        #Minimal remote turtle file
        cls.ttl_mock_url = 'http://some.dcat.file.ttl'
        cls.ttl_content_type = 'text/turtle'
        cls.ttl_content = '''@prefix dcat: <http://www.w3.org/ns/dcat#> .
        @prefix dc: <http://purl.org/dc/terms/> .
        <https://data.some.org/catalog>
          a dcat:Catalog ;
          dcat:dataset <https://data.some.org/catalog/datasets/1>, <https://data.some.org/catalog/datasets/2> .
        <https://data.some.org/catalog/datasets/1>
          a dcat:Dataset ;
          dc:title "Example dataset 1" .
        <https://data.some.org/catalog/datasets/2>
          a dcat:Dataset ;
          dc:title "Example dataset 2" .
          '''
        cls.ttl_remote_file_small = '''@prefix dcat: <http://www.w3.org/ns/dcat#> .
        @prefix dc: <http://purl.org/dc/terms/> .
        <https://data.some.org/catalog>
          a dcat:Catalog ;
          dcat:dataset <https://data.some.org/catalog/datasets/1>, <https://data.some.org/catalog/datasets/2> .
        <https://data.some.org/catalog/datasets/1>
          a dcat:Dataset ;
          dc:title "Example dataset 1" .
          '''
        cls.ttl_unicode_in_keywords = u'''@prefix dcat: <http://www.w3.org/ns/dcat#> .
        @prefix dc: <http://purl.org/dc/terms/> .
        <https://data.some.org/catalog>
          a dcat:Catalog ;
          dcat:dataset <https://data.some.org/catalog/datasets/1> .
        <https://data.some.org/catalog/datasets/1>
          a dcat:Dataset ;
          dc:title "Example dataset 1" ;
          dcat:keyword "förskola", "Garduña" .
        <https://data.some.org/catalog/datasets/2>
          a dcat:Dataset ;
          dc:title "Example dataset 2" ;
          dcat:keyword "San Sebastián", "Ελλάδα" .
          '''
        cls.ttl_commas_in_keywords = u'''@prefix dcat: <http://www.w3.org/ns/dcat#> .
        @prefix dc: <http://purl.org/dc/terms/> .
        <https://data.some.org/catalog>
          a dcat:Catalog ;
          dcat:dataset <https://data.some.org/catalog/datasets/1> .
        <https://data.some.org/catalog/datasets/1>
          a dcat:Dataset ;
          dc:title "Example dataset 1" ;
          dcat:keyword "Utbildning, kontaktuppgifter" .
        <https://data.some.org/catalog/datasets/2>
          a dcat:Dataset ;
          dc:title "Example dataset 2" ;
          dcat:keyword "Trees, forest, shrub" .
          '''
        cls.ttl_remote_file_invalid = '''@prefix dcat: <http://www.w3.org/ns/dcat#> .
        @prefix dc: <http://purl.org/dc/terms/> .
        <https://data.some.org/catalog>
          a dcat:Catalog ;
        <https://data.some.org/catalog/datasets/1>
          a dcat:Dataset ;
          dc:title "Example dataset 1" .
          '''


    def _create_harvest_source(self, mock_url, **kwargs):

        source_dict = {
            'title': 'Test RDF DCAT Source',
            'name': 'test-rdf-dcat-source',
            'url': mock_url,
            'source_type': 'dcat_rdf',
        }

        source_dict.update(**kwargs)

        harvest_source = helpers.call_action('harvest_source_create',
                                       {}, **source_dict)

        return harvest_source

    def _create_harvest_job(self, harvest_source_id):

        harvest_job = helpers.call_action('harvest_job_create',
                                    {}, source_id=harvest_source_id)

        return harvest_job

    def _run_jobs(self, harvest_source_id=None):
        try:
            helpers.call_action('harvest_jobs_run',
                          {}, source_id=harvest_source_id)
        except Exception as e:
            if (str(e) == 'There are no new harvesting jobs'):
                pass

    def _gather_queue(self, num_jobs=1):

        for job in range(num_jobs):
            # Pop one item off the queue (the job id) and run the callback
            reply = self.gather_consumer.basic_get(
                queue='ckan.harvest.gather.test')

            # Make sure something was sent to the gather queue
            assert reply[2], 'Empty gather queue'

            # Send the item to the gather callback, which will call the
            # harvester gather_stage
            queue.gather_callback(self.gather_consumer, *reply)

    def _fetch_queue(self, num_objects=1):

        for _object in range(num_objects):
            # Pop item from the fetch queues (object ids) and run the callback,
            # one for each object created
            reply = self.fetch_consumer.basic_get(
                queue='ckan.harvest.fetch.test')

            # Make sure something was sent to the fetch queue
            assert reply[2], 'Empty fetch queue, the gather stage failed'

            # Send the item to the fetch callback, which will call the
            # harvester fetch_stage and import_stage
            queue.fetch_callback(self.fetch_consumer, *reply)

    def _run_full_job(self, harvest_source_id, num_jobs=1, num_objects=1):

        # Create new job for the source
        self._create_harvest_job(harvest_source_id)

        # Run the job
        self._run_jobs(harvest_source_id)

        # Handle the gather queue
        self._gather_queue(num_jobs)

        # Handle the fetch queue
        self._fetch_queue(num_objects)


@pytest.mark.usefixtures('with_plugins', 'clean_db', 'clean_index', 'harvest_setup', 'clean_queues')
@pytest.mark.ckan_config('ckan.plugins', 'dcat harvest dcat_rdf_harvester')
class TestDCATHarvestFunctional(FunctionalHarvestTest):

    def test_harvest_create_rdf(self):

        self._test_harvest_create(self.rdf_mock_url,
                                  self.rdf_content,
                                  self.rdf_content_type)

    def test_harvest_create_ttl(self):

        self._test_harvest_create(self.ttl_mock_url,
                                  self.ttl_content,
                                  self.ttl_content_type)

    def test_harvest_create_with_config_content_Type(self):

        self._test_harvest_create(self.ttl_mock_url,
                                  self.ttl_content,
                                  'text/plain',
                                  config='{"rdf_format":"text/turtle"}')

    def test_harvest_create_unicode_keywords(self):

        self._test_harvest_create(self.ttl_mock_url,
                                  self.ttl_unicode_in_keywords,
                                  self.ttl_content_type)

    def test_harvest_create_commas_keywords(self):

        self._test_harvest_create(self.ttl_mock_url,
                                  self.ttl_commas_in_keywords,
                                  self.ttl_content_type)

    @responses.activate
    def _test_harvest_create(self, url, content, content_type, **kwargs):

        # Mock the GET request to get the file
        responses.add(responses.GET, url,
                               body=content, content_type=content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # this as well
        responses.add(responses.HEAD, url,
                               status=405, content_type=content_type)

        harvest_source = self._create_harvest_source(url, **kwargs)

        self._run_full_job(harvest_source['id'], num_objects=2)

        # Check that two datasets were created
        fq = "+type:dataset harvest_source_id:{0}".format(harvest_source['id'])
        results = helpers.call_action('package_search', {}, fq=fq)

        assert results['count'] == 2
        for result in results['results']:
            assert result['title'] in ('Example dataset 1',
                                       'Example dataset 2')

    @responses.activate
    def test_harvest_create_rdf_pagination(self):

        # Mock the GET requests needed to get the file
        responses.add(responses.GET, self.rdf_mock_url_pagination_1,
                               body=self.rdf_content_pagination_1,
                               content_type=self.rdf_content_type)

        responses.add(responses.GET, self.rdf_mock_url_pagination_2,
                               body=self.rdf_content_pagination_2,
                               content_type=self.rdf_content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # them as well
        responses.add(responses.HEAD, self.rdf_mock_url_pagination_1,
                               status=405,
                               content_type=self.rdf_content_type)

        responses.add(responses.HEAD, self.rdf_mock_url_pagination_2,
                               status=405,
                               content_type=self.rdf_content_type)

        harvest_source = self._create_harvest_source(
            self.rdf_mock_url_pagination_1)

        self._run_full_job(harvest_source['id'], num_objects=4)

        # Check that four datasets were created
        fq = "+type:dataset harvest_source_id:{0}".format(harvest_source['id'])
        results = helpers.call_action('package_search', {}, fq=fq)

        assert results['count'] == 4
        assert (sorted([d['title'] for d in results['results']]) ==
            ['Example dataset 1', 'Example dataset 2',
             'Example dataset 3', 'Example dataset 4'])

    @responses.activate
    def test_harvest_create_rdf_pagination_same_content(self):

        # Mock the GET requests needed to get the file. Two different URLs but
        # same content to mock a misconfigured server
        responses.add(responses.GET, self.rdf_mock_url_pagination_1,
                               body=self.rdf_content_pagination_1,
                               content_type=self.rdf_content_type)

        responses.add(responses.GET, self.rdf_mock_url_pagination_2,
                               body=self.rdf_content_pagination_1,
                               content_type=self.rdf_content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # them as well
        responses.add(responses.HEAD, self.rdf_mock_url_pagination_1,
                               status=405,
                               content_type=self.rdf_content_type)

        responses.add(responses.HEAD, self.rdf_mock_url_pagination_2,
                               status=405,
                               content_type=self.rdf_content_type)

        harvest_source = self._create_harvest_source(
            self.rdf_mock_url_pagination_1)

        self._run_full_job(harvest_source['id'], num_objects=2)

        # Check that two datasets were created
        fq = "+type:dataset harvest_source_id:{0}".format(harvest_source['id'])
        results = helpers.call_action('package_search', {}, fq=fq)

        assert results['count'] == 2
        assert (sorted([d['title'] for d in results['results']]) ==
            ['Example dataset 1', 'Example dataset 2'])

    def test_harvest_update_rdf(self):

        self._test_harvest_update(self.rdf_mock_url,
                                  self.rdf_content,
                                  self.rdf_content_type)

    def test_harvest_update_ttl(self):

        self._test_harvest_update(self.ttl_mock_url,
                                  self.ttl_content,
                                  self.ttl_content_type)

    def test_harvest_update_unicode_keywords(self):

        self._test_harvest_create(self.ttl_mock_url,
                                  self.ttl_unicode_in_keywords,
                                  self.ttl_content_type)

    def test_harvest_update_commas_keywords(self):

        self._test_harvest_update(self.ttl_mock_url,
                                  self.ttl_commas_in_keywords,
                                  self.ttl_content_type)

    @responses.activate
    def _test_harvest_update(self, url, content, content_type):
        # Mock the GET request to get the file
        responses.add(responses.GET, url,
                               body=content, content_type=content_type)

        # Mock an update in the remote file
        new_file = content.replace('Example dataset 1',
                                   'Example dataset 1 (updated)')

        responses.add(responses.GET, url,
                               body=new_file, content_type=content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # this as well
        responses.add(responses.HEAD, url,
                               status=405, content_type=content_type)

        harvest_source = self._create_harvest_source(url)

        # First run, will create two datasets as previously tested
        self._run_full_job(harvest_source['id'], num_objects=2)

        # Run the jobs to mark the previous one as Finished
        self._run_jobs()

        # Run a second job
        self._run_full_job(harvest_source['id'], num_objects=2)

        # Check that we still have two datasets
        fq = "+type:dataset harvest_source_id:{0}".format(harvest_source['id'])
        results = helpers.call_action('package_search', {}, fq=fq)

        assert results['count'] == 2

        # Check that the dataset was updated
        for result in results['results']:
            assert result['title'] in ('Example dataset 1 (updated)',
                                       'Example dataset 2')

    def test_harvest_update_existing_resources(self):

        existing, new = self._test_harvest_update_resources(self.rdf_mock_url,
                                  self.rdf_content_with_distribution_uri,
                                  self.rdf_content_type)
        assert new['uri'] == 'https://data.some.org/catalog/datasets/1/resource/1'
        assert new['uri'] == existing['uri']
        assert new['id'] == existing['id']

    def test_harvest_update_new_resources(self):

        existing, new = self._test_harvest_update_resources(self.rdf_mock_url,
                                  self.rdf_content_with_distribution,
                                  self.rdf_content_type)
        assert existing['uri'] == ''
        assert new['uri'] == ''
        assert new['id'] != existing['id']

    @responses.activate
    def _test_harvest_update_resources(self, url, content, content_type):
        # Mock the GET request to get the file
        responses.add(responses.GET, url,
                               body=content, content_type=content_type)

        # Mock an update in the remote file
        new_file = content.replace('Example resource 1',
                                   'Example resource 1 (updated)')
        responses.add(responses.GET, url,
                               body=new_file, content_type=content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # this as well
        responses.add(responses.HEAD, url,
                               status=405, content_type=content_type)

        harvest_source = self._create_harvest_source(url)

        # First run, create the dataset with the resource
        self._run_full_job(harvest_source['id'], num_objects=1)

        # Run the jobs to mark the previous one as Finished
        self._run_jobs()

        # get the created dataset
        fq = "+type:dataset harvest_source_id:{0}".format(harvest_source['id'])
        results = helpers.call_action('package_search', {}, fq=fq)
        assert results['count'] == 1

        existing_dataset = results['results'][0]
        existing_resource = existing_dataset.get('resources')[0]

        # Run a second job
        self._run_full_job(harvest_source['id'])

        # get the updated dataset
        new_results = helpers.call_action('package_search', {}, fq=fq)
        assert new_results['count'] == 1

        new_dataset = new_results['results'][0]
        new_resource = new_dataset.get('resources')[0]

        assert existing_resource['name'] == 'Example resource 1'
        assert len(new_dataset.get('resources')) == 1
        assert new_resource['name'] == 'Example resource 1 (updated)'
        return (existing_resource, new_resource)

    def test_harvest_delete_rdf(self):

        self._test_harvest_delete(self.rdf_mock_url,
                                  self.rdf_content,
                                  self.rdf_remote_file_small,
                                  self.rdf_content_type)

    def test_harvest_delete_ttl(self):

        self._test_harvest_delete(self.ttl_mock_url,
                                  self.ttl_content,
                                  self.ttl_remote_file_small,
                                  self.ttl_content_type)

    @responses.activate
    def _test_harvest_delete(self, url, content, content_small, content_type):

        # Mock the GET request to get the file
        responses.add(responses.GET, url,
                               body=content, content_type=content_type)
        # Mock a deletion in the remote file
        responses.add(responses.GET, url,
                               body=content_small, content_type=content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # this as well
        responses.add(responses.HEAD, url,
                               status=405, content_type=content_type)

        harvest_source = self._create_harvest_source(url)

        # First run, will create two datasets as previously tested
        self._run_full_job(harvest_source['id'], num_objects=2)

        # Run the jobs to mark the previous one as Finished
        self._run_jobs()

        # Run a second job
        self._run_full_job(harvest_source['id'], num_objects=2)

        # Check that we only have one dataset
        fq = "+type:dataset harvest_source_id:{0}".format(harvest_source['id'])
        results = helpers.call_action('package_search', {}, fq=fq)

        assert results['count'] == 1

        assert results['results'][0]['title'] == 'Example dataset 1'

    def test_harvest_bad_format_rdf(self):

        self._test_harvest_bad_format(self.rdf_mock_url,
                                      self.rdf_remote_file_invalid,
                                      self.rdf_content_type)

    def test_harvest_bad_format_ttl(self):

        self._test_harvest_bad_format(self.ttl_mock_url,
                                      self.ttl_remote_file_invalid,
                                      self.ttl_content_type)

    @responses.activate
    def _test_harvest_bad_format(self, url, bad_content, content_type):

        # Mock the GET request to get the file
        responses.add(responses.GET, url,
                               body=bad_content, content_type=content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # this as well
        responses.add(responses.HEAD, url,
                               status=405, content_type=content_type)

        harvest_source = self._create_harvest_source(url)
        self._create_harvest_job(harvest_source['id'])
        self._run_jobs(harvest_source['id'])
        self._gather_queue(1)

        # Run the jobs to mark the previous one as Finished
        self._run_jobs()

        # Get the harvest source with the udpated status
        harvest_source = helpers.call_action('harvest_source_show',
                                       id=harvest_source['id'])

        last_job_status = harvest_source['status']['last_job']

        assert last_job_status['status'] == 'Finished'
        assert ('Error parsing the RDF file'
                in last_job_status['gather_error_summary'][0][0])

    @responses.activate
    @patch.object(ckanext.dcat.harvesters.rdf.RDFParser, 'datasets')
    def test_harvest_exception_in_profile(self, mock_datasets):
        mock_datasets.side_effect = Exception

        # Mock the GET request to get the file
        responses.add(responses.GET, self.rdf_mock_url,
                               body=self.rdf_content, content_type=self.rdf_content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # this as well
        responses.add(responses.HEAD, self.rdf_mock_url,
                               status=405, content_type=self.rdf_content_type)

        harvest_source = self._create_harvest_source(self.rdf_mock_url)
        self._create_harvest_job(harvest_source['id'])
        self._run_jobs(harvest_source['id'])
        self._gather_queue(1)

        # Run the jobs to mark the previous one as Finished
        self._run_jobs()

        # Get the harvest source with the udpated status
        harvest_source = helpers.call_action('harvest_source_show',
                                       id=harvest_source['id'])

        last_job_status = harvest_source['status']['last_job']

        assert last_job_status['status'] == 'Finished'
        assert ('Error when processsing dataset'
                in last_job_status['gather_error_summary'][0][0])

    @responses.activate
    def test_harvest_create_duplicate_titles(self):

        # Mock the GET request to get the file
        responses.add(responses.GET, self.rdf_mock_url_duplicates,
                               body=self.rdf_duplicate_titles,
                               content_type=self.rdf_content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # this as well
        responses.add(responses.HEAD, self.rdf_mock_url_duplicates,
                               status=405,
                               content_type=self.rdf_content_type)

        harvest_source = self._create_harvest_source(self.rdf_mock_url_duplicates)

        self._run_full_job(harvest_source['id'], num_objects=2)

        # Check that two datasets were created
        fq = "+type:dataset harvest_source_id:{0}".format(harvest_source['id'])
        results = helpers.call_action('package_search', {}, fq=fq)

        assert results['count'] == 2
        for result in results['results']:
            assert result['name'] in ('example-dataset',
                                      'example-dataset-1')


@pytest.mark.usefixtures(
    'with_plugins',
    'clean_db',
    'clean_index',
    'harvest_setup',
    'clean_queues',
)
@pytest.mark.ckan_config('ckan.plugins', 'dcat harvest dcat_rdf_harvester test_rdf_harvester')
class TestDCATHarvestFunctionalExtensionPoints(FunctionalHarvestTest):

    def test_harvest_before_download_extension_point_gets_called(self, reset_calls_counter):
        reset_calls_counter('test_rdf_harvester')
        plugin = p.get_plugin('test_rdf_harvester')

        harvest_source = self._create_harvest_source(self.rdf_mock_url)
        self._create_harvest_job(harvest_source['id'])
        self._run_jobs(harvest_source['id'])
        self._gather_queue(1)

        assert plugin.calls['before_download'] == 1

    @responses.activate
    def test_harvest_before_download_null_url_stops_gather_stage(self, reset_calls_counter):

        reset_calls_counter('test_rdf_harvester')
        plugin = p.get_plugin('test_rdf_harvester')

        source_url = 'http://return.none'

        # Mock the GET request to get the file
        responses.add(responses.GET, source_url,
                               body=self.rdf_content,
                               content_type=self.rdf_content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # this as well
        responses.add(responses.HEAD, source_url,
                               status=405,
                               content_type=self.rdf_content_type)

        harvest_source = self._create_harvest_source(source_url)
        self._create_harvest_job(harvest_source['id'])
        self._run_jobs(harvest_source['id'])
        self._gather_queue(1)

        assert plugin.calls['before_download'] == 1

        # Run the jobs to mark the previous one as Finished
        self._run_jobs()

        # Check that the file was not requested
        assert len(responses.calls) == 0

        # Get the harvest source with the udpated status
        harvest_source = helpers.call_action('harvest_source_show',
                                       id=harvest_source['id'])

        last_job_status = harvest_source['status']['last_job']

        assert last_job_status['status'] == 'Finished'

        assert last_job_status['stats']['added'] == 0

    @responses.activate
    def test_harvest_before_download_errors_get_stored(self, reset_calls_counter):

        reset_calls_counter('test_rdf_harvester')
        plugin = p.get_plugin('test_rdf_harvester')

        source_url = 'http://return.errors'

        # Mock the GET request to get the file
        responses.add(responses.GET, source_url,
                               body=self.rdf_content,
                               content_type=self.rdf_content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # this as well
        responses.add(responses.HEAD, source_url,
                               status=405,
                               content_type=self.rdf_content_type)

        harvest_source = self._create_harvest_source(source_url)
        self._create_harvest_job(harvest_source['id'])
        self._run_jobs(harvest_source['id'])
        self._gather_queue(1)

        assert plugin.calls['before_download'] == 1

        # Run the jobs to mark the previous one as Finished
        self._run_jobs()

        # Check that the file was not requested
        assert len(responses.calls) == 0

        # Get the harvest source with the udpated status
        harvest_source = helpers.call_action('harvest_source_show',
                                       id=harvest_source['id'])

        last_job_status = harvest_source['status']['last_job']

        assert 'Error 1' == last_job_status['gather_error_summary'][0][0]
        assert 'Error 2' == last_job_status['gather_error_summary'][1][0]

    def test_harvest_update_session_extension_point_gets_called(self, reset_calls_counter):

        reset_calls_counter('test_rdf_harvester')
        plugin = p.get_plugin('test_rdf_harvester')


        harvest_source = self._create_harvest_source(self.rdf_mock_url)
        self._create_harvest_job(harvest_source['id'])
        self._run_jobs(harvest_source['id'])
        self._gather_queue(1)

        assert plugin.calls['update_session'] == 1

    @responses.activate
    def test_harvest_update_session_add_header(self, reset_calls_counter):

        reset_calls_counter('test_rdf_harvester')
        plugin = p.get_plugin('test_rdf_harvester')

        responses.add(responses.GET, self.rdf_mock_url)
        responses.add(responses.HEAD, self.rdf_mock_url)

        harvest_source = self._create_harvest_source(self.rdf_mock_url)
        self._create_harvest_job(harvest_source['id'])
        self._run_jobs(harvest_source['id'])
        self._gather_queue(1)

        assert plugin.calls['update_session'] == 1

        # Run the jobs to mark the previous one as Finished
        self._run_jobs()

        # Check that the header was actually set
        assert ('true'
                in responses.calls[-1].request.headers['x-test'])

    @responses.activate
    def test_harvest_after_download_extension_point_gets_called(self, reset_calls_counter):

        reset_calls_counter('test_rdf_harvester')
        plugin = p.get_plugin('test_rdf_harvester')

        # Mock the GET request to get the file
        responses.add(responses.GET, self.rdf_mock_url)

        # The harvester will try to do a HEAD request first so we need to mock
        # this as well
        responses.add(responses.HEAD, self.rdf_mock_url,
                               status=405)

        harvest_source = self._create_harvest_source(self.rdf_mock_url)
        self._create_harvest_job(harvest_source['id'])
        self._run_jobs(harvest_source['id'])
        self._gather_queue(1)

        assert plugin.calls['after_download'] == 1

    @responses.activate
    def test_harvest_after_download_empty_content_stops_gather_stage(self, reset_calls_counter):

        reset_calls_counter('test_rdf_harvester')
        plugin = p.get_plugin('test_rdf_harvester')

        source_url = 'http://return.empty.content'

        # Mock the GET request to get the file
        responses.add(responses.GET, source_url,
                               body='return.empty.content',
                               content_type=self.rdf_content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # this as well
        responses.add(responses.HEAD, source_url,
                               status=405,
                               content_type=self.rdf_content_type)

        harvest_source = self._create_harvest_source(source_url)
        self._create_harvest_job(harvest_source['id'])
        self._run_jobs(harvest_source['id'])
        self._gather_queue(1)

        assert plugin.calls['after_download'] == 1

        # Run the jobs to mark the previous one as Finished
        self._run_jobs()

        # Check that the file was requested
        assert ('return.empty.content'
                in responses.calls[-1].request.url)

        # Get the harvest source with the udpated status
        harvest_source = helpers.call_action('harvest_source_show',
                                       id=harvest_source['id'])

        last_job_status = harvest_source['status']['last_job']

        assert last_job_status['status'] == 'Finished'

        assert last_job_status['stats']['added'] == 0

    @responses.activate
    def test_harvest_after_download_errors_get_stored(self, reset_calls_counter):

        reset_calls_counter('test_rdf_harvester')
        plugin = p.get_plugin('test_rdf_harvester')

        source_url = 'http://return.content.errors'

        # Mock the GET request to get the file
        responses.add(responses.GET, source_url,
                               body='return.errors',
                               content_type=self.rdf_content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # this as well
        responses.add(responses.HEAD, source_url,
                               status=405,
                               content_type=self.rdf_content_type)

        harvest_source = self._create_harvest_source(source_url)
        self._create_harvest_job(harvest_source['id'])
        self._run_jobs(harvest_source['id'])
        self._gather_queue(1)

        assert plugin.calls['after_download'] == 1

        # Run the jobs to mark the previous one as Finished
        self._run_jobs()

        # Check that the file was requested
        assert ('return.content.errors'
                in responses.calls[-1].request.url)

        # Get the harvest source with the udpated status
        harvest_source = helpers.call_action('harvest_source_show',
                                       id=harvest_source['id'])

        last_job_status = harvest_source['status']['last_job']

        assert 'Error 1' == last_job_status['gather_error_summary'][0][0]
        assert 'Error 2' == last_job_status['gather_error_summary'][1][0]

    @responses.activate
    def test_harvest_after_parsing_extension_point_gets_called(self, reset_calls_counter):

        reset_calls_counter('test_rdf_harvester')
        plugin = p.get_plugin('test_rdf_harvester')

        url = self.rdf_mock_url
        content =  self.rdf_content
        content_type = self.rdf_content_type

        # Mock the GET request to get the file
        responses.add(responses.GET, url,
                               body=content, content_type=content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # this as well
        responses.add(responses.HEAD, url,
                               status=405, content_type=content_type)

        harvest_source = self._create_harvest_source(self.rdf_mock_url)
        self._create_harvest_job(harvest_source['id'])
        self._run_jobs(harvest_source['id'])
        self._gather_queue(1)

        assert plugin.calls['after_parsing'] == 1

    @responses.activate
    def test_harvest_after_parsing_empty_content_stops_gather_stage(self, reset_calls_counter):

        reset_calls_counter('test_rdf_harvester')
        plugin = p.get_plugin('test_rdf_harvester')
        plugin.after_parsing_mode = 'return.empty.rdf_parser'

        # ensure after_parsing_mode is reset, so wrap in try..finally block
        try:
            url = self.rdf_mock_url
            content =  self.rdf_content
            content_type = self.rdf_content_type

            # Mock the GET request to get the file
            responses.add(responses.GET, url,
                                body=content, content_type=content_type)

            # The harvester will try to do a HEAD request first so we need to mock
            # this as well
            responses.add(responses.HEAD, url,
                                status=405, content_type=content_type)

            harvest_source = self._create_harvest_source(self.rdf_mock_url)
            self._create_harvest_job(harvest_source['id'])
            self._run_jobs(harvest_source['id'])
            self._gather_queue(1)

            assert plugin.calls['after_parsing'] == 1

            # Run the jobs to mark the previous one as Finished
            self._run_jobs()

            # Get the harvest source with the updated status
            harvest_source = helpers.call_action('harvest_source_show',
                                        id=harvest_source['id'])

            last_job_status = harvest_source['status']['last_job']

            assert last_job_status['status'] == 'Finished'

            assert last_job_status['stats']['added'] == 0
        finally:
            plugin.after_parsing_mode = ''


    @responses.activate
    def test_harvest_after_parsing_errors_get_stored(self, reset_calls_counter):

        reset_calls_counter('test_rdf_harvester')
        plugin = p.get_plugin('test_rdf_harvester')
        plugin.after_parsing_mode = 'return.errors'

        # ensure after_parsing_mode is reset, so wrap in try..finally block
        try:
            url = self.rdf_mock_url
            content =  self.rdf_content
            content_type = self.rdf_content_type

            # Mock the GET request to get the file
            responses.add(responses.GET, url,
                                body=content, content_type=content_type)

            # The harvester will try to do a HEAD request first so we need to mock
            # this as well
            responses.add(responses.HEAD, url,
                                status=405, content_type=content_type)

            harvest_source = self._create_harvest_source(self.rdf_mock_url)
            self._create_harvest_job(harvest_source['id'])
            self._run_jobs(harvest_source['id'])
            self._gather_queue(1)

            assert plugin.calls['after_parsing'] == 1

            # Run the jobs to mark the previous one as Finished
            self._run_jobs()

            # Get the harvest source with the updated status
            harvest_source = helpers.call_action('harvest_source_show',
                                        id=harvest_source['id'])

            last_job_status = harvest_source['status']['last_job']

            assert 'Error 1' == last_job_status['gather_error_summary'][0][0]
            assert 'Error 2' == last_job_status['gather_error_summary'][1][0]
        finally:
            plugin.after_parsing_mode = ''

    @responses.activate
    def test_harvest_import_extensions_point_gets_called(self, reset_calls_counter):

        reset_calls_counter('test_rdf_harvester')
        plugin = p.get_plugin('test_rdf_harvester')

        url = self.rdf_mock_url
        content =  self.rdf_content
        content_type = self.rdf_content_type

        # Mock the GET request to get the file
        responses.add(responses.GET, url,
                               body=content, content_type=content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # this as well
        responses.add(responses.HEAD, url,
                               status=405, content_type=content_type)

        harvest_source = self._create_harvest_source(url)

        # First run, will create two datasets as previously tested
        self._run_full_job(harvest_source['id'], num_objects=2)

        # Run the jobs to mark the previous one as Finished
        self._run_jobs()

        # Get the harvest source with the udpated status
        harvest_source = helpers.call_action('harvest_source_show',
                                       id=harvest_source['id'])
        last_job_status = harvest_source['status']['last_job']
        assert last_job_status['status'] == 'Finished'

        assert plugin.calls['update_package_schema_for_create'] == 2
        assert plugin.calls['before_create'] == 2
        assert plugin.calls['after_create'] == 2
        assert plugin.calls['update_package_schema_for_update'] == 0
        assert plugin.calls['before_update'] == 0
        assert plugin.calls['after_update'] == 0

        # Mock an update in the remote file
        new_file = content.replace('Example dataset 1',
                                   'Example dataset 1 (updated)')
        responses.add(responses.GET, url,
                               body=new_file, content_type=content_type)

        # Run a second job
        self._run_full_job(harvest_source['id'], num_objects=2)

        assert plugin.calls['update_package_schema_for_create'] == 2
        assert plugin.calls['before_create'] == 2
        assert plugin.calls['after_create'] == 2
        assert plugin.calls['update_package_schema_for_update'] == 2
        assert plugin.calls['before_update'] == 2
        assert plugin.calls['after_update'] == 2


@pytest.mark.usefixtures(
    'with_plugins',
    'clean_db',
    'clean_index',
    'harvest_setup',
    'clean_queues',
)
@pytest.mark.ckan_config('ckan.plugins', 'dcat harvest dcat_rdf_harvester test_rdf_null_harvester')
class TestDCATHarvestFunctionalSetNull(FunctionalHarvestTest):

    @responses.activate
    def test_harvest_with_before_create_null(self, reset_calls_counter):

        reset_calls_counter('test_rdf_null_harvester')
        plugin = p.get_plugin('test_rdf_null_harvester')

        url = self.rdf_mock_url
        content =  self.rdf_content
        content_type = self.rdf_content_type

        # Mock the GET request to get the file
        responses.add(responses.GET, url,
                               body=content, content_type=content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # this as well
        responses.add(responses.HEAD, url,
                               status=405, content_type=content_type)

        harvest_source = self._create_harvest_source(url)

        self._run_full_job(harvest_source['id'], num_objects=2)

        # Run the jobs to mark the previous one as Finished
        self._run_jobs()

        # Get the harvest source with the updated status
        harvest_source = helpers.call_action('harvest_source_show',
                                       id=harvest_source['id'])
        last_job_status = harvest_source['status']['last_job']
        assert last_job_status['status'] == 'Finished'

        assert (last_job_status['stats'] ==
            {
                'deleted': 0,
                'added': 0,
                'updated': 0,
                'not modified': 2,
                'errored': 0
            }
        )

        assert plugin.calls['update_package_schema_for_create'] == 2
        assert plugin.calls['before_create'] == 2
        assert plugin.calls['after_create'] == 0
        assert plugin.calls['update_package_schema_for_update'] == 0
        assert plugin.calls['before_update'] == 0
        assert plugin.calls['after_update'] == 0


@pytest.mark.usefixtures(
    'with_plugins',
    'clean_db',
    'clean_index',
    'harvest_setup',
    'clean_queues',
)
@pytest.mark.ckan_config('ckan.plugins', 'dcat harvest dcat_rdf_harvester test_rdf_exception_harvester')
class TestDCATHarvestFunctionalRaiseExcpetion(FunctionalHarvestTest):

    @responses.activate
    def test_harvest_with_before_create_raising_exception(self, reset_calls_counter):
        reset_calls_counter('test_rdf_exception_harvester')
        plugin = p.get_plugin('test_rdf_exception_harvester')

        url = self.rdf_mock_url
        content =  self.rdf_content
        content_type = self.rdf_content_type

        # Mock the GET request to get the file
        responses.add(responses.GET, url,
                               body=content, content_type=content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # this as well
        responses.add(responses.HEAD, url,
                               status=405, content_type=content_type)

        harvest_source = self._create_harvest_source(url)

        self._run_full_job(harvest_source['id'], num_objects=2)

        # Run the jobs to mark the previous one as Finished
        self._run_jobs()

        # Get the harvest source with the updated status
        harvest_source = helpers.call_action('harvest_source_show',
                                       id=harvest_source['id'])
        last_job_status = harvest_source['status']['last_job']
        assert last_job_status['status'] == 'Finished'

        assert ('Error importing dataset'
                in last_job_status['object_error_summary'][0][0])

        assert (
            last_job_status['stats'] ==
            {
                'deleted': 0,
                'added': 1,
                'updated': 0,
                'not modified': 0,
                'errored': 1
            }
        )
        assert plugin.calls['update_package_schema_for_create'] == 2
        assert plugin.calls['before_create'] == 2
        assert plugin.calls['after_create'] == 1
        assert plugin.calls['update_package_schema_for_update'] == 0
        assert plugin.calls['before_update'] == 0
        assert plugin.calls['after_update'] == 0


class TestDCATRDFHarvester(object):

    def test_validates_correct_config(self):
        harvester = DCATRDFHarvester()

        for config in ['{}', '{"rdf_format":"text/turtle"}']:
            assert config == harvester.validate_config(config)

    def test_does_not_validate_incorrect_config(self):
        harvester = DCATRDFHarvester()

        for config in ['invalid', '{invalid}', '{rdf_format:invalid}']:
            try:
                harvester.validate_config(config)
                assert False
            except ValueError:
                assert True


class TestIDCATRDFHarvester(object):

    def test_before_download(self):

        i = IDCATRDFHarvester()

        url = 'http://some.url'

        values = i.before_download(url, {})

        assert values[0] == url
        assert values[1] == []

    def test_after_download(self):

        i = IDCATRDFHarvester()

        content = 'some.content'

        values = i.after_download(content, {})

        assert values[0] == content
        assert values[1] == []

    def test_after_parsing(self):

        i = IDCATRDFHarvester()

        rdf_parser = 'some.parser'

        values = i.after_parsing(rdf_parser, {})

        assert values[0] == rdf_parser
        assert values[1] == []

    def test_update_package_schema_for_create(self):

        i = IDCATRDFHarvester()

        package_schema = dict(some_validator='some.content')

        value = i.update_package_schema_for_create(package_schema)

        assert value == package_schema

    def test_update_package_schema_for_update(self):

        i = IDCATRDFHarvester()

        package_schema = dict(some_validator='some.content')

        value = i.update_package_schema_for_update(package_schema)

        assert value == package_schema
