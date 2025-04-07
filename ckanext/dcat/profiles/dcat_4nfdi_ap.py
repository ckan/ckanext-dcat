import json
from decimal import Decimal, DecimalException

from rdflib import term, URIRef, BNode, Literal, Graph
import ckantoolkit as toolkit

# from ckan.lib.munge import munge_tag
import logging

from ckanext.dcat.profiles.dcat_4c_ap import (Agent,
                        AnalysisDataset,
                        AnalysisSourceData,
                        DataAnalysis,
                        DataCreatingActivity,
                        DefinedTerm,
                        Document,
                        EvaluatedEntity,
                        LinguisticSystem,
                        Standard,
                        QualitativeAttribute)
from . import EuropeanDCATAPProfile, EuropeanDCATAP2Profile

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
    CHEMINF,  # this
    CHMO,  # this
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
from linkml_runtime.dumpers import RDFLibDumper
from linkml_runtime.utils.schemaview import SchemaView


class DCATNFDi4ChemProfile(EuropeanDCATAPProfile):
    """
    An RDF profile extending DCAT-AP for NFDI4Chem

    Extends the EuropeanDCATAPProfile to support NFDI4Chem-specific fields.
    """

    def parse_dataset(self, dataset_dict, dataset_ref):
        # TODO: Create a parser
        dataset_dict['title'] = str(dataset_ref.value(DCT.title))
        dataset_dict['notes'] = str(dataset_ref.value(DCT.description))
        dataset_dict['doi'] = str(dataset_ref.value(DCT.identifier))
        dataset_dict['language'] = [
            str(theme.value(SKOS.prefLabel)) for theme in dataset_ref.objects(DCAT.theme)
        ]
        return dataset_dict

    def graph_from_dataset(self,dataset_dict,dataset_ref):

        # super().graph_from_dataset(dataset_dict, dataset_ref)

        for prefix, namespace in namespaces.items():
            self.g.bind(prefix, namespace)

        # Get the ID of the dataset
        if dataset_dict.get('doi'):
            dataset_uri = 'https://doi.org/' + dataset_dict.get('doi')
            # not a mandatory field, but makes sense to do this here as it's the same value as the node URI
            dataset_id = 'https://doi.org/' + dataset_dict.get('doi')
        else:
            dataset_uri = dataset_dict.get('id').strip()
            dataset_id = dataset_dict.get('id').strip()

        # Instantiate the evaluated sample
        # TODO: We used a fake ID, as the real one is not within the example dataset, but might be in the source data.
        # TODO: Do we need different instantiation steps/conditions based on where the metadata comes from?
        sample = EvaluatedEntity(
            id=dataset_id + '/sample',
            has_qualitative_attribute=[
                QualitativeAttribute(
                    rdf_type=DefinedTerm(
                        id='CHEMINF:000059',
                        title='InChiKey'),
                    title='assigned InChiKey',
                    value=dataset_dict.get('inchi_key')),
                QualitativeAttribute(
                    rdf_type=DefinedTerm(
                        id='CHEMINF:000113',
                        title='InChi'),
                    title='assigned InChi',
                    value=dataset_dict.get('inchi')),
                QualitativeAttribute(
                    rdf_type=DefinedTerm(
                        id='CHEMINF:000018',
                        title='SMILES'),
                    title='assigned SMILES',
                    value=dataset_dict.get('smiles')),
                QualitativeAttribute(
                    rdf_type=DefinedTerm(
                        id='CHEMINF:000037',
                        title='IUPACChemicalFormula'),
                    title='assigned IUPACChemicalFormula',
                    value= dataset_dict.get('mol_formula') )
            ]
        )

        # Instantiate the measurement process/activity
        if dataset_dict.get('measurement_technique_iri'):
            measurement = DataCreatingActivity(
                rdf_type=DefinedTerm(
                    id=dataset_dict.get('measurement_technique_iri'),
                    title=dataset_dict.get('measurement_technique')),
                evaluated_entity=[sample]
            )



        # Instantiate the spectrum that was analysed by the measurement with a fake ID, as it does not have one,
        # but the ID is a mandatory slot for an AnalysisSourceData (which is a EvaluatedEntity)
        # Hardcode the rdf_type, as this is necessary in the domain agnostic version of our DCAT-AP extension
        spectrum = AnalysisSourceData(
            id=dataset_id + '/spectrum',
            rdf_type=DefinedTerm(id='CHMO:0000800',
                                 title='spectrum'),
            was_generated_by=[measurement]
        )

        # Instantiate the analysis of the spectrum
        # Hardcode the rdf_type, as this is necessary in this domain agnostic version of our DCAT-AP extension
        analysis = DataAnalysis(
            rdf_type=DefinedTerm(
                id='http://purl.allotrope.org/ontologies/process#AFP_0003618',
                title='peak identification'),
            evaluated_entity=[spectrum])


