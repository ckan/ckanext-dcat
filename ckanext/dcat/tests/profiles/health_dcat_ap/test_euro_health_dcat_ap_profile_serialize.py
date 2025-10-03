import json

import pytest
from ckan.tests.helpers import call_action
from geomet import wkt
from rdflib import Graph, PROV, Literal
from rdflib.term import URIRef
from rdflib.namespace import Namespace

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

# Open Annotation namespace
OA = Namespace("http://www.w3.org/ns/oa#")

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

        # Test provenance activity
        provenance = [t for t in g.triples((dataset_ref, PROV.wasGeneratedBy, None))]
        assert len(provenance) == 1
        activity_node = provenance[0][2]
        activity_items = [
            (RDF.type, PROV.Activity),
            (RDFS.label, Literal(dataset_dict["provenance_activity"][0]["label"])),
            (RDFS.seeAlso, URIRef(dataset_dict["provenance_activity"][0]["seeAlso"])),
            (DCT.type, URIRef(dataset_dict["provenance_activity"][0]["dct_type"])),
            (PROV.startedAtTime, Literal(dataset_dict["provenance_activity"][0]["startedAtTime"], datatype=XSD.dateTime)),
        ]
        for predicate, value in activity_items:
            assert self._triple(g, activity_node, predicate, value), f"Provenance {predicate} mismatch"

        agent_triple = list(g.objects(activity_node, PROV.wasAssociatedWith))
        assert len(agent_triple) == 1
        agent_node = agent_triple[0]
        agent_items = [
            (RDF.type, PROV.Agent),
            (FOAF.name, Literal(dataset_dict["provenance_activity"][0]["wasAssociatedWith"][0]["name"])),
            (FOAF.homepage, URIRef(dataset_dict["provenance_activity"][0]["wasAssociatedWith"][0]["homepage"])),
            (FOAF.mbox, URIRef(dataset_dict["provenance_activity"][0]["wasAssociatedWith"][0]["email"])),
        ]

        acted_on = list(g.objects(agent_node, PROV.actedOnBehalfOf))
        assert len(acted_on) == 1
        org_node = acted_on[0]
        assert self._triple(g, org_node, FOAF.name, Literal(dataset_dict["provenance_activity"][0]["wasAssociatedWith"][0]["actedOnBehalfOf"][0]["name"]))

        # Test qualified attribution
        attributions = [t for t in g.triples((dataset_ref, DCAT.qualifiedAttribution, None))]
        assert len(attributions) == 1
        attr_node = attributions[0][2]
        assert self._triple(g, attr_node, RDF.type, DCAT.Attribution)
        assert self._triple(g, attr_node, DCAT.hadRole, URIRef(dataset_dict["qualified_attribution"][0]["role"]))

        agent_node = list(g.objects(attr_node, DCAT.agent))[0]
        agent_details = dataset_dict["qualified_attribution"][0]["agent"][0]
        agent_items = [
            (RDF.type, FOAF.Organization),
            (FOAF.name, Literal(agent_details["name"])),
            (FOAF.mbox, URIRef("mailto:" + agent_details["email"])),
            (FOAF.homepage, URIRef(agent_details["homepage"])),
        ]
        for predicate, value in agent_items:
            assert self._triple(g, agent_node, predicate, value), f"QualifiedAttribution Agent {predicate} mismatch"

        # Test qualified annotation
        annotations = [t for t in
                       g.triples((dataset_ref, URIRef("http://www.w3.org/ns/dqv#hasQualityAnnotation"), None))]
        assert len(annotations) == 1, "Expected one dqv:hasQualityAnnotation triple"

        annotation_node = annotations[0][2]
        assert self._triple(g, annotation_node, RDF.type, URIRef("http://www.w3.org/ns/oa#Annotation"))

        annotation_details = dataset_dict["quality_annotation"][0]

        # Assert URI-based fields
        for field, predicate_uri in [
            ("motivated_by", OA.motivatedBy),
            ("body", OA.hasBody),
            ("target", OA.hasTarget),
        ]:
            value = annotation_details.get(field)
            assert value is not None, f"Missing {field} in annotation"
            assert self._triple(g, annotation_node, URIRef(predicate_uri),
                                URIRef(value)), f"QualityAnnotation {field} mismatch"
            
        # Extract the distribution node
        distributions = list(g.objects(dataset_ref, DCAT.distribution))
        assert len(distributions) > 0, "No distributions found"
        distribution_node = distributions[0]

        distribution_details = dataset_dict["resources"][0]

        assert self._triple(g, distribution_node, RDF.type, DCAT.Distribution)

        # Check retention period
        retention_nodes = list(g.objects(distribution_node, HEALTHDCATAP.retentionPeriod))
        assert len(retention_nodes) == 1, "Expected one retentionPeriod node on distribution"
        retention_node = retention_nodes[0]
        assert self._triple(g, retention_node, RDF.type, DCT.PeriodOfTime)
        assert self._triple(
            g,
            retention_node,
            DCAT.startDate,
            Literal(distribution_details["retention_period"][0]["start"], datatype=XSD.date)
        )
        assert self._triple(
            g,
            retention_node,
            DCAT.endDate,
            Literal(distribution_details["retention_period"][0]["end"], datatype=XSD.date)
        )


