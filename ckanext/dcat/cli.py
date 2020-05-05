# -*- coding: utf-8 -*-

import click
import ckan.plugins.toolkit as tk
import ckanext.dcat.utils as utils

@click.group()
def generate_static():
    """Generates static files containing all datasets.

    """
    pass

@generate_static.command()
@click.argument('output', type=click.File(mode="w"))
def json(output):
    """The generate command will generate a static file containing all of
    the datasets in the catalog in JSON format.

    """
    utils.generate_static_json(output)


def get_commands():
    return [generate_static]
