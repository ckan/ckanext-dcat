# This file is based on profiles/schemaorg.py, and adjusted to suit the Croissant specification, including
# extra fields that will be present if schemas/croissant.yaml is enabled for use with the ckanext-scheming
# extension. The overarching features of the original file are the same here, but the term 'distribution'
# has been replaced with 'resource' for better internal consistency, as well as some other nomenclature
# changes for clarity.

import datetime

from dateutil.parser import parse as parse_date
from rdflib import URIRef, BNode, Literal
from ckantoolkit import url_for, config

from ckanext.dcat.utils import resource_uri
from .base import RDFProfile, CleanedURIRef
from .base import (
    CR,
    DCT,
    RDF,
    SCHEMA,
)

class CroissantProfile(RDFProfile):
    """
    An RDF profile based on the schema.org Dataset, modified by Croissant.

    More information and specification:

    http://schema.org/Dataset
    https://docs.mlcommons.org/croissant/docs/croissant-spec.html

    Mapping between schema.org Dataset and DCAT:

    https://www.w3.org/wiki/WebSchemas/Datasets
    """

    def graph_from_dataset(self, dataset_dict, dataset_ref):

        g = self.g

        # Namespaces
        self._bind_namespaces()

        dataset_id_given = self._get_dict_value(dataset_dict, "id_given") # optional
        if dataset_id_given:
            dataset_ref = CleanedURIRef(dataset_id_given)

        g.add((dataset_ref, RDF.type, SCHEMA.Dataset))

        # Basic fields
        self._basic_fields_graph(dataset_ref, dataset_dict)

        # Catalog
        self._catalog_graph(dataset_ref, dataset_dict)

        # Groups
        self._groups_graph(dataset_ref, dataset_dict)

        # Tags
        self._tags_graph(dataset_ref, dataset_dict)

        # Lists
        self._list_fields_graph(dataset_ref, dataset_dict)

        # Creator
        self._agent_graph(dataset_ref, dataset_dict, SCHEMA.creator)

        # Publisher
        self._agent_graph(dataset_ref, dataset_dict, SCHEMA.publisher)

        # Temporal
        self._temporal_graph(dataset_ref, dataset_dict)

        # Spatial
        self._spatial_graph(dataset_ref, dataset_dict)

        # Additional fields
        self.additional_fields(dataset_ref, dataset_dict)

        # Resources
        self._resources_graph(dataset_ref, dataset_dict)

    def _add_date_triple(self, subject, predicate, value, _type=Literal):
        """
        Adds a new triple with a date object.

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
        self.g.namespace_manager.bind("cr", CR, replace=True)
        self.g.namespace_manager.bind("schema", SCHEMA, replace=True)

    def _basic_fields_graph(self, dataset_ref, dataset_dict):
        self.g.add((dataset_ref, DCT.conformsTo, Literal("http://mlcommons.org/croissant/1.0"))) # required

        items = [
            # Elements here are like: (key, predicate, fallbacks, _type)
            ("title", SCHEMA.name, None, Literal), # required
            ("notes", SCHEMA.description, None, Literal), # required
            ("version", SCHEMA.version, None, Literal), # recommended
            ("cite_as", CR.citeAs, None, Literal), # optional
            ("license", SCHEMA.license, ["license_url", "license_title"], Literal), # required. Being here implies a cardinality of ONE, but the Croissant specification really indicates a cardinality of MANY. See _list_fields_graph() for the approach that would allow this. Keeping here in order to work with the default schema.
            ("structured_data_license", SCHEMA.sdLicense, None, Literal), # recommended. Being here implies a cardinality of ONE, but the Croissant specification really indicates a cardinality of MANY. See _list_fields_graph() for the approach that would allow this. Keeping here in order to match license.
        ]
        self._add_triples_from_dict(dataset_dict, dataset_ref, items)

        items = [
            ("created", SCHEMA.dateCreated, None, Literal), # recommended
            ("issued", SCHEMA.datePublished, ["metadata_created"], Literal), # required
            ("modified", SCHEMA.dateModified, ["metadata_modified"], Literal), # recommended
        ]
        self._add_date_triples_from_dict(dataset_dict, dataset_ref, items)

        dataset_url = url_for("dataset.read", id=dataset_dict["name"], _external=True) # required
        self.g.add((dataset_ref, SCHEMA.url, Literal(dataset_url)))

        if dataset_dict.get("is_live_dataset") == "True":
            is_live_dataset = True
        elif dataset_dict.get("is_live_dataset") == "False":
            is_live_dataset = False
        else:
            is_live_dataset = None

        if is_live_dataset is not None:
            self.g.add((dataset_ref, CR.isLiveDataset, Literal(is_live_dataset))) # optional

    def _catalog_graph(self, dataset_ref, dataset_dict):
        catalog_ref = BNode()
        self.g.add((dataset_ref, SCHEMA.includedInDataCatalog, catalog_ref))
        self.g.add((catalog_ref, RDF.type, SCHEMA.DataCatalog))
        self.g.add((catalog_ref, SCHEMA.name, Literal(config.get("ckan.site_title"))))
        self.g.add((catalog_ref, SCHEMA.description, Literal(config.get("ckan.site_description"))))
        self.g.add((catalog_ref, SCHEMA.url, Literal(config.get("ckan.site_url"))))

    def _groups_graph(self, dataset_ref, dataset_dict):
        for group_dict in dataset_dict.get("groups", []):
            group_url = url_for(controller="group", action="read", id=group_dict.get("id"), _external=True)
            about_ref = BNode()
            self.g.add((dataset_ref, SCHEMA.about, about_ref))
            self.g.add((about_ref, RDF.type, SCHEMA.Thing))
            self.g.add((about_ref, SCHEMA.name, Literal(group_dict["name"])))
            self.g.add((about_ref, SCHEMA.url, Literal(group_url)))

    def _tags_graph(self, dataset_ref, dataset_dict):
        for tag in dataset_dict.get("tags", []):
            self.g.add((dataset_ref, SCHEMA.keywords, Literal(tag["name"]))) # recommended

    def _list_fields_graph(self, dataset_ref, dataset_dict):
        items = [
            ("language", SCHEMA.inLanguage, None, Literal), # recommended
            ("same_as", SCHEMA.sameAs, None, Literal), # recommended
            # ("license", SCHEMA.license, None, Literal), # required. This would appear here if using the Croissant cardinality of MANY. See schemas/croissant.yaml for further details.
            # ("structured_data_license", SCHEMA.sdLicense, None, Literal), # recommended. This would appear here is using the Croissant cardinality of MANY. See schemas/croissant.yaml for further details.
        ]
        self._add_list_triples_from_dict(dataset_dict, dataset_ref, items)

    def _agent_graph(self, dataset_ref, dataset_dict, agent_type):
        agent_dicts = []
        if agent_type == SCHEMA.creator:
            if isinstance(self._get_dataset_value(dataset_dict, "creator"), list):
                agent_dicts = self._get_dataset_value(dataset_dict, "creator") # required
            if len(agent_dicts) == 0 and isinstance(self._get_dataset_value(dataset_dict, "organization"), dict):
                agent_dict = self._get_dataset_value(dataset_dict, "organization")
                agent_dict["id_given"] = agent_dict["id"]
                if not agent_dict.get("email") and self._get_dataset_value(dataset_dict, "maintainer_email"):
                    agent_dict["email"] = self._get_dataset_value(dataset_dict, "maintainer_email")
                if not agent_dict.get("email") and self._get_dataset_value(dataset_dict, "author_email"):
                    agent_dict["email"] = self._get_dataset_value(dataset_dict, "author_email")
                if not agent_dict.get("url") and config.get("ckan.site_url"):
                    agent_dict["url"] = config.get("ckan.site_url")
                agent_dicts = [agent_dict]
        elif agent_type == SCHEMA.publisher:
            if isinstance(self._get_dataset_value(dataset_dict, "publisher"), list):
                agent_dicts = self._get_dataset_value(dataset_dict, "publisher") # recommended

        for agent_dict in agent_dicts:
            if agent_dict.get("type") == "organization":
                agent_type_specific = SCHEMA.Organization
            elif agent_dict.get("type") == "person":
                agent_type_specific = SCHEMA.Person
            else:
                agent_type_specific = SCHEMA.Organization

            agent_id_given = self._get_dict_value(agent_dict, "id_given") # optional
            if agent_id_given:
                agent_ref = CleanedURIRef(agent_id_given)
            else:
                agent_ref = BNode()

            self.g.add((dataset_ref, agent_type, agent_ref))
            self.g.add((agent_ref, RDF.type, agent_type_specific))

            items = [
                ("identifier", SCHEMA.identifier, None, Literal),
                ("title", SCHEMA.name, None, Literal),
                ("email", SCHEMA.email, None, Literal),
                ("url", SCHEMA.url, None, Literal),
            ]
            self._add_triples_from_dict(agent_dict, agent_ref, items)

    def _temporal_graph(self, dataset_ref, dataset_dict):
        start = self._get_dataset_value(dataset_dict, "temporal_start")
        end = self._get_dataset_value(dataset_dict, "temporal_end")
        if start or end:
            if start and end:
                self.g.add((dataset_ref, SCHEMA.temporalCoverage, Literal("%s/%s" % (start, end))))
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

            self.g.add((dataset_ref, SCHEMA.spatialCoverage, spatial_ref))
            self.g.add((spatial_ref, RDF.type, SCHEMA.Place))

            if spatial_text:
                self.g.add((spatial_ref, SCHEMA.description, Literal(spatial_text)))

            if spatial_geom:
                geom_ref = BNode()
                self.g.add((spatial_ref, SCHEMA.geo, geom_ref))
                self.g.add((geom_ref, RDF.type, SCHEMA.GeoShape))
                # The spatial_geom typically contains GeoJSON
                self.g.add((geom_ref, SCHEMA.polygon, Literal(spatial_geom)))

    def additional_fields(self, dataset_ref, dataset_dict):
        """
        Adds any additional fields.

        For a custom schema you should extend this class and
        implement this method.
        """
        pass

    def _resources_graph(self, dataset_ref, dataset_dict):
        for resource_dict in dataset_dict.get("resources", []):
            if resource_dict.get("type") == "fileObject":
                resource_type_specific = CR.FileObject
            elif resource_dict.get("type") == "fileSet":
                resource_type_specific = CR.FileSet
            else:
                resource_type_specific = CR.FileObject

            resource_id_given = self._get_dict_value(resource_dict, "id_given") # optional
            if resource_id_given:
                resource_ref = CleanedURIRef(resource_id_given)
            else:
                resource_ref = URIRef(resource_uri(resource_dict)) # This is called 'distribution' in profiles/schemaorg.py. Changed for better internal consistency.

            self.g.add((dataset_ref, SCHEMA.distribution, resource_ref))
            self.g.add((resource_ref, RDF.type, resource_type_specific)) # This is SCHEMA.DataDownload in profiles/schemaorg.py. Changed for compliance with the Croissant specification.

            self._resource_graph(dataset_ref, resource_ref, resource_dict)

    def _resource_graph(self, dataset_ref, resource_ref, resource_dict):
        # Basic fields
        self._resource_basic_fields_graph(resource_ref, resource_dict)

        # Lists
        self._resource_list_fields_graph(resource_ref, resource_dict)

        # Format
        self._resource_format_graph(resource_ref, resource_dict)

        # URL
        self._resource_url_graph(resource_ref, resource_dict)

        # Numbers
        self._resource_numbers_graph(resource_ref, resource_dict)

        # Subresources
        self._resource_subresources_graph(dataset_ref, resource_ref, resource_dict)

    def _resource_basic_fields_graph(self, resource_ref, resource_dict):
        items = [
            ("name", SCHEMA.name, None, Literal),
            ("description", SCHEMA.description, None, Literal),
            ("hash", SCHEMA.sha256, None, Literal),
        ]
        self._add_triples_from_dict(resource_dict, resource_ref, items)

    def _resource_list_fields_graph(self, resource_ref, resource_dict):
        items = [
            ("same_as", SCHEMA.sameAs, None, Literal),
        ]
        self._add_list_triples_from_dict(resource_dict, resource_ref, items)

    def _resource_format_graph(self, resource_ref, resource_dict):
        if resource_dict.get("format"):
            self.g.add((resource_ref, SCHEMA.encodingFormat, Literal(resource_dict["format"])))
        elif resource_dict.get("mimetype"):
            self.g.add((resource_ref, SCHEMA.encodingFormat, Literal(resource_dict["mimetype"])))

    def _resource_url_graph(self, resource_ref, resource_dict):
        if resource_dict.get("url"):
            self.g.add((resource_ref, SCHEMA.contentUrl, Literal(resource_dict.get("url"))))

    def _resource_numbers_graph(self, resource_ref, resource_dict):
        if resource_dict.get("size"):
            self.g.add((resource_ref, SCHEMA.contentSize, Literal(resource_dict["size"])))

    def _resource_subresources_graph(self, dataset_ref, resource_ref, resource_dict):
        subresource_dicts = self._get_resource_value(resource_dict, "subresources")

        if isinstance(subresource_dicts, list):
            subresource_dicts = [
                subresource_dict
                for subresource_dict in subresource_dicts
                if any(subresource_dict.values())
            ]

            for subresource_dict in subresource_dicts:
                if subresource_dict.get("type") == "fileObject":
                    subresource_type_specific = CR.FileObject
                elif subresource_dict.get("type") == "fileSet":
                    subresource_type_specific = CR.FileSet
                else:
                    subresource_type_specific = CR.FileObject

                subresource_id_given = self._get_dict_value(subresource_dict, "id_given") # optional
                if subresource_id_given:
                    subresource_ref = CleanedURIRef(subresource_id_given)
                else:
                    subresource_ref = BNode()

                self.g.add((dataset_ref, SCHEMA.distribution, subresource_ref)) # Note that this is added to the dataset_ref node, not to the resource_ref node
                self.g.add((subresource_ref, RDF.type, subresource_type_specific))

                items = [
                    ("description", SCHEMA.description, None, Literal),
                    ("format", SCHEMA.encodingFormat, None, Literal),
                ]
                self._add_triples_from_dict(subresource_dict, subresource_ref, items)

                if resource_dict.get("type") == "fileSet":
                    items = [
                        ("includes", CR.includes, None, Literal),
                        ("excludes", CR.excludes, None, Literal),
                    ]
                    self._add_list_triples_from_dict(subresource_dict, subresource_ref, items)

                self.g.add((subresource_ref, CR.containedIn, resource_ref))