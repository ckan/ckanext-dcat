from rdflib import Literal, BNode

from ckanext.dcat.profiles import (
    DCAT,
    XSD,
    SKOS,
    ADMS,
    RDF,
)

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
