import pytest

from ckan.tests.helpers import call_action

from ckanext.dcat.processors import RDFParser
from ckanext.dcat.tests.utils import BaseParseTest


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
class TestSchemingParseSupport(BaseParseTest):
    def test_e2e_dcat_to_ckan(self):
        """
        Parse a DCAT RDF graph into a CKAN dataset dict, create a dataset with
        package_create and check that all expected fields are there
        """
        contents = self._get_file_contents("dcat/dataset.rdf")

        p = RDFParser()

        p.parse(contents)

        datasets = [d for d in p.datasets()]

        assert len(datasets) == 1

        dataset_dict = datasets[0]

        dataset_dict["name"] = "test-dcat-1"
        dataset = call_action("package_create", **dataset_dict)

        # Core fields

        assert dataset["title"] == "Zimbabwe Regional Geochemical Survey."
        assert (
            dataset["notes"]
            == "During the period 1982-86 a team of geologists from the British Geological Survey ..."
        )
        assert dataset["url"] == "http://dataset.info.org"
        assert dataset["version"] == "2.3"
        assert dataset["license_id"] == "cc-nc"
        assert sorted([t["name"] for t in dataset["tags"]]) == [
            "exploration",
            "geochemistry",
            "geology",
        ]

        # Standard fields
        assert dataset["version_notes"] == "New schema added"
        assert dataset["identifier"] == "9df8df51-63db-37a8-e044-0003ba9b0d98"
        assert dataset["frequency"] == "http://purl.org/cld/freq/daily"
        assert dataset["access_rights"] == "public"
        assert dataset["provenance"] == "Some statement about provenance"
        assert dataset["dcat_type"] == "test-type"

        assert dataset["issued"] == "2012-05-10"
        assert dataset["modified"] == "2012-05-10T21:04:00"
        assert dataset["temporal_resolution"] == "PT15M"
        assert dataset["spatial_resolution_in_meters"] == "1.5"

        # List fields
        assert sorted(dataset["conforms_to"]) == ["Standard 1", "Standard 2"]
        assert sorted(dataset["language"]) == ["ca", "en", "es"]
        assert sorted(dataset["theme"]) == [
            "Earth Sciences",
            "http://eurovoc.europa.eu/100142",
            "http://eurovoc.europa.eu/209065",
        ]
        assert sorted(dataset["alternate_identifier"]) == [
            "alternate-identifier-1",
            "alternate-identifier-2",
        ]
        assert sorted(dataset["documentation"]) == [
            "http://dataset.info.org/doc1",
            "http://dataset.info.org/doc2",
        ]

        assert sorted(dataset["is_referenced_by"]) == [
            "https://doi.org/10.1038/sdata.2018.22",
            "test_isreferencedby",
        ]

        # Repeating subfields

        assert dataset["contact"][0]["name"] == "Point of Contact"
        assert dataset["contact"][0]["email"] == "contact@some.org"

        assert dataset["creator"][0]["name"] == "Creating Organization for dataset 1"
        assert dataset["creator"][0]["email"] == "creator@example.org"
        assert dataset["creator"][0]["url"] == "http://example.org"

        assert (
            dataset["publisher"][0]["name"] == "Publishing Organization for dataset 1"
        )
        assert dataset["publisher"][0]["email"] == "contact@some.org"
        assert dataset["publisher"][0]["url"] == "http://some.org"
        assert (
            dataset["publisher"][0]["type"]
            == "http://purl.org/adms/publishertype/NonProfitOrganisation"
        )

        assert dataset["temporal_coverage"][0]["start"] == "1905-03-01"
        assert dataset["temporal_coverage"][0]["end"] == "2013-01-05"

        resource = dataset["resources"][0]

        # Resources: core fields
        assert resource["url"] == "http://www.bgs.ac.uk/gbase/geochemcd/home.html"

        # Resources: standard fields
        assert resource["license"] == "http://creativecommons.org/licenses/by-nc/2.0/"
        assert resource["identifier"] == "https://example.org/distributions/1"
        assert resource["rights"] == "Some statement about rights"
        assert resource["issued"] == "2012-05-11"
        assert resource["modified"] == "2012-05-01T00:04:06"
        assert resource["status"] == "http://purl.org/adms/status/Completed"
        assert resource["size"] == 12323
        assert resource["character_encoding"] == "UTF-8"
        assert resource["temporal_resolution"] == "PT15M"
        assert resource["spatial_resolution_in_meters"] == 1.5
        assert (
            resource["compress_format"]
            == "http://www.iana.org/assignments/media-types/application/gzip"
        )
        assert (
            resource["package_format"]
            == "http://publications.europa.eu/resource/authority/file-type/TAR"
        )

        assert resource["hash"] == "4304cf2e751e6053c90b1804c89c0ebb758f395a"
        assert (
            resource["hash_algorithm"]
            == "http://spdx.org/rdf/terms#checksumAlgorithm_sha1"
        )

        assert (
            resource["access_url"] == "http://www.bgs.ac.uk/gbase/geochemcd/home.html"
        )
        assert "download_url" not in resource

        # Resources: list fields
        assert sorted(resource["language"]) == ["ca", "en", "es"]
        assert sorted(resource["documentation"]) == [
            "http://dataset.info.org/distribution1/doc1",
            "http://dataset.info.org/distribution1/doc2",
        ]
        assert sorted(resource["conforms_to"]) == ["Standard 1", "Standard 2"]

        # Resources: repeating subfields
        assert resource["access_services"][0]["title"] == "Sparql-end Point"
        assert resource["access_services"][0]["endpoint_url"] == [
            "http://publications.europa.eu/webapi/rdf/sparql"
        ]

    def test_two_distributions(self):

        data = """
        @prefix dcat: <http://www.w3.org/ns/dcat#> .
        @prefix dcat-us: <http://resources.data.gov/ontology/dcat-us#> .
        @prefix dcterms: <http://purl.org/dc/terms/> .
        @prefix locn: <http://www.w3.org/ns/locn#> .
        @prefix gsp: <http://www.opengis.net/ont/geosparql#> .

        <https://example.com/dataset1>
          a dcat:Dataset ;
          dcterms:title "Dataset 1" ;
          dcterms:description "This is a dataset" ;
          dcterms:publisher <https://example.com/publisher1> ;
          dcat:distribution <http://test.ckan.net/dataset/xxx/resource/yyy> ;
          dcat:distribution <http://test.ckan.net/dataset/xxx/resource/zzz>
        .

        <http://test.ckan.net/dataset/xxx/resource/yyy> a dcat:Distribution ;
            dcterms:title "Resource 1" ;
            dcterms:identifier "id1"
        .

        <http://test.ckan.net/dataset/xxx/resource/zzz> a dcat:Distribution ;
            dcterms:title "Resource 2" ;
            dcterms:identifier "id2"
        .

        """
        p = RDFParser()

        p.parse(data, _format="ttl")

        datasets = [d for d in p.datasets()]

        assert len(datasets[0]["resources"]) == 2

        assert datasets[0]["resources"][0]["name"] == "Resource 1"
        assert datasets[0]["resources"][0]["identifier"] == "id1"
        assert datasets[0]["resources"][1]["name"] == "Resource 2"
        assert datasets[0]["resources"][1]["identifier"] == "id2"

    def test_bbox(self):

        data = """
        @prefix dcat: <http://www.w3.org/ns/dcat#> .
        @prefix dcat-us: <http://resources.data.gov/ontology/dcat-us#> .
        @prefix dcterms: <http://purl.org/dc/terms/> .
        @prefix locn: <http://www.w3.org/ns/locn#> .
        @prefix gsp: <http://www.opengis.net/ont/geosparql#> .

        <https://example.com/dataset1>
          a dcat:Dataset ;
          dcterms:title "Dataset 1" ;
          dcterms:description "This is a dataset" ;
          dcterms:publisher <https://example.com/publisher1> ;
          dcat-us:geographicBoundingBox [
              a dcat-us:GeographicBoundingBox ;
              dcat-us:westBoundingLongitude 22.3;
              dcat-us:eastBoundingLongitude 10.3;
              dcat-us:northBoundingLatitude 50.2;
              dcat-us:southBoundingLatitude 20.2;
          ]
        .
        """
        p = RDFParser()

        p.parse(data, _format="ttl")

        datasets = [d for d in p.datasets()]

        dataset = datasets[0]

        assert dataset["bbox"][0]["west"] == "22.3"
        assert dataset["bbox"][0]["east"] == "10.3"
        assert dataset["bbox"][0]["north"] == "50.2"
        assert dataset["bbox"][0]["south"] == "20.2"

    def test_data_dictionary_dataset(self):

        data = """
        @prefix dcat: <http://www.w3.org/ns/dcat#> .
        @prefix dcat-us: <http://resources.data.gov/ontology/dcat-us#> .
        @prefix dcterms: <http://purl.org/dc/terms/> .

        <https://example.com/dataset1>
          a dcat:Dataset ;
          dcterms:title "Dataset 1" ;
          dcterms:description "This is a dataset" ;
          dcterms:publisher <https://example.com/publisher1> ;
          dcat-us:describedBy [ a dcat:Distribution ;
                  dcterms:format <https://resources.data.gov/vocab/file-type/TODO/JSON> ;
                  dcterms:license <https://resources.data.gov/vocab/license/TODO/CC_BYNC_4_0> ;
                  dcat:accessURL <https://example.org/some-data-dictionary> ]
        .
        """
        p = RDFParser()

        p.parse(data, _format="ttl")

        datasets = [d for d in p.datasets()]

        dataset = datasets[0]
        assert (
            dataset["data_dictionary"][0]["url"]
            == "https://example.org/some-data-dictionary"
        )
        assert (
            dataset["data_dictionary"][0]["format"]
            == "https://resources.data.gov/vocab/file-type/TODO/JSON"
        )
        assert (
            dataset["data_dictionary"][0]["license"]
            == "https://resources.data.gov/vocab/license/TODO/CC_BYNC_4_0"
        )

    def test_data_dictionary_distribution(self):

        data = """
        @prefix dcat: <http://www.w3.org/ns/dcat#> .
        @prefix dcat-us: <http://resources.data.gov/ontology/dcat-us#> .
        @prefix dcterms: <http://purl.org/dc/terms/> .

        <https://example.com/dataset1>
          a dcat:Dataset ;
          dcterms:title "Dataset 1" ;
          dcterms:description "This is a dataset" ;
          dcterms:publisher <https://example.com/publisher1> ;
          dcat:distribution <http://test.ckan.net/dataset/xxx/resource/yyy>
        .

        <http://test.ckan.net/dataset/xxx/resource/yyy> a dcat:Distribution ;
          dcat-us:describedBy [ a dcat:Distribution ;
                  dcterms:format <https://resources.data.gov/vocab/file-type/TODO/JSON> ;
                  dcterms:license <https://resources.data.gov/vocab/license/TODO/CC_BYNC_4_0> ;
                  dcat:accessURL <https://example.org/some-data-dictionary> ]
        .
        """
        p = RDFParser()

        p.parse(data, _format="ttl")

        datasets = [d for d in p.datasets()]

        resource = datasets[0]["resources"][0]
        assert (
            resource["data_dictionary"][0]["url"]
            == "https://example.org/some-data-dictionary"
        )
        assert (
            resource["data_dictionary"][0]["format"]
            == "https://resources.data.gov/vocab/file-type/TODO/JSON"
        )
        assert (
            resource["data_dictionary"][0]["license"]
            == "https://resources.data.gov/vocab/license/TODO/CC_BYNC_4_0"
        )

    def test_data_liability_statement(self):

        data = """
        @prefix dcat: <http://www.w3.org/ns/dcat#> .
        @prefix dcat-us: <http://resources.data.gov/ontology/dcat-us#> .
        @prefix dcterms: <http://purl.org/dc/terms/> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

        <https://example.com/dataset1>
          a dcat:Dataset ;
          dcterms:title "Dataset 1" ;
          dcterms:description "This is a dataset" ;
          dcat-us:liabilityStatement [
              a dcat-us:LiabilityStatement;
              rdfs:label "This dataset is provided 'as-is'."
            ]
        .
        """
        p = RDFParser()

        p.parse(data, _format="ttl")

        datasets = [d for d in p.datasets()]

        dataset = datasets[0]

        assert dataset["liability"] == "This dataset is provided 'as-is'."

    def test_contributors(self):

        data = """
        @prefix dcat: <http://www.w3.org/ns/dcat#> .
        @prefix dcat-us: <http://resources.data.gov/ontology/dcat-us#> .
        @prefix dcterms: <http://purl.org/dc/terms/> .
        @prefix foaf: <http://xmlns.com/foaf/0.1/> .
        @prefix vcard: <http://www.w3.org/2006/vcard/ns#> .

        <https://example.com/dataset1>
          a dcat:Dataset ;
          dcterms:title "Dataset 1" ;
          dcterms:description "This is a dataset" ;
          dcterms:contributor <https://orcid.org/0000-0002-0693-466X> ;
          dcterms:contributor [
            a foaf:Agent;
            foaf:name "Test Contributor 1" ;
            vcard:hasEmail <mailto:contributor1@example.org> ;
            foaf:homepage <https://example.org> ;
            ]
        .

        <https://orcid.org/0000-0002-0693-466X> a foaf:Person;
          foaf:name "John Doe" ;
        .
        """
        p = RDFParser()

        p.parse(data, _format="ttl")

        datasets = [d for d in p.datasets()]

        dataset = datasets[0]

        assert dataset["contributor"][0]["name"] == "John Doe"
        assert (
            dataset["contributor"][0]["uri"] == "https://orcid.org/0000-0002-0693-466X"
        )

        assert dataset["contributor"][1]["name"] == "Test Contributor 1"
        assert dataset["contributor"][1]["email"] == "contributor1@example.org"
        assert dataset["contributor"][1]["url"] == "https://example.org"

    def test_usage_note(self):

        data = """
        @prefix dcat: <http://www.w3.org/ns/dcat#> .
        @prefix dcat-us: <http://resources.data.gov/ontology/dcat-us#> .
        @prefix dcterms: <http://purl.org/dc/terms/> .
        @prefix skos: <http://www.w3.org/2004/02/skos/core#> .

        <https://example.com/dataset1>
          a dcat:Dataset ;
          dcterms:title "Dataset 1" ;
          dcterms:description "This is a dataset" ;
          skos:scopeNote "Some statement about usage"
        .
        """
        p = RDFParser()

        p.parse(data, _format="ttl")

        datasets = [d for d in p.datasets()]

        dataset = datasets[0]

        assert dataset["usage"] == ["Some statement about usage"]

    def test_purpose(self):

        data = """
        @prefix dcat: <http://www.w3.org/ns/dcat#> .
        @prefix dcat-us: <http://resources.data.gov/ontology/dcat-us#> .
        @prefix dcterms: <http://purl.org/dc/terms/> .

        <https://example.com/dataset1>
          a dcat:Dataset ;
          dcterms:title "Dataset 1" ;
          dcterms:description "This is a dataset" ;
          dcat-us:purpose "Some statement about purpose"
        .
        """
        p = RDFParser()

        p.parse(data, _format="ttl")

        datasets = [d for d in p.datasets()]

        dataset = datasets[0]

        assert dataset["purpose"] == ["Some statement about purpose"]
