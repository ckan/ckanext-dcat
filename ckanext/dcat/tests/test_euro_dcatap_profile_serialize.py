from builtins import str
from builtins import object
import json

import pytest

from ckantoolkit import config

from dateutil.parser import parse as parse_date
from rdflib import URIRef, BNode, Literal
from rdflib.namespace import RDF

from geomet import wkt

from ckantoolkit.tests import helpers, factories

from ckanext.dcat import utils
from ckanext.dcat.processors import RDFSerializer, HYDRA
from ckanext.dcat.profiles import (
    DCAT, DCT, ADMS, XSD, VCARD, FOAF, SCHEMA,
    SKOS, LOCN, GSP, OWL, SPDX, GEOJSON_IMT,
)
from ckanext.dcat.profiles.euro_dcat_ap import DISTRIBUTION_LICENSE_FALLBACK_CONFIG
from ckanext.dcat.utils import DCAT_EXPOSE_SUBCATALOGS
from ckanext.dcat.tests.utils import BaseSerializeTest


class TestEuroDCATAPProfileSerializeDataset(BaseSerializeTest):
    def _build_graph_and_check_format_mediatype(self, dataset_dict, expected_format, expected_mediatype):
        """
        Creates a graph based on the given dict and checks for dct:format and dct:mediaType in the
        first resource element.

        :param dataset_dict:
            dataset dict, expected to contain one resource
        :param expected_format:
            expected list of dct:format items in the resource
        :param expected_mediatype:
            expected list of dcat:mediaType items in the resource
        """
        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset_dict)

        # graph should contain the expected nodes
        resource_ref = list(g.objects(dataset_ref, DCAT.distribution))[0]
        dct_format = list(g.objects(resource_ref, DCT['format']))
        dcat_mediatype = list(g.objects(resource_ref, DCAT.mediaType))
        assert expected_format == dct_format
        assert expected_mediatype == dcat_mediatype

    def _get_base_dataset_with_resource(self):
        """
        Creates a minimal test dataset with one resource. The dataset and resource are
        both returned and can be extended in test cases.
        """
        resource = {
            'id': 'c041c635-054f-4431-b647-f9186926d021',
            'package_id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'CSV file',
        }

        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'title': 'Test DCAT dataset',
            'resources': [
                resource
            ]
        }

        return dataset, resource

    def test_graph_from_dataset(self):

        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'title': 'Test DCAT dataset',
            'notes': 'Lorem ipsum',
            'url': 'http://example.com/ds1',
            'version': '1.0b',
            'metadata_created': '2015-06-26T15:21:09.034694',
            'metadata_modified': '2015-06-26T15:21:09.075774',
            'tags': [{'name': 'Tag 1'}, {'name': 'Tag 2'}],
            'extras': [
                {'key': 'alternate_identifier', 'value': '[\"xyz\", \"abc\", \"https://data.some.org/catalog/datasets/a-id-1\"]'},
                {'key': 'version_notes', 'value': 'This is a beta version'},
                {'key': 'frequency', 'value': 'monthly'},
                {'key': 'language', 'value': '[\"en\", \"http://publications.europa.eu/resource/authority/language/ITA\"]'},
                {'key': 'theme', 'value': '[\"http://eurovoc.europa.eu/100142\", \"http://eurovoc.europa.eu/100152\"]'},
                {'key': 'conforms_to', 'value': '[\"Standard 1\", \"Standard 2\"]'},
                {'key': 'access_rights', 'value': 'public'},
                {'key': 'documentation', 'value': '[\"http://dataset.info.org/doc1\", \"http://dataset.info.org/doc2\"]'},
                {'key': 'provenance', 'value': 'Some statement about provenance'},
                {'key': 'dcat_type', 'value': 'test-type'},
                {'key': 'related_resource', 'value': '[\"http://dataset.info.org/related1\", \"http://dataset.info.org/related2\"]'},
                {'key': 'has_version', 'value': '[\"https://data.some.org/catalog/datasets/derived-dataset-1\", \"https://data.some.org/catalog/datasets/derived-dataset-2\"]'},
                {'key': 'is_version_of', 'value': '[\"https://data.some.org/catalog/datasets/original-dataset\"]'},
                {'key': 'source', 'value': '[\"https://data.some.org/catalog/datasets/source-dataset-1\", \"https://data.some.org/catalog/datasets/source-dataset-2\", \"test_source\"]'},
                {'key': 'sample', 'value': '[\"https://data.some.org/catalog/datasets/9df8df51-63db-37a8-e044-0003ba9b0d98/sample\", \"test_sample\"]'},
            ]
        }
        extras = self._extras(dataset)

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        assert str(dataset_ref) == utils.dataset_uri(dataset)

        # Basic fields
        assert self._triple(g, dataset_ref, RDF.type, DCAT.Dataset)
        assert self._triple(g, dataset_ref, DCT.title, dataset['title'])
        assert self._triple(g, dataset_ref, DCT.description, dataset['notes'])

        assert self._triple(g, dataset_ref, OWL.versionInfo, dataset['version'])
        assert self._triple(g, dataset_ref, ADMS.versionNotes, extras['version_notes'])
        assert self._triple(g, dataset_ref, DCT.accrualPeriodicity, extras['frequency'])
        assert self._triple(g, dataset_ref, DCT.accessRights, extras['access_rights'])
        assert self._triple(g, dataset_ref, DCT.provenance, extras['provenance'])
        assert self._triple(g, dataset_ref, DCT.type, extras['dcat_type'])

        # Tags
        assert len([t for t in g.triples((dataset_ref, DCAT.keyword, None))]) == 2
        for tag in dataset['tags']:
            assert self._triple(g, dataset_ref, DCAT.keyword, tag['name'])

        # Dates
        assert self._triple(g, dataset_ref, DCT.issued, dataset['metadata_created'], XSD.dateTime)
        assert self._triple(g, dataset_ref, DCT.modified, dataset['metadata_modified'], XSD.dateTime)

        # List
        for item in [
            ('language', DCT.language, [Literal, URIRef]),
            ('theme', DCAT.theme, URIRef),
            ('conforms_to', DCT.conformsTo, Literal),
            ('alternate_identifier', ADMS.identifier, [Literal, Literal, URIRef]),
            ('documentation', FOAF.page, URIRef),
            ('related_resource', DCT.relation, URIRef),
            ('has_version', DCT.hasVersion, URIRef),
            ('is_version_of', DCT.isVersionOf, URIRef),
            ('source', DCT.source, [URIRef, URIRef, Literal]),
            ('sample', ADMS.sample, [URIRef, Literal]),
        ]:
            values = json.loads(extras[item[0]])
            assert len([t for t in g.triples((dataset_ref, item[1], None))]) == len(values)
            for num, value in enumerate(values):
                _type = item[2]
                if isinstance(item[2], list):
                    assert len(item[2]) == len(values)
                    _type = item[2][num]
                assert self._triple(g, dataset_ref, item[1], _type(value))

    def test_identifier_extra(self):
        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'extras': [
                {'key': 'identifier', 'value': 'idxxx'},
                {'key': 'guid', 'value': 'guidyyy'},
            ]
        }
        extras = self._extras(dataset)

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        assert self._triple(g, dataset_ref, DCT.identifier, extras['identifier'])

    def test_identifier_extra_uri(self):
        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'extras': [
                {'key': 'identifier', 'value': 'https://data.some.org/catalog/datasets/idxxx'},
                {'key': 'guid', 'value': 'guidyyy'},
            ]
        }
        extras = self._extras(dataset)

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        assert self._triple(g, dataset_ref, DCT.identifier, URIRef(extras['identifier']))

    def test_identifier_guid(self):
        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'extras': [
                {'key': 'guid', 'value': 'guidyyy'},
            ]
        }
        extras = self._extras(dataset)

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        assert self._triple(g, dataset_ref, DCT.identifier, extras['guid'])

    def test_identifier_id(self):
        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
        }

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        assert self._triple(g, dataset_ref, DCT.identifier, dataset['id'])

    def test_alternate_identifier_numeric(self):
        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'extras': [
                {'key': 'alternate_identifier', 'value': '1.0'},
            ]
        }

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        assert self._triple(g, dataset_ref, DCT.identifier, dataset['id'])

    def test_alternate_identifier_uri(self):
        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'extras': [
                {'key': 'alternate_identifier', 'value': 'https://data.some.org/catalog/datasets/alt-id'},
            ]
        }

        extras = self._extras(dataset)

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        assert self._triple(g, dataset_ref, ADMS.identifier, URIRef(extras['alternate_identifier']))

    def test_access_rights_uri(self):
        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'extras': [
                {'key': 'access_rights', 'value': 'https://data.some.org/catalog/datasets/public'}
            ]
        }
        extras = self._extras(dataset)

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        assert self._triple(g, dataset_ref, DCT.accessRights, URIRef(extras['access_rights']))

    def test_contact_details_extras(self):
        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'maintainer': 'Example Maintainer',
            'maintainer_email': 'dep@example.com',
            'author': 'Example Author',
            'author_email': 'ped@example.com',
            'extras': [
                {'key': 'contact_uri', 'value': 'http://example.com/contact'},
                {'key': 'contact_name', 'value': 'Example Contact'},
                {'key': 'contact_email', 'value': 'contact@example.com'},

            ]


        }
        extras = self._extras(dataset)

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        # Contact details

        contact_details = self._triple(g, dataset_ref, DCAT.contactPoint, None)[2]
        assert contact_details
        assert str(contact_details) == extras['contact_uri']
        assert self._triple(g, contact_details, VCARD.fn, extras['contact_name'])
        assert self._triple(g, contact_details, VCARD.hasEmail, URIRef('mailto:' + extras['contact_email']))

    def test_contact_details_maintainer(self):
        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'maintainer': 'Example Maintainer',
            'maintainer_email': 'dep@example.com',
            'author': 'Example Author',
            'author_email': 'ped@example.com',
        }

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        contact_details = self._triple(g, dataset_ref, DCAT.contactPoint, None)[2]
        assert contact_details
        assert isinstance(contact_details, BNode)
        assert self._triple(g, contact_details, VCARD.fn, dataset['maintainer'])
        assert self._triple(g, contact_details, VCARD.hasEmail, URIRef('mailto:' + dataset['maintainer_email']))

    def test_contact_details_author(self):
        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'author': 'Example Author',
            'author_email': 'ped@example.com',
        }

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        contact_details = self._triple(g, dataset_ref, DCAT.contactPoint, None)[2]
        assert contact_details
        assert isinstance(contact_details, BNode)
        assert self._triple(g, contact_details, VCARD.fn, dataset['author'])
        assert self._triple(g, contact_details, VCARD.hasEmail, URIRef('mailto:' + dataset['author_email']))

    def test_contact_details_no_duplicate_mailto(self):
        # tests that mailto: isn't added again if it is stored in the dataset
        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'author': 'Example Author',
            'author_email': 'mailto:ped@example.com',
        }

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        contact_details = self._triple(g, dataset_ref, DCAT.contactPoint, None)[2]
        assert contact_details
        assert isinstance(contact_details, BNode)
        assert self._triple(g, contact_details, VCARD.fn, dataset['author'])
        assert self._triple(g, contact_details, VCARD.hasEmail, URIRef(dataset['author_email']))

    def test_publisher_extras(self):
        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'organization': {
                'id': '',
                'name': 'publisher1',
                'title': 'Example Publisher from Org',
            },
            'extras': [
                {'key': 'publisher_uri', 'value': 'http://example.com/publisher'},
                {'key': 'publisher_name', 'value': 'Example Publisher'},
                {'key': 'publisher_email', 'value': 'publisher@example.com'},
                {'key': 'publisher_url', 'value': 'http://example.com/publisher/home'},
                {'key': 'publisher_type', 'value': 'http://purl.org/adms/publishertype/Company'},
            ]


        }
        extras = self._extras(dataset)

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        publisher = self._triple(g, dataset_ref, DCT.publisher, None)[2]
        assert publisher
        assert str(publisher) == extras['publisher_uri']

        assert self._triple(g, publisher, RDF.type, FOAF.Organization)
        assert self._triple(g, publisher, FOAF.name, extras['publisher_name'])
        assert self._triple(g, publisher, FOAF.mbox, extras['publisher_email'])
        assert self._triple(g, publisher, FOAF.homepage, URIRef(extras['publisher_url']))
        assert self._triple(g, publisher, DCT.type, URIRef(extras['publisher_type']))

    def test_publisher_org(self):
        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'organization': {
                'id': '',
                'name': 'publisher1',
                'title': 'Example Publisher from Org',
            }
        }

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        publisher = self._triple(g, dataset_ref, DCT.publisher, None)[2]
        assert publisher

        assert self._triple(g, publisher, RDF.type, FOAF.Organization)
        assert self._triple(g, publisher, FOAF.name, dataset['organization']['title'])

    def test_publisher_no_uri(self):
        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'extras': [
                {'key': 'publisher_name', 'value': 'Example Publisher'},
            ]
        }
        extras = self._extras(dataset)

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        publisher = self._triple(g, dataset_ref, DCT.publisher, None)[2]
        assert publisher
        assert isinstance(publisher, BNode)

        assert self._triple(g, publisher, RDF.type, FOAF.Organization)
        assert self._triple(g, publisher, FOAF.name, extras['publisher_name'])

    def test_publisher_org_no_uri(self):
        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'organization': {
                'id': '',
                'name': 'publisher1',
                'title': 'Example Publisher from Org',
            },
            'extras': [
                {'key': 'publisher_name', 'value': 'Example Publisher'},
                {'key': 'publisher_email', 'value': 'publisher@example.com'},
                {'key': 'publisher_url', 'value': 'http://example.com/publisher/home'},
                {'key': 'publisher_type', 'value': 'http://purl.org/adms/publishertype/Company'},
            ]
        }
        extras = self._extras(dataset)

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        publisher = self._triple(g, dataset_ref, DCT.publisher, None)[2]
        assert publisher
        assert isinstance(publisher, BNode)

        assert self._triple(g, publisher, RDF.type, FOAF.Organization)
        assert self._triple(g, publisher, FOAF.name, extras['publisher_name'])
        assert self._triple(g, publisher, FOAF.mbox, extras['publisher_email'])
        assert self._triple(g, publisher, FOAF.homepage, URIRef(extras['publisher_url']))
        assert self._triple(g, publisher, DCT.type, URIRef(extras['publisher_type']))

    def test_temporal(self):
        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'extras': [
                {'key': 'temporal_start', 'value': '2015-06-26T15:21:09.075774'},
                {'key': 'temporal_end', 'value': '2015-07-14'},
            ]
        }
        extras = self._extras(dataset)

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        temporal = self._triple(g, dataset_ref, DCT.temporal, None)[2]
        assert temporal

        assert self._triple(g, temporal, RDF.type, DCT.PeriodOfTime)
        assert self._triple(g, temporal, SCHEMA.startDate, parse_date(extras['temporal_start']).isoformat(), XSD.dateTime)
        assert self._triple(g, temporal, SCHEMA.endDate, parse_date(extras['temporal_end']).isoformat(), XSD.dateTime)

    def test_spatial(self):
        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'extras': [
                {'key': 'spatial_uri', 'value': 'http://sws.geonames.org/6361390/'},
                {'key': 'spatial_text', 'value': 'Tarragona'},
                {'key': 'spatial', 'value': '{"type": "Polygon", "coordinates": [[[1.1870606,41.0786393],[1.1870606,41.1655218],[1.3752339,41.1655218],[1.3752339,41.0786393],[1.1870606,41.0786393]]]}'},

            ]
        }
        extras = self._extras(dataset)

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        spatial = self._triple(g, dataset_ref, DCT.spatial, None)[2]
        assert spatial
        assert str(spatial) == extras['spatial_uri']
        assert self._triple(g, spatial, RDF.type, DCT.Location)
        assert self._triple(g, spatial, SKOS.prefLabel, extras['spatial_text'])

        assert len([t for t in g.triples((spatial, LOCN.geometry, None))]) == 2
        # Geometry in GeoJSON
        assert self._triple(g, spatial, LOCN.geometry, extras['spatial'], GEOJSON_IMT)

        # Geometry in WKT
        wkt_geom = wkt.dumps(json.loads(extras['spatial']), decimals=4)
        assert self._triple(g, spatial, LOCN.geometry, wkt_geom, GSP.wktLiteral)

    def test_spatial_bad_geojson_no_wkt(self):
        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'extras': [
                {'key': 'spatial', 'value': '{"key": "NotGeoJSON"}'},

            ]
        }
        extras = self._extras(dataset)

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        spatial = self._triple(g, dataset_ref, DCT.spatial, None)[2]
        assert spatial
        assert isinstance(spatial, BNode)
        # Geometry in GeoJSON
        assert self._triple(g, spatial, LOCN.geometry, extras['spatial'], GEOJSON_IMT)

        # Geometry in WKT
        assert len([t for t in g.triples((spatial, LOCN.geometry, None))]) == 1

    def test_spatial_bad_json_no_wkt(self):
        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'extras': [
                {'key': 'spatial', 'value': 'NotJSON'},

            ]
        }
        extras = self._extras(dataset)

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        spatial = self._triple(g, dataset_ref, DCT.spatial, None)[2]
        assert spatial
        assert isinstance(spatial, BNode)
        # Geometry in GeoJSON
        assert self._triple(g, spatial, LOCN.geometry, extras['spatial'], GEOJSON_IMT)

        # Geometry in WKT
        assert len([t for t in g.triples((spatial, LOCN.geometry, None))]) == 1

    def test_distributions(self):

        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'title': 'Test DCAT dataset',
            'resources': [
                {
                    'id': 'c041c635-054f-4431-b647-f9186926d021',
                    'package_id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
                    'name': 'CSV file'
                },
                {
                    'id': '8bceeda9-0084-477f-aa33-dad6148900d5',
                    'package_id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
                    'name': 'XLS file'
                },
                {
                    'id': 'da73d939-0f11-45a1-9733-5de108383133',
                    'package_id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
                    'name': 'PDF file'
                },

            ]
        }

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        assert len([t for t in g.triples((dataset_ref, DCAT.distribution, None))]) == 3

        for resource in dataset['resources']:
            distribution = self._triple(g,
                                        dataset_ref,
                                        DCAT.distribution,
                                        URIRef(utils.resource_uri(resource)))[2]

            assert self._triple(g, distribution, RDF.type, DCAT.Distribution)
            assert self._triple(g, distribution, DCT.title, resource['name'])

    def test_distribution_fields(self):

        resource = {
            'id': 'c041c635-054f-4431-b647-f9186926d021',
            'package_id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'CSV file',
            'description': 'A CSV file',
            'url': 'http://example.com/data/file.csv',
            'status': 'http://purl.org/adms/status/Completed',
            'rights': 'Some statement about rights',
            'license': 'http://creativecommons.org/licenses/by/3.0/',
            'created': '2015-07-06T15:21:09.034694',
            'metadata_modified': '2015-07-07T15:21:09.075774',
            'issued': '2015-06-26T15:21:09.034694',
            'modified': '2015-06-26T15:21:09.075774',
            'size': 1234,
            'documentation': '[\"http://dataset.info.org/distribution1/doc1\", \"http://dataset.info.org/distribution1/doc2\"]',
            'language': '[\"en\", \"es\", \"http://publications.europa.eu/resource/authority/language/ITA\"]',
            'conforms_to': '[\"Standard 1\", \"Standard 2\"]',
            'hash': '4304cf2e751e6053c90b1804c89c0ebb758f395a',
            'hash_algorithm': 'http://spdx.org/rdf/terms#checksumAlgorithm_sha1',

        }

        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'title': 'Test DCAT dataset',
            'resources': [
                resource
            ]
        }

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        assert len([t for t in g.triples((dataset_ref, DCAT.distribution, None))]) == 1

        # URI
        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]
        assert str(distribution) == utils.resource_uri(resource)

        # Basic fields
        assert self._triple(g, distribution, RDF.type, DCAT.Distribution)
        assert self._triple(g, distribution, DCT.title, resource['name'])
        assert self._triple(g, distribution, DCT.description, resource['description'])
        assert self._triple(g, distribution, DCT.rights, resource['rights'])
        assert self._triple(g, distribution, DCT.license, URIRef(resource['license']))
        assert self._triple(g, distribution, ADMS.status, URIRef(resource['status']))

        # List
        for item in [
            ('documentation', FOAF.page, URIRef),
            ('language', DCT.language, [Literal, Literal, URIRef]),
            ('conforms_to', DCT.conformsTo, Literal),
        ]:
            values = json.loads(resource[item[0]])
            assert len([t for t in g.triples((distribution, item[1], None))]) == len(values)
            for num, value in enumerate(values):
                _type = item[2]
                if isinstance(item[2], list):
                    assert len(item[2]) == len(values)
                    _type = item[2][num]
                assert self._triple(g, distribution, item[1], _type(value))

        # Dates
        assert self._triple(g, distribution, DCT.issued, resource['issued'], XSD.dateTime)
        assert self._triple(g, distribution, DCT.modified, resource['modified'], XSD.dateTime)

        # Numbers
        assert self._triple(g, distribution, DCAT.byteSize, float(resource['size']), XSD.decimal)

        # Checksum
        checksum = self._triple(g, distribution, SPDX.checksum, None)[2]
        assert checksum
        assert self._triple(g, checksum, RDF.type, SPDX.Checksum)
        assert self._triple(g, checksum, SPDX.checksumValue, resource['hash'], data_type='http://www.w3.org/2001/XMLSchema#hexBinary')
        assert self._triple(g, checksum, SPDX.algorithm, URIRef(resource['hash_algorithm']))

    def test_distribution_size_not_number(self):

        resource = {
            'id': 'c041c635-054f-4431-b647-f9186926d021',
            'package_id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'CSV file',
            'size': 'aaaa',
        }

        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'title': 'Test DCAT dataset',
            'resources': [
                resource
            ]
        }

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]

        assert self._triple(g, distribution, DCAT.byteSize, resource['size'])

    def test_distribution_url_only(self):

        resource = {
            'id': 'c041c635-054f-4431-b647-f9186926d021',
            'package_id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'CSV file',
            'url': 'http://example.com/data/file.csv',
        }

        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'title': 'Test DCAT dataset',
            'resources': [
                resource
            ]
        }

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]

        assert self._triple(g, distribution, DCAT.accessURL, URIRef(resource['url']))
        assert self._triple(g, distribution, DCAT.downloadURL, None) is None

    def test_distribution_access_url_only(self):

        resource = {
            'id': 'c041c635-054f-4431-b647-f9186926d021',
            'package_id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'CSV file',
            'access_url': 'http://example.com/data/file.csv',
        }

        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'title': 'Test DCAT dataset',
            'resources': [
                resource
            ]
        }

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]

        assert self._triple(g, distribution, DCAT.accessURL, URIRef(resource['access_url']))
        assert self._triple(g, distribution, DCAT.downloadURL, None) is None

    def test_distribution_download_url_only(self):

        resource = {
            'id': 'c041c635-054f-4431-b647-f9186926d021',
            'package_id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'CSV file',
            'download_url': 'http://example.com/data/file.csv',
        }

        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'title': 'Test DCAT dataset',
            'resources': [
                resource
            ]
        }

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]

        assert self._triple(g, distribution, DCAT.downloadURL, URIRef(resource['download_url']))
        assert self._triple(g, distribution, DCAT.accessURL, None) is None

    def test_distribution_both_urls_different(self):

        resource = {
            'id': 'c041c635-054f-4431-b647-f9186926d021',
            'package_id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'CSV file',
            'url': 'http://example.com/data/file',
            'download_url': 'http://example.com/data/file.csv',
        }

        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'title': 'Test DCAT dataset',
            'resources': [
                resource
            ]
        }

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]

        assert self._triple(g, distribution, DCAT.accessURL, URIRef( resource['url']))
        assert self._triple(g, distribution, DCAT.downloadURL, URIRef(resource['download_url']))

    def test_distribution_both_urls_different_with_access_url(self):

        resource = {
            'id': 'c041c635-054f-4431-b647-f9186926d021',
            'package_id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'CSV file',
            'access_url': 'http://example.com/data/file',
            'download_url': 'http://example.com/data/file.csv',
        }

        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'title': 'Test DCAT dataset',
            'resources': [
                resource
            ]
        }

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]

        assert self._triple(g, distribution, DCAT.accessURL, URIRef( resource['access_url']))
        assert self._triple(g, distribution, DCAT.downloadURL, URIRef(resource['download_url']))

    def test_distribution_prefer_access_url(self):

        resource = {
            'id': 'c041c635-054f-4431-b647-f9186926d021',
            'package_id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'CSV file',
            'url': 'http://example.com/data',
            'access_url': 'http://example.com/data/file',
        }

        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'title': 'Test DCAT dataset',
            'resources': [
                resource
            ]
        }

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]

        assert self._triple(g, distribution, DCAT.accessURL, URIRef( resource['access_url']))
        assert self._triple(g, distribution, DCAT.downloadURL, None) is None

    def test_distribution_prefer_access_url_with_download(self):

        resource = {
            'id': 'c041c635-054f-4431-b647-f9186926d021',
            'package_id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'CSV file',
            'url': 'http://example.com/data',
            'access_url': 'http://example.com/data/file',
            'download_url': 'http://example.com/data/file.csv',
        }

        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'title': 'Test DCAT dataset',
            'resources': [
                resource
            ]
        }

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]

        assert self._triple(g, distribution, DCAT.accessURL, URIRef( resource['access_url']))
        assert self._triple(g, distribution, DCAT.downloadURL, URIRef(resource['download_url']))

    def test_distribution_both_urls_the_same(self):

        # old behavior - only serialize url to accessURL if it is different from downloadURL
        resource = {
            'id': 'c041c635-054f-4431-b647-f9186926d021',
            'package_id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'CSV file',
            'url': 'http://example.com/data/file.csv',
            'download_url': 'http://example.com/data/file.csv',
        }

        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'title': 'Test DCAT dataset',
            'resources': [
                resource
            ]
        }

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]

        assert self._triple(g, distribution, DCAT.downloadURL, URIRef(resource['url']))
        assert self._triple(g, distribution, DCAT.accessURL, None) is None

    def test_distribution_both_urls_the_same_with_access_url(self):

        # when the access_url is present, it should be serialized regardless if it is the same as downloadURL.
        resource = {
            'id': 'c041c635-054f-4431-b647-f9186926d021',
            'package_id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'CSV file',
            'access_url': 'http://example.com/data/file.csv',
            'download_url': 'http://example.com/data/file.csv',
        }

        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'title': 'Test DCAT dataset',
            'resources': [
                resource
            ]
        }

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]

        assert self._triple(g, distribution, DCAT.downloadURL, URIRef(resource['download_url']))
        assert self._triple(g, distribution, DCAT.accessURL, URIRef(resource['access_url']))

    def test_distribution_format_iana_uri(self):
        dataset_dict, resource = self._get_base_dataset_with_resource()
        # when only format is available and it looks like an IANA media type, use DCAT.mediaType instead
        # of DCT.format for output
        fmt_uri = 'https://www.iana.org/assignments/media-types/application/json'
        resource['format'] = fmt_uri

        # expect no dct:format node and the URI in dcat:mediaType
        self._build_graph_and_check_format_mediatype(
            dataset_dict,
            [],
            [URIRef(fmt_uri)]
        )

    def test_distribution_format_other_uri(self):
        dataset_dict, resource = self._get_base_dataset_with_resource()
        # when only format is available and it does not look like an IANA media type, use dct:format
        fmt_uri = 'https://example.com/my/format'
        resource['format'] = fmt_uri

        # expect dct:format node with the URI and no dcat:mediaType
        self._build_graph_and_check_format_mediatype(
            dataset_dict,
            [URIRef(fmt_uri)],
            []
        )

    def test_distribution_format_mediatype_text(self):
        dataset_dict, resource = self._get_base_dataset_with_resource()
        # if format value looks like an IANA media type, output dcat:mediaType instead of dct:format
        fmt_text = 'application/json'
        resource['format'] = fmt_text

        # expect no dct:format node and the literal value in dcat:mediaType
        self._build_graph_and_check_format_mediatype(
            dataset_dict,
            [],
            [Literal(fmt_text)]
        )

    def test_distribution_format_mediatype_same(self):
        dataset_dict, resource = self._get_base_dataset_with_resource()
        # if format and mediaType are identical, output only dcat:mediaType
        fmt_text = 'application/json'
        resource['format'] = fmt_text
        resource['mimetype'] = fmt_text

        # expect no dct:format node and the literal value in dcat:mediaType
        self._build_graph_and_check_format_mediatype(
            dataset_dict,
            [],
            [Literal(fmt_text)]
        )

    def test_distribution_dates_fallback(self):

        resource = {
            'id': 'c041c635-054f-4431-b647-f9186926d022',
            'package_id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'metadata_modified': '2015-06-26T15:21:09.075774',
            'created': '2015-06-26T15:21:09.034694',
        }

        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'title': 'Test DCAT dataset',
            'resources': [
                resource
            ]
        }

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        assert len([t for t in g.triples((dataset_ref, DCAT.distribution, None))]) == 1
        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]

        # Dates
        assert self._triple(g, distribution, DCT.modified, resource['metadata_modified'], XSD.dateTime)
        assert self._triple(g, distribution, DCT.issued, resource['created'], XSD.dateTime)

    def test_distribution_format_mediatype_different(self):
        dataset_dict, resource = self._get_base_dataset_with_resource()
        # if format and mediaType are different, output both
        resource['format'] = 'myformat'
        resource['mimetype'] = 'application/json'

        # expect both nodes
        self._build_graph_and_check_format_mediatype(
            dataset_dict,
            [Literal('myformat')],
            [Literal('application/json')]
        )

    def test_hash_algorithm_not_uri(self):

        resource = {
            'id': 'c041c635-054f-4431-b647-f9186926d021',
            'package_id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'CSV file',
            'hash': 'aaaa',
            'hash_algorithm': 'sha1',
        }

        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'title': 'Test DCAT dataset',
            'resources': [
                resource
            ]
        }

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]

        checksum = self._triple(g, distribution, SPDX.checksum, None)[2]
        assert checksum
        assert self._triple(g, checksum, RDF.type, SPDX.Checksum)
        assert self._triple(g, checksum, SPDX.checksumValue, resource['hash'], data_type='http://www.w3.org/2001/XMLSchema#hexBinary')
        assert self._triple(g, checksum, SPDX.algorithm, resource['hash_algorithm'])


