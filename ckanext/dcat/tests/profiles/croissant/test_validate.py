import json
import sys
from unittest import mock

try:
    import mlcroissant as mlc
except ImportError:
    pass

import pytest

from ckan.tests.helpers import call_action
from ckanext.dcat.processors import RDFSerializer
from ckanext.dcat.profiles.croissant import JSONLD_CONTEXT
from ckanext.dcat.tests.utils import get_file_contents


@pytest.mark.skipif(
    sys.version_info < (3, 10), reason="mlcroissant is not available in py<3.10"
)
def test_valid_output():

    dataset_dict = json.loads(
        get_file_contents("ckan/ckan_full_dataset_croissant.json")
    )

    s = RDFSerializer(profiles=["croissant"])

    s.graph_from_dataset(dataset_dict)

    croissant_dict = json.loads(
        s.g.serialize(format="json-ld", auto_compact=True, context=JSONLD_CONTEXT)
    )
    with open("graph.jsonld", "w") as f:
        f.write(json.dumps(croissant_dict))

    try:
        mlc.Dataset(croissant_dict)
    except mlc.ValidationError as exception:
        raise


@pytest.mark.skipif(
    sys.version_info < (3, 10), reason="mlcroissant is not available in py<3.10"
)
def test_valid_output_with_recordset():

    dataset_dict = json.loads(
        get_file_contents("ckan/ckan_full_dataset_croissant.json")
    )

    resource_id = dataset_dict["resources"][0]["id"]

    def mock_datastore_info(context, data_dict):
        return {
            "meta": {"id": resource_id, "count": 10, "table_type": "BASE TABLE"},
            "fields": [
                {"id": "name", "type": "text", "schema": {"is_index": True}},
                {"id": "age", "type": "int", "schema": {"is_index": False}},
                {"id": "timestamp", "type": "timestamp", "schema": {"is_index": False}},
            ],
        }

    with mock.patch("ckanext.dcat.profiles.croissant.get_action") as mock_get_action:
        mock_get_action.return_value = mock_datastore_info

        s = RDFSerializer(profiles=["croissant"])

        s.graph_from_dataset(dataset_dict)

        croissant_dict = json.loads(
            s.g.serialize(format="json-ld", auto_compact=True, context=JSONLD_CONTEXT)
        )
        with open("graph.jsonld", "w") as f:
            f.write(json.dumps(croissant_dict))

        try:
            mlc.Dataset(croissant_dict)
        except mlc.ValidationError as exception:
            raise
