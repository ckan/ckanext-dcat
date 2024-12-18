import json

from rdflib import URIRef, BNode, Literal, term
from .base import RDFProfile, CleanedURIRef, URIRefOrLiteral
from .base import (
    RDF,
    DCAT,
    DCT,
    VCARD,
    FOAF,
    SKOS,
    LOCN,
)


class EuropeanDCATAPSchemingProfile(RDFProfile):
    """
    This is a compatibilty profile meant to add support for ckanext-scheming to the
    existing `euro_dcat_ap` and `euro_dcat_ap_2` profiles.
    It does not add or remove any properties from these profiles, it just transforms the
    resulting dataset_dict so it is compatible with a ckanext-scheming schema
    """

    def parse_dataset(self, dataset_dict, dataset_ref):

        return self._parse_dataset_v2_scheming(dataset_dict, dataset_ref)

    def graph_from_dataset(self, dataset_dict, dataset_ref):

        self._graph_from_dataset_v2_scheming(dataset_dict, dataset_ref)

    def _parse_dataset_v2_scheming(self, dataset_dict, dataset_ref):
        """
        Modify the dataset_dict generated by the euro_dcat_ap and euro_dcat_ap_2
        profiles to make it compatible with the scheming file definitions:
            * Move extras to root level fields
            * Parse lists (multiple text preset)
            * Turn namespaced extras into repeating subfields
        """

        if not self._dataset_schema:
            # Not using scheming
            return dataset_dict

        # Move extras to root

        extras_to_remove = []
        extras = dataset_dict.get("extras", [])
        for extra in extras:
            if self._schema_field(extra["key"]):
                # This is a field defined in the dataset schema
                dataset_dict[extra["key"]] = extra["value"]
                extras_to_remove.append(extra["key"])

        dataset_dict["extras"] = [e for e in extras if e["key"] not in extras_to_remove]

        # Parse lists
        def _parse_list_value(data_dict, field_name):
            schema_field = self._schema_field(
                field_name
            ) or self._schema_resource_field(field_name)

            if schema_field and "scheming_multiple_text" in schema_field.get(
                "validators", []
            ):
                if isinstance(data_dict[field_name], str):
                    try:
                        data_dict[field_name] = json.loads(data_dict[field_name])
                    except ValueError:
                        pass

        for field_name in dataset_dict.keys():
            _parse_list_value(dataset_dict, field_name)

        for resource_dict in dataset_dict.get("resources", []):
            for field_name in resource_dict.keys():
                _parse_list_value(resource_dict, field_name)

        # Repeating subfields
        new_fields_mapping = {
            "spatial_coverage": "spatial",
            "temporal_coverage": "temporal",
        }
        for schema_field in self._dataset_schema["dataset_fields"]:
            if "repeating_subfields" in schema_field:
                # Check if existing extras need to be migrated
                field_name = schema_field["field_name"]
                new_extras = []
                new_dict = {}
                check_name = new_fields_mapping.get(field_name, field_name)
                for extra in dataset_dict.get("extras", []):
                    if extra["key"].startswith(f"{check_name}_"):
                        subfield = extra["key"][extra["key"].index("_") + 1 :]
                        if subfield in [
                            f["field_name"] for f in schema_field["repeating_subfields"]
                        ]:
                            new_dict[subfield] = extra["value"]
                        else:
                            new_extras.append(extra)
                    elif extra["key"] == "spatial" and field_name == "spatial_coverage":
                        # Special case, spatial geom
                        new_dict["geom"] = extra["value"]
                    else:
                        new_extras.append(extra)
                if new_dict:
                    dataset_dict[field_name] = [new_dict]
                    dataset_dict["extras"] = new_extras

        # Contact details
        contacts = self._contact_details(dataset_ref, DCAT.contactPoint)
        if contacts:
            dataset_dict["contact"] = contacts

        # Publishers and creators
        for item in [("publisher", DCT.publisher), ("creator", DCT.creator)]:
            key, predicate = item
            agents = self._agents_details(dataset_ref, predicate)
            if agents:
                dataset_dict[key] = agents

        # Add any qualifiedRelations
        qual_relations = self._relationship_details(dataset_ref, DCAT.qualifiedRelation)
        if qual_relations:
            dataset_dict["qualified_relation"] = qual_relations

        # Repeating subfields: resources
        for schema_field in self._dataset_schema["resource_fields"]:
            if "repeating_subfields" in schema_field:
                # Check if value needs to be load from JSON
                field_name = schema_field["field_name"]
                for resource_dict in dataset_dict.get("resources", []):
                    if resource_dict.get(field_name) and isinstance(
                        resource_dict[field_name], str
                    ):
                        try:
                            # TODO: load only subfields in schema?
                            resource_dict[field_name] = json.loads(
                                resource_dict[field_name]
                            )
                        except ValueError:
                            pass

        return dataset_dict

    def _graph_from_dataset_v2_scheming(self, dataset_dict, dataset_ref):
        """
        Add triples to the graph from new repeating subfields
        """
        contact = dataset_dict.get("contact")
        if (
            isinstance(contact, list)
            and len(contact)
            and self._not_empty_dict(contact[0])
        ):
            for item in contact:
                contact_uri = item.get("uri")
                if contact_uri:
                    contact_details = CleanedURIRef(contact_uri)
                else:
                    contact_details = BNode()

                self.g.add((contact_details, RDF.type, VCARD.Kind))
                self.g.add((dataset_ref, DCAT.contactPoint, contact_details))

                self._add_triple_from_dict(item, contact_details, VCARD.fn, "name")
                # Add mail address as URIRef, and ensure it has a mailto: prefix
                self._add_triple_from_dict(
                    item,
                    contact_details,
                    VCARD.hasEmail,
                    "email",
                    _type=URIRef,
                    value_modifier=self._add_mailto,
                )
                self._add_triple_from_dict(
                    item,
                    contact_details,
                    VCARD.hasUID,
                    "identifier",
                    _type=URIRefOrLiteral,
                )
                self._add_triple_from_dict(
                    item,
                    contact_details,
                    VCARD.hasURL,
                    "url",
                    _type=URIRef,
                )

        self._add_agents(dataset_ref, dataset_dict, "publisher", DCT.publisher)
        self._add_agents(dataset_ref, dataset_dict, "creator", DCT.creator)

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

        spatial = dataset_dict.get("spatial_coverage")
        if (
            isinstance(spatial, list)
            and len(spatial)
            and self._not_empty_dict(spatial[0])
        ):
            for item in spatial:
                if item.get("uri"):
                    spatial_ref = CleanedURIRef(item["uri"])
                else:
                    spatial_ref = BNode()
                self.g.add((spatial_ref, RDF.type, DCT.Location))
                self.g.add((dataset_ref, DCT.spatial, spatial_ref))

                if item.get("text"):
                    self.g.add((spatial_ref, SKOS.prefLabel, Literal(item["text"])))

                for field in [
                    ("geom", LOCN.Geometry),
                    ("bbox", DCAT.bbox),
                    ("centroid", DCAT.centroid),
                ]:
                    if item.get(field[0]):
                        self._add_spatial_value_to_graph(
                            spatial_ref, field[1], item[field[0]]
                        )

        self._add_relationship(
            dataset_ref, dataset_dict, "qualified_relation", DCAT.qualifiedRelation
        )

        resources = dataset_dict.get("resources", [])
        for resource in resources:
            if resource.get("access_services"):
                if isinstance(resource["access_services"], str):
                    try:
                        resource["access_services"] = json.loads(
                            resource["access_services"]
                        )
                    except ValueError:
                        pass

    def _add_agents(
        self, dataset_ref, dataset_dict, agent_key, rdf_predicate, first_only=False
    ):
        """
        Adds one or more agents (e.g. publisher or creator) to the RDF graph.

        :param dataset_ref: The RDF reference of the dataset
        :param dataset_dict: The dataset dictionary containing agent information
        :param agent_key: field name in the CKAN dict (.e.g. "publisher", "creator", etc)
        :param rdf_predicate: The RDF predicate (DCT.publisher, DCT.creator, etc)
        :first_only: Add the first item found only (used for 0..1 properties)
        """
        agent = dataset_dict.get(agent_key)
        if isinstance(agent, list) and len(agent) and self._not_empty_dict(agent[0]):
            agents = [agent[0]] if first_only else agent

            for agent in agents:

                agent_uri = agent.get("uri")
                if agent_uri:
                    agent_ref = CleanedURIRef(agent_uri)
                else:
                    agent_ref = BNode()

                self.g.add((agent_ref, RDF.type, FOAF.Agent))
                self.g.add((dataset_ref, rdf_predicate, agent_ref))

                self._add_triple_from_dict(agent, agent_ref, FOAF.name, "name")
                self._add_triple_from_dict(
                    agent, agent_ref, FOAF.homepage, "url", _type=URIRef
                )
                self._add_triple_from_dict(
                    agent,
                    agent_ref,
                    DCT.type,
                    "type",
                    _type=URIRefOrLiteral,
                )
                self._add_triple_from_dict(
                    agent,
                    agent_ref,
                    VCARD.hasEmail,
                    "email",
                    _type=URIRef,
                    value_modifier=self._add_mailto,
                )
                self._add_triple_from_dict(
                    agent,
                    agent_ref,
                    DCT.identifier,
                    "identifier",
                    _type=URIRefOrLiteral,
                )

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

    @staticmethod
    def _not_empty_dict(data_dict):
        return any(data_dict.values())
