import nose

from routes import url_for

try:
    from ckan.tests import helpers, factories
except ImportError:
    from ckan.new_tests import helpers, factories

from ckanext.dcat.processors import RDFParser

eq_ = nose.tools.eq_
assert_true = nose.tools.assert_true


class TestEndpoints(helpers.FunctionalTestBase):

    @classmethod
    def teardown_class(cls):
        helpers.reset_db()

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
