# -*- coding: utf-8 -*-
from builtins import str
from builtins import range
import time

from collections import OrderedDict
from six.moves.urllib.parse import urlparse, parse_qs, urlencode, urlunparse

import pytest

from ckan import plugins as p

from rdflib import Graph
from ckantoolkit import url_for as core_url_for
from ckantoolkit.tests import factories

from ckanext.dcat.processors import RDFParser
from ckanext.dcat.profiles import RDF, DCAT
from ckanext.dcat.processors import HYDRA


def _sort_query_params(url):
    parts = urlparse(url)
    qs = parse_qs(parts.query)
    ordered_qs = OrderedDict(sorted(qs.items()))
    encoded_qs = urlencode(ordered_qs).replace('u%27', '%27')

    return urlunparse(
        (parts.scheme, parts.netloc, parts.path, parts.params,
         encoded_qs, parts.fragment)
    )


def url_for(*args, **kwargs):

    if not p.toolkit.check_ckan_version(min_version='2.9'):

        external = kwargs.pop('_external', False)
        if external is not None:
            kwargs['qualified'] = external

        if len(args) and args[0] == 'dcat.read_dataset':
            return core_url_for('dcat_dataset', **kwargs)
        elif len(args) and args[0] == 'dcat.read_catalog':
            return core_url_for('dcat_catalog', **kwargs)
        elif len(args) and args[0] == 'dataset.new':
            return core_url_for(controller='package', action='new', **kwargs)
        elif len(args) and args[0] == 'dataset.read':
            return core_url_for(controller='package', action='read', **kwargs)


    return core_url_for(*args, **kwargs)


