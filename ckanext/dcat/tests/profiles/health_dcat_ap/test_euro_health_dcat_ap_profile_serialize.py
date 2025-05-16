import json

import pytest
from ckan.tests.helpers import call_action
from geomet import wkt
from rdflib import Graph
from rdflib.namespace import RDF
from rdflib.term import URIRef

from ckanext.dcat import utils
from ckanext.dcat.processors import RDFSerializer
from ckanext.dcat.profiles import (
    ADMS,
    DCAT,
    DCATAP,
    DCT,
    FOAF,
    GSP,
    LOCN,
    OWL,
    RDF,
    RDFS,
    SKOS,
    SPDX,
    VCARD,
    XSD,
)
from ckanext.dcat.profiles.euro_health_dcat_ap import HEALTHDCATAP
from ckanext.dcat.tests.utils import BaseSerializeTest

DCAT_AP_PROFILES = ["euro_dcat_ap_3"]


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
class TestEuroDCATAP3ProfileSerializeDataset(BaseSerializeTest):
    def test_e2e_ckan_to_dcat(self):
        """
        End to end testing of CKAN dataset to RDF triples.

        Note: in this HealthDCAT-AP profile, only the HealthDCAT-AP specific triples are tested for.
        Triples in other profiles could be tested, but should mainly be tested by their respective
        profiles."""
        dataset_dict = json.loads(self._get_file_contents("ckan/health_dcat_ap.json"))[
            0
        ]

        dataset = call_action("package_create", **dataset_dict)

        # Make sure schema was used
        assert dataset["hdab"][0]["name"] == "EU Health Data Access Body"

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        # Test dataset URI
        assert str(dataset_ref) == utils.dataset_uri(dataset)

        # Load Reference graph that only containes
        contents = self._get_file_contents("dcat/dataset_health_no_blank.ttl")
        reference = Graph()
        reference.parse(data=contents, format="turtle")

        # First check that all non-blind nodes from the reference are present in the output
        # Any other nodes added by other profiles (e.g. DCAT-AP 3) we do not have an opinion about
        for triple in reference:
            assert triple in g, f"Triple {triple} not in output graph"
        # assert all(triple in g for triple in reference)

        # Test HealthDCAT-AP specific HDAB triples
        # We can assume other blank nodes (e.g. contact point, publisher, temporal) are taken care
        # of by the base profile.
        hdab = [t for t in g.triples((dataset_ref, HEALTHDCATAP.hdab, None))]
        assert len(hdab) == 1
        hdab_items = [
            (FOAF.name, dataset_dict["hdab"][0]["name"]),
            (VCARD.hasEmail, URIRef("mailto:" + dataset_dict["hdab"][0]["email"])),
            (FOAF.homepage, URIRef(dataset_dict["hdab"][0]["url"])),
        ]
        for predicate, value in hdab_items:
            assert self._triple(
                g, hdab[0][2], predicate, value
            ), f"HDAB Predicate {predicate} does not have value {value}"

        # Test qualified relation
        relation = [t for t in g.triples((dataset_ref, DCAT.qualifiedRelation, None))]
        assert len(relation) == 1
        relation_items = [
            (DCT.relation, URIRef(dataset_dict["qualified_relation"][0]["relation"])),
            (DCAT.hadRole, URIRef(dataset_dict["qualified_relation"][0]["role"])),
        ]
        for predicate, value in relation_items:
            assert self._triple(
                g, relation[0][2], predicate, value
            ), f"relation Predicate {predicate} does not have value {value}"
