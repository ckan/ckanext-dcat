from builtins import str
from builtins import object
import os
import json

import pytest

from rdflib import Graph, URIRef, BNode, Literal
from rdflib.namespace import RDF

from ckan.plugins import toolkit

from ckantoolkit import config
from ckantoolkit.tests import helpers, factories

from ckanext.dcat.processors import RDFParser, RDFSerializer
from ckanext.dcat.profiles import (DCAT, DCT, ADMS, LOCN, SKOS, GSP, RDFS,
                                   GEOJSON_IMT, VCARD, XSD)
from ckanext.dcat.utils import DCAT_EXPOSE_SUBCATALOGS, DCAT_CLEAN_TAGS
from ckanext.dcat.tests.utils import BaseParseTest

DCAT_AP_2_PROFILE = 'euro_dcat_ap_2'
DCAT_AP_PROFILES = [DCAT_AP_2_PROFILE]


class TestEuroDCATAP2ProfileParsing(BaseParseTest):

    def test_temporal_resolution(self):
        g = Graph()

        dataset = URIRef('http://example.org/datasets/1')
        g.add((dataset, RDF.type, DCAT.Dataset))

        temporal_resolution = 'P1D'
        g.add((dataset, DCAT.temporalResolution, Literal(temporal_resolution, datatype=XSD.duration)))

        p = RDFParser(profiles=DCAT_AP_PROFILES)

        p.g = g

        datasets = [d for d in p.datasets()]

        extras = self._extras(datasets[0])

        temporal_resolution_list = json.loads(extras['temporal_resolution'])
        assert len(temporal_resolution_list) == 1
        assert  temporal_resolution in temporal_resolution_list

    def test_temporal_resolution_multiple(self):
        g = Graph()

        dataset = URIRef('http://example.org/datasets/1')
        g.add((dataset, RDF.type, DCAT.Dataset))

        temporal_resolution = 'P1D'
        g.add((dataset, DCAT.temporalResolution, Literal(temporal_resolution, datatype=XSD.duration)))
        temporal_resolution_2 = 'PT15M'
        g.add((dataset, DCAT.temporalResolution, Literal(temporal_resolution_2, datatype=XSD.duration)))

        p = RDFParser(profiles=DCAT_AP_PROFILES)

        p.g = g

        datasets = [d for d in p.datasets()]

        extras = self._extras(datasets[0])

        temporal_resolution_list = json.loads(extras['temporal_resolution'])
        assert len(temporal_resolution_list) == 2
        assert  temporal_resolution in temporal_resolution_list
        assert  temporal_resolution_2 in temporal_resolution_list

    def test_spatial_resolution_in_meters(self):
        g = Graph()

        dataset = URIRef('http://example.org/datasets/1')
        g.add((dataset, RDF.type, DCAT.Dataset))

        spatial_resolution_in_meters = 30
        g.add((dataset, DCAT.spatialResolutionInMeters, Literal(spatial_resolution_in_meters, datatype=XSD.decimal)))

        p = RDFParser(profiles=DCAT_AP_PROFILES)

        p.g = g

        datasets = [d for d in p.datasets()]

        extras = self._extras(datasets[0])

        spatial_resolution_list = json.loads(extras['spatial_resolution_in_meters'])
        assert len(spatial_resolution_list) == 1
        assert  spatial_resolution_in_meters in spatial_resolution_list

    def test_spatial_resolution_in_meters_multiple(self):
        g = Graph()

        dataset = URIRef('http://example.org/datasets/1')
        g.add((dataset, RDF.type, DCAT.Dataset))

        spatial_resolution_in_meters = 30
        g.add((dataset, DCAT.spatialResolutionInMeters, Literal(spatial_resolution_in_meters, datatype=XSD.decimal)))

        spatial_resolution_in_meters_2 = 20
        g.add((dataset, DCAT.spatialResolutionInMeters, Literal(spatial_resolution_in_meters_2, datatype=XSD.decimal)))

        p = RDFParser(profiles=DCAT_AP_PROFILES)

        p.g = g

        datasets = [d for d in p.datasets()]

        extras = self._extras(datasets[0])

        spatial_resolution_list = json.loads(extras['spatial_resolution_in_meters'])
        assert len(spatial_resolution_list) == 2
        assert  spatial_resolution_in_meters in spatial_resolution_list
        assert  spatial_resolution_in_meters_2 in spatial_resolution_list

