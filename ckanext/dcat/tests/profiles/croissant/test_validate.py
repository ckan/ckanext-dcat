import json

import mlcroissant as mlc

from ckan.tests.helpers import call_action
from ckanext.dcat.processors import RDFSerializer
from ckanext.dcat.tests.utils import get_file_contents


def test_valid_output():

    dataset_dict = json.loads(get_file_contents("ckan/ckan_full_dataset_croissant.json"))

    s = RDFSerializer(profiles=["croissant"])

    s.graph_from_dataset(dataset_dict)

    croissant_dict = s.g.serialize(format="json-ld")

    try:
        mlc.Dataset(croissant_dict)
    except mlc.ValidationError as exception:
        raise