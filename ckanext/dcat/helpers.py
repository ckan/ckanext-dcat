"""
Helpers used by templates
"""

import simplejson as json

import ckantoolkit as toolkit

from pyld import jsonld

from ckanext.dcat.processors import RDFSerializer
from ckanext.dcat.profiles.croissant import JSONLD_CONTEXT

config = toolkit.config


ENABLE_RDF_ENDPOINTS_CONFIG = "ckanext.dcat.enable_rdf_endpoints"


def endpoints_enabled():
    return toolkit.asbool(config.get(ENABLE_RDF_ENDPOINTS_CONFIG, True))


def get_endpoint(_type="dataset"):
    return "dcat.read_dataset" if _type == "dataset" else "dcat.read_catalog"


def _get_serialization(
    dataset_dict, profiles=None, _format="jsonld", context=None, frame=None
):

    serializer = RDFSerializer(profiles=profiles)

    output = serializer.serialize_dataset(
        dataset_dict, _format=_format, context=context
    )

    # parse result again to prevent UnicodeDecodeError and add formatting

    if _format == "jsonld":
        try:
            json_data = json.loads(output)

            if frame:
                json_data = jsonld.frame(json_data, frame)

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
        profiles = config.get("ckanext.dcat.structured_data.profiles", ["schemaorg"])

    return _get_serialization(dataset_dict, profiles, "jsonld")


def croissant(dataset_dict, profiles=None):
    """
    Returns a string containing the Croissant ML representation of the given
    dataset using the `croissant` profile.
    This string can be used in the frontend.
    """

    if not profiles:
        profiles = config.get("ckanext.dcat.croissant.profiles", ["croissant"])

    frame = {"@context": JSONLD_CONTEXT, "@type": "sc:Dataset"}

    return _get_serialization(
        dataset_dict, profiles, "jsonld", context=JSONLD_CONTEXT, frame=frame
    )
