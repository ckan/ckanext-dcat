from builtins import str
import json

import pytest

from ckantoolkit import config, url_for

from dateutil.parser import parse as parse_date
from rdflib import URIRef, BNode, Literal
from rdflib.namespace import RDF

from ckantoolkit.tests import helpers, factories

from ckanext.dcat import utils
from ckanext.dcat.profiles import XSD, DCT, FOAF
from ckanext.dcat.processors import RDFSerializer
from ckanext.dcat.profiles.croissant import SCHEMA, CR

from ckanext.dcat.tests.profiles.dcat_ap.test_euro_dcatap_profile_serialize import (
    BaseSerializeTest,
)
from ckanext.dcat.tests.utils import get_file_contents


class TestCroissantProfileSerializeDataset(BaseSerializeTest):

    def test_graph_from_dataset(self):

        dataset_dict = json.loads(
            get_file_contents("ckan/ckan_full_dataset_croissant.json")
        )

        s = RDFSerializer(profiles=["croissant"])
        g = s.g

        s.graph_from_dataset(dataset_dict)

        dataset_ref = URIRef(dataset_dict["id_given"])

        # Basic fields
        assert self._triple(g, dataset_ref, RDF.type, SCHEMA.Dataset)
        assert self._triple(g, dataset_ref, SCHEMA.name, dataset_dict["title"])
        assert self._triple(g, dataset_ref, SCHEMA.description, dataset_dict["notes"])
        assert self._triple(g, dataset_ref, SCHEMA.version, dataset_dict["version"])
        assert self._triple(g, dataset_ref, SCHEMA.license, dataset_dict["license"])
        assert self._triple(
            g, dataset_ref, SCHEMA.sdLicense, dataset_dict["structured_data_license"]
        )
        assert self._triple(
            g,
            dataset_ref,
            SCHEMA.url,
            url_for("dataset.read", id=dataset_dict["name"], _external=True),
        )

        assert self._triple(
            g, dataset_ref, CR.isLiveDataset, dataset_dict["is_live_dataset"]
        )
        assert self._triple(g, dataset_ref, CR.citeAs, dataset_dict["cite_as"])

        # Dates
        assert self._triple(
            g,
            dataset_ref,
            SCHEMA.dateCreated,
            dataset_dict["created"],
            data_type=XSD.date,
        )
        assert self._triple(
            g,
            dataset_ref,
            SCHEMA.datePublished,
            dataset_dict["issued"],
            data_type=XSD.date,
        )
        assert self._triple(
            g,
            dataset_ref,
            SCHEMA.dateModified,
            dataset_dict["modified"],
            data_type=XSD.date,
        )

        # Tags
        assert len([t for t in g.triples((dataset_ref, SCHEMA.keywords, None))]) == 2
        for tag in dataset_dict["tags"]:
            assert self._triple(g, dataset_ref, SCHEMA.keywords, tag["name"])

        # Lists
        assert sorted(
            [str(t) for t in g.objects(dataset_ref, SCHEMA.inLanguage)]
        ) == sorted(dataset_dict["language"])

        assert sorted(
            [str(t) for t in g.objects(dataset_ref, SCHEMA.sameAs)]
        ) == sorted(dataset_dict["same_as"])

        # Agents
        creator = [t for t in g.triples((dataset_ref, SCHEMA.creator, None))]
        assert len(creator) == 1
        creator_ref = URIRef(dataset_dict["creator"][0]["id_given"])
        assert self._triple(
            g, creator_ref, SCHEMA.name, dataset_dict["creator"][0]["name"]
        )
        assert self._triple(
            g,
            creator_ref,
            SCHEMA.email,
            dataset_dict["creator"][0]["email"],
        )
        assert self._triple(
            g,
            creator_ref,
            SCHEMA.url,
            dataset_dict["creator"][0]["url"],
        )
        assert self._triple(
            g,
            creator_ref,
            SCHEMA.identifier,
            dataset_dict["creator"][0]["identifier"],
        )
        assert self._triple(
            g,
            creator_ref,
            RDF.type,
            SCHEMA.Person,
        )

        publisher = [t for t in g.triples((dataset_ref, SCHEMA.publisher, None))]
        assert len(publisher) == 1
        publisher_ref = URIRef(dataset_dict["publisher"][0]["id_given"])
        assert self._triple(
            g, publisher_ref, SCHEMA.name, dataset_dict["publisher"][0]["name"]
        )
        assert self._triple(
            g,
            publisher_ref,
            SCHEMA.email,
            dataset_dict["publisher"][0]["email"],
        )
        assert self._triple(
            g,
            publisher_ref,
            SCHEMA.url,
            dataset_dict["publisher"][0]["url"],
        )
        assert self._triple(
            g,
            publisher_ref,
            SCHEMA.identifier,
            dataset_dict["publisher"][0]["identifier"],
        )
        assert self._triple(
            g,
            publisher_ref,
            RDF.type,
            SCHEMA.Person,
        )

        # Resources
        distributions = [t for t in g.triples((dataset_ref, SCHEMA.distribution, None))]
        assert len(distributions) == 3  # 1 resource + 2 sub-resources
        resource_ref = URIRef(dataset_dict["resources"][0]["id_given"])
        resource_dict = dataset_dict["resources"][0]

        assert self._triple(g, resource_ref, RDF.type, CR.FileObject)
        assert self._triple(g, resource_ref, SCHEMA.name, resource_dict["name"])
        assert self._triple(
            g, resource_ref, SCHEMA.description, resource_dict["description"]
        )
        assert self._triple(g, resource_ref, SCHEMA.contentUrl, resource_dict["url"])
        assert self._triple(
            g, resource_ref, SCHEMA.encodingFormat, resource_dict["format"]
        )
        assert self._triple(g, resource_ref, SCHEMA.sha256, resource_dict["hash"])
        assert self._triple(g, resource_ref, SCHEMA.contentSize, resource_dict["size"])

        # Sub-resources

        sub_resource_file_obj_dict = [
            d
            for d in dataset_dict["resources"][0]["subresources"]
            if d["type"] == "fileObject"
        ][0]
        sub_resource_file_obj_ref = URIRef(sub_resource_file_obj_dict["id_given"])

        assert self._triple(g, sub_resource_file_obj_ref, RDF.type, CR.FileObject)

        assert self._triple(
            g, sub_resource_file_obj_ref, SCHEMA.containedIn, resource_ref
        )

        assert self._triple(
            g,
            sub_resource_file_obj_ref,
            SCHEMA.description,
            sub_resource_file_obj_dict["description"],
        )
        assert self._triple(
            g,
            sub_resource_file_obj_ref,
            SCHEMA.contentUrl,
            sub_resource_file_obj_dict["url"],
        )
        assert self._triple(
            g,
            sub_resource_file_obj_ref,
            SCHEMA.encodingFormat,
            sub_resource_file_obj_dict["format"],
        )
        assert self._triple(
            g,
            sub_resource_file_obj_ref,
            SCHEMA.contentSize,
            sub_resource_file_obj_dict["size"],
        )

        # Hash should not be in sub-resources
        assert not self._triple(
            g,
            sub_resource_file_obj_ref,
            SCHEMA.sha256,
            sub_resource_file_obj_dict["hash"],
        )

        sub_resource_file_set_dict = [
            d
            for d in dataset_dict["resources"][0]["subresources"]
            if d["type"] == "fileSet"
        ][0]
        sub_resource_file_set_ref = URIRef(sub_resource_file_set_dict["id_given"])

        assert self._triple(g, sub_resource_file_set_ref, RDF.type, CR.FileSet)

        assert self._triple(
            g, sub_resource_file_set_ref, SCHEMA.containedIn, resource_ref
        )

        assert self._triple(
            g,
            sub_resource_file_set_ref,
            SCHEMA.description,
            sub_resource_file_set_dict["description"],
        )
        assert self._triple(
            g,
            sub_resource_file_set_ref,
            SCHEMA.encodingFormat,
            sub_resource_file_set_dict["format"],
        )
        assert self._triple(
            g,
            sub_resource_file_set_ref,
            CR.includes,
            sub_resource_file_set_dict["includes"],
        )
        assert self._triple(
            g,
            sub_resource_file_set_ref,
            CR.excludes,
            sub_resource_file_set_dict["excludes"],
        )

    @pytest.mark.usefixtures("with_plugins", "clean_db")
    def test_graph_from_dataset_org_fallback(self):

        org = factories.Organization()

        data_dict = {
            "name": "test-dataset",
            "title": "Test dataset",
            "owner_org": org["id"],
        }
        dataset_dict = helpers.call_action("package_create", **data_dict)

        assert dataset_dict["organization"]["title"] == org["title"]

        s = RDFSerializer(profiles=["croissant"])
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset_dict)

        creator = [t for t in g.triples((dataset_ref, SCHEMA.creator, None))]
        assert len(creator) == 1
        creator_ref = creator[0][2]
        assert self._triple(g, creator_ref, SCHEMA.name, org["title"])
