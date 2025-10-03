from rdflib import XSD, Literal, URIRef, RDF, BNode, DCAT, RDFS
from rdflib.namespace import Namespace
from rdflib.namespace import DCTERMS as DCT
from .base import CleanedURIRef
from ckanext.dcat.utils import resource_uri
from ckanext.dcat.profiles.base import URIRefOrLiteral
from ckanext.dcat.profiles.euro_dcat_ap_3 import EuropeanDCATAP3Profile

# HealthDCAT-AP namespace. Note: not finalized yet
HEALTHDCATAP = Namespace("http://healthdataportal.eu/ns/health#")

# Data Privacy Vocabulary namespace
DPV = Namespace("https://w3id.org/dpv#")

# Data Quality Vocabulary namespace
DQV = Namespace("http://www.w3.org/ns/dqv#")

# Open Annotation namespace
OA = Namespace("http://www.w3.org/ns/oa#")

namespaces = {
    "healthdcatap": HEALTHDCATAP,
    "dpv": DPV,
}

# HealthDCAT-AP fields that can contain language-tagged literals
MULTILINGUAL_LITERAL_FIELDS = {
    "population_coverage": HEALTHDCATAP.populationCoverage,
    "publisher_note": HEALTHDCATAP.publisherNote,
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
        multilingual_fields = set(self._multilingual_dataset_fields())

        self.__parse_healthdcat_stringvalues(
            dataset_dict, dataset_ref, multilingual_fields
        )
        self.__parse_healthdcat_booleanvalues(dataset_dict, dataset_ref)
        self.__parse_healthdcat_intvalues(dataset_dict, dataset_ref)

        # Add the HDAB. There should only ever be one but you never know
        agents = self._agents_details(dataset_ref, HEALTHDCATAP.hdab)
        if agents:
            dataset_dict["hdab"] = agents
        # Add the quality annotations            
        quality_annotations = self._parse_quality_annotation(dataset_ref)
        if quality_annotations:
            dataset_dict["quality_annotation"] = quality_annotations
            
        # Dataset-level retention
        dataset_dict["retention_period"] = self._parse_retention_period(dataset_ref)

        # Distribution-level retention
        for distribution_ref in self._distributions(dataset_ref):
            for resource_dict in dataset_dict.get("resources", []):
                if resource_dict["distribution_ref"] == str(distribution_ref):
                    resource_dict["retention_period"] = self._parse_retention_period(distribution_ref)

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

    def __parse_healthdcat_stringvalues(
        self, dataset_dict, dataset_ref, multilingual_fields
    ):
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
            if (
                key in MULTILINGUAL_LITERAL_FIELDS
                and key in multilingual_fields
            ):
                value = self._object_value(
                    dataset_ref, predicate, multilingual=True
                )
            else:
                value = self._object_value_list(dataset_ref, predicate)

            if value:
                dataset_dict[key] = value

    def __parse_healthdcat_booleanvalues(self, dataset_dict, dataset_ref):
        for key, predicate in (
            ("trusted_data_holder", HEALTHDCATAP.trustedDataHolder),
        ):
            value = self._object_value(dataset_ref, predicate)
            if value is not None:
                lowered = value.lower()
                if lowered in ("true", "false"):
                    dataset_dict[key] = lowered == "true"
                    
    def _parse_quality_annotation(self, dataset_ref):
        """
        Parse DQV quality annotations from the RDF graph.

        Returns a list of quality annotation dictionaries.
        Only includes annotations where body and target are valid URIs.
        """
        quality_annotation = []

        # Find all quality annotations for this dataset
        for annotation_ref in self.g.objects(dataset_ref, DQV.hasQualityAnnotation):
            annotation_dict = {}

            # Get the body (must be a URI)
            body = self._object_value(annotation_ref, OA.hasBody)
            if body and isinstance(body, str) and body.startswith(("http://", "https://")):
                annotation_dict["body"] = body

            # Get the target (must be a URI)
            target = self._object_value(annotation_ref, OA.hasTarget)
            if target and isinstance(target, str) and target.startswith(("http://", "https://")):
                annotation_dict["target"] = target

            # Only include the annotation if both body and target are valid URIs
            if "body" not in annotation_dict or "target" not in annotation_dict:
                continue

            # Get the motivation (URI or literal)
            motivation = self._object_value(annotation_ref, OA.motivatedBy)
            if motivation:
                annotation_dict["motivated_by"] = motivation

            quality_annotation.append(annotation_dict)

        return quality_annotation

    def _parse_retention_period(self, subject_ref):
        """
        Parses the HEALTHDCATAP.retentionPeriod from the RDF graph for a given subject
        (e.g., dataset or distribution).

        Returns a list with a single dict, e.g.,
        [{"start": "2023-01-01", "end": "2025-01-01"}]
        or an empty list if no values are found.
        """
        retention_start, retention_end = self._time_interval(
            subject_ref, HEALTHDCATAP.retentionPeriod, dcat_ap_version=2
        )
        retention_dict = {}
        if retention_start is not None:
            retention_dict["start"] = retention_start
        if retention_end is not None:
            retention_dict["end"] = retention_end

        return [retention_dict] if retention_dict else []


    def graph_from_dataset(self, dataset_dict, dataset_ref):
        super().graph_from_dataset(dataset_dict, dataset_ref)
        for prefix, namespace in namespaces.items():
            self.g.bind(prefix, namespace)

        # key, predicate, fallbacks, _type, _class
        list_items = [
            ("analytics", HEALTHDCATAP.analytics, None, URIRefOrLiteral),
            ("code_values", HEALTHDCATAP.hasCodeValues, None, URIRefOrLiteral),
            ("coding_system", HEALTHDCATAP.hasCodingSystem, None, URIRefOrLiteral),
            ("health_category", HEALTHDCATAP.healthCategory, None, URIRefOrLiteral),
            ("health_theme", HEALTHDCATAP.healthCategory, None, URIRefOrLiteral),
            ("legal_basis", DPV.hasLegalBasis, None, URIRefOrLiteral),
            ("personal_data", DPV.hasPersonalData, None, URIRef),
            ("publisher_type", HEALTHDCATAP.publisherType, None, URIRefOrLiteral),
            ("purpose", DPV.hasPurpose, None, URIRefOrLiteral),
        ]
        self._add_list_triples_from_dict(dataset_dict, dataset_ref, list_items)

        multilingual_fields = set(self._multilingual_dataset_fields())
        for key, predicate in MULTILINGUAL_LITERAL_FIELDS.items():
            value = self._get_dataset_value(dataset_dict, key)
            if not value:
                continue

            if key in multilingual_fields and isinstance(value, dict):
                for lang, translated_value in value.items():
                    if translated_value:
                        self.g.add(
                            (
                                dataset_ref,
                                predicate,
                                Literal(translated_value, lang=lang),
                            )
                        )
                continue

            self._add_triple_from_dict(
                dataset_dict,
                dataset_ref,
                predicate,
                key,
                list_value=True,
                _type=URIRefOrLiteral,
            )

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
        self._add_quality_annotation(dataset_dict, dataset_ref)

        # Dataset-level retention period
        self._add_retention_period(dataset_ref, dataset_dict.get("retention_period", []))

        for resource_dict in dataset_dict.get("resources", []):
            distribution_ref = CleanedURIRef(resource_uri(resource_dict))
            self._add_retention_period(distribution_ref, resource_dict.get("retention_period", []))

    def _add_retention_period(self, subject_ref, retention_list):
        for retention in retention_list:
            start = retention.get("start")
            end = retention.get("end")
            comment = retention.get("comment")

            if start or end or comment:
                period_node = BNode()
                self.g.add((subject_ref, HEALTHDCATAP.retentionPeriod, period_node))
                self.g.add((period_node, RDF.type, DCT.PeriodOfTime))

                if start:
                    self.g.add((period_node, DCAT.startDate, Literal(start, datatype=XSD.date)))
                if end:
                    self.g.add((period_node, DCAT.endDate, Literal(end, datatype=XSD.date)))
                if comment:
                    self.g.add((period_node, RDFS.comment, Literal(comment, lang="en")))

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

    def _add_quality_annotation(self, dataset_dict, dataset_ref):
        """
        Serialize qualified_annotation entries into RDF as DQV.QualityAnnotations.
        Only URI-based body, target, and motivation values are supported.
        """
        quality_annotation = self._get_dict_value(dataset_dict, "quality_annotation")

        if not quality_annotation:
            return

        for annotation in quality_annotation:
            if not isinstance(annotation, dict):
                continue

            annotation_ref = BNode()

            # Link from dataset
            self.g.add((dataset_ref, DQV.hasQualityAnnotation, annotation_ref))
            self.g.add((annotation_ref, RDF.type, OA.Annotation))

            # URI-based fields only
            for field, predicate in [
                ("body", OA.hasBody),
                ("target", OA.hasTarget),
                ("motivated_by", OA.motivatedBy),
            ]:
                uri = annotation.get(field)
                if isinstance(uri, str) and uri.startswith(("http://", "https://")):
                    self.g.add((annotation_ref, predicate, URIRef(uri)))


    def graph_from_catalog(self, catalog_dict, catalog_ref):
        super().graph_from_catalog(catalog_dict, catalog_ref)
