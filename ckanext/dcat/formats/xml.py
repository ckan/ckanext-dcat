import logging

from lxml import etree

log = logging.getLogger(__name__)


class MappedXmlObject(object):
    elements = []


class MappedXmlDocument(MappedXmlObject):

    base_class = None

    def __init__(self, xml_str=None, xml_tree=None, lang='en'):
        assert (xml_str or xml_tree is not None), 'Must provide some XML in one format or another'
        self.xml_str = xml_str
        self.xml_tree = xml_tree
        self.lang = lang

    def read_values(self):
        '''For all of the elements listed, finds the values of them in the
        XML and returns them.'''
        values = {}
        tree = self.get_xml_tree()
        for element in self.elements:
            values[element.name] = element.read_value(tree, self.lang)
        self.infer_values(values)
        return values

    def read_value(self, name):
        '''For the given element name, find the value in the XML and return
        it.
        '''
        tree = self.get_xml_tree()
        for element in self.elements:
            if element.name == name:
                return element.read_value(tree)
        raise KeyError

    def get_xml_tree(self):
        if self.xml_tree is None:
            parser = etree.XMLParser(remove_blank_text=True)
            if type(self.xml_str) == unicode:
                xml_str = self.xml_str.encode('utf8')
            else:
                xml_str = self.xml_str
            self.xml_tree = etree.fromstring(xml_str, parser=parser)

            if self.base_class and ':' in self.base_class:
                ns = self.base_class.split(':')[0]
                if self.base_class.replace(ns, self.xml_tree.nsmap[ns]) != self.xml_tree.tag:
                    elements = self.xml_tree.xpath(self.base_class, namespaces=self.xml_tree.nsmap)
                    if len(elements):
                        self.xml_tree = elements[0]
                    else:
                        raise ValueError('The provided document does not seem to contain a {0} element'.format(self.base_class))

        return self.xml_tree

    def infer_values(self, values):
        pass


class MappedXmlElement(MappedXmlObject):
    namespaces = {}

    def __init__(self, name, search_paths=[], multiplicity='*', elements=[], multilingual=False):
        self.name = name
        self.search_paths = search_paths
        self.multiplicity = multiplicity
        self.elements = elements or self.elements
        self.multilingual = multilingual

    def read_value(self, tree, lang=None):
        values = []
        for xpath in self.get_search_paths():
            elements = self.get_elements(tree, xpath, lang)
            values = self.get_values(elements)
            if values:
                break
        return self.fix_multiplicity(values)

    def get_search_paths(self):
        if type(self.search_paths) != type([]):
            search_paths = [self.search_paths]
        else:
            search_paths = self.search_paths
        return search_paths

    def get_elements(self, tree, xpath, lang=None):
        if xpath.endswith('/text()') and lang and self.multilingual:
            xpath_lang = xpath.replace('/text()',
                    '[@xml:lang="{0}"]/text()'.format(lang))
            elements = tree.xpath(xpath_lang, namespaces=self.namespaces)
            if elements:
                return elements
        return tree.xpath(xpath, namespaces=self.namespaces)

    def get_values(self, elements):
        values = []
        if len(elements) == 0:
            pass
        else:
            for element in elements:
                value = self.get_value(element)
                values.append(value)
        return values

    def get_value(self, element):
        if self.elements:
            value = {}
            for child in self.elements:
                value[child.name] = child.read_value(element)
            return value
        elif type(element) == etree._ElementStringResult:
            value = str(element)
        elif type(element) == etree._ElementUnicodeResult:
            value = unicode(element)
        else:
            value = self.element_tostring(element)
        return value

    def element_tostring(self, element):
        return etree.tostring(element, pretty_print=False)

    def fix_multiplicity(self, values):
        '''
        When a field contains multiple values, yet the spec says
        it should contain only one, then return just the first value,
        rather than a list.

        In the ISO19115 specification, multiplicity relates to:
        * 'Association Cardinality'
        * 'Obligation/Condition' & 'Maximum Occurence'
        '''
        if self.multiplicity == '0':
            # 0 = None
            if values:
                log.warn('Values found for element "%s" when multiplicity should be 0: %s',  self.name, values)
            return ''
        elif self.multiplicity == '1':
            # 1 = Mandatory, maximum 1 = Exactly one
            if not values:
                log.warn('Value not found for element "%s"' % self.name)
                return ''
            return values[0]
        elif self.multiplicity == '*':
            # * = 0..* = zero or more
            return values
        elif self.multiplicity == '0..1':
            # 0..1 = Mandatory, maximum 1 = optional (zero or one)
            if values:
                return values[0]
            else:
                return ''
        elif self.multiplicity == '1..*':
            # 1..* = one or more
            return values
        else:
            log.warning('Multiplicity not specified for element: %s',
                        self.name)
            return values


