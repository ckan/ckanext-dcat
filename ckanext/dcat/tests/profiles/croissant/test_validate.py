import json
import sys

try:
    import mlcroissant as mlc
except ImportError:
    pass

import pytest

from ckan.tests.helpers import call_action

from ckanext.dcat.helpers import croissant
from ckanext.dcat.tests.utils import get_file_contents


@pytest.mark.skipif(
    sys.version_info < (3, 10), reason="croissant is not available in py<3.10"
)
def test_valid_output():

    dataset_dict = json.loads(
        get_file_contents("ckan/ckan_full_dataset_croissant.json")
    )

    croissant_dict = json.loads(croissant(dataset_dict))

    try:
        mlc.Dataset(croissant_dict)
    except mlc.ValidationError as exception:
        raise
