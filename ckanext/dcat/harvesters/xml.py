import logging
from hashlib import sha1

from lxml import etree

from ckanext.dcat import converters, formats
from ckanext.dcat.harvesters.base import DCATHarvester

log = logging.getLogger(__name__)


class DCATXMLHarvester(DCATHarvester):

    DCAT_NS = 'http://www.w3.org/ns/dcat#'
    DCT_NS = 'http://purl.org/dc/terms/'
    RDF_NS = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'

    def info(self):
        return {
            'name': 'dcat_xml',
            'title': 'DCAT XML-RDF Harvester',
            'description': 'Harvester for DCAT dataset descriptions ' +
                           'serialized as XML-RDF'
        }

    def _get_guids_and_datasets(self, content):

        doc = etree.fromstring(content)

        for dataset_element in doc.xpath('//dcat:Dataset',
                                         namespaces={'dcat': self.DCAT_NS}):

            as_string = etree.tostring(dataset_element)

            # Get identifier
            guid = dataset_element.get('{{{ns}}}about'.format(ns=self.RDF_NS))
            if not guid:
                id_element = dataset_element.find(
                    '{{{ns}}}identifier'.format(ns=self.DCT_NS))
                if id_element:
                    guid = id_element.strip()
                else:
                    # This is bad, any ideas welcomed
                    guid = sha1(as_string).hexdigest()

            yield guid, as_string

    def _get_package_dict(self, harvest_object):

        content = harvest_object.content

        try:
            dataset = formats.xml.DCATDataset(content)
        except ValueError:
            msg = 'Content does not look like dcat:Dataset for harvest object {0}'.format(harvest_object.id)
            self._save_object_error(msg, harvest_object, 'Import')
            return None, None
        dcat_dict = dataset.read_values()

        package_dict = converters.dcat_to_ckan(dcat_dict)

        return package_dict, dcat_dict
