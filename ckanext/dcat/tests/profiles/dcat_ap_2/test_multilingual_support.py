import json

import pytest

from ckan.tests.helpers import call_action
from ckanext.dcat.processors import RDFSerializer, RDFParser
from ckanext.dcat.profiles import (
    DCAT,
    DCATAP,
    DCT,
    ADMS,
    VCARD,
    FOAF,
    SKOS,
    LOCN,
    GSP,
    OWL,
    SPDX,
    RDFS,
)
from ckanext.dcat.tests.utils import BaseSerializeTest, BaseParseTest


@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.plugins", "dcat scheming_datasets fluent")
@pytest.mark.ckan_config("ckan.locales_offered", "en ca es")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas", "ckanext.dcat.schemas:dcat_ap_multilingual.yaml"
)
@pytest.mark.ckan_config(
    "ckanext.dcat.rdf.profiles", "euro_dcat_ap_2 euro_dcat_ap_scheming"
)
class TestSchemingFluentSerializeSupport(BaseSerializeTest):
    def test_e2e_ckan_to_dcat(self):
        """
        Create a dataset using the scheming fluent schema, check that fields
        are exposed in the DCAT RDF graph with the approapiate language
        """

        dataset_dict = json.loads(
            self._get_file_contents("ckan/ckan_dataset_multilingual.json")
        )

        dataset = call_action("package_create", **dataset_dict)

        # Make sure scheming and fluent was used
        assert dataset["title_translated"]["en"] == "Test DCAT dataset"
        assert dataset["version_notes"]["ca"] == "Notes sobre la versió"

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        assert self._triple(
            g, dataset_ref, DCT.title, dataset["title_translated"]["en"], lang="en"
        )
        assert self._triple(
            g, dataset_ref, DCT.title, dataset["title_translated"]["ca"], lang="ca"
        )
        assert self._triple(
            g, dataset_ref, DCT.title, dataset["title_translated"]["es"], lang="es"
        )

        assert self._triple(
            g,
            dataset_ref,
            DCT.description,
            dataset["notes_translated"]["en"],
            lang="en",
        )
        assert self._triple(
            g,
            dataset_ref,
            DCT.description,
            dataset["notes_translated"]["ca"],
            lang="ca",
        )
        assert self._triple(
            g,
            dataset_ref,
            DCT.description,
            dataset["notes_translated"]["es"],
            lang="es",
        )

        assert self._triple(
            g,
            dataset_ref,
            ADMS.versionNotes,
            dataset["version_notes"]["en"],
            lang="en",
        )
        assert self._triple(
            g,
            dataset_ref,
            ADMS.versionNotes,
            dataset["version_notes"]["ca"],
            lang="ca",
        )
        assert self._triple(
            g,
            dataset_ref,
            ADMS.versionNotes,
            dataset["version_notes"]["es"],
            lang="es",
        )

        statement = [s for s in g.objects(dataset_ref, DCT.provenance)][0]
        assert self._triple(
            g, statement, RDFS.label, dataset["provenance"]["en"], lang="en"
        )
        assert self._triple(
            g, statement, RDFS.label, dataset["provenance"]["ca"], lang="ca"
        )
        assert self._triple(
            g, statement, RDFS.label, dataset["provenance"]["es"], lang="es"
        )

        assert len([t for t in g.triples((dataset_ref, DCAT.keyword, None))]) == 6
        for lang in dataset["tags_translated"]:
            for tag in dataset["tags_translated"][lang]:
                assert self._triple(g, dataset_ref, DCAT.keyword, tag, lang=lang)

        # Resource fields

        distribution_ref = self._triple(g, dataset_ref, DCAT.distribution, None)[2]
        resource = dataset_dict["resources"][0]

        assert self._triple(
            g, distribution_ref, DCT.title, resource["name_translated"]["en"], lang="en"
        )
        assert self._triple(
            g, distribution_ref, DCT.title, resource["name_translated"]["ca"], lang="ca"
        )
        assert self._triple(
            g, distribution_ref, DCT.title, resource["name_translated"]["es"], lang="es"
        )

        assert self._triple(
            g,
            distribution_ref,
            DCT.description,
            resource["description_translated"]["en"],
            lang="en",
        )
        assert self._triple(
            g,
            distribution_ref,
            DCT.description,
            resource["description_translated"]["ca"],
            lang="ca",
        )
        assert self._triple(
            g,
            distribution_ref,
            DCT.description,
            resource["description_translated"]["es"],
            lang="es",
        )

        statement = [s for s in g.objects(distribution_ref, DCT.rights)][0]
        assert self._triple(
            g, statement, RDFS.label, resource["rights"]["en"], lang="en"
        )
        assert self._triple(
            g, statement, RDFS.label, resource["rights"]["ca"], lang="ca"
        )
        assert self._triple(
            g, statement, RDFS.label, resource["rights"]["es"], lang="es"
        )

        # Check non translated fields for good measure

        assert self._triple(g, dataset_ref, OWL.versionInfo, dataset["version"])

        contact_details = [t for t in g.triples((dataset_ref, DCAT.contactPoint, None))]

        assert len(contact_details) == len(dataset["contact"])
        assert self._triple(
            g, contact_details[0][2], VCARD.fn, dataset_dict["contact"][0]["name"]
        )
