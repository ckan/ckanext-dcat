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
from ckanext.dcat.tests.utils import BaseSerializeTest

DCAT_AP_PROFILES = ["euro_dcat_ap_3"]


@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.plugins", "dcat scheming_datasets")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas", "ckanext.dcat.schemas:healthdcat_ap.yaml"
)
@pytest.mark.ckan_config("ckanext.dcat.rdf.profiles", "euro_health_dcat_ap")
class TestEuroDCATAP3ProfileSerializeDataset(BaseSerializeTest):
    def test_e2e_ckan_to_dcat(self):
        dataset_dict = json.loads(self._get_file_contents("ckan/healthdcat_ap.json"))[0]

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
        assert all(triple in g for triple in reference)

        print(s.g.serialize(format="turtle"))
        assert False
