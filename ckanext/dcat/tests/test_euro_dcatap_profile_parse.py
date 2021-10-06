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
                                   GEOJSON_IMT, VCARD)
from ckanext.dcat.utils import DCAT_EXPOSE_SUBCATALOGS, DCAT_CLEAN_TAGS


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

    def _build_and_parse_format_mediatype_graph(self, format_item=None, mediatype_item=None):
        """
        Creates a minimal graph with a distribution having the specified dct:format and dcat:mediaType
        nodes. At least one of those nodes has to be given.

        After creating the graph, it is parsed using the euro_dcat_ap profile.

        :param format_item:
            Literal or URIRef object for dct:format. None if the node should be omitted.
        :param mediatype_item:
            Literal or URIRef object for dcat:mediaType. None if the node should be omitted.

        :returns:
            The parsed resource dict
        """
        g = Graph()

        dataset = URIRef("http://example.org/datasets/1")
        g.add((dataset, RDF.type, DCAT.Dataset))

        distribution = URIRef("http://example.org/datasets/1/ds/1")
        g.add((dataset, DCAT.distribution, distribution))
        g.add((distribution, RDF.type, DCAT.Distribution))
        if format_item:
            g.add((distribution, DCT['format'], format_item))
        if mediatype_item:
            g.add((distribution, DCAT.mediaType, mediatype_item))
        if format_item is None and mediatype_item is None:
            raise AssertionError('At least one of format or mediaType is required!')

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        dataset = [d for d in p.datasets()][0]
        return dataset.get('resources')

    def test_dataset_all_fields(self):

        contents = self._get_file_contents('dataset.rdf')

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.parse(contents)

        datasets = [d for d in p.datasets()]

        assert len(datasets) == 1

        dataset = datasets[0]

        # Basic fields

        assert dataset['title'] == u'Zimbabwe Regional Geochemical Survey.'
        assert dataset['notes'] == u'During the period 1982-86 a team of geologists from the British Geological Survey ...'
        assert dataset['url'] == 'http://dataset.info.org'
        assert dataset['version'] == '2.3'
        assert dataset['license_id'] == 'cc-nc'

        # Tags

        assert (sorted(dataset['tags'], key=lambda k: k['name']) ==
            [
                {'name': u'exploration'},
                {'name': u'geochemistry'},
                {'name': u'geology'}
            ])

        # Extras

        def _get_extra_value(key):
            v = [extra['value'] for extra in dataset['extras'] if extra['key'] == key]
            return v[0] if v else None

        def _get_extra_value_as_list(key):
            value = _get_extra_value(key)
            return json.loads(value) if value else []

        #  Simple values
        assert _get_extra_value('issued') == u'2012-05-10'
        assert _get_extra_value('modified') == u'2012-05-10T21:04:00'
        assert _get_extra_value('identifier') == u'9df8df51-63db-37a8-e044-0003ba9b0d98'
        assert _get_extra_value('version_notes') == u'New schema added'
        assert _get_extra_value('temporal_start') == '1905-03-01'
        assert _get_extra_value('temporal_end') == '2013-01-05'
        assert _get_extra_value('frequency') == 'http://purl.org/cld/freq/daily'
        assert _get_extra_value('spatial_uri') == 'http://publications.europa.eu/mdr/authority/country/ZWE'
        assert _get_extra_value('publisher_uri') == 'http://orgs.vocab.org/some-org'
        assert _get_extra_value('publisher_name') == 'Publishing Organization for dataset 1'
        assert _get_extra_value('publisher_email') == 'contact@some.org'
        assert _get_extra_value('publisher_url') == 'http://some.org'
        assert _get_extra_value('publisher_type') == 'http://purl.org/adms/publishertype/NonProfitOrganisation'
        assert _get_extra_value('contact_name') == 'Point of Contact'
        # mailto gets removed for storage and is added again on output
        assert _get_extra_value('contact_email') == 'contact@some.org'
        assert _get_extra_value('access_rights') == 'public'
        assert _get_extra_value('provenance') == 'Some statement about provenance'
        assert _get_extra_value('dcat_type') == 'test-type'

        #  Lists
        assert sorted(_get_extra_value_as_list('language')), [u'ca', u'en' == u'es']
        assert (sorted(_get_extra_value_as_list('theme')) ==
                [u'Earth Sciences',
                 u'http://eurovoc.europa.eu/100142',
                 u'http://eurovoc.europa.eu/209065'])
        assert sorted(_get_extra_value_as_list('conforms_to')), [u'Standard 1' == u'Standard 2']

        assert sorted(_get_extra_value_as_list('alternate_identifier')), [u'alternate-identifier-1' == u'alternate-identifier-2']
        assert (sorted(_get_extra_value_as_list('documentation')) ==
                [u'http://dataset.info.org/doc1',
                 u'http://dataset.info.org/doc2'])
        assert (sorted(_get_extra_value_as_list('related_resource')) ==
                [u'http://dataset.info.org/related1',
                 u'http://dataset.info.org/related2'])
        assert (sorted(_get_extra_value_as_list('has_version')) ==
                [u'https://data.some.org/catalog/datasets/derived-dataset-1',
                 u'https://data.some.org/catalog/datasets/derived-dataset-2'])
        assert sorted(_get_extra_value_as_list('is_version_of')) == [u'https://data.some.org/catalog/datasets/original-dataset']
        assert (sorted(_get_extra_value_as_list('source')) ==
                [u'https://data.some.org/catalog/datasets/source-dataset-1',
                 u'https://data.some.org/catalog/datasets/source-dataset-2'])
        assert sorted(_get_extra_value_as_list('sample')) == [u'https://data.some.org/catalog/datasets/9df8df51-63db-37a8-e044-0003ba9b0d98/sample']

        # Dataset URI
        assert _get_extra_value('uri') == u'https://data.some.org/catalog/datasets/9df8df51-63db-37a8-e044-0003ba9b0d98'

        # Resources
        assert len(dataset['resources']) == 1

        resource = dataset['resources'][0]

        #  Simple values
        assert resource['name'] == u'Some website'
        assert resource['description'] == u'A longer description'
        assert resource['format'] == u'HTML'
        assert resource['mimetype'] == u'text/html'
        assert resource['issued'] == u'2012-05-11'
        assert resource['modified'] == u'2012-05-01T00:04:06'
        assert resource['status'] == u'http://purl.org/adms/status/Completed'

        assert resource['hash'] == u'4304cf2e751e6053c90b1804c89c0ebb758f395a'
        assert resource['hash_algorithm'] == u'http://spdx.org/rdf/terms#checksumAlgorithm_sha1'

        # Lists
        for item in [
            ('documentation', [u'http://dataset.info.org/distribution1/doc1', u'http://dataset.info.org/distribution1/doc2']),
            ('language', [u'ca', u'en', u'es']),
            ('conforms_to', [u'Standard 1', u'Standard 2']),
        ]:
            assert sorted(json.loads(resource[item[0]])) == item[1]

        # These two are likely to need clarification
        assert resource['license'] == u'http://creativecommons.org/licenses/by-nc/2.0/'
        assert resource['rights'] == u'Some statement about rights'

        assert resource['url'] == u'http://www.bgs.ac.uk/gbase/geochemcd/home.html'
        assert 'download_url' not in resource

        assert resource['size'] == 12323

        # Distribution URI
        assert resource['uri'] == u'https://data.some.org/catalog/datasets/9df8df51-63db-37a8-e044-0003ba9b0d98/1'

    # owl:versionInfo is tested on the test above
    def test_dataset_version_adms(self):
        g = Graph()

        dataset1 = URIRef("http://example.org/datasets/1")
        g.add((dataset1, RDF.type, DCAT.Dataset))

        g.add((dataset1, ADMS.version, Literal('2.3a')))

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        dataset = [d for d in p.datasets()][0]

        assert dataset['version'] == u'2.3a'

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
        assert dataset['license_id'] == 'cc-by'

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
        assert dataset['license_id'] == 'cc-by'

    def test_dataset_contact_point_vcard_hasVN_literal(self):
        g = Graph()

        dataset_ref = URIRef("http://example.org/datasets/1")
        g.add((dataset_ref, RDF.type, DCAT.Dataset))

        contact_point = BNode()
        g.add((contact_point, RDF.type, VCARD.Organization))
        g.add((contact_point, VCARD.hasFN, Literal('Point of Contact')))
        g.add((dataset_ref, DCAT.contactPoint, contact_point))

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        dataset = [d for d in p.datasets()][0]
        extras = self._extras(dataset)
        assert extras['contact_name'] == 'Point of Contact'

    def test_dataset_contact_point_vcard_hasVN_hasValue(self):
        g = Graph()

        dataset_ref = URIRef("http://example.org/datasets/1")
        g.add((dataset_ref, RDF.type, DCAT.Dataset))

        contact_point = BNode()
        g.add((contact_point, RDF.type, VCARD.Organization))
        hasVN = BNode()
        g.add((hasVN, VCARD.hasValue, Literal('Point of Contact')))
        g.add((contact_point, VCARD.hasFN, hasVN))
        g.add((contact_point, RDF.type, VCARD.Organization))
        g.add((dataset_ref, DCAT.contactPoint, contact_point))

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        dataset = [d for d in p.datasets()][0]
        extras = self._extras(dataset)
        assert extras['contact_name'] == 'Point of Contact'

    def test_dataset_contact_point_vcard_hasEmail_hasValue(self):
        g = Graph()

        dataset_ref = URIRef("http://example.org/datasets/1")
        g.add((dataset_ref, RDF.type, DCAT.Dataset))

        contact_point = BNode()
        g.add((contact_point, RDF.type, VCARD.Organization))
        hasEmail = BNode()
        g.add((hasEmail, VCARD.hasValue, Literal('mailto:contact@some.org')))
        g.add((contact_point, VCARD.hasEmail, hasEmail))
        g.add((contact_point, RDF.type, VCARD.Organization))
        g.add((dataset_ref, DCAT.contactPoint, contact_point))

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        dataset = [d for d in p.datasets()][0]
        extras = self._extras(dataset)
        assert extras['contact_email'] == 'contact@some.org'

    def test_dataset_access_rights_and_distribution_rights_rights_statement_literal(self):
        # license_id retrieved from the URI of dcat:license object
        g = Graph()

        dataset_ref = URIRef("http://example.org/datasets/1")
        g.add((dataset_ref, RDF.type, DCAT.Dataset))

        # access_rights
        access_rights = BNode()
        g.add((access_rights, RDF.type, DCT.RightsStatement))
        g.add((access_rights, RDFS.label, Literal('public dataset')))
        g.add((dataset_ref, DCT.accessRights, access_rights))
        # rights
        rights = BNode()
        g.add((rights, RDF.type, DCT.RightsStatement))
        g.add((rights, RDFS.label, Literal('public distribution')))
        distribution = URIRef("http://example.org/datasets/1/ds/1")
        g.add((dataset_ref, DCAT.distribution, distribution))
        g.add((distribution, RDF.type, DCAT.Distribution))
        g.add((distribution, DCT.rights, rights))

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        dataset = [d for d in p.datasets()][0]
        extras = self._extras(dataset)
        assert extras['access_rights'] == 'public dataset'
        resource = dataset['resources'][0]
        assert resource['rights'] == 'public distribution'

    def test_dataset_access_rights_and_distribution_rights_rights_statement_uriref(self):
        g = Graph()

        dataset_ref = URIRef("http://example.org/datasets/1")
        g.add((dataset_ref, RDF.type, DCAT.Dataset))

        # access_rights
        access_rights = BNode()
        g.add((access_rights, RDF.type, DCT.RightsStatement))
        g.add((access_rights, RDFS.label, URIRef("http://example.org/datasets/1/ds/3")))
        g.add((dataset_ref, DCT.accessRights, access_rights))
        # rights
        rights = BNode()
        g.add((rights, RDF.type, DCT.RightsStatement))
        g.add((rights, RDFS.label, URIRef("http://example.org/datasets/1/ds/2")))
        distribution = URIRef("http://example.org/datasets/1/ds/1")
        g.add((dataset_ref, DCAT.distribution, distribution))
        g.add((distribution, RDF.type, DCAT.Distribution))
        g.add((distribution, DCT.rights, rights))

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        dataset = [d for d in p.datasets()][0]
        extras = self._extras(dataset)
        assert extras['access_rights'] == 'http://example.org/datasets/1/ds/3'
        resource = dataset['resources'][0]
        assert resource['rights'] == 'http://example.org/datasets/1/ds/2'

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

        assert resource['url'] == u'http://access.url.org'
        assert resource['access_url'] == u'http://access.url.org'
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

        assert resource['url'] == u'http://download.url.org'
        assert resource['download_url'] == u'http://download.url.org'
        assert 'access_url' not in resource

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

        assert resource['url'] == u'http://download.url.org'
        assert resource['download_url'] == u'http://download.url.org'
        assert resource['access_url'] == u'http://access.url.org'

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

        assert resource['format'] == u'CSV'
        assert resource['mimetype'] == u'text/csv'

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

        assert resource['format'] == u'CSV'
        assert 'mimetype' not in resource

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
            assert resource['format'] == u'CSV'
            assert resource['mimetype'] == u'text/csv'
        else:
            assert resource['format'] == u'text/csv'

    @pytest.mark.ckan_config('ckanext.dcat.normalize_ckan_format', False)
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

        assert resource['format'] == u'text/csv'
        assert resource['mimetype'] == u'text/csv'

    @pytest.mark.ckan_config('ckanext.dcat.normalize_ckan_format', False)
    def test_distribution_format_format_only_without_slash_normalize_false(self):
        g = Graph()

        dataset1 = URIRef("http://example.org/datasets/1")
        g.add((dataset1, RDF.type, DCAT.Dataset))

        distribution1_1 = URIRef("http://example.org/datasets/1/ds/1")
        g.add((distribution1_1, RDF.type, DCAT.Distribution))
        g.add((distribution1_1, DCT['format'], Literal('Comma Separated Values')))
        g.add((dataset1, DCAT.distribution, distribution1_1))

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        datasets = [d for d in p.datasets()]

        resource = datasets[0]['resources'][0]

        assert resource['format'] == u'Comma Separated Values'
        assert 'mimetype' not in resource

    @pytest.mark.ckan_config('ckanext.dcat.normalize_ckan_format', False)
    def test_distribution_format_format_only_with_slash_normalize_false(self):
        g = Graph()

        dataset1 = URIRef("http://example.org/datasets/1")
        g.add((dataset1, RDF.type, DCAT.Dataset))

        distribution1_1 = URIRef("http://example.org/datasets/1/ds/1")
        g.add((distribution1_1, RDF.type, DCAT.Distribution))
        g.add((distribution1_1, DCT['format'], Literal('text/csv')))
        g.add((dataset1, DCAT.distribution, distribution1_1))

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        datasets = [d for d in p.datasets()]

        resource = datasets[0]['resources'][0]

        assert resource['format'] == u'text/csv'
        assert resource['mimetype'] == u'text/csv'

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

        assert resource['format'] == u'text/unknown-imt'
        assert resource['mimetype'] == u'text/unknown-imt'

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

        assert resource['format'] == u'text/unknown-imt'
        assert resource['mimetype'] == u'text/unknown-imt'

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
            assert resource['format'] == u'CSV'
            assert resource['mimetype'] == u'text/csv'
        else:
            assert resource['format'] == u'Comma Separated Values'

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

        assert resource['format'] == u'Turtle'
        assert resource['mimetype'] == u'text/turtle'

    def test_distribution_dct_format_iana_uri(self):
        resources = self._build_and_parse_format_mediatype_graph(
            format_item=URIRef("https://www.iana.org/assignments/media-types/application/json")
        )
        # IANA mediatype URI should be added to mimetype field as well
        assert u'json' in resources[0].get('format').lower()
        assert (u'https://www.iana.org/assignments/media-types/application/json' ==
            resources[0].get('mimetype'))

    def test_distribution_mediatype_iana_uri_without_format(self):
        resources = self._build_and_parse_format_mediatype_graph(
            mediatype_item=URIRef("https://www.iana.org/assignments/media-types/application/json")
        )
        # IANA mediatype URI should be added to mimetype field and to format as well
        assert (u'https://www.iana.org/assignments/media-types/application/json' ==
            resources[0].get('mimetype'))
        assert (u'https://www.iana.org/assignments/media-types/application/json' ==
            resources[0].get('format'))

    def test_distribution_dct_format_other_uri(self):
        resources = self._build_and_parse_format_mediatype_graph(
            format_item=URIRef("https://example.com/my/format")
        )
        assert (u'https://example.com/my/format' ==
            resources[0].get('format'))
        assert None == resources[0].get('mimetype')

    def test_distribution_dct_format_mediatype_text(self):
        resources = self._build_and_parse_format_mediatype_graph(
            format_item=Literal("application/json")
        )
        # IANA mediatype should be added to mimetype field as well
        assert u'json' in resources[0].get('format').lower()
        assert (u'application/json' ==
            resources[0].get('mimetype'))

    def test_distribution_format_and_dcat_mediatype(self):
        # Even if dct:format is a valid IANA type, prefer dcat:mediaType if given
        resources = self._build_and_parse_format_mediatype_graph(
            format_item=Literal("application/json"),
            mediatype_item=Literal("test-mediatype")
        )
        # both should be stored
        assert u'json' in resources[0].get('format').lower()
        assert (u'test-mediatype' ==
            resources[0].get('mimetype'))

    def test_catalog_xml_rdf(self):

        contents = self._get_file_contents('catalog.rdf')

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.parse(contents)

        datasets = [d for d in p.datasets()]

        assert len(datasets) == 2

        dataset = (datasets[0] if datasets[0]['title'] == 'Example dataset 1'
                   else datasets[1])

        assert dataset['title'] == 'Example dataset 1'
        assert len(dataset['resources']) == 3
        assert len(dataset['tags']) == 2

    def test_dataset_turtle_1(self):

        contents = self._get_file_contents('dataset_deri.ttl')

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.parse(contents, _format='n3')

        datasets = [d for d in p.datasets()]

        assert len(datasets) == 1

        dataset = datasets[0]

        assert dataset['title'] == 'Abandoned Vehicles'
        assert len(dataset['resources']) == 1

        resource = dataset['resources'][0]
        assert resource['name'] == u'CSV distribution of: Abandoned Vehicles'
        assert resource['url'] == u'http://data.london.gov.uk/datafiles/environment/abandoned-vehicles-borough.csv'
        assert resource['uri'] == u'http://data.london.gov.uk/dataset/Abandoned_Vehicles/csv'

    def test_dataset_json_ld_1(self):

        contents = self._get_file_contents('catalog_pod.jsonld')

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.parse(contents, _format='json-ld')

        datasets = [d for d in p.datasets()]

        assert len(datasets) == 1

        dataset = datasets[0]
        extras = dict((e['key'], e['value']) for e in dataset['extras'])

        assert dataset['title'] == 'U.S. Widget Manufacturing Statistics'

        assert extras['contact_name'] == 'Jane Doe'
        # mailto gets removed for storage and is added again on output
        assert extras['contact_email'] == 'jane.doe@agency.gov'
        assert extras['publisher_name'] == 'Widget Services'
        assert extras['publisher_email'] == 'widget.services@agency.gov'

        assert len(dataset['resources']) == 4

        resource = [r for r in dataset['resources'] if r['name'] == 'widgets.csv'][0]
        assert resource['name'] == u'widgets.csv'
        assert resource['url'] == u'https://data.agency.gov/datasets/widgets-statistics/widgets.csv'
        assert resource['download_url'] == u'https://data.agency.gov/datasets/widgets-statistics/widgets.csv'

    def test_dataset_json_ld_with_at_graph(self):

        contents = self._get_file_contents('catalog_with_at_graph.jsonld')

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.parse(contents, _format='json-ld')

        datasets = [d for d in p.datasets()]

        assert len(datasets) == 1

        dataset = datasets[0]
        extras = dict((e['key'], e['value']) for e in dataset['extras'])

        assert dataset['title'] == 'Title dataset'

        assert extras['contact_name'] == 'Jane Doe'
        # mailto gets removed for storage and is added again on output
        assert extras['contact_email'] == 'jane.doe@agency.gov'

        assert len(dataset['resources']) == 1

        resource = dataset['resources'][0]
        assert resource['name'] == u'download.zip'
        assert resource['url'] == u'http://example2.org/files/download.zip'
        assert resource['access_url'] == u'https://ckan.example.org/dataset/d4ce4e6e-ab89-44cb-bf5c-33a162c234de/resource/a289c289-55c9-410f-b4c7-f88e5f6f4e47'
        assert resource['download_url'] == u'http://example2.org/files/download.zip'

    def test_dataset_compatibility_mode(self):

        contents = self._get_file_contents('dataset.rdf')

        p = RDFParser(profiles=['euro_dcat_ap'], compatibility_mode=True)

        p.parse(contents)

        datasets = [d for d in p.datasets()]

        assert len(datasets) == 1

        dataset = datasets[0]

        def _get_extra_value(key):
            v = [extra['value'] for extra in dataset['extras'] if extra['key'] == key]
            return v[0] if v else None

        assert _get_extra_value('dcat_issued') == u'2012-05-10'
        assert _get_extra_value('dcat_modified') == u'2012-05-10T21:04:00'
        assert _get_extra_value('dcat_publisher_name') == 'Publishing Organization for dataset 1'
        assert _get_extra_value('dcat_publisher_email') == 'contact@some.org'
        assert _get_extra_value('language') == 'ca,en,es'

    @pytest.mark.ckan_config(DCAT_EXPOSE_SUBCATALOGS, 'true')
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
        assert subcatalogs

        # at least one dataset in subcatalogs
        subdatasets = []
        for subcatalog in subcatalogs:
            datasets = p.g.objects(subcatalog, DCAT.dataset)
            for dataset in datasets:
                subdatasets.append((dataset,subcatalog,))
        assert subdatasets

        datasets = dict([(d['title'], d) for d in p.datasets()])

        for subdataset, subcatalog in subdatasets:
            title = str(list(p.g.objects(subdataset, DCT.title))[0])
            dataset = datasets[title]
            has_subcat = False
            for ex in dataset['extras']:
                exval = ex['value']
                exkey = ex['key']
                if exkey == 'source_catalog_homepage':
                    has_subcat = True
                    assert exval == str(subcatalog)
            # check if we had subcatalog in extras
            assert has_subcat


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

        assert extras['spatial_uri'] == 'http://geonames/Newark'
        assert extras['spatial_text'] == 'Newark'
        assert extras['spatial'], '{"type": "Point", "coordinates": [23 == 45]}'

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

        assert extras['spatial_uri'] == 'http://geonames/Newark'
        assert extras['spatial_text'] == 'Newark'
        assert extras['spatial'], '{"type": "Point", "coordinates": [23 == 45]}'

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

        assert 'spatial_uri' not in extras
        assert extras['spatial_text'] == 'Newark'
        assert extras['spatial'], '{"type": "Point", "coordinates": [23 == 45]}'


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

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        datasets = [d for d in p.datasets()]

        extras = self._extras(datasets[0])

        assert extras['spatial'], '{"type": "Point", "coordinates": [23 == 45]}'

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
        assert extras['spatial'], '{"type": "Point", "coordinates": [67.0 == 89.0]}'

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

        assert 'spatial' not in extras

    def test_spatial_literal_only(self):
        g = Graph()

        dataset = URIRef('http://example.org/datasets/1')
        g.add((dataset, RDF.type, DCAT.Dataset))

        g.add((dataset, DCT.spatial, Literal('Newark')))

        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        datasets = [d for d in p.datasets()]

        extras = self._extras(datasets[0])

        assert extras['spatial_text'] == 'Newark'
        assert 'spatial_uri' not in extras
        assert 'spatial' not in extras

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

        assert extras['spatial_uri'] == 'http://geonames/Newark'
        assert 'spatial_text' not in extras
        assert 'spatial' not in extras

    def test_tags_with_commas(self):
        g = Graph()

        dataset = URIRef('http://example.org/datasets/1')
        g.add((dataset, RDF.type, DCAT.Dataset))
        g.add((dataset, DCAT.keyword, Literal('Tree, forest, shrub')))
        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        datasets = [d for d in p.datasets()]

        assert len(datasets[0]['tags']) == 3

    INVALID_TAG = "Som`E-in.valid tag!;"
    VALID_TAG = {'name': 'some-invalid-tag'}

    @pytest.mark.ckan_config(DCAT_CLEAN_TAGS, 'true')
    def test_tags_with_commas_clean_tags_on(self):
        g = Graph()

        dataset = URIRef('http://example.org/datasets/1')
        g.add((dataset, RDF.type, DCAT.Dataset))
        g.add((dataset, DCAT.keyword, Literal(self.INVALID_TAG)))
        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        datasets = [d for d in p.datasets()]

        assert self.VALID_TAG in datasets[0]['tags']
        assert self.INVALID_TAG not in datasets[0]['tags']


    @pytest.mark.ckan_config(DCAT_CLEAN_TAGS, 'false')
    def test_tags_with_commas_clean_tags_off(self):
        g = Graph()

        dataset = URIRef('http://example.org/datasets/1')
        g.add((dataset, RDF.type, DCAT.Dataset))
        g.add((dataset, DCAT.keyword, Literal(self.INVALID_TAG)))
        p = RDFParser(profiles=['euro_dcat_ap'])

        p.g = g

        # when config flag is set to false, bad tags can happen

        datasets = [d for d in p.datasets()]
        assert self.VALID_TAG not in datasets[0]['tags']
        assert {'name': self.INVALID_TAG} in datasets[0]['tags']
