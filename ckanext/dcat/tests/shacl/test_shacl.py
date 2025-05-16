import json
import os

from rdflib import URIRef
from pyshacl import validate
import pytest

from ckan.tests.helpers import call_action

from ckanext.dcat.processors import RDFSerializer
from ckanext.dcat.tests.utils import get_file_contents


def _get_shacl_file_path(file_name):
    return os.path.join(os.path.dirname(__file__), file_name)


generated_graphs = {}


def graph_from_dataset(file_name):
    global generated_graphs

    if not generated_graphs.get(file_name):
        if not file_name.startswith("ckan/"):
            file_name = "ckan/" + file_name
        dataset_dict = json.loads(get_file_contents(file_name))
        dataset = call_action("package_create", **dataset_dict)

        s = RDFSerializer()
        s.graph_from_dataset(dataset)

        generated_graphs[file_name] = s.g

    return generated_graphs[file_name]


def _results_count(results_graph):
    return len(
        [
            t
            for t in results_graph.triples(
                (None, URIRef("http://www.w3.org/ns/shacl#result"), None)
            )
        ]
    )


@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.plugins", "dcat scheming_datasets")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas", "ckanext.dcat.schemas:dcat_ap_full.yaml"
)
@pytest.mark.ckan_config(
    "scheming.presets",
    "ckanext.scheming:presets.json ckanext.dcat.schemas:presets.yaml",
)
@pytest.mark.ckan_config(
    "ckanext.dcat.rdf.profiles", "euro_dcat_ap_2 euro_dcat_ap_scheming"
)
def test_validate_dcat_ap_2_graph_shapes():

    graph = graph_from_dataset("ckan_full_dataset_dcat_ap.json")

    # dcat-ap_2.1.1_shacl_shapes.ttl: constraints concerning existance, domain and
    # literal range, and cardinalities.
    path = _get_shacl_file_path("dcat-ap_2.1.1_shacl_shapes.ttl")
    r = validate(graph, shacl_graph=path)
    conforms, results_graph, results_text = r
    assert conforms, results_text


@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.plugins", "dcat scheming_datasets")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas", "ckanext.dcat.schemas:dcat_ap_full.yaml"
)
@pytest.mark.ckan_config(
    "scheming.presets",
    "ckanext.scheming:presets.json ckanext.dcat.schemas:presets.yaml",
)
@pytest.mark.ckan_config(
    "ckanext.dcat.rdf.profiles", "euro_dcat_ap_2 euro_dcat_ap_scheming"
)
def test_validate_dcat_ap_2_graph_shapes_recommended():

    graph = graph_from_dataset("ckan_full_dataset_dcat_ap.json")

    # dcat-ap_2.1.1_shacl_shapes_recommended.ttl: constraints concerning existance
    # of recommended properties.
    path = _get_shacl_file_path("dcat-ap_2.1.1_shacl_shapes_recommended.ttl")
    r = validate(graph, shacl_graph=path)
    conforms, results_graph, results_text = r
    assert conforms, results_text


@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.plugins", "dcat")
@pytest.mark.ckan_config("ckanext.dcat.rdf.profiles", "euro_dcat_ap_2")
def test_validate_dcat_ap_2_legacy_graph_shapes():

    graph = graph_from_dataset("ckan_full_dataset_dcat_ap_legacy.json")

    # dcat-ap_2.1.1_shacl_shapes.ttl: constraints concerning existance, domain and
    # literal range, and cardinalities.
    path = _get_shacl_file_path("dcat-ap_2.1.1_shacl_shapes.ttl")
    r = validate(graph, shacl_graph=path)
    conforms, results_graph, results_text = r
    assert conforms, results_text


