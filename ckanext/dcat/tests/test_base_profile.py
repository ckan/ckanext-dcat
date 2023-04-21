from builtins import str
from builtins import object

import pytest

from rdflib import Graph, URIRef, Literal
from rdflib.namespace import Namespace

from ckanext.dcat.profiles import RDFProfile, CleanedURIRef

from ckanext.dcat.tests.test_base_parser import _default_graph


DCT = Namespace("http://purl.org/dc/terms/")
TEST = Namespace("http://test.org/")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
ADMS = Namespace("http://www.w3.org/ns/adms#")


class TestURIRefPreprocessing(object):

    def test_with_valid_items(self):
        testUriPart = "://www.w3.org/ns/dcat#"

        for prefix in ['http', 'https']:
            assert CleanedURIRef(prefix + testUriPart) == URIRef(prefix + testUriPart)
            # leading and trailing whitespace should be removed
            assert CleanedURIRef(' ' + prefix + testUriPart + ' ') == URIRef(prefix + testUriPart)

        testNonHttpUri = "mailto:someone@example.com"
        assert CleanedURIRef(testNonHttpUri) == URIRef(testNonHttpUri)
        # leading and trailing whitespace should be removed again
        assert CleanedURIRef(' ' + testNonHttpUri + ' ') == URIRef(testNonHttpUri)

    def test_with_invalid_items(self):
        testUriPart = "://www.w3.org/ns/!dcat #"
        expectedUriPart = "://www.w3.org/ns/%21dcat%20#"

        for prefix in ['http', 'https']:
            assert CleanedURIRef(prefix + testUriPart) == URIRef(prefix + expectedUriPart)
            # applying on escaped data should have no effect
            assert CleanedURIRef(prefix + expectedUriPart) == URIRef(prefix + expectedUriPart)

        # leading and trailing space should not be escaped
        testNonHttpUri = " mailto:with space!@example.com "
        expectedNonHttpUri = "mailto:with%20space%21@example.com"

        assert CleanedURIRef(testNonHttpUri) == URIRef(expectedNonHttpUri)
        # applying on escaped data should have no effect
        assert CleanedURIRef(expectedNonHttpUri) == URIRef(expectedNonHttpUri)


