import os
import json

import nose

from rdflib import Graph, URIRef, Literal
from rdflib.namespace import Namespace, RDF

from ckanext.dcat.parsers import RDFParser

eq_ = nose.tools.eq_

DCAT = Namespace("http://www.w3.org/ns/dcat#")


class TestEuroDCATAPProfile(object):

    def _get_file_contents(self, file_name):
        path = os.path.join(os.path.dirname(__file__),
                            '..', '..', '..', 'examples',
                            file_name)
        with open(path, 'r') as f:
            return f.read()

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
        eq_(_get_extra_value('alternate_identifier'), u'alternate-identifier-x343')
        eq_(_get_extra_value('dcat_version'), u'2.3')
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

        #  Lists
        eq_(sorted(_get_extra_value_as_list('language')), [u'ca', u'en' , u'es'])
        eq_(sorted(_get_extra_value_as_list('theme')), [u'Earth Sciences',
                                                        u'http://eurovoc.europa.eu/100142',
                                                        u'http://eurovoc.europa.eu/209065'])
        eq_(sorted(_get_extra_value_as_list('conforms_to')), [u'Standard 1', u'Standard 2'])

        # Dataset URI
        eq_(_get_extra_value('uri'), u'https://data.some.org/catalog/datasets/9df8df51-63db-37a8-e044-0003ba9b0d98')

        # Resources
        eq_(len(dataset['resources']), 1)

        resource = dataset['resources'][0]

        #  Simple values
        eq_(resource['name'], u'Some website')
        eq_(resource['description'], u'A longer description')

        # eq_(resource['format'], u'')
        # eq_(resource['mimetype'], u'')
        eq_(resource['issued'], u'2012-05-11')
        eq_(resource['modified'], u'2012-05-01T00:04:06')
        eq_(resource['status'], u'http://purl.org/adms/status/Completed')

        # These two are likely to need clarification
        eq_(resource['license'], u'http://creativecommons.org/licenses/by/3.0/')
        eq_(resource['rights'], u'Some statement about rights')

        eq_(resource['url'], u'http://www.bgs.ac.uk/gbase/geochemcd/home.html')
        assert 'download_url' not in resource

        eq_(resource['size'], 12323)

        # Distribution URI
        eq_(resource['uri'], u'https://data.some.org/catalog/datasets/9df8df51-63db-37a8-e044-0003ba9b0d98/1')

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
