import os

from pyshacl import validate
import pytest

from ckan.tests.helpers import call_action

from ckanext.dcat.processors import RDFSerializer


dataset_dict = {
    # Core fields
    "name": "test-dataset",
    "title": "Test DCAT dataset",
    "notes": "Lorem ipsum",
    "url": "http://example.org/ds1",
    "version": "1.0b",
    "tags": [{"name": "Tag 1"}, {"name": "Tag 2"}],
    # Standard fields
    "issued": "2024-05-01",
    "modified": "2024-05-05",
    "identifier": "xx-some-dataset-id-yy",
    "frequency": "monthly",
    "provenance": "Statement about provenance",
    "dcat_type": "test-type",
    "version_notes": "Some version notes",
    "access_rights": "Statement about access rights",
    # List fields (lists)
    "alternate_identifier": ["alt-id-1", "alt-id-2"],
    "theme": [
        "https://example.org/uri/theme1",
        "https://example.org/uri/theme2",
        "https://example.org/uri/theme3",
    ],
    "language": ["en", "ca", "es"],
    "documentation": ["https://example.org/some-doc.html"],
    "conforms_to": ["Standard 1", "Standard 2"],
    "is_referenced_by": [
        "https://doi.org/10.1038/sdata.2018.22",
        "test_isreferencedby",
    ],
    "applicable_legislation": [
        "http://data.europa.eu/eli/reg_impl/2023/138/oj",
        "http://data.europa.eu/eli/reg_impl/2023/138/oj_alt",
    ],
    # Repeating subfields
    "contact": [
        {"name": "Contact 1", "email": "contact1@example.org"},
        {"name": "Contact 2", "email": "contact2@example.org"},
    ],
    "publisher": [
        {
            "name": "Test Publisher",
            "email": "publisher@example.org",
            "url": "https://example.org",
            "type": "public_body",
        },
    ],
    "temporal_coverage": [
        {"start": "1905-03-01", "end": "2013-01-05"},
    ],
    "temporal_resolution": "PT15M",
    "spatial_coverage": [
        {
            "geom": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [11.9936, 54.0486],
                        [11.9936, 54.2466],
                        [12.3045, 54.2466],
                        [12.3045, 54.0486],
                        [11.9936, 54.0486],
                    ]
                ],
            },
            "text": "Tarragona",
            "uri": "https://sws.geonames.org/6361390/",
            "bbox": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-2.1604, 42.7611],
                        [-2.0938, 42.7611],
                        [-2.0938, 42.7931],
                        [-2.1604, 42.7931],
                        [-2.1604, 42.7611],
                    ]
                ],
            },
            "centroid": {"type": "Point", "coordinates": [1.26639, 41.12386]},
        }
    ],
    "spatial_resolution_in_meters": 1.5,
    "resources": [
        {
            "name": "Resource 1",
            "description": "Some description",
            "url": "https://example.com/data.csv",
            "format": "CSV",
            "availability": "http://publications.europa.eu/resource/authority/planned-availability/EXPERIMENTAL",
            "compress_format": "http://www.iana.org/assignments/media-types/application/gzip",
            "package_format": "http://publications.europa.eu/resource/authority/file-type/TAR",
            "size": 12323,
            "hash": "4304cf2e751e6053c90b1804c89c0ebb758f395a",
            "hash_algorithm": "http://spdx.org/rdf/terms#checksumAlgorithm_sha1",
            "status": "http://purl.org/adms/status/Completed",
            "access_url": "https://example.com/data.csv",
            "download_url": "https://example.com/data.csv",
            "issued": "2024-05-01T01:20:33",
            "modified": "2024-05-05T09:33:20",
            "license": "http://creativecommons.org/licenses/by/3.0/",
            "rights": "Some stament about rights",
            "language": ["en", "ca", "es"],
            "access_services": [
                {
                    "title": "Access Service 1",
                    "endpoint_description": "https://example.org/endpoint_description",
                    "endpoint_url": [
                        "https://example.org/access_service/1",
                        "https://example.org/access_service/2",
                    ],
                    "serves_dataset": [
                        "https://example.org/dataset/1",
                        "https://example.org/dataset/2",
                    ],
                }
            ],
        }
    ],
}


def _get_shacl_file_path(file_name):
    return os.path.join(os.path.dirname(__file__), "shacl", file_name)


generated_graph = None


@pytest.fixture
def graph():
    global generated_graph

    if not generated_graph:
        dataset = call_action("package_create", **dataset_dict)

        s = RDFSerializer()
        s.graph_from_dataset(dataset)

        generated_graph = s.g

    return generated_graph


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
def test_validate_dcat_ap_2_graph_shapes(graph):

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
def test_validate_dcat_ap_2_graph_shapes_recommended(graph):

    # dcat-ap_2.1.1_shacl_shapes_recommended.ttl: constraints concerning existance
    # of recommended properties.
    path = _get_shacl_file_path("dcat-ap_2.1.1_shacl_shapes_recommended.ttl")
    r = validate(graph, shacl_graph=path)
    conforms, results_graph, results_text = r
    assert conforms, results_text
