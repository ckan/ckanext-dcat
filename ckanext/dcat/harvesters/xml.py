from ckan import plugins as p


msg = '''
[ckanext-dcat] The XML harvester (dcat_xml_harvester) is DEPRECATED, please use
the generic RDF harvester (dcat_rdf_harvester) instead. Check the following for
more details:
   https://github.com/ckan/ckanext-dcat#xml-dcat-harvester-deprecated
'''


class DCATXMLHarvester(p.SingletonPlugin):

    p.implements(p.IConfigurer, inherit=True)

    def update_config(self, config):

        raise Exception(msg)
