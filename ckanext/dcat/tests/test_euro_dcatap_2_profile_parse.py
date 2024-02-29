# -*- coding: utf-8 -*-

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

    def test_dataset_all_fields(self):

        temporal_resolution = 'P1D'
        spatial_resolution_in_meters = 30
        isreferencedby_uri = 'https://doi.org/10.1038/sdata.2018.22'
        temporal_start = '1905-03-01T03:00:00+02:00'
        temporal_end = '2013-01-05'
        dist_availability = "http://publications.europa.eu/resource/authority/planned-availability/AVAILABLE"
        compress_format = "http://www.iana.org/assignments/media-types/application/gzip"
        package_format = 'http://publications.europa.eu/resource/authority/file-type/TAR'
        applicable_legislation = 'http://data.europa.eu/eli/reg_impl/2023/138/oj'
        hvd_category = 'http://data.europa.eu/bna/c_164e0bf5'

        data = '''<?xml version="1.0" encoding="utf-8" ?>
        <rdf:RDF
         xmlns:dct="http://purl.org/dc/terms/"
         xmlns:dcat="http://www.w3.org/ns/dcat#"
         xmlns:dcatap="http://data.europa.eu/r5r/"
         xmlns:schema="http://schema.org/"
         xmlns:time="http://www.w3.org/2006/time"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
        <dcat:Dataset rdf:about="http://example.org">
            <dct:temporal>
                <dct:PeriodOfTime>
                    <dcat:startDate rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime">{start}</dcat:startDate>
                    <dcat:endDate rdf:datatype="http://www.w3.org/2001/XMLSchema#date">{end}</dcat:endDate>
                </dct:PeriodOfTime>
            </dct:temporal>
            <dcatap:applicableLegislation rdf:resource="{applicable_legislation}"/>
            <dcatap:hvdCategory rdf:resource="{hvd_category}"/>
            <dcat:temporalResolution rdf:datatype="http://www.w3.org/2001/XMLSchema#duration">{temp_res}</dcat:temporalResolution>
            <dcat:spatialResolutionInMeters rdf:datatype="http://www.w3.org/2001/XMLSchema#decimal">{spatial_res}</dcat:spatialResolutionInMeters>
            <dct:isReferencedBy rdf:resource="{referenced_by}"/>
            <dcat:distribution>
                <dcat:Distribution rdf:about="https://data.some.org/catalog/datasets/9df8df51-63db-37a8-e044-0003ba9b0d98/1">
                    <dcat:accessURL rdf:resource="http://geodienste.hamburg.de/darf_nicht_die_gleiche_url_wie_downloadurl_sein_da_es_sonst_nicht_angezeigt_wird"/>
                    <dct:description>Das ist eine deutsche Beschreibung der Distribution</dct:description>
                    <dct:issued rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2017-02-27</dct:issued>
                    <dct:title>Download WFS Naturräume Geest und Marsch (GML)</dct:title>
                    <dct:modified rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime">2017-03-07T10:00:00</dct:modified>
                    <dcatap:availability rdf:resource="{availability}"/>
                    <dcat:compressFormat rdf:resource="{compressFormat}"/>
                    <dcat:packageFormat rdf:resource="{packageFormat}"/>
                    <dcatap:applicableLegislation rdf:resource="{applicable_legislation}"/>
                    <dcat:accessService>
                        <dcat:DataService>
                            <dcatap:availability rdf:resource="http://publications.europa.eu/resource/authority/planned-availability/AVAILABLE"/>
                            <dct:title>Sparql-end Point</dct:title>
                            <dcat:endpointURL rdf:resource="http://publications.europa.eu/webapi/rdf/sparql"/>
                            <dct:description>This SPARQL end point allow to directly query the EU Whoiswho content (organization / membership / person)</dct:description>
                            <dcat:endpointDescription>SPARQL url description</dcat:endpointDescription>
                            <dct:license rdf:resource="http://publications.europa.eu/resource/authority/licence/COM_REUSE"/>
                            <dct:accessRights rdf:resource="http://publications.europa.eu/resource/authority/access-right/PUBLIC"/>
                        </dcat:DataService>
                    </dcat:accessService>
                </dcat:Distribution>
            </dcat:distribution>
        </dcat:Dataset>
        </rdf:RDF>
        '''.format(start=temporal_start, end=temporal_end, temp_res=temporal_resolution,
                   spatial_res=spatial_resolution_in_meters, referenced_by=isreferencedby_uri,
                   availability=dist_availability, compressFormat=compress_format,
                   packageFormat=package_format, applicable_legislation=applicable_legislation,
                   hvd_category=hvd_category)

        p = RDFParser(profiles=DCAT_AP_PROFILES)

        p.parse(data)

        datasets = [d for d in p.datasets()]

        assert len(datasets) == 1

        dataset = datasets[0]

        # Dataset
        extras = self._extras(dataset)

        temporal_resolution_list = json.loads(extras['temporal_resolution'])
        assert len(temporal_resolution_list) == 1
        assert temporal_resolution in temporal_resolution_list

        spatial_resolution_list = json.loads(extras['spatial_resolution_in_meters'])
        assert len(spatial_resolution_list) == 1
        assert spatial_resolution_in_meters in spatial_resolution_list

        isreferencedby_list = json.loads(extras['is_referenced_by'])
        assert len(isreferencedby_list) == 1
        assert isreferencedby_uri in isreferencedby_list

        assert extras['temporal_start'] == temporal_start
        assert extras['temporal_end'] == temporal_end

        applicable_legislation_list = json.loads(extras['applicable_legislation'])
        assert len(applicable_legislation_list) == 1
        assert applicable_legislation in applicable_legislation_list

        hvd_category_list = json.loads(extras['hvd_category'])
        assert len(hvd_category_list) == 1
        assert hvd_category in hvd_category_list

        # Resources
        assert len(dataset['resources']) == 1

        resource = dataset['resources'][0]

        # Simple values
        assert resource['availability'] == dist_availability
        assert resource['compress_format'] == compress_format
        assert resource['package_format'] == package_format

        # List values
        dist_applicable_legislation_list = json.loads(resource.get('applicable_legislation'))
        assert dist_applicable_legislation_list == applicable_legislation_list

        # Access services
        access_service_list = json.loads(resource.get('access_services'))
        assert len(access_service_list) == 1

        access_service = access_service_list[0]

        # Simple values
        assert access_service.get('availability') == 'http://publications.europa.eu/resource/authority/planned-availability/AVAILABLE'
        assert access_service.get('title') == 'Sparql-end Point'
        assert access_service.get('endpoint_description') == 'SPARQL url description'
        assert access_service.get('license') == 'http://publications.europa.eu/resource/authority/licence/COM_REUSE'
        assert access_service.get('access_rights') == 'http://publications.europa.eu/resource/authority/access-right/PUBLIC'
        assert access_service.get('description') == 'This SPARQL end point allow to directly query the EU Whoiswho content (organization / membership / person)'

        # List
        endpoint_url_list = access_service.get('endpoint_url')
        assert len(endpoint_url_list) == 1
        assert 'http://publications.europa.eu/webapi/rdf/sparql' in endpoint_url_list

    def test_availability_distibutions_without_uri(self):

        dist_availability = "http://publications.europa.eu/resource/authority/planned-availability/AVAILABLE"

        data = '''<?xml version="1.0" encoding="utf-8" ?>
        <rdf:RDF
         xmlns:dct="http://purl.org/dc/terms/"
         xmlns:dcat="http://www.w3.org/ns/dcat#"
         xmlns:dcatap="http://data.europa.eu/r5r/"
         xmlns:schema="http://schema.org/"
         xmlns:time="http://www.w3.org/2006/time"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
        <dcat:Dataset rdf:about="http://example.org">
            <dcat:distribution>
                <dcat:Distribution>
                    <dcat:accessURL rdf:resource="http://geodienste.hamburg.de/darf_nicht_die_gleiche_url_wie_downloadurl_sein_da_es_sonst_nicht_angezeigt_wird"/>
                    <dct:description>Das ist eine deutsche Beschreibung der Distribution</dct:description>
                    <dct:issued rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2017-02-27</dct:issued>
                    <dct:title>Download WFS Naturräume Geest und Marsch (GML)</dct:title>
                    <dct:modified rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime">2017-03-07T10:00:00</dct:modified>
                    <dcatap:availability rdf:resource="{availability}"/>
                </dcat:Distribution>
            </dcat:distribution>
        </dcat:Dataset>
        </rdf:RDF>
        '''.format(availability=dist_availability)

        p = RDFParser(profiles=DCAT_AP_PROFILES)

        p.parse(data)

        datasets = [d for d in p.datasets()]

        assert len(datasets) == 1

        dataset = datasets[0]

        assert len(dataset['resources']) == 1

        resource = dataset['resources'][0]

        assert resource['availability'] == dist_availability

    def test_availability_multiple_distibutions(self):

        dist_availability_1 = "http://publications.europa.eu/resource/authority/planned-availability/AVAILABLE"
        dist_availability_2 = "http://publications.europa.eu/resource/authority/planned-availability/EXPERIMENTAL"
        dist_availability_3 = "http://publications.europa.eu/resource/authority/planned-availability/STABLE"

        data = '''<?xml version="1.0" encoding="utf-8" ?>
        <rdf:RDF
         xmlns:dct="http://purl.org/dc/terms/"
         xmlns:dcat="http://www.w3.org/ns/dcat#"
         xmlns:dcatap="http://data.europa.eu/r5r/"
         xmlns:schema="http://schema.org/"
         xmlns:time="http://www.w3.org/2006/time"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
        <dcat:Dataset rdf:about="http://example.org">
            <dcat:distribution>
                <dcat:Distribution>
                    <dcat:accessURL rdf:resource="http://geodienste.hamburg.de/darf_nicht_die_gleiche_url_wie_downloadurl_sein_da_es_sonst_nicht_angezeigt_wird"/>
                    <dct:description>{availability_1}</dct:description>
                    <dct:issued rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2017-02-27</dct:issued>
                    <dct:title>Download WFS Naturräume Geest und Marsch (GML)</dct:title>
                    <dct:modified rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime">2017-03-07T10:00:00</dct:modified>
                    <dcatap:availability rdf:resource="{availability_1}"/>
                </dcat:Distribution>
            </dcat:distribution>
            <dcat:distribution>
                <dcat:Distribution rdf:about="https://data.some.org/catalog/datasets/9df8df51-63db-37a8-e044-0003ba9b0d98/1">
                    <dcat:accessURL rdf:resource="http://geodienste.hamburg.de/darf_nicht_die_gleiche_url_wie_downloadurl_sein_da_es_sonst_nicht_angezeigt_wird"/>
                    <dct:description>{availability_2}</dct:description>
                    <dct:issued rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2017-02-27</dct:issued>
                    <dct:title>Download WFS Naturräume Geest und Marsch (GML)</dct:title>
                    <dct:modified rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime">2017-03-07T10:00:00</dct:modified>
                    <dcatap:availability rdf:resource="{availability_2}"/>
                </dcat:Distribution>
            </dcat:distribution>
            <dcat:distribution>
                <dcat:Distribution>
                    <dcat:accessURL rdf:resource="http://geodienste.hamburg.de/darf_nicht_die_gleiche_url_wie_downloadurl_sein_da_es_sonst_nicht_angezeigt_wird"/>
                    <dct:description>{availability_3}</dct:description>
                    <dct:issued rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2017-02-27</dct:issued>
                    <dct:title>Download WFS Naturräume Geest und Marsch (GML)</dct:title>
                    <dct:modified rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime">2017-03-07T10:00:00</dct:modified>
                    <dcatap:availability rdf:resource="{availability_3}"/>
                </dcat:Distribution>
            </dcat:distribution>
        </dcat:Dataset>
        </rdf:RDF>
        '''.format(availability_1=dist_availability_1, availability_2=dist_availability_2,
                   availability_3=dist_availability_3)

        p = RDFParser(profiles=DCAT_AP_PROFILES)

        p.parse(data)

        datasets = [d for d in p.datasets()]

        assert len(datasets) == 1

        dataset = datasets[0]

        assert len(dataset['resources']) == 3

        for resource in dataset['resources']:
            assert resource['availability'] == resource['description']

    def test_dataset_all_fields_literal(self):

        dist_availability = "AVAILABLE"
        compress_format = "gzip"
        package_format = "TAR"

        data = '''<?xml version="1.0" encoding="utf-8" ?>
        <rdf:RDF
         xmlns:dct="http://purl.org/dc/terms/"
         xmlns:dcat="http://www.w3.org/ns/dcat#"
         xmlns:dcatap="http://data.europa.eu/r5r/"
         xmlns:schema="http://schema.org/"
         xmlns:time="http://www.w3.org/2006/time"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
        <dcat:Dataset rdf:about="http://example.org">
            <dcat:distribution>
                <dcat:Distribution>
                    <dcat:accessURL rdf:resource="http://geodienste.hamburg.de/darf_nicht_die_gleiche_url_wie_downloadurl_sein_da_es_sonst_nicht_angezeigt_wird"/>
                    <dct:description>Das ist eine deutsche Beschreibung der Distribution</dct:description>
                    <dct:issued rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2017-02-27</dct:issued>
                    <dct:title>Download WFS Naturräume Geest und Marsch (GML)</dct:title>
                    <dct:modified rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime">2017-03-07T10:00:00</dct:modified>
                    <dcatap:availability>{availability}</dcatap:availability>
                    <dcat:compressFormat rdf:resource="{compressFormat}"/>
                    <dcat:packageFormat rdf:resource="{packageFormat}"/>
                </dcat:Distribution>
            </dcat:distribution>
        </dcat:Dataset>
        </rdf:RDF>
        '''.format(availability=dist_availability, compressFormat=compress_format,
                   packageFormat=package_format)

        p = RDFParser(profiles=DCAT_AP_PROFILES)

        p.parse(data)

        datasets = [d for d in p.datasets()]

        assert len(datasets) == 1

        dataset = datasets[0]

        assert len(dataset['resources']) == 1

        resource = dataset['resources'][0]

        assert resource['availability'] == dist_availability
        assert resource['compress_format'] == compress_format
        assert resource['package_format'] == package_format

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

    def test_isreferencedby_multiple(self):
        g = Graph()

        dataset = URIRef('http://example.org/datasets/1')
        g.add((dataset, RDF.type, DCAT.Dataset))

        isreferencedby_uri = 'https://doi.org/10.1038/sdata.2018.22'
        g.add((dataset, DCT.isReferencedBy, URIRef(isreferencedby_uri)))

        isreferencedby_uri_2 = 'https://doi.org/10.1093/ajae/aaq063'
        g.add((dataset, DCT.isReferencedBy, URIRef(isreferencedby_uri_2)))

        p = RDFParser(profiles=DCAT_AP_PROFILES)

        p.g = g

        datasets = [d for d in p.datasets()]

        extras = self._extras(datasets[0])

        isreferencedby_list = json.loads(extras['is_referenced_by'])
        assert len(isreferencedby_list) == 2
        assert isreferencedby_uri in isreferencedby_list
        assert isreferencedby_uri_2 in isreferencedby_list

    def test_high_value_datasets(self):
        applicable_legislation = 'http://data.europa.eu/eli/reg_impl/2023/138/oj'
        applicable_legislation_alt = 'http://data.europa.eu/eli/reg_impl/2023/138/oj_alt'
        hvd_category = 'http://data.europa.eu/bna/c_164e0bf5'
        hvd_category_alt = 'http://data.europa.eu/bna/c_ac64a52d'

        data = '''<?xml version="1.0" encoding="utf-8" ?>
        <rdf:RDF
         xmlns:dct="http://purl.org/dc/terms/"
         xmlns:dcat="http://www.w3.org/ns/dcat#"
         xmlns:dcatap="http://data.europa.eu/r5r/"
         xmlns:schema="http://schema.org/"
         xmlns:time="http://www.w3.org/2006/time"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
        <dcat:Dataset rdf:about="http://example.org">
            <dcatap:applicableLegislation rdf:resource="{applicable_legislation}"/>
            <dcatap:applicableLegislation>{applicable_legislation_alt}</dcatap:applicableLegislation>
            <dcatap:hvdCategory rdf:resource="{hvd_category}"/>
            <dcatap:hvdCategory>{hvd_category_alt}</dcatap:hvdCategory>
            <dcat:distribution>
                <dcat:Distribution rdf:about="https://data.some.org/catalog/datasets/9df8df51-63db-37a8-e044-0003ba9b0d98/1">
                    <dcatap:applicableLegislation rdf:resource="{applicable_legislation}"/>
                    <dcatap:applicableLegislation>{applicable_legislation_alt}</dcatap:applicableLegislation>
                </dcat:Distribution>
            </dcat:distribution>
        </dcat:Dataset>
        </rdf:RDF>
        '''.format(applicable_legislation=applicable_legislation, applicable_legislation_alt=applicable_legislation_alt,
                   hvd_category=hvd_category, hvd_category_alt=hvd_category_alt)

        p = RDFParser(profiles=DCAT_AP_PROFILES)

        p.parse(data)

        datasets = [d for d in p.datasets()]
        assert len(datasets) == 1

        dataset = datasets[0]

        # Dataset
        extras = self._extras(dataset)

        applicable_legislation_list = json.loads(extras['applicable_legislation'])
        assert len(applicable_legislation_list) == 2
        assert applicable_legislation in applicable_legislation_list
        assert applicable_legislation_alt in applicable_legislation_list

        hvd_category_list = json.loads(extras['hvd_category'])
        assert len(hvd_category_list) == 2
        assert hvd_category in hvd_category_list
        assert hvd_category_alt in hvd_category_list

        # Resources
        assert len(dataset['resources']) == 1

        resource = dataset['resources'][0]

        dist_applicable_legislation_list = [applicable_legislation, applicable_legislation_alt]
        assert dist_applicable_legislation_list == applicable_legislation_list

    def test_parse_distribution_access_service(self):

        expected_access_services = [{
            'availability': 'http://publications.europa.eu/resource/authority/planned-availability/AVAILABLE',
            'title': 'Sparql-end Point',
            'endpoint_description': 'SPARQL url description',
            'license': 'http://publications.europa.eu/resource/authority/licence/COM_REUSE',
            'access_rights': 'http://publications.europa.eu/resource/authority/access-right/PUBLIC',
            'description': 'This SPARQL end point allow to directly query the EU Whoiswho content',
            'endpoint_url': ['http://publications.europa.eu/webapi/rdf/sparql'],
            'serves_dataset': ['http://data.europa.eu/88u/dataset/eu-whoiswho-the-official-directory-of-the-european-union'],
            'uri': ''
            }, {
            'availability': 'http://publications.europa.eu/resource/authority/planned-availability/EXPERIMENTAL',
            'title': 'Sparql-end Point 2',
            'endpoint_description': 'SPARQL url description 2',
            'license': 'http://publications.europa.eu/resource/authority/licence/CC_BY',
            'access_rights': 'http://publications.europa.eu/resource/authority/access-right/OP_DATPRO',
            'description': 'This SPARQL end point allow to directly query the EU Whoiswho content',
            'endpoint_url': ['http://publications.europa.eu/webapi/rdf/sparql'],
            'serves_dataset': ['http://data.europa.eu/88u/dataset/eu-whoiswho-the-official-directory-of-the-european-union'],
            'uri': ''
        }]

        self._run_parse_access_service(expected_access_services)

    def test_parse_distribution_access_service_literal(self):

        expected_access_services = [{
            'availability': 'http://publications.europa.eu/resource/authority/planned-availability/AVAILABLE',
            'title': 'Sparql-end Point',
            'endpoint_description': 'SPARQL url description',
            'license': 'COM_REUSE',
            'access_rights': 'PUBLIC',
            'description': 'This SPARQL end point allow to directly query the EU Whoiswho content',
            'endpoint_url': ['sparql'],
            'serves_dataset': ['eu-whoiswho-the-official-directory-of-the-european-union'],
            'uri': ''
            }, {
            'availability': 'EXPERIMENTAL',
            'title': 'Sparql-end Point 2',
            'endpoint_description': 'SPARQL url description 2',
            'license': 'CC_BY',
            'access_rights': 'OP_DATPRO',
            'description': 'This SPARQL end point allow to directly query the EU Whoiswho content',
            'endpoint_url': ['sparql'],
            'serves_dataset': ['eu-whoiswho-the-official-directory-of-the-european-union'],
            'uri': ''
        }]

        self._run_parse_access_service(expected_access_services)

    def test_dataset_distribution_access_service_list_values_only(self):

        data = '''<?xml version="1.0" encoding="utf-8" ?>
        <rdf:RDF
         xmlns:dct="http://purl.org/dc/terms/"
         xmlns:dcat="http://www.w3.org/ns/dcat#"
         xmlns:dcatap="http://data.europa.eu/r5r/"
         xmlns:schema="http://schema.org/"
         xmlns:time="http://www.w3.org/2006/time"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
        <dcat:Dataset rdf:about="http://example.org">
            <dcat:distribution>
                <dcat:Distribution rdf:about="https://data.some.org/catalog/datasets/9df8df51-63db-37a8-e044-0003ba9b0d98/1">
                    <dct:description>Das ist eine deutsche Beschreibung der Distribution</dct:description>
                    <dct:title>Download WFS Naturräume Geest und Marsch (GML)</dct:title>
                    <dcat:accessService>
                        <dcat:DataService>
                            <dcat:endpointURL rdf:resource="http://publications.europa.eu/webapi/rdf/sparql"/>
                            <dcat:servesDataset rdf:resource="http://example.org" />
                        </dcat:DataService>
                    </dcat:accessService>
                </dcat:Distribution>
            </dcat:distribution>
        </dcat:Dataset>
        </rdf:RDF>
        '''

        p = RDFParser(profiles=DCAT_AP_PROFILES)

        p.parse(data)

        datasets = [d for d in p.datasets()]

        assert len(datasets) == 1

        dataset = datasets[0]

        # Resources
        assert len(dataset['resources']) == 1

        resource = dataset['resources'][0]

        # Access services
        access_service_list = json.loads(resource.get('access_services'))
        assert len(access_service_list) == 1

        access_service = access_service_list[0]

        # List
        endpoint_url_list = access_service.get('endpoint_url')
        print(access_service)
        assert len(endpoint_url_list) == 1
        assert 'http://publications.europa.eu/webapi/rdf/sparql' in endpoint_url_list

        serves_dataset_list = access_service.get('serves_dataset')
        assert len(serves_dataset_list) == 1
        assert 'http://example.org' in serves_dataset_list

    def _build_access_services_graph_from_list(self, access_service_list):
        """
        Creates an access service graph based on the given list.
        :param: access_service_list
            dict list of the access services
        :returns:
            The access service graph
        """
        service_graph = ''
        for access_service_dict in access_service_list:
            #Lists
            endpoint_urls = access_service_dict.get('endpoint_url', [])
            endpoint_url_string = ''
            for endpoint_url in  endpoint_urls:
                endpoint_url_string += ('<dcat:endpointURL rdf:resource="{ds_endpointURL}"/>'
                                        .format(ds_endpointURL = endpoint_url))


            serves_datasets = access_service_dict.get('serves_dataset', [])
            serves_dataset_string = ''
            for serves_dataset in  serves_datasets:
                serves_dataset_string += ('<dcat:servesDataset rdf:resource="{ds_servesDataset}"/>'
                                          .format(ds_servesDataset = serves_dataset))

            data = '''
            <dcat:accessService>
                <dcat:DataService>
                    <dcatap:availability rdf:resource="{ds_availability}"/>
                    <dct:title>{ds_title}</dct:title>
                    {ds_endpointURL}
                    <dct:description>{ds_description}</dct:description>
                    <dcat:endpointDescription>{ds_endpointDescription}</dcat:endpointDescription>
                    <dct:license>{ds_license}</dct:license>
                    <dct:accessRights>{ds_accessRights}</dct:accessRights>
                    {ds_servesDataset}
                </dcat:DataService>
            </dcat:accessService>
            '''.format(ds_availability = access_service_dict.get('availability'),
                       ds_title = access_service_dict.get('title'), ds_endpointURL = endpoint_url_string,
                       ds_description = access_service_dict.get('description'), ds_endpointDescription = access_service_dict.get('endpoint_description'),
                       ds_accessRights = access_service_dict.get('access_rights'), ds_license = access_service_dict.get('license'),
                       ds_servesDataset = serves_dataset_string)

            service_graph += data

        return service_graph

    def _run_parse_access_service(self, expected_access_services):
        """
        Creates a minimal graph with access services based on the given list and checks
        if the expected access services are present in the parsed resource dict.
        """
        access_services_graph = self._build_access_services_graph_from_list(expected_access_services)

        data = '''<?xml version="1.0" encoding="utf-8" ?>
        <rdf:RDF
         xmlns:dct="http://purl.org/dc/terms/"
         xmlns:dcat="http://www.w3.org/ns/dcat#"
         xmlns:dcatap="http://data.europa.eu/r5r/"
         xmlns:schema="http://schema.org/"
         xmlns:time="http://www.w3.org/2006/time"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
        <dcat:Dataset rdf:about="http://example.org">
            <dcat:distribution>
                <dcat:Distribution rdf:about="https://data.some.org/catalog/datasets/9df8df51-63db-37a8-e044-0003ba9b0d98/1">
                    <dct:description>Das ist eine deutsche Beschreibung der Distribution</dct:description>
                    <dct:title>Download WFS Naturräume Geest und Marsch (GML)</dct:title>
                    {access_services}
                </dcat:Distribution>
            </dcat:distribution>
        </dcat:Dataset>
        </rdf:RDF>
        '''.format(access_services = access_services_graph)

        p = RDFParser(profiles=DCAT_AP_PROFILES)

        p.parse(data)

        datasets = [d for d in p.datasets()]

        assert len(datasets) == 1
        dataset = datasets[0]

        resources = dataset.get('resources')
        assert len(resources) == 1
        resource_dict = resources[0]

        access_services = resource_dict.get('access_services')
        access_services_list = json.loads(access_services)
        assert len(access_services_list) == 2

        for access_service in access_services_list:
            assert access_service.get('access_service_ref')
            access_service.pop('access_service_ref')
            assert access_service in expected_access_services

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
