import json

import nose

from ckantoolkit import config

from dateutil.parser import parse as parse_date
from rdflib import URIRef, BNode, Literal
from rdflib.namespace import RDF

from geomet import wkt

from ckantoolkit.tests import helpers, factories

from ckanext.dcat import utils
from ckanext.dcat.processors import RDFSerializer
from ckanext.dcat.profiles import (DCAT, DCT, ADMS, XSD, VCARD, FOAF, SCHEMA,
                                   SKOS, LOCN, GSP, OWL, SPDX, GEOJSON_IMT)
from ckanext.dcat.utils import DCAT_EXPOSE_SUBCATALOGS

eq_ = nose.tools.eq_
assert_true = nose.tools.assert_true


class BaseSerializeTest(object):

    def _extras(self, dataset):
        extras = {}
        for extra in dataset.get('extras'):
            extras[extra['key']] = extra['value']
        return extras

    def _triples(self, graph, subject, predicate, _object, data_type=None):

        if not (isinstance(_object, URIRef) or isinstance(_object, BNode) or _object is None):
            if data_type:
                _object = Literal(_object, datatype=data_type)
            else:
                _object = Literal(_object)
        triples = [t for t in graph.triples((subject, predicate, _object))]
        return triples

    def _triple(self, graph, subject, predicate, _object, data_type=None):
        triples = self._triples(graph, subject, predicate, _object, data_type)
        return triples[0] if triples else None


