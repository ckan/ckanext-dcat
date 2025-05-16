# test
import json
import logging
from pprint import pprint

import pytest
from ckan.tests.helpers import call_action

from ckanext.dcat.processors import RDFParser
from ckanext.dcat.tests.utils import BaseParseTest

log = logging.getLogger(__name__)


@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.plugins", "dcat scheming_datasets")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas", "ckanext.dcat.schemas:health_dcat_ap.yaml"
)
@pytest.mark.ckan_config(
    "scheming.presets",
    "ckanext.scheming:presets.json ckanext.dcat.schemas:presets.yaml",
)
@pytest.mark.ckan_config("ckanext.dcat.rdf.profiles", "euro_health_dcat_ap")
class TestSchemingParseSupport(BaseParseTest):
    def test_e2e_dcat_to_ckan(self):
        """
        Parse a DCAT RDF graph into a CKAN dataset dict, create a dataset with
        package_create and check that all expected fields are there
        """

        contents = self._get_file_contents("dcat/dataset_health.ttl")

        p = RDFParser()

        p.parse(contents, _format="turtle")

        datasets = [d for d in p.datasets()]

        assert len(datasets) == 1

        dataset_dict = datasets[0]

        dataset_dict["name"] = "test-dcat-1"
        dataset = call_action("package_create", **dataset_dict)

        # Core fields

        assert dataset["title"] == "HealthDCAT-AP test dataset"
        assert (
            dataset["notes"]
            == "This dataset is an example of using HealthDCAT-AP in CKAN"
        )

        assert sorted([t["name"] for t in dataset["tags"]]) == [
            "Test 1",
            "Test 2",
            "Test 3",
        ]

        # Standard fields
        assert dataset["version_notes"] == "Dataset continuously updated"
        assert dataset["identifier"] == "http://example.com/dataset/1234567890"
        assert (
            dataset["frequency"]
            == "http://publications.europa.eu/resource/authority/frequency/DAILY"
        )
        assert (
            dataset["access_rights"]
            == "http://publications.europa.eu/resource/authority/access-right/NON_PUBLIC"
        )
        assert (
            dataset["provenance"]
            == "This example dataset is partly sourced from TEHDAS2"
        )

        # Hard to map (example uses a blank node which doesn't work well in CKAN)
        # assert dataset["dcat_type"] == "test-type"

        assert dataset["issued"] == "2024-01-01T00:00:00+00:00"
        assert dataset["modified"] == "2024-12-31T23:59:59+00:00"
        assert dataset["temporal_resolution"] == "P1D"

        assert dataset["analytics"] == ["http://example.com/analytics"]
        assert sorted(dataset["code_values"]) == [
            "http://example.com/code1",
            "http://example.com/code2",
        ]
        assert sorted(dataset["coding_system"]) == [
            "http://www.wikidata.org/entity/P1690",
            "http://www.wikidata.org/entity/P4229",
        ]

        assert dataset["spatial_coverage"] == [
            {
                "uri": "http://publications.europa.eu/resource/authority/country/BEL",
            }
        ]

        # List fields
        assert sorted(dataset["conforms_to"]) == [
            "http://www.wikidata.org/entity/Q19597236"
        ]
        assert sorted(dataset["language"]) == [
            "http://publications.europa.eu/resource/authority/language/ENG",
            "http://publications.europa.eu/resource/authority/language/FRA",
            "http://publications.europa.eu/resource/authority/language/NLD",
        ]
        assert sorted(dataset["theme"]) == [
            "http://publications.europa.eu/resource/authority/data-theme/HEAL"
        ]

        assert sorted(dataset["is_referenced_by"]) == [
            "https://doi.org/10.1038/sdata.2016.18",
            "https://dx.doi.org/10.1002/jmri.28679",
        ]
        assert sorted(dataset["applicable_legislation"]) == [
            "http://data.europa.eu/eli/reg/2022/868/oj",
        ]

        # Repeating subfields
        assert dataset["contact"][0]["name"] == "Contact Point"
        assert dataset["contact"][0]["email"] == "contact@example.com"

        assert dataset["publisher"][0]["name"] == "Contact Point"
        assert dataset["publisher"][0]["email"] == "info@example.com"
        assert dataset["publisher"][0]["url"] == "https://healthdata.nl"

        assert len(dataset["qualified_relation"]) == 1
        assert (
            dataset["qualified_relation"][0]["relation"]
            == "http://example.com/dataset/3.141592"
        )
        assert (
            dataset["qualified_relation"][0]["role"]
            == "http://www.iana.org/assignments/relation/related"
        )

        assert dataset["temporal_coverage"][0]["start"] == "2020-03-01"
        assert dataset["temporal_coverage"][0]["end"] == "2024-12-31"

        ## HealthDCAT specific
        assert sorted(dataset["health_theme"]) == [
            "http://www.wikidata.org/entity/Q58624061",
            "http://www.wikidata.org/entity/Q7907952",
        ]

        assert dataset["legal_basis"] == ["https://w3id.org/dpv#Consent"]

        assert dataset["hdab"][0]["name"] == "EU Health Data Access Body"
        assert dataset["hdab"][0]["email"] == "hdab@example.com"
        assert dataset["hdab"][0]["url"] == "https://www.example.com/hdab"

        # CKAN converts these to strings, but also converts back to decimal/nonneg int
        assert dataset["min_typical_age"] == "0"
        assert dataset["max_typical_age"] == "110"
        assert dataset["number_of_records"] == "123456789"
        assert dataset["number_of_unique_individuals"] == "7654321"

        assert sorted(dataset["personal_data"]) == [
            "https://w3id.org/dpv/dpv-pd#Age",
            "https://w3id.org/dpv/dpv-pd#Gender",
            "https://w3id.org/dpv/dpv-pd#HealthRecord",
        ]

        assert dataset["population_coverage"] == [
            "This example includes a very non-descript population"
        ]
        assert dataset["publisher_note"] == [
            "Health-RI is the Dutch health care initiative to build an integrated health data infrastructure for research and innovation."
        ]
        assert dataset["publisher_type"] == [
            "http://example.com/publisherType/undefined"
        ]
        assert dataset["trusted_data_holder"] is True

        assert dataset["purpose"] == ["https://w3id.org/dpv#AcademicResearch"]

        assert dataset["retention_period"] == [
            {
                "start": "2020-03-01",
                "end": "2034-12-31",
            }
        ]
