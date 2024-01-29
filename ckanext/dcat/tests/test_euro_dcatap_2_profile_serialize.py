# -*- coding: utf-8 -*-

from builtins import str
from builtins import object
import json
import six

import pytest

from ckantoolkit import config

from dateutil.parser import parse as parse_date
from rdflib import URIRef, BNode, Literal
from rdflib.namespace import RDF

from geomet import wkt

from ckantoolkit.tests import helpers, factories

from ckanext.dcat import utils
from ckanext.dcat.processors import RDFSerializer
from ckanext.dcat.profiles import (DCAT, DCATAP, DCT, ADMS, XSD, VCARD, FOAF, SCHEMA,
                                   SKOS, LOCN, GSP, OWL, SPDX, GEOJSON_IMT)
from ckanext.dcat.utils import DCAT_EXPOSE_SUBCATALOGS
from ckanext.dcat.tests.utils import BaseSerializeTest

DCAT_AP_2_PROFILE = 'euro_dcat_ap_2'
DCAT_AP_PROFILES = [DCAT_AP_2_PROFILE]


class TestEuroDCATAP2ProfileSerializeDataset(BaseSerializeTest):

    def test_graph_from_dataset(self):

        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'title': 'Test DCAT 2 dataset',
            'notes': 'Lorem ipsum',
            'url': 'http://example.com/ds1',
            'version': '1.0b',
            'metadata_created': '2021-06-21T15:21:09.034694',
            'metadata_modified': '2021-06-21T15:21:09.075774',
            'extras': [
                {'key': 'temporal_resolution', 'value': '[\"PT15M\", \"P1D\"]'},
                {'key': 'spatial_resolution_in_meters', 'value': '[30,20]'},
                {'key': 'is_referenced_by', 'value': '[\"https://doi.org/10.1038/sdata.2018.22\", \"test_isreferencedby\"]'},
            ]
        }

        extras = self._extras(dataset)

        s = RDFSerializer(profiles=DCAT_AP_PROFILES)
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        # List
        for item in [
            ('temporal_resolution', DCAT.temporalResolution, [Literal, Literal], [XSD.duration, XSD.duration]),
            ('is_referenced_by', DCT.isReferencedBy, [URIRef, Literal], [None, None]),
        ]:
            values = json.loads(extras[item[0]])
            assert len([t for t in g.triples((dataset_ref, item[1], None))]) == len(values)
            for num, value in enumerate(values):
                _type = item[2]
                _datatype = item[3]
                if isinstance(item[2], list):
                    assert len(item[2]) == len(values)
                    _type = item[2][num]
                    _datatype = item[3][num]
                assert self._triple(g, dataset_ref, item[1], _type(value), _datatype)

        # Spatial Resolution in Meters
        values = json.loads(extras['spatial_resolution_in_meters'])
        assert len([t for t in g.triples((dataset_ref, DCAT.spatialResolutionInMeters, None))]) == len(values)

        for value in values:
            assert self._triple(g, dataset_ref, DCAT.spatialResolutionInMeters, Literal(float(value),
                                datatype=XSD.decimal))

    def test_spatial_resolution_in_meters_single_value(self):

        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'title': 'Test DCAT 2 dataset',
            'notes': 'Lorem ipsum',
            'url': 'http://example.com/ds1',
            'version': '1.0b',
            'metadata_created': '2021-06-21T15:21:09.034694',
            'metadata_modified': '2021-06-21T15:21:09.075774',
            'extras': [
                {'key': 'spatial_resolution_in_meters', 'value': '30'}
            ]
        }

        extras = self._extras(dataset)

        s = RDFSerializer(profiles=DCAT_AP_PROFILES)
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        assert len([t for t in g.triples((dataset_ref, DCAT.spatialResolutionInMeters, None))]) == 1
        assert self._triple(g, dataset_ref, DCAT.spatialResolutionInMeters,
                            Literal(float(extras['spatial_resolution_in_meters']), datatype=XSD.decimal))

    def test_spatial_resolution_in_meters_a_value_is_not_a_number(self):

        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'title': 'Test DCAT 2 dataset',
            'notes': 'Lorem ipsum',
            'url': 'http://example.com/ds1',
            'version': '1.0b',
            'metadata_created': '2021-06-21T15:21:09.034694',
            'metadata_modified': '2021-06-21T15:21:09.075774',
            'extras': [
                {'key': 'spatial_resolution_in_meters', 'value': '[\"foo\",20]'}
            ]
        }

        extras = self._extras(dataset)

        s = RDFSerializer(profiles=DCAT_AP_PROFILES)
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        values = json.loads(extras['spatial_resolution_in_meters'])
        assert len([t for t in g.triples((dataset_ref, DCAT.spatialResolutionInMeters, None))]) == len(values)
        assert self._triple(g, dataset_ref, DCAT.spatialResolutionInMeters, Literal(values[0]))
        assert self._triple(g, dataset_ref, DCAT.spatialResolutionInMeters,
                            Literal(float(values[1]), datatype=XSD.decimal))

    def test_spatial_resolution_value_is_invalid_json(self):

        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'title': 'Test DCAT 2 dataset',
            'notes': 'Lorem ipsum',
            'url': 'http://example.com/ds1',
            'version': '1.0b',
            'metadata_created': '2021-06-21T15:21:09.034694',
            'metadata_modified': '2021-06-21T15:21:09.075774',
            'extras': [
                {'key': 'spatial_resolution_in_meters', 'value': 'foo 30'}
            ]
        }

        extras = self._extras(dataset)

        s = RDFSerializer(profiles=DCAT_AP_PROFILES)
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        assert len([t for t in g.triples((dataset_ref, DCAT.spatialResolutionInMeters, None))]) == 1
        assert self._triple(g, dataset_ref, DCAT.spatialResolutionInMeters,
                            Literal(extras['spatial_resolution_in_meters']))

    def test_spatial(self):
        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'extras': [
                {'key': 'spatial_uri', 'value': 'http://sws.geonames.org/6361390/'},
                {'key': 'spatial_text', 'value': 'Tarragona'},
                {'key': 'spatial', 'value': '{"type": "Polygon", "coordinates": [[[1.1870606,41.0786393],[1.1870606,41.1655218],[1.3752339,41.1655218],[1.3752339,41.0786393],[1.1870606,41.0786393]]]}'},
                {'key': 'spatial_bbox', 'value': '{"type": "Polygon", "coordinates": [[[2.1870606,42.0786393],[2.1870606,42.1655218],[2.3752339,42.1655218],[2.3752339,42.0786393],[2.1870606,42.0786393]]]}'},
                {'key': 'spatial_centroid', 'value': '{"type": "Point", "coordinates": [2.28114725,42.12208055]}'},

            ]
        }
        extras = self._extras(dataset)

        s = RDFSerializer(profiles=DCAT_AP_PROFILES)
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        spatial = self._triple(g, dataset_ref, DCT.spatial, None)[2]
        assert spatial
        assert str(spatial) == extras['spatial_uri']
        assert self._triple(g, spatial, RDF.type, DCT.Location)
        assert self._triple(g, spatial, SKOS.prefLabel, extras['spatial_text'])

        assert len([t for t in g.triples((spatial, LOCN.geometry, None))]) == 2
        assert len([t for t in g.triples((spatial, DCAT.bbox, None))]) == 2
        assert len([t for t in g.triples((spatial, DCAT.centroid, None))]) == 2
        # Geometry in GeoJSON
        assert self._triple(g, spatial, LOCN.geometry, extras['spatial'], GEOJSON_IMT)
        assert self._triple(g, spatial, DCAT.bbox, extras['spatial_bbox'], GEOJSON_IMT)
        assert self._triple(g, spatial, DCAT.centroid, extras['spatial_centroid'], GEOJSON_IMT)

        # Geometry in WKT
        wkt_geom = wkt.dumps(json.loads(extras['spatial']), decimals=4)
        assert self._triple(g, spatial, LOCN.geometry, wkt_geom, GSP.wktLiteral)
        wkt_bbox = wkt.dumps(json.loads(extras['spatial_bbox']), decimals=4)
        assert self._triple(g, spatial, DCAT.bbox, wkt_bbox, GSP.wktLiteral)
        wkt_cent = wkt.dumps(json.loads(extras['spatial_centroid']), decimals=4)
        assert self._triple(g, spatial, DCAT.centroid, wkt_cent, GSP.wktLiteral)

    def test_spatial_bad_geojson_no_wkt(self):
        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'extras': [
                {'key': 'spatial', 'value': '{"key": "NotGeoJSON"}'},
                {'key': 'spatial_bbox', 'value': '{"key": "NotGeoJSON"}'},
                {'key': 'spatial_centroid', 'value': '{"key": "NotGeoJSON"}'},

            ]
        }
        extras = self._extras(dataset)

        s = RDFSerializer(profiles=DCAT_AP_PROFILES)
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        spatial = self._triple(g, dataset_ref, DCT.spatial, None)[2]
        assert spatial
        assert isinstance(spatial, BNode)
        # Geometry in GeoJSON
        assert self._triple(g, spatial, LOCN.geometry, extras['spatial'], GEOJSON_IMT)
        assert self._triple(g, spatial, LOCN.geometry, extras['spatial_bbox'], GEOJSON_IMT)
        assert self._triple(g, spatial, LOCN.geometry, extras['spatial_centroid'], GEOJSON_IMT)


        # Geometry in WKT
        assert len([t for t in g.triples((spatial, LOCN.geometry, None))]) == 1
        assert len([t for t in g.triples((spatial, DCAT.bbox, None))]) == 1
        assert len([t for t in g.triples((spatial, DCAT.centroid, None))]) == 1

    def test_spatial_bad_json_no_wkt(self):
        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'extras': [
                {'key': 'spatial', 'value': 'NotJSON'},
                {'key': 'spatial_bbox', 'value': 'NotJSON'},
                {'key': 'spatial_centroid', 'value': 'NotJSON'},

            ]
        }
        extras = self._extras(dataset)

        s = RDFSerializer(profiles=DCAT_AP_PROFILES)
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        spatial = self._triple(g, dataset_ref, DCT.spatial, None)[2]
        assert spatial
        assert isinstance(spatial, BNode)
        # Geometry in GeoJSON
        assert self._triple(g, spatial, LOCN.geometry, extras['spatial'], GEOJSON_IMT)
        assert self._triple(g, spatial, LOCN.geometry, extras['spatial_bbox'], GEOJSON_IMT)
        assert self._triple(g, spatial, LOCN.geometry, extras['spatial_centroid'], GEOJSON_IMT)

        # No Geometry in WKT, only one single triple for GeoJSON
        assert len([t for t in g.triples((spatial, LOCN.geometry, None))]) == 1
        # Always only one single triple
        assert len([t for t in g.triples((spatial, DCAT.bbox, None))]) == 1
        assert len([t for t in g.triples((spatial, DCAT.centroid, None))]) == 1

    def test_temporal(self):
        """
        Tests that the DCAT date properties are included in the graph in addition to schema.org dates.
        """

        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'extras': [
                {'key': 'temporal_start', 'value': '2015-06-26T15:21:09.075774'},
                {'key': 'temporal_end', 'value': '2015-07-14'},
            ]
        }
        extras = self._extras(dataset)

        s = RDFSerializer(profiles=DCAT_AP_PROFILES)
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        temporals = self._triples(g, dataset_ref, DCT.temporal, None)
        assert temporals
        assert len(temporals) == 2

        assert len([self._triple(g, temporal[2] , RDF.type, DCT.PeriodOfTime) for temporal in temporals]) == 2

        temporal_obj_list = [temporal[2] for temporal in temporals]
        for predicate in [SCHEMA.startDate, DCAT.startDate]:
            triples = []
            for temporal_obj in temporal_obj_list:
                triples.extend(self._triples(g, temporal_obj, predicate, parse_date(extras['temporal_start']).isoformat(), XSD.dateTime))
            assert len(triples) == 1

        for predicate in [SCHEMA.endDate, DCAT.endDate]:
            triples = []
            for temporal_obj in temporal_obj_list:
                triples.extend(self._triples(g, temporal_obj, predicate, parse_date(extras['temporal_end']).isoformat(), XSD.dateTime))
            assert len(triples) == 1

    def test_high_value_datasets(self):
        """
        Tests that the HVD information properties are included in the graph.
        """

        resource = {
            'id': 'c041c635-054f-4431-b647-f9186926d021',
            'package_id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'Distribution name',
            'applicable_legislation': json.dumps(['http://data.europa.eu/eli/reg_impl/2023/138/oj', 'http://data.europa.eu/eli/reg_impl/2023/138/oj_alt']),
        }

        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'extras': [
                {'key': 'applicable_legislation', 'value': '[\"http://data.europa.eu/eli/reg_impl/2023/138/oj\", \"http://data.europa.eu/eli/reg_impl/2023/138/oj_alt\"]'},
                {'key': 'hvd_category', 'value': '[\"http://data.europa.eu/bna/c_164e0bf5\", \"http://data.europa.eu/bna/c_ac64a52d\"]'},
            ],
            'resources': [
                resource
            ]
        }
        extras = self._extras(dataset)

        s = RDFSerializer(profiles=DCAT_AP_PROFILES)
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        values = json.loads(extras['applicable_legislation'])
        assert len([t for t in g.triples((dataset_ref, DCATAP.applicableLegislation, None))]) == len(values)
        assert self._triple(g, dataset_ref, DCATAP.applicableLegislation, URIRef(values[0]))

        values = json.loads(extras['hvd_category'])
        assert len([t for t in g.triples((dataset_ref, DCATAP.hvdCategory, None))]) == len(values)
        assert self._triple(g, dataset_ref, DCATAP.hvdCategory, URIRef(values[0]))

        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]
        self._assert_values_list(g, distribution, DCATAP.applicableLegislation,
                               self._get_typed_list(json.loads(resource['applicable_legislation']), URIRef))


    def test_distribution_fields(self):

        resource = {
            'id': 'c041c635-054f-4431-b647-f9186926d021',
            'package_id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'Distribution name',
            'availability': 'http://publications.europa.eu/resource/authority/planned-availability/EXPERIMENTAL',
            'compress_format': 'http://www.iana.org/assignments/media-types/application/gzip',
            'package_format': 'http://publications.europa.eu/resource/authority/file-type/TAR',
            'access_services': json.dumps([
                {
                    'availability': 'http://publications.europa.eu/resource/authority/planned-availability/AVAILABLE',
                    'title': 'Sparql-end Point 1',
                    'endpoint_description': 'SPARQL url description 1',
                    'license': 'http://publications.europa.eu/resource/authority/licence/COM_REUSE',
                    'access_rights': 'http://publications.europa.eu/resource/authority/access-right/PUBLIC',
                    'description': 'This SPARQL end point allow to directly query the EU Whoiswho content 1',
                    'endpoint_url': ['http://publications.europa.eu/webapi/rdf/sparql'],
                    'serves_dataset': ['http://data.europa.eu/88u/dataset/eu-whoiswho-the-official-directory-of-the-european-union']
                },
                {
                    'availability': 'http://publications.europa.eu/resource/authority/planned-availability/EXPERIMENTAL',
                    'title': 'Sparql-end Point 2',
                    'endpoint_description': 'SPARQL url description 2',
                    'license': 'http://publications.europa.eu/resource/authority/licence/CC_BY',
                    'access_rights': 'http://publications.europa.eu/resource/authority/access-right/OP_DATPRO',
                    'description': 'This SPARQL end point allow to directly query the EU Whoiswho content 2',
                    'endpoint_url': ['http://publications.europa.eu/webapi/rdf/sparql'],
                    'serves_dataset': ['http://data.europa.eu/88u/dataset/eu-whoiswho-the-official-directory-of-the-european-union']
                }
            ])
        }

        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'title': 'Test DCAT dataset',
            'resources': [
                resource
            ]
        }

        s = RDFSerializer(profiles=DCAT_AP_PROFILES)
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        assert len([t for t in g.triples((dataset_ref, DCAT.distribution, None))]) == 1

        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]

        assert self._triple(g, distribution, RDF.type, DCAT.Distribution)
        assert self._triple(g, distribution, DCATAP.availability, URIRef(resource['availability']))
        assert self._triple(g, distribution, DCAT.compressFormat, URIRef(resource['compress_format']))
        assert self._triple(g, distribution, DCAT.packageFormat, URIRef(resource['package_format']))

        # Access services
        object_list = self._triples(g, distribution, DCAT.accessService, None)

        assert len(object_list) == 2
        access_services = json.loads(resource['access_services'])

        for object in object_list:
            title_objects = self._triples(g, object[2], DCT.title, None)
            assert len(title_objects) == 1
            access_service = self._get_dict_from_list(access_services, 'title',
                                                                six.text_type(title_objects[0][2]))
            assert access_service

            # Simple values
            self._assert_simple_value(g, object[2], DCATAP.availability,
                                  URIRef(access_service.get('availability')))
            self._assert_simple_value(g, object[2], DCT.accessRights,
                                  URIRef(access_service.get('access_rights')))
            self._assert_simple_value(g, object[2], DCT.license,
                                  URIRef(access_service.get('license')))
            self._assert_simple_value(g, object[2], DCT.title,
                                  Literal(access_service.get('title')))
            self._assert_simple_value(g, object[2], DCT.description,
                                  Literal(access_service.get('description')))
            self._assert_simple_value(g, object[2], DCAT.endpointDescription,
                                  Literal(access_service.get('endpoint_description')))

            # Lists
            self._assert_values_list(g, object[2], DCAT.endpointURL,
                               self._get_typed_list(access_service.get('endpoint_url'), URIRef))
            self._assert_values_list(g, object[2], DCAT.servesDataset,
                               self._get_typed_list(access_service.get('serves_dataset'), URIRef))

    def test_distribution_fields_literal(self):

        resource = {
            'id': 'c041c635-054f-4431-b647-f9186926d021',
            'package_id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'Distribution name',
            'availability': 'EXPERIMENTAL',
            'compress_format': 'gzip',
            'package_format': 'TAR',
            'access_services': json.dumps([
                {
                    'availability': 'AVAILABLE',
                    'title': 'Sparql-end Point 1',
                    'license': 'COM_REUSE',
                    'access_rights': 'PUBLIC',
                    'endpoint_url': ['sparql'],
                    'serves_dataset': ['eu-whoiswho-the-official-directory-of-the-european-union']
                },
                {
                    'availability': 'EXPERIMENTAL',
                    'title': 'Sparql-end Point 2',
                    'license': 'CC_BY',
                    'access_rights': 'OP_DATPRO',
                    'endpoint_url': ['sparql'],
                    'serves_dataset': ['eu-whoiswho-the-official-directory-of-the-european-union']
                }
            ])
        }

        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'title': 'Test DCAT dataset',
            'resources': [
                resource
            ]
        }

        s = RDFSerializer(profiles=DCAT_AP_PROFILES)
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        assert len([t for t in g.triples((dataset_ref, DCAT.distribution, None))]) == 1

        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]

        assert self._triple(g, distribution, RDF.type, DCAT.Distribution)
        assert self._triple(g, distribution, DCATAP.availability, Literal(resource['availability']))
        assert self._triple(g, distribution, DCAT.compressFormat, Literal(resource['compress_format']))
        assert self._triple(g, distribution, DCAT.packageFormat, Literal(resource['package_format']))

        # Access services
        object_list = self._triples(g, distribution, DCAT.accessService, None)

        assert len(object_list) == 2
        access_services = json.loads(resource['access_services'])

        for object in object_list:
            title_objects = self._triples(g, object[2], DCT.title, None)
            assert len(title_objects) == 1
            access_service = self._get_dict_from_list(access_services, 'title',
                                                                six.text_type(title_objects[0][2]))
            assert access_service
            assert access_service.get('access_service_ref', None)

            # Simple values
            self._assert_simple_value(g, object[2], DCATAP.availability,
                                  Literal(access_service.get('availability')))
            self._assert_simple_value(g, object[2], DCT.accessRights,
                                  Literal(access_service.get('access_rights')))
            self._assert_simple_value(g, object[2], DCT.license,
                                  Literal(access_service.get('license')))
            self._assert_simple_value(g, object[2], DCT.title,
                                  Literal(access_service.get('title')))

            # Lists
            self._assert_values_list(g, object[2], DCAT.endpointURL,
                               self._get_typed_list(access_service.get('endpoint_url'), Literal))
            self._assert_values_list(g, object[2], DCAT.servesDataset,
                               self._get_typed_list(access_service.get('serves_dataset'), Literal))

    def test_access_service_fields_invalid_json(self):

        resource = {
            'id': 'c041c635-054f-4431-b647-f9186926d021',
            'package_id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'Distribution name'
        }

        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'title': 'Test DCAT dataset',
            'resources': [
                resource
            ]
        }

        access_service_list = "Invalid Json"

        dataset['resources'][0]['access_services'] = access_service_list

        s = RDFSerializer(profiles=DCAT_AP_PROFILES)
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        assert len([t for t in g.triples((dataset_ref, DCAT.distribution, None))]) == 1

        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]


        object_list = [t for t in g.triples((distribution, DCAT.accessService, None))]
        assert len(object_list) == 0

    def test_access_services_absent(self):

        resource = {
            'id': 'c041c635-054f-4431-b647-f9186926d021',
            'package_id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'Distribution name'
        }

        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'title': 'Test DCAT dataset',
            'resources': [
                resource
            ]
        }

        s = RDFSerializer(profiles=DCAT_AP_PROFILES)
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        assert len([t for t in g.triples((dataset_ref, DCAT.distribution, None))]) == 1

        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]

        object_list = [t for t in g.triples((distribution, DCAT.accessService, None))]
        assert len(object_list) == 0
        assert 'access_services' not in dataset['resources'][0]

    def test_access_services_list_values_only(self):

        resource = {
            'id': 'c041c635-054f-4431-b647-f9186926d021',
            'package_id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'Distribution name',
            'access_services': json.dumps([
                {
                    'endpoint_url': ['http://publications.europa.eu/webapi/rdf/sparql'],
                    'serves_dataset': ['http://data.europa.eu/88u/dataset/eu-whoiswho-the-official-directory-of-the-european-union']
                }
            ])
        }

        dataset = {
            'id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'test-dataset',
            'title': 'Test DCAT dataset',
            'resources': [
                resource
            ]
        }

        s = RDFSerializer(profiles=DCAT_AP_PROFILES)
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        assert len([t for t in g.triples((dataset_ref, DCAT.distribution, None))]) == 1

        distribution = self._triple(g, dataset_ref, DCAT.distribution, None)[2]

        assert len([t for t in g.triples((distribution, DCAT.accessService, None))]) == 1

        # Access services
        access_service_object = self._triple(g, distribution, DCAT.accessService, None)[2]

        access_services = json.loads(resource['access_services'])

        # Lists
        self._assert_values_list(g, access_service_object, DCAT.endpointURL,
                            self._get_typed_list(access_services[0].get('endpoint_url'), URIRef))
        self._assert_values_list(g, access_service_object, DCAT.servesDataset,
                            self._get_typed_list(access_services[0].get('serves_dataset'), URIRef))

    def _assert_simple_value(self, graph, object, predicate, value):
        """
        Checks if a triple with the given value is present in the graph
        """
        triples = self._triples(graph, object, predicate, None)
        assert len(triples) == 1
        assert triples[0][2] == value

    def _assert_values_list(self, graph, object, predicate, values):
        """
        Checks if triples with the given values are present in the graph
        """
        triples = self._triples(graph, object, predicate, None)
        assert len(triples) == len(values)
        for triple in triples:
            assert triple[2] in values
