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
        self.__parse_healthdcat_stringvalues(dataset_dict, dataset_ref)

        self.__parse_healthdcat_intvalues(dataset_dict, dataset_ref)

        # Purpose is a dpv:Purpose, inside is a dct:Description
        pass

        # Add the HDAB. There should only ever be one but you never know
        agents = self._agents_details(dataset_ref, HEALTHDCATAP.hdab)
        if agents:
            dataset_dict["hdab"] = agents

        # Retention period
        retention_start, retention_end = self._time_interval(
            dataset_ref, HEALTHDCATAP.retentionPeriod, dcat_ap_version=2
        )
        retention_dict = {}
        if retention_start is not None:
            retention_dict["start"] = retention_start
        if retention_end is not None:
            retention_dict["end"] = retention_end
        if retention_dict:
            dataset_dict["retention_period"] = [retention_dict]

        return dataset_dict

    def __parse_healthdcat_intvalues(self, dataset_dict, dataset_ref):
        for key, predicate in (
            ("min_typical_age", HEALTHDCATAP.minTypicalAge),
            ("max_typical_age", HEALTHDCATAP.maxTypicalAge),
            ("number_of_records", HEALTHDCATAP.numberOfRecords),
            ("number_of_unique_individuals", HEALTHDCATAP.numberOfUniqueIndividuals),
        ):
            value = self._object_value_int(dataset_ref, predicate)
            # A zero value evaluates as False but is definitely not a None
            if value is not None:
                dataset_dict[key] = value

    def __parse_healthdcat_stringvalues(self, dataset_dict, dataset_ref):
        for (
            key,
            predicate,
        ) in (
            # ("purpose", HEALTHDCATAP.purpose),
            ("health_category", HEALTHDCATAP.healthCategory),
            ("health_theme", HEALTHDCATAP.healthTheme),
            ("population_coverage", HEALTHDCATAP.populationCoverage),
            ("publisher_note", HEALTHDCATAP.publisherNote),
        ):
            values = self._object_value_list(dataset_ref, predicate)
            if values:
                dataset_dict[key] = values

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
