# -*- coding: utf-8 -*-

from collections import defaultdict

import nose
import httpretty
from mock import patch

import ckan.plugins as p
import ckantoolkit.tests.helpers as h

import ckanext.harvest.model as harvest_model
from ckanext.harvest import queue

from ckanext.dcat.harvesters import DCATRDFHarvester, DCATJSONHarvester
from ckanext.dcat.interfaces import IDCATRDFHarvester
import ckanext.dcat.harvesters.rdf


eq_ = nose.tools.eq_


# This horrible monkey patch is needed because httpretty does not play well
# with redis, so we need to disable it straight after the mocked call is used.
# See https://github.com/gabrielfalcao/HTTPretty/issues/113

# Start monkey-patch

original_rdf_get_content_and_type = DCATRDFHarvester._get_content_and_type

def _patched_rdf_get_content_and_type(self, url, harvest_job, page=1, content_type=None):

    httpretty.enable()

    value1, value2 = original_rdf_get_content_and_type(self, url, harvest_job, page, content_type)

    httpretty.disable()

    return value1, value2

DCATRDFHarvester._get_content_and_type = _patched_rdf_get_content_and_type

original_json_get_content_and_type = DCATJSONHarvester._get_content_and_type

def _patched_json_get_content_and_type(self, url, harvest_job, page=1, content_type=None):

    httpretty.enable()

    value1, value2 = original_json_get_content_and_type(self, url, harvest_job, page, content_type)

    httpretty.disable()

    return value1, value2

DCATJSONHarvester._get_content_and_type = _patched_json_get_content_and_type

# End monkey-patch


class TestRDFHarvester(p.SingletonPlugin):

    p.implements(IDCATRDFHarvester)

    calls = defaultdict(int)

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

    def test_get_guid_uri(self):

        dataset = {
            'name': 'test-dataset',
            'extras': [
                {'key': 'uri', 'value': 'http://dataset/uri'},
                {'key': 'dcat_identifier', 'value': 'dataset_dcat_id'},
            ]
        }

        guid = DCATRDFHarvester()._get_guid(dataset)

        eq_(guid, 'http://dataset/uri')

    def test_get_guid_identifier(self):

        dataset = {
            'name': 'test-dataset',
            'extras': [
                {'key': 'identifier', 'value': 'dataset_dcat_id'},
            ]
        }

        guid = DCATRDFHarvester()._get_guid(dataset)

        eq_(guid, 'dataset_dcat_id')

    def test_get_guid_dcat_identifier(self):

        dataset = {
            'name': 'test-dataset',
            'extras': [
                {'key': 'dcat_identifier', 'value': 'dataset_dcat_id'},
            ]
        }

        guid = DCATRDFHarvester()._get_guid(dataset)

        eq_(guid, 'dataset_dcat_id')

    def test_get_guid_uri_none(self):

        dataset = {
            'name': 'test-dataset',
            'extras': [
                {'key': 'uri', 'value': None},
                {'key': 'dcat_identifier', 'value': 'dataset_dcat_id'},
            ]
        }

        guid = DCATRDFHarvester()._get_guid(dataset)

        eq_(guid, 'dataset_dcat_id')

    def test_get_guid_dcat_identifier_none(self):

        dataset = {
            'name': 'test-dataset',
            'extras': [
                {'key': 'dcat_identifier', 'value': None},
            ]
        }

        guid = DCATRDFHarvester()._get_guid(dataset)

        eq_(guid, 'test-dataset')

    def test_get_guid_source_url_name(self):

        dataset = {
            'name': 'test-dataset',
            'extras': [
            ]
        }

        guid = DCATRDFHarvester()._get_guid(dataset, 'http://source_url')

        eq_(guid, 'http://source_url/test-dataset')

        guid = DCATRDFHarvester()._get_guid(dataset, 'http://source_url/')

        eq_(guid, 'http://source_url/test-dataset')

    def test_get_guid_name(self):

        dataset = {
            'name': 'test-dataset',
            'extras': [
            ]
        }

        guid = DCATRDFHarvester()._get_guid(dataset)

        eq_(guid, 'test-dataset')

    def test_get_guid_none(self):

        dataset = {
            'extras': [
            ]
        }

        guid = DCATRDFHarvester()._get_guid(dataset)

        eq_(guid, None)