class TestEuroDCATAPProfileSerializeDataset(BaseSerializeTest):

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
                {'key': 'alternate_identifier', 'value': '[\"xyz\", \"abc\"]'},
                {'key': 'version_notes', 'value': 'This is a beta version'},
                {'key': 'frequency', 'value': 'monthly'},
                {'key': 'language', 'value': '[\"en\"]'},
                {'key': 'theme', 'value': '[\"http://eurovoc.europa.eu/100142\", \"http://eurovoc.europa.eu/100152\"]'},
                {'key': 'conforms_to', 'value': '[\"Standard 1\", \"Standard 2\"]'},
                {'key': 'access_rights', 'value': 'public'},
                {'key': 'documentation', 'value': '[\"http://dataset.info.org/doc1\", \"http://dataset.info.org/doc2\"]'},
                {'key': 'provenance', 'value': 'Some statement about provenance'},
                {'key': 'dcat_type', 'value': 'test-type'},
                {'key': 'related_resource', 'value': '[\"http://dataset.info.org/related1\", \"http://dataset.info.org/related2\"]'},
                {'key': 'has_version', 'value': '[\"https://data.some.org/catalog/datasets/derived-dataset-1\", \"https://data.some.org/catalog/datasets/derived-dataset-2\"]'},
                {'key': 'is_version_of', 'value': '[\"https://data.some.org/catalog/datasets/original-dataset\"]'},
                {'key': 'source', 'value': '[\"https://data.some.org/catalog/datasets/source-dataset-1\", \"https://data.some.org/catalog/datasets/source-dataset-2\"]'},
                {'key': 'sample', 'value': '[\"https://data.some.org/catalog/datasets/9df8df51-63db-37a8-e044-0003ba9b0d98/sample\"]'},
            ]
        }
        extras = self._extras(dataset)

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        eq_(unicode(dataset_ref), utils.dataset_uri(dataset))

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
        eq_(len([t for t in g.triples((dataset_ref, DCAT.keyword, None))]), 2)
        for tag in dataset['tags']:
            assert self._triple(g, dataset_ref, DCAT.keyword, tag['name'])

        # Dates
        assert self._triple(g, dataset_ref, DCT.issued, dataset['metadata_created'], XSD.dateTime)
        assert self._triple(g, dataset_ref, DCT.modified, dataset['metadata_modified'], XSD.dateTime)

        # List
        for item in [
            ('language', DCT.language, Literal),
            ('theme', DCAT.theme, URIRef),
            ('conforms_to', DCT.conformsTo, Literal),
            ('alternate_identifier', ADMS.identifier, Literal),
            ('documentation', FOAF.page, Literal),
            ('related_resource', DCT.relation, Literal),
            ('has_version', DCT.hasVersion, Literal),
            ('is_version_of', DCT.isVersionOf, Literal),
            ('source', DCT.source, Literal),
            ('sample', ADMS.sample, Literal),
        ]:
            values = json.loads(extras[item[0]])
            eq_(len([t for t in g.triples((dataset_ref, item[1], None))]), len(values))
            for value in values:
                assert self._triple(g, dataset_ref, item[1], item[2](value))

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

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        assert self._triple(g, dataset_ref, DCT.identifier, extras['identifier'])

    def test_identifier_guid(self):
        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'extras': [
                {'key': 'guid', 'value': 'guidyyy'},
            ]
        }
        extras = self._extras(dataset)

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        assert self._triple(g, dataset_ref, DCT.identifier, extras['guid'])

    def test_identifier_id(self):
        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
        }

        s = RDFSerializer()
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

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        assert self._triple(g, dataset_ref, DCT.identifier, dataset['id'])

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

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        # Contact details

        contact_details = self._triple(g, dataset_ref, DCAT.contactPoint, None)[2]
        assert contact_details
        eq_(unicode(contact_details), extras['contact_uri'])
        assert self._triple(g, contact_details, VCARD.fn, extras['contact_name'])
        assert self._triple(g, contact_details, VCARD.hasEmail, extras['contact_email'])

    def test_contact_details_maintainer(self):
        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'maintainer': 'Example Maintainer',
            'maintainer_email': 'dep@example.com',
            'author': 'Example Author',
            'author_email': 'ped@example.com',
        }

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        contact_details = self._triple(g, dataset_ref, DCAT.contactPoint, None)[2]
        assert contact_details
        assert_true(isinstance(contact_details, BNode))
        assert self._triple(g, contact_details, VCARD.fn, dataset['maintainer'])
        assert self._triple(g, contact_details, VCARD.hasEmail, dataset['maintainer_email'])

    def test_contact_details_author(self):
        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'author': 'Example Author',
            'author_email': 'ped@example.com',
        }

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        contact_details = self._triple(g, dataset_ref, DCAT.contactPoint, None)[2]
        assert contact_details
        assert_true(isinstance(contact_details, BNode))
        assert self._triple(g, contact_details, VCARD.fn, dataset['author'])
        assert self._triple(g, contact_details, VCARD.hasEmail, dataset['author_email'])

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

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        publisher = self._triple(g, dataset_ref, DCT.publisher, None)[2]
        assert publisher
        eq_(unicode(publisher), extras['publisher_uri'])

        assert self._triple(g, publisher, RDF.type, FOAF.Organization)
        assert self._triple(g, publisher, FOAF.name, extras['publisher_name'])
        assert self._triple(g, publisher, FOAF.mbox, extras['publisher_email'])
        assert self._triple(g, publisher, FOAF.homepage, URIRef(extras['publisher_url']))
        assert self._triple(g, publisher, DCT.type, extras['publisher_type'])

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

        s = RDFSerializer()
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

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        publisher = self._triple(g, dataset_ref, DCT.publisher, None)[2]
        assert publisher
        assert_true(isinstance(publisher, BNode))

        assert self._triple(g, publisher, RDF.type, FOAF.Organization)
        assert self._triple(g, publisher, FOAF.name, extras['publisher_name'])

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

        s = RDFSerializer()
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

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        spatial = self._triple(g, dataset_ref, DCT.spatial, None)[2]
        assert spatial
        eq_(unicode(spatial), extras['spatial_uri'])
        assert self._triple(g, spatial, RDF.type, DCT.Location)
        assert self._triple(g, spatial, SKOS.prefLabel, extras['spatial_text'])

        eq_(len([t for t in g.triples((spatial, LOCN.geometry, None))]), 2)
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

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        spatial = self._triple(g, dataset_ref, DCT.spatial, None)[2]
        assert spatial
        assert_true(isinstance(spatial, BNode))
        # Geometry in GeoJSON
        assert self._triple(g, spatial, LOCN.geometry, extras['spatial'], GEOJSON_IMT)

        # Geometry in WKT
        eq_(len([t for t in g.triples((spatial, LOCN.geometry, None))]), 1)

    def test_spatial_bad_json_no_wkt(self):
        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'extras': [
                {'key': 'spatial', 'value': 'NotJSON'},

            ]
        }
        extras = self._extras(dataset)

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        spatial = self._triple(g, dataset_ref, DCT.spatial, None)[2]
        assert spatial
        assert_true(isinstance(spatial, BNode))
        # Geometry in GeoJSON
        assert self._triple(g, spatial, LOCN.geometry, extras['spatial'], GEOJSON_IMT)

        # Geometry in WKT
        eq_(len([t for t in g.triples((spatial, LOCN.geometry, None))]), 1)

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

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        eq_(len([t for t in g.triples((dataset_ref, DCAT.distribution, None))]), 3)

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
            'issued': '2015-06-26T15:21:09.034694',
            'modified': '2015-06-26T15:21:09.075774',
            'size': 1234,
            'documentation': '[\"http://dataset.info.org/distribution1/doc1\", \"http://dataset.info.org/distribution1/doc2\"]',
            'language': '[\"en\", \"es\", \"ca\"]',
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

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        eq_(len([t for t in g.triples((dataset_ref, DCAT.distribution, None))]), 1)

        # URI
        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]
        eq_(unicode(distribution), utils.resource_uri(resource))

        # Basic fields
        assert self._triple(g, distribution, RDF.type, DCAT.Distribution)
        assert self._triple(g, distribution, DCT.title, resource['name'])
        assert self._triple(g, distribution, DCT.description, resource['description'])
        assert self._triple(g, distribution, DCT.rights, resource['rights'])
        assert self._triple(g, distribution, DCT.license, resource['license'])
        assert self._triple(g, distribution, ADMS.status, resource['status'])

        # List
        for item in [
            ('documentation', FOAF.page),
            ('language', DCT.language),
            ('conforms_to', DCT.conformsTo),
        ]:
            values = json.loads(resource[item[0]])
            eq_(len([t for t in g.triples((distribution, item[1], None))]), len(values))
            for value in values:
                assert self._triple(g, distribution, item[1], value)

        # Dates
        assert self._triple(g, distribution, DCT.issued, resource['issued'], XSD.dateTime)
        assert self._triple(g, distribution, DCT.modified, resource['modified'], XSD.dateTime)

        # Numbers
        assert self._triple(g, distribution, DCAT.byteSize, float(resource['size']), XSD.decimal)

        # Checksum
        checksum = self._triple(g, distribution, SPDX.checksum, None)[2]
        assert checksum
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

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]

        assert self._triple(g, distribution, DCAT.byteSize, resource['size'])

    def test_distribution_access_url_only(self):

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

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]

        assert self._triple(g, distribution, DCAT.accessURL, URIRef(resource['url']))
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

        s = RDFSerializer()
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

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]

        assert self._triple(g, distribution, DCAT.accessURL, URIRef( resource['url']))
        assert self._triple(g, distribution, DCAT.downloadURL, URIRef(resource['download_url']))

    def test_distribution_both_urls_the_same(self):

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

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]

        assert self._triple(g, distribution, DCAT.downloadURL, URIRef(resource['url']))
        assert self._triple(g, distribution, DCAT.accessURL, None) is None

    def test_distribution_format(self):

        resource = {
            'id': 'c041c635-054f-4431-b647-f9186926d021',
            'package_id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'CSV file',
            'url': 'http://example.com/data/file.csv',
            'format': 'CSV',
            'mimetype': 'text/csv',
        }

        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'title': 'Test DCAT dataset',
            'resources': [
                resource
            ]
        }

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]

        assert self._triple(g, distribution, DCT['format'], resource['format'])
        assert self._triple(g, distribution, DCAT.mediaType, resource['mimetype'])

    def test_distribution_format_with_backslash(self):

        resource = {
            'id': 'c041c635-054f-4431-b647-f9186926d021',
            'package_id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'CSV file',
            'url': 'http://example.com/data/file.csv',
            'format': 'text/csv',
        }

        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'title': 'Test DCAT dataset',
            'resources': [
                resource
            ]
        }

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]

        assert self._triple(g, distribution, DCAT.mediaType, resource['format'])

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

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]

        checksum = self._triple(g, distribution, SPDX.checksum, None)[2]
        assert checksum
        assert self._triple(g, checksum, SPDX.checksumValue, resource['hash'], data_type='http://www.w3.org/2001/XMLSchema#hexBinary')
        assert self._triple(g, checksum, SPDX.algorithm, resource['hash_algorithm'])


