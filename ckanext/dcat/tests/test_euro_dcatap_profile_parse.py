import os
import json

import nose

from ckantoolkit import config

from rdflib import Graph, URIRef, BNode, Literal
from rdflib.namespace import RDF

from ckan.plugins import toolkit

from ckantoolkit.tests import helpers, factories

from ckanext.dcat.processors import RDFParser, RDFSerializer
from ckanext.dcat.profiles import (DCAT, DCT, ADMS, LOCN, SKOS, GSP, RDFS,
                                   GEOJSON_IMT)
from ckanext.dcat.utils import DCAT_EXPOSE_SUBCATALOGS, DCAT_CLEAN_TAGS

eq_ = nose.tools.eq_
assert_true = nose.tools.assert_true


class BaseParseTest(object):

    def _extras(self, dataset):
        extras = {}
        for extra in dataset.get('extras'):
            extras[extra['key']] = extra['value']
        return extras

    def _get_file_contents(self, file_name):
        path = os.path.join(os.path.dirname(__file__),
                            '..', '..', '..', 'examples',
                            file_name)
        with open(path, 'r') as f:
            return f.read()


class TestEuroDCATAPProfileParsing(BaseParseTest):

    def test_dataset_all_fields(self):

        contents = self._get_file_contents('dataset.rdf')

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.parse(contents)

        datasets = [d for d in p.datasets()]

        eq_(len(datasets), 1)

        dataset = datasets[0]

        # Basic fields

        eq_(dataset['title'], u'Zimbabwe Regional Geochemical Survey.')
        eq_(dataset['notes'], u'During the period 1982-86 a team of geologists from the British Geological Survey ...')
        eq_(dataset['url'], 'http://dataset.info.org')
        eq_(dataset['version'], '2.3')
        eq_(dataset['license_id'], 'cc-nc')

        # Tags

        eq_(sorted(dataset['tags'], key=lambda k: k['name']), [{'name': u'exploration'},
                                                               {'name': u'geochemistry'},
                                                               {'name': u'geology'}])
        # Extras

        def _get_extra_value(key):
            v = [extra['value'] for extra in dataset['extras'] if extra['key'] == key]
            return v[0] if v else None

        def _get_extra_value_as_list(key):
            value = _get_extra_value(key)
            return json.loads(value) if value else []

        #  Simple values
        eq_(_get_extra_value('issued'), u'2012-05-10')
        eq_(_get_extra_value('modified'), u'2012-05-10T21:04:00')
        eq_(_get_extra_value('identifier'), u'9df8df51-63db-37a8-e044-0003ba9b0d98')
        eq_(_get_extra_value('version_notes'), u'New schema added')
        eq_(_get_extra_value('temporal_start'), '1905-03-01')
        eq_(_get_extra_value('temporal_end'), '2013-01-05')
        eq_(_get_extra_value('frequency'), 'http://purl.org/cld/freq/daily')
        eq_(_get_extra_value('spatial_uri'), 'http://publications.europa.eu/mdr/authority/country/ZWE')
        eq_(_get_extra_value('publisher_uri'), 'http://orgs.vocab.org/some-org')
        eq_(_get_extra_value('publisher_name'), 'Publishing Organization for dataset 1')
        eq_(_get_extra_value('publisher_email'), 'contact@some.org')
        eq_(_get_extra_value('publisher_url'), 'http://some.org')
        eq_(_get_extra_value('publisher_type'), 'http://purl.org/adms/publishertype/NonProfitOrganisation')
        eq_(_get_extra_value('contact_name'), 'Point of Contact')
        eq_(_get_extra_value('contact_email'), 'mailto:contact@some.org')
        eq_(_get_extra_value('access_rights'), 'public')
        eq_(_get_extra_value('provenance'), 'Some statement about provenance')
        eq_(_get_extra_value('dcat_type'), 'test-type')

        #  Lists
        eq_(sorted(_get_extra_value_as_list('language')), [u'ca', u'en', u'es'])
        eq_(sorted(_get_extra_value_as_list('theme')), [u'Earth Sciences',
                                                        u'http://eurovoc.europa.eu/100142',
                                                        u'http://eurovoc.europa.eu/209065'])
        eq_(sorted(_get_extra_value_as_list('conforms_to')), [u'Standard 1', u'Standard 2'])

        eq_(sorted(_get_extra_value_as_list('alternate_identifier')), [u'alternate-identifier-1', u'alternate-identifier-2'])
        eq_(sorted(_get_extra_value_as_list('documentation')), [u'http://dataset.info.org/doc1',
                                                                u'http://dataset.info.org/doc2'])
        eq_(sorted(_get_extra_value_as_list('related_resource')), [u'http://dataset.info.org/related1',
                                                                   u'http://dataset.info.org/related2'])
        eq_(sorted(_get_extra_value_as_list('has_version')), [u'https://data.some.org/catalog/datasets/derived-dataset-1',
                                                              u'https://data.some.org/catalog/datasets/derived-dataset-2'])
        eq_(sorted(_get_extra_value_as_list('is_version_of')), [u'https://data.some.org/catalog/datasets/original-dataset'])
        eq_(sorted(_get_extra_value_as_list('source')), [u'https://data.some.org/catalog/datasets/source-dataset-1',
                                                         u'https://data.some.org/catalog/datasets/source-dataset-2'])
        eq_(sorted(_get_extra_value_as_list('sample')), [u'https://data.some.org/catalog/datasets/9df8df51-63db-37a8-e044-0003ba9b0d98/sample'])

        # Dataset URI
        eq_(_get_extra_value('uri'), u'https://data.some.org/catalog/datasets/9df8df51-63db-37a8-e044-0003ba9b0d98')

        # Resources
        eq_(len(dataset['resources']), 1)

        resource = dataset['resources'][0]

        #  Simple values
        eq_(resource['name'], u'Some website')
        eq_(resource['description'], u'A longer description')
        eq_(resource['format'], u'HTML')
        eq_(resource['mimetype'], u'text/html')
        eq_(resource['issued'], u'2012-05-11')
        eq_(resource['modified'], u'2012-05-01T00:04:06')
        eq_(resource['status'], u'http://purl.org/adms/status/Completed')

        eq_(resource['hash'], u'4304cf2e751e6053c90b1804c89c0ebb758f395a')
        eq_(resource['hash_algorithm'], u'http://spdx.org/rdf/terms#checksumAlgorithm_sha1')

        # Lists
        for item in [
            ('documentation', [u'http://dataset.info.org/distribution1/doc1', u'http://dataset.info.org/distribution1/doc2']),
            ('language', [u'ca', u'en', u'es']),
            ('conforms_to', [u'Standard 1', u'Standard 2']),
        ]:
            eq_(sorted(json.loads(resource[item[0]])), item[1])

        # These two are likely to need clarification
        eq_(resource['license'], u'http://creativecommons.org/licenses/by-nc/2.0/')
        eq_(resource['rights'], u'Some statement about rights')

        eq_(resource['url'], u'http://www.bgs.ac.uk/gbase/geochemcd/home.html')
        assert 'download_url' not in resource

        eq_(resource['size'], 12323)

        # Distribution URI
        eq_(resource['uri'], u'https://data.some.org/catalog/datasets/9df8df51-63db-37a8-e044-0003ba9b0d98/1')

    # owl:versionInfo is tested on the test above
    def test_dataset_version_adms(self):
        g = Graph()

        dataset1 = URIRef("http://example.org/datasets/1")
        g.add((dataset1, RDF.type, DCAT.Dataset))

        g.add((dataset1, ADMS.version, Literal('2.3a')))

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        dataset = [d for d in p.datasets()][0]

        eq_(dataset['version'], u'2.3a')

    def test_dataset_license_from_distribution_by_uri(self):
        # license_id retrieved from the URI of dcat:license object
        g = Graph()

        dataset = URIRef("http://example.org/datasets/1")
        g.add((dataset, RDF.type, DCAT.Dataset))

        distribution = URIRef("http://example.org/datasets/1/ds/1")
        g.add((dataset, DCAT.distribution, distribution))
        g.add((distribution, RDF.type, DCAT.Distribution))
        g.add((distribution, DCT.license,
               URIRef("http://www.opendefinition.org/licenses/cc-by")))

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        dataset = [d for d in p.datasets()][0]
        eq_(dataset['license_id'], 'cc-by')

    def test_dataset_license_from_distribution_by_title(self):
        # license_id retrieved from dct:title of dcat:license object
        g = Graph()

        dataset = URIRef("http://example.org/datasets/1")
        g.add((dataset, RDF.type, DCAT.Dataset))

        distribution = URIRef("http://example.org/datasets/1/ds/1")
        g.add((distribution, RDF.type, DCAT.Distribution))
        g.add((dataset, DCAT.distribution, distribution))
        license = BNode()
        g.add((distribution, DCT.license, license))
        g.add((license, DCT.title, Literal("Creative Commons Attribution")))

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        dataset = [d for d in p.datasets()][0]
        eq_(dataset['license_id'], 'cc-by')

    def test_distribution_access_url(self):
        g = Graph()

        dataset1 = URIRef("http://example.org/datasets/1")
        g.add((dataset1, RDF.type, DCAT.Dataset))

        distribution1_1 = URIRef("http://example.org/datasets/1/ds/1")
        g.add((distribution1_1, RDF.type, DCAT.Distribution))
        g.add((distribution1_1, DCAT.accessURL, Literal('http://access.url.org')))
        g.add((dataset1, DCAT.distribution, distribution1_1))

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        datasets = [d for d in p.datasets()]

        resource = datasets[0]['resources'][0]

        eq_(resource['url'], u'http://access.url.org')
        assert 'download_url' not in resource

    def test_distribution_download_url(self):
        g = Graph()

        dataset1 = URIRef("http://example.org/datasets/1")
        g.add((dataset1, RDF.type, DCAT.Dataset))

        distribution1_1 = URIRef("http://example.org/datasets/1/ds/1")
        g.add((distribution1_1, RDF.type, DCAT.Distribution))
        g.add((distribution1_1, DCAT.downloadURL, Literal('http://download.url.org')))
        g.add((dataset1, DCAT.distribution, distribution1_1))

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        datasets = [d for d in p.datasets()]

        resource = datasets[0]['resources'][0]

        eq_(resource['url'], u'http://download.url.org')
        eq_(resource['download_url'], u'http://download.url.org')

    def test_distribution_both_access_and_download_url(self):
        g = Graph()

        dataset1 = URIRef("http://example.org/datasets/1")
        g.add((dataset1, RDF.type, DCAT.Dataset))

        distribution1_1 = URIRef("http://example.org/datasets/1/ds/1")
        g.add((distribution1_1, RDF.type, DCAT.Distribution))
        g.add((distribution1_1, DCAT.accessURL, Literal('http://access.url.org')))
        g.add((distribution1_1, DCAT.downloadURL, Literal('http://download.url.org')))
        g.add((dataset1, DCAT.distribution, distribution1_1))

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        datasets = [d for d in p.datasets()]

        resource = datasets[0]['resources'][0]

        eq_(resource['url'], u'http://access.url.org')
        eq_(resource['download_url'], u'http://download.url.org')

    def test_distribution_format_imt_and_format(self):
        g = Graph()

        dataset1 = URIRef("http://example.org/datasets/1")
        g.add((dataset1, RDF.type, DCAT.Dataset))

        distribution1_1 = URIRef("http://example.org/datasets/1/ds/1")
        g.add((distribution1_1, RDF.type, DCAT.Distribution))
        g.add((distribution1_1, DCAT.mediaType, Literal('text/csv')))
        g.add((distribution1_1, DCT['format'], Literal('CSV')))
        g.add((dataset1, DCAT.distribution, distribution1_1))

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        datasets = [d for d in p.datasets()]

        resource = datasets[0]['resources'][0]

        eq_(resource['format'], u'CSV')
        eq_(resource['mimetype'], u'text/csv')

    def test_distribution_format_format_only(self):
        g = Graph()

        dataset1 = URIRef("http://example.org/datasets/1")
        g.add((dataset1, RDF.type, DCAT.Dataset))

        distribution1_1 = URIRef("http://example.org/datasets/1/ds/1")
        g.add((distribution1_1, RDF.type, DCAT.Distribution))
        g.add((distribution1_1, DCT['format'], Literal('CSV')))
        g.add((dataset1, DCAT.distribution, distribution1_1))

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        datasets = [d for d in p.datasets()]

        resource = datasets[0]['resources'][0]

        eq_(resource['format'], u'CSV')

    def test_distribution_format_imt_only(self):
        g = Graph()

        dataset1 = URIRef("http://example.org/datasets/1")
        g.add((dataset1, RDF.type, DCAT.Dataset))

        distribution1_1 = URIRef("http://example.org/datasets/1/ds/1")
        g.add((distribution1_1, RDF.type, DCAT.Distribution))
        g.add((distribution1_1, DCAT.mediaType, Literal('text/csv')))
        g.add((dataset1, DCAT.distribution, distribution1_1))

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        datasets = [d for d in p.datasets()]

        resource = datasets[0]['resources'][0]
        if toolkit.check_ckan_version(min_version='2.3'):
            eq_(resource['format'], u'CSV')
            eq_(resource['mimetype'], u'text/csv')
        else:
            eq_(resource['format'], u'text/csv')

    @helpers.change_config('ckanext.dcat.normalize_ckan_format', False)
    def test_distribution_format_imt_only_normalize_false(self):
        g = Graph()

        dataset1 = URIRef("http://example.org/datasets/1")
        g.add((dataset1, RDF.type, DCAT.Dataset))

        distribution1_1 = URIRef("http://example.org/datasets/1/ds/1")
        g.add((distribution1_1, RDF.type, DCAT.Distribution))
        g.add((distribution1_1, DCAT.mediaType, Literal('text/csv')))
        g.add((dataset1, DCAT.distribution, distribution1_1))

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        datasets = [d for d in p.datasets()]

        resource = datasets[0]['resources'][0]

        eq_(resource['format'], u'text/csv')
        eq_(resource['mimetype'], u'text/csv')

    @helpers.change_config('ckanext.dcat.normalize_ckan_format', False)
    def test_distribution_format_format_only_normalize_false(self):
        g = Graph()

        dataset1 = URIRef("http://example.org/datasets/1")
        g.add((dataset1, RDF.type, DCAT.Dataset))

        distribution1_1 = URIRef("http://example.org/datasets/1/ds/1")
        g.add((distribution1_1, RDF.type, DCAT.Distribution))
        g.add((distribution1_1, DCT['format'], Literal('CSV')))
        g.add((dataset1, DCAT.distribution, distribution1_1))

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        datasets = [d for d in p.datasets()]

        resource = datasets[0]['resources'][0]

        eq_(resource['format'], u'CSV')
        assert 'mimetype' not in resource

    def test_distribution_format_unknown_imt(self):
        g = Graph()

        dataset1 = URIRef("http://example.org/datasets/1")
        g.add((dataset1, RDF.type, DCAT.Dataset))

        distribution1_1 = URIRef("http://example.org/datasets/1/ds/1")
        g.add((distribution1_1, RDF.type, DCAT.Distribution))
        g.add((distribution1_1, DCAT.mediaType, Literal('text/unknown-imt')))
        g.add((dataset1, DCAT.distribution, distribution1_1))

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        datasets = [d for d in p.datasets()]

        resource = datasets[0]['resources'][0]

        eq_(resource['format'], u'text/unknown-imt')
        eq_(resource['mimetype'], u'text/unknown-imt')

    def test_distribution_format_imt_normalized(self):
        g = Graph()

        dataset1 = URIRef("http://example.org/datasets/1")
        g.add((dataset1, RDF.type, DCAT.Dataset))

        distribution1_1 = URIRef("http://example.org/datasets/1/ds/1")
        g.add((distribution1_1, RDF.type, DCAT.Distribution))
        g.add((distribution1_1, DCAT.mediaType, Literal('text/unknown-imt')))
        g.add((dataset1, DCAT.distribution, distribution1_1))

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        datasets = [d for d in p.datasets()]

        resource = datasets[0]['resources'][0]

        eq_(resource['format'], u'text/unknown-imt')
        eq_(resource['mimetype'], u'text/unknown-imt')

    def test_distribution_format_format_normalized(self):
        g = Graph()

        dataset1 = URIRef("http://example.org/datasets/1")
        g.add((dataset1, RDF.type, DCAT.Dataset))

        distribution1_1 = URIRef("http://example.org/datasets/1/ds/1")
        g.add((distribution1_1, RDF.type, DCAT.Distribution))
        g.add((distribution1_1, DCAT.mediaType, Literal('text/csv')))
        g.add((distribution1_1, DCT['format'], Literal('Comma Separated Values')))
        g.add((dataset1, DCAT.distribution, distribution1_1))

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        datasets = [d for d in p.datasets()]

        resource = datasets[0]['resources'][0]

        if toolkit.check_ckan_version(min_version='2.3'):
            eq_(resource['format'], u'CSV')
            eq_(resource['mimetype'], u'text/csv')
        else:
            eq_(resource['format'], u'Comma Separated Values')

    def test_distribution_format_IMT_field(self):
        g = Graph()

        dataset1 = URIRef("http://example.org/datasets/1")
        g.add((dataset1, RDF.type, DCAT.Dataset))

        distribution1_1 = URIRef("http://example.org/datasets/1/ds/1")

        imt = BNode()

        g.add((imt, RDF.type, DCT.IMT))
        g.add((imt, RDF.value, Literal('text/turtle')))
        g.add((imt, RDFS.label, Literal('Turtle')))

        g.add((distribution1_1, RDF.type, DCAT.Distribution))
        g.add((distribution1_1, DCT['format'], imt))
        g.add((dataset1, DCAT.distribution, distribution1_1))

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        datasets = [d for d in p.datasets()]

        resource = datasets[0]['resources'][0]

        eq_(resource['format'], u'Turtle')
        eq_(resource['mimetype'], u'text/turtle')

    def test_catalog_xml_rdf(self):

        contents = self._get_file_contents('catalog.rdf')

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.parse(contents)

        datasets = [d for d in p.datasets()]

        eq_(len(datasets), 2)

        dataset = (datasets[0] if datasets[0]['title'] == 'Example dataset 1'
                   else datasets[1])

        eq_(dataset['title'], 'Example dataset 1')
        eq_(len(dataset['resources']), 3)
        eq_(len(dataset['tags']), 2)

    def test_dataset_turtle_1(self):

        contents = self._get_file_contents('dataset_deri.ttl')

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.parse(contents, _format='n3')

        datasets = [d for d in p.datasets()]

        eq_(len(datasets), 1)

        dataset = datasets[0]

        eq_(dataset['title'], 'Abandoned Vehicles')
        eq_(len(dataset['resources']), 1)

        resource = dataset['resources'][0]
        eq_(resource['name'], u'CSV distribution of: Abandoned Vehicles')
        eq_(resource['url'], u'http://data.london.gov.uk/datafiles/environment/abandoned-vehicles-borough.csv')
        eq_(resource['uri'], u'http://data.london.gov.uk/dataset/Abandoned_Vehicles/csv')

    def test_dataset_json_ld_1(self):

        contents = self._get_file_contents('catalog_pod.jsonld')

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.parse(contents, _format='json-ld')

        datasets = [d for d in p.datasets()]

        eq_(len(datasets), 1)

        dataset = datasets[0]
        extras = dict((e['key'], e['value']) for e in dataset['extras'])

        eq_(dataset['title'], 'U.S. Widget Manufacturing Statistics')

        eq_(extras['contact_name'], 'Jane Doe')
        eq_(extras['contact_email'], 'mailto:jane.doe@agency.gov')
        eq_(extras['publisher_name'], 'Widget Services')
        eq_(extras['publisher_email'], 'widget.services@agency.gov')

        eq_(len(dataset['resources']), 4)

        resource = [r for r in dataset['resources'] if r['name'] == 'widgets.csv'][0]
        eq_(resource['name'], u'widgets.csv')
        eq_(resource['url'], u'https://data.agency.gov/datasets/widgets-statistics/widgets.csv')
        eq_(resource['download_url'], u'https://data.agency.gov/datasets/widgets-statistics/widgets.csv')

    def test_dataset_compatibility_mode(self):

        contents = self._get_file_contents('dataset.rdf')

        p = RDFParser(profiles=['euro_dcat_ap'], compatibility_mode=True)

        p.parse(contents)

        datasets = [d for d in p.datasets()]

        eq_(len(datasets), 1)

        dataset = datasets[0]

        def _get_extra_value(key):
            v = [extra['value'] for extra in dataset['extras'] if extra['key'] == key]
            return v[0] if v else None

        eq_(_get_extra_value('dcat_issued'), u'2012-05-10')
        eq_(_get_extra_value('dcat_modified'), u'2012-05-10T21:04:00')
        eq_(_get_extra_value('dcat_publisher_name'), 'Publishing Organization for dataset 1')
        eq_(_get_extra_value('dcat_publisher_email'), 'contact@some.org')
        eq_(_get_extra_value('language'), 'ca,en,es')
    
    @helpers.change_config(DCAT_EXPOSE_SUBCATALOGS, 'true')
    def test_parse_subcatalog(self):
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
        s.serialize_catalog(catalog_dict, dataset_dicts=[dataset])
        g = s.g

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        # at least one subcatalog with hasPart
        subcatalogs = list(p.g.objects(None, DCT.hasPart))
        assert_true(subcatalogs)

        # at least one dataset in subcatalogs
        subdatasets = []
        for subcatalog in subcatalogs:
            datasets = p.g.objects(subcatalog, DCAT.dataset)
            for dataset in datasets:
                subdatasets.append((dataset,subcatalog,))
        assert_true(subdatasets)
        
        datasets = dict([(d['title'], d) for d in p.datasets()])

        for subdataset, subcatalog in subdatasets:
            title = unicode(list(p.g.objects(subdataset, DCT.title))[0])
            dataset = datasets[title]
            has_subcat = False
            for ex in dataset['extras']:
                exval = ex['value']
                exkey = ex['key']
                if exkey == 'source_catalog_homepage':
                    has_subcat = True
                    eq_(exval, unicode(subcatalog))
            # check if we had subcatalog in extras
            assert_true(has_subcat)