class TestEuroDCATAP2ProfileParsingSpatial(BaseParseTest):

    def test_spatial_multiple_dct_spatial_instances(self):
        g = Graph()

        dataset = URIRef('http://example.org/datasets/1')
        g.add((dataset, RDF.type, DCAT.Dataset))

        spatial_uri = URIRef('http://geonames/Newark')
        g.add((dataset, DCT.spatial, spatial_uri))

        location_ref = BNode()
        g.add((location_ref, RDF.type, DCT.Location))
        g.add((dataset, DCT.spatial, location_ref))

        geometry_val = '{"type": "Point", "coordinates": [23, 45]}'
        g.add((location_ref, LOCN.geometry, Literal(geometry_val, datatype=GEOJSON_IMT)))

        bbox_val = '{"type": "Polygon", "coordinates": [[[1, 1], [1, 2], [2, 2], [2, 1], [1, 1]]]}'
        g.add((location_ref, DCAT.bbox, Literal(bbox_val, datatype=GEOJSON_IMT)))

        centroid_val = '{"type": "Point", "coordinates": [1.5, 1.5]}'
        g.add((location_ref, DCAT.centroid, Literal(centroid_val, datatype=GEOJSON_IMT)))

        location_ref = BNode()
        g.add((location_ref, RDF.type, DCT.Location))
        g.add((dataset, DCT.spatial, location_ref))
        g.add((location_ref, SKOS.prefLabel, Literal('Newark')))

        p = RDFParser(profiles=DCAT_AP_PROFILES)

        p.g = g

        datasets = [d for d in p.datasets()]

        extras = self._extras(datasets[0])

        assert extras['spatial_uri'] == 'http://geonames/Newark'
        assert extras['spatial_text'] == 'Newark'
        assert extras['spatial'] == geometry_val
        assert extras['spatial_bbox'] == bbox_val
        assert extras['spatial_centroid'] == centroid_val

    def test_spatial_one_dct_spatial_instance(self):
        g = Graph()

        dataset = URIRef('http://example.org/datasets/1')
        g.add((dataset, RDF.type, DCAT.Dataset))

        spatial_uri = URIRef('http://geonames/Newark')
        g.add((dataset, DCT.spatial, spatial_uri))
        g.add((spatial_uri, RDF.type, DCT.Location))
        g.add((spatial_uri, SKOS.prefLabel, Literal('Newark')))

        geometry_val = '{"type": "Point", "coordinates": [23, 45]}'
        g.add((spatial_uri, LOCN.geometry, Literal(geometry_val, datatype=GEOJSON_IMT)))

        bbox_val = '{"type": "Polygon", "coordinates": [[[1, 1], [1, 2], [2, 2], [2, 1], [1, 1]]]}'
        g.add((spatial_uri, DCAT.bbox, Literal(bbox_val, datatype=GEOJSON_IMT)))

        centroid_val = '{"type": "Point", "coordinates": [1.5, 1.5]}'
        g.add((spatial_uri, DCAT.centroid, Literal(centroid_val, datatype=GEOJSON_IMT)))

        p = RDFParser(profiles=DCAT_AP_PROFILES)

        p.g = g

        datasets = [d for d in p.datasets()]

        extras = self._extras(datasets[0])

        assert extras['spatial_uri'] == 'http://geonames/Newark'
        assert extras['spatial_text'] == 'Newark'
        assert extras['spatial'] == geometry_val
        assert extras['spatial_bbox'] == bbox_val
        assert extras['spatial_centroid'] == centroid_val

    def test_spatial_one_dct_spatial_instance_no_uri_no_bbox_no_centroid(self):
        g = Graph()

        dataset = URIRef('http://example.org/datasets/1')
        g.add((dataset, RDF.type, DCAT.Dataset))

        location_ref = BNode()
        g.add((dataset, DCT.spatial, location_ref))

        g.add((location_ref, RDF.type, DCT.Location))
        g.add((location_ref,
               LOCN.geometry,
               Literal('{"type": "Point", "coordinates": [23, 45]}', datatype=GEOJSON_IMT)))
        g.add((location_ref, SKOS.prefLabel, Literal('Newark')))

        p = RDFParser(profiles=DCAT_AP_PROFILES)

        p.g = g

        datasets = [d for d in p.datasets()]

        extras = self._extras(datasets[0])

        assert 'spatial_uri' not in extras
        assert 'spatial_bbox' not in extras
        assert 'spatial_centroid' not in extras
        assert extras['spatial_text'] == 'Newark'
        assert extras['spatial'] == '{"type": "Point", "coordinates": [23, 45]}'

    def test_spatial_rdfs_label(self):
        g = Graph()

        dataset = URIRef('http://example.org/datasets/1')
        g.add((dataset, RDF.type, DCAT.Dataset))

        spatial_uri = URIRef('http://geonames/Newark')
        g.add((dataset, DCT.spatial, spatial_uri))

        g.add((spatial_uri, RDF.type, DCT.Location))
        g.add((spatial_uri, RDFS.label, Literal('Newark')))

        p = RDFParser(profiles=DCAT_AP_PROFILES)

        p.g = g

        datasets = [d for d in p.datasets()]

        extras = self._extras(datasets[0])

        assert extras['spatial_text'] == 'Newark'

    def test_spatial_both_geojson_and_wkt(self):
        g = Graph()

        dataset = URIRef('http://example.org/datasets/1')
        g.add((dataset, RDF.type, DCAT.Dataset))

        spatial_uri = URIRef('http://geonames/Newark')
        g.add((dataset, DCT.spatial, spatial_uri))

        g.add((spatial_uri, RDF.type, DCT.Location))
        g.add((spatial_uri,
               LOCN.geometry,
               Literal('{"type": "Point", "coordinates": [23, 45]}', datatype=GEOJSON_IMT)))
        g.add((spatial_uri,
               LOCN.geometry,
               Literal('POINT (67 89)', datatype=GSP.wktLiteral)))
        g.add((spatial_uri,
               DCAT.bbox,
               Literal('{"type": "Point", "coordinates": [24, 46]}', datatype=GEOJSON_IMT)))
        g.add((spatial_uri,
               DCAT.bbox,
               Literal('POINT (68 90)', datatype=GSP.wktLiteral)))
        g.add((spatial_uri,
               DCAT.centroid,
               Literal('{"type": "Point", "coordinates": [25, 47]}', datatype=GEOJSON_IMT)))
        g.add((spatial_uri,
               DCAT.centroid,
               Literal('POINT (69 91)', datatype=GSP.wktLiteral)))

        p = RDFParser(profiles=DCAT_AP_PROFILES)

        p.g = g

        datasets = [d for d in p.datasets()]

        extras = self._extras(datasets[0])

        assert extras['spatial'] == '{"type": "Point", "coordinates": [23, 45]}'
        assert extras['spatial_bbox'] == '{"type": "Point", "coordinates": [24, 46]}'
        assert extras['spatial_centroid'] == '{"type": "Point", "coordinates": [25, 47]}'

    def test_spatial_wkt_only(self):
        g = Graph()

        dataset = URIRef('http://example.org/datasets/1')
        g.add((dataset, RDF.type, DCAT.Dataset))

        spatial_uri = URIRef('http://geonames/Newark')
        g.add((dataset, DCT.spatial, spatial_uri))

        g.add((spatial_uri, RDF.type, DCT.Location))
        g.add((spatial_uri,
               LOCN.geometry,
               Literal('POINT (67 89)', datatype=GSP.wktLiteral)))
        g.add((spatial_uri,
               DCAT.bbox,
               Literal('POINT (68 90)', datatype=GSP.wktLiteral)))
        g.add((spatial_uri,
               DCAT.centroid,
               Literal('POINT (69 91)', datatype=GSP.wktLiteral)))

        p = RDFParser(profiles=DCAT_AP_PROFILES)

        p.g = g

        datasets = [d for d in p.datasets()]

        extras = self._extras(datasets[0])
        # NOTE: geomet returns floats for coordinates on WKT -> GeoJSON
        assert extras['spatial'] == '{"type": "Point", "coordinates": [67.0, 89.0]}'
        assert extras['spatial_bbox'] == '{"type": "Point", "coordinates": [68.0, 90.0]}'
        assert extras['spatial_centroid'] == '{"type": "Point", "coordinates": [69.0, 91.0]}'

    def test_spatial_wrong_geometries(self):
        g = Graph()

        dataset = URIRef('http://example.org/datasets/1')
        g.add((dataset, RDF.type, DCAT.Dataset))

        spatial_uri = URIRef('http://geonames/Newark')
        g.add((dataset, DCT.spatial, spatial_uri))

        g.add((spatial_uri, RDF.type, DCT.Location))
        g.add((spatial_uri,
               LOCN.geometry,
               Literal('Not GeoJSON', datatype=GEOJSON_IMT)))
        g.add((spatial_uri,
               LOCN.geometry,
               Literal('Not WKT', datatype=GSP.wktLiteral)))
        g.add((spatial_uri,
               DCAT.bbox,
               Literal('Not GeoJSON', datatype=GEOJSON_IMT)))
        g.add((spatial_uri,
               DCAT.bbox,
               Literal('Not WKT', datatype=GSP.wktLiteral)))
        g.add((spatial_uri,
               DCAT.centroid,
               Literal('Not GeoJSON', datatype=GEOJSON_IMT)))
        g.add((spatial_uri,
               DCAT.centroid,
               Literal('Not WKT', datatype=GSP.wktLiteral)))

        p = RDFParser(profiles=DCAT_AP_PROFILES)

        p.g = g

        datasets = [d for d in p.datasets()]

        extras = self._extras(datasets[0])

        assert 'spatial' not in extras
        assert 'spatial_bbox' not in extras
        assert 'spatial_centroid' not in extras

    def test_spatial_literal_only(self):
        g = Graph()

        dataset = URIRef('http://example.org/datasets/1')
        g.add((dataset, RDF.type, DCAT.Dataset))

        g.add((dataset, DCT.spatial, Literal('Newark')))

        p = RDFParser(profiles=DCAT_AP_PROFILES)

        p.g = g

        datasets = [d for d in p.datasets()]

        extras = self._extras(datasets[0])

        assert extras['spatial_text'] == 'Newark'
        assert 'spatial_uri' not in extras
        assert 'spatial' not in extras
        assert 'spatial_bbox' not in extras
        assert 'spatial_centroid' not in extras

    def test_spatial_uri_only(self):
        g = Graph()

        dataset = URIRef('http://example.org/datasets/1')
        g.add((dataset, RDF.type, DCAT.Dataset))

        spatial_uri = URIRef('http://geonames/Newark')
        g.add((dataset, DCT.spatial, spatial_uri))
        p = RDFParser(profiles=DCAT_AP_PROFILES)

        p.g = g

        datasets = [d for d in p.datasets()]

        extras = self._extras(datasets[0])

        assert extras['spatial_uri'] == 'http://geonames/Newark'
        assert 'spatial_text' not in extras
        assert 'spatial' not in extras
        assert 'spatial_bbox' not in extras
        assert 'spatial_centroid' not in extras
