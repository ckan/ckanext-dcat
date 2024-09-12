import datetime

from dateutil.parser import parse as parse_date
from rdflib import URIRef, BNode, Literal
from ckantoolkit import url_for, config

from ckanext.dcat.utils import resource_uri, publisher_uri_organization_fallback
from .base import RDFProfile, CleanedURIRef
from .base import (
    RDF,
    SCHEMA,
)


class SchemaOrgProfile(RDFProfile):
    """
    An RDF profile based on the schema.org Dataset

    More information and specification:

    http://schema.org/Dataset

    Mapping between schema.org Dataset and DCAT:

    https://www.w3.org/wiki/WebSchemas/Datasets
    """

    def graph_from_dataset(self, dataset_dict, dataset_ref):

        g = self.g

        # Namespaces
        self._bind_namespaces()

        g.add((dataset_ref, RDF.type, SCHEMA.Dataset))

        # Basic fields
        self._basic_fields_graph(dataset_ref, dataset_dict)

        # Catalog
        self._catalog_graph(dataset_ref, dataset_dict)

        # Groups
        self._groups_graph(dataset_ref, dataset_dict)

        # Tags
        self._tags_graph(dataset_ref, dataset_dict)

        #  Lists
        self._list_fields_graph(dataset_ref, dataset_dict)

        # Publisher
        self._agent_graph(dataset_ref, dataset_dict, SCHEMA.publisher, "publisher")

        # Creator
        self._agent_graph(dataset_ref, dataset_dict, SCHEMA.creator, "creator")

        # Temporal
        self._temporal_graph(dataset_ref, dataset_dict)

        # Spatial
        self._spatial_graph(dataset_ref, dataset_dict)

        # Resources
        self._resources_graph(dataset_ref, dataset_dict)

        # Additional fields
        self.additional_fields(dataset_ref, dataset_dict)

    def additional_fields(self, dataset_ref, dataset_dict):
        """
        Adds any additional fields.

        For a custom schema you should extend this class and
        implement this method.
        """
        pass

    def _add_date_triple(self, subject, predicate, value, _type=Literal):
        """
        Adds a new triple with a date object

        Dates are parsed using dateutil, and if the date obtained is correct,
        added to the graph as an SCHEMA.DateTime value.

        If there are parsing errors, the literal string value is added.
        """
        if not value:
            return
        try:
            default_datetime = datetime.datetime(1, 1, 1, 0, 0, 0)
            _date = parse_date(value, default=default_datetime)

            self.g.add((subject, predicate, _type(_date.isoformat())))
        except ValueError:
            self.g.add((subject, predicate, _type(value)))

    def _bind_namespaces(self):
        self.g.namespace_manager.bind("schema", SCHEMA, replace=True)

    def _basic_fields_graph(self, dataset_ref, dataset_dict):
        items = [
            ("identifier", SCHEMA.identifier, None, Literal),
            ("title", SCHEMA.name, None, Literal),
            ("notes", SCHEMA.description, None, Literal),
            ("version", SCHEMA.version, ["dcat_version"], Literal),
            ("issued", SCHEMA.datePublished, ["metadata_created"], Literal),
            ("modified", SCHEMA.dateModified, ["metadata_modified"], Literal),
            ("license", SCHEMA.license, ["license_url", "license_title"], Literal),
        ]
        self._add_triples_from_dict(dataset_dict, dataset_ref, items)

        items = [
            ("issued", SCHEMA.datePublished, ["metadata_created"], Literal),
            ("modified", SCHEMA.dateModified, ["metadata_modified"], Literal),
        ]

        self._add_date_triples_from_dict(dataset_dict, dataset_ref, items)

        # Dataset URL
        dataset_url = url_for("dataset.read", id=dataset_dict["name"], _external=True)
        self.g.add((dataset_ref, SCHEMA.url, Literal(dataset_url)))

    def _catalog_graph(self, dataset_ref, dataset_dict):
        data_catalog = BNode()
        self.g.add((dataset_ref, SCHEMA.includedInDataCatalog, data_catalog))
        self.g.add((data_catalog, RDF.type, SCHEMA.DataCatalog))
        self.g.add((data_catalog, SCHEMA.name, Literal(config.get("ckan.site_title"))))
        self.g.add(
            (
                data_catalog,
                SCHEMA.description,
                Literal(config.get("ckan.site_description")),
            )
        )
        self.g.add((data_catalog, SCHEMA.url, Literal(config.get("ckan.site_url"))))

    def _groups_graph(self, dataset_ref, dataset_dict):
        for group in dataset_dict.get("groups", []):
            group_url = url_for(
                controller="group", action="read", id=group.get("id"), _external=True
            )
            about = BNode()

            self.g.add((about, RDF.type, SCHEMA.Thing))

            self.g.add((about, SCHEMA.name, Literal(group["name"])))
            self.g.add((about, SCHEMA.url, Literal(group_url)))

            self.g.add((dataset_ref, SCHEMA.about, about))

    def _tags_graph(self, dataset_ref, dataset_dict):
        for tag in dataset_dict.get("tags", []):
            self.g.add((dataset_ref, SCHEMA.keywords, Literal(tag["name"])))

    def _list_fields_graph(self, dataset_ref, dataset_dict):
        items = [
            ("language", SCHEMA.inLanguage, None, Literal),
        ]
        self._add_list_triples_from_dict(dataset_dict, dataset_ref, items)

    def _agent_graph(self, dataset_ref, dataset_dict, agent_type, schema_property_prefix):
        uri_key = f"{schema_property_prefix}_uri"
        name_key = f"{schema_property_prefix}_name"
        url_key = f"{schema_property_prefix}_url"
        email_key = f"{schema_property_prefix}_email"
        identifier_key = f"{schema_property_prefix}_identifier"

        if any(
            [
                self._get_dataset_value(dataset_dict, uri_key),
                self._get_dataset_value(dataset_dict, name_key),
                dataset_dict.get("organization"),
            ]
        ):
            agent_uri = self._get_dataset_value(dataset_dict, uri_key)
            agent_uri_fallback = publisher_uri_organization_fallback(dataset_dict)
            agent_name = self._get_dataset_value(dataset_dict, name_key)

            if agent_uri:
                agent_details = CleanedURIRef(agent_uri)
            elif not agent_name and agent_uri_fallback:
                agent_details = CleanedURIRef(agent_uri_fallback)
            else:
                agent_details = BNode()

            self.g.add((agent_details, RDF.type, SCHEMA.Organization))
            self.g.add((dataset_ref, agent_type, agent_details))

            if (
                not agent_name
                and not agent_uri
                and dataset_dict.get("organization")
            ):
                agent_name = dataset_dict["organization"]["title"]
            self.g.add((agent_details, SCHEMA.name, Literal(agent_name)))

            contact_point = BNode()
            self.g.add((contact_point, RDF.type, SCHEMA.ContactPoint))
            self.g.add((agent_details, SCHEMA.contactPoint, contact_point))
            self.g.add((contact_point, SCHEMA.contactType, Literal("customer service")))

            agent_url = self._get_dataset_value(dataset_dict, url_key)
            if not agent_url and dataset_dict.get("organization"):
                agent_url = dataset_dict["organization"].get("url") or config.get(
                    "ckan.site_url"
                )
            self.g.add((contact_point, SCHEMA.url, Literal(agent_url)))

            items = [
                (
                    email_key,
                    SCHEMA.email,
                    ["contact_email", "maintainer_email", "author_email"],
                    Literal,
                ),
                (
                    name_key,
                    SCHEMA.name,
                    ["contact_name", "maintainer", "author"],
                    Literal,
                ),
            ]
            self._add_triples_from_dict(dataset_dict, contact_point, items)

            agent_identifier = self._get_dataset_value(dataset_dict, identifier_key)
            if agent_identifier:
                self.g.add((agent_details, SCHEMA.identifier, Literal(agent_identifier)))

    def _temporal_graph(self, dataset_ref, dataset_dict):
        start = self._get_dataset_value(dataset_dict, "temporal_start")
        end = self._get_dataset_value(dataset_dict, "temporal_end")
        if start or end:
            if start and end:
                self.g.add(
                    (
                        dataset_ref,
                        SCHEMA.temporalCoverage,
                        Literal("%s/%s" % (start, end)),
                    )
                )
            elif start:
                self._add_date_triple(dataset_ref, SCHEMA.temporalCoverage, start)
            elif end:
                self._add_date_triple(dataset_ref, SCHEMA.temporalCoverage, end)

    def _spatial_graph(self, dataset_ref, dataset_dict):
        spatial_uri = self._get_dataset_value(dataset_dict, "spatial_uri")
        spatial_text = self._get_dataset_value(dataset_dict, "spatial_text")
        spatial_geom = self._get_dataset_value(dataset_dict, "spatial")

        if spatial_uri or spatial_text or spatial_geom:
            if spatial_uri:
                spatial_ref = URIRef(spatial_uri)
            else:
                spatial_ref = BNode()

            self.g.add((spatial_ref, RDF.type, SCHEMA.Place))
            self.g.add((dataset_ref, SCHEMA.spatialCoverage, spatial_ref))

            if spatial_text:
                self.g.add((spatial_ref, SCHEMA.description, Literal(spatial_text)))

            if spatial_geom:
                geo_shape = BNode()
                self.g.add((geo_shape, RDF.type, SCHEMA.GeoShape))
                self.g.add((spatial_ref, SCHEMA.geo, geo_shape))

                # the spatial_geom typically contains GeoJSON
                self.g.add((geo_shape, SCHEMA.polygon, Literal(spatial_geom)))

    def _resources_graph(self, dataset_ref, dataset_dict):
        g = self.g
        for resource_dict in dataset_dict.get("resources", []):
            distribution = URIRef(resource_uri(resource_dict))
            g.add((dataset_ref, SCHEMA.distribution, distribution))
            g.add((distribution, RDF.type, SCHEMA.DataDownload))

            self._distribution_graph(distribution, resource_dict)

    def _distribution_graph(self, distribution, resource_dict):
        #  Simple values
        self._distribution_basic_fields_graph(distribution, resource_dict)

        # Lists
        self._distribution_list_fields_graph(distribution, resource_dict)

        # Format
        self._distribution_format_graph(distribution, resource_dict)

        # URL
        self._distribution_url_graph(distribution, resource_dict)

        # Numbers
        self._distribution_numbers_graph(distribution, resource_dict)

    def _distribution_basic_fields_graph(self, distribution, resource_dict):
        items = [
            ("name", SCHEMA.name, None, Literal),
            ("description", SCHEMA.description, None, Literal),
            ("license", SCHEMA.license, ["rights"], Literal),
        ]

        self._add_triples_from_dict(resource_dict, distribution, items)

        items = [
            ("issued", SCHEMA.datePublished, None, Literal),
            ("modified", SCHEMA.dateModified, None, Literal),
        ]

        self._add_date_triples_from_dict(resource_dict, distribution, items)

    def _distribution_list_fields_graph(self, distribution, resource_dict):
        items = [
            ("language", SCHEMA.inLanguage, None, Literal),
        ]
        self._add_list_triples_from_dict(resource_dict, distribution, items)

    def _distribution_format_graph(self, distribution, resource_dict):
        if resource_dict.get("format"):
            self.g.add(
                (distribution, SCHEMA.encodingFormat, Literal(resource_dict["format"]))
            )
        elif resource_dict.get("mimetype"):
            self.g.add(
                (
                    distribution,
                    SCHEMA.encodingFormat,
                    Literal(resource_dict["mimetype"]),
                )
            )

    def _distribution_url_graph(self, distribution, resource_dict):
        url = resource_dict.get("url")
        download_url = resource_dict.get("download_url")
        if download_url:
            self.g.add((distribution, SCHEMA.contentUrl, Literal(download_url)))
        if (url and not download_url) or (url and url != download_url):
            self.g.add((distribution, SCHEMA.url, Literal(url)))

    def _distribution_numbers_graph(self, distribution, resource_dict):
        if resource_dict.get("size"):
            self.g.add(
                (distribution, SCHEMA.contentSize, Literal(resource_dict["size"]))
            )
