from rdflib import XSD, Literal, URIRef
from rdflib.namespace import Namespace

from ckanext.dcat.profiles.base import URIRefOrLiteral
from ckanext.dcat.profiles.euro_dcat_ap_3 import EuropeanDCATAP3Profile

# HealthDCAT-AP namespace. Note: not finalized yet
HEALTHDCATAP = Namespace("http://healthdataportal.eu/ns/health#")

# Data Privacy Vocabulary namespace
DPV = Namespace("https://w3id.org/dpv#")

namespaces = {
    "healthdcatap": HEALTHDCATAP,
    "dpv": DPV,
}


class EuropeanHealthDCATAPProfile(EuropeanDCATAP3Profile):
    """
    A profile implementing HealthDCAT-AP, a health-related extension of the DCAT
    application profile for sharing information about Catalogues containing Datasets
    and Data Services descriptions in Europe.
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
        self.__parse_healthdcat_booleanvalues(dataset_dict, dataset_ref)
        self.__parse_healthdcat_intvalues(dataset_dict, dataset_ref)

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
        for (key, predicate,) in (
            ("analytics", HEALTHDCATAP.analytics),
            ("code_values", HEALTHDCATAP.hasCodeValues),
            ("coding_system", HEALTHDCATAP.hasCodingSystem),
            ("health_category", HEALTHDCATAP.healthCategory),
            ("health_theme", HEALTHDCATAP.healthTheme),
            ("legal_basis", DPV.hasLegalBasis),
            ("personal_data", DPV.hasPersonalData),
            ("population_coverage", HEALTHDCATAP.populationCoverage),
            ("publisher_note", HEALTHDCATAP.publisherNote),
            ("publisher_type", HEALTHDCATAP.publisherType),
            ("purpose", DPV.hasPurpose),
        ):
            values = self._object_value_list(dataset_ref, predicate)
            if values:
                dataset_dict[key] = values

    def graph_from_dataset(self, dataset_dict, dataset_ref):
        super().graph_from_dataset(dataset_dict, dataset_ref)
        for prefix, namespace in namespaces.items():
            self.g.bind(prefix, namespace)

        # key, predicate, fallbacks, _type, _class
        items = [
            ("analytics", HEALTHDCATAP.analytics, None, URIRefOrLiteral),
            ("code_values", HEALTHDCATAP.hasCodeValues, None, URIRefOrLiteral),
            ("coding_system", HEALTHDCATAP.hasCodingSystem, None, URIRefOrLiteral),
            ("health_category", HEALTHDCATAP.healthCategory, None, URIRefOrLiteral),
            ("health_theme", HEALTHDCATAP.healthCategory, None, URIRefOrLiteral),
            ("legal_basis", DPV.hasLegalBasis, None, URIRefOrLiteral),
            (
                "population_coverage",
                HEALTHDCATAP.populationCoverage,
                None,
                URIRefOrLiteral,
            ),
            ("personal_data", DPV.hasPersonalData, None, URIRef),
            ("publisher_note", HEALTHDCATAP.publisherNote, None, URIRefOrLiteral),
            ("publisher_type", HEALTHDCATAP.publisherType, None, URIRefOrLiteral),
            ("purpose", DPV.hasPurpose, None, URIRefOrLiteral),
        ]
        self._add_list_triples_from_dict(dataset_dict, dataset_ref, items)

        if "trusted_data_holder" in dataset_dict:
            self.g.add(
                (
                    dataset_ref,
                    HEALTHDCATAP.trustedDataHolder,
                    Literal(bool(dataset_dict["trusted_data_holder"]), datatype=XSD.boolean),
                )
            )

        items = [
            ("min_typical_age", HEALTHDCATAP.minTypicalAge),
            ("max_typical_age", HEALTHDCATAP.maxTypicalAge),
            ("number_of_records", HEALTHDCATAP.numberOfRecords),
            ("number_of_unique_individuals", HEALTHDCATAP.numberOfUniqueIndividuals),
        ]
        for key, predicate in items:
            self._add_nonneg_integer_triple(dataset_dict, dataset_ref, key, predicate)

        self._add_agents(dataset_ref, dataset_dict, "hdab", HEALTHDCATAP.hdab)

    def _add_nonneg_integer_triple(self, dataset_dict, dataset_ref, key, predicate):
        """
        Adds non-negative integers to the Dataset graph (xsd:nonNegativeInteger)

        dataset_ref: subject of Graph
        key: scheming key in CKAN
        predicate: predicate to use
        """
        value = self._get_dict_value(dataset_dict, key)

        if value:
            try:
                if int(value) < 0:
                    raise ValueError("Not a non-negative integer")
                self.g.add(
                    (
                        dataset_ref,
                        predicate,
                        Literal(int(value), datatype=XSD.nonNegativeInteger),
                    )
                )
            except (ValueError, TypeError):
                self.g.add((dataset_ref, predicate, Literal(value)))
                
    def __parse_healthdcat_booleanvalues(self, dataset_dict, dataset_ref):
        for key, predicate in (
            ("trusted_data_holder", HEALTHDCATAP.trustedDataHolder),
        ):
            value = self._object_value(dataset_ref, predicate)
            if value is not None:
                dataset_dict[key] = value.lower() == "true"

    def graph_from_catalog(self, catalog_dict, catalog_ref):
        super().graph_from_catalog(catalog_dict, catalog_ref)