@pytest.mark.usefixtures('with_plugins', 'clean_db', 'clean_index')
class TestEndpoints():

    def _object_value(self, graph, subject, predicate):

        objects = [o for o in graph.objects(subject, predicate)]
        return str(objects[0]) if objects else None

    def test_dataset_default(self, app):

        dataset = factories.Dataset(
            notes='Test dataset'
        )

        url = url_for('dcat.read_dataset', _id=dataset['name'], _format='rdf')

        response = app.get(url)

        assert response.headers['Content-Type'] == 'application/rdf+xml'

        content = response.body

        # Parse the contents to check it's an actual serialization
        p = RDFParser()

        p.parse(content, _format='xml')

        dcat_datasets = [d for d in p.datasets()]

        assert len(dcat_datasets) == 1

        dcat_dataset = dcat_datasets[0]

        assert dcat_dataset['title'] == dataset['title']
        assert dcat_dataset['notes'] == dataset['notes']

    def test_dataset_xml(self, app):

        dataset = factories.Dataset(
            notes='Test dataset'
        )

        url = url_for('dcat.read_dataset', _id=dataset['name'], _format='xml')

        response = app.get(url)

        assert response.headers['Content-Type'] == 'application/rdf+xml'

        content = response.body

        # Parse the contents to check it's an actual serialization
        p = RDFParser()

        p.parse(content, _format='xml')

        dcat_datasets = [d for d in p.datasets()]

        assert len(dcat_datasets) == 1

        dcat_dataset = dcat_datasets[0]

        assert dcat_dataset['title'] == dataset['title']
        assert dcat_dataset['notes'] == dataset['notes']

    def test_dataset_ttl(self, app):

        dataset = factories.Dataset(
            notes='Test dataset'
        )

        url = url_for('dcat.read_dataset', _id=dataset['name'], _format='ttl')

        response = app.get(url)

        assert response.headers['Content-Type'] == 'text/turtle'

        content = response.body

        # Parse the contents to check it's an actual serialization
        p = RDFParser()

        p.parse(content, _format='turtle')

        dcat_datasets = [d for d in p.datasets()]

        assert len(dcat_datasets) == 1

        dcat_dataset = dcat_datasets[0]

        assert dcat_dataset['title'] == dataset['title']
        assert dcat_dataset['notes'] == dataset['notes']

    def test_dataset_n3(self, app):

        dataset = factories.Dataset(
            notes='Test dataset'
        )

        url = url_for('dcat.read_dataset', _id=dataset['name'], _format='n3')

        response = app.get(url)

        assert response.headers['Content-Type'] == 'text/n3'

        content = response.body

        # Parse the contents to check it's an actual serialization
        p = RDFParser()

        p.parse(content, _format='n3')

        dcat_datasets = [d for d in p.datasets()]

        assert len(dcat_datasets) == 1

        dcat_dataset = dcat_datasets[0]

        assert dcat_dataset['title'] == dataset['title']
        assert dcat_dataset['notes'] == dataset['notes']

    def test_dataset_jsonld(self, app):

        dataset = factories.Dataset(
            notes='Test dataset'
        )

        url = url_for('dcat.read_dataset', _id=dataset['name'], _format='jsonld')

        response = app.get(url)

        assert response.headers['Content-Type'] == 'application/ld+json'

        content = response.body

        # Parse the contents to check it's an actual serialization
        p = RDFParser()

        p.parse(content, _format='json-ld')

        dcat_datasets = [d for d in p.datasets()]

        assert len(dcat_datasets) == 1

        dcat_dataset = dcat_datasets[0]

        assert dcat_dataset['title'] == dataset['title']
        assert dcat_dataset['notes'] == dataset['notes']

    def test_dataset_profiles_jsonld(self, app):

        dataset = factories.Dataset(
            notes='Test dataset'
        )

        url = url_for('dcat.read_dataset', _id=dataset['name'], _format='jsonld', profiles='schemaorg')

        response = app.get(url)

        assert response.headers['Content-Type'] == 'application/ld+json'

        content = response.body

        assert '"@type": "schema:Dataset"' in content
        assert '"schema:description": "%s"' % dataset['notes'] in content

    def test_dataset_profiles_not_found(self, app):

        dataset = factories.Dataset(
            notes='Test dataset'
        )

        url = url_for('dcat.read_dataset', _id=dataset['name'], _format='jsonld', profiles='nope')

        response = app.get(url, status=409)

        assert 'Unknown RDF profiles: nope' in response.body

    def test_dataset_not_found(self, app):
        import uuid

        url = url_for('dcat.read_dataset', _id=str(uuid.uuid4()), _format='n3')

        app.get(url, status=404)

    def test_dataset_form_is_rendered(self, app):
        sysadmin = factories.Sysadmin()
        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        url = url_for('dataset.new')

        response = app.get(url, extra_environ=env)

        content = response.body

        assert '<input id="field-title"' in content

    def test_catalog_default(self, app):

        for i in range(4):
            factories.Dataset()

        url = url_for('dcat.read_catalog', _format='rdf')

        response = app.get(url)

        assert response.headers['Content-Type'] == 'application/rdf+xml'

        content = response.body

        # Parse the contents to check it's an actual serialization
        p = RDFParser()

        p.parse(content, _format='xml')

        dcat_datasets = [d for d in p.datasets()]

        assert len(dcat_datasets) == 4

    def test_catalog_ttl(self, app):

        for i in range(4):
            factories.Dataset()

        url = url_for('dcat.read_catalog', _format='ttl')

        response = app.get(url)

        assert response.headers['Content-Type'] == 'text/turtle'

        content = response.body

        # Parse the contents to check it's an actual serialization
        p = RDFParser()

        p.parse(content, _format='turtle')

        dcat_datasets = [d for d in p.datasets()]

        assert len(dcat_datasets) == 4

    def test_catalog_modified_date(self, app):

        dataset1 = factories.Dataset(title='First dataset')
        time.sleep(1)
        dataset2 = factories.Dataset(title='Second dataset')

        url = url_for('dcat.read_catalog',
                      _format='ttl',
                      modified_since=dataset2['metadata_modified'])

        response = app.get(url)

        content = response.body

        p = RDFParser()

        p.parse(content, _format='turtle')

        dcat_datasets = [d for d in p.datasets()]

        assert len(dcat_datasets) == 1

        assert dcat_datasets[0]['title'] == dataset2['title']

    def test_catalog_modified_date_wrong_date(self, app):

        url = url_for('dcat.read_catalog',
                      _format='ttl',
                      modified_since='wrong_date')

        app.get(url, status=409)

    def test_catalog_q_search(self, app):

        dataset1 = factories.Dataset(title='First dataset')
        dataset2 = factories.Dataset(title='Second dataset')

        url = url_for('dcat.read_catalog',
                      _format='ttl',
                      q='First')


        response = app.get(url)
        content = response.body
        p = RDFParser()
        p.parse(content, _format='turtle')

        dcat_datasets = [d for d in p.datasets()]
        assert len(dcat_datasets) == 1
        assert dcat_datasets[0]['title'] == dataset1['title']

    def test_catalog_fq_filter(self, app):
        dataset1 = factories.Dataset(
            title='First dataset',
            tags=[
                {'name': 'economy'},
                {'name': 'statistics'}
            ]
        )
        dataset2 = factories.Dataset(
            title='Second dataset',
            tags=[{'name': 'economy'}]
        )
        dataset3 = factories.Dataset(
            title='Third dataset',
            tags=[{'name': 'statistics'}]
        )

        url = url_for('dcat.read_catalog',
                      _format='ttl',
                      fq='tags:economy')


        response = app.get(url)
        content = response.body
        p = RDFParser()
        p.parse(content, _format='turtle')

        dcat_datasets = [d for d in p.datasets()]
        assert len(dcat_datasets) == 2
        assert dcat_datasets[0]['title'] in [dataset1['title'], dataset2['title']]
        assert dcat_datasets[1]['title'] in [dataset1['title'], dataset2['title']]

    @pytest.mark.ckan_config('ckanext.dcat.datasets_per_page', 10)
    def test_catalog_pagination(self, app):

        for i in range(12):
            factories.Dataset()

        url = url_for('dcat.read_catalog', _format='rdf')

        response = app.get(url)

        content = response.body

        g = Graph()
        g.parse(data=content, format='xml')

        assert len([d for d in g.subjects(RDF.type, DCAT.Dataset)]) == 10

        pagination = [o for o in g.subjects(RDF.type, HYDRA.PagedCollection)][0]

        assert self._object_value(g, pagination, HYDRA.totalItems) == '12'

        assert self._object_value(g, pagination, HYDRA.itemsPerPage) == '10'

        assert (_sort_query_params(self._object_value(g, pagination, HYDRA.firstPage)) ==
            _sort_query_params(url_for('dcat.read_catalog', _format='rdf', page=1, _external=True)))

        assert (_sort_query_params(self._object_value(g, pagination, HYDRA.nextPage)) ==
            _sort_query_params(url_for('dcat.read_catalog', _format='rdf', page=2, _external=True)))

        assert (_sort_query_params(self._object_value(g, pagination, HYDRA.lastPage)) ==
            _sort_query_params(url_for('dcat.read_catalog', _format='rdf', page=2, _external=True)))

    @pytest.mark.ckan_config('ckanext.dcat.datasets_per_page', 10)
    def test_catalog_pagination_parameters(self, app):

        for i in range(12):
            factories.Dataset()

        url = url_for('dcat.read_catalog', _format='rdf', modified_since='2018-03-22', extra_param='test')

        response = app.get(url)

        content = response.body

        g = Graph()
        g.parse(data=content, format='xml')


        pagination = [o for o in g.subjects(RDF.type, HYDRA.PagedCollection)][0]

        assert self._object_value(g, pagination, HYDRA.itemsPerPage) == '10'

        assert (
            _sort_query_params(self._object_value(g, pagination, HYDRA.firstPage)) ==
            _sort_query_params(url_for('dcat.read_catalog', _format='rdf', page=1, _external=True, modified_since='2018-03-22'))
        )

    def test_catalog_profiles_not_found(self, app):

        url = url_for('dcat.read_catalog', _format='jsonld', profiles='nope')

        response = app.get(url, status=409)

        assert 'Unknown RDF profiles: nope' in response.body


