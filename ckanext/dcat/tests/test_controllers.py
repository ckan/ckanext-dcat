import time
import nose

from ckan.lib.helpers import url_for

from rdflib import Graph

try:
    from ckan.tests import helpers, factories
except ImportError:
    from ckan.new_tests import helpers, factories

from ckanext.dcat.processors import RDFParser
from ckanext.dcat.profiles import RDF, DCAT
from ckanext.dcat.processors import HYDRA

eq_ = nose.tools.eq_
assert_true = nose.tools.assert_true


class TestEndpoints(helpers.FunctionalTestBase):

    @classmethod
    def teardown_class(cls):
        helpers.reset_db()

    def _object_value(self, graph, subject, predicate):

        objects = [o for o in graph.objects(subject, predicate)]
        return unicode(objects[0]) if objects else None

    def test_dataset_default(self):

        dataset = factories.Dataset(
            notes='Test dataset'
        )

        url = url_for('dcat_dataset', _id=dataset['id'], _format='rdf')

        app = self._get_test_app()

        response = app.get(url)

        eq_(response.headers['Content-Type'], 'application/rdf+xml')

        content = response.body

        # Parse the contents to check it's an actual serialization
        p = RDFParser()

        p.parse(content, _format='xml')

        dcat_datasets = [d for d in p.datasets()]

        eq_(len(dcat_datasets), 1)

        dcat_dataset = dcat_datasets[0]

        eq_(dcat_dataset['title'], dataset['title'])
        eq_(dcat_dataset['notes'], dataset['notes'])

    def test_dataset_xml(self):

        dataset = factories.Dataset(
            notes='Test dataset'
        )

        url = url_for('dcat_dataset', _id=dataset['id'], _format='xml')

        app = self._get_test_app()

        response = app.get(url)

        eq_(response.headers['Content-Type'], 'application/rdf+xml')

        content = response.body

        # Parse the contents to check it's an actual serialization
        p = RDFParser()

        p.parse(content, _format='xml')

        dcat_datasets = [d for d in p.datasets()]

        eq_(len(dcat_datasets), 1)

        dcat_dataset = dcat_datasets[0]

        eq_(dcat_dataset['title'], dataset['title'])
        eq_(dcat_dataset['notes'], dataset['notes'])

    def test_dataset_ttl(self):

        dataset = factories.Dataset(
            notes='Test dataset'
        )

        url = url_for('dcat_dataset', _id=dataset['id'], _format='ttl')

        app = self._get_test_app()

        response = app.get(url)

        eq_(response.headers['Content-Type'], 'text/turtle')

        content = response.body

        # Parse the contents to check it's an actual serialization
        p = RDFParser()

        p.parse(content, _format='turtle')

        dcat_datasets = [d for d in p.datasets()]

        eq_(len(dcat_datasets), 1)

        dcat_dataset = dcat_datasets[0]

        eq_(dcat_dataset['title'], dataset['title'])
        eq_(dcat_dataset['notes'], dataset['notes'])

    def test_dataset_n3(self):

        dataset = factories.Dataset(
            notes='Test dataset'
        )

        url = url_for('dcat_dataset', _id=dataset['id'], _format='n3')

        app = self._get_test_app()

        response = app.get(url)

        eq_(response.headers['Content-Type'], 'text/n3')

        content = response.body

        # Parse the contents to check it's an actual serialization
        p = RDFParser()

        p.parse(content, _format='n3')

        dcat_datasets = [d for d in p.datasets()]

        eq_(len(dcat_datasets), 1)

        dcat_dataset = dcat_datasets[0]

        eq_(dcat_dataset['title'], dataset['title'])
        eq_(dcat_dataset['notes'], dataset['notes'])

    def test_catalog_default(self):

        for i in xrange(4):
            factories.Dataset()

        url = url_for('dcat_catalog', _format='rdf')

        app = self._get_test_app()

        response = app.get(url)

        eq_(response.headers['Content-Type'], 'application/rdf+xml')

        content = response.body

        # Parse the contents to check it's an actual serialization
        p = RDFParser()

        p.parse(content, _format='xml')

        dcat_datasets = [d for d in p.datasets()]

        eq_(len(dcat_datasets), 4)

    def test_catalog_ttl(self):

        for i in xrange(4):
            factories.Dataset()

        url = url_for('dcat_catalog', _format='ttl')

        app = self._get_test_app()

        response = app.get(url)

        eq_(response.headers['Content-Type'], 'text/turtle')

        content = response.body

        # Parse the contents to check it's an actual serialization
        p = RDFParser()

        p.parse(content, _format='turtle')

        dcat_datasets = [d for d in p.datasets()]

        eq_(len(dcat_datasets), 4)

    def test_catalog_modified_date(self):

        dataset1 = factories.Dataset(title='First dataset')
        time.sleep(1)
        dataset2 = factories.Dataset(title='Second dataset')

        url = url_for('dcat_catalog',
                      _format='ttl',
                      modified_since=dataset2['metadata_modified'])

        app = self._get_test_app()

        response = app.get(url)

        content = response.body

        p = RDFParser()

        p.parse(content, _format='turtle')

        dcat_datasets = [d for d in p.datasets()]

        eq_(len(dcat_datasets), 1)

        eq_(dcat_datasets[0]['title'], dataset2['title'])

    def test_catalog_modified_date_wrong_date(self):

        url = url_for('dcat_catalog',
                      _format='ttl',
                      modified_since='wrong_date')

        app = self._get_test_app()

        app.get(url, status=409)

    @helpers.change_config('ckanext.dcat.datasets_per_page', 10)
    def test_catalog_pagination(self):

        for i in xrange(12):
            factories.Dataset()

        app = self._get_test_app()

        url = url_for('dcat_catalog', _format='rdf')

        response = app.get(url)

        content = response.body

        g = Graph()
        g.parse(data=content, format='xml')

        eq_(len([d for d in g.subjects(RDF.type, DCAT.Dataset)]), 10)

        pagination = [o for o in g.subjects(RDF.type, HYDRA.PagedCollection)][0]

        eq_(self._object_value(g, pagination, HYDRA.totalItems), '12')

        eq_(self._object_value(g, pagination, HYDRA.itemsPerPage), '10')

        eq_(self._object_value(g, pagination, HYDRA.firstPage),
            url_for('dcat_catalog', _format='rdf', page=1, host='localhost'))

        eq_(self._object_value(g, pagination, HYDRA.nextPage),
            url_for('dcat_catalog', _format='rdf', page=2, host='localhost'))

        eq_(self._object_value(g, pagination, HYDRA.lastPage),
            url_for('dcat_catalog', _format='rdf', page=2, host='localhost'))
