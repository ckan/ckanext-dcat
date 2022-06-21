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
from ckanext.dcat.profiles import (DCAT, DCT, ADMS, XSD, VCARD, FOAF, SCHEMA,
                                   SKOS, LOCN, GSP, OWL, SPDX, GEOJSON_IMT)
from ckanext.dcat.utils import DCAT_EXPOSE_SUBCATALOGS
from ckanext.dcat.tests.utils import BaseSerializeTest

DCAT_AP_2_PROFILE = 'euro_dcat_ap_2'
DCAT_AP_PROFILES = [DCAT_AP_2_PROFILE]


class TestEuroDCATAP2ProfileSerializeDataset(BaseSerializeTest):

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
