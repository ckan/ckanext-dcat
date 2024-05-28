import pytest

from rdflib.namespace import RDF
from rdflib.term import URIRef

from ckan.tests.helpers import call_action

from ckanext.dcat import utils
from ckanext.dcat.processors import RDFSerializer, RDFParser
from ckanext.dcat.profiles import (
    DCAT,
    DCT,
    ADMS,
    XSD,
    VCARD,
    FOAF,
    SCHEMA,
    SKOS,
    LOCN,
    GSP,
    OWL,
    SPDX,
    GEOJSON_IMT,
    DISTRIBUTION_LICENSE_FALLBACK_CONFIG,
)
from ckanext.dcat.tests.utils import BaseSerializeTest, BaseParseTest


@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.plugins", "dcat scheming_datasets")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas", "ckanext.dcat.schemas:dcat_ap_2.1.yaml"
)
@pytest.mark.ckan_config("scheming.presets", "ckanext.scheming:presets.json")
@pytest.mark.ckan_config(
    "ckanext.dcat.rdf.profiles", "euro_dcat_ap_2 euro_dcat_ap_scheming"
)
class TestSchemingSerializeSupport(BaseSerializeTest):
    def test_e2e_ckan_to_dcat(self):
        """
        Create a dataset using the scheming schema, check that fields
        are exposed in the DCAT RDF graph
        """

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
            # Repeating subfields
            "contact": [
                {"name": "Contact 1", "email": "contact1@example.org"},
                {"name": "Contact 2", "email": "contact2@example.org"},
            ],
            "resources": [
                {
                    "name": "Resource 1",
                    "description": "Some description",
                    "url": "https://example.com/data.csv",
                    "format": "CSV",
                    "status": "published",
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
                            "endpoint_url": [
                                "https://example.org/access_service/1",
                                "https://example.org/access_service/2",
                            ],
                        }
                    ],
                }
            ],
        }

        dataset = call_action("package_create", **dataset_dict)

        # Make sure schema was used
        assert dataset["conforms_to"][0] == "Standard 1"
        assert dataset["contact"][0]["name"] == "Contact 1"

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        assert str(dataset_ref) == utils.dataset_uri(dataset)

        # Core fields
        assert self._triple(g, dataset_ref, RDF.type, DCAT.Dataset)
        assert self._triple(g, dataset_ref, DCT.title, dataset["title"])
        assert self._triple(g, dataset_ref, DCT.description, dataset["notes"])
        assert self._triple(g, dataset_ref, OWL.versionInfo, dataset["version"])

        # Standard fields
        assert self._triple(g, dataset_ref, DCT.identifier, dataset["identifier"])
        assert self._triple(
            g, dataset_ref, DCT.accrualPeriodicity, dataset["frequency"]
        )
        assert self._triple(g, dataset_ref, DCT.provenance, dataset["provenance"])
        assert self._triple(g, dataset_ref, DCT.type, dataset["dcat_type"])
        assert self._triple(g, dataset_ref, ADMS.versionNotes, dataset["version_notes"])
        assert self._triple(g, dataset_ref, DCT.accessRights, dataset["access_rights"])

        # Dates
        assert self._triple(
            g,
            dataset_ref,
            DCT.issued,
            dataset["issued"] + "T00:00:00",
            data_type=XSD.dateTime,
        )
        assert self._triple(
            g,
            dataset_ref,
            DCT.modified,
            dataset["modified"] + "T00:00:00",
            data_type=XSD.dateTime,
        )

        # List fields

        assert (
            self._triples_list_values(g, dataset_ref, DCT.conformsTo)
            == dataset["conforms_to"]
        )
        assert (
            self._triples_list_values(g, dataset_ref, ADMS.identifier)
            == dataset["alternate_identifier"]
        )
        assert self._triples_list_values(g, dataset_ref, DCAT.theme) == dataset["theme"]
        assert (
            self._triples_list_values(g, dataset_ref, DCT.language)
            == dataset["language"]
        )
        assert (
            self._triples_list_values(g, dataset_ref, FOAF.page)
            == dataset["documentation"]
        )

        # Repeating subfields

        contact_details = [t for t in g.triples((dataset_ref, DCAT.contactPoint, None))]

        assert len(contact_details) == len(dataset["contact"])
        assert self._triple(
            g, contact_details[0][2], VCARD.fn, dataset_dict["contact"][0]["name"]
        )
        assert self._triple(
            g,
            contact_details[0][2],
            VCARD.hasEmail,
            URIRef("mailto:" + dataset_dict["contact"][0]["email"]),
        )
        assert self._triple(
            g, contact_details[1][2], VCARD.fn, dataset_dict["contact"][1]["name"]
        )
        assert self._triple(
            g,
            contact_details[1][2],
            VCARD.hasEmail,
            dataset_dict["contact"][1]["email"],
        )

        distribution_ref = self._triple(g, dataset_ref, DCAT.distribution, None)[2]

        # Resources: core fields

        assert self._triple(
            g, distribution_ref, DCT.title, dataset_dict["resources"][0]["name"]
        )
        assert self._triple(
            g,
            distribution_ref,
            DCT.description,
            dataset_dict["resources"][0]["description"],
        )

        # Resources: standard fields

        assert self._triple(
            g, distribution_ref, DCT.rights, dataset_dict["resources"][0]["rights"]
        )
        assert self._triple(
            g, distribution_ref, ADMS.status, dataset_dict["resources"][0]["status"]
        )
        assert self._triple(
            g,
            distribution_ref,
            DCAT.accessURL,
            URIRef(dataset_dict["resources"][0]["access_url"]),
        )
        assert self._triple(
            g,
            distribution_ref,
            DCAT.downloadURL,
            URIRef(dataset_dict["resources"][0]["download_url"]),
        )

        # Resources: dates
        assert self._triple(
            g,
            distribution_ref,
            DCT.issued,
            dataset["resources"][0]["issued"],
            data_type=XSD.dateTime,
        )
        assert self._triple(
            g,
            distribution_ref,
            DCT.modified,
            dataset["resources"][0]["modified"],
            data_type=XSD.dateTime,
        )

        # Resources: list fields

        language = [
            str(t[2]) for t in g.triples((distribution_ref, DCT.language, None))
        ]
        assert language == dataset_dict["resources"][0]["language"]

        # Resource: repeating subfields
        access_services = [
            t for t in g.triples((distribution_ref, DCAT.accessService, None))
        ]

        assert len(access_services) == len(dataset["resources"][0]["access_services"])
        assert self._triple(
            g,
            access_services[0][2],
            DCT.title,
            dataset_dict["resources"][0]["access_services"][0]["title"],
        )

        endpoint_urls = [
            str(t[2])
            for t in g.triples((access_services[0][2], DCAT.endpointURL, None))
        ]
        assert (
            endpoint_urls
            == dataset_dict["resources"][0]["access_services"][0]["endpoint_url"]
        )


