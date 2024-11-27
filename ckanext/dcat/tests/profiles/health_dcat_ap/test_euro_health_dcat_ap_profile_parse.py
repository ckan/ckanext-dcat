# test
import pytest
from ckan.tests.helpers import call_action

from ckanext.dcat.processors import RDFParser
from ckanext.dcat.tests.utils import BaseParseTest


@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.plugins", "dcat scheming_datasets")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas", "ckanext.dcat.schemas:healthdcat_ap.yaml"
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

        assert (
            dataset["title"]
            == "[Adapted] Linking of registers for COVID-19 vaccine surveillance"
        )
        assert (
            dataset["notes"]
            == "The LINK-VACC project links selected variables from existing registries..."
        )
        # assert dataset["url"] == "http://dataset.info.org"
        # assert dataset["version"] == "Project HDBP0250"
        # assert dataset["license_id"] == "cc-nc"
        assert sorted([t["name"] for t in dataset["tags"]]) == [
            "COVID-19",
            "Vaccination",
            "Vaccine effectiveness",
        ]

        # Standard fields
        assert dataset["version_notes"] == "Dataset continuously updated"
        assert (
            dataset["identifier"]
            == "http://fdp2.healthdataportal.eu/dataset/8bb235c9-7bcd-4290-a188-49fe33c2170c"
        )
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
            == "The data for the LINK-VACC project is sourced from..."
        )

        # Hard to map (example uses a blind node which doesn't work well in CKAN)
        # assert dataset["dcat_type"] == "test-type"

        assert dataset["issued"] == "2023-01-20T08:51:00+00:00"
        assert dataset["modified"] == "2024-10-09T00:00:00+00:00"
        assert dataset["temporal_resolution"] == "P1D"
        assert dataset["spatial_resolution_in_meters"] == "10.0"

        # List fields
        assert sorted(dataset["conforms_to"]) == [
            "https://www.wikidata.org/wiki/Q19597236"
        ]
        assert sorted(dataset["language"]) == [
            "http://publications.europa.eu/resource/authority/language/ENG",
            "http://publications.europa.eu/resource/authority/language/FRA",
            "http://publications.europa.eu/resource/authority/language/NLD",
        ]
        assert sorted(dataset["theme"]) == [
            "http://publications.europa.eu/resource/authority/data-theme/HEAL"
        ]
        # assert sorted(dataset["alternate_identifier"]) == [
        #     "alternate-identifier-1",
        #     "alternate-identifier-2",
        # ]
        # assert sorted(dataset["documentation"]) == [
        #     "http://dataset.info.org/doc1",
        #     "http://dataset.info.org/doc2",
        # ]

        # <> , <https://doi.org/10.1186/s13690-021-00709-x>;
        assert sorted(dataset["is_referenced_by"]) == [
            "https://doi.org/10.1136/jech-2023-220751",
            "https://doi.org/10.1186/s13690-021-00709-x",
        ]
        assert sorted(dataset["applicable_legislation"]) == [
            "http://data.europa.eu/eli/reg/2022/868/oj",
        ]
        # Repeating subfields

        assert dataset["contact"][0]["name"] == "Sciensano"
        assert dataset["contact"][0]["email"] == "covacsurv@sciensano.be"

        assert dataset["publisher"][0]["name"] == "Sciensano"
        assert dataset["publisher"][0]["email"] == "info@sciensano.be"
        assert dataset["publisher"][0]["url"] == "https://sciensano.be"
        # assert (
        #     dataset["publisher"][0]["type"]
        #     == "http://purl.org/adms/publishertype/NonProfitOrganisation"
        # )
        assert dataset["temporal_coverage"][0]["start"] == "2020-03-01"
        assert dataset["temporal_coverage"][0]["end"] == "2024-12-31"

        ## HealthDCAT specific
        assert sorted(dataset["health_theme"]) == [
            "https://www.wikidata.org/wiki/Q58624061",
            "https://www.wikidata.org/wiki/Q7907952",
        ]

        assert dataset["hdab"][0]["name"] == "Belgian Health Data Agency"
        assert dataset["hdab"][0]["email"] == "info@hda.fgov.be"
        assert dataset["hdab"][0]["url"] == "https://www.hda.belgium.be"

        assert dataset["min_typical_age"] == "0"
        assert dataset["max_typical_age"] == "110"
        assert dataset["number_of_records"] == "124866488"
        assert dataset["number_of_unique_individuals"] == "8914722"

        assert dataset["population_coverage"] == [
            "The population targeted by the LINK-VACC project comprises all individuals ..."
        ]
        assert dataset["publisher_note"] == [
            "Sciensano is a research institute and the national public health institute ..."
        ]

        assert dataset["retention_period"] == [
            {
                "start": "2020-03-01",
                "end": "2034-12-31",
            }
        ]

        # resource = dataset["resources"][0]

        # # Resources: core fields
        # assert resource["url"] == "http://www.bgs.ac.uk/gbase/geochemcd/home.html"

        # # Resources: standard fields
        # assert resource["license"] == "http://creativecommons.org/licenses/by-nc/2.0/"
        # assert resource["rights"] == "Some statement about rights"
        # assert resource["issued"] == "2012-05-11"
        # assert resource["modified"] == "2012-05-01T00:04:06"
        # assert resource["temporal_resolution"] == "PT15M"
        # assert resource["spatial_resolution_in_meters"] == 1.5
        # assert resource["status"] == "http://purl.org/adms/status/Completed"
        # assert resource["size"] == 12323
        # assert (
        #     resource["availability"]
        #     == "http://publications.europa.eu/resource/authority/planned-availability/EXPERIMENTAL"
        # )
        # assert (
        #     resource["compress_format"]
        #     == "http://www.iana.org/assignments/media-types/application/gzip"
        # )
        # assert (
        #     resource["package_format"]
        #     == "http://publications.europa.eu/resource/authority/file-type/TAR"
        # )

        # assert resource["hash"] == "4304cf2e751e6053c90b1804c89c0ebb758f395a"
        # assert (
        #     resource["hash_algorithm"]
        #     == "http://spdx.org/rdf/terms#checksumAlgorithm_sha1"
        # )

        # assert (
        #     resource["access_url"] == "http://www.bgs.ac.uk/gbase/geochemcd/home.html"
        # )
        # assert "download_url" not in resource

        # # Resources: list fields
        # assert sorted(resource["language"]) == ["ca", "en", "es"]
        # assert sorted(resource["documentation"]) == [
        #     "http://dataset.info.org/distribution1/doc1",
        #     "http://dataset.info.org/distribution1/doc2",
        # ]
        # assert sorted(resource["conforms_to"]) == ["Standard 1", "Standard 2"]

        # # Resources: repeating subfields
        # assert resource["access_services"][0]["title"] == "Sparql-end Point"
        # assert resource["access_services"][0]["endpoint_url"] == [
        #     "http://publications.europa.eu/webapi/rdf/sparql"
        # ]
