from ckanext.dcat.profiles import (
    DCT,
)
from ckanext.dcat.utils import resource_uri

from .base import URIRefOrLiteral, CleanedURIRef
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

        for distribution_ref in self._distributions(dataset_ref):

            # Distribution identifier
            value = self._object_value(distribution_ref, DCT.identifier)
            if value:
                for resource_dict in dataset_dict.get("resources", []):
                    if resource_dict["distribution_ref"] == str(distribution_ref):
                        resource_dict["identifier"] = value

    def _graph_from_dataset_v3_us(self, dataset_dict, dataset_ref):

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