@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.plugins", "dcat scheming_datasets")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas", "ckanext.dcat.schemas:dcat_ap_2.1.yaml"
)
@pytest.mark.ckan_config("scheming.presets", "ckanext.scheming:presets.json")
@pytest.mark.ckan_config(
    "ckanext.dcat.rdf.profiles", "euro_dcat_ap_2 euro_dcat_ap_scheming"
)
class TestSchemingParseSupport(BaseParseTest):
    def test_e2e_dcat_to_ckan(self):
        """
        Parse a DCAT RDF graph into a CKAN dataset dict, create a dataset with package_create
        and check that all expected fields are there
        """
        contents = self._get_file_contents("dataset.rdf")

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
        assert dataset["identifier"] == u"9df8df51-63db-37a8-e044-0003ba9b0d98"
        assert dataset["frequency"] == "http://purl.org/cld/freq/daily"
        assert dataset["access_rights"] == "public"
        assert dataset["provenance"] == "Some statement about provenance"
        assert dataset["dcat_type"] == "test-type"

        assert dataset["issued"] == u"2012-05-10"
        assert dataset["modified"] == u"2012-05-10T21:04:00"

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

        # Repeating subfields

        assert dataset["contact"][0]["name"] == "Point of Contact"
        assert dataset["contact"][0]["email"] == "contact@some.org"

        resource = dataset["resources"][0]

        # Resources: core fields
        assert resource["url"] == "http://www.bgs.ac.uk/gbase/geochemcd/home.html"

        # Resources: standard fields
        assert resource["license"] == "http://creativecommons.org/licenses/by-nc/2.0/"
        assert resource["rights"] == "Some statement about rights"
        assert resource["issued"] == "2012-05-11"
        assert resource["modified"] == "2012-05-01T00:04:06"
        assert resource["status"] == "http://purl.org/adms/status/Completed"
        assert resource["size"] == 12323

        # assert resource['hash'] == u'4304cf2e751e6053c90b1804c89c0ebb758f395a'
        # assert resource['hash_algorithm'] == u'http://spdx.org/rdf/terms#checksumAlgorithm_sha1'

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