# TODO: Empty Values are to be tested, to check if it is NONE or not

        if dataset_dict.get('notes'):
            description = dataset_dict.get('notes')
        else:
            description= 'No description'

        dataset = AnalysisDataset(id=dataset_uri,
                                  title=dataset_dict.get('title'),
                                  description=description,
                                  was_generated_by=analysis,
                                  identifier=dataset_id,
                                  describes_entity={'id': dataset_id + '/sample'},
                                  # using nmrXiv docs just as a dummy example for how we could use this slot
                                  # TODO: Use MICHI PURL once possible
                                  conforms_to=Standard(
                                      identifier='https://docs.nmrxiv.org/submission-guides/data-model/spectra.html')
                                  )

        creators = []
        # Dirty parsing workaround for the above nmrXiv example
        try:
            if dataset_dict.get('author'):
                for creator in dataset_dict.get('author').replace('., ', '.|').split('|'):
                    creators.append(Agent(name=creator))
                    dataset.creator = creators
            else:
                dataset.creator = creators.append(Agent(name='NA'))
        except Exception as e:
            log.error(e)

        #Add language attribute to the dataset
        # TODO: Simplify, once normalization happens in the previous harvesting/parsing step
        if dataset_dict.get('language'):
            if dataset_dict.get('language') == 'english':
                dataset.language.append(LinguisticSystem(language_tag='en'))
            else:
                dataset.language.append(LinguisticSystem(language_tag=dataset_dict.get('language')))

        else:
            dataset.language.append(LinguisticSystem(language_tag='en'))

        # Add landing_page attribute to the dataset
        if dataset_dict.get('url'):
            dataset.landing_page = Document(identifier=dataset_dict.get('url'))

        # Add release_date attribute to the dataset
        dataset.release_date = dataset_dict.get('metadata_created')

        # Add modification_date attribute to the dataset
        dataset.modification_date = dataset_dict.get('metadata_modified')

        schemaview = SchemaView(schema ="/usr/lib/ckan/default/src/ckanext-dcat/ckanext/dcat/schemas/dcat_4c_ap.yaml"
                                )

        rdf_nfdi_dumper = RDFLibDumper()
        # nfdi_graph = rdf_nfdi_dumper.as_rdf_graph(sample, schemaview=schemaview)
        # nfdi_graph += rdf_nfdi_dumper.as_rdf_graph(measurement, schemaview=schemaview)
        # nfdi_graph += rdf_nfdi_dumper.as_rdf_graph(spectrum, schemaview=schemaview)
        # nfdi_graph += rdf_nfdi_dumper.as_rdf_graph(analysis, schemaview=schemaview)
        nfdi_graph = rdf_nfdi_dumper.as_rdf_graph(dataset, schemaview=schemaview)

        for triple in nfdi_graph:
            self.g.add(triple)



########################################################################################################
# Commenting the usable information for further use
        # TODO: add a condition to account for MassBank and other sources not providing this, where we could hardcode,
        #  like in the below Massbank example.
        # elif source == 'Massbank:
        #    measurement = DataCreatingActivity(
        #        rdf_type=DefinedTerm(
        #            id='CHMO:0000470',
        #            title='mass spectrometry,
        #        evaluated_entity=[sample]
        #    )
        # # if dataset_dict.get('notes'):
        # #     description = dataset_dict.get('notes')
        # # else:
        # #     description= 'None'
        # #
        # # # Instantiate the dataset
        # # dataset = AnalysisDataset(id=dataset_uri,
        # #                           title=dataset_dict.get('title'),
        # #                           description=description,
        # #                           was_generated_by=analysis,
        # #                           identifier=dataset_id,
        # #                           describes_entity={'id': dataset_id + '/sample'},
        # #                           # using nmrXiv docs just as a dummy example for how we could use this slot
        # #                           # TODO: Use MICHI PURL once possible
        # #                           conforms_to=Standard(
        # #                               identifier='https://docs.nmrxiv.org/submission-guides/data-model/spectra.html')
        # #                           )
        #
        # # Add language attribute to the dataset
        # # TODO: Simplify, once normalization happens in the previous harvesting/parsing step
        # # if dataset_dict.get('language'):
        # #     if dataset_dict.get('language') == 'english':
        # #         dataset.language.append(LinguisticSystem(language_tag='en'))
        # #     else:
        # #         dataset.language.append(LinguisticSystem(language_tag=dataset_dict.get('language')))
        #
        # # Add landing_page attribute to the dataset
        # # if dataset_dict.get('url'):
        # #     dataset.landing_page = Document(identifier=dataset_dict.get('url'))
        #
        # # Add release_date attribute to the dataset
        # # dataset.release_date = dataset_dict.get('metadata_created')
        #
        # # Add modification_date attribute to the dataset
        # # dataset.modification_date = dataset_dict.get('metadata_modified')
        #
        # # Add creators to the dataset
        # # TODO: Simplify, once normalization happens in the previous harvesting/parsing step
        # # WILL ONLY WORK IF 'author' is a list of authors not all mushed in a string
        # creators = []
        # # Dirty parsing workaround for the above nmrXiv example
        # try:
        #     for creator in dataset_dict.get('author').replace('., ', '.|').split('|'):
        #         creators.append(Agent(name=creator))
        #         dataset.creator = creators
        # except Exception as e:
        #     log.error(e)
        #
        #
        # # TODO: parse the rest of the given dataset attributes, most importantly the measurement variables
        #
        #
        # # rdf_graph = RDFLibDumper().as_rdf_graph(dataset, schemaview=schemaview)
        #
        # schemaview = SchemaView("ckanext/dcat/schemas/dcat_4c_ap.yaml")
        #
        # rdf_nfdi_dumper = RDFLibDumper()
        # nfdi_graph = rdf_nfdi_dumper.as_rdf_graph(sample, schemaview=schemaview)
        # nfdi_graph += rdf_nfdi_dumper.as_rdf_graph(measurement, schemaview=schemaview)
        # nfdi_graph += rdf_nfdi_dumper.as_rdf_graph(spectrum, schemaview=schemaview)
        # nfdi_graph += rdf_nfdi_dumper.as_rdf_graph(analysis, schemaview=schemaview)
        # # nfdi_graph = rdf_nfdi_dumper.as_rdf_graph(dataset, schemaview=schemaview)
        #
        # for triple in nfdi_graph:
        #     self.g.add(triple)


