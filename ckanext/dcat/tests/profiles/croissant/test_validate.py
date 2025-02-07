import json
import sys

import mlcroissant as mlc

import pytest

from ckan.tests.helpers import call_action
from ckanext.dcat.processors import RDFSerializer
from ckanext.dcat.profiles.croissant import JSONLD_CONTEXT
from ckanext.dcat.tests.utils import get_file_contents


@pytest.mark.skipif(
    sys.version_info < (3, 10), reason="croissant is not available in py<3.10"
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

    try:
        mlc.Dataset(croissant_dict)
    except mlc.ValidationError as exception:
        raise
