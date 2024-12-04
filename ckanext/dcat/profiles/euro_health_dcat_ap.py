"""Test document"""

import json

from rdflib import RDF, SKOS, XSD, BNode, Literal, term
from rdflib.namespace import Namespace

from ckanext.dcat.profiles.base import DCAT, DCT, CleanedURIRef, URIRefOrLiteral
from ckanext.dcat.profiles.euro_dcat_ap_3 import EuropeanDCATAP3Profile

# HealthDCAT-AP namespace. Note: not finalized yet
HEALTHDCATAP = Namespace("http://healthdataportal.eu/ns/health#")

# Data Privacy Vocabulary namespace
DPV = Namespace("https://w3id.org/dpv#")

namespaces = {
    "healthdcatap": HEALTHDCATAP,
    "dpv": DPV,
}


class EuropeanHealthDCATAPProfile(EuropeanDCATAP3Profile):
    """
    A profile implementing HealthDCAT-AP, a health-related extension of the DCAT application profile
    for sharing information about Catalogues containing Datasets and Data Services descriptions in Europe.
    """

    def parse_dataset(self, dataset_dict, dataset_ref):
        # Call super method for DCAT-AP 3 properties
        dataset_dict = super(EuropeanHealthDCATAPProfile, self).parse_dataset(
            dataset_dict, dataset_ref
        )

        dataset_dict = self._parse_health_fields(dataset_dict, dataset_ref)

        return dataset_dict

    def _parse_health_fields(self, dataset_dict, dataset_ref):
        self.__parse_healthdcat_stringvalues(dataset_dict, dataset_ref)

        self.__parse_healthdcat_intvalues(dataset_dict, dataset_ref)

        # Purpose is a dpv:Purpose, inside is a dct:Description
        pass

        # Add the HDAB. There should only ever be one but you never know
        agents = self._agents_details(dataset_ref, HEALTHDCATAP.hdab)
        if agents:
            dataset_dict["hdab"] = agents

        # Add any qualifiedRelations
        qual_relations = self._relationship_details(dataset_ref, DCAT.qualifiedRelation)
        if qual_relations:
            dataset_dict["qualified_relation"] = qual_relations

        # Retention period
        retention_start, retention_end = self._time_interval(
            dataset_ref, HEALTHDCATAP.retentionPeriod, dcat_ap_version=2
        )
        retention_dict = {}
        if retention_start is not None:
            retention_dict["start"] = retention_start
        if retention_end is not None:
            retention_dict["end"] = retention_end
        if retention_dict:
            dataset_dict["retention_period"] = [retention_dict]

        return dataset_dict

    def __parse_healthdcat_intvalues(self, dataset_dict, dataset_ref):
        for key, predicate in (
            ("min_typical_age", HEALTHDCATAP.minTypicalAge),
            ("max_typical_age", HEALTHDCATAP.maxTypicalAge),
            ("number_of_records", HEALTHDCATAP.numberOfRecords),
            ("number_of_unique_individuals", HEALTHDCATAP.numberOfUniqueIndividuals),
        ):
            value = self._object_value_int(dataset_ref, predicate)
            # A zero value evaluates as False but is definitely not a None
            if value is not None:
                dataset_dict[key] = value

    def __parse_healthdcat_stringvalues(self, dataset_dict, dataset_ref):
        for (
            key,
            predicate,
        ) in (
            ("analytics", HEALTHDCATAP.analytics),
            ("code_values", HEALTHDCATAP.hasCodeValues),
            ("coding_system", HEALTHDCATAP.hasCodingSystem),
            ("health_category", HEALTHDCATAP.healthCategory),
            ("health_theme", HEALTHDCATAP.healthTheme),
            ("legal_basis", DPV.hasLegalBasis),
            ("population_coverage", HEALTHDCATAP.populationCoverage),
            ("publisher_note", HEALTHDCATAP.publisherNote),
            ("publisher_type", HEALTHDCATAP.publisherType),
            ("purpose", DPV.hasPurpose),
        ):
            values = self._object_value_list(dataset_ref, predicate)
            if values:
                dataset_dict[key] = values

    def graph_from_dataset(self, dataset_dict, dataset_ref):
        super().graph_from_dataset(dataset_dict, dataset_ref)
        for prefix, namespace in namespaces.items():
            self.g.bind(prefix, namespace)

        # g = self.g

        # ("coding_system", HEALTHDCATAP.hasCodingSystem),
        # ("health_category", HEALTHDCATAP.healthCategory),
        # ("health_theme", HEALTHDCATAP.healthTheme),
        # ("population_coverage", HEALTHDCATAP.populationCoverage),
        # ("publisher_note", HEALTHDCATAP.publisherNote),
        # ("publisher_type", HEALTHDCATAP.publisherType),
        # List items:
        #  - Purpose
        #  - Health theme

        ## key, predicate, fallbacks, _type, _class
        items = [
            ("analytics", HEALTHDCATAP.analytics, None, URIRefOrLiteral),
            ("code_values", HEALTHDCATAP.hasCodeValues, None, URIRefOrLiteral),
            ("coding_system", HEALTHDCATAP.hasCodingSystem, None, URIRefOrLiteral),
            ("health_category", HEALTHDCATAP.healthCategory, None, URIRefOrLiteral),
            ("health_theme", HEALTHDCATAP.healthCategory, None, URIRefOrLiteral),
            ("legal_basis", DPV.hasLegalBasis, None, URIRefOrLiteral),
            (
                "population_coverage",
                HEALTHDCATAP.populationCoverage,
                None,
                URIRefOrLiteral,
            ),
            ("publisher_note", HEALTHDCATAP.publisherNote, None, URIRefOrLiteral),
            ("publisher_type", HEALTHDCATAP.publisherType, None, URIRefOrLiteral),
            ("purpose", DPV.hasPurpose, None, URIRefOrLiteral),
        ]
        self._add_list_triples_from_dict(dataset_dict, dataset_ref, items)

        items = [
            ("min_typical_age", HEALTHDCATAP.minTypicalAge),
            ("max_typical_age", HEALTHDCATAP.maxTypicalAge),
            ("number_of_records", HEALTHDCATAP.numberOfRecords),
            ("number_of_unique_individuals", HEALTHDCATAP.numberOfUniqueIndividuals),
        ]
        for key, predicate in items:
            self._add_nonneg_integer_triple(dataset_dict, dataset_ref, key, predicate)

        self._add_agents(dataset_ref, dataset_dict, "hdab", HEALTHDCATAP.hdab)
        self._add_relationship(
            dataset_ref, dataset_dict, "qualified_relation", DCAT.qualifiedRelation
        )

    def _add_nonneg_integer_triple(self, dataset_dict, dataset_ref, key, predicate):
        """
        Adds non-negative integers to the Dataset graph (xsd:nonNegativeInteger)

        dataset_ref: subject of Graph
        key: scheming key in CKAN
        predicate: predicate to use
        """
        value = self._get_dict_value(dataset_dict, key)

        if value:
            try:
                if int(value) < 0:
                    raise ValueError("Not a non-negative integer")
                self.g.add(
                    (
                        dataset_ref,
                        predicate,
                        Literal(int(value), datatype=XSD.nonNegativeInteger),
                    )
                )
            except (ValueError, TypeError):
                self.g.add((dataset_ref, predicate, Literal(value)))

    def _add_timeframe_triple(self, dataset_dict, dataset_ref):
        temporal = dataset_dict.get("temporal_coverage")
        if (
            isinstance(temporal, list)
            and len(temporal)
            and self._not_empty_dict(temporal[0])
        ):
            for item in temporal:
                temporal_ref = BNode()
                self.g.add((temporal_ref, RDF.type, DCT.PeriodOfTime))
                if item.get("start"):
                    self._add_date_triple(temporal_ref, DCAT.startDate, item["start"])
                if item.get("end"):
                    self._add_date_triple(temporal_ref, DCAT.endDate, item["end"])
                self.g.add((dataset_ref, DCT.temporal, temporal_ref))

    def _relationship_details(self, subject, predicate):
        """
        Returns a list of dicts with details about a dcat:Relationship property, e.g.
        dcat:qualifiedRelation

        Both subject and predicate must be rdflib URIRef or BNode objects

        Returns keys for uri, role, and relation with the values set to
        an empty string if they could not be found.
        """

        relations = []
        for relation in self.g.objects(subject, predicate):
            relation_details = {}
            relation_details["uri"] = (
                str(relation) if isinstance(relation, term.URIRef) else ""
            )
            relation_details["role"] = self._object_value(relation, DCAT.hadRole)
            relation_details["relation"] = self._object_value(relation, DCT.relation)
            relations.append(relation_details)

        return relations

    def _add_relationship(
        self,
        dataset_ref,
        dataset_dict,
        relation_key,
        rdf_predicate,
    ):
        """
        Adds one or more Relationships to the RDF graph.

        :param dataset_ref: The RDF reference of the dataset
        :param dataset_dict: The dataset dictionary containing agent information
        :param relation_key: field name in the CKAN dict (.e.g. "qualifiedRelation")
        :param rdf_predicate: The RDF predicate (DCAT.qualifiedRelation)
        """
        relation = dataset_dict.get(relation_key)
        if (
            isinstance(relation, list)
            and len(relation)
            and self._not_empty_dict(relation[0])
        ):
            relations = relation

            for relation in relations:

                agent_uri = relation.get("uri")
                if agent_uri:
                    agent_ref = CleanedURIRef(agent_uri)
                else:
                    agent_ref = BNode()

                self.g.add((agent_ref, DCT.type, DCAT.Relationship))
                self.g.add((dataset_ref, rdf_predicate, agent_ref))

                self._add_triple_from_dict(
                    relation,
                    agent_ref,
                    DCT.relation,
                    "relation",
                    _type=URIRefOrLiteral,
                )
                self._add_triple_from_dict(
                    relation,
                    agent_ref,
                    DCAT.hadRole,
                    "role",
                    _type=URIRefOrLiteral,
                )

    def graph_from_catalog(self, catalog_dict, catalog_ref):
        super().graph_from_catalog(catalog_dict, catalog_ref)
