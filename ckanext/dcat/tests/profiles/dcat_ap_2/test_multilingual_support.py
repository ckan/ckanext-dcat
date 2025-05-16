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
@pytest.mark.ckan_config(
    "scheming.dataset_schemas", "ckanext.dcat.schemas:dcat_ap_multilingual.yaml"
)
@pytest.mark.ckan_config(
    "scheming.presets",
    "ckanext.scheming:presets.json ckanext.dcat.schemas:presets.yaml ckanext.fluent:presets.json",
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


@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.plugins", "dcat scheming_datasets fluent")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas", "ckanext.dcat.schemas:dcat_ap_multilingual.yaml"
)
@pytest.mark.ckan_config(
    "scheming.presets",
    "ckanext.scheming:presets.json ckanext.dcat.schemas:presets.yaml ckanext.fluent:presets.json",
)
@pytest.mark.ckan_config(
    "ckanext.dcat.rdf.profiles", "euro_dcat_ap_2 euro_dcat_ap_scheming"
)
class TestSchemingFluentParseSupport(BaseParseTest):
    def test_e2e_dcat_to_ckan(self):
        """
        Parse a DCAT RDF graph into a CKAN dataset dict, create a dataset with
        package_create and check that all the translated fields are there
        """
        contents = self._get_file_contents("dcat/dataset_multilingual.ttl")

        p = RDFParser()

        p.parse(contents, _format="ttl")

        datasets = [d for d in p.datasets()]

        assert len(datasets) == 1

        dataset_dict = datasets[0]

        dataset_dict["name"] = "test-dcat-1"
        dataset = call_action("package_create", **dataset_dict)

        # Dataset core fields
        assert dataset["title"] == "Test DCAT dataset"
        assert dataset["title_translated"]["en"] == "Test DCAT dataset"
        assert dataset["title_translated"]["ca"] == "Conjunt de dades de prova DCAT"
        assert dataset["title_translated"]["es"] == "Conjunto de datos de prueba DCAT"

        assert dataset["notes"] == "Some description"
        assert dataset["notes_translated"]["en"] == "Some description"
        assert dataset["notes_translated"]["ca"] == "Una descripció qualsevol"
        assert dataset["notes_translated"]["es"] == "Una descripción cualquiera"

        # Tags
        assert sorted(dataset["tags_translated"]["en"]) == sorted(["Oaks", "Pines"])
        assert sorted(dataset["tags_translated"]["ca"]) == sorted(["Roures", "Pins"])
        assert sorted(dataset["tags_translated"]["es"]) == sorted(["Robles", "Pinos"])

        # Dataset fields
        assert dataset["provenance"]["en"] == "Statement about provenance"
        assert dataset["provenance"]["ca"] == "Una declaració sobre la procedència"
        assert dataset["provenance"]["es"] == "Una declaración sobre la procedencia"

        assert dataset["version_notes"]["en"] == "Some version notes"
        assert dataset["version_notes"]["ca"] == "Notes sobre la versió"
        assert dataset["version_notes"]["es"] == "Notas sobre la versión"

        resource = dataset["resources"][0]

        # Resource core fields
        assert resource["name"] == "Resource 1"
        assert resource["name_translated"]["en"] == "Resource 1"
        assert resource["name_translated"]["ca"] == "Recurs 1"
        assert resource["name_translated"]["es"] == "Recurso 1"

        assert resource["description"] == "Some description"
        assert resource["description_translated"]["en"] == "Some description"
        assert resource["description_translated"]["ca"] == "Una descripció qualsevol"
        assert resource["description_translated"]["es"] == "Una descripción cualquiera"

        # Resource fields
        assert resource["rights"]["en"] == "Some stament about rights"
        assert resource["rights"]["ca"] == "Una nota sobre drets"
        assert resource["rights"]["es"] == "Una nota sobre derechos"
