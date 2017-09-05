import nose

from rdflib import Graph, URIRef, Literal
from rdflib.namespace import Namespace

from ckanext.dcat.profiles import RDFProfile

from ckanext.dcat.tests.test_base_parser import _default_graph


eq_ = nose.tools.eq_

DCT = Namespace("http://purl.org/dc/terms/")
TEST = Namespace("http://test.org/")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
ADMS = Namespace("http://www.w3.org/ns/adms#")


class TestBaseRDFProfile(object):

    def test_datasets(self):

        p = RDFProfile(_default_graph())

        eq_(len([d for d in p._datasets()]), 3)

    def test_datasets_none_found(self):

        p = RDFProfile(Graph())

        eq_(len([d for d in p._datasets()]), 0)

    def test_distributions(self):

        p = RDFProfile(_default_graph())

        for dataset in p._datasets():
            if str(dataset) == 'http://example.org/datasets/1':
                eq_(len([d for d in p._distributions(dataset)]), 2)
            elif str(dataset) == 'http://example.org/datasets/2':
                eq_(len([d for d in p._distributions(dataset)]), 1)
            elif str(dataset) == 'http://example.org/datasets/3':
                eq_(len([d for d in p._distributions(dataset)]), 0)

    def test_object(self):

        p = RDFProfile(_default_graph())

        _object = p._object(URIRef('http://example.org/datasets/1'),
                            DCT.title)

        assert isinstance(_object, Literal)
        eq_(str(_object), 'Test Dataset 1')

    def test_object_not_found(self):

        p = RDFProfile(_default_graph())

        _object = p._object(URIRef('http://example.org/datasets/1'),
                            DCT.unknown_property)

        eq_(_object, None)

    def test_object_value(self):

        p = RDFProfile(_default_graph())

        value = p._object_value(URIRef('http://example.org/datasets/1'),
                                DCT.title)

        assert isinstance(value, unicode)
        eq_(value, 'Test Dataset 1')

    def test_object_value_not_found(self):

        p = RDFProfile(_default_graph())

        value = p._object_value(URIRef('http://example.org/datasets/1'),
                                DCT.unknown_property)

        eq_(value, '')

    def test_object_int(self):

        p = RDFProfile(_default_graph())

        p.g.add((URIRef('http://example.org/datasets/1'),
                 TEST.some_number,
                 Literal('23')))

        value = p._object_value_int(URIRef('http://example.org/datasets/1'),
                                    TEST.some_number)

        assert isinstance(value, int)
        eq_(value, 23)

    def test_object_int_not_found(self):

        p = RDFProfile(_default_graph())

        value = p._object_value_int(URIRef('http://example.org/datasets/1'),
                                    TEST.some_number)

        eq_(value, None)

    def test_object_int_wrong_value(self):

        p = RDFProfile(_default_graph())

        p.g.add((URIRef('http://example.org/datasets/1'),
                 TEST.some_number,
                 Literal('Not an intger')))

        value = p._object_value_int(URIRef('http://example.org/datasets/1'),
                                    TEST.some_number)

        eq_(value, None)

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
        assert isinstance(value[0], unicode)
        eq_(len(value), 2)
        eq_(sorted(value), ['moon', 'space'])

    def test_object_list_not_found(self):

        p = RDFProfile(_default_graph())

        value = p._object_value_list(URIRef('http://example.org/datasets/1'),
                                     TEST.some_list)

        assert isinstance(value, list)
        eq_(value, [])

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

        g.parse(data=data)

        p = RDFProfile(g)

        start, end = p._time_interval(URIRef('http://example.org'), DCT.temporal)

        eq_(start, '1905-03-01')
        eq_(end, '2013-01-05')

    def test_time_interval_w3c_time(self):

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

        g.parse(data=data)

        p = RDFProfile(g)

        start, end = p._time_interval(URIRef('http://example.org'), DCT.temporal)

        eq_(start, '1904-01-01')
        eq_(end, '2014-03-22')

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

        g.parse(data=data)

        p = RDFProfile(g)

        publisher = p._publisher(URIRef('http://example.org'), DCT.publisher)

        eq_(publisher['uri'], 'http://orgs.vocab.org/some-org')
        eq_(publisher['name'], 'Publishing Organization for dataset 1')
        eq_(publisher['email'], 'contact@some.org')
        eq_(publisher['url'], 'http://some.org')
        eq_(publisher['type'], 'http://purl.org/adms/publishertype/NonProfitOrganisation')

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

        g.parse(data=data)

        p = RDFProfile(g)

        publisher = p._publisher(URIRef('http://example.org'), DCT.publisher)

        eq_(publisher['uri'], 'http://orgs.vocab.org/some-org')

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

        g.parse(data=data)

        p = RDFProfile(g)

        contact = p._contact_details(URIRef('http://example.org'), ADMS.contactPoint)

        eq_(contact['name'], 'Point of Contact')
        eq_(contact['email'], 'mailto:contact@some.org')