@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.plugins", "dcat")
@pytest.mark.ckan_config("ckanext.dcat.rdf.profiles", "euro_dcat_ap_2")
def test_validate_dcat_ap_2_legacy_graph_shapes_recommended():

    graph = graph_from_dataset("ckan_full_dataset_dcat_ap_legacy.json")

    # dcat-ap_2.1.1_shacl_shapes_recommended.ttl: constraints concerning existance
    # of recommended properties.
    path = _get_shacl_file_path("dcat-ap_2.1.1_shacl_shapes_recommended.ttl")
    r = validate(graph, shacl_graph=path)
    conforms, results_graph, results_text = r
    assert conforms, results_text


@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.plugins", "dcat scheming_datasets")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas", "ckanext.dcat.schemas:dcat_ap_full.yaml"
)
@pytest.mark.ckan_config(
    "scheming.presets",
    "ckanext.scheming:presets.json ckanext.dcat.schemas:presets.yaml",
)
@pytest.mark.ckan_config(
    "ckanext.dcat.rdf.profiles", "euro_dcat_ap_2 euro_dcat_ap_scheming"
)
def test_validate_dcat_ap_2_graph_shapes_range():

    graph = graph_from_dataset("ckan_full_dataset_dcat_ap_vocabularies.json")

    # dcat-ap_2.1.1_shacl_range.ttl: constraints concerning object range
    path = _get_shacl_file_path("dcat-ap_2.1.1_shacl_range.ttl")
    r = validate(graph, shacl_graph=path)
    conforms, results_graph, results_text = r

    failures = [
        str(t[2])
        for t in results_graph.triples(
            (
                None,
                URIRef("http://www.w3.org/ns/shacl#resultMessage"),
                None,
            )
        )
    ]

    known_failures = [
        "Value does not have class skos:Concept",
        "Value does not have class dcat:Dataset",
        # Qualified relations
        "Value does not conform to Shape :DcatResource_Shape. See details for more information.",
        "The node is either a Catalog, Dataset or a DataService",
    ]

    assert set(failures) - set(known_failures) == set(), results_text


@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.plugins", "dcat scheming_datasets")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas", "ckanext.dcat.schemas:dcat_ap_full.yaml"
)
@pytest.mark.ckan_config(
    "scheming.presets",
    "ckanext.scheming:presets.json ckanext.dcat.schemas:presets.yaml",
)
@pytest.mark.ckan_config("ckanext.dcat.rdf.profiles", "euro_dcat_ap_3")
def test_validate_dcat_ap_3_graph():

    graph = graph_from_dataset("ckan_full_dataset_dcat_ap_vocabularies.json")

    path = _get_shacl_file_path("dcat-ap_3_shacl_shapes.ttl")
    r = validate(graph, shacl_graph=path)
    conforms, results_graph, results_text = r

    failures = [
        str(t[2])
        for t in results_graph.triples(
            (
                None,
                URIRef("http://www.w3.org/ns/shacl#resultMessage"),
                None,
            )
        )
    ]

    known_failures = [
        "Value does not have class skos:Concept",
        "Value does not have class dcat:Dataset",
    ]

    assert set(failures) - set(known_failures) == set(), results_text


@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.plugins", "dcat scheming_datasets")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas", "ckanext.dcat.schemas:dcat_us_full.yaml"
)
@pytest.mark.ckan_config(
    "scheming.presets",
    "ckanext.scheming:presets.json ckanext.dcat.schemas:presets.yaml",
)
@pytest.mark.ckan_config("ckanext.dcat.rdf.profiles", "dcat_us_3")
def test_validate_dcat_us_3_graph():

    graph = graph_from_dataset("ckan_full_dataset_dcat_us_vocabularies.json")

    path = _get_shacl_file_path("dcat-us_3.0_shacl_shapes.ttl")
    r = validate(graph, shacl_graph=path)
    conforms, results_graph, results_text = r

    failures = [
        str(t[2])
        for t in results_graph.triples(
            (
                None,
                URIRef("http://www.w3.org/ns/shacl#resultMessage"),
                None,
            )
        )
    ]

    known_failures = [
        "Value does not have class skos:Concept",
        "Value does not have class dcat:Dataset",
    ]

    assert set(failures) - set(known_failures) == set(), results_text
