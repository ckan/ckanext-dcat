import json
from decimal import Decimal, DecimalException

from rdflib import URIRef, BNode, Literal, Namespace
from ckanext.dcat.utils import resource_uri

from .base import URIRefOrLiteral, CleanedURIRef
from .base import (
    RDF,
    SKOS,
    DCAT,
    DCATAP,
    DCT,
    XSD,
    SCHEMA,
    RDFS,
)

from .euro_dcat_ap import EuropeanDCATAPProfile


ELI = Namespace("http://data.europa.eu/eli/ontology#")


class EuropeanDCATAP2Profile(EuropeanDCATAPProfile):
    """
    An RDF profile based on the DCAT-AP 2 for data portals in Europe

    More information and specification:

    https://joinup.ec.europa.eu/asset/dcat_application_profile

    """

    def parse_dataset(self, dataset_dict, dataset_ref):

        # call super method
        super(EuropeanDCATAP2Profile, self).parse_dataset(dataset_dict, dataset_ref)

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
            # For some reason we incorrectly allowed lists in this property at some point
            # keep support for it but default to single value
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
                    ):
                        value = self._object_value(distribution, predicate)
                        if value:
                            resource_dict[key] = value

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

                        #  Simple values
                        for key, predicate in (
                            ("availability", DCATAP.availability),
                            ("title", DCT.title),
                            ("endpoint_description", DCAT.endpointDescription),
                            ("license", DCT.license),
                            ("access_rights", DCT.accessRights),
                            ("description", DCT.description),
                        ):
                            value = self._object_value(access_service, predicate)
                            if value:
                                access_service_dict[key] = value
                        #  List
                        for key, predicate in (
                            ("endpoint_url", DCAT.endpointURL),
                            ("serves_dataset", DCAT.servesDataset),
                        ):
                            values = self._object_value_list(access_service, predicate)
                            if values:
                                access_service_dict[key] = values

                        # Access service URI (explicitly show the missing ones)
                        access_service_dict["uri"] = (
                            str(access_service)
                            if isinstance(access_service, URIRef)
                            else ""
                        )

                        # Remember the (internal) access service reference for referencing in
                        # further profiles, e.g. for adding more properties
                        access_service_dict["access_service_ref"] = str(access_service)

                        access_service_list.append(access_service_dict)

                    if access_service_list:
                        resource_dict["access_services"] = json.dumps(
                            access_service_list
                        )

        return dataset_dict

    def graph_from_dataset(self, dataset_dict, dataset_ref):

        # call super method
        super(EuropeanDCATAP2Profile, self).graph_from_dataset(
            dataset_dict, dataset_ref
        )

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
            )

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

            distribution = CleanedURIRef(resource_uri(resource_dict))

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

            self._add_triples_from_dict(resource_dict, distribution, items)

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
            self._add_list_triples_from_dict(resource_dict, distribution, items)

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
                    # Remember the (internal) access service reference for referencing in
                    # further profiles
                    access_service_dict["access_service_ref"] = str(access_service_node)

                self.g.add((distribution, DCAT.accessService, access_service_node))

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
                    ),
                    ("description", DCT.description, None, Literal),
                ]

                self._add_triples_from_dict(
                    access_service_dict, access_service_node, items
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

    def graph_from_catalog(self, catalog_dict, catalog_ref):

        # call super method
        super(EuropeanDCATAP2Profile, self).graph_from_catalog(
            catalog_dict, catalog_ref
        )