@pytest.mark.usefixtures('with_plugins', 'clean_db', 'clean_index')
class TestAcceptHeader():
    '''
    ckanext.dcat.enable_content_negotiation is enabled on test.ini
    '''

    def test_dataset_basic(self, app):

        dataset = factories.Dataset()

        url = url_for('dataset.read', id=dataset['name'])

        headers = {'Accept': 'application/ld+json'}

        response = app.get(url, headers=headers)

        assert response.headers['Content-Type'] == 'application/ld+json'

    def test_dataset_multiple(self, app):

        dataset = factories.Dataset()

        url = url_for('dataset.read', id=dataset['name'])

        headers = {'Accept': 'text/csv; q=1.0, text/turtle; q=0.6, application/ld+json; q=0.3'}

        response = app.get(url, headers=headers)

        assert response.headers['Content-Type'] == 'text/turtle'

    def test_dataset_not_supported_returns_html(self, app):

        dataset = factories.Dataset()

        url = url_for('dataset.read', id=dataset['name'])

        headers = {'Accept': 'image/gif'}

        response = app.get(url, headers=headers)

        assert response.headers['Content-Type'] == 'text/html; charset=utf-8'

    def test_dataset_no_header_returns_html(self, app):

        dataset = factories.Dataset()

        url = url_for('dataset.read', id=dataset['name'])

        response = app.get(url)

        assert response.headers['Content-Type'] == 'text/html; charset=utf-8'

    def test_catalog_basic(self, app):

        url = url_for('home')

        headers = {'Accept': 'application/ld+json'}

        response = app.get(url, headers=headers)

        assert response.headers['Content-Type'] == 'application/ld+json'

    def test_catalog_multiple(self, app):

        url = url_for('home')

        headers = {'Accept': 'text/csv; q=1.0, text/turtle; q=0.6, application/ld+json; q=0.3'}

        response = app.get(url, headers=headers)

        assert response.headers['Content-Type'] == 'text/turtle'

    def test_catalog_not_supported_returns_html(self, app):

        url = url_for('home')

        headers = {'Accept': 'image/gif'}

        response = app.get(url, headers=headers)

        assert response.headers['Content-Type'] == 'text/html; charset=utf-8'

    def test_catalog_no_header_returns_html(self, app):

        url = url_for('home')

        response = app.get(url)

        assert response.headers['Content-Type'] == 'text/html; charset=utf-8'


