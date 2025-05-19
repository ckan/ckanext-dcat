from rdflib import Literal, BNode, URIRef

from ckanext.dcat.profiles import (
    DCAT,
    XSD,
    SKOS,
    ADMS,
    RDF,
)

from ckanext.dcat.utils import dataset_uri
from .euro_dcat_ap_2 import EuropeanDCATAP2Profile
from .euro_dcat_ap_scheming import EuropeanDCATAPSchemingProfile


class EuropeanDCATAP3Profile(EuropeanDCATAP2Profile, EuropeanDCATAPSchemingProfile):
    """
    An RDF profile based on the DCAT-AP 3 for data portals in Europe
    """

    def parse_dataset(self, dataset_dict, dataset_ref):

        # Call base method for common properties
        dataset_dict = self._parse_dataset_base(dataset_dict, dataset_ref)

        # DCAT AP v2 properties also applied to higher versions
        dataset_dict = self._parse_dataset_v2(dataset_dict, dataset_ref)

        # DCAT AP v2 scheming fields
        dataset_dict = self._parse_dataset_v2_scheming(dataset_dict, dataset_ref)

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

    def graph_from_catalog(self, catalog_dict, catalog_ref):

        self._graph_from_catalog_base(catalog_dict, catalog_ref)

    def _graph_from_dataset_v3(self, dataset_dict, dataset_ref):

        dataset_series = False

        # TODO: support custom type names (ckan/ckanext-dataset-series#6)
        if dataset_dict.get("type") == "dataset_series":
            dataset_series = True
            self.g.remove((dataset_ref, RDF.type, None))
            self.g.add((dataset_ref, RDF.type, DCAT.DatasetSeries))

        # byteSize decimal -> nonNegativeInteger
        for subject, predicate, object in self.g.triples((None, DCAT.byteSize, None)):
            if object and object.datatype == XSD.decimal:
                self.g.remove((subject, predicate, object))

                self.g.add(
                    (
                        subject,
                        predicate,
                        Literal(int(object), datatype=XSD.nonNegativeInteger),
                    )
                )

        # Other identifiers
        value = self._get_dict_value(dataset_dict, "alternate_identifier")
        if value:
            items = self._read_list_value(value)
            for item in items:
                identifier = BNode()
                self.g.add((dataset_ref, ADMS.identifier, identifier))
                self.g.add((identifier, RDF.type, ADMS.Identifier))
                self.g.add((identifier, SKOS.notation, Literal(item)))

        # Dataset Series
        if dataset_series and dataset_dict.get("series_navigation"):

            if dataset_dict["series_navigation"].get("first"):
                self.g.add(
                    (
                        dataset_ref,
                        DCAT.first,
                        URIRef(dataset_uri(dataset_dict["series_navigation"]["first"])),
                    )
                )
            if dataset_dict["series_navigation"].get("last"):
                self.g.add(
                    (
                        dataset_ref,
                        DCAT.last,
                        URIRef(dataset_uri(dataset_dict["series_navigation"]["last"])),
                    )
                )
        elif dataset_dict.get("in_series"):
            for series_id in dataset_dict["in_series"]:
                # TODO: dataset type?
                self.g.add(
                    (dataset_ref, DCAT.inSeries, URIRef(dataset_uri({"id": series_id})))
                )
                for series_nav in dataset_dict.get("series_navigation", []):
                    if series_nav["id"] == series_id:
                        if series_nav.get("previous"):
                            self.g.add(
                                (
                                    dataset_ref,
                                    DCAT.prev,
                                    URIRef(dataset_uri(series_nav["previous"])),
                                )
                            )
                        if series_nav.get("next"):
                            self.g.add(
                                (
                                    dataset_ref,
                                    DCAT.next,
                                    URIRef(dataset_uri(series_nav["next"])),
                                )
                            )
