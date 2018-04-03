import httpretty
import nose

import ckantoolkit.tests.helpers as h

from test_harvester import FunctionalHarvestTest

eq_ = nose.tools.eq_

class TestDCATJSONHarvestFunctional(FunctionalHarvestTest):

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

    def test_harvest_create(self):

        self._test_harvest_create(self.json_mock_url,
                                  self.json_content,
                                  self.json_content_type)

    def _test_harvest_create(self, url, content, content_type, num_datasets=2,
                             **kwargs):

        # Mock the GET request to get the file
        httpretty.register_uri(httpretty.GET, url,
                               body=content, content_type=content_type)

        # The harvester will try to do a HEAD request first so we need to mock
        # this as well
        httpretty.register_uri(httpretty.HEAD, url,
                               status=405, content_type=content_type)

        kwargs['source_type'] = 'dcat_json'
        harvest_source = self._create_harvest_source(url, **kwargs)

        self._run_full_job(harvest_source['id'], num_objects=num_datasets)

        fq = "+type:dataset harvest_source_id:{0}".format(harvest_source['id'])
        results = h.call_action('package_search', {}, fq=fq)

        eq_(results['count'], num_datasets)
        for result in results['results']:
            assert result['title'] in ('Example dataset 1',
                                       'Example dataset 2')
