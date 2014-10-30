import json
import logging
from hashlib import sha1

from ckanext.dcat import converters
from ckanext.dcat.harvesters.base import DCATHarvester

log = logging.getLogger(__name__)


class DCATJSONHarvester(DCATHarvester):

    def info(self):
        return {
            'name': 'dcat_json',
            'title': 'DCAT JSON Harvester',
            'description': 'Harvester for DCAT dataset descriptions ' +
                           'serialized as JSON'
        }

    def _get_guids_and_datasets(self, content):

        doc = json.loads(content)

        if isinstance(doc, list):
            # Assume a list of datasets
            datasets = doc
        elif isinstance(doc, dict):
            datasets = doc.get('dataset', [])
        else:
            raise ValueError('Wrong JSON object')

        for dataset in datasets:

            as_string = json.dumps(dataset)

            # Get identifier
            guid = dataset.get('identifier')
            if not guid:
                # This is bad, any ideas welcomed
                guid = sha1(as_string).hexdigest()

            yield guid, as_string

    def _get_package_dict(self, harvest_object):

        content = harvest_object.content

        dcat_dict = json.loads(content)

        package_dict = converters.dcat_to_ckan(dcat_dict)

        return package_dict, dcat_dict
