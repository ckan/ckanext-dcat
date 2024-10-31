import json
from decimal import DecimalException

from rdflib import Literal, BNode, URIRef

from ckanext.dcat.profiles import (
    CNT,
    DCAT,
    DCATUS,
    DCT,
    FOAF,
    RDF,
    RDFS,
    SKOS,
    XSD,
)
from ckanext.dcat.utils import resource_uri

from .base import URIRefOrLiteral, CleanedURIRef, ORG
from .euro_dcat_ap_3 import EuropeanDCATAP3Profile


class DCATUS3Profile(EuropeanDCATAP3Profile):
    """
    An RDF profile based on the DCAT-US 3 for data portals in the US
    """

    def parse_dataset(self, dataset_dict, dataset_ref):

        # Call base method for common properties
        dataset_dict = self._parse_dataset_base(dataset_dict, dataset_ref)

        # DCAT AP v2 properties also applied to higher versions
        dataset_dict = self._parse_dataset_v2(dataset_dict, dataset_ref)

        # DCAT AP v2 scheming fields
        dataset_dict = self._parse_dataset_v2_scheming(dataset_dict, dataset_ref)

        # DCAT US v3 properties also applied to higher versions
        self._parse_dataset_v3_us(dataset_dict, dataset_ref)

        return dataset_dict

    def graph_from_dataset(self, dataset_dict, dataset_ref):

        # Call base method for common properties
        self._graph_from_dataset_base(dataset_dict, dataset_ref)

        # DCAT AP v2 properties also applied to higher versions
        self._graph_from_dataset_v2(dataset_dict, dataset_ref)

        # DCAT AP v2 scheming fields
        self._graph_from_dataset_v2_scheming(dataset_dict, dataset_ref)

        # DCAT AP v3 properties also applied to higher versions
        self._graph_from_dataset_v3(dataset_dict, dataset_ref)

        # DCAT US v3 properties also applied to higher versions
        self._graph_from_dataset_v3_us(dataset_dict, dataset_ref)

    def graph_from_catalog(self, catalog_dict, catalog_ref):

        self._graph_from_catalog_base(catalog_dict, catalog_ref)

    def _data_dictionary_parse(self, data_dict, subject):

        g = self.g

        for data_dictionary_ref in g.objects(subject, DCATUS.describedBy):
            if isinstance(data_dictionary_ref, Literal):
                data_dict["data_dictionary"] = str(data_dictionary_ref)
            else:
                if not isinstance(data_dict.get("data_dictionary"), list):
                    data_dict["data_dictionary"] = []
                data_dictionary_dict = {}
                for item in [
                    (DCAT.accessURL, "url"),
                    (DCT["format"], "format"),
                    (DCT.license, "license"),
                ]:
                    predicate, key = item
                    value = self._object_value(data_dictionary_ref, predicate)
                    if value:
                        data_dictionary_dict[key] = value
                if data_dictionary_dict:
                    data_dict["data_dictionary"].append(data_dictionary_dict)

        return data_dict

    def _data_dictionary_graph(self, data_dict, subject):
        """
        Adds triples related to the data dictionary property of a Datasets
        or a Distribution

        TODO: Link somehow to the DataStore data dictionary if that exists
        and is public
        """

        g = self.g

        data_dictionary = self._get_dict_value(data_dict, "data_dictionary")
        if isinstance(data_dictionary, str):
            g.add((subject, DCATUS.describedBy, Literal(data_dictionary)))
        elif (
            isinstance(data_dictionary, list)
            and len(data_dictionary)
            and isinstance(data_dictionary[0], dict)
        ):
            data_dictionary = data_dictionary[0]
            url = data_dictionary.get("url")
            if url:
                data_dictionary_ref = BNode()
                g.add((data_dictionary_ref, RDF.type, DCAT.Distribution))
                self._add_triple_from_dict(
                    data_dictionary,
                    data_dictionary_ref,
                    DCAT.accessURL,
                    "url",
                    _type=URIRef,
                    _class=RDFS.Resource,
                )
                if data_dictionary.get("format"):
                    self._add_triple_from_dict(
                        data_dictionary,
                        data_dictionary_ref,
                        DCT["format"],
                        "format",
                        _type=URIRefOrLiteral,
                        _class=DCT.MediaTypeOrExtent,
                    )
                # TODO: fallback to dataset / distribution one
                if data_dictionary.get("license"):
                    self._add_triple_from_dict(
                        data_dictionary,
                        data_dictionary_ref,
                        DCT.license,
                        "license",
                        _type=URIRefOrLiteral,
                        _class=DCT.LicenseDocument,
                    )
                g.add((subject, DCATUS.describedBy, data_dictionary_ref))

    def _parse_dataset_v3_us(self, dataset_dict, dataset_ref):

        g = self.g

        # Bounding box
        for bbox_ref in g.objects(dataset_ref, DCATUS.geographicBoundingBox):
            if not dataset_dict.get("bbox"):
                dataset_dict["bbox"] = []
            dataset_dict["bbox"].append(
                {
                    "west": self._object_value(bbox_ref, DCATUS.westBoundingLongitude),
                    "east": self._object_value(bbox_ref, DCATUS.eastBoundingLongitude),
                    "north": self._object_value(bbox_ref, DCATUS.northBoundingLatitude),
                    "south": self._object_value(bbox_ref, DCATUS.southBoundingLatitude),
                }
            )

        # Data dictionary
        self._data_dictionary_parse(dataset_dict, dataset_ref)

        # Liability statement
        value = self._object_value(dataset_ref, DCATUS.liabilityStatement)
        if value:
            dataset_dict["liability"] = value

        # Contributors
        contributors = self._agents_details(dataset_ref, DCT.contributor)
        if contributors:
            dataset_dict["contributor"] = []
            for contributor in contributors:
                dataset_dict["contributor"].append(contributor)

        # List fields
        for key, predicate in (
            ("purpose", DCATUS.purpose),
            ("usage", SKOS.scopeNote),
        ):
            values = self._object_value_list(dataset_ref, predicate)
            if values:
                dataset_dict[key] = values

        for distribution_ref in self._distributions(dataset_ref):

            for resource_dict in dataset_dict.get("resources", []):
                if resource_dict["distribution_ref"] == str(distribution_ref):

                    # Distribution identifier
                    value = self._object_value(distribution_ref, DCT.identifier)
                    if value:
                        resource_dict["identifier"] = value

                    # Temporal resolution
                    value = self._object_value(
                        distribution_ref, DCAT.temporalResolution
                    )
                    if value:
                        resource_dict["temporal_resolution"] = value

                    # Character encoding
                    value = self._object_value(
                        distribution_ref, CNT.characterEncoding
                    )
                    if value:
                        resource_dict["character_encoding"] = value

                    # Data dictionary
                    self._data_dictionary_parse(resource_dict, distribution_ref)

    def _graph_from_dataset_v3_us(self, dataset_dict, dataset_ref):

        g = self.g

        # Remove foaf:Document class from landing page and documentation if there
        # is no title defined for them
        # See Usage note in https://doi-do.github.io/dcat-us/#properties-for-document
        for page_ref in g.objects(dataset_ref, DCAT.landingPage):
            if not len([t for t in g.triples((page_ref, DCT.title, None))]):
                g.remove((page_ref, RDF.type, None))
        for doc_ref in g.objects(dataset_ref, FOAF.page):
            if not len([t for t in g.triples((page_ref, DCT.title, None))]):
                g.remove((doc_ref, RDF.type, None))

        for publisher_ref in g.objects(dataset_ref, DCT.publisher):

            # Use org:Organization instead of foaf:Agent
            g.remove((publisher_ref, RDF.type, None))
            g.add((publisher_ref, RDF.type, ORG.Organization))

            # Add skos:prefLabel
            name = self._object_value(publisher_ref, FOAF.name)
            if name:
                g.add((publisher_ref, SKOS.prefLabel, Literal(name)))

        # Bounding box
        # TODO: we could fall back to spatial or spatial_coverage's bbox/geom
        bboxes = self._get_dataset_value(dataset_dict, "bbox")
        if bboxes:
            for bbox in bboxes:
                bbox_ref = BNode()
                g.add((dataset_ref, DCATUS.geographicBoundingBox, bbox_ref))
                g.add((bbox_ref, RDF.type, DCATUS.geographicBoundingBox))

                def add_bounding(predicate, value):
                    try:
                        g.add(
                            (
                                bbox_ref,
                                predicate,
                                Literal(value, datatype=XSD.decimal),
                            )
                        )
                    except (ValueError, TypeError, DecimalException):
                        g.add((bbox_ref, predicate, Literal(value)))

                for item in (
                    (DCATUS.westBoundingLongitude, bbox["west"]),
                    (DCATUS.eastBoundingLongitude, bbox["east"]),
                    (DCATUS.northBoundingLatitude, bbox["north"]),
                    (DCATUS.southBoundingLatitude, bbox["south"]),
                ):
                    add_bounding(item[0], item[1])

        # Data dictionary
        self._data_dictionary_graph(dataset_dict, dataset_ref)

        # Liability statement
        self._add_statement_to_graph(
            dataset_dict,
            "liability",
            dataset_ref,
            DCATUS.liabilityStatement,
            DCATUS.LiabilityStatement,
        )

        # Contributor
        self._add_agents(dataset_ref, dataset_dict, "contributor", DCT.contributor)

        #  Lists
        items = [
            ("purpose", DCATUS.purpose, None, Literal),
            ("usage", SKOS.scopeNote, None, Literal),
        ]
        self._add_list_triples_from_dict(dataset_dict, dataset_ref, items)

        for resource_dict in dataset_dict.get("resources", []):

            distribution_ref = CleanedURIRef(resource_uri(resource_dict))

            # Distribution identifier
            self._add_triple_from_dict(
                resource_dict,
                distribution_ref,
                DCT.identifier,
                "identifier",
                fallbacks=["guid", "id"],
                _type=URIRefOrLiteral,
            )

            # Data dictionary
            self._data_dictionary_graph(resource_dict, distribution_ref)

            # Character encoding
            self._add_triple_from_dict(
                resource_dict,
                distribution_ref,
                CNT.characterEncoding,
                "character_encoding",
                _type=Literal,
            )