@pytest.mark.usefixtures('with_plugins', 'clean_db', 'clean_index')
class TestTranslations():

    def __init__(self):
        if p.toolkit.check_ckan_version(max_version='2.4.99'):
            pytest.skip('ITranslations not available on CKAN < 2.5')

    def test_labels_default(self, app):

        dataset = factories.Dataset(extras=[
            {'key': 'version_notes', 'value': 'bla'}
        ])

        url = url_for('dataset.read', id=dataset['name'])

        response = app.get(url)

        assert 'Version notes' in response.body

    def test_labels_translated(self, app):

        dataset = factories.Dataset(extras=[
            {'key': 'version_notes', 'value': 'bla'}
        ])

        url = url_for('dataset.read', id=dataset['name'], locale='ca')

        response = app.get(url)

        assert 'Notes de la versió' in response.body

    @pytest.mark.ckan_config('ckanext.dcat.translate_keys', True)
    def test_labels_enable_by_config(self, app):
        dataset = factories.Dataset(extras=[
            {'key': 'version_notes', 'value': 'bla'}
        ])

        url = url_for('dataset.read', id=dataset['name'], locale='ca')

        response = app.get(url)

        assert 'Notes de la versió' in response.body
        assert not 'Version notes' in response.body

    @pytest.mark.ckan_config('ckanext.dcat.translate_keys', False)
    def test_labels_disable_by_config(self, app):
        dataset = factories.Dataset(extras=[
            {'key': 'version_notes', 'value': 'bla'}
        ])

        url = url_for('dataset.read', id=dataset['name'], locale='ca')

        response = app.get(url)

        assert not 'Notes de la versió' in response.body
        assert not 'Version notes' in response.body
        assert 'version_notes' in response.body


@pytest.mark.usefixtures('with_plugins', 'clean_db', 'clean_index')
class TestStructuredData():

    @pytest.mark.ckan_config('ckan.plugins', 'dcat structured_data')
    def test_structured_data_generated(self, app):

        dataset = factories.Dataset(
            notes='test description'
        )

        url = url_for('dataset.read', id=dataset['name'])

        response = app.get(url)

        assert '<script type="application/ld+json">' in response.body
        assert '"schema:description": "test description"' in response.body

    def test_structured_data_not_generated(self, app):

        dataset = factories.Dataset(
            notes='test description'
        )

        url = url_for('dataset.read', id=dataset['name'])

        response = app.get(url)
        assert not '<script type="application/ld+json">' in response.body
