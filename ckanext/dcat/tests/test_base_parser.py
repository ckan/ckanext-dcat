import nose

from ckantoolkit import config

from rdflib import Graph, URIRef, Literal
from rdflib.namespace import Namespace, RDF

from ckanext.dcat.processors import (
    RDFParser,
    RDFParserException,
    RDFProfileException,
    DEFAULT_RDF_PROFILES,
    RDF_PROFILES_CONFIG_OPTION
)

from ckanext.dcat.profiles import RDFProfile

DCT = Namespace("http://purl.org/dc/terms/")
DCAT = Namespace("http://www.w3.org/ns/dcat#")

eq_ = nose.tools.eq_


def _default_graph():

    g = Graph()

    dataset1 = URIRef("http://example.org/datasets/1")
    g.add((dataset1, RDF.type, DCAT.Dataset))
    g.add((dataset1, DCT.title, Literal('Test Dataset 1')))

    distribution1_1 = URIRef("http://example.org/datasets/1/ds/1")
    g.add((distribution1_1, RDF.type, DCAT.Distribution))
    distribution1_2 = URIRef("http://example.org/datasets/1/ds/2")
    g.add((distribution1_2, RDF.type, DCAT.Distribution))

    g.add((dataset1, DCAT.distribution, distribution1_1))
    g.add((dataset1, DCAT.distribution, distribution1_2))

    dataset2 = URIRef("http://example.org/datasets/2")
    g.add((dataset2, RDF.type, DCAT.Dataset))
    g.add((dataset2, DCT.title, Literal('Test Dataset 2')))

    distribution2_1 = URIRef("http://example.org/datasets/2/ds/1")
    g.add((distribution2_1, RDF.type, DCAT.Distribution))
    g.add((dataset2, DCAT.distribution, distribution2_1))

    dataset3 = URIRef("http://example.org/datasets/3")
    g.add((dataset3, RDF.type, DCAT.Dataset))
    g.add((dataset3, DCT.title, Literal('Test Dataset 3')))

    return g


class MockRDFProfile1(RDFProfile):

    def parse_dataset(self, dataset_dict, dataset_ref):

        dataset_dict['profile_1'] = True

        return dataset_dict


class MockRDFProfile2(RDFProfile):

    def parse_dataset(self, dataset_dict, dataset_ref):

        dataset_dict['profile_2'] = True

        return dataset_dict


class TestRDFParser(object):

    def test_default_profile(self):

        p = RDFParser()

        eq_(sorted([pr.name for pr in p._profiles]),
            sorted(DEFAULT_RDF_PROFILES))

    def test_profiles_via_config_option(self):

        original_config = config.copy()

        config[RDF_PROFILES_CONFIG_OPTION] = 'profile_conf_1 profile_conf_2'
        try:
            RDFParser()
        except RDFProfileException as e:

            eq_(str(e), 'Unknown RDF profiles: profile_conf_1, profile_conf_2')

        config.clear()
        config.update(original_config)

    def test_no_profile_provided(self):
        try:
            RDFParser(profiles=[])
        except RDFProfileException as e:

            eq_(str(e), 'No suitable RDF profiles could be loaded')

    def test_profile_not_found(self):
        try:
            RDFParser(profiles=['not_found'])
        except RDFProfileException as e:

            eq_(str(e), 'Unknown RDF profiles: not_found')

    def test_profiles_are_called_on_datasets(self):

        p = RDFParser()

        p._profiles = [MockRDFProfile1, MockRDFProfile2]

        p.g = _default_graph()

        for dataset in p.datasets():
            assert dataset['profile_1']
            assert dataset['profile_2']

    def test_parse_data(self):

        data = '''<?xml version="1.0" encoding="utf-8" ?>
        <rdf:RDF
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
        <rdfs:SomeClass rdf:about="http://example.org">
            <rdfs:label>Some label</rdfs:label>
        </rdfs:SomeClass>
        </rdf:RDF>
        '''

        p = RDFParser()

        eq_(len(p.g), 0)

        p.parse(data)

        eq_(len(p.g), 2)

    def test_parse_pagination_next_page(self):

        data = '''<?xml version="1.0" encoding="utf-8" ?>
        <rdf:RDF
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
         xmlns:hydra="http://www.w3.org/ns/hydra/core#">
         <hydra:PagedCollection rdf:about="http://example.com/catalog.xml?page=1">
            <hydra:totalItems rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">245</hydra:totalItems>
            <hydra:lastPage>http://example.com/catalog.xml?page=3</hydra:lastPage>
            <hydra:itemsPerPage rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">100</hydra:itemsPerPage>
            <hydra:nextPage>http://example.com/catalog.xml?page=2</hydra:nextPage>
            <hydra:firstPage>http://example.com/catalog.xml?page=1</hydra:firstPage>
        </hydra:PagedCollection>
        </rdf:RDF>
        '''

        p = RDFParser()

        p.parse(data)

        eq_(p.next_page(), 'http://example.com/catalog.xml?page=2')

    def test_parse_without_pagination(self):

        data = '''<?xml version="1.0" encoding="utf-8" ?>
        <rdf:RDF
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
        <rdfs:SomeClass rdf:about="http://example.org">
            <rdfs:label>Some label</rdfs:label>
        </rdfs:SomeClass>
        </rdf:RDF>
        '''

        p = RDFParser()

        p.parse(data)

        eq_(p.next_page(), None)

    def test_parse_pagination_last_page(self):

        data = '''<?xml version="1.0" encoding="utf-8" ?>
        <rdf:RDF
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
         xmlns:hydra="http://www.w3.org/ns/hydra/core#">
         <hydra:PagedCollection rdf:about="http://example.com/catalog.xml?page=3">
            <hydra:totalItems rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">245</hydra:totalItems>
            <hydra:lastPage>http://example.com/catalog.xml?page=3</hydra:lastPage>
            <hydra:itemsPerPage rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">100</hydra:itemsPerPage>
            <hydra:firstPage>http://example.com/catalog.xml?page=1</hydra:firstPage>
            <hydra:previousPage>http://example.com/catalog.xml?page=2</hydra:previousPage>
        </hydra:PagedCollection>
        </rdf:RDF>
        '''

        p = RDFParser()

        p.parse(data)

        eq_(p.next_page(), None)

    def test_parse_data_different_format(self):

        data = '''
        @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

        <http://example.org> a rdfs:SomeClass ;
            rdfs:label "Some label" .
        '''

        p = RDFParser()

        eq_(len(p.g), 0)

        p.parse(data, _format='n3')

        eq_(len(p.g), 2)

    def test_parse_data_raises_on_parse_error(self):

        p = RDFParser()

        data = 'Wrong data'

        nose.tools.assert_raises(RDFParserException, p.parse, '')

        nose.tools.assert_raises(RDFParserException, p.parse, data)

        nose.tools.assert_raises(RDFParserException, p.parse, data,
                                 _format='n3',)

    def test__datasets(self):

        p = RDFParser()

        p.g = _default_graph()

        eq_(len([d for d in p._datasets()]), 3)

    def test__datasets_none_found(self):

        p = RDFParser()

        p.g = Graph()

        eq_(len([d for d in p._datasets()]), 0)

    def test_datasets(self):

        p = RDFParser()

        p.g = _default_graph()

        datasets = []
        for dataset in p.datasets():

            assert 'title' in dataset

            datasets.append(dataset)

        eq_(len(datasets), 3)

    def test_datasets_none_found(self):

        p = RDFParser()

        p.g = Graph()

        eq_(len([d for d in p.datasets()]), 0)