class FunctionalHarvestTest(object):

    @classmethod
    def setup_class(cls):

        h.reset_db()

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
        # Use slashes for paginated URLs because HTTPretty won't distinguish
        # query strings
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

    def setup(self):

        harvest_model.setup()

        queue.purge_queues()

    def teardown(cls):
        h.reset_db()

    def _create_harvest_source(self, mock_url, **kwargs):

        source_dict = {
            'title': 'Test RDF DCAT Source',
            'name': 'test-rdf-dcat-source',
            'url': mock_url,
            'source_type': 'dcat_rdf',
        }

        source_dict.update(**kwargs)

        harvest_source = h.call_action('harvest_source_create',
                                       {}, **source_dict)

        return harvest_source

    def _create_harvest_job(self, harvest_source_id):

        harvest_job = h.call_action('harvest_job_create',
                                    {}, source_id=harvest_source_id)

        return harvest_job

    def _run_jobs(self, harvest_source_id=None):
        try:
            h.call_action('harvest_jobs_run',
                          {}, source_id=harvest_source_id)
        except Exception, e:
            if (str(e) == 'There are no new harvesting jobs'):
                pass

    def _gather_queue(self, num_jobs=1):

        for job in xrange(num_jobs):
            # Pop one item off the queue (the job id) and run the callback
            reply = self.gather_consumer.basic_get(
                queue='ckan.harvest.gather.test')

            # Make sure something was sent to the gather queue
            assert reply[2], 'Empty gather queue'

            # Send the item to the gather callback, which will call the
            # harvester gather_stage
            queue.gather_callback(self.gather_consumer, *reply)

    def _fetch_queue(self, num_objects=1):

        for _object in xrange(num_objects):
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

    def _test_harvest_create(self, url, content, content_type, **kwargs):

        # Mock the GET request to get the file
        httpretty.register_uri(httpretty.GET, url,
                               body=content, content_type=content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # this as well
        httpretty.register_uri(httpretty.HEAD, url,
                               status=405, content_type=content_type)

        harvest_source = self._create_harvest_source(url, **kwargs)

        self._run_full_job(harvest_source['id'], num_objects=2)

        # Check that two datasets were created
        fq = "+type:dataset harvest_source_id:{0}".format(harvest_source['id'])
        results = h.call_action('package_search', {}, fq=fq)

        eq_(results['count'], 2)
        for result in results['results']:
            assert result['title'] in ('Example dataset 1',
                                       'Example dataset 2')

    def test_harvest_create_rdf_pagination(self):

        # Mock the GET requests needed to get the file
        httpretty.register_uri(httpretty.GET, self.rdf_mock_url_pagination_1,
                               body=self.rdf_content_pagination_1,
                               content_type=self.rdf_content_type)

        httpretty.register_uri(httpretty.GET, self.rdf_mock_url_pagination_2,
                               body=self.rdf_content_pagination_2,
                               content_type=self.rdf_content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # them as well
        httpretty.register_uri(httpretty.HEAD, self.rdf_mock_url_pagination_1,
                               status=405,
                               content_type=self.rdf_content_type)

        httpretty.register_uri(httpretty.HEAD, self.rdf_mock_url_pagination_2,
                               status=405,
                               content_type=self.rdf_content_type)

        harvest_source = self._create_harvest_source(
            self.rdf_mock_url_pagination_1)

        self._run_full_job(harvest_source['id'], num_objects=4)

        # Check that four datasets were created
        fq = "+type:dataset harvest_source_id:{0}".format(harvest_source['id'])
        results = h.call_action('package_search', {}, fq=fq)

        eq_(results['count'], 4)
        eq_(sorted([d['title'] for d in results['results']]),
            ['Example dataset 1', 'Example dataset 2',
             'Example dataset 3', 'Example dataset 4'])

    def test_harvest_create_rdf_pagination_same_content(self):

        # Mock the GET requests needed to get the file. Two different URLs but
        # same content to mock a misconfigured server
        httpretty.register_uri(httpretty.GET, self.rdf_mock_url_pagination_1,
                               body=self.rdf_content_pagination_1,
                               content_type=self.rdf_content_type)

        httpretty.register_uri(httpretty.GET, self.rdf_mock_url_pagination_2,
                               body=self.rdf_content_pagination_1,
                               content_type=self.rdf_content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # them as well
        httpretty.register_uri(httpretty.HEAD, self.rdf_mock_url_pagination_1,
                               status=405,
                               content_type=self.rdf_content_type)

        httpretty.register_uri(httpretty.HEAD, self.rdf_mock_url_pagination_2,
                               status=405,
                               content_type=self.rdf_content_type)

        harvest_source = self._create_harvest_source(
            self.rdf_mock_url_pagination_1)

        self._run_full_job(harvest_source['id'], num_objects=2)

        # Check that two datasets were created
        fq = "+type:dataset harvest_source_id:{0}".format(harvest_source['id'])
        results = h.call_action('package_search', {}, fq=fq)

        eq_(results['count'], 2)
        eq_(sorted([d['title'] for d in results['results']]),
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

    def _test_harvest_update(self, url, content, content_type):
        # Mock the GET request to get the file
        httpretty.register_uri(httpretty.GET, url,
                               body=content, content_type=content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # this as well
        httpretty.register_uri(httpretty.HEAD, url,
                               status=405, content_type=content_type)

        harvest_source = self._create_harvest_source(url)

        # First run, will create two datasets as previously tested
        self._run_full_job(harvest_source['id'], num_objects=2)

        # Run the jobs to mark the previous one as Finished
        self._run_jobs()

        # Mock an update in the remote file
        new_file = content.replace('Example dataset 1',
                                   'Example dataset 1 (updated)')
        httpretty.register_uri(httpretty.GET, url,
                               body=new_file, content_type=content_type)

        # Run a second job
        self._run_full_job(harvest_source['id'], num_objects=2)

        # Check that we still have two datasets
        fq = "+type:dataset harvest_source_id:{0}".format(harvest_source['id'])
        results = h.call_action('package_search', {}, fq=fq)

        eq_(results['count'], 2)

        # Check that the dataset was updated
        for result in results['results']:
            assert result['title'] in ('Example dataset 1 (updated)',
                                       'Example dataset 2')

    def test_harvest_update_existing_resources(self):

        existing, new = self._test_harvest_update_resources(self.rdf_mock_url,
                                  self.rdf_content_with_distribution_uri,
                                  self.rdf_content_type)
        eq_(new['uri'], 'https://data.some.org/catalog/datasets/1/resource/1')
        eq_(new['uri'], existing['uri'])
        eq_(new['id'], existing['id'])

    def test_harvest_update_new_resources(self):

        existing, new = self._test_harvest_update_resources(self.rdf_mock_url,
                                  self.rdf_content_with_distribution,
                                  self.rdf_content_type)
        eq_(existing['uri'], '')
        eq_(new['uri'], '')
        nose.tools.assert_is_not(new['id'], existing['id'])

    def _test_harvest_update_resources(self, url, content, content_type):
        # Mock the GET request to get the file
        httpretty.register_uri(httpretty.GET, url,
                               body=content, content_type=content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # this as well
        httpretty.register_uri(httpretty.HEAD, url,
                               status=405, content_type=content_type)

        harvest_source = self._create_harvest_source(url)

        # First run, create the dataset with the resource
        self._run_full_job(harvest_source['id'], num_objects=1)

        # Run the jobs to mark the previous one as Finished
        self._run_jobs()

        # get the created dataset
        fq = "+type:dataset harvest_source_id:{0}".format(harvest_source['id'])
        results = h.call_action('package_search', {}, fq=fq)
        eq_(results['count'], 1)

        existing_dataset = results['results'][0]
        existing_resource = existing_dataset.get('resources')[0]

        # Mock an update in the remote file
        new_file = content.replace('Example resource 1',
                                   'Example resource 1 (updated)')
        httpretty.register_uri(httpretty.GET, url,
                               body=new_file, content_type=content_type)

        # Run a second job
        self._run_full_job(harvest_source['id'])

        # get the updated dataset
        new_results = h.call_action('package_search', {}, fq=fq)
        eq_(new_results['count'], 1)

        new_dataset = new_results['results'][0]
        new_resource = new_dataset.get('resources')[0]

        eq_(existing_resource['name'], 'Example resource 1')
        eq_(len(new_dataset.get('resources')), 1)
        eq_(new_resource['name'], 'Example resource 1 (updated)')
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

    def _test_harvest_delete(self, url, content, content_small, content_type):

        # Mock the GET request to get the file
        httpretty.register_uri(httpretty.GET, url,
                               body=content, content_type=content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # this as well
        httpretty.register_uri(httpretty.HEAD, url,
                               status=405, content_type=content_type)

        harvest_source = self._create_harvest_source(url)

        # First run, will create two datasets as previously tested
        self._run_full_job(harvest_source['id'], num_objects=2)

        # Run the jobs to mark the previous one as Finished
        self._run_jobs()

        # Mock a deletion in the remote file
        httpretty.register_uri(httpretty.GET, url,
                               body=content_small, content_type=content_type)

        # Run a second job
        self._run_full_job(harvest_source['id'], num_objects=2)

        # Check that we only have one dataset
        fq = "+type:dataset harvest_source_id:{0}".format(harvest_source['id'])
        results = h.call_action('package_search', {}, fq=fq)

        eq_(results['count'], 1)

        eq_(results['results'][0]['title'], 'Example dataset 1')

    def test_harvest_bad_format_rdf(self):

        self._test_harvest_bad_format(self.rdf_mock_url,
                                      self.rdf_remote_file_invalid,
                                      self.rdf_content_type)

    def test_harvest_bad_format_ttl(self):

        self._test_harvest_bad_format(self.ttl_mock_url,
                                      self.ttl_remote_file_invalid,
                                      self.ttl_content_type)

    def _test_harvest_bad_format(self, url, bad_content, content_type):

        # Mock the GET request to get the file
        httpretty.register_uri(httpretty.GET, url,
                               body=bad_content, content_type=content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # this as well
        httpretty.register_uri(httpretty.HEAD, url,
                               status=405, content_type=content_type)

        harvest_source = self._create_harvest_source(url)
        self._create_harvest_job(harvest_source['id'])
        self._run_jobs(harvest_source['id'])
        self._gather_queue(1)

        # Run the jobs to mark the previous one as Finished
        self._run_jobs()

        # Get the harvest source with the udpated status
        harvest_source = h.call_action('harvest_source_show',
                                       id=harvest_source['id'])

        last_job_status = harvest_source['status']['last_job']

        eq_(last_job_status['status'], 'Finished')
        assert ('Error parsing the RDF file'
                in last_job_status['gather_error_summary'][0][0])

    @patch.object(ckanext.dcat.harvesters.rdf.RDFParser, 'datasets')
    def test_harvest_exception_in_profile(self, mock_datasets):
        mock_datasets.side_effect = Exception

        # Mock the GET request to get the file
        httpretty.register_uri(httpretty.GET, self.rdf_mock_url,
                               body=self.rdf_content, content_type=self.rdf_content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # this as well
        httpretty.register_uri(httpretty.HEAD, self.rdf_mock_url,
                               status=405, content_type=self.rdf_content_type)

        harvest_source = self._create_harvest_source(self.rdf_mock_url)
        self._create_harvest_job(harvest_source['id'])
        self._run_jobs(harvest_source['id'])
        self._gather_queue(1)

        # Run the jobs to mark the previous one as Finished
        self._run_jobs()

        # Get the harvest source with the udpated status
        harvest_source = h.call_action('harvest_source_show',
                                       id=harvest_source['id'])

        last_job_status = harvest_source['status']['last_job']

        eq_(last_job_status['status'], 'Finished')
        assert ('Error when processsing dataset'
                in last_job_status['gather_error_summary'][0][0])


class TestDCATHarvestFunctionalExtensionPoints(FunctionalHarvestTest):

    @classmethod
    def setup_class(self):

        super(TestDCATHarvestFunctionalExtensionPoints, self).setup_class()

        p.load('test_rdf_harvester')

    @classmethod
    def teardown_class(self):

        p.unload('test_rdf_harvester')

    def setup(self):

        super(TestDCATHarvestFunctionalExtensionPoints, self).setup()

        plugin = p.get_plugin('test_rdf_harvester')
        plugin.calls = defaultdict(int)

    def teardown(self):

        super(TestDCATHarvestFunctionalExtensionPoints, self).teardown()

        plugin = p.get_plugin('test_rdf_harvester')
        plugin.calls = defaultdict(int)

    def test_harvest_before_download_extension_point_gets_called(self):

        plugin = p.get_plugin('test_rdf_harvester')

        harvest_source = self._create_harvest_source(self.rdf_mock_url)
        self._create_harvest_job(harvest_source['id'])
        self._run_jobs(harvest_source['id'])
        self._gather_queue(1)

        eq_(plugin.calls['before_download'], 1)

    def test_harvest_before_download_null_url_stops_gather_stage(self):

        plugin = p.get_plugin('test_rdf_harvester')

        source_url = 'http://return.none'

        # Mock the GET request to get the file
        httpretty.register_uri(httpretty.GET, source_url,
                               body=self.rdf_content,
                               content_type=self.rdf_content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # this as well
        httpretty.register_uri(httpretty.HEAD, source_url,
                               status=405,
                               content_type=self.rdf_content_type)

        harvest_source = self._create_harvest_source(source_url)
        self._create_harvest_job(harvest_source['id'])
        self._run_jobs(harvest_source['id'])
        self._gather_queue(1)

        eq_(plugin.calls['before_download'], 1)

        # Run the jobs to mark the previous one as Finished
        self._run_jobs()

        # Check that the file was not requested
        assert 'return.none' not in httpretty.last_request().headers['host']

        # Get the harvest source with the udpated status
        harvest_source = h.call_action('harvest_source_show',
                                       id=harvest_source['id'])

        last_job_status = harvest_source['status']['last_job']

        eq_(last_job_status['status'], 'Finished')

        eq_(last_job_status['stats']['added'], 0)

    def test_harvest_before_download_errors_get_stored(self):

        plugin = p.get_plugin('test_rdf_harvester')

        source_url = 'http://return.errors'

        # Mock the GET request to get the file
        httpretty.register_uri(httpretty.GET, source_url,
                               body=self.rdf_content,
                               content_type=self.rdf_content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # this as well
        httpretty.register_uri(httpretty.HEAD, source_url,
                               status=405,
                               content_type=self.rdf_content_type)

        harvest_source = self._create_harvest_source(source_url)
        self._create_harvest_job(harvest_source['id'])
        self._run_jobs(harvest_source['id'])
        self._gather_queue(1)

        eq_(plugin.calls['before_download'], 1)

        # Run the jobs to mark the previous one as Finished
        self._run_jobs()

        # Check that the file was not requested
        assert 'return.errors' not in httpretty.last_request().headers['host']

        # Get the harvest source with the udpated status
        harvest_source = h.call_action('harvest_source_show',
                                       id=harvest_source['id'])

        last_job_status = harvest_source['status']['last_job']

        eq_('Error 1', last_job_status['gather_error_summary'][0][0])
        eq_('Error 2', last_job_status['gather_error_summary'][1][0])

    def test_harvest_update_session_extension_point_gets_called(self):

        plugin = p.get_plugin('test_rdf_harvester')

        harvest_source = self._create_harvest_source(self.rdf_mock_url)
        self._create_harvest_job(harvest_source['id'])
        self._run_jobs(harvest_source['id'])
        self._gather_queue(1)

        eq_(plugin.calls['update_session'], 1)

    def test_harvest_update_session_add_header(self):

        plugin = p.get_plugin('test_rdf_harvester')

        harvest_source = self._create_harvest_source(self.rdf_mock_url)
        self._create_harvest_job(harvest_source['id'])
        self._run_jobs(harvest_source['id'])
        self._gather_queue(1)

        eq_(plugin.calls['update_session'], 1)

        # Run the jobs to mark the previous one as Finished
        self._run_jobs()

        # Check that the header was actually set
        assert ('true'
                in httpretty.last_request().headers['x-test'])

    def test_harvest_after_download_extension_point_gets_called(self):

        plugin = p.get_plugin('test_rdf_harvester')

        # Mock the GET request to get the file
        httpretty.register_uri(httpretty.GET, self.rdf_mock_url)

        # The harvester will try to do a HEAD request first so we need to mock
        # this as well
        httpretty.register_uri(httpretty.HEAD, self.rdf_mock_url,
                               status=405)

        harvest_source = self._create_harvest_source(self.rdf_mock_url)
        self._create_harvest_job(harvest_source['id'])
        self._run_jobs(harvest_source['id'])
        self._gather_queue(1)

        eq_(plugin.calls['after_download'], 1)

    def test_harvest_after_download_empty_content_stops_gather_stage(self):

        plugin = p.get_plugin('test_rdf_harvester')

        source_url = 'http://return.empty.content'

        # Mock the GET request to get the file
        httpretty.register_uri(httpretty.GET, source_url,
                               body='return.empty.content',
                               content_type=self.rdf_content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # this as well
        httpretty.register_uri(httpretty.HEAD, source_url,
                               status=405,
                               content_type=self.rdf_content_type)

        harvest_source = self._create_harvest_source(source_url)
        self._create_harvest_job(harvest_source['id'])
        self._run_jobs(harvest_source['id'])
        self._gather_queue(1)

        eq_(plugin.calls['after_download'], 1)

        # Run the jobs to mark the previous one as Finished
        self._run_jobs()

        # Check that the file was requested
        assert ('return.empty.content'
                in httpretty.last_request().headers['host'])

        # Get the harvest source with the udpated status
        harvest_source = h.call_action('harvest_source_show',
                                       id=harvest_source['id'])

        last_job_status = harvest_source['status']['last_job']

        eq_(last_job_status['status'], 'Finished')

        eq_(last_job_status['stats']['added'], 0)

    def test_harvest_after_download_errors_get_stored(self):

        plugin = p.get_plugin('test_rdf_harvester')

        source_url = 'http://return.content.errors'

        # Mock the GET request to get the file
        httpretty.register_uri(httpretty.GET, source_url,
                               body='return.errors',
                               content_type=self.rdf_content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # this as well
        httpretty.register_uri(httpretty.HEAD, source_url,
                               status=405,
                               content_type=self.rdf_content_type)

        harvest_source = self._create_harvest_source(source_url)
        self._create_harvest_job(harvest_source['id'])
        self._run_jobs(harvest_source['id'])
        self._gather_queue(1)

        eq_(plugin.calls['after_download'], 1)

        # Run the jobs to mark the previous one as Finished
        self._run_jobs()

        # Check that the file was requested
        assert ('return.content.errors'
                in httpretty.last_request().headers['host'])

        # Get the harvest source with the udpated status
        harvest_source = h.call_action('harvest_source_show',
                                       id=harvest_source['id'])

        last_job_status = harvest_source['status']['last_job']

        eq_('Error 1', last_job_status['gather_error_summary'][0][0])
        eq_('Error 2', last_job_status['gather_error_summary'][1][0])

    def test_harvest_import_extensions_point_gets_called(self):

        plugin = p.get_plugin('test_rdf_harvester')

        url = self.rdf_mock_url
        content =  self.rdf_content
        content_type = self.rdf_content_type

        # Mock the GET request to get the file
        httpretty.register_uri(httpretty.GET, url,
                               body=content, content_type=content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # this as well
        httpretty.register_uri(httpretty.HEAD, url,
                               status=405, content_type=content_type)

        harvest_source = self._create_harvest_source(url)

        # First run, will create two datasets as previously tested
        self._run_full_job(harvest_source['id'], num_objects=2)

        # Run the jobs to mark the previous one as Finished
        self._run_jobs()

        # Get the harvest source with the udpated status
        harvest_source = h.call_action('harvest_source_show',
                                       id=harvest_source['id'])
        last_job_status = harvest_source['status']['last_job']
        eq_(last_job_status['status'], 'Finished')

        eq_(plugin.calls['before_create'], 2)
        eq_(plugin.calls['after_create'], 2)
        eq_(plugin.calls['before_update'], 0)
        eq_(plugin.calls['after_update'], 0)

        # Mock an update in the remote file
        new_file = content.replace('Example dataset 1',
                                   'Example dataset 1 (updated)')
        httpretty.register_uri(httpretty.GET, url,
                               body=new_file, content_type=content_type)

        # Run a second job
        self._run_full_job(harvest_source['id'], num_objects=2)

        eq_(plugin.calls['before_create'], 2)
        eq_(plugin.calls['after_create'], 2)
        eq_(plugin.calls['before_update'], 2)
        eq_(plugin.calls['after_update'], 2)


class TestDCATHarvestFunctionalSetNull(FunctionalHarvestTest):

    @classmethod
    def setup_class(self):
        super(TestDCATHarvestFunctionalSetNull, self).setup_class()
        p.load('test_rdf_null_harvester')

    @classmethod
    def teardown_class(self):
        p.unload('test_rdf_null_harvester')

    def setup(self):
        super(TestDCATHarvestFunctionalSetNull, self).setup()

        plugin = p.get_plugin('test_rdf_null_harvester')
        plugin.calls = defaultdict(int)

    def teardown(self):
        super(TestDCATHarvestFunctionalSetNull, self).teardown()

        plugin = p.get_plugin('test_rdf_null_harvester')
        plugin.calls = defaultdict(int)

    def test_harvest_with_before_create_null(self):
        plugin = p.get_plugin('test_rdf_null_harvester')

        url = self.rdf_mock_url
        content =  self.rdf_content
        content_type = self.rdf_content_type

        # Mock the GET request to get the file
        httpretty.register_uri(httpretty.GET, url,
                               body=content, content_type=content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # this as well
        httpretty.register_uri(httpretty.HEAD, url,
                               status=405, content_type=content_type)

        harvest_source = self._create_harvest_source(url)

        self._run_full_job(harvest_source['id'], num_objects=2)

        # Run the jobs to mark the previous one as Finished
        self._run_jobs()

        # Get the harvest source with the updated status
        harvest_source = h.call_action('harvest_source_show',
                                       id=harvest_source['id'])
        last_job_status = harvest_source['status']['last_job']
        eq_(last_job_status['status'], 'Finished')

        nose.tools.assert_dict_equal(
            last_job_status['stats'],
            {
                'deleted': 0,
                'added': 0,
                'updated': 0,
                'not modified': 2,
                'errored': 0
            }
        )

        eq_(plugin.calls['before_create'], 2)
        eq_(plugin.calls['after_create'], 0)
        eq_(plugin.calls['before_update'], 0)
        eq_(plugin.calls['after_update'], 0)


class TestDCATHarvestFunctionalRaiseExcpetion(FunctionalHarvestTest):

    @classmethod
    def setup_class(self):
        super(TestDCATHarvestFunctionalRaiseExcpetion, self).setup_class()
        p.load('test_rdf_exception_harvester')

    @classmethod
    def teardown_class(self):
        p.unload('test_rdf_exception_harvester')

    def setup(self):
        super(TestDCATHarvestFunctionalRaiseExcpetion, self).setup()

        plugin = p.get_plugin('test_rdf_exception_harvester')
        plugin.calls = defaultdict(int)

    def teardown(self):
        super(TestDCATHarvestFunctionalRaiseExcpetion, self).teardown()

        plugin = p.get_plugin('test_rdf_exception_harvester')
        plugin.calls = defaultdict(int)

    def test_harvest_with_before_create_raising_exception(self):
        plugin = p.get_plugin('test_rdf_exception_harvester')

        url = self.rdf_mock_url
        content =  self.rdf_content
        content_type = self.rdf_content_type

        # Mock the GET request to get the file
        httpretty.register_uri(httpretty.GET, url,
                               body=content, content_type=content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # this as well
        httpretty.register_uri(httpretty.HEAD, url,
                               status=405, content_type=content_type)

        harvest_source = self._create_harvest_source(url)

        self._run_full_job(harvest_source['id'], num_objects=2)

        # Run the jobs to mark the previous one as Finished
        self._run_jobs()

        # Get the harvest source with the updated status
        harvest_source = h.call_action('harvest_source_show',
                                       id=harvest_source['id'])
        last_job_status = harvest_source['status']['last_job']
        eq_(last_job_status['status'], 'Finished')

        assert ('Error importing dataset'
                in last_job_status['object_error_summary'][0][0])

        nose.tools.assert_dict_equal(
            last_job_status['stats'],
            {
                'deleted': 0,
                'added': 1,
                'updated': 0,
                'not modified': 0,
                'errored': 1
            }
        )

        eq_(plugin.calls['before_create'], 2)
        eq_(plugin.calls['after_create'], 1)
        eq_(plugin.calls['before_update'], 0)
        eq_(plugin.calls['after_update'], 0)


class TestDCATRDFHarvester(object):

    def test_validates_correct_config(self):
        harvester = DCATRDFHarvester()

        for config in ['{}', '{"rdf_format":"text/turtle"}']:
            eq_(config, harvester.validate_config(config))

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

        eq_(values[0], url)
        eq_(values[1], [])

    def test_after_download(self):

        i = IDCATRDFHarvester()

        content = 'some.content'

        values = i.after_download(content, {})

        eq_(values[0], content)
        eq_(values[1], [])
