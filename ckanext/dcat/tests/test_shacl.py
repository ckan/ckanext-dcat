import json
import os
from random import randrange

from pyshacl import validate
import pytest

from ckan.tests.helpers import call_action

from ckanext.dcat.processors import RDFSerializer
from ckanext.dcat.tests.utils import get_file_contents


def _get_shacl_file_path(file_name):
    return os.path.join(os.path.dirname(__file__), "shacl", file_name)


generated_graphs = {}


def graph_from_dataset(file_name):
    global generated_graphs

    if not generated_graphs.get(file_name):
        if not file_name.startswith("ckan/"):
            file_name = "ckan/" + file_name
        dataset_dict = json.loads(get_file_contents(file_name))
        dataset_dict["name"] += "-" + str(randrange(0, 1000))
        dataset = call_action("package_create", **dataset_dict)

        s = RDFSerializer()
        s.graph_from_dataset(dataset)

        generated_graphs[file_name] = s.g

    return generated_graphs[file_name]


@pytest.mark.usefixtures("with_plugins")
@pytest.mark.ckan_config("ckan.plugins", "dcat scheming_datasets")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas", "ckanext.dcat.schemas:dcat_ap_2.1_full.yaml"
)
@pytest.mark.ckan_config(
    "scheming.presets",
    "ckanext.scheming:presets.json ckanext.dcat.schemas:presets.yaml",
)
@pytest.mark.ckan_config(
    "ckanext.dcat.rdf.profiles", "euro_dcat_ap_2 euro_dcat_ap_scheming"
)
def test_validate_dcat_ap_2_graph_shapes():

    graph = graph_from_dataset("ckan_full_dataset_dcat_ap_2.json")

    # dcat-ap_2.1.1_shacl_shapes.ttl: constraints concerning existance, domain and
    # literal range, and cardinalities.
    path = _get_shacl_file_path("dcat-ap_2.1.1_shacl_shapes.ttl")
    r = validate(graph, shacl_graph=path)
    conforms, results_graph, results_text = r
    assert conforms, results_text


@pytest.mark.usefixtures("with_plugins")
@pytest.mark.ckan_config("ckan.plugins", "dcat scheming_datasets")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas", "ckanext.dcat.schemas:dcat_ap_2.1_full.yaml"
)
@pytest.mark.ckan_config(
    "scheming.presets",
    "ckanext.scheming:presets.json ckanext.dcat.schemas:presets.yaml",
)
@pytest.mark.ckan_config(
    "ckanext.dcat.rdf.profiles", "euro_dcat_ap_2 euro_dcat_ap_scheming"
)
def test_validate_dcat_ap_2_graph_shapes_recommended():

    graph = graph_from_dataset("ckan_full_dataset_dcat_ap_2.json")

    # dcat-ap_2.1.1_shacl_shapes_recommended.ttl: constraints concerning existance
    # of recommended properties.
    path = _get_shacl_file_path("dcat-ap_2.1.1_shacl_shapes_recommended.ttl")
    r = validate(graph, shacl_graph=path)
    conforms, results_graph, results_text = r
    assert conforms, results_text


@pytest.mark.usefixtures("with_plugins")
@pytest.mark.ckan_config("ckan.plugins", "dcat")
@pytest.mark.ckan_config("ckanext.dcat.rdf.profiles", "euro_dcat_ap_2")
def test_validate_dcat_ap_2_legacy_graph_shapes():

    graph = graph_from_dataset("ckan_full_dataset_dcat_ap_2_legacy.json")

    # dcat-ap_2.1.1_shacl_shapes.ttl: constraints concerning existance, domain and
    # literal range, and cardinalities.
    path = _get_shacl_file_path("dcat-ap_2.1.1_shacl_shapes.ttl")
    r = validate(graph, shacl_graph=path)
    conforms, results_graph, results_text = r
    assert conforms, results_text


@pytest.mark.usefixtures("with_plugins")
@pytest.mark.ckan_config("ckan.plugins", "dcat")
@pytest.mark.ckan_config("ckanext.dcat.rdf.profiles", "euro_dcat_ap_2")
def test_validate_dcat_ap_2_legacy_graph_shapes_recommended():

    graph = graph_from_dataset("ckan_full_dataset_dcat_ap_2_legacy.json")

    # dcat-ap_2.1.1_shacl_shapes_recommended.ttl: constraints concerning existance
    # of recommended properties.
    path = _get_shacl_file_path("dcat-ap_2.1.1_shacl_shapes_recommended.ttl")
    r = validate(graph, shacl_graph=path)
    conforms, results_graph, results_text = r
    assert conforms, results_text
