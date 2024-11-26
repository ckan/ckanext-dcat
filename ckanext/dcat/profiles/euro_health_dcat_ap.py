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

        dataset_dict = self._parse_health_fields(dataset_dict, dataset_ref)

        return dataset_dict

    def _parse_health_fields(self, dataset_dict, dataset_ref):
        for (
            key,
            predicate,
        ) in (
            # ("purpose", HEALTHDCATAP.purpose),
            ("health_category", HEALTHDCATAP.healthCategory),
            ("health_theme", HEALTHDCATAP.healthTheme),
        ):
            values = self._object_value_list(dataset_ref, predicate)
            if values:
                dataset_dict[key] = values

        for key, predicate in (
            ("min_typical_age", HEALTHDCATAP.minTypicalAge),
            ("max_typical_age", HEALTHDCATAP.maxTypicalAge),
            ("number_of_records", HEALTHDCATAP.numberOfRecords),
        ):
            value = self._object_value_int(dataset_ref, predicate)
            # a zero value evaluates as False but is definitely not a None
            if value is not None:
                dataset_dict[key] = value

        # Purpose is a dpv:Purpose, inside is a dct:Description

        # Add the HDAB. There should only ever be one but you never know
        agents = self._agents_details(dataset_ref, HEALTHDCATAP.hdab)
        if agents:
            dataset_dict["hdab"] = agents

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