class TestEuroDCATAPProfileParsingSpatial(BaseParseTest):

    def test_spatial_multiple_dct_spatial_instances(self):
        g = Graph()

        dataset = URIRef('http://example.org/datasets/1')
        g.add((dataset, RDF.type, DCAT.Dataset))

        spatial_uri = URIRef('http://geonames/Newark')
        g.add((dataset, DCT.spatial, spatial_uri))

        location_ref = BNode()
        g.add((location_ref, RDF.type, DCT.Location))
        g.add((dataset, DCT.spatial, location_ref))
        g.add((location_ref,
               LOCN.geometry,
               Literal('{"type": "Point", "coordinates": [23, 45]}', datatype=GEOJSON_IMT)))

        location_ref = BNode()
        g.add((location_ref, RDF.type, DCT.Location))
        g.add((dataset, DCT.spatial, location_ref))
        g.add((location_ref, SKOS.prefLabel, Literal('Newark')))

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        datasets = [d for d in p.datasets()]

        extras = self._extras(datasets[0])

        eq_(extras['spatial_uri'], 'http://geonames/Newark')
        eq_(extras['spatial_text'], 'Newark')
        eq_(extras['spatial'], '{"type": "Point", "coordinates": [23, 45]}')

    def test_spatial_one_dct_spatial_instance(self):
        g = Graph()

        dataset = URIRef('http://example.org/datasets/1')
        g.add((dataset, RDF.type, DCAT.Dataset))

        spatial_uri = URIRef('http://geonames/Newark')
        g.add((dataset, DCT.spatial, spatial_uri))

        g.add((spatial_uri, RDF.type, DCT.Location))
        g.add((spatial_uri,
               LOCN.geometry,
               Literal('{"type": "Point", "coordinates": [23, 45]}', datatype=GEOJSON_IMT)))
        g.add((spatial_uri, SKOS.prefLabel, Literal('Newark')))

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        datasets = [d for d in p.datasets()]

        extras = self._extras(datasets[0])

        eq_(extras['spatial_uri'], 'http://geonames/Newark')
        eq_(extras['spatial_text'], 'Newark')
        eq_(extras['spatial'], '{"type": "Point", "coordinates": [23, 45]}')

    def test_spatial_one_dct_spatial_instance_no_uri(self):
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

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        datasets = [d for d in p.datasets()]

        extras = self._extras(datasets[0])

        assert_true('spatial_uri' not in extras)
        eq_(extras['spatial_text'], 'Newark')
        eq_(extras['spatial'], '{"type": "Point", "coordinates": [23, 45]}')


    def test_spatial_rdfs_label(self):
        g = Graph()

        dataset = URIRef('http://example.org/datasets/1')
        g.add((dataset, RDF.type, DCAT.Dataset))

        spatial_uri = URIRef('http://geonames/Newark')
        g.add((dataset, DCT.spatial, spatial_uri))

        g.add((spatial_uri, RDF.type, DCT.Location))
        g.add((spatial_uri, RDFS.label, Literal('Newark')))

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        datasets = [d for d in p.datasets()]

        extras = self._extras(datasets[0])

        eq_(extras['spatial_text'], 'Newark')

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

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        datasets = [d for d in p.datasets()]

        extras = self._extras(datasets[0])

        eq_(extras['spatial'], '{"type": "Point", "coordinates": [23, 45]}')

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

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        datasets = [d for d in p.datasets()]

        extras = self._extras(datasets[0])
        # NOTE: geomet returns floats for coordinates on WKT -> GeoJSON
        eq_(extras['spatial'], '{"type": "Point", "coordinates": [67.0, 89.0]}')

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

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        datasets = [d for d in p.datasets()]

        extras = self._extras(datasets[0])

        assert_true('spatial' not in extras)

    def test_spatial_literal_only(self):
        g = Graph()

        dataset = URIRef('http://example.org/datasets/1')
        g.add((dataset, RDF.type, DCAT.Dataset))

        g.add((dataset, DCT.spatial, Literal('Newark')))

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        datasets = [d for d in p.datasets()]

        extras = self._extras(datasets[0])

        eq_(extras['spatial_text'], 'Newark')
        assert_true('spatial_uri' not in extras)
        assert_true('spatial' not in extras)

    def test_spatial_uri_only(self):
        g = Graph()

        dataset = URIRef('http://example.org/datasets/1')
        g.add((dataset, RDF.type, DCAT.Dataset))

        spatial_uri = URIRef('http://geonames/Newark')
        g.add((dataset, DCT.spatial, spatial_uri))
        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        datasets = [d for d in p.datasets()]

        extras = self._extras(datasets[0])

        eq_(extras['spatial_uri'], 'http://geonames/Newark')
        assert_true('spatial_text' not in extras)
        assert_true('spatial' not in extras)

    def test_tags_with_commas(self):
        g = Graph()

        dataset = URIRef('http://example.org/datasets/1')
        g.add((dataset, RDF.type, DCAT.Dataset))
        g.add((dataset, DCAT.keyword, Literal('Tree, forest, shrub')))
        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        datasets = [d for d in p.datasets()]
        
        eq_(len(datasets[0]['tags']), 3)

    INVALID_TAG = "Som`E-in.valid tag!;"
    VALID_TAG = {'name': 'some-invalid-tag'}

    @helpers.change_config(DCAT_CLEAN_TAGS, 'true')
    def test_tags_with_commas_clean_tags_on(self):
        g = Graph()

        dataset = URIRef('http://example.org/datasets/1')
        g.add((dataset, RDF.type, DCAT.Dataset))
        g.add((dataset, DCAT.keyword, Literal(self.INVALID_TAG)))
        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        datasets = [d for d in p.datasets()]

        assert_true(self.VALID_TAG in datasets[0]['tags'])
        assert_true(self.INVALID_TAG not in datasets[0]['tags'])


    @helpers.change_config(DCAT_CLEAN_TAGS, 'false')
    def test_tags_with_commas_clean_tags_off(self):
        g = Graph()

        dataset = URIRef('http://example.org/datasets/1')
        g.add((dataset, RDF.type, DCAT.Dataset))
        g.add((dataset, DCAT.keyword, Literal(self.INVALID_TAG)))
        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        # when config flag is set to false, bad tags can happen
        
        datasets = [d for d in p.datasets()]
        assert_true(self.VALID_TAG not in datasets[0]['tags'])
        assert_true({'name': self.INVALID_TAG} in datasets[0]['tags'])