class TestEuroDCATAPProfileSerializeCatalog(BaseSerializeTest):

    @classmethod
    def teardown_class(cls):
        helpers.reset_db()

    def test_graph_from_catalog(self):

        s = RDFSerializer()
        g = s.g

        catalog = s.graph_from_catalog()

        eq_(unicode(catalog), utils.catalog_uri())

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

        s = RDFSerializer()
        g = s.g

        catalog = s.graph_from_catalog(catalog_dict)

        eq_(unicode(catalog), utils.catalog_uri())

        # Basic fields
        assert self._triple(g, catalog, RDF.type, DCAT.Catalog)
        assert self._triple(g, catalog, DCT.title, catalog_dict['title'])
        assert self._triple(g, catalog, DCT.description, catalog_dict['description'])
        assert self._triple(g, catalog, FOAF.homepage, URIRef(catalog_dict['homepage']))
        assert self._triple(g, catalog, DCT.language, catalog_dict['language'])

    def test_graph_from_catalog_modified_date(self):

        dataset = factories.Dataset()

        s = RDFSerializer()
        g = s.g

        catalog = s.graph_from_catalog()

        eq_(unicode(catalog), utils.catalog_uri())

        assert self._triple(g, catalog, DCT.modified, dataset['metadata_modified'], XSD.dateTime)

    @helpers.change_config(DCAT_EXPOSE_SUBCATALOGS, 'true')
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

        s = RDFSerializer()
        g = s.g

        s.serialize_catalog(catalog_dict, dataset_dicts=[dataset])

        # check if we have catalog->hasPart->subcatalog
        catalogs = list(g.triples((None, RDF.type, DCAT.Catalog,)))
        root = list(g.subjects(DCT.hasPart, None))
        assert_true(len(catalogs)>0, catalogs)
        assert_true(len(root) == 1, root)

        root_ref = root[0]
        
        # check subcatalog
        subcatalogs = list(g.objects(root_ref, DCT.hasPart))
        assert_true(len(subcatalogs) == 1)
        stitle = list(g.objects(subcatalogs[0], DCT.title))
        assert_true(len(stitle) == 1)
        assert_true(str(stitle[0]) == 'Subcatalog example')

        # check dataset
        dataset_ref = list(g.subjects(RDF.type, DCAT.Dataset))
        assert_true(len(dataset_ref) == 1)
        dataset_ref = dataset_ref[0]
        dataset_title = list(g.objects(dataset_ref, DCT.title))
        assert_true(len(dataset_title) == 1)
        assert_true(unicode(dataset_title[0]) == dataset['title'])
