import json
from decimal import Decimal, DecimalException

from rdflib import URIRef, BNode, Literal, Namespace, FOAF, PROV, RDF, RDFS
from ckanext.dcat.utils import resource_uri

from .base import URIRefOrLiteral, CleanedURIRef
from .base import (
    RDF,
    DCAT,
    DCATAP,
    DCT,
    XSD,
    SCHEMA,
    RDFS,
    ADMS,
)

from .euro_dcat_ap_base import BaseEuropeanDCATAPProfile

ELI = Namespace("http://data.europa.eu/eli/ontology#")


class EuropeanDCATAP2Profile(BaseEuropeanDCATAPProfile):
    """
    An RDF profile based on the DCAT-AP 2 for data portals in Europe

    More information and specification:

    https://joinup.ec.europa.eu/asset/dcat_application_profile

    """

    def parse_dataset(self, dataset_dict, dataset_ref):

        # Call base method for common properties
        dataset_dict = self._parse_dataset_base(dataset_dict, dataset_ref)

        # DCAT AP v2 properties also applied to higher versions
        dataset_dict = self._parse_dataset_v2(dataset_dict, dataset_ref)

        return dataset_dict

    def graph_from_dataset(self, dataset_dict, dataset_ref):

        # Call base method for common properties
        self._graph_from_dataset_base(dataset_dict, dataset_ref)

        # DCAT AP v2 properties also applied to higher versions
        self._graph_from_dataset_v2(dataset_dict, dataset_ref)

        # DCAT AP v2 specific properties
        self._graph_from_dataset_v2_only(dataset_dict, dataset_ref)

    def graph_from_catalog(self, catalog_dict, catalog_ref):

        self._graph_from_catalog_base(catalog_dict, catalog_ref)

    def _parse_dataset_v2(self, dataset_dict, dataset_ref):
        """
        DCAT -> CKAN properties carried forward to higher DCAT-AP versions
        """

        # Call base super method for common properties
        super().parse_dataset(dataset_dict, dataset_ref)

        # --- Provenance deserialization ---
        was_generated_by = self.g.value(dataset_ref, PROV.wasGeneratedBy)
        if was_generated_by:
            activity_dict = {}
            activity_dict["uri"] = str(was_generated_by)
            activity_dict["type"] = [
                str(t) for t in self.g.objects(was_generated_by, RDF.type)
            ]
            activity_dict["label"] = self._object_value(was_generated_by, RDFS.label)
            activity_dict["seeAlso"] = self._object_value(was_generated_by, RDFS.seeAlso)
            activity_dict["dct_type"] = self._object_value(was_generated_by, DCT.type)
            activity_dict["startedAtTime"] = self._object_value(
                was_generated_by, PROV.startedAtTime
            )

            agents = self._agents_details(was_generated_by, PROV.wasAssociatedWith)
            if agents:
                activity_dict["wasAssociatedWith"] = [agents[0]] # Only take the first agent

            dataset_dict["provenance_activity"] = [activity_dict]

        # --- Qualified Attribution ---
        qualified_attributions = self._parse_qualified_attributions(dataset_ref)
        if qualified_attributions:
            dataset_dict["qualified_attribution"] = qualified_attributions
        
        # Standard values
        value = self._object_value(dataset_ref, DCAT.temporalResolution)
        if value:
            dataset_dict["extras"].append(
                {"key": "temporal_resolution", "value": value}
            )

        # Lists
        for key, predicate in (
            ("is_referenced_by", DCT.isReferencedBy),
            ("applicable_legislation", DCATAP.applicableLegislation),
            ("hvd_category", DCATAP.hvdCategory),
        ):
            values = self._object_value_list(dataset_ref, predicate)
            if values:
                dataset_dict["extras"].append({"key": key, "value": json.dumps(values)})
        # Temporal
        start, end = self._time_interval(dataset_ref, DCT.temporal, dcat_ap_version=2)
        if start:
            self._insert_or_update_temporal(dataset_dict, "temporal_start", start)
        if end:
            self._insert_or_update_temporal(dataset_dict, "temporal_end", end)

        # Spatial
        spatial = self._spatial(dataset_ref, DCT.spatial)
        for key in ("bbox", "centroid"):
            self._add_spatial_to_dict(dataset_dict, key, spatial)

        # Spatial resolution in meters
        spatial_resolution = self._object_value_float_list(
            dataset_ref, DCAT.spatialResolutionInMeters
        )
        if spatial_resolution:
            # For some reason we incorrectly allowed lists in this property at
            # some point, keep support for it but default to single value
            value = (
                spatial_resolution[0]
                if len(spatial_resolution) == 1
                else json.dumps(spatial_resolution)
            )
            dataset_dict["extras"].append(
                {
                    "key": "spatial_resolution_in_meters",
                    "value": value,
                }
            )

        # Resources
        for distribution in self._distributions(dataset_ref):
            distribution_ref = str(distribution)
            for resource_dict in dataset_dict.get("resources", []):
                # Match distribution in graph and distribution in resource dict
                if resource_dict and distribution_ref == resource_dict.get(
                    "distribution_ref"
                ):
                    #  Simple values
                    for key, predicate in (
                        ("availability", DCATAP.availability),
                        ("compress_format", DCAT.compressFormat),
                        ("package_format", DCAT.packageFormat),
                        ("temporal_resolution", DCAT.temporalResolution),
                    ):
                        value = self._object_value(distribution, predicate)
                        if value:
                            resource_dict[key] = value

                    # Spatial resolution in meters
                    spatial_resolution = self._object_value_float_list(
                        distribution, DCAT.spatialResolutionInMeters
                    )
                    if spatial_resolution:
                        value = (
                            spatial_resolution[0]
                            if len(spatial_resolution) == 1
                            else json.dumps(spatial_resolution)
                        )
                        resource_dict["spatial_resolution_in_meters"] = value

                    #  Lists
                    for key, predicate in (
                        ("applicable_legislation", DCATAP.applicableLegislation),
                    ):
                        values = self._object_value_list(distribution, predicate)
                        if values:
                            resource_dict[key] = json.dumps(values)

                    # Access services
                    access_service_list = []

                    for access_service in self.g.objects(
                        distribution, DCAT.accessService
                    ):
                        access_service_dict = {}

                        # Simple values
                        for key, predicate in (
                            ("availability", DCATAP.availability),
                            ("title", DCT.title),
                            ("endpoint_description", DCAT.endpointDescription),
                            ("license", DCT.license),
                            ("access_rights", DCT.accessRights),
                            ("description", DCT.description),
                            ("identifier", DCT.identifier),
                            ("description", DCT.description),
                            ("modified", DCT.modified),
                        ):
                            value = self._object_value(access_service, predicate)
                            if value:
                                access_service_dict[key] = value

                        # List values
                        for key, predicate in (
                            ("endpoint_url", DCAT.endpointURL),
                            ("serves_dataset", DCAT.servesDataset),
                            ("conforms_to", DCT.conformsTo),
                            ("format", DCT["format"]),
                            ("language", DCT.language),
                            ("rights", DCT.rights),
                            ("landing_page", DCAT.landingPage),
                            ("keyword", DCAT.keyword),
                            ("applicable_legislation", DCATAP.applicableLegislation),
                            ("theme", DCAT.theme),
                        ):
                            values = self._object_value_list(access_service, predicate)
                            if values:
                                access_service_dict[key] = values

                        contact_points = self._contact_details(access_service, DCAT.contactPoint)
                        if contact_points:
                            access_service_dict["contact"] = contact_points
                            
                        publishers = self._agents_details(access_service, DCT.publisher)
                        if publishers:
                            access_service_dict["publisher"] = publishers

                        creators = self._agents_details(access_service, DCT.creator)
                        if creators:
                            access_service_dict["creator"] = creators

                        # Access service URI (explicitly show the missing ones)
                        access_service_dict["uri"] = (
                            str(access_service)
                            if isinstance(access_service, URIRef)
                            else ""
                        )

                        # Remember the (internal) access service reference for
                        # referencing in further profiles, e.g. for adding more
                        # properties
                        access_service_dict["access_service_ref"] = str(access_service)

                        access_service_list.append(access_service_dict)

                    if access_service_list:
                        resource_dict["access_services"] = json.dumps(
                            access_service_list
                        )

        return dataset_dict

    def _graph_from_dataset_v2(self, dataset_dict, dataset_ref):
        """
        CKAN -> DCAT properties carried forward to higher DCAT-AP versions
        """

        # Standard values
        self._add_triple_from_dict(
            dataset_dict,
            dataset_ref,
            DCAT.temporalResolution,
            "temporal_resolution",
            _datatype=XSD.duration,
        )

        # Lists
        for key, predicate, fallbacks, type, datatype, _class in (
            (
                "is_referenced_by",
                DCT.isReferencedBy,
                None,
                URIRefOrLiteral,
                None,
                RDFS.Resource,
            ),
            (
                "applicable_legislation",
                DCATAP.applicableLegislation,
                None,
                URIRefOrLiteral,
                None,
                ELI.LegalResource,
            ),
            ("hvd_category", DCATAP.hvdCategory, None, URIRefOrLiteral, None, None),
        ):
            self._add_triple_from_dict(
                dataset_dict,
                dataset_ref,
                predicate,
                key,
                list_value=True,
                fallbacks=fallbacks,
                _type=type,
                _datatype=datatype,
                _class=_class,
            )

        # --- Provenance serialization ---
        activities = dataset_dict.get("provenance_activity", [])

        for activity in activities:
            activity_uri = URIRef(activity.get("uri")) if activity.get("uri") else BNode()
            self.g.add((dataset_ref, PROV.wasGeneratedBy, activity_uri))
            self.g.add((activity_uri, RDF.type, PROV.Activity))

            if activity.get("label"):
                self.g.add((activity_uri, RDFS.label, Literal(activity["label"])))
            if activity.get("seeAlso"):
                self.g.add((activity_uri, RDFS.seeAlso, URIRef(activity["seeAlso"])))
            if activity.get("dct_type"):
                self.g.add((activity_uri, DCT.type, URIRef(activity["dct_type"])))
            if activity.get("startedAtTime"):
                self.g.add((activity_uri, PROV.startedAtTime, Literal(activity["startedAtTime"], datatype=XSD.dateTime)))

            for agent_dict in activity.get("wasAssociatedWith", []):
                self._add_agent_to_graph(activity_uri, PROV.wasAssociatedWith, agent_dict)

        # Qualified Attribution
        qualified_attributions = dataset_dict.get("qualified_attribution", [])
        for attr in qualified_attributions:
            attr_ref = BNode()
            self.g.add((dataset_ref, DCAT.qualifiedAttribution, attr_ref))
            self.g.add((attr_ref, RDF.type, DCAT.Attribution))

            agent_list = attr.get("agent", [])
            for agent_dict in agent_list:
                if isinstance(agent_dict, dict):
                    self._add_agent_to_graph(attr_ref, DCAT.agent, agent_dict)
                elif isinstance(agent_dict, str):
                    self.g.add((attr_ref, DCAT.agent, URIRef(agent_dict)))
            role = attr.get("role")
            if role:
                self.g.add((attr_ref, DCAT.hadRole, URIRef(role)))


        # Temporal

        # The profile for DCAT-AP 1 stored triples using schema:startDate,
        # remove them to avoid duplication
        for temporal in self.g.objects(dataset_ref, DCT.temporal):
            if SCHEMA.startDate in [t for t in self.g.predicates(temporal, None)]:
                self.g.remove((temporal, None, None))
                self.g.remove((dataset_ref, DCT.temporal, temporal))

        start = self._get_dataset_value(dataset_dict, "temporal_start")
        end = self._get_dataset_value(dataset_dict, "temporal_end")
        if start or end:
            temporal_extent_dcat = BNode()

            self.g.add((temporal_extent_dcat, RDF.type, DCT.PeriodOfTime))
            if start:
                self._add_date_triple(temporal_extent_dcat, DCAT.startDate, start)
            if end:
                self._add_date_triple(temporal_extent_dcat, DCAT.endDate, end)
            self.g.add((dataset_ref, DCT.temporal, temporal_extent_dcat))

        # spatial
        spatial_bbox = self._get_dataset_value(dataset_dict, "spatial_bbox")
        spatial_cent = self._get_dataset_value(dataset_dict, "spatial_centroid")

        if spatial_bbox or spatial_cent:
            spatial_ref = self._get_or_create_spatial_ref(dataset_dict, dataset_ref)

            if spatial_bbox:
                self._add_spatial_value_to_graph(spatial_ref, DCAT.bbox, spatial_bbox)

            if spatial_cent:
                self._add_spatial_value_to_graph(
                    spatial_ref, DCAT.centroid, spatial_cent
                )

        # Spatial resolution in meters
        spatial_resolution_in_meters = self._read_list_value(
            self._get_dataset_value(dataset_dict, "spatial_resolution_in_meters")
        )
        if spatial_resolution_in_meters:
            for value in spatial_resolution_in_meters:
                try:
                    self.g.add(
                        (
                            dataset_ref,
                            DCAT.spatialResolutionInMeters,
                            Literal(Decimal(value), datatype=XSD.decimal),
                        )
                    )
                except (ValueError, TypeError, DecimalException):
                    self.g.add(
                        (dataset_ref, DCAT.spatialResolutionInMeters, Literal(value))
                    )

        # Resources
        for resource_dict in dataset_dict.get("resources", []):

            distribution_ref = CleanedURIRef(resource_uri(resource_dict))

            #  Simple values
            items = [
                ("availability", DCATAP.availability, None, URIRefOrLiteral),
                (
                    "compress_format",
                    DCAT.compressFormat,
                    None,
                    URIRefOrLiteral,
                    DCT.MediaType,
                ),
                (
                    "package_format",
                    DCAT.packageFormat,
                    None,
                    URIRefOrLiteral,
                    DCT.MediaType,
                ),
            ]

            self._add_triples_from_dict(resource_dict, distribution_ref, items)

            # Temporal resolution
            self._add_triple_from_dict(
                resource_dict,
                distribution_ref,
                DCAT.temporalResolution,
                "temporal_resolution",
                _datatype=XSD.duration,
            )

            # Spatial resolution in meters
            spatial_resolution_in_meters = self._read_list_value(
                self._get_resource_value(resource_dict, "spatial_resolution_in_meters")
            )
            if spatial_resolution_in_meters:
                for value in spatial_resolution_in_meters:
                    try:
                        self.g.add(
                            (
                                distribution_ref,
                                DCAT.spatialResolutionInMeters,
                                Literal(Decimal(value), datatype=XSD.decimal),
                            )
                        )
                    except (ValueError, TypeError, DecimalException):
                        self.g.add(
                            (
                                distribution_ref,
                                DCAT.spatialResolutionInMeters,
                                Literal(value),
                            )
                        )
            #  Lists
            items = [
                (
                    "applicable_legislation",
                    DCATAP.applicableLegislation,
                    None,
                    URIRefOrLiteral,
                    ELI.LegalResource,
                ),
            ]
            self._add_list_triples_from_dict(resource_dict, distribution_ref, items)

            # Access services
            access_service_list = resource_dict.get("access_services", [])
            if isinstance(access_service_list, str):
                try:
                    access_service_list = json.loads(access_service_list)
                except ValueError:
                    access_service_list = []

            for access_service_dict in access_service_list:

                access_service_uri = access_service_dict.get("uri")
                if access_service_uri:
                    access_service_node = CleanedURIRef(access_service_uri)
                else:
                    access_service_node = BNode()
                    # Remember the (internal) access service reference for referencing
                    # in further profiles
                    access_service_dict["access_service_ref"] = str(access_service_node)

                self.g.add((distribution_ref, DCAT.accessService, access_service_node))

                self.g.add((access_service_node, RDF.type, DCAT.DataService))

                #  Simple values
                items = [
                    ("availability", DCATAP.availability, None, URIRefOrLiteral),
                    ("license", DCT.license, None, URIRefOrLiteral),
                    ("access_rights", DCT.accessRights, None, URIRefOrLiteral),
                    ("title", DCT.title, None, Literal),
                    (
                        "endpoint_description",
                        DCAT.endpointDescription,
                        None,
                        URIRefOrLiteral,
                        RDFS.Resource,
                    ),
                    ("description", DCT.description, None, Literal),
                    ("modified", DCT.modified, None, Literal),
                ]
                self._add_triples_from_dict(
                    access_service_dict, access_service_node, items
                )

                if access_service_dict.get("modified"):
                    self._add_date_triple(access_service_node, DCT.modified, access_service_dict.get("modified"))


                contact_point_dict = access_service_dict.get("contact")
                if contact_point_dict:
                    self._add_contact_to_graph(access_service_node, DCAT.contactPoint, contact_point_dict)

                publisher_dict = access_service_dict.get("publisher")
                if publisher_dict:
                    self._add_agent_to_graph(access_service_node, DCT.publisher, publisher_dict)

                for creator_dict in access_service_dict.get("creator", []):
                    self._add_agent_to_graph(access_service_node, DCT.creator, creator_dict)

                # Extra list values for access services
                extra_items = [
                    ("conforms_to", DCT.conformsTo, None, URIRefOrLiteral),
                    ("format", DCT["format"], None, URIRefOrLiteral),
                    ("language", DCT.language, None, URIRefOrLiteral),
                    ("rights", DCT.rights, None, URIRefOrLiteral),
                    ("landing_page", DCAT.landingPage, None, URIRefOrLiteral),
                    ("applicable_legislation", DCATAP.applicableLegislation, None, URIRefOrLiteral, ELI.LegalResource),
                    ("theme", DCAT.theme, None, URIRefOrLiteral),
                ]
                self._add_list_triples_from_dict(access_service_dict, access_service_node, extra_items)

                # Add single-value triple for identifier
                self._add_triple_from_dict(
                    access_service_dict,
                    access_service_node,
                    DCT.identifier,
                    "identifier",
                    _type=URIRefOrLiteral
                )

                # Add keyword list
                self._add_triple_from_dict(
                    access_service_dict,
                    access_service_node,
                    DCAT.keyword,
                    "keyword",
                    list_value=True,
                    _type=Literal
                )

                #  Lists
                items = [
                    (
                        "endpoint_url",
                        DCAT.endpointURL,
                        None,
                        URIRefOrLiteral,
                        RDFS.Resource,
                    ),
                    ("serves_dataset", DCAT.servesDataset, None, URIRefOrLiteral),
                ]
                self._add_list_triples_from_dict(
                    access_service_dict, access_service_node, items
                )

            if access_service_list:
                resource_dict["access_services"] = json.dumps(access_service_list)

    def _graph_from_dataset_v2_only(self, dataset_dict, dataset_ref):
        """
        CKAN -> DCAT v2 specific properties (not applied to higher versions)
        """

        # Other identifiers (these are handled differently in the
        # DCAT-AP v3 profile)
        self._add_triple_from_dict(
            dataset_dict,
            dataset_ref,
            ADMS.identifier,
            "alternate_identifier",
            list_value=True,
            _type=URIRefOrLiteral,
            _class=ADMS.Identifier,
        )
        
    def _parse_qualified_attributions(self, dataset_ref):
        attributions = []
        for qual_attr_ref in self.g.objects(dataset_ref, PROV.qualifiedAttribution):
            attr = {}

            # Get role
            for role_ref in self.g.objects(qual_attr_ref, DCAT.hadRole):
                attr["role"] = str(role_ref)
                break

            # Get agent (using shared logic)
            agent_details = self._agents_details(qual_attr_ref, PROV.agent)
            if agent_details:
                attr["agent"] = agent_details

            if attr:
                attributions.append(attr)

        return attributions