class DCATElement(MappedXmlElement):

    namespaces = {
		'time': 'http://www.w3.org/2006/time#',
		'dct': 'http://purl.org/dc/terms/',
		'dc': 'http://purl.org/dc/elements/1.1/',
		'dcat': 'http://www.w3.org/ns/dcat#',
		'foaf': 'http://xmlns.com/foaf/0.1/',
		'xsd': 'http://www.w3.org/2001/XMLSchema#',
		'tema': 'http://datos.gob.es/kos/sector-publico/sector/',
		'auto': 'http://datos.gob.es/recurso/sector-publico/territorio/Autonomia/',
		'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
		'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    }

class DCATDistribution(DCATElement):

    elements = [
        DCATElement(
            name='title',
            search_paths=[
                'dct:title/text()'
            ],
            multiplicity='0..1',
            multilingual=True,
        ),
        DCATElement(
            name='description',
            search_paths=[
                'dct:description/text()'
            ],
            multiplicity='0..1',
            multilingual=True,
        ),
        DCATElement(
            name='issued',
            search_paths=[
                'dct:issued/text()'
            ],
            multiplicity='0..1',
        ),
        DCATElement(
            name='modified',
            search_paths=[
                'dct:modified/text()'
            ],
            multiplicity='0..1',
        ),
        DCATElement(
            name='license',
            search_paths=[
                'dct:license/text()',
                'dct:license/@rdf:resource'
            ],
            multiplicity='0..1',
        ),
        DCATElement(
            name='accessURL',
            search_paths=[
                'dcat:accessURL/text()'
            ],
            multiplicity='0..1',
        ),
        DCATElement(
            name='downloadURL',
            search_paths=[
                'dcat:downloadURL/text()'
            ],
            multiplicity='0..1',
        ),
        DCATElement(
            name='byteSize',
            search_paths=[
                'dcat:byteSize/text()'
            ],
            multiplicity='0..1',
        ),
        DCATElement(
            name='format',
            search_paths=[
                'dcat:mediaType/text()',
                'dct:format/dct:IMT/rdf:value/text()',
                'dct:format/text()'
            ],
            multiplicity='0..1',
        ),

    ]


_dcat_publisher = DCATElement(
    name='publisher',
    search_paths=[
        'dct:publisher/foaf:Organization/foaf:name/text()',
        'dct:publisher/foaf:Person/foaf:name/text()',
        'dct:publisher/text()',
        'dct:publisher/@rdf:about',
    ],
    multiplicity='0..1'
)



'''
    TODO:
        * dct:accrualPeriodicity (dct:Frequency, how do you encode those?)
        * dct:spatial
        * dct:temporal
        * dcat:theme
'''
_dcat_dataset_elements = [
    DCATElement(
        name='title',
        search_paths=[
            'dct:title/text()'
        ],
        multiplicity='0..1',
        multilingual=True,
    ),
    DCATElement(
        name='description',
        search_paths=[
            'dct:description/text()'
        ],
        multiplicity='0..1',
        multilingual=True,
    ),
    DCATElement(
        name='issued',
        search_paths=[
            'dct:issued/text()'
        ],
        multiplicity='0..1',
    ),
    DCATElement(
        name='modified',
        search_paths=[
            'dct:modified/text()'
        ],
        multiplicity='0..1',
    ),
    DCATElement(
        name='language',
        search_paths=[
            'dc:language/text()'
        ],
        multiplicity='*',
    ),
    DCATElement(
        name='identifier',
        search_paths=[
            '@rdf:about',
            'dct:identifier/text()'
        ],
        multiplicity='0..1',
    ),
    DCATElement(
        name='keyword',
        search_paths=[
            'dcat:keyword/text()'
        ],
        multiplicity='*',
        multilingual=True,
    ),
    DCATElement(
        name='landingPage',
        search_paths=[
            'dcat:landingPage/text()'
        ],
        multiplicity='0..1',
    ),
    _dcat_publisher,
    DCATDistribution(
        name="distribution",
        search_paths=[
            'dcat:distribution/dcat:Distribution'
        ],
        multiplicity='*',
    )

]


class _DCATDataset(DCATElement):

    elements = _dcat_dataset_elements


class DCATDataset(MappedXmlDocument):

    base_class = 'dcat:Dataset'

    elements = _dcat_dataset_elements


class DCATCatalog(MappedXmlDocument):
    '''
        TODO:
            * dct:accrualPeriodicity (dct:Frequency, how do you encode those?)
            * dct:spatial
            * dcat:theme
    '''

    base_class = 'dcat:Catalog'

    elements = [
        DCATElement(
            name='title',
            search_paths=[
                'dct:title/text()'
            ],
            multiplicity='0..1',
            multilingual=True,
        ),
        DCATElement(
            name='description',
            search_paths=[
                'dct:description/text()'
            ],
            multiplicity='0..1',
            multilingual=True,
        ),
        DCATElement(
            name='issued',
            search_paths=[
                'dct:issued/text()'
            ],
            multiplicity='0..1',
        ),
        DCATElement(
            name='modified',
            search_paths=[
                'dct:modified/text()'
            ],
            multiplicity='0..1',
        ),
        DCATElement(
            name='license',
            search_paths=[
                'dct:license/text()',
                'dct:license/@rdf:resource'
            ],
            multiplicity='0..1',
        ),
        DCATElement(
            name='language',
            search_paths=[
                'dc:language/text()'
            ],
            multiplicity='0..1',
        ),
        DCATElement(
            name='homepage',
            search_paths=[
                'foaf:homepage/text()'
            ],
            multiplicity='0..1',
        ),
        _dcat_publisher,
        _DCATDataset(
            name="dataset",
            search_paths=[
                'dcat:dataset/dcat:Dataset'
            ],
            multiplicity='*',
        )

    ]
