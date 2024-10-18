import json
import pytest

from rdflib.namespace import RDF
from rdflib.term import URIRef
from geomet import wkt

from ckan.tests.helpers import call_action
from ckanext.dcat.processors import RDFSerializer
from ckanext.dcat.tests.utils import BaseSerializeTest

from ckanext.dcat import utils
from ckanext.dcat.profiles import (
    CNT,
    DCAT,
    DCATUS,
    DCT,
    ADMS,
    XSD,
    VCARD,
    FOAF,
    SKOS,
    LOCN,
    GSP,
    OWL,
    SPDX,
    RDFS,
)


@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.plugins", "dcat scheming_datasets")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas", "ckanext.dcat.schemas:dcat_us_full.yaml"
)
@pytest.mark.ckan_config(
    "scheming.presets",
    "ckanext.scheming:presets.json ckanext.dcat.schemas:presets.yaml",
)
@pytest.mark.ckan_config("ckanext.dcat.rdf.profiles", "dcat_us_3")
class TestDCATUS3ProfileSerializeDataset(BaseSerializeTest):
    def test_e2e_ckan_to_dcat(self):
        """
        Create a dataset using the scheming schema, check that fields
        are exposed in the DCAT RDF graph
        """

        dataset_dict = json.loads(
            self._get_file_contents("ckan/ckan_full_dataset_dcat_us_vocabularies.json")
        )

        dataset = call_action("package_create", **dataset_dict)

        # Make sure schema was used
        assert (
            dataset["conforms_to"][0]
            == "https://resources.data.gov/vocab/TODO/ProtocolValue/DCAT_US_3_0"
        )
        assert dataset["contact"][0]["name"] == "Contact 1"

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        assert str(dataset_ref) == utils.dataset_uri(dataset)

        # Core fields
        assert self._triple(g, dataset_ref, RDF.type, DCAT.Dataset)
        assert self._triple(g, dataset_ref, DCT.title, dataset["title"])
        assert self._triple(g, dataset_ref, DCT.description, dataset["notes"])
        assert self._triple(g, dataset_ref, OWL.versionInfo, dataset["version"])

        # Standard fields
        assert self._triple(g, dataset_ref, DCT.identifier, dataset["identifier"])
        assert self._triple(
            g, dataset_ref, DCT.accrualPeriodicity, URIRef(dataset["frequency"])
        )
        assert self._triple(
            g, dataset_ref, DCT.provenance, URIRef(dataset["provenance"])
        )
        assert self._triple(g, dataset_ref, DCT.type, URIRef(dataset["dcat_type"]))
        assert self._triple(g, dataset_ref, ADMS.versionNotes, dataset["version_notes"])
        assert self._triple(
            g, dataset_ref, DCT.accessRights, URIRef(dataset["access_rights"])
        )
        assert self._triple(
            g,
            dataset_ref,
            DCAT.spatialResolutionInMeters,
            dataset["spatial_resolution_in_meters"],
            data_type=XSD.decimal,
        )

        # Dates
        assert self._triple(
            g,
            dataset_ref,
            DCT.issued,
            dataset["issued"],
            data_type=XSD.date,
        )
        assert self._triple(
            g,
            dataset_ref,
            DCT.modified,
            dataset["modified"],
            data_type=XSD.date,
        )
        assert self._triple(
            g,
            dataset_ref,
            DCAT.temporalResolution,
            dataset["temporal_resolution"],
            data_type=XSD.duration,
        )

        # List fields

        assert (
            self._triples_list_values(g, dataset_ref, DCT.conformsTo)
            == dataset["conforms_to"]
        )
        assert self._triples_list_values(g, dataset_ref, DCAT.theme) == dataset["theme"]
        assert (
            self._triples_list_values(g, dataset_ref, DCT.language)
            == dataset["language"]
        )
        assert (
            self._triples_list_values(g, dataset_ref, FOAF.page)
            == dataset["documentation"]
        )
        assert (
            self._triples_list_values(g, dataset_ref, DCT.isReferencedBy)
            == dataset["is_referenced_by"]
        )
        assert (
            self._triples_list_values(g, dataset_ref, DCATUS.purpose)
            == dataset["purpose"]
        )
        assert (
            self._triples_list_values(g, dataset_ref, SKOS.scopeNote)
            == dataset["usage"]
        )

        # Repeating subfields

        contact_details = [t for t in g.triples((dataset_ref, DCAT.contactPoint, None))]

        assert len(contact_details) == len(dataset["contact"])
        assert self._triple(
            g, contact_details[0][2], VCARD.fn, dataset_dict["contact"][0]["name"]
        )
        assert self._triple(
            g,
            contact_details[0][2],
            VCARD.hasEmail,
            URIRef("mailto:" + dataset_dict["contact"][0]["email"]),
        )
        assert self._triple(
            g, contact_details[1][2], VCARD.fn, dataset_dict["contact"][1]["name"]
        )
        assert self._triple(
            g,
            contact_details[1][2],
            VCARD.hasEmail,
            URIRef("mailto:" + dataset_dict["contact"][1]["email"]),
        )

        publisher = [t for t in g.triples((dataset_ref, DCT.publisher, None))]

        assert len(publisher) == 1
        assert self._triple(
            g, publisher[0][2], FOAF.name, dataset_dict["publisher"][0]["name"]
        )
        assert self._triple(
            g,
            publisher[0][2],
            VCARD.hasEmail,
            URIRef("mailto:" + dataset_dict["publisher"][0]["email"]),
        )
        assert self._triple(
            g,
            publisher[0][2],
            FOAF.homepage,
            URIRef(dataset_dict["publisher"][0]["url"]),
        )

        contributor = [t for t in g.triples((dataset_ref, DCT.contributor, None))]

        assert len(contributor) == 2
        assert self._triple(
            g, contributor[0][2], FOAF.name, dataset_dict["contributor"][0]["name"]
        )
        assert self._triple(
            g,
            contributor[0][2],
            VCARD.hasEmail,
            URIRef("mailto:" + dataset_dict["contributor"][0]["email"]),
        )
        assert self._triple(
            g,
            contributor[0][2],
            FOAF.homepage,
            URIRef(dataset_dict["contributor"][0]["url"]),
        )
        assert self._triple(
            g, contributor[1][2], FOAF.name, dataset_dict["contributor"][1]["name"]
        )
        assert self._triple(
            g,
            contributor[1][2],
            VCARD.hasEmail,
            URIRef("mailto:" + dataset_dict["contributor"][1]["email"]),
        )
        assert self._triple(
            g,
            contributor[1][2],
            FOAF.homepage,
            URIRef(dataset_dict["contributor"][1]["url"]),
        )

        temporal = [t for t in g.triples((dataset_ref, DCT.temporal, None))]

        assert len(temporal) == len(dataset["temporal_coverage"])
        assert self._triple(
            g,
            temporal[0][2],
            DCAT.startDate,
            dataset_dict["temporal_coverage"][0]["start"],
            data_type=XSD.date,
        )
        assert self._triple(
            g,
            temporal[0][2],
            DCAT.endDate,
            dataset_dict["temporal_coverage"][0]["end"],
            data_type=XSD.date,
        )
        assert self._triple(
            g,
            temporal[1][2],
            DCAT.startDate,
            dataset_dict["temporal_coverage"][1]["start"],
            data_type=XSD.date,
        )
        assert self._triple(
            g,
            temporal[1][2],
            DCAT.endDate,
            dataset_dict["temporal_coverage"][1]["end"],
            data_type=XSD.date,
        )

        spatial = [t for t in g.triples((dataset_ref, DCT.spatial, None))]
        assert len(spatial) == len(dataset["spatial_coverage"])
        assert str(spatial[0][2]) == dataset["spatial_coverage"][0]["uri"]
        assert self._triple(g, spatial[0][2], RDF.type, DCT.Location)
        assert self._triple(
            g, spatial[0][2], SKOS.prefLabel, dataset["spatial_coverage"][0]["text"]
        )

        assert len([t for t in g.triples((spatial[0][2], LOCN.Geometry, None))]) == 1
        # Geometry in WKT
        wkt_geom = wkt.dumps(dataset["spatial_coverage"][0]["geom"], decimals=4)
        assert self._triple(g, spatial[0][2], LOCN.Geometry, wkt_geom, GSP.wktLiteral)

        # Alternate identifiers
        ids = []
        for subject in [t[2] for t in g.triples((dataset_ref, ADMS.identifier, None))]:
            ids.append(str(g.value(subject, SKOS.notation)))
        assert ids == dataset["alternate_identifier"]

        # Liability statement
        statement = [s for s in g.objects(dataset_ref, DCATUS.liabilityStatement)][0]
        assert self._triple(g, statement, RDFS.label, dataset["liability"])

        # Resources

        distribution_ref = self._triple(g, dataset_ref, DCAT.distribution, None)[2]
        resource = dataset_dict["resources"][0]

        # Resources: core fields

        assert self._triple(g, distribution_ref, DCT.title, resource["name"])
        assert self._triple(
            g,
            distribution_ref,
            DCT.description,
            resource["description"],
        )

        # Resources: standard fields

        assert self._triple(
            g, distribution_ref, ADMS.status, URIRef(resource["status"])
        )
        assert self._triple(
            g,
            distribution_ref,
            DCAT.accessURL,
            URIRef(resource["access_url"]),
        )
        assert self._triple(
            g,
            distribution_ref,
            DCAT.compressFormat,
            URIRef(resource["compress_format"]),
        )
        assert self._triple(
            g,
            distribution_ref,
            DCAT.packageFormat,
            URIRef(resource["package_format"]),
        )
        assert self._triple(
            g,
            distribution_ref,
            DCAT.downloadURL,
            URIRef(resource["download_url"]),
        )
        assert self._triple(
            g,
            distribution_ref,
            DCAT.temporalResolution,
            resource["temporal_resolution"],
            data_type=XSD.duration,
        )
        assert self._triple(
            g,
            distribution_ref,
            DCAT.spatialResolutionInMeters,
            resource["spatial_resolution_in_meters"],
            data_type=XSD.decimal,
        )
        assert self._triple(
            g,
            distribution_ref,
            CNT.characterEncoding,
            resource["character_encoding"],
        )

        assert self._triple(
            g, distribution_ref, DCAT.byteSize, resource["size"], XSD.nonNegativeInteger
        )

        assert self._triple(
            g,
            distribution_ref,
            DCAT.temporalResolution,
            resource["temporal_resolution"],
            data_type=XSD.duration,
        )

        # Checksum
        checksum = self._triple(g, distribution_ref, SPDX.checksum, None)[2]
        assert checksum
        assert self._triple(g, checksum, RDF.type, SPDX.Checksum)
        assert self._triple(
            g,
            checksum,
            SPDX.checksumValue,
            resource["hash"],
            data_type="http://www.w3.org/2001/XMLSchema#hexBinary",
        )
        assert self._triple(
            g, checksum, SPDX.algorithm, URIRef(resource["hash_algorithm"])
        )

        # Resources: dates
        assert self._triple(
            g,
            distribution_ref,
            DCT.issued,
            dataset["resources"][0]["issued"],
            data_type=XSD.dateTime,
        )
        assert self._triple(
            g,
            distribution_ref,
            DCT.modified,
            dataset["resources"][0]["modified"],
            data_type=XSD.dateTime,
        )

        # Resources: list fields
        assert (
            self._triples_list_values(g, distribution_ref, DCT.language)
            == resource["language"]
        )

        # Resources: statements
        statement = [s for s in g.objects(distribution_ref, DCT.rights)][0]
        assert self._triple(g, statement, RDFS.label, resource["rights"])

    def test_distribution_identifier(self):

        dataset_dict = {
            "name": "test-dcat-us",
            "description": "Test",
            "resources": [
                {
                    "id": "89b67e5b-d0e1-4bc3-a75a-59f21c66ebc0",
                    "name": "some data",
                    "identifier": "https://example.org/distributions/1",
                }
            ],
        }

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset_dict)

        distribution_ref = self._triple(g, dataset_ref, DCAT.distribution, None)[2]
        resource = dataset_dict["resources"][0]

        assert self._triple(
            g, distribution_ref, DCT.identifier, URIRef(resource["identifier"])
        )

    def test_distribution_identifier_falls_back_to_id(self):

        dataset_dict = {
            "name": "test-dcat-us",
            "description": "Test",
            "resources": [
                {
                    "id": "89b67e5b-d0e1-4bc3-a75a-59f21c66ebc0",
                    "name": "some data",
                }
            ],
        }

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset_dict)

        distribution_ref = self._triple(g, dataset_ref, DCAT.distribution, None)[2]
        resource = dataset_dict["resources"][0]

        assert self._triple(g, distribution_ref, DCT.identifier, resource["id"])

    def test_bbox(self):
        dataset_dict = {
            "name": "test-dcat-us",
            "description": "Test",
            "bbox": [
                {"west": -179.15, "east": -129.98, "north": 71.54, "south": 51.21}
            ],
        }

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset_dict)

        bbox_ref = [s for s in g.objects(dataset_ref, DCATUS.geographicBoundingBox)][0]
        assert self._triple(
            g,
            bbox_ref,
            DCATUS.westBoundingLongitude,
            dataset_dict["bbox"][0]["west"],
            data_type=XSD.decimal,
        )
        assert self._triple(
            g,
            bbox_ref,
            DCATUS.eastBoundingLongitude,
            dataset_dict["bbox"][0]["east"],
            data_type=XSD.decimal,
        )
        assert self._triple(
            g,
            bbox_ref,
            DCATUS.northBoundingLatitude,
            dataset_dict["bbox"][0]["north"],
            data_type=XSD.decimal,
        )
        assert self._triple(
            g,
            bbox_ref,
            DCATUS.southBoundingLatitude,
            dataset_dict["bbox"][0]["south"],
            data_type=XSD.decimal,
        )

    def test_data_dictionary_dataset(self):

        data_dictionary_dict = {
            "url": "https://example.org/some-data-dictionary",
            "format": "https://resources.data.gov/vocab/file-type/TODO/JSON",
            "license": "https://resources.data.gov/vocab/license/TODO/CC_BYNC_4_0",
        }

        dataset_dict = {
            "name": "test-dcat-us",
            "description": "Test",
            "data_dictionary": [data_dictionary_dict],
        }

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset_dict)

        data_dictionary_ref = [s for s in g.objects(dataset_ref, DCATUS.describedBy)][0]

        assert self._triple(
            g,
            data_dictionary_ref,
            RDF.type,
            DCAT.Distribution,
        )

        assert self._triple(
            g,
            data_dictionary_ref,
            DCAT.accessURL,
            URIRef(data_dictionary_dict["url"]),
        )

        assert self._triple(
            g,
            data_dictionary_ref,
            DCT["format"],
            URIRef(data_dictionary_dict["format"]),
        )

        assert self._triple(
            g,
            data_dictionary_ref,
            DCT.license,
            URIRef(data_dictionary_dict["license"]),
        )

    def test_data_dictionary_distribution(self):

        data_dictionary_dict = {
            "url": "https://example.org/some-data-dictionary",
            "format": "https://resources.data.gov/vocab/file-type/TODO/JSON",
            "license": "https://resources.data.gov/vocab/license/TODO/CC_BYNC_4_0",
        }

        dataset_dict = {
            "name": "test-dcat-us",
            "description": "Test",
            "resources": [
                {
                    "id": "2607a002-142a-40b1-8026-96457b70c01d",
                    "name": "test",
                    "data_dictionary": [data_dictionary_dict],
                }
            ],
        }

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset_dict)

        distribution_ref = [s for s in g.objects(dataset_ref, DCAT.distribution)][0]

        data_dictionary_ref = [
            s for s in g.objects(distribution_ref, DCATUS.describedBy)
        ][0]

        assert self._triple(
            g,
            data_dictionary_ref,
            RDF.type,
            DCAT.Distribution,
        )

        assert self._triple(
            g,
            data_dictionary_ref,
            DCAT.accessURL,
            URIRef(data_dictionary_dict["url"]),
        )

        assert self._triple(
            g,
            data_dictionary_ref,
            DCT["format"],
            URIRef(data_dictionary_dict["format"]),
        )

        assert self._triple(
            g,
            data_dictionary_ref,
            DCT.license,
            URIRef(data_dictionary_dict["license"]),
        )

    def test_data_dictionary_dataset_string(self):

        dataset_dict = {
            "name": "test-dcat-us",
            "description": "Test",
            "data_dictionary": "https://example.org/some-data-dictionary",
        }

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset_dict)

        assert self._triple(
            g,
            dataset_ref,
            DCATUS.describedBy,
            dataset_dict["data_dictionary"],
        )
