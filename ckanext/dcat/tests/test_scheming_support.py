import pytest

from rdflib.namespace import RDF

from ckan.tests.helpers import call_action

from ckanext.dcat import utils
from ckanext.dcat.processors import RDFSerializer
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
from ckanext.dcat.tests.utils import BaseSerializeTest


@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.plugins", "dcat scheming_datasets")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas", "ckanext.dcat.schemas:dcat_ap_2.1.yaml"
)
@pytest.mark.ckan_config("scheming.presets", "ckanext.scheming:presets.json")
class TestSchemingSupport(BaseSerializeTest):
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
            "version_notes": "Some version notes",
            # List fields (lists)
            "conforms_to": ["Standard 1", "Standard 2"],
            # Repeating subfields
            "contact": [
                {"name": "Contact 1", "email": "contact1@example.org"},
                {"name": "Contact 2", "email": "contact2@example.org"},
            ],
            # TODO: resources
        }

        dataset = call_action("package_create", **dataset_dict)

        # Make sure schema was used
        assert dataset["conforms_to"][0] == "Standard 1"
        assert dataset["contact"][0]["name"] == "Contact 1"

        s = RDFSerializer(profiles=["euro_dcat_ap"])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        assert str(dataset_ref) == utils.dataset_uri(dataset)

        # Core fields
        assert self._triple(g, dataset_ref, RDF.type, DCAT.Dataset)
        assert self._triple(g, dataset_ref, DCT.title, dataset["title"])
        assert self._triple(g, dataset_ref, DCT.description, dataset["notes"])

        # Standard fields
        assert self._triple(g, dataset_ref, ADMS.versionNotes, dataset["version_notes"])

        # List fields
        # TODO helper function
        conforms = [t for t in g.triples((dataset_ref, DCT.conformsTo, None))]
        assert len(conforms) == len(dataset["conforms_to"])
        for index, item in enumerate(conforms):
            assert str(item[2]) == dataset["conforms_to"][index]

        # Repeating subfields

        contact_details = [t for t in g.triples((dataset_ref, DCAT.contactPoint, None))]

        assert len(contact_details) == len(dataset["contact"])
        self._triple(g, contact_details[0][2], VCARD.fn, dataset_dict["contact"][0]["name"])
        self._triple(g, contact_details[0][2], VCARD.hasEmail, dataset_dict["contact"][0]["email"])
        self._triple(g, contact_details[1][2], VCARD.fn, dataset_dict["contact"][1]["name"])
        self._triple(g, contact_details[1][2], VCARD.hasEmail, dataset_dict["contact"][1]["email"])