class TestBaseRDFProfile(object):

    def test_datasets(self):

        p = RDFProfile(_default_graph())

        assert len([d for d in p._datasets()]) == 3

    def test_datasets_none_found(self):

        p = RDFProfile(Graph())

        assert len([d for d in p._datasets()]) == 0

    def test_distributions(self):

        p = RDFProfile(_default_graph())

        for dataset in p._datasets():
            if str(dataset) == 'http://example.org/datasets/1':
                assert len([d for d in p._distributions(dataset)]) == 2
            elif str(dataset) == 'http://example.org/datasets/2':
                assert len([d for d in p._distributions(dataset)]) == 1
            elif str(dataset) == 'http://example.org/datasets/3':
                assert len([d for d in p._distributions(dataset)]) == 0

    def test_object(self):

        p = RDFProfile(_default_graph())

        _object = p._object(URIRef('http://example.org/datasets/1'),
                            DCT.title)

        assert isinstance(_object, Literal)
        assert str(_object) == 'Test Dataset 1'

    def test_object_not_found(self):

        p = RDFProfile(_default_graph())

        _object = p._object(URIRef('http://example.org/datasets/1'),
                            DCT.unknown_property)

        assert _object == None

    def test_object_value(self):

        p = RDFProfile(_default_graph())

        value = p._object_value(URIRef('http://example.org/datasets/1'),
                                DCT.title)

        assert isinstance(value, str)
        assert value == 'Test Dataset 1'

    def test_object_value_not_found(self):

        p = RDFProfile(_default_graph())

        value = p._object_value(URIRef('http://example.org/datasets/1'),
                                DCT.unknown_property)

        assert value == ''

    @pytest.mark.ckan_config('ckan.locale_default', 'de')
    def test_object_value_default_lang(self):
        p = RDFProfile(_default_graph())

        p.g.add((URIRef('http://example.org/datasets/1'),
                 DCT.title, Literal('Test Datensatz 1', lang='de')))
        p.g.add((URIRef('http://example.org/datasets/1'),
                 DCT.title, Literal('Test Dataset 1 (EN)', lang='en')))

        value = p._object_value(URIRef('http://example.org/datasets/1'),
                                DCT.title)

        assert isinstance(value, str)
        assert value == 'Test Datensatz 1'

    @pytest.mark.ckan_config('ckan.locale_default', 'fr')
    def test_object_value_default_lang_not_in_graph(self):
        p = RDFProfile(_default_graph())

        p.g.add((URIRef('http://example.org/datasets/1'),
                 DCT.title, Literal('Test Datensatz 1', lang='de')))

        value = p._object_value(URIRef('http://example.org/datasets/1'),
                                DCT.title)

        assert isinstance(value, str)
        # FR is not in graph, so either node may be used
        assert value.startswith('Test D')
        assert value.endswith(' 1')

    def test_object_value_default_lang_fallback(self):
        p = RDFProfile(_default_graph())

        p.g.add((URIRef('http://example.org/datasets/1'),
                 DCT.title, Literal('Test Datensatz 1', lang='de')))
        p.g.add((URIRef('http://example.org/datasets/1'),
                 DCT.title, Literal('Test Dataset 1 (EN)', lang='en')))

        value = p._object_value(URIRef('http://example.org/datasets/1'),
                                DCT.title)

        assert isinstance(value, str)
        # without config parameter, EN is used as default
        assert value == 'Test Dataset 1 (EN)'

    def test_object_value_default_lang_missing_lang_param(self):
        p = RDFProfile(_default_graph())

        value = p._object_value(URIRef('http://example.org/datasets/1'),
                                DCT.title)

        assert isinstance(value, str)
        assert value == 'Test Dataset 1'

    def test_object_int(self):

        p = RDFProfile(_default_graph())

        p.g.add((URIRef('http://example.org/datasets/1'),
                 TEST.some_number,
                 Literal('23')))

        value = p._object_value_int(URIRef('http://example.org/datasets/1'),
                                    TEST.some_number)

        assert isinstance(value, int)
        assert value == 23

    def test_object_int_decimal(self):

        p = RDFProfile(_default_graph())

        p.g.add((URIRef('http://example.org/datasets/1'),
                 TEST.some_number,
                 Literal('23.0')))

        value = p._object_value_int(URIRef('http://example.org/datasets/1'),
                                    TEST.some_number)

        assert isinstance(value, int)
        assert value == 23

    def test_object_int_not_found(self):

        p = RDFProfile(_default_graph())

        value = p._object_value_int(URIRef('http://example.org/datasets/1'),
                                    TEST.some_number)

        assert value == None

    def test_object_int_wrong_value(self):

        p = RDFProfile(_default_graph())

        p.g.add((URIRef('http://example.org/datasets/1'),
                 TEST.some_number,
                 Literal('Not an intger')))

        value = p._object_value_int(URIRef('http://example.org/datasets/1'),
                                    TEST.some_number)

        assert value == None

    def test_object_list(self):

        p = RDFProfile(_default_graph())

        p.g.add((URIRef('http://example.org/datasets/1'),
                 DCAT.keyword,
                 Literal('space')))
        p.g.add((URIRef('http://example.org/datasets/1'),
                 DCAT.keyword,
                 Literal('moon')))

        value = p._object_value_list(URIRef('http://example.org/datasets/1'),
                                     DCAT.keyword)

        assert isinstance(value, list)
        assert isinstance(value[0], str)
        assert len(value) == 2
        assert sorted(value) == ['moon', 'space']

    def test_object_list_not_found(self):

        p = RDFProfile(_default_graph())

        value = p._object_value_list(URIRef('http://example.org/datasets/1'),
                                     TEST.some_list)

        assert isinstance(value, list)
        assert value == []

    def test_time_interval_schema_org(self):

        data = '''<?xml version="1.0" encoding="utf-8" ?>
        <rdf:RDF
         xmlns:dct="http://purl.org/dc/terms/"
         xmlns:schema="http://schema.org/"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
        <rdfs:SomeClass rdf:about="http://example.org">
            <dct:temporal>
                <dct:PeriodOfTime>
                    <schema:startDate rdf:datatype="http://www.w3.org/2001/XMLSchema#date">1905-03-01</schema:startDate>
                    <schema:endDate rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2013-01-05</schema:endDate>
                </dct:PeriodOfTime>
            </dct:temporal>
        </rdfs:SomeClass>
        </rdf:RDF>
        '''

        g = Graph()

        g.parse(format='xml', data=data)

        p = RDFProfile(g)

        start, end = p._time_interval(URIRef('http://example.org'), DCT.temporal)

        assert start == '1905-03-01'
        assert end == '2013-01-05'

    def test_time_interval_w3c_time_inXSDDateTime(self):

        data = '''<?xml version="1.0" encoding="utf-8" ?>
        <rdf:RDF
         xmlns:dct="http://purl.org/dc/terms/"
         xmlns:time="http://www.w3.org/2006/time"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
        <rdfs:SomeClass rdf:about="http://example.org">
          <dct:temporal>
            <dct:PeriodOfTime>
              <time:hasBeginning>
                <time:Instant>
                  <time:inXSDDateTime rdf:datatype="http://www.w3.org/2001/XMLSchema#date">1904</time:inXSDDateTime>
                </time:Instant>
              </time:hasBeginning>
              <time:hasEnd>
                <time:Instant>
                  <time:inXSDDateTime rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2014-03-22</time:inXSDDateTime>
                </time:Instant>
              </time:hasEnd>
            </dct:PeriodOfTime>
          </dct:temporal>
        </rdfs:SomeClass>
        </rdf:RDF>
        '''

        g = Graph()

        g.parse(format='xml', data=data)

        p = RDFProfile(g)

        start, end = p._time_interval(URIRef('http://example.org'), DCT.temporal)

        assert start == '1904-01-01'
        assert end == '2014-03-22'

    def test_time_interval_w3c_time_inXSDDateTimeStamp(self):

        data = '''<?xml version="1.0" encoding="utf-8" ?>
        <rdf:RDF
         xmlns:dct="http://purl.org/dc/terms/"
         xmlns:time="http://www.w3.org/2006/time"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
        <rdfs:SomeClass rdf:about="http://example.org">
          <dct:temporal>
            <dct:PeriodOfTime>
              <time:hasBeginning>
                <time:Instant>
                  <time:inXSDDateTimeStamp rdf:datatype="http://www.w3.org/2001/XMLSchema#date">1904</time:inXSDDateTimeStamp>
                </time:Instant>
              </time:hasBeginning>
              <time:hasEnd>
                <time:Instant>
                  <time:inXSDDateTimeStamp rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2014-03-22</time:inXSDDateTimeStamp>
                </time:Instant>
              </time:hasEnd>
            </dct:PeriodOfTime>
          </dct:temporal>
        </rdfs:SomeClass>
        </rdf:RDF>
        '''

        g = Graph()

        g.parse(format='xml', data=data)

        p = RDFProfile(g)

        start, end = p._time_interval(URIRef('http://example.org'), DCT.temporal)

        assert start == '1904-01-01'
        assert end == '2014-03-22'

    def test_time_interval_w3c_time_inXSDDate(self):

        data = '''<?xml version="1.0" encoding="utf-8" ?>
        <rdf:RDF
         xmlns:dct="http://purl.org/dc/terms/"
         xmlns:time="http://www.w3.org/2006/time"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
        <rdfs:SomeClass rdf:about="http://example.org">
          <dct:temporal>
            <dct:PeriodOfTime>
              <time:hasBeginning>
                <time:Instant>
                  <time:inXSDDate rdf:datatype="http://www.w3.org/2001/XMLSchema#date">1904</time:inXSDDate>
                </time:Instant>
              </time:hasBeginning>
              <time:hasEnd>
                <time:Instant>
                  <time:inXSDDate rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2014-03-22</time:inXSDDate>
                </time:Instant>
              </time:hasEnd>
            </dct:PeriodOfTime>
          </dct:temporal>
        </rdfs:SomeClass>
        </rdf:RDF>
        '''

        g = Graph()

        g.parse(format='xml', data=data)

        p = RDFProfile(g)

        start, end = p._time_interval(URIRef('http://example.org'), DCT.temporal)

        assert start == '1904-01-01'
        assert end == '2014-03-22'

    def test_time_interval_multiple_w3c_time(self):
        """
        Test priority for W3C Time. Order of priority: 1. XSDDateTimeStamp 2. XSDDateTime 3. XSDDate
        """

        data = '''<?xml version="1.0" encoding="utf-8" ?>
        <rdf:RDF
         xmlns:dct="http://purl.org/dc/terms/"
         xmlns:time="http://www.w3.org/2006/time"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
        <rdfs:SomeClass rdf:about="http://example.org">
          <dct:temporal>
            <dct:PeriodOfTime>
              <time:hasBeginning>
                <time:Instant>
                  <time:inXSDDateTime rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2005</time:inXSDDateTime>
                  <time:inXSDDateTimeStamp rdf:datatype="http://www.w3.org/2001/XMLSchema#date">1904</time:inXSDDateTimeStamp>
                  <time:inXSDDate rdf:datatype="http://www.w3.org/2001/XMLSchema#date">1974</time:inXSDDate>
                </time:Instant>
              </time:hasBeginning>
              <time:hasEnd>
                <time:Instant>
                  <time:inXSDDate rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2017-05-29</time:inXSDDate>
                  <time:inXSDDateTime rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2004-08-22</time:inXSDDateTime>
                  <time:inXSDDateTimeStamp rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2014-03-22</time:inXSDDateTimeStamp>
                </time:Instant>
              </time:hasEnd>
            </dct:PeriodOfTime>
          </dct:temporal>
        </rdfs:SomeClass>
        </rdf:RDF>
        '''

        g = Graph()

        g.parse(format='xml', data=data)

        p = RDFProfile(g)

        start, end = p._time_interval(URIRef('http://example.org'), DCT.temporal)

        assert start == '1904-01-01'
        assert end == '2014-03-22'

    def test_time_interval_dcat(self):

        data = '''<?xml version="1.0" encoding="utf-8" ?>
        <rdf:RDF
         xmlns:dct="http://purl.org/dc/terms/"
         xmlns:dcat="http://www.w3.org/ns/dcat#"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
        <rdfs:SomeClass rdf:about="http://example.org">
            <dct:temporal>
                <dct:PeriodOfTime>
                    <dcat:startDate rdf:datatype="http://www.w3.org/2001/XMLSchema#date">1905-03-01</dcat:startDate>
                    <dcat:endDate rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2013-01-05</dcat:endDate>
                </dct:PeriodOfTime>
            </dct:temporal>
        </rdfs:SomeClass>
        </rdf:RDF>
        '''

        g = Graph()

        g.parse(format='xml', data=data)

        p = RDFProfile(g)

        start, end = p._time_interval(URIRef('http://example.org'), DCT.temporal, dcat_ap_version=2)

        assert start == '1905-03-01'
        assert end == '2013-01-05'

    def test_time_interval_all_dcat_ap_2_dcat_found(self):
        """
        DCAT-AP 2

        Tests that DCAT dates have priority when W3C Time and schema.org are provided as well.
        """

        data = '''<?xml version="1.0" encoding="utf-8" ?>
        <rdf:RDF
         xmlns:dct="http://purl.org/dc/terms/"
         xmlns:dcat="http://www.w3.org/ns/dcat#"
         xmlns:schema="http://schema.org/"
         xmlns:time="http://www.w3.org/2006/time"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
        <rdfs:SomeClass rdf:about="http://example.org">
            <dct:temporal>
                <dct:PeriodOfTime>
                  <time:hasBeginning>
                    <time:Instant>
                      <time:inXSDDateTime rdf:datatype="http://www.w3.org/2001/XMLSchema#date">1904</time:inXSDDateTime>
                    </time:Instant>
                  </time:hasBeginning>
                  <time:hasEnd>
                    <time:Instant>
                      <time:inXSDDateTime rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2014-03-22</time:inXSDDateTime>
                    </time:Instant>
                  </time:hasEnd>
                </dct:PeriodOfTime>
            </dct:temporal>
            <dct:temporal>
                <dct:PeriodOfTime>
                    <dcat:startDate rdf:datatype="http://www.w3.org/2001/XMLSchema#date">1905-03-01</dcat:startDate>
                    <dcat:endDate rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2013-01-05</dcat:endDate>
                </dct:PeriodOfTime>
            </dct:temporal>
            <dct:temporal>
                <dct:PeriodOfTime>
                    <schema:startDate rdf:datatype="http://www.w3.org/2001/XMLSchema#date">1970-05-31</schema:startDate>
                    <schema:endDate rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2021-08-05</schema:endDate>
                </dct:PeriodOfTime>
            </dct:temporal>
        </rdfs:SomeClass>
        </rdf:RDF>
        '''

        g = Graph()

        g.parse(format='xml', data=data)

        p = RDFProfile(g)

        start, end = p._time_interval(URIRef('http://example.org'), DCT.temporal, dcat_ap_version=2)

        assert start == '1905-03-01'
        assert end == '2013-01-05'

    def test_time_interval_all_dcat_ap_1_schema_org_found(self):
        """
        DCAT-AP 1

        Tests that schema.org has priority when W3C Time is provided as well, and DCAT dates are ignored.
        """

        data = '''<?xml version="1.0" encoding="utf-8" ?>
        <rdf:RDF
         xmlns:dct="http://purl.org/dc/terms/"
         xmlns:dcat="http://www.w3.org/ns/dcat#"
         xmlns:schema="http://schema.org/"
         xmlns:time="http://www.w3.org/2006/time"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
        <rdfs:SomeClass rdf:about="http://example.org">
            <dct:temporal>
                <dct:PeriodOfTime>
                  <time:hasBeginning>
                    <time:Instant>
                      <time:inXSDDateTime rdf:datatype="http://www.w3.org/2001/XMLSchema#date">1904</time:inXSDDateTime>
                    </time:Instant>
                  </time:hasBeginning>
                  <time:hasEnd>
                    <time:Instant>
                      <time:inXSDDateTime rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2014-03-22</time:inXSDDateTime>
                    </time:Instant>
                  </time:hasEnd>
                </dct:PeriodOfTime>
            </dct:temporal>
            <dct:temporal>
                <dct:PeriodOfTime>
                    <dcat:startDate rdf:datatype="http://www.w3.org/2001/XMLSchema#date">1905-03-01</dcat:startDate>
                    <dcat:endDate rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2013-01-05</dcat:endDate>
                </dct:PeriodOfTime>
            </dct:temporal>
            <dct:temporal>
                <dct:PeriodOfTime>
                    <schema:startDate rdf:datatype="http://www.w3.org/2001/XMLSchema#date">1970-05-31</schema:startDate>
                    <schema:endDate rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2021-08-05</schema:endDate>
                </dct:PeriodOfTime>
            </dct:temporal>
        </rdfs:SomeClass>
        </rdf:RDF>
        '''

        g = Graph()

        g.parse(format='xml', data=data)

        p = RDFProfile(g)

        start, end = p._time_interval(URIRef('http://example.org'), DCT.temporal)

        assert start == '1970-05-31'
        assert end == '2021-08-05'

    def test_time_interval_all_dcat_ap_2_w3c_time_found(self):
        """
        DCAT-AP 2

        Tests that W3C Time has priority when schema.org is provided as well
        and DCAT dates are not available.
        """

        data = '''<?xml version="1.0" encoding="utf-8" ?>
        <rdf:RDF
         xmlns:dct="http://purl.org/dc/terms/"
         xmlns:dcat="http://www.w3.org/ns/dcat#"
         xmlns:schema="http://schema.org/"
         xmlns:time="http://www.w3.org/2006/time"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
        <rdfs:SomeClass rdf:about="http://example.org">
            <dct:temporal>
                <dct:PeriodOfTime>
                    <schema:startDate rdf:datatype="http://www.w3.org/2001/XMLSchema#date">1970-05-31</schema:startDate>
                    <schema:endDate rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2021-08-05</schema:endDate>
                </dct:PeriodOfTime>
            </dct:temporal>
            <dct:temporal>
                <dct:PeriodOfTime>
                    <time:hasBeginning>
                        <time:Instant>
                        <time:inXSDDateTime rdf:datatype="http://www.w3.org/2001/XMLSchema#date">1904</time:inXSDDateTime>
                        </time:Instant>
                    </time:hasBeginning>
                    <time:hasEnd>
                        <time:Instant>
                        <time:inXSDDateTime rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2014-03-22</time:inXSDDateTime>
                        </time:Instant>
                    </time:hasEnd>
                </dct:PeriodOfTime>
            </dct:temporal>
        </rdfs:SomeClass>
        </rdf:RDF>
        '''

        g = Graph()

        g.parse(format='xml', data=data)

        p = RDFProfile(g)

        start, end = p._time_interval(URIRef('http://example.org'), DCT.temporal, dcat_ap_version=2)

        assert start == '1904-01-01'
        assert end == '2014-03-22'

    def test_publisher_foaf(self):

        data = '''<?xml version="1.0" encoding="utf-8" ?>
        <rdf:RDF
         xmlns:dct="http://purl.org/dc/terms/"
         xmlns:foaf="http://xmlns.com/foaf/0.1/"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
        <rdfs:SomeClass rdf:about="http://example.org">
          <dct:publisher>
            <foaf:Organization rdf:about="http://orgs.vocab.org/some-org">
              <foaf:name>Publishing Organization for dataset 1</foaf:name>
              <foaf:mbox>contact@some.org</foaf:mbox>
              <foaf:homepage>http://some.org</foaf:homepage>
              <dct:type rdf:resource="http://purl.org/adms/publishertype/NonProfitOrganisation"/>
            </foaf:Organization>
          </dct:publisher>
        </rdfs:SomeClass>
        </rdf:RDF>
        '''

        g = Graph()

        g.parse(format='xml', data=data)

        p = RDFProfile(g)

        publisher = p._publisher(URIRef('http://example.org'), DCT.publisher)

        assert publisher['uri'] == 'http://orgs.vocab.org/some-org'
        assert publisher['name'] == 'Publishing Organization for dataset 1'
        assert publisher['email'] == 'contact@some.org'
        assert publisher['url'] == 'http://some.org'
        assert publisher['type'] == 'http://purl.org/adms/publishertype/NonProfitOrganisation'

    def test_publisher_ref(self):

        data = '''<?xml version="1.0" encoding="utf-8" ?>
        <rdf:RDF
         xmlns:dct="http://purl.org/dc/terms/"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
        <rdfs:SomeClass rdf:about="http://example.org">
          <dct:publisher rdf:resource="http://orgs.vocab.org/some-org" />
        </rdfs:SomeClass>
        </rdf:RDF>
        '''

        g = Graph()

        g.parse(format='xml', data=data)

        p = RDFProfile(g)

        publisher = p._publisher(URIRef('http://example.org'), DCT.publisher)

        assert publisher['uri'] == 'http://orgs.vocab.org/some-org'

    def test_contact_details(self):

        data = '''<?xml version="1.0" encoding="utf-8" ?>
        <rdf:RDF
         xmlns:dct="http://purl.org/dc/terms/"
         xmlns:vcard="http://www.w3.org/2006/vcard/ns#"
         xmlns:adms="http://www.w3.org/ns/adms#"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
        <rdfs:SomeClass rdf:about="http://example.org">
          <adms:contactPoint>
            <vcard:Organization>
              <vcard:fn>Point of Contact</vcard:fn>
              <vcard:hasEmail rdf:resource="mailto:contact@some.org"/>
            </vcard:Organization>
          </adms:contactPoint>
        </rdfs:SomeClass>
        </rdf:RDF>
        '''

        g = Graph()

        g.parse(format='xml', data=data)

        p = RDFProfile(g)

        contact = p._contact_details(URIRef('http://example.org'), ADMS.contactPoint)

        assert contact['name'] == 'Point of Contact'
        # mailto gets removed for storage and is added again on output
        assert contact['email'] == 'contact@some.org'
