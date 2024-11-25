"""Test document"""

import json

from rdflib import SKOS, XSD, Literal
from rdflib.namespace import Namespace

from ckanext.dcat.profiles.base import URIRefOrLiteral
from ckanext.dcat.profiles.euro_dcat_ap_3 import EuropeanDCATAP3Profile

HEALTHDCATAP = Namespace("http://healthdataportal.eu/ns/health#")


class EuropeanHealthDCATAPProfile(EuropeanDCATAP3Profile):
    """
    A profile implementing HealthDCAT-AP, a health-related extension of the DCAT application profile
    for sharing information about Catalogues containing Datasets and Data Services descriptions in Europe.
    """

    def parse_dataset(self, dataset_dict, dataset_ref):
        # Call super method for DCAT-AP 3 properties
        dataset_dict = super(EuropeanHealthDCATAPProfile, self).parse_dataset(
            dataset_dict, dataset_ref
        )

        dataset_dict = self._parse_mandatory_fields(dataset_dict, dataset_ref)

        return dataset_dict

    def _parse_mandatory_fields(self, dataset_dict, dataset_ref):

        #  Lists for "purpose" and "health theme"
        for (
            key,
            predicate,
        ) in (
            ("purpose", HEALTHDCATAP.purpose),
            ("health_theme", HEALTHDCATAP.healthTheme),
        ):
            values = self._object_value_list(dataset_ref, predicate)
            if values:
                dataset_dict[key].append(json.dumps(values))

        # Find number of records
        number_of_records = self._object_value_int(
            dataset_ref, HEALTHDCATAP.numberOfRecords
        )
        if number_of_records is not None:
            dataset_dict["number_of_records"] = number_of_records

        return dataset_dict

    def graph_from_dataset(self, dataset_dict, dataset_ref):
        super().graph_from_dataset(dataset_dict, dataset_ref)

        g = self.g
        # List items:
        #  - Purpose
        #  - Health theme
        items = [
            ("purpose", HEALTHDCATAP.purpose, None, URIRefOrLiteral),
            (
                "health_theme",
                HEALTHDCATAP.healthTheme,
                None,
                URIRefOrLiteral,
                SKOS.concept,
            ),
        ]
        self._add_list_triples_from_dict(dataset_dict, dataset_ref, items)

        # Number of records
        if dataset_dict.get("number_of_records"):
            try:
                g.add(
                    (
                        dataset_ref,
                        HEALTHDCATAP.numberOfRecords,
                        Literal(
                            dataset_dict["number_of_records"],
                            datatype=XSD.nonNegativeInteger,
                        ),
                    )
                )
            except (ValueError, TypeError):
                g.add(
                    (
                        dataset_ref,
                        HEALTHDCATAP.numberOfRecords,
                        Literal(dataset_dict["number_of_records"]),
                    )
                )

    def graph_from_catalog(self, catalog_dict, catalog_ref):
        super().graph_from_catalog(catalog_dict, catalog_ref)

    def __init__(self):
        return None
