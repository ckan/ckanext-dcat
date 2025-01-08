"""
Helpers used by templates
"""
import simplejson as json

import ckantoolkit as toolkit

from ckanext.dcat.processors import RDFSerializer

config = toolkit.config


ENABLE_RDF_ENDPOINTS_CONFIG = "ckanext.dcat.enable_rdf_endpoints"


def endpoints_enabled():
    return toolkit.asbool(config.get(ENABLE_RDF_ENDPOINTS_CONFIG, True))


def get_endpoint(_type="dataset"):
    return "dcat.read_dataset" if _type == "dataset" else "dcat.read_catalog"


def _get_serialization(dataset_dict, profiles=None, _format="jsonld"):

    serializer = RDFSerializer(profiles=profiles)

    output = serializer.serialize_dataset(dataset_dict, _format=_format)

    # parse result again to prevent UnicodeDecodeError and add formatting
    if _format == "jsonld":
        try:
            json_data = json.loads(output)
            return json.dumps(
                json_data,
                sort_keys=True,
                indent=4,
                separators=(",", ": "),
                cls=json.JSONEncoderForHTML,
            )
        except ValueError:
            # result was not JSON, return anyway
            pass
    return output


def structured_data(dataset_dict, profiles=None):
    """
    Returns a string containing the structured data of the given
    dataset id and using the given profiles (if no profiles are supplied
    the default profiles are used).

    This string can be used in the frontend.
    """

    if not profiles:
        profiles = ["schemaorg"]

    return _get_serialization(dataset_dict, profiles, "jsonld")


def croissant(dataset_dict, profiles=None):
    """
    Returns a string containing the Croissant ML representation of the given
    dataset using the `croissant` profile.
    This string can be used in the frontend.
    """

    if not profiles:
        profiles = ["croissant"]

    return _get_serialization(dataset_dict, profiles, "jsonld")
