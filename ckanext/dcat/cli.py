# -*- coding: utf-8 -*-
import json

import click

import ckan.plugins.toolkit as tk

import ckanext.dcat.utils as utils
from ckanext.dcat.processors import (
    RDFParser,
    RDFSerializer,
    DEFAULT_RDF_PROFILES,
    RDF_PROFILES_CONFIG_OPTION,
)


@click.group()
def dcat():
    """DCAT utilities for CKAN"""
    pass


@dcat.command()
@click.argument("output", type=click.File(mode="w"))
def generate_static(output):
    """[Deprecated] Generate a static datasets file in JSON format
    (requires the dcat_json_interface plugin) .
    """
    utils.generate_static_json(output)


def _get_profiles(profiles):
    if profiles:
        profiles = profiles.split()
    elif tk.config.get(RDF_PROFILES_CONFIG_OPTION):
        profiles = tk.aslist(tk.config[RDF_PROFILES_CONFIG_OPTION])
    else:
        profiles = None

    return profiles


@dcat.command(context_settings={"show_default": True})
@click.argument("input", type=click.File(mode="r"))
@click.option(
    "-o",
    "--output",
    type=click.File(mode="w"),
    default="-",
    help="By default the command will output the result to stdin, "
    "alternatively you can provide a file path with this option",
)
@click.option(
    "-f", "--format", default="xml", help="Serialization format (eg ttl, jsonld)"
)
@click.option(
    "-p",
    "--profiles",
    help=f"RDF profiles to use. If not provided will be read from config, "
    "if not present there, the default will be used: {DEFAULT_RDF_PROFILES}",
)
@click.option(
    "-P", "--pretty", is_flag=True, help="Make the output more human readable"
)
@click.option(
    "-m", "--compat_mode", is_flag=True, help="Compatibility mode (deprecated)"
)
def consume(input, output, format, profiles, pretty, compat_mode):
    """
    Parses DCAT RDF graphs into CKAN dataset JSON objects.

    The input serializations can be provided as a path to a file, e.g.:

        ckan dcat consume examples/dataset.ttl

    Or be read from stdin:

        ckan dcat consume -
    """
    contents = input.read()

    profiles = _get_profiles(profiles)

    parser = RDFParser(profiles=profiles, compatibility_mode=compat_mode)
    parser.parse(contents, _format=format)

    ckan_datasets = [d for d in parser.datasets()]

    indent = 4 if pretty else None
    out = json.dumps(ckan_datasets, indent=indent)

    output.write(out)


@dcat.command(context_settings={"show_default": True})
@click.argument("input", type=click.File(mode="r"))
@click.option(
    "-o",
    "--output",
    type=click.File(mode="w"),
    default="-",
    help="By default the command will output the result to stdin, "
    "alternatively you can provide a file path with this option",
)
@click.option(
    "-f", "--format", default="xml", help="Serialization format (eg ttl, jsonld)"
)
@click.option(
    "-p",
    "--profiles",
    help=f"RDF profiles to use. If not provided will be read from config, "
    "if not present there, the default will be used: {DEFAULT_RDF_PROFILES}",
)
@click.option(
    "-m", "--compat_mode", is_flag=True, help="Compatibility mode (deprecated)"
)
def produce(input, output, format, profiles, compat_mode):
    """
    Transforms CKAN dataset JSON objects into DCAT RDF serializations.

    The input datasets can be provided as a path to a file, e.g.:

        ckan dcat consume examples/ckan_dataset.json

    Or be read from stdin:

        ckan dcat produce -
    """
    contents = input.read()

    profiles = _get_profiles(profiles)

    serializer = RDFSerializer(profiles=profiles, compatibility_mode=compat_mode)

    dataset = json.loads(contents)
    if isinstance(dataset, list):
        out = serializer.serialize_datasets(dataset, _format=format)
    else:
        out = serializer.serialize_dataset(dataset, _format=format)

    output.write(out)


def get_commands():
    return [dcat]
