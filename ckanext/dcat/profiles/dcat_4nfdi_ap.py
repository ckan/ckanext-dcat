import json
from decimal import Decimal, DecimalException

from rdflib import term, URIRef, BNode, Literal, Graph
import ckantoolkit as toolkit

from ckan.lib.munge import munge_tag
import logging
log = logging.getLogger(__name__)

from ckanext.dcat.utils import (
    resource_uri,
    DCAT_EXPOSE_SUBCATALOGS,
    DCAT_CLEAN_TAGS,
    publisher_uri_organization_fallback,
)
from .base import RDFProfile, URIRefOrLiteral, CleanedURIRef
from .base import (
    RDF,
    XSD,
    SKOS,
    RDFS,
    DCAT,
    DCT,
    ADMS,
    VCARD,
    FOAF,
    SCHEMA,
    NFDI,
    CHEMINF, # this
    CHMO, # this
    OBI,
    IAO,
    PROV,
    CHEBI,
    NMR,
    QUDT,
NCIT,
FIX,
    namespaces
)

class DCATNFDi4ChemProfile(RDFProfile):
    """
    An RDF profile extending DCAT-AP for NFDI4Chem

    Extends the EuropeanDCATAPProfile to support NFDI4Chem-specific fields.
    """

    def parse_dataset(self, dataset_dict, dataset_ref):
        dataset_dict['title'] = str(dataset_ref.value(DCT.title))
        dataset_dict['notes'] = str(dataset_ref.value(DCT.description))
        dataset_dict['doi'] = str(dataset_ref.value(DCT.identifier))
        dataset_dict['language'] = [
            str(theme.value(SKOS.prefLabel)) for theme in dataset_ref.objects(DCAT.theme)
        ]
        return dataset_dict


    def graph_from_dataset(self, dataset_dict, dataset_ref):
        g = self.g

        g.bind('dcat', DCAT)
        g.bind('dcterms', DCT)
        g.bind('chebi', CHEBI)
        g.bind('cheminf', CHEMINF)
        g.bind('chmo', CHMO)
        g.bind('prov', PROV)
        g.bind('obi', OBI)
        g.bind('nmr', NMR)
        g.bind('iao', IAO)
        g.bind('qudt', QUDT)
        g.bind('skos', SKOS)
        g.bind('vcard', VCARD)
        g.bind('foaf', FOAF)
        g.bind('nfdi', NFDI)
        g.bind('ncit', NCIT)
        g.bind('fix', FIX)
        g.bind('schema', SCHEMA)

        # Define Dataset
        if dataset_dict.get('doi'):
            dataset_uri = URIRef(dataset_dict.get('doi'))
            g.add((dataset_uri, RDF.type, DCAT.Dataset))
            g.add((dataset_uri, DCT.identifier, Literal(dataset_dict.get('doi'), datatype=URIRef("xsd:anyURI"))))

        else:
            dataset_uri = URIRef(dataset_dict.get('id').strip())
            g.add((dataset_uri, RDF.type, DCAT.Dataset))
            g.add((dataset_uri, DCT.identifier, Literal(dataset_dict.get('id').strip(), datatype=URIRef("xsd:anyURI"))))

        g.add((dataset_uri, DCT.title, Literal(dataset_dict.get('title'))))
        g.add((dataset_uri, DCT.description, Literal(dataset_dict.get('notes'))))
        g.add((dataset_uri, DCT.language, Literal(dataset_dict.get('language'))))
        if dataset_dict.get('url'):
            g.add((dataset_uri, DCT.landingPage, URIRef(dataset_dict.get('url'))))

        g.add((dataset_uri, DCT.issued, Literal(dataset_dict.get('metadata_created'))))
        g.add((dataset_uri, DCT.modified, Literal(dataset_dict.get('metadata_modified'))))

        # Author Information
        contact_node = BNode()
        g.add((dataset_uri, DCAT.contactPoint, contact_node))
        g.add((contact_node, RDF.type, VCARD.Kind))
        g.add((contact_node, VCARD.fn, Literal(dataset_dict.get('author'))))

        # Dataset Theme
        theme_node = BNode()
        g.add((dataset_uri, DCAT.theme, theme_node))
        g.add((theme_node, RDF.type, SKOS.Concept))
        if dataset_dict.get('keyword') is not None:
            g.add((theme_node, SKOS.prefLabel, Literal(dataset_dict.get('keyword'))))

        # wasGeneratedBy Activity
        was_generated_by = BNode()
        g.add((dataset_uri, PROV.wasGeneratedBy, was_generated_by))
        g.add((was_generated_by, RDF.type, CHMO['0000595']))
        g.add((was_generated_by, RDF.type, PROV.Activity))

        # Used Chemical Entity Node (CHEBI)
        used_entity_chem = BNode()
        g.add((was_generated_by, PROV.used, used_entity_chem))
        g.add((used_entity_chem, RDF.type, CHEBI['59999']))
        g.add((used_entity_chem, DCT.identifier, Literal(dataset_dict.get('doi'))))
        g.add((used_entity_chem, DCT.title, Literal(dataset_dict.get('title'))))
        g.add((used_entity_chem, CHEMINF['000059'], Literal(dataset_dict.get('inchi_key'))))  # inchi_key
        g.add((used_entity_chem, CHEMINF['000113'], Literal(dataset_dict.get('inchi'))))  # inchi
        g.add((used_entity_chem, CHEMINF['000018'], Literal(dataset_dict.get('smiles'))))  # smiles
        g.add((used_entity_chem, CHEMINF['000037'], Literal(dataset_dict.get('mol_formula'))))  # mol_formula


        # Used Instrument Entity Node (NMR Instrument)
        used_tool = BNode()
        g.add((was_generated_by, PROV.used, used_tool))
        g.add((used_tool, RDF.type, OBI['0000566']))
        g.add((used_tool,RDF.type, PROV.Entity))

        variable_node = BNode()
        g.add((used_tool, PROV.used, variable_node))

        # Variable Measured
        if dataset_dict.get('variableMeasured',[]):
            variable_measured = dataset_dict.get('variableMeasured', [])

            for vm in variable_measured:
                property_id = vm['variableMeasured_propertyID']
                value = vm['variableMeasured_value']
                variable_name = vm['variableMeasured_name']

                # Split to get namespace
                if ':' in property_id:
                    prefix, identifier = property_id.split(':', 1)
                else:
                    # Handle the case where it's not in the expected format
                    prefix = None
                    identifier = property_id  # or raise an error/log warning

                if prefix == 'NMR':
                    prop_uri = URIRef(NMR['1000330'])
                elif prefix == 'NCIT':
                    prop_uri = URIRef(NCIT[identifier])
                elif prefix == 'FIX':
                    prop_uri = URIRef(FIX[identifier])
                elif prefix == 'CHMO':
                    prop_uri = URIRef(CHMO[identifier])
                elif prefix == 'OBI':
                    prop_uri = URIRef(OBI[identifier])
                else:
                    prop_uri= URIRef(IAO['0000140'])  # Skip unrecognized prefixes

                # Add title before the property
                # if property_id in property_title_map:
                used_entity = BNode()
                g.add((variable_node, DCT.relation, used_entity))

                if variable_name == 'Temperature':
                    g.add((used_entity, RDF.type, QUDT.Quantity))  # Temperature
                    g.add((used_entity, QUDT.hasQuantityKind, URIRef("http://qudt.org/vocab/quantitykind/Temperature")))
                    g.add((used_entity, QUDT.unit, URIRef("https://qudt.org/vocab/unit/K")))
                    g.add((used_entity, QUDT.value, Literal(value)))
                else:
                    g.add((used_entity, RDF.type, PROV.Entity))
                    g.add((used_entity, RDF.type, prop_uri))
                    g.add((used_entity, DCT.title, Literal(variable_name)))
                    g.add((used_entity, PROV.value, Literal(value)))# Create a blank node for Quantity

        return g
