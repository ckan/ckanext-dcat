import json
import os

from ckanext.dcat.cli import dcat as dcat_cli


def test_consume(cli):

    path = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "examples", "dataset_afs.ttl"
    )

    result = cli.invoke(dcat_cli, ["consume", "-f", "ttl", path])
    assert result.exit_code == 0

    assert json.loads(result.stdout)[0]["title"] == "A test dataset on your catalogue"


def test_produce(cli):

    path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "..",
        "examples",
        "full_ckan_dataset.json",
    )

    result = cli.invoke(dcat_cli, ["produce", "-f", "jsonld", path])
    assert result.exit_code == 0

    assert json.loads(result.stdout)["@context"]["dcat"] == "http://www.w3.org/ns/dcat#"
