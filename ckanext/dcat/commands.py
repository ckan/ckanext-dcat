# -*- coding: utf-8 -*-

import logging
from ckan import plugins as p

import ckanext.dcat.utils as utils


class GenerateStaticDCATCommand(p.toolkit.CkanCommand):
    """
    Generates static JSON files containing all datasets.

    The generate command will generate a static file containing all of the
    datasets in the catalog in JSON format.

    paster generate_static json <OUTPUT_FILE> -c <PATH_TO_CONFIG>
    """
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 2
    min_args = 2

    def __init__(self, name):
        super(GenerateStaticDCATCommand, self).__init__(name)

    def command(self):
        self._load_config()
        self.log = logging.getLogger(__name__)

        if len(self.args) != 2:
            self.log.error("You must specify the command and the output file")
            return

        cmd, output = self.args

        if cmd == 'json':
            self.generate(output)
        else:
            self.log.error("Unknown command {0}".format(cmd))

    def generate(self, output):
        """
        Keep reading and converting datasets until we get an empty list back
        from dcat_datasets_list
        """
        with open(output, 'w') as f:
            utils.generate_static_json(f)