@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.plugins", "dcat scheming_datasets fluent")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas",
    "ckanext.dcat.schemas:health_dcat_ap_multilingual.yaml",
)
@pytest.mark.ckan_config(
    "scheming.presets",
    "ckanext.scheming:presets.json ckanext.dcat.schemas:presets.yaml ckanext.fluent:presets.json",
)
@pytest.mark.ckan_config("ckanext.dcat.rdf.profiles", "euro_health_dcat_ap")
class TestEuroDCATAP3ProfileSerializeDatasetFluent(BaseSerializeTest):
    def test_e2e_ckan_to_dcat_multilingual(self):
        dataset_dict = {
            "name": "health-dcat-fluent",
            "title_translated": {
                "en": "Health dataset",
                "nl": "Gezondheidsdataset",
            },
            "notes_translated": {
                "en": "A dataset with multilingual metadata",
                "nl": "Een dataset met meertalige metadata",
            },
            "tags_translated": {
                "en": ["health"],
                "nl": ["gezondheid"],
            },
            "population_coverage": {
                "en": "Population coverage in English",
                "nl": "Populatiedekking in het Nederlands",
            },
            "publisher_note": {
                "en": "Publisher note in English",
                "nl": "Notitie van de uitgever in het Nederlands",
            },
            "publisher": [
                {
                    "name": "Health Institute",
                    "name_translated": {
                        "en": "Health Institute",
                        "nl": "Gezondheidsinstituut",
                    },
                    "email": "info@example.com",
                    "url": "https://healthdata.nl",
                }
            ],
            "creator": [
                {
                    "name": "Health Creator",
                    "name_translated": {
                        "en": "Health Creator",
                        "nl": "Gezondheidsmaker",
                    },
                    "email": "creator@example.com",
                }
            ],
            "resources": [
                {
                    "url": "http://example.test/dataset/1/resource.csv",
                    "name_translated": {
                        "en": "CSV extract",
                        "nl": "CSV-uitvoer",
                    },
                    "description_translated": {
                        "en": "Distribution description in English",
                        "nl": "Beschrijving van de distributie in het Nederlands",
                    },
                    "rights": {
                        "en": "Rights statement",
                        "nl": "Rechtenverklaring",
                    },
                }
            ],
        }

        dataset = call_action("package_create", **dataset_dict)

        serializer = RDFSerializer()
        graph = serializer.g
        dataset_ref = serializer.graph_from_dataset(dataset)

        assert self._triple(graph, dataset_ref, DCT.title, "Health dataset", lang="en")
        assert self._triple(
            graph, dataset_ref, DCT.title, "Gezondheidsdataset", lang="nl"
        )

        assert self._triple(
            graph,
            dataset_ref,
            HEALTHDCATAP.populationCoverage,
            "Population coverage in English",
            lang="en",
        )
        assert self._triple(
            graph,
            dataset_ref,
            HEALTHDCATAP.populationCoverage,
            "Populatiedekking in het Nederlands",
            lang="nl",
        )

        assert self._triple(
            graph,
            dataset_ref,
            HEALTHDCATAP.publisherNote,
            "Publisher note in English",
            lang="en",
        )
        assert self._triple(
            graph,
            dataset_ref,
            HEALTHDCATAP.publisherNote,
            "Notitie van de uitgever in het Nederlands",
            lang="nl",
        )

        publisher_ref = next(graph.objects(dataset_ref, DCT.publisher))
        assert self._triple(
            graph, publisher_ref, FOAF.name, "Health Institute", lang="en"
        )
        assert self._triple(
            graph, publisher_ref, FOAF.name, "Gezondheidsinstituut", lang="nl"
        )

        creator_ref = next(graph.objects(dataset_ref, DCT.creator))
        assert self._triple(
            graph, creator_ref, FOAF.name, "Health Creator", lang="en"
        )
        assert self._triple(
            graph, creator_ref, FOAF.name, "Gezondheidsmaker", lang="nl"
        )

        distribution_ref = self._triple(
            graph, dataset_ref, DCAT.distribution, None
        )[2]

        assert self._triple(
            graph, distribution_ref, DCT.title, "CSV extract", lang="en"
        )
        assert self._triple(
            graph, distribution_ref, DCT.title, "CSV-uitvoer", lang="nl"
        )

        assert self._triple(
            graph,
            distribution_ref,
            DCT.description,
            "Distribution description in English",
            lang="en",
        )
        assert self._triple(
            graph,
            distribution_ref,
            DCT.description,
            "Beschrijving van de distributie in het Nederlands",
            lang="nl",
        )

        rights_node = next(graph.objects(distribution_ref, DCT.rights))
        assert self._triple(
            graph, rights_node, RDFS.label, "Rights statement", lang="en"
        )
        assert self._triple(
            graph, rights_node, RDFS.label, "Rechtenverklaring", lang="nl"
        )