class TestEuroDCATAPProfileSerializeCatalog(BaseSerializeTest):

    @classmethod
    def teardown_class(cls):
        helpers.reset_db()

    def test_graph_from_catalog(self):

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        catalog = s.graph_from_catalog()

        assert str(catalog) == utils.catalog_uri()

        # Basic fields
        assert self._triple(g, catalog, RDF.type, DCAT.Catalog)
        assert self._triple(g, catalog, DCT.title, config.get('ckan.site_title'))
        assert self._triple(g, catalog, FOAF.homepage, URIRef(config.get('ckan.site_url')))
        assert self._triple(g, catalog, DCT.language, 'en')

    def test_graph_from_catalog_dict(self):

        catalog_dict = {
            'title': 'My Catalog',
            'description': 'An Open Data Catalog',
            'homepage': 'http://example.com',
            'language': 'de',
        }

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        catalog = s.graph_from_catalog(catalog_dict)

        assert str(catalog) == utils.catalog_uri()

        # Basic fields
        assert self._triple(g, catalog, RDF.type, DCAT.Catalog)
        assert self._triple(g, catalog, DCT.title, catalog_dict['title'])
        assert self._triple(g, catalog, DCT.description, catalog_dict['description'])
        assert self._triple(g, catalog, FOAF.homepage, URIRef(catalog_dict['homepage']))
        assert self._triple(g, catalog, DCT.language, catalog_dict['language'])

    def test_graph_from_catalog_dict_language_uri_ref(self):

        catalog_dict = {
            'title': 'My Catalog',
            'description': 'An Open Data Catalog',
            'homepage': 'http://example.com',
            'language': 'http://publications.europa.eu/resource/authority/language/ITA',
        }

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        catalog = s.graph_from_catalog(catalog_dict)

        assert str(catalog) == utils.catalog_uri()

        # language field
        assert self._triple(g, catalog, DCT.language, URIRef(catalog_dict['language']))

    def test_graph_from_catalog_modified_date(self):

        dataset = factories.Dataset()

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        catalog = s.graph_from_catalog()

        assert str(catalog) == utils.catalog_uri()

        assert self._triple(g, catalog, DCT.modified, dataset['metadata_modified'], XSD.dateTime)

    @pytest.mark.ckan_config(DCAT_EXPOSE_SUBCATALOGS, 'true')
    def test_subcatalog(self):
        publisher = {'name': 'Publisher',
                     'email': 'email@test.com',
                     'type': 'Publisher',
                     'uri': 'http://pub.lish.er'}
        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'title': 'test dataset',
            'extras': [
                {'key': 'source_catalog_title', 'value': 'Subcatalog example'},
                {'key': 'source_catalog_homepage', 'value': 'http://subcatalog.example'},
                {'key': 'source_catalog_description', 'value': 'Subcatalog example description'},
                {'key': 'source_catalog_language', 'value': 'http://publications.europa.eu/resource/authority/language/ITA'},
                {'key': 'source_catalog_modified', 'value': '2000-01-01'},
                {'key': 'source_catalog_publisher', 'value': json.dumps(publisher)}
            ]
        }
        catalog_dict = {
            'title': 'My Catalog',
            'description': 'An Open Data Catalog',
            'homepage': 'http://example.com',
            'language': 'de',
        }

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        s.serialize_catalog(catalog_dict, dataset_dicts=[dataset])

        # check if we have catalog->hasPart->subcatalog
        catalogs = list(g.triples((None, RDF.type, DCAT.Catalog,)))
        root = list(g.subjects(DCT.hasPart, None))
        assert len(catalogs) > 0, catalogs
        assert len(root) == 1, root

        root_ref = root[0]

        # check subcatalog
        subcatalogs = list(g.objects(root_ref, DCT.hasPart))
        assert len(subcatalogs) == 1
        stitle = list(g.objects(subcatalogs[0], DCT.title))
        assert len(stitle) == 1
        assert str(stitle[0]) == 'Subcatalog example'

        # check dataset
        dataset_ref = list(g.subjects(RDF.type, DCAT.Dataset))
        assert len(dataset_ref) == 1
        dataset_ref = dataset_ref[0]
        dataset_title = list(g.objects(dataset_ref, DCT.title))
        assert len(dataset_title) == 1
        assert str(dataset_title[0]) == dataset['title']

    def test_catalog_pagination(self):
        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'title': 'test dataset',
            'extras': [
                {'key': 'source_catalog_title', 'value': 'Subcatalog example'},
                {'key': 'source_catalog_homepage', 'value': 'http://subcatalog.example'},
                {'key': 'source_catalog_description', 'value': 'Subcatalog example description'}
            ]
        }
        catalog_dict = {
            'title': 'My Catalog',
            'description': 'An Open Data Catalog',
            'homepage': 'http://example.com',
            'language': 'de',
        }

        expected_first = 'http://subcatalog.example?page=1'
        expected_next = 'http://subcatalog.example?page=2'
        expected_last = 'http://subcatalog.example?page=3'

        pagination = {
            'count': 12,
            'items_per_page': 5,
            'current':expected_first,
            'first':expected_first,
            'last':expected_last,
            'next':expected_next,
        }

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        s.serialize_catalog(catalog_dict, dataset_dicts=[dataset], pagination_info=pagination)

        paged_collection = list(g.subjects(RDF.type, HYDRA.PagedCollection))
        assert len(paged_collection) == 1

        # Pagination item: next
        next = list(g.objects(paged_collection[0], HYDRA.next))
        assert len(next) == 1
        assert str(next[0]) == expected_next
        next_page = list(g.objects(paged_collection[0], HYDRA.nextPage))
        assert len(next_page) == 1
        assert str(next_page[0]) == expected_next

        # Pagination item: previous
        previous_page = list(g.objects(paged_collection[0], HYDRA.previousPage))
        assert len(previous_page) == 0
        previous = list(g.objects(paged_collection[0], HYDRA.previous))
        assert len(previous) == 0

        # Pagination item: last
        last = list(g.objects(paged_collection[0], HYDRA.last))
        assert len(last) == 1
        assert str(last[0]) == expected_last
        last_page = list(g.objects(paged_collection[0], HYDRA.lastPage))
        assert len(last_page) == 1
        assert str(last_page[0]) == expected_last

        # Pagination item: count
        total_items = list(g.objects(paged_collection[0], HYDRA.totalItems))
        assert len(total_items) == 1
        assert str(total_items[0]) == "12"

        # Pagination item: items_per_page
        items_per_page = list(g.objects(paged_collection[0], HYDRA.itemsPerPage))
        assert len(items_per_page) == 1
        assert str(items_per_page[0]) == "5"

    @pytest.mark.ckan_config(DISTRIBUTION_LICENSE_FALLBACK_CONFIG, 'true')
    def test_set_missing_license_for_resource(self):
        ''' Check the behavior if param in config is set: Add license_id to the resource'''
        resource = {
            'id': 'c041c635-054f-4431-b647-f9186926d021',
            'package_id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'CSV file',
            'url': 'http://example.com/data/file.csv',
            'download_url': 'http://example.com/data/file.csv',
        }

        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'title': 'Test DCAT dataset',
            'license_id': 'https://example.com/license',
            'license_url': 'https://example.com/another-license',
            'resources': [
                resource
            ]
        }

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]
        assert str(distribution) == utils.resource_uri(resource)

        # Verify that the license_id of the dataset is now also in the distribution
        assert self._triple(g, distribution, DCT.license, URIRef(dataset['license_id']))

    @pytest.mark.ckan_config(DISTRIBUTION_LICENSE_FALLBACK_CONFIG, 'true')
    def test_set_missing_license_url_for_resource(self):
        ''' Check the behavior if param in config is set: Add license_url to the resource since license_id is not a valid URI '''
        resource = {
            'id': 'c041c635-054f-4431-b647-f9186926d021',
            'package_id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'CSV file',
            'url': 'http://example.com/data/file.csv',
            'download_url': 'http://example.com/data/file.csv',
        }

        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'title': 'Test DCAT dataset',
            'license_id': 'invalidUrl',
            'license_url': 'https://example.com/another-license',
            'resources': [
                resource
            ]
        }

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]
        assert str(distribution) == utils.resource_uri(resource)

        # Verify that the license_url of the dataset is now also in the distribution
        assert self._triple(g, distribution, DCT.license, URIRef(dataset['license_url']))

    @pytest.mark.ckan_config(DISTRIBUTION_LICENSE_FALLBACK_CONFIG, 'true')
    def test_set_no_missing_license_for_resource(self):
        ''' Check the behavior if param in config is set and no valid license information is given'''
        resource = {
            'id': 'c041c635-054f-4431-b647-f9186926d021',
            'package_id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'CSV file',
            'url': 'http://example.com/data/file.csv',
            'download_url': 'http://example.com/data/file.csv',
        }

        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'title': 'Test DCAT dataset',
            'license_id': 'invalidUrl',
            'license_url': 'anotherInvalidUrl',
            'resources': [
                resource
            ]
        }

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]
        assert str(distribution) == utils.resource_uri(resource)

        # Verify that there is no license in the distributions
        assert not self._triple(g, distribution, DCT.license, None)

    def test_dont_set_missing_license_for_resource(self):
        ''' Check the default behavior: Do not add a license to the resource'''
        resource = {
            'id': 'c041c635-054f-4431-b647-f9186926d021',
            'package_id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'CSV file',
            'url': 'http://example.com/data/file.csv',
            'download_url': 'http://example.com/data/file.csv',
        }

        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'title': 'Test DCAT dataset',
            'license_id': 'https://example.com/license',
            'resources': [
                resource
            ]
        }

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]
        assert str(distribution) == utils.resource_uri(resource)

        # Verify that the license of the dataset is not in the distribution
        assert not self._triple(g, distribution, DCT.license, URIRef(dataset['license_id']))

    @pytest.mark.ckan_config(DISTRIBUTION_LICENSE_FALLBACK_CONFIG, 'false')
    def test_dont_set_missing_license_for_resource_config_param_value_false(self):
        ''' Check the default behavior: Do not add a license to the resource'''
        resource = {
            'id': 'c041c635-054f-4431-b647-f9186926d021',
            'package_id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'CSV file',
            'url': 'http://example.com/data/file.csv',
            'download_url': 'http://example.com/data/file.csv',
        }

        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'title': 'Test DCAT dataset',
            'license_id': 'https://example.com/license',
            'resources': [
                resource
            ]
        }

        s = RDFSerializer(profiles=['euro_dcat_ap'])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]
        assert str(distribution) == utils.resource_uri(resource)

        # Verify that the license of the dataset is not in the distribution
        assert not self._triple(g, distribution, DCT.license, URIRef(dataset['license_id']))
