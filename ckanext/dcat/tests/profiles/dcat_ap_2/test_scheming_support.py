from unittest import mock
import json
from decimal import Decimal

import pytest
from rdflib.namespace import RDF
from rdflib.term import URIRef
from geomet import wkt

from ckan.tests import factories
from ckan.tests.helpers import call_action

from ckanext.dcat import utils
from ckanext.dcat.processors import RDFSerializer, RDFParser
from ckanext.dcat.profiles import (
    DCAT,
    DCATAP,
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
)
from ckanext.dcat.tests.utils import BaseSerializeTest, BaseParseTest


@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.plugins", "dcat scheming_datasets")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas", "ckanext.dcat.schemas:dcat_ap_full.yaml"
)
@pytest.mark.ckan_config(
    "scheming.presets",
    "ckanext.scheming:presets.json ckanext.dcat.schemas:presets.yaml",
)
@pytest.mark.ckan_config(
    "ckanext.dcat.rdf.profiles", "euro_dcat_ap_2 euro_dcat_ap_scheming"
)
class TestSchemingSerializeSupport(BaseSerializeTest):
    def test_e2e_ckan_to_dcat(self):
        """
        Create a dataset using the scheming schema, check that fields
        are exposed in the DCAT RDF graph
        """

        dataset_dict = {
            # Core fields
            "name": "test-dataset",
            "title": "Test DCAT dataset",
            "notes": "Lorem ipsum",
            "url": "http://example.org/ds1",
            "version": "1.0b",
            "tags": [{"name": "Tag 1"}, {"name": "Tag 2"}],
            # Standard fields
            "issued": "2024-05-01",
            "modified": "2024-05-05",
            "identifier": "xx-some-dataset-id-yy",
            "frequency": "monthly",
            "provenance": "Statement about provenance",
            "dcat_type": "test-type",
            "version_notes": "Some version notes",
            "access_rights": "Statement about access rights",
            # List fields (lists)
            "alternate_identifier": ["alt-id-1", "alt-id-2"],
            "theme": [
                "https://example.org/uri/theme1",
                "https://example.org/uri/theme2",
                "https://example.org/uri/theme3",
            ],
            "language": ["en", "ca", "es"],
            "documentation": ["https://example.org/some-doc.html"],
            "conforms_to": ["Standard 1", "Standard 2"],
            "is_referenced_by": [
                "https://doi.org/10.1038/sdata.2018.22",
                "test_isreferencedby",
            ],
            "applicable_legislation": [
                "http://data.europa.eu/eli/reg_impl/2023/138/oj",
                "http://data.europa.eu/eli/reg_impl/2023/138/oj_alt",
            ],
            # Repeating subfields
            "contact": [
                {"name": "Contact 1", "email": "contact1@example.org"},
                {"name": "Contact 2", "email": "contact2@example.org"},
            ],
            "publisher": [
                {
                    "name": "Test Publisher",
                    "email": "publisher@example.org",
                    "url": "https://example.org",
                    "type": "public_body",
                    "identifier": "http://example.org/publisher-id",
                },
            ],
            "temporal_coverage": [
                {"start": "1905-03-01", "end": "2013-01-05"},
                {"start": "2024-04-10", "end": "2024-05-29"},
            ],
            "temporal_resolution": "PT15M",
            "spatial_coverage": [
                {
                    "geom": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [11.9936, 54.0486],
                                [11.9936, 54.2466],
                                [12.3045, 54.2466],
                                [12.3045, 54.0486],
                                [11.9936, 54.0486],
                            ]
                        ],
                    },
                    "text": "Tarragona",
                    "uri": "https://sws.geonames.org/6361390/",
                    "bbox": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [-2.1604, 42.7611],
                                [-2.0938, 42.7611],
                                [-2.0938, 42.7931],
                                [-2.1604, 42.7931],
                                [-2.1604, 42.7611],
                            ]
                        ],
                    },
                    "centroid": {"type": "Point", "coordinates": [1.26639, 41.12386]},
                }
            ],
            "spatial_resolution_in_meters": 1.5,
            "resources": [
                {
                    "name": "Resource 1",
                    "description": "Some description",
                    "url": "https://example.com/data.csv",
                    "format": "CSV",
                    "availability": "http://publications.europa.eu/resource/authority/planned-availability/EXPERIMENTAL",
                    "compress_format": "http://www.iana.org/assignments/media-types/application/gzip",
                    "package_format": "http://publications.europa.eu/resource/authority/file-type/TAR",
                    "size": 12323,
                    "hash": "4304cf2e751e6053c90b1804c89c0ebb758f395a",
                    "hash_algorithm": "http://spdx.org/rdf/terms#checksumAlgorithm_sha1",
                    "status": "http://purl.org/adms/status/Completed",
                    "access_url": "https://example.com/data.csv",
                    "download_url": "https://example.com/data.csv",
                    "issued": "2024-05-01T01:20:33",
                    "modified": "2024-05-05T09:33:20",
                    "license": "http://creativecommons.org/licenses/by/3.0/",
                    "rights": "Some stament about rights",
                    "language": ["en", "ca", "es"],
                    "access_services": [
                        {
                            "title": "Access Service 1",
                            "endpoint_url": [
                                "https://example.org/access_service/1",
                                "https://example.org/access_service/2",
                            ],
                        }
                    ],
                }
            ],
        }

        dataset = call_action("package_create", **dataset_dict)

        # Make sure schema was used
        assert dataset["conforms_to"][0] == "Standard 1"
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
            g, dataset_ref, DCT.accrualPeriodicity, dataset["frequency"]
        )
        assert self._triple(g, dataset_ref, DCT.provenance, dataset["provenance"])
        assert self._triple(g, dataset_ref, DCT.type, dataset["dcat_type"])
        assert self._triple(g, dataset_ref, ADMS.versionNotes, dataset["version_notes"])
        assert self._triple(g, dataset_ref, DCT.accessRights, dataset["access_rights"])
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
        assert (
            self._triples_list_values(g, dataset_ref, ADMS.identifier)
            == dataset["alternate_identifier"]
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
            self._triples_list_values(g, dataset_ref, DCATAP.applicableLegislation)
            == dataset["applicable_legislation"]
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
        assert self._triple(
            g,
            publisher[0][2],
            DCT.type,
            dataset_dict["publisher"][0]["type"],
        )
        assert self._triple(
            g,
            publisher[0][2],
            DCT.identifier,
            URIRef(dataset_dict["publisher"][0]["identifier"])
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

        assert self._triple(g, distribution_ref, DCT.rights, resource["rights"])
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
            DCATAP.availability,
            URIRef(resource["availability"]),
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
            g, distribution_ref, DCAT.byteSize, Decimal(resource["size"]), XSD.decimal
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

        # Resource: repeating subfields
        access_services = [
            t for t in g.triples((distribution_ref, DCAT.accessService, None))
        ]

        assert len(access_services) == len(dataset["resources"][0]["access_services"])
        assert self._triple(
            g,
            access_services[0][2],
            DCT.title,
            resource["access_services"][0]["title"],
        )

        endpoint_urls = [
            str(t[2])
            for t in g.triples((access_services[0][2], DCAT.endpointURL, None))
        ]
        assert endpoint_urls == resource["access_services"][0]["endpoint_url"]

    def test_publisher_fallback_org(self):

        org = factories.Organization(
            title="Some publisher org",
        )
        dataset_dict = {
            "name": "test-dataset-2",
            "title": "Test DCAT dataset 2",
            "notes": "Lorem ipsum",
            "owner_org": org["id"],
        }

        dataset = call_action("package_create", **dataset_dict)

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)
        publisher = [t for t in g.triples((dataset_ref, DCT.publisher, None))]

        assert len(publisher) == 1
        assert self._triple(g, publisher[0][2], FOAF.name, org["title"])

    def test_publisher_fallback_org_ignored_if_publisher_field_present(self):

        org = factories.Organization()
        dataset_dict = {
            "name": "test-dataset-2",
            "title": "Test DCAT dataset 2",
            "notes": "Lorem ipsum",
            "publisher": [
                {
                    "name": "Test Publisher",
                    "email": "publisher@example.org",
                    "url": "https://example.org",
                    "type": "public_body",
                },
            ],
            "owner_org": org["id"],
        }

        dataset = call_action("package_create", **dataset_dict)

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)
        publisher = [t for t in g.triples((dataset_ref, DCT.publisher, None))]

        assert len(publisher) == 1
        assert self._triple(
            g, publisher[0][2], FOAF.name, dataset_dict["publisher"][0]["name"]
        )

    def test_empty_repeating_subfields_not_serialized(self):

        dataset_dict = {
            "name": "test-dataset-3",
            "title": "Test DCAT dataset 3",
            "notes": "Lorem ipsum",
            "spatial_coverage": [
                {
                    "uri": "",
                    "geom": "",
                },
            ],
        }

        dataset = call_action("package_create", **dataset_dict)

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)
        assert not [t for t in g.triples((dataset_ref, DCT.spatial, None))]

    def test_legacy_fields(self):

        dataset_dict = {
            "name": "test-dataset-2",
            "title": "Test DCAT dataset 2",
            "notes": "Lorem ipsum",
            "extras": [
                {"key": "contact_name", "value": "Test Contact"},
                {"key": "contact_email", "value": "contact@example.org"},
                {"key": "publisher_name", "value": "Test Publisher"},
                {"key": "publisher_email", "value": "publisher@example.org"},
                {"key": "publisher_url", "value": "https://example.org"},
                {"key": "publisher_type", "value": "public_body"},
            ],
        }

        dataset = call_action("package_create", **dataset_dict)

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)
        contact_details = [t for t in g.triples((dataset_ref, DCAT.contactPoint, None))]
        assert len(contact_details) == 1
        assert self._triple(g, contact_details[0][2], VCARD.fn, "Test Contact")

        publisher = [t for t in g.triples((dataset_ref, DCT.publisher, None))]
        assert len(publisher) == 1
        assert self._triple(g, publisher[0][2], FOAF.name, "Test Publisher")

    def test_dcat_date(self):
        dataset_dict = {
            # Core fields
            "name": "test-dataset",
            "title": "Test DCAT dataset",
            "notes": "Some notes",
            "issued": "2024",
            "modified": "2024-10",
            "temporal_coverage": [
                {"start": "1905-03-01T10:07:31.182680", "end": "2013-01-05"},
                {"start": "2024-04-10T10:07:31", "end": "2024-05-29"},
                {"start": "11/24/24", "end": "06/12/12"},
            ],
        }

        dataset = call_action("package_create", **dataset_dict)

        s = RDFSerializer()
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        # Year
        assert dataset["issued"] == dataset_dict["issued"]
        assert self._triple(
            g,
            dataset_ref,
            DCT.issued,
            dataset_dict["issued"],
            data_type=XSD.gYear,
        )

        # Year-month
        assert dataset["modified"] == dataset_dict["modified"]
        assert self._triple(
            g,
            dataset_ref,
            DCT.modified,
            dataset_dict["modified"],
            data_type=XSD.gYearMonth,
        )

        temporal = [t for t in g.triples((dataset_ref, DCT.temporal, None))]

        # Date
        assert (
            dataset["temporal_coverage"][0]["end"]
            == dataset_dict["temporal_coverage"][0]["end"]
        )

        assert self._triple(
            g,
            temporal[0][2],
            DCAT.endDate,
            dataset_dict["temporal_coverage"][0]["end"],
            data_type=XSD.date,
        )

        # Datetime
        assert (
            dataset["temporal_coverage"][0]["start"]
            == dataset_dict["temporal_coverage"][0]["start"]
        )
        assert self._triple(
            g,
            temporal[0][2],
            DCAT.startDate,
            dataset_dict["temporal_coverage"][0]["start"],
            data_type=XSD.dateTime,
        )

        assert (
            dataset["temporal_coverage"][1]["start"]
            == dataset_dict["temporal_coverage"][1]["start"]
        )
        assert self._triple(
            g,
            temporal[1][2],
            DCAT.startDate,
            dataset_dict["temporal_coverage"][1]["start"],
            data_type=XSD.dateTime,
        )

        # Ambiguous Datetime
        assert (
            dataset["temporal_coverage"][2]["start"]
            == dataset_dict["temporal_coverage"][2]["start"]
        )
        assert self._triple(
            g,
            temporal[2][2],
            DCAT.startDate,
            "2024-11-24T00:00:00",
            data_type=XSD.dateTime,
        )
        assert (
            dataset["temporal_coverage"][2]["end"]
            == dataset_dict["temporal_coverage"][2]["end"]
        )
        assert self._triple(
            g,
            temporal[2][2],
            DCAT.endDate,
            "2012-06-12T00:00:00",
            data_type=XSD.dateTime,
        )


