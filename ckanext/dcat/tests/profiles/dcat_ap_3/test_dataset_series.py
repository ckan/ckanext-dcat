import json

import pytest
from rdflib.term import URIRef

from ckan.plugins.toolkit import check_ckan_version
from ckan.tests import factories
from ckan.tests.helpers import call_action
from ckanext.dcat.tests.utils import BaseSerializeTest
from ckanext.dcat.processors import RDFSerializer
from ckanext.dcat import utils
from ckanext.dcat.profiles import RDF, DCAT, DCT


@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.plugins", "dcat scheming_datasets dataset_series")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas",
    "ckanext.dcat.schemas:dcat_ap_dataset_series.yaml "
    "ckanext.dcat.schemas:dcat_ap_in_series.yaml",
)
@pytest.mark.ckan_config(
    "scheming.presets",
    "ckanext.scheming:presets.json "
    "ckanext.dcat.schemas:presets.yaml "
    "ckanext.dataset_series.schemas:presets.yaml",
)
@pytest.mark.ckan_config("ckanext.dcat.rdf.profiles", "euro_dcat_ap_3")
@pytest.mark.skipif(
    not check_ckan_version(min_version="2.10.0"),
    reason="ckanext-dataset-series requires CKAN>=2.10",
)
class TestEuroDCATAP3ProfileSerializeDatasetSeries(BaseSerializeTest):
    def test_e2e_ckan_to_dcat(self):
        """
        Create a dataset series using the scheming schema, check that fields
        are exposed in the DCAT RDF graph
        """

        dataset_series_dict = json.loads(
            self._get_file_contents("ckan/ckan_dcat_ap_dataset_series.json")
        )

        dataset_series = call_action("package_create", **dataset_series_dict)

        # Make sure schema was used
        assert dataset_series["type"] == "dataset_series"
        assert dataset_series["contact"][0]["name"] == "Contact 1"

        s = RDFSerializer()
        g = s.g

        dataset_series_ref = s.graph_from_dataset(dataset_series)

        assert str(dataset_series_ref) == utils.dataset_uri(dataset_series)

        assert self._triple(g, dataset_series_ref, RDF.type, DCAT.DatasetSeries)
        assert self._triple(g, dataset_series_ref, DCT.title, dataset_series["title"])
        assert self._triple(
            g, dataset_series_ref, DCT.description, dataset_series["notes"]
        )

    def test_dataset_series_navigation(self):

        dataset_series = factories.Dataset(
            type="dataset_series",
            title="Test Dataset Series",
            notes="Some Dataset Series",
            series_order_field="metadata_created",
            series_order_type="date",
        )

        datasets_in_series = []
        for x in range(1, 4):

            datasets_in_series.append(
                factories.Dataset(
                    title=f"Test dataset {x}",
                    notes=f"Test dataset {x}",
                    in_series=dataset_series["id"],
                )
            )

        # Test dataset series navigation (first / last)

        # Call package_show to get the series navigation details included
        dataset_series = call_action("package_show", id=dataset_series["id"])

        s = RDFSerializer()
        g = s.g

        dataset_series_ref = s.graph_from_dataset(dataset_series)

        assert str(dataset_series_ref) == utils.dataset_uri(dataset_series)

        assert self._triple(
            g,
            dataset_series_ref,
            DCAT.first,
            URIRef(utils.dataset_uri(datasets_in_series[0])),
        )

        assert self._triple(
            g,
            dataset_series_ref,
            DCAT.last,
            URIRef(utils.dataset_uri(datasets_in_series[-1])),
        )

        # Test member datasets navigation (prev / next)

        first_dataset = call_action("package_show", id=datasets_in_series[0]["id"])

        dataset_ref = s.graph_from_dataset(first_dataset)

        assert str(dataset_ref) == utils.dataset_uri(first_dataset)

        assert self._triple(
            g,
            dataset_ref,
            DCAT.inSeries,
            URIRef(utils.dataset_uri(dataset_series)),
        )

        assert not self._triple(
            g,
            dataset_ref,
            DCAT.prev,
            None,
        )

        assert self._triple(
            g,
            dataset_ref,
            DCAT.next,
            URIRef(utils.dataset_uri(datasets_in_series[1])),
        )

        middle_dataset = call_action("package_show", id=datasets_in_series[1]["id"])

        dataset_ref = s.graph_from_dataset(middle_dataset)

        assert str(dataset_ref) == utils.dataset_uri(middle_dataset)

        assert self._triple(
            g,
            dataset_ref,
            DCAT.inSeries,
            URIRef(utils.dataset_uri(dataset_series)),
        )

        assert self._triple(
            g,
            dataset_ref,
            DCAT.prev,
            URIRef(utils.dataset_uri(datasets_in_series[0])),
        )

        assert self._triple(
            g,
            dataset_ref,
            DCAT.next,
            URIRef(utils.dataset_uri(datasets_in_series[2])),
        )

        last_dataset = call_action("package_show", id=datasets_in_series[2]["id"])

        dataset_ref = s.graph_from_dataset(last_dataset)

        assert str(dataset_ref) == utils.dataset_uri(last_dataset)

        assert self._triple(
            g,
            dataset_ref,
            DCAT.inSeries,
            URIRef(utils.dataset_uri(dataset_series)),
        )

        assert self._triple(
            g,
            dataset_ref,
            DCAT.prev,
            URIRef(utils.dataset_uri(datasets_in_series[1])),
        )

        assert not self._triple(
            g,
            dataset_ref,
            DCAT.next,
            None,
        )
