'''
Converts EU RDF descriptions of codelists to ckanext-scheming choices.

<rdf:Description rdf:about="http://data.europa.eu/bna/c_164e0bf5">
	<startDate xmlns="http://publications.europa.eu/ontology/euvoc#" rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2019-07-06</startDate>
	<created xmlns="http://purl.org/dc/terms/" rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2023-09-05</created>
	<modified xmlns="http://purl.org/dc/terms/" rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2023-09-13</modified>
	<rdf:type rdf:resource="http://www.w3.org/2004/02/skos/core#Concept"/>
	<prefLabel xmlns="http://www.w3.org/2004/02/skos/core#" xml:lang="en">Meteorological</prefLabel>
	<prefLabel xmlns="http://www.w3.org/2004/02/skos/core#" xml:lang="es">Meteorología</prefLabel>
	<prefLabel xmlns="http://www.w3.org/2004/02/skos/core#" xml:lang="lv">Meteoroloģijas datu kopas</prefLabel>
	<prefLabel xmlns="http://www.w3.org/2004/02/skos/core#" xml:lang="mt">Data meteoroloġika</prefLabel>
	<prefLabel xmlns="http://www.w3.org/2004/02/skos/core#" xml:lang="nl">Meteorologische data</prefLabel>
	<prefLabel xmlns="http://www.w3.org/2004/02/skos/core#" xml:lang="sv">Meteorologiska data</prefLabel>
        ... 
	<order xmlns="http://publications.europa.eu/ontology/euvoc#" rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">3</order>
	<definition xmlns="http://www.w3.org/2004/02/skos/core#" xml:lang="en">data sets as described in Commission Implementing Regulation (EU) 2023/138 of 21 December 2022 laying down a list of specific high-value datasets and the arrangements for their publication and re-use, Annex, Section 3</definition>
	<inScheme xmlns="http://www.w3.org/2004/02/skos/core#" rdf:resource="http://data.europa.eu/bna/asd487ae75"/>
	<topConceptOf xmlns="http://www.w3.org/2004/02/skos/core#" rdf:resource="http://data.europa.eu/bna/asd487ae75"/>
</rdf:Description>

to:

 {
    "label": {
      "en": "Meteorological",
      "ga": "Meit\u00e9areola\u00edoch",
      "mt": "Data meteorolo\u0121ika"
    },
    "value": "http://data.europa.eu/bna/c_164e0bf5"
  },


These are suitable for inclusion in the schema.json.

'''

import rdflib
import rdflib.parser

from rdflib.namespace import Namespace, RDF, SKOS

from pathlib import Path
import xml
import json
from functools import lru_cache

from ckan.plugins import toolkit

import logging
log = logging.getLogger(__name__)


EUVOC = Namespace("http://publications.europa.eu/ontology/euvoc#")
# filter out variants of languages, en_GB doesn't match en.
LANGS = set(l.split('_')[0] for l in toolkit.aslist(toolkit.config.get('ckan.locales_offered', ['en'])))


class Codelist:
    def __init__(self, choices, scheme):
        self.choices = choices
        self.scheme = scheme
        self.choices_map = {elt['value']:elt['label'] for elt in choices}
        log.debug(LANGS)
    def labels(self, val):
        return self.choices_map.get(val, {})

@lru_cache(None)
def extract(f:Path):

    g = rdflib.ConjunctiveGraph()
    try:
        g.parse(data=f.read_text(), format='xml')
    # Apparently there is no single way of catching exceptions from all
    # rdflib parsers at once, so if you use a new one and the parsing
    # exceptions are not cached, add them here.
    # PluginException indicates that an unknown format was passed.
    except (SyntaxError, xml.sax.SAXParseException,
            rdflib.plugin.PluginException, TypeError) as e:
        raise Exception(e)

    choices = {}

    for subject in g.subjects(RDF.type, SKOS.Concept):
        labels = {l.language: str(l) for l in g.objects(subject, SKOS.prefLabel) if l.language in LANGS }
        try:
            order = list(g.objects(subject, EUVOC.order))[0]
        except KeyError:
            order = str(subject)

        choice = {"label": labels,
                  "value": str(subject)}

        choices[order] = choice

    ordered_choices = [v for k,v in sorted(choices.items())]

    scheme = None
    for subject in g.subjects(RDF.type, SKOS.ConceptScheme):
        scheme = str(subject)
    
    return Codelist(ordered_choices, scheme)


def write_json():
    for path in Path(__file__).parent.glob('*.rdf'):
        data = extract(path)
        dest = path.parent / (path.stem + '.json')
        with open (dest, 'w') as f:
            json.dump(data.choices, f, indent=2)
        

#print(json.dumps(ordered_choices, indent=2))
    
    
    
