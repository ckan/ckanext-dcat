# -*- coding: utf-8 -*-

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

    def test_distribution_fields(self):

        resource = {
            'id': 'c041c635-054f-4431-b647-f9186926d021',
            'package_id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'Distribution name',
            'availability': 'http://publications.europa.eu/resource/authority/planned-availability/EXPERIMENTAL',
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

    def test_distribution_availability_literal(self):

        resource = {
            'id': 'c041c635-054f-4431-b647-f9186926d021',
            'package_id': '4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6',
            'name': 'Distribution name',
            'availability': 'EXPERIMENTAL',
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