@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.plugins", "dcat scheming_datasets")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas", "ckanext.dcat.schemas:dcat_ap_full.yaml"
)
@pytest.mark.ckan_config(
    "scheming.presets",
    "ckanext.scheming:presets.json ckanext.dcat.schemas:presets.yaml",
)
@pytest.mark.ckan_config(
    "ckanext.dcat.rdf.profiles", "euro_dcat_ap_2 euro_dcat_ap_scheming"
)
class TestSchemingValidators:
    def test_mimetype_is_guessed(self):
        dataset_dict = {
            "name": "test-dataset-2",
            "title": "Test DCAT dataset 2",
            "notes": "Lorem ipsum",
            "resources": [
                {"url": "https://example.org/data.csv"},
                {"url": "https://example.org/report.pdf"},
            ],
        }

        dataset = call_action("package_create", **dataset_dict)

        assert sorted([r["mimetype"] for r in dataset["resources"]]) == [
            "application/pdf",
            "text/csv",
        ]


@pytest.mark.usefixtures("with_plugins", "clean_db")
@pytest.mark.ckan_config("ckan.plugins", "dcat scheming_datasets")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas", "ckanext.dcat.schemas:dcat_ap_full.yaml"
)
@pytest.mark.ckan_config(
    "scheming.presets",
    "ckanext.scheming:presets.json ckanext.dcat.schemas:presets.yaml",
)
@pytest.mark.ckan_config(
    "ckanext.dcat.rdf.profiles", "euro_dcat_ap_2 euro_dcat_ap_scheming"
)
class TestSchemingParseSupport(BaseParseTest):
    def test_e2e_dcat_to_ckan(self):
        """
        Parse a DCAT RDF graph into a CKAN dataset dict, create a dataset with package_create
        and check that all expected fields are there
        """
        contents = self._get_file_contents("dcat/dataset.rdf")

        p = RDFParser()

        p.parse(contents)

        datasets = [d for d in p.datasets()]

        assert len(datasets) == 1

        dataset_dict = datasets[0]

        dataset_dict["name"] = "test-dcat-1"
        dataset = call_action("package_create", **dataset_dict)

        # Core fields

        assert dataset["title"] == "Zimbabwe Regional Geochemical Survey."
        assert (
            dataset["notes"]
            == "During the period 1982-86 a team of geologists from the British Geological Survey ..."
        )
        assert dataset["url"] == "http://dataset.info.org"
        assert dataset["version"] == "2.3"
        assert dataset["license_id"] == "cc-nc"
        assert sorted([t["name"] for t in dataset["tags"]]) == [
            "exploration",
            "geochemistry",
            "geology",
        ]

        # Standard fields
        assert dataset["version_notes"] == "New schema added"
        assert dataset["identifier"] == u"9df8df51-63db-37a8-e044-0003ba9b0d98"
        assert dataset["frequency"] == "http://purl.org/cld/freq/daily"
        assert dataset["access_rights"] == "public"
        assert dataset["provenance"] == "Some statement about provenance"
        assert dataset["dcat_type"] == "test-type"

        assert dataset["issued"] == u"2012-05-10"
        assert dataset["modified"] == u"2012-05-10T21:04:00"
        assert dataset["temporal_resolution"] == "PT15M"
        assert dataset["spatial_resolution_in_meters"] == "1.5"

        # List fields
        assert sorted(dataset["conforms_to"]) == ["Standard 1", "Standard 2"]
        assert sorted(dataset["language"]) == ["ca", "en", "es"]
        assert sorted(dataset["theme"]) == [
            "Earth Sciences",
            "http://eurovoc.europa.eu/100142",
            "http://eurovoc.europa.eu/209065",
        ]
        assert sorted(dataset["alternate_identifier"]) == [
            "alternate-identifier-1",
            "alternate-identifier-2",
        ]
        assert sorted(dataset["documentation"]) == [
            "http://dataset.info.org/doc1",
            "http://dataset.info.org/doc2",
        ]

        assert sorted(dataset["is_referenced_by"]) == [
            "https://doi.org/10.1038/sdata.2018.22",
            "test_isreferencedby",
        ]
        assert sorted(dataset["applicable_legislation"]) == [
            "http://data.europa.eu/eli/reg_impl/2023/138/oj",
            "http://data.europa.eu/eli/reg_impl/2023/138/oj_alt",
        ]
        # Repeating subfields

        assert dataset["contact"][0]["name"] == "Point of Contact"
        assert dataset["contact"][0]["email"] == "contact@some.org"

        assert (
            dataset["publisher"][0]["name"] == "Publishing Organization for dataset 1"
        )
        assert dataset["publisher"][0]["email"] == "contact@some.org"
        assert dataset["publisher"][0]["url"] == "http://some.org"
        assert (
            dataset["publisher"][0]["type"]
            == "http://purl.org/adms/publishertype/NonProfitOrganisation"
        )
        assert dataset["temporal_coverage"][0]["start"] == "1905-03-01"
        assert dataset["temporal_coverage"][0]["end"] == "2013-01-05"

        resource = dataset["resources"][0]

        # Resources: core fields
        assert resource["url"] == "http://www.bgs.ac.uk/gbase/geochemcd/home.html"

        # Resources: standard fields
        assert resource["license"] == "http://creativecommons.org/licenses/by-nc/2.0/"
        assert resource["rights"] == "Some statement about rights"
        assert resource["issued"] == "2012-05-11"
        assert resource["modified"] == "2012-05-01T00:04:06"
        assert resource["status"] == "http://purl.org/adms/status/Completed"
        assert resource["size"] == 12323
        assert (
            resource["availability"]
            == "http://publications.europa.eu/resource/authority/planned-availability/EXPERIMENTAL"
        )
        assert (
            resource["compress_format"]
            == "http://www.iana.org/assignments/media-types/application/gzip"
        )
        assert (
            resource["package_format"]
            == "http://publications.europa.eu/resource/authority/file-type/TAR"
        )

        assert resource["hash"] == "4304cf2e751e6053c90b1804c89c0ebb758f395a"
        assert (
            resource["hash_algorithm"]
            == "http://spdx.org/rdf/terms#checksumAlgorithm_sha1"
        )

        assert (
            resource["access_url"] == "http://www.bgs.ac.uk/gbase/geochemcd/home.html"
        )
        assert "download_url" not in resource

        # Resources: list fields
        assert sorted(resource["language"]) == ["ca", "en", "es"]
        assert sorted(resource["documentation"]) == [
            "http://dataset.info.org/distribution1/doc1",
            "http://dataset.info.org/distribution1/doc2",
        ]
        assert sorted(resource["conforms_to"]) == ["Standard 1", "Standard 2"]

        # Resources: repeating subfields
        assert resource["access_services"][0]["title"] == "Sparql-end Point"
        assert resource["access_services"][0]["endpoint_url"] == [
            "http://publications.europa.eu/webapi/rdf/sparql"
        ]


