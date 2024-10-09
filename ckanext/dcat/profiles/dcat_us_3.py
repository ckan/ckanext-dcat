from decimal import Decimal, DecimalException

from rdflib import Literal, BNode

from ckanext.dcat.profiles import (
    DCAT,
    DCATUS,
    DCT,
    FOAF,
    RDF,
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

        for distribution_ref in self._distributions(dataset_ref):

            # Distribution identifier
            value = self._object_value(distribution_ref, DCT.identifier)
            if value:
                for resource_dict in dataset_dict.get("resources", []):
                    if resource_dict["distribution_ref"] == str(distribution_ref):
                        resource_dict["identifier"] = value

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
