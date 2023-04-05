from builtins import str

from ckantoolkit import config

from rdflib import URIRef, Literal
from rdflib.namespace import Namespace, RDF

from ckanext.dcat.processors import (
    RDFSerializer,
    RDFProfileException,
    DEFAULT_RDF_PROFILES,
    RDF_PROFILES_CONFIG_OPTION
)

from ckanext.dcat.profiles import RDFProfile
from ckanext.dcat.tests.utils import BaseSerializeTest

DCT = Namespace("http://purl.org/dc/terms/")
DCAT = Namespace("http://www.w3.org/ns/dcat#")


def _default_dict():

    dataset = {
        'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
        'name': 'test-dataset',
        'title': 'Test DCAT dataset',
        'notes': 'Lorem ipsum',
        'url': 'http://example.com/ds1',
        'tags': [{'name': 'Tag 1'}, {'name': 'Tag 2'}],
        'resources': [
            {
                'id': 'c041c635-054f-4431-b647-f9186926d021',
                'package_id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
                'name': 'CSV file'
            }
        ]
    }

    return dataset


class MockRDFProfile1(RDFProfile):

    def graph_from_dataset(self, dataset_dict, dataset_ref):

        self.g.add((dataset_ref, DCAT.keyword, Literal('profile_1')))


class MockRDFProfile2(RDFProfile):

    def graph_from_dataset(self, dataset_dict, dataset_ref):

        self.g.add((dataset_ref, DCAT.keyword, Literal('profile_2')))


class TestRDFSerializer(BaseSerializeTest):

    def test_default_profile(self):

        s = RDFSerializer()

        assert (sorted([pr.name for pr in s._profiles]) ==
            sorted(DEFAULT_RDF_PROFILES))

    def test_profiles_via_config_option(self):

        original_config = config.copy()

        config[RDF_PROFILES_CONFIG_OPTION] = 'profile_conf_1 profile_conf_2'
        try:
            RDFSerializer()
        except RDFProfileException as e:

            assert str(e) == 'Unknown RDF profiles: profile_conf_1, profile_conf_2'

        config.clear()
        config.update(original_config)

    def test_no_profile_provided(self):
        try:
            RDFSerializer(profiles=[])
        except RDFProfileException as e:

            assert str(e) == 'No suitable RDF profiles could be loaded'

    def test_profile_not_found(self):
        try:
            RDFSerializer(profiles=['not_found'])
        except RDFProfileException as e:

            assert str(e) == 'Unknown RDF profiles: not_found'

    def test_profiles_are_called_on_datasets(self):

        s = RDFSerializer()

        s._profiles = [MockRDFProfile1, MockRDFProfile2]

        dataset_rdf_string = s.serialize_dataset(_default_dict())

        assert dataset_rdf_string

        assert self._triples(s.g, None, DCAT.keyword, Literal('profile_1'))
        assert self._triples(s.g, None, DCAT.keyword, Literal('profile_2'))

    def test_serialize_dataset(self):

        s = RDFSerializer()

        dataset_rdf_string = s.serialize_dataset(_default_dict())

        assert dataset_rdf_string
        assert '<dct:title>Test DCAT dataset</dct:title>' in str(dataset_rdf_string)
        assert '<dcat:Distribution' in str(dataset_rdf_string)

        assert self._triples(s.g, None, DCT.description, Literal('Lorem ipsum'))
        assert len(self._triples(s.g, None, DCAT.distribution, None)) == 1