@pytest.mark.usefixtures("with_plugins", "clean_db", "clean_index")
@pytest.mark.ckan_config("ckan.plugins", "dcat scheming_datasets")
@pytest.mark.ckan_config(
    "scheming.dataset_schemas", "ckanext.dcat.schemas:dcat_ap_full.yaml"
)
@pytest.mark.ckan_config(
    "scheming.presets",
    "ckanext.scheming:presets.json ckanext.dcat.schemas:presets.yaml",
)
@pytest.mark.ckan_config(
    "ckanext.dcat.rdf.profiles", "euro_dcat_ap_2 euro_dcat_ap_scheming"
)
class TestSchemingIndexFields:
    def test_repeating_subfields_index(self):

        dataset_dict = {
            # Core fields
            "name": "test-dataset",
            "title": "Test DCAT dataset",
            "notes": "Some notes",
            # Repeating subfields
            "contact": [
                {"name": "Contact 1", "email": "contact1@example.org"},
                {"name": "Contact 2", "email": "contact2@example.org"},
            ],
        }

        with mock.patch("ckan.lib.search.index.make_connection") as m:
            call_action("package_create", **dataset_dict)

            # Dict sent to Solr
            search_dict = m.mock_calls[1].kwargs["docs"][0]
            assert search_dict["extras_contact__name"] == "Contact 1 Contact 2"
            assert (
                search_dict["extras_contact__email"]
                == "contact1@example.org contact2@example.org"
            )

    def test_repeating_subfields_search(self):

        dataset_dict = {
            # Core fields
            "name": "test-dataset",
            "title": "Test DCAT dataset",
            "notes": "Some notes",
            # Repeating subfields
            "contact": [
                {"name": "Contact 1", "email": "contact1@example.org"},
                {"name": "Contact 2", "email": "contact2@example.org"},
            ],
        }

        dataset = call_action("package_create", **dataset_dict)

        result = call_action("package_search", q="Contact 2")

        assert result["results"][0]["id"] == dataset["id"]

        result = call_action("package_search", q="Contact 3")

        assert result["count"] == 0

    def test_spatial_field(self):

        dataset_dict = {
            # Core fields
            "name": "test-dataset",
            "title": "Test DCAT dataset",
            "notes": "Some notes",
            "spatial_coverage": [
                {
                    "uri": "https://sws.geonames.org/6361390/",
                    "centroid": {"type": "Point", "coordinates": [1.26639, 41.12386]},
                },
                {
                    "geom": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [11.9936, 54.0486],
                                [11.9936, 54.2466],
                                [12.3045, 54.2466],
                                [12.3045, 54.0486],
                                [11.9936, 54.0486],
                            ]
                        ],
                    },
                    "text": "Tarragona",
                },
            ],
        }

        with mock.patch("ckan.lib.search.index.make_connection") as m:
            call_action("package_create", **dataset_dict)

            # Dict sent to Solr
            search_dict = m.mock_calls[1].kwargs["docs"][0]
            assert search_dict["spatial"] == json.dumps(
                dataset_dict["spatial_coverage"][0]["centroid"]
            )
