# Auto generated from dcat_4c_ap.yaml by pythongen.py version: 0.0.1
# Generation date: 2025-03-24T12:33:35
# Schema: dcat-4C-ap
#
# id: https://stroemphi.github.io/dcat-4C-ap/dcat_4c_ap.yaml
# description: This is an extension of the DCAT Application Profile in LinkML. It is intended to be used by NFDI4Chem & NFDI4Cat as a core that can further be extended in profiles to provide domain specific metadata for a dataset.
# license: CC-BY 4.0
import logging
log = logging.getLogger(__name__)
import dataclasses
import re
from dataclasses import dataclass
from datetime import (
    date,
    datetime,
    time
)
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Optional,
    Union
)

from jsonasobj2 import (
    JsonObj,
    as_dict
)
from linkml_runtime.linkml_model.meta import (
    EnumDefinition,
    PermissibleValue,
    PvFormulaOptions
)
from linkml_runtime.utils.curienamespace import CurieNamespace
from linkml_runtime.utils.dataclass_extensions_376 import dataclasses_init_fn_with_kwargs
from linkml_runtime.utils.enumerations import EnumDefinitionImpl
from linkml_runtime.utils.formatutils import (
    camelcase,
    sfx,
    underscore
)
from linkml_runtime.utils.metamodelcore import (
    bnode,
    empty_dict,
    empty_list
)
from linkml_runtime.utils.slot import Slot
from linkml_runtime.utils.yamlutils import (
    YAMLRoot,
    extended_float,
    extended_int,
    extended_str
)
from rdflib import (
    Namespace,
    URIRef
)

from linkml_runtime.linkml_model.types import Decimal, Float, String, Uri, Uriorcurie
from linkml_runtime.utils.metamodelcore import Decimal, URI, URIorCURIE

metamodel_version = "1.7.0"
version = None

# Overwrite dataclasses _init_fn to add **kwargs in __init__
dataclasses._init_fn = dataclasses_init_fn_with_kwargs

# Namespaces
BFO = CurieNamespace('BFO', 'http://purl.obolibrary.org/obo/BFO_')
CHEBI = CurieNamespace('CHEBI', 'http://purl.obolibrary.org/obo/CHEBI_')
CHEMINF = CurieNamespace('CHEMINF', 'http://semanticscience.org/resource/CHEMINF_')
CHMO = CurieNamespace('CHMO', 'http://purl.obolibrary.org/obo/CHMO_')
FOODON = CurieNamespace('FOODON', 'http://purl.obolibrary.org/obo/FOODON_')
IAO = CurieNamespace('IAO', 'http://purl.obolibrary.org/obo/IAO_')
NCIT = CurieNamespace('NCIT', 'http://purl.obolibrary.org/obo/NCIT_')
NMR = CurieNamespace('NMR', 'http://nmrML.org/nmrCV#NMR:')
OBI = CurieNamespace('OBI', 'http://purl.obolibrary.org/obo/OBI_')
PATO = CurieNamespace('PATO', 'http://purl.obolibrary.org/obo/PATO_')
RO = CurieNamespace('RO', 'http://purl.obolibrary.org/obo/RO_')
RXNO = CurieNamespace('RXNO', 'http://purl.obolibrary.org/obo/RXNO_')
SIO = CurieNamespace('SIO', 'http://semanticscience.org/resource/SIO_')
T4FS = CurieNamespace('T4FS', 'http://purl.obolibrary.org/obo/T4FS_')
ADMS = CurieNamespace('adms', 'http://www.w3.org/ns/adms#')
BIOLINK = CurieNamespace('biolink', 'https://w3id.org/biolink/vocab/')
DCAT = CurieNamespace('dcat', 'http://www.w3.org/ns/dcat#')
DCATAP = CurieNamespace('dcatap', 'http://data.europa.eu/r5r/')
DCTERMS = CurieNamespace('dcterms', 'http://purl.org/dc/terms/')
DOI = CurieNamespace('doi', 'https://doi.org/')
ELI = CurieNamespace('eli', 'http://data.europa.eu/eli/ontology#')
EX = CurieNamespace('ex', 'http://example.org/')
FOAF = CurieNamespace('foaf', 'http://xmlns.com/foaf/0.1/')
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
LINKMLDCATAP = CurieNamespace('linkmldcatap', 'https://stroemphi.github.io/dcat-4C-ap/dcat_ap_linkml/')
LOCN = CurieNamespace('locn', 'http://www.w3.org/ns/locn#')
NFDI = CurieNamespace('nfdi', 'https://stroemphi.github.io/dcat-4C-ap/dcat_4nfdi_ap/')
NFDI4C = CurieNamespace('nfdi4c', 'https://stroemphi.github.io/dcat-4C-ap/dcat_4c_ap/')
NMR_SPECTROSCOPY = CurieNamespace('nmr_spectroscopy', 'https://stroemphi.github.io/dcat-4C-ap/nmr_spectroscopy.yaml')
ODRL = CurieNamespace('odrl', 'http://www.w3.org/ns/odrl/2/')
OWL = CurieNamespace('owl', 'http://www.w3.org/2002/07/owl#')
PROV = CurieNamespace('prov', 'http://www.w3.org/ns/prov#')
QUDT = CurieNamespace('qudt', 'http://qudt.org/schema/qudt/')
RDF = CurieNamespace('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
RDFS = CurieNamespace('rdfs', 'http://www.w3.org/2000/01/rdf-schema#')
SCHEMA = CurieNamespace('schema', 'http://schema.org/')
SKOS = CurieNamespace('skos', 'http://www.w3.org/2004/02/skos/core#')
SOSA = CurieNamespace('sosa', 'http://www.w3.org/ns/sosa/')
SPDX = CurieNamespace('spdx', 'http://spdx.org/rdf/terms#')
TIME = CurieNamespace('time', 'http://www.w3.org/2006/time#')
VCARD = CurieNamespace('vcard', 'http://www.w3.org/2006/vcard/ns#')
XSD = CurieNamespace('xsd', 'http://www.w3.org/2001/XMLSchema#')
DEFAULT_ = NFDI4C


# Types
class Duration(str):
    """ The datatype that represents durations of time. """
    type_class_uri = XSD["duration"]
    type_class_curie = "xsd:duration"
    type_name = "duration"
    type_model_uri = NFDI4C.Duration


class HexBinary(str):
    """ The datatype that represents arbitrary hex-encoded binary data. """
    type_class_uri = XSD["hexBinary"]
    type_class_curie = "xsd:hexBinary"
    type_name = "hexBinary"
    type_model_uri = NFDI4C.HexBinary


class NonNegativeInteger(int):
    """ The datatype that represents non-negative integers. """
    type_class_uri = XSD["nonNegativeInteger"]
    type_class_curie = "xsd:nonNegativeInteger"
    type_name = "nonNegativeInteger"
    type_model_uri = NFDI4C.NonNegativeInteger


# Class references
class DefinedTermId(URIorCURIE):
    pass


class EvaluatedEntityId(URIorCURIE):
    pass


class MaterialSampleId(EvaluatedEntityId):
    pass


class ChemicalSampleId(MaterialSampleId):
    pass


class AnalysisSourceDataId(EvaluatedEntityId):
    pass


class NMRSpectrumId(AnalysisSourceDataId):
    pass


class EvaluatedActivityId(URIorCURIE):
    pass


class ChemicalReactionId(EvaluatedActivityId):
    pass


class ResearchCatalogId(URIorCURIE):
    pass


class ResearchDatasetId(URIorCURIE):
    pass


class AnalysisDatasetId(ResearchDatasetId):
    pass


class NMRAnalysisDatasetId(AnalysisDatasetId):
    pass


@dataclass(repr=False)
class ChemicalSubstance(YAMLRoot):
    """
    A portion of matter of constant composition, composed of molecular entities of the same type or of different types
    that is being evaluated in a scientific process.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = CHEBI["59999"]
    class_class_curie: ClassVar[str] = "CHEBI:59999"
    class_name: ClassVar[str] = "ChemicalSubstance"
    class_model_uri: ClassVar[URIRef] = NFDI4C.ChemicalSubstance

    composed_of: Optional[Union[Union[dict, "ChemicalEntity"], List[Union[dict, "ChemicalEntity"]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if not isinstance(self.composed_of, list):
            self.composed_of = [self.composed_of] if self.composed_of is not None else []
        self.composed_of = [v if isinstance(v, ChemicalEntity) else ChemicalEntity(**as_dict(v)) for v in self.composed_of]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ChemicalEntity(YAMLRoot):
    """
    Any constitutionally or isotopically distinct atom, molecule, ion, ion pair, radical, radical ion, complex,
    conformer etc., identifiable as a separately distinguishable entity.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = CHEBI["23367"]
    class_class_curie: ClassVar[str] = "CHEBI:23367"
    class_name: ClassVar[str] = "ChemicalEntity"
    class_model_uri: ClassVar[URIRef] = NFDI4C.ChemicalEntity

    inchi: Optional[Union[dict, "InChi"]] = None
    inchikey: Optional[Union[dict, "InChIKey"]] = None
    smiles: Optional[Union[dict, "SMILES"]] = None
    iupac_formula: Optional[Union[dict, "IUPACChemicalFormula"]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.inchi is not None and not isinstance(self.inchi, InChi):
            self.inchi = InChi(**as_dict(self.inchi))

        if self.inchikey is not None and not isinstance(self.inchikey, InChIKey):
            self.inchikey = InChIKey(**as_dict(self.inchikey))

        if self.smiles is not None and not isinstance(self.smiles, SMILES):
            self.smiles = SMILES(**as_dict(self.smiles))

        if self.iupac_formula is not None and not isinstance(self.iupac_formula, IUPACChemicalFormula):
            self.iupac_formula = IUPACChemicalFormula(**as_dict(self.iupac_formula))

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Solvent(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = SIO["010417"]
    class_class_curie: ClassVar[str] = "SIO:010417"
    class_name: ClassVar[str] = "Solvent"
    class_model_uri: ClassVar[URIRef] = NFDI4C.Solvent

    composed_of: Optional[Union[Union[dict, ChemicalEntity], List[Union[dict, ChemicalEntity]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if not isinstance(self.composed_of, list):
            self.composed_of = [self.composed_of] if self.composed_of is not None else []
        self.composed_of = [v if isinstance(v, ChemicalEntity) else ChemicalEntity(**as_dict(v)) for v in self.composed_of]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ClassifierMixin(YAMLRoot):
    """
    A mixin with which an entity of this schema can be classified via an additional rdf:type assertion.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = NFDI["ClassifierMixin"]
    class_class_curie: ClassVar[str] = "nfdi:ClassifierMixin"
    class_name: ClassVar[str] = "ClassifierMixin"
    class_model_uri: ClassVar[URIRef] = NFDI4C.ClassifierMixin

    type: Optional[Union[dict, "DefinedTerm"]] = None
    rdf_type: Optional[Union[dict, "DefinedTerm"]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.type is not None and not isinstance(self.type, DefinedTerm):
            self.type = DefinedTerm(**as_dict(self.type))

        if self.rdf_type is not None and not isinstance(self.rdf_type, DefinedTerm):
            self.rdf_type = DefinedTerm(**as_dict(self.rdf_type))

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class DefinedTerm(YAMLRoot):
    """
    A word, name, acronym, phrase that is defined in a controlled vocabulary (CV) and that is used to provide an
    additional rdf:type or dcterms:type of a class within this schema.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = SCHEMA["DefinedTerm"]
    class_class_curie: ClassVar[str] = "schema:DefinedTerm"
    class_name: ClassVar[str] = "DefinedTerm"
    class_model_uri: ClassVar[URIRef] = NFDI4C.DefinedTerm

    id: Union[str, DefinedTermId] = None
    title: Optional[str] = None
    from_CV: Optional[Union[str, URIorCURIE]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, DefinedTermId):
            self.id = DefinedTermId(self.id)

        if self.title is not None and not isinstance(self.title, str):
            self.title = str(self.title)

        if self.from_CV is not None and not isinstance(self.from_CV, URIorCURIE):
            self.from_CV = URIorCURIE(self.from_CV)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class EvaluatedEntity(YAMLRoot):
    """
    A physical, digital, conceptual, or other kind of thing with some fixed aspects that is not an activity or process
    and that is being evaluated in a DataCreatingActivity.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = PROV["Entity"]
    class_class_curie: ClassVar[str] = "prov:Entity"
    class_name: ClassVar[str] = "EvaluatedEntity"
    class_model_uri: ClassVar[URIRef] = NFDI4C.EvaluatedEntity

    id: Union[str, EvaluatedEntityId] = None
    title: Optional[str] = None
    description: Optional[str] = None
    other_identifier: Optional[Union[Union[dict, "Identifier"], List[Union[dict, "Identifier"]]]] = empty_list()
    has_qualitative_attribute: Optional[Union[Union[dict, "QualitativeAttribute"], List[Union[dict, "QualitativeAttribute"]]]] = empty_list()
    has_quantitative_attribute: Optional[Union[Union[dict, "QuantitativeAttribute"], List[Union[dict, "QuantitativeAttribute"]]]] = empty_list()
    has_part: Optional[Union[str, EvaluatedEntityId]] = None
    was_generated_by: Optional[Union[Union[dict, "Activity"], List[Union[dict, "Activity"]]]] = empty_list()
    type: Optional[Union[dict, DefinedTerm]] = None
    rdf_type: Optional[Union[dict, DefinedTerm]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, EvaluatedEntityId):
            self.id = EvaluatedEntityId(self.id)

        if self.title is not None and not isinstance(self.title, str):
            self.title = str(self.title)

        if self.description is not None and not isinstance(self.description, str):
            self.description = str(self.description)

        if not isinstance(self.other_identifier, list):
            self.other_identifier = [self.other_identifier] if self.other_identifier is not None else []
        self.other_identifier = [v if isinstance(v, Identifier) else Identifier(**as_dict(v)) for v in self.other_identifier]

        if not isinstance(self.has_qualitative_attribute, list):
            self.has_qualitative_attribute = [self.has_qualitative_attribute] if self.has_qualitative_attribute is not None else []
        self.has_qualitative_attribute = [v if isinstance(v, QualitativeAttribute) else QualitativeAttribute(**as_dict(v)) for v in self.has_qualitative_attribute]

        if not isinstance(self.has_quantitative_attribute, list):
            self.has_quantitative_attribute = [self.has_quantitative_attribute] if self.has_quantitative_attribute is not None else []
        self.has_quantitative_attribute = [v if isinstance(v, QuantitativeAttribute) else QuantitativeAttribute(**as_dict(v)) for v in self.has_quantitative_attribute]

        if self.has_part is not None and not isinstance(self.has_part, EvaluatedEntityId):
            self.has_part = EvaluatedEntityId(self.has_part)

        if not isinstance(self.was_generated_by, list):
            self.was_generated_by = [self.was_generated_by] if self.was_generated_by is not None else []
        self.was_generated_by = [v if isinstance(v, Activity) else Activity(**as_dict(v)) for v in self.was_generated_by]

        if self.type is not None and not isinstance(self.type, DefinedTerm):
            self.type = DefinedTerm(**as_dict(self.type))

        if self.rdf_type is not None and not isinstance(self.rdf_type, DefinedTerm):
            self.rdf_type = DefinedTerm(**as_dict(self.rdf_type))

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class MaterialSample(EvaluatedEntity):
    """
    A material entity that has the role of being a sample within a research activity.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = OBI["0000747"]
    class_class_curie: ClassVar[str] = "OBI:0000747"
    class_name: ClassVar[str] = "MaterialSample"
    class_model_uri: ClassVar[URIRef] = NFDI4C.MaterialSample

    id: Union[str, MaterialSampleId] = None
    has_mass: Optional[Union[dict, "Mass"]] = None
    has_volume: Optional[Union[dict, "Volume"]] = None
    has_length: Optional[Union[dict, "Length"]] = None
    has_width: Optional[Union[dict, "Width"]] = None
    has_height: Optional[Union[dict, "Height"]] = None
    has_surface_area: Optional[Union[dict, "SurfaceArea"]] = None
    was_derived_from: Optional[Union[str, MaterialSampleId]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, MaterialSampleId):
            self.id = MaterialSampleId(self.id)

        if self.has_mass is not None and not isinstance(self.has_mass, Mass):
            self.has_mass = Mass(**as_dict(self.has_mass))

        if self.has_volume is not None and not isinstance(self.has_volume, Volume):
            self.has_volume = Volume(**as_dict(self.has_volume))

        if self.has_length is not None and not isinstance(self.has_length, Length):
            self.has_length = Length(**as_dict(self.has_length))

        if self.has_width is not None and not isinstance(self.has_width, Width):
            self.has_width = Width(**as_dict(self.has_width))

        if self.has_height is not None and not isinstance(self.has_height, Height):
            self.has_height = Height(**as_dict(self.has_height))

        if self.has_surface_area is not None and not isinstance(self.has_surface_area, SurfaceArea):
            self.has_surface_area = SurfaceArea(**as_dict(self.has_surface_area))

        if self.was_derived_from is not None and not isinstance(self.was_derived_from, MaterialSampleId):
            self.was_derived_from = MaterialSampleId(self.was_derived_from)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ChemicalSample(MaterialSample):
    """
    A chemical substance that is being evaluated within a DataCreatingActivity.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = CHEBI["59999"]
    class_class_curie: ClassVar[str] = "CHEBI:59999"
    class_name: ClassVar[str] = "ChemicalSample"
    class_model_uri: ClassVar[URIRef] = NFDI4C.ChemicalSample

    id: Union[str, ChemicalSampleId] = None
    composed_of: Optional[Union[Union[dict, ChemicalEntity], List[Union[dict, ChemicalEntity]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, ChemicalSampleId):
            self.id = ChemicalSampleId(self.id)

        if not isinstance(self.composed_of, list):
            self.composed_of = [self.composed_of] if self.composed_of is not None else []
        self.composed_of = [v if isinstance(v, ChemicalEntity) else ChemicalEntity(**as_dict(v)) for v in self.composed_of]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class AnalysisSourceData(EvaluatedEntity):
    """
    Information that was evaluated within a DataAnalysis.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = PROV["Entity"]
    class_class_curie: ClassVar[str] = "prov:Entity"
    class_name: ClassVar[str] = "AnalysisSourceData"
    class_model_uri: ClassVar[URIRef] = NFDI4C.AnalysisSourceData

    id: Union[str, AnalysisSourceDataId] = None
    was_generated_by: Optional[Union[Union[dict, "DataCreatingActivity"], List[Union[dict, "DataCreatingActivity"]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, AnalysisSourceDataId):
            self.id = AnalysisSourceDataId(self.id)

        if not isinstance(self.was_generated_by, list):
            self.was_generated_by = [self.was_generated_by] if self.was_generated_by is not None else []
        self.was_generated_by = [v if isinstance(v, DataCreatingActivity) else DataCreatingActivity(**as_dict(v)) for v in self.was_generated_by]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class NMRSpectrum(AnalysisSourceData):
    """
    A set of chemical shifts obtained via NMR spectroscopy.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = NMR["1002007"]
    class_class_curie: ClassVar[str] = "NMR:1002007"
    class_name: ClassVar[str] = "NMRSpectrum"
    class_model_uri: ClassVar[URIRef] = NFDI4C.NMRSpectrum

    id: Union[str, NMRSpectrumId] = None
    was_generated_by: Optional[Union[Union[dict, "NMRSpectroscopy"], List[Union[dict, "NMRSpectroscopy"]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, NMRSpectrumId):
            self.id = NMRSpectrumId(self.id)

        if not isinstance(self.was_generated_by, list):
            self.was_generated_by = [self.was_generated_by] if self.was_generated_by is not None else []
        self.was_generated_by = [v if isinstance(v, NMRSpectroscopy) else NMRSpectroscopy(**as_dict(v)) for v in self.was_generated_by]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Tool(YAMLRoot):
    """
    A entity with a certain function used within a DataCreatingActivity.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = PROV["Entity"]
    class_class_curie: ClassVar[str] = "prov:Entity"
    class_name: ClassVar[str] = "Tool"
    class_model_uri: ClassVar[URIRef] = NFDI4C.Tool

    title: Optional[str] = None
    description: Optional[str] = None
    other_identifier: Optional[Union[Union[dict, "Identifier"], List[Union[dict, "Identifier"]]]] = empty_list()
    has_qualitative_attribute: Optional[Union[Union[dict, "QualitativeAttribute"], List[Union[dict, "QualitativeAttribute"]]]] = empty_list()
    has_quantitative_attribute: Optional[Union[Union[dict, "QuantitativeAttribute"], List[Union[dict, "QuantitativeAttribute"]]]] = empty_list()
    has_part: Optional[Union[Union[dict, "Tool"], List[Union[dict, "Tool"]]]] = empty_list()
    type: Optional[Union[dict, DefinedTerm]] = None
    rdf_type: Optional[Union[dict, DefinedTerm]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.title is not None and not isinstance(self.title, str):
            self.title = str(self.title)

        if self.description is not None and not isinstance(self.description, str):
            self.description = str(self.description)

        if not isinstance(self.other_identifier, list):
            self.other_identifier = [self.other_identifier] if self.other_identifier is not None else []
        self.other_identifier = [v if isinstance(v, Identifier) else Identifier(**as_dict(v)) for v in self.other_identifier]

        if not isinstance(self.has_qualitative_attribute, list):
            self.has_qualitative_attribute = [self.has_qualitative_attribute] if self.has_qualitative_attribute is not None else []
        self.has_qualitative_attribute = [v if isinstance(v, QualitativeAttribute) else QualitativeAttribute(**as_dict(v)) for v in self.has_qualitative_attribute]

        if not isinstance(self.has_quantitative_attribute, list):
            self.has_quantitative_attribute = [self.has_quantitative_attribute] if self.has_quantitative_attribute is not None else []
        self.has_quantitative_attribute = [v if isinstance(v, QuantitativeAttribute) else QuantitativeAttribute(**as_dict(v)) for v in self.has_quantitative_attribute]

        if not isinstance(self.has_part, list):
            self.has_part = [self.has_part] if self.has_part is not None else []
        self.has_part = [v if isinstance(v, Tool) else Tool(**as_dict(v)) for v in self.has_part]

        if self.type is not None and not isinstance(self.type, DefinedTerm):
            self.type = DefinedTerm(**as_dict(self.type))

        if self.rdf_type is not None and not isinstance(self.rdf_type, DefinedTerm):
            self.rdf_type = DefinedTerm(**as_dict(self.rdf_type))

        super().__post_init__(**kwargs)


class HardwareTool(Tool):
    """
    A hardware device with a certain function that was used within a DataCreatingActivity.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = NFDI["HardwareTool"]
    class_class_curie: ClassVar[str] = "nfdi:HardwareTool"
    class_name: ClassVar[str] = "HardwareTool"
    class_model_uri: ClassVar[URIRef] = NFDI4C.HardwareTool


class SoftwareTool(Tool):
    """
    A software program with a certain function that was used within a DataCreatingActivity.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = NFDI["SoftwareTool"]
    class_class_curie: ClassVar[str] = "nfdi:SoftwareTool"
    class_name: ClassVar[str] = "SoftwareTool"
    class_model_uri: ClassVar[URIRef] = NFDI4C.SoftwareTool


@dataclass(repr=False)
class Environment(YAMLRoot):
    """
    The surrounding in which the dataset creating activity took place (e.g. a lab).
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = PROV["Entity"]
    class_class_curie: ClassVar[str] = "prov:Entity"
    class_name: ClassVar[str] = "Environment"
    class_model_uri: ClassVar[URIRef] = NFDI4C.Environment

    title: Optional[str] = None
    description: Optional[str] = None
    other_identifier: Optional[Union[Union[dict, "Identifier"], List[Union[dict, "Identifier"]]]] = empty_list()
    type: Optional[Union[dict, DefinedTerm]] = None
    rdf_type: Optional[Union[dict, DefinedTerm]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.title is not None and not isinstance(self.title, str):
            self.title = str(self.title)

        if self.description is not None and not isinstance(self.description, str):
            self.description = str(self.description)

        if not isinstance(self.other_identifier, list):
            self.other_identifier = [self.other_identifier] if self.other_identifier is not None else []
        self.other_identifier = [v if isinstance(v, Identifier) else Identifier(**as_dict(v)) for v in self.other_identifier]

        if self.type is not None and not isinstance(self.type, DefinedTerm):
            self.type = DefinedTerm(**as_dict(self.type))

        if self.rdf_type is not None and not isinstance(self.rdf_type, DefinedTerm):
            self.rdf_type = DefinedTerm(**as_dict(self.rdf_type))

        super().__post_init__(**kwargs)


class Laboratory(Environment):
    """
    A facility that provides controlled conditions in which scientific or technological research, experiments, and
    measurement may be performed.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = PROV["Entity"]
    class_class_curie: ClassVar[str] = "prov:Entity"
    class_name: ClassVar[str] = "Laboratory"
    class_model_uri: ClassVar[URIRef] = NFDI4C.Laboratory


@dataclass(repr=False)
class Plan(YAMLRoot):
    """
    A piece of information that specifies how an activity has to be carried out by its agents including what kind of
    steps have to be taken and what kind of parameters have to be met/set.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = PROV["Entity"]
    class_class_curie: ClassVar[str] = "prov:Entity"
    class_name: ClassVar[str] = "Plan"
    class_model_uri: ClassVar[URIRef] = NFDI4C.Plan

    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[Union[dict, DefinedTerm]] = None
    rdf_type: Optional[Union[dict, DefinedTerm]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.title is not None and not isinstance(self.title, str):
            self.title = str(self.title)

        if self.description is not None and not isinstance(self.description, str):
            self.description = str(self.description)

        if self.type is not None and not isinstance(self.type, DefinedTerm):
            self.type = DefinedTerm(**as_dict(self.type))

        if self.rdf_type is not None and not isinstance(self.rdf_type, DefinedTerm):
            self.rdf_type = DefinedTerm(**as_dict(self.rdf_type))

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class QualitativeAttribute(YAMLRoot):
    """
    A piece of information that is attributed to an entity of interest, tool or environment.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = PROV["Entity"]
    class_class_curie: ClassVar[str] = "prov:Entity"
    class_name: ClassVar[str] = "QualitativeAttribute"
    class_model_uri: ClassVar[URIRef] = NFDI4C.QualitativeAttribute

    value: str = None
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[Union[dict, DefinedTerm]] = None
    rdf_type: Optional[Union[dict, DefinedTerm]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.value):
            self.MissingRequiredField("value")
        if not isinstance(self.value, str):
            self.value = str(self.value)

        if self.title is not None and not isinstance(self.title, str):
            self.title = str(self.title)

        if self.description is not None and not isinstance(self.description, str):
            self.description = str(self.description)

        if self.type is not None and not isinstance(self.type, DefinedTerm):
            self.type = DefinedTerm(**as_dict(self.type))

        if self.rdf_type is not None and not isinstance(self.rdf_type, DefinedTerm):
            self.rdf_type = DefinedTerm(**as_dict(self.rdf_type))

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class InChIKey(QualitativeAttribute):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = CHEMINF["000059"]
    class_class_curie: ClassVar[str] = "CHEMINF:000059"
    class_name: ClassVar[str] = "InChIKey"
    class_model_uri: ClassVar[URIRef] = NFDI4C.InChIKey

    value: str = None

@dataclass(repr=False)
class InChi(QualitativeAttribute):
    """
    A structure descriptor which conforms to the InChI format specification.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = CHEMINF["000113"]
    class_class_curie: ClassVar[str] = "CHEMINF:000113"
    class_name: ClassVar[str] = "InChi"
    class_model_uri: ClassVar[URIRef] = NFDI4C.InChi

    value: str = None

@dataclass(repr=False)
class IUPACChemicalFormula(QualitativeAttribute):
    """
    A systematic name which is formulated according to the rules and recommendations for chemical nomenclature set out
    by the International Union of Pure and Applied Chemistry (IUPAC).
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = CHEMINF["000037"]
    class_class_curie: ClassVar[str] = "CHEMINF:000037"
    class_name: ClassVar[str] = "IUPACChemicalFormula"
    class_model_uri: ClassVar[URIRef] = NFDI4C.IUPACChemicalFormula

    value: str = None

@dataclass(repr=False)
class SMILES(QualitativeAttribute):
    """
    A structure descriptor that denotes a molecular structure as a graph and conforms to the SMILES format
    specification.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = CHEMINF["000018"]
    class_class_curie: ClassVar[str] = "CHEMINF:000018"
    class_name: ClassVar[str] = "SMILES"
    class_model_uri: ClassVar[URIRef] = NFDI4C.SMILES

    value: str = None

@dataclass(repr=False)
class QuantitativeAttribute(YAMLRoot):
    """
    A quantifiable piece of information that is attributed to an entity of interest, tool or environment.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = QUDT["Quantity"]
    class_class_curie: ClassVar[str] = "qudt:Quantity"
    class_name: ClassVar[str] = "QuantitativeAttribute"
    class_model_uri: ClassVar[URIRef] = NFDI4C.QuantitativeAttribute

    value: float = None
    has_quantity_type: Union[str, DefinedTermId] = None
    title: Optional[str] = None
    description: Optional[str] = None
    unit: Optional[Union[str, DefinedTermId]] = None
    type: Optional[Union[dict, DefinedTerm]] = None
    rdf_type: Optional[Union[dict, DefinedTerm]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.value):
            self.MissingRequiredField("value")
        if not isinstance(self.value, float):
            self.value = float(self.value)

        if self._is_empty(self.has_quantity_type):
            self.MissingRequiredField("has_quantity_type")
        if not isinstance(self.has_quantity_type, DefinedTermId):
            self.has_quantity_type = DefinedTermId(self.has_quantity_type)

        if self.title is not None and not isinstance(self.title, str):
            self.title = str(self.title)

        if self.description is not None and not isinstance(self.description, str):
            self.description = str(self.description)

        if self.unit is not None and not isinstance(self.unit, DefinedTermId):
            self.unit = DefinedTermId(self.unit)

        if self.type is not None and not isinstance(self.type, DefinedTerm):
            self.type = DefinedTerm(**as_dict(self.type))

        if self.rdf_type is not None and not isinstance(self.rdf_type, DefinedTerm):
            self.rdf_type = DefinedTerm(**as_dict(self.rdf_type))

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Mass(QuantitativeAttribute):
    """
    Mass is the quality of the amount of a MaterialSample.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = SIO["000279"]
    class_class_curie: ClassVar[str] = "SIO:000279"
    class_name: ClassVar[str] = "Mass"
    class_model_uri: ClassVar[URIRef] = NFDI4C.Mass

    value: float = None
    has_quantity_type: Union[str, DefinedTermId] = None

@dataclass(repr=False)
class Length(QuantitativeAttribute):
    """
    Length is the longer dimensional extent along a 2D projection of the object.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = SIO["000041"]
    class_class_curie: ClassVar[str] = "SIO:000041"
    class_name: ClassVar[str] = "Length"
    class_model_uri: ClassVar[URIRef] = NFDI4C.Length

    value: float = None
    has_quantity_type: Union[str, DefinedTermId] = None

@dataclass(repr=False)
class Height(QuantitativeAttribute):
    """
    Height is the one dimensional extent along the vertical projection of a 3D object from a base plane of reference.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = SIO["000040"]
    class_class_curie: ClassVar[str] = "SIO:000040"
    class_name: ClassVar[str] = "Height"
    class_model_uri: ClassVar[URIRef] = NFDI4C.Height

    value: float = None
    has_quantity_type: Union[str, DefinedTermId] = None

@dataclass(repr=False)
class Width(QuantitativeAttribute):
    """
    Width is the shorter dimensional extent perpendicular to a 2D projection of the object.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = SIO["000042"]
    class_class_curie: ClassVar[str] = "SIO:000042"
    class_name: ClassVar[str] = "Width"
    class_model_uri: ClassVar[URIRef] = NFDI4C.Width

    value: float = None
    has_quantity_type: Union[str, DefinedTermId] = None

@dataclass(repr=False)
class SurfaceArea(QuantitativeAttribute):
    """
    The surface area of a MaterialSample is a measure of the total area that the surface of the object occupies.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = SIO["001407"]
    class_class_curie: ClassVar[str] = "SIO:001407"
    class_name: ClassVar[str] = "SurfaceArea"
    class_model_uri: ClassVar[URIRef] = NFDI4C.SurfaceArea

    value: float = None
    has_quantity_type: Union[str, DefinedTermId] = None

@dataclass(repr=False)
class Volume(QuantitativeAttribute):
    """
    Volume is the quantity of three-dimensional space enclosed by some closed boundary.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = SIO["000049"]
    class_class_curie: ClassVar[str] = "SIO:000049"
    class_name: ClassVar[str] = "Volume"
    class_model_uri: ClassVar[URIRef] = NFDI4C.Volume

    value: float = None
    has_quantity_type: Union[str, DefinedTermId] = None

class Activity(YAMLRoot):
    """
    See [DCAT-AP specs:Activity](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#Activity)
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = PROV["Activity"]
    class_class_curie: ClassVar[str] = "prov:Activity"
    class_name: ClassVar[str] = "Activity"
    class_model_uri: ClassVar[URIRef] = NFDI4C.Activity


@dataclass(repr=False)
class DataCreatingActivity(Activity):
    """
    An activity (process) that has the objective to produce information about an entity or activity.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = PROV["Activity"]
    class_class_curie: ClassVar[str] = "prov:Activity"
    class_name: ClassVar[str] = "DataCreatingActivity"
    class_model_uri: ClassVar[URIRef] = NFDI4C.DataCreatingActivity

    title: Optional[str] = None
    description: Optional[str] = None
    other_identifier: Optional[Union[Union[dict, "Identifier"], List[Union[dict, "Identifier"]]]] = empty_list()
    evaluated_entity: Optional[Union[Dict[Union[str, EvaluatedEntityId], Union[dict, EvaluatedEntity]], List[Union[dict, EvaluatedEntity]]]] = empty_dict()
    evaluated_activity: Optional[Union[Dict[Union[str, EvaluatedActivityId], Union[dict, "EvaluatedActivity"]], List[Union[dict, "EvaluatedActivity"]]]] = empty_dict()
    used_tool: Optional[Union[Union[dict, Tool], List[Union[dict, Tool]]]] = empty_list()
    realized_plan: Optional[Union[dict, Plan]] = None
    has_part: Optional[Union[dict, Activity]] = None
    occurred_in: Optional[Union[dict, Environment]] = None
    type: Optional[Union[dict, DefinedTerm]] = None
    rdf_type: Optional[Union[dict, DefinedTerm]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.title is not None and not isinstance(self.title, str):
            self.title = str(self.title)

        if self.description is not None and not isinstance(self.description, str):
            self.description = str(self.description)

        if not isinstance(self.other_identifier, list):
            self.other_identifier = [self.other_identifier] if self.other_identifier is not None else []
        self.other_identifier = [v if isinstance(v, Identifier) else Identifier(**as_dict(v)) for v in self.other_identifier]

        self._normalize_inlined_as_list(slot_name="evaluated_entity", slot_type=EvaluatedEntity, key_name="id", keyed=True)

        self._normalize_inlined_as_list(slot_name="evaluated_activity", slot_type=EvaluatedActivity, key_name="id", keyed=True)

        if not isinstance(self.used_tool, list):
            self.used_tool = [self.used_tool] if self.used_tool is not None else []
        self.used_tool = [v if isinstance(v, Tool) else Tool(**as_dict(v)) for v in self.used_tool]

        if self.realized_plan is not None and not isinstance(self.realized_plan, Plan):
            self.realized_plan = Plan(**as_dict(self.realized_plan))

        if self.has_part is not None and not isinstance(self.has_part, Activity):
            self.has_part = Activity()

        if self.occurred_in is not None and not isinstance(self.occurred_in, Environment):
            self.occurred_in = Environment(**as_dict(self.occurred_in))

        if self.type is not None and not isinstance(self.type, DefinedTerm):
            self.type = DefinedTerm(**as_dict(self.type))

        if self.rdf_type is not None and not isinstance(self.rdf_type, DefinedTerm):
            self.rdf_type = DefinedTerm(**as_dict(self.rdf_type))

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class NMRSpectroscopy(DataCreatingActivity):
    """
    Spectroscopy where the energy states of spin-active nuclei placed in a static magnetic field are interrogated by
    inducing transitions between the states via radio frequency irradiation. Each experiment consists of a sequence of
    radio frequency pulses with delay periods in between them.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = NMR_SPECTROSCOPY["NMRSpectroscopy"]
    class_class_curie: ClassVar[str] = "nmr_spectroscopy:NMRSpectroscopy"
    class_name: ClassVar[str] = "NMRSpectroscopy"
    class_model_uri: ClassVar[URIRef] = NFDI4C.NMRSpectroscopy

    evaluated_entity: Optional[Union[Dict[Union[str, ChemicalSampleId], Union[dict, ChemicalSample]], List[Union[dict, ChemicalSample]]]] = empty_dict()
    rdf_type: Optional[Union[dict, DefinedTerm]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        self._normalize_inlined_as_list(slot_name="evaluated_entity", slot_type=ChemicalSample, key_name="id", keyed=True)

        if self.rdf_type is not None and not isinstance(self.rdf_type, DefinedTerm):
            self.rdf_type = DefinedTerm(**as_dict(self.rdf_type))

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class DataAnalysis(DataCreatingActivity):
    """
    A DataCreatingActivity that evaluates the data produced by another DataCreatingActivity.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = PROV["Activity"]
    class_class_curie: ClassVar[str] = "prov:Activity"
    class_name: ClassVar[str] = "DataAnalysis"
    class_model_uri: ClassVar[URIRef] = NFDI4C.DataAnalysis

    evaluated_entity: Optional[Union[Dict[Union[str, AnalysisSourceDataId], Union[dict, AnalysisSourceData]], List[Union[dict, AnalysisSourceData]]]] = empty_dict()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        self._normalize_inlined_as_list(slot_name="evaluated_entity", slot_type=AnalysisSourceData, key_name="id", keyed=True)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class NMRSpectralAnalysis(DataAnalysis):
    """
    A DataAnalysis which assigns a chemical structure to the peaks of a NMRSpectrum generated by a NMRSpectroscopy
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = NMR["1000259"]
    class_class_curie: ClassVar[str] = "NMR:1000259"
    class_name: ClassVar[str] = "NMRSpectralAnalysis"
    class_model_uri: ClassVar[URIRef] = NFDI4C.NMRSpectralAnalysis

    evaluated_entity: Optional[Union[Dict[Union[str, NMRSpectrumId], Union[dict, NMRSpectrum]], List[Union[dict, NMRSpectrum]]]] = empty_dict()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        self._normalize_inlined_as_list(slot_name="evaluated_entity", slot_type=NMRSpectrum, key_name="id", keyed=True)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class EvaluatedActivity(Activity):
    """
    An activity or process that is being evaluated in a DataCreatingActivity.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = PROV["Activity"]
    class_class_curie: ClassVar[str] = "prov:Activity"
    class_name: ClassVar[str] = "EvaluatedActivity"
    class_model_uri: ClassVar[URIRef] = NFDI4C.EvaluatedActivity

    id: Union[str, EvaluatedActivityId] = None
    title: Optional[str] = None
    description: Optional[str] = None
    other_identifier: Optional[Union[Union[dict, "Identifier"], List[Union[dict, "Identifier"]]]] = empty_list()
    has_qualitative_attribute: Optional[Union[Union[dict, QualitativeAttribute], List[Union[dict, QualitativeAttribute]]]] = empty_list()
    has_quantitative_attribute: Optional[Union[Union[dict, QuantitativeAttribute], List[Union[dict, QuantitativeAttribute]]]] = empty_list()
    has_part: Optional[Union[str, EvaluatedActivityId]] = None
    type: Optional[Union[dict, DefinedTerm]] = None
    rdf_type: Optional[Union[dict, DefinedTerm]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, EvaluatedActivityId):
            self.id = EvaluatedActivityId(self.id)

        if self.title is not None and not isinstance(self.title, str):
            self.title = str(self.title)

        if self.description is not None and not isinstance(self.description, str):
            self.description = str(self.description)

        if not isinstance(self.other_identifier, list):
            self.other_identifier = [self.other_identifier] if self.other_identifier is not None else []
        self.other_identifier = [v if isinstance(v, Identifier) else Identifier(**as_dict(v)) for v in self.other_identifier]

        if not isinstance(self.has_qualitative_attribute, list):
            self.has_qualitative_attribute = [self.has_qualitative_attribute] if self.has_qualitative_attribute is not None else []
        self.has_qualitative_attribute = [v if isinstance(v, QualitativeAttribute) else QualitativeAttribute(**as_dict(v)) for v in self.has_qualitative_attribute]

        if not isinstance(self.has_quantitative_attribute, list):
            self.has_quantitative_attribute = [self.has_quantitative_attribute] if self.has_quantitative_attribute is not None else []
        self.has_quantitative_attribute = [v if isinstance(v, QuantitativeAttribute) else QuantitativeAttribute(**as_dict(v)) for v in self.has_quantitative_attribute]

        if self.has_part is not None and not isinstance(self.has_part, EvaluatedActivityId):
            self.has_part = EvaluatedActivityId(self.has_part)

        if self.type is not None and not isinstance(self.type, DefinedTerm):
            self.type = DefinedTerm(**as_dict(self.type))

        if self.rdf_type is not None and not isinstance(self.rdf_type, DefinedTerm):
            self.rdf_type = DefinedTerm(**as_dict(self.rdf_type))

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ChemicalReaction(EvaluatedActivity):
    """
    An experimental procedure with the aim of producing a portion of a given compound or mixture.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = RXNO["0000329"]
    class_class_curie: ClassVar[str] = "RXNO:0000329"
    class_name: ClassVar[str] = "ChemicalReaction"
    class_model_uri: ClassVar[URIRef] = NFDI4C.ChemicalReaction

    id: Union[str, ChemicalReactionId] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, ChemicalReactionId):
            self.id = ChemicalReactionId(self.id)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Catalogue(YAMLRoot):
    """
    See [DCAT-AP specs:Catalogue](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#Catalogue)
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DCAT["Catalog"]
    class_class_curie: ClassVar[str] = "dcat:Catalog"
    class_name: ClassVar[str] = "Catalogue"
    class_model_uri: ClassVar[URIRef] = NFDI4C.Catalogue

    description: Union[str, List[str]] = None
    publisher: Union[dict, "Agent"] = None
    title: Union[str, List[str]] = None
    applicable_legislation: Optional[Union[Union[dict, "LegalResource"], List[Union[dict, "LegalResource"]]]] = empty_list()
    catalogue: Optional[Union[Union[dict, "Catalogue"], List[Union[dict, "Catalogue"]]]] = empty_list()
    creator: Optional[Union[dict, "Agent"]] = None
    geographical_coverage: Optional[Union[Union[dict, "Location"], List[Union[dict, "Location"]]]] = empty_list()
    has_dataset: Optional[Union[Union[dict, "Dataset"], List[Union[dict, "Dataset"]]]] = empty_list()
    has_part: Optional[Union[Union[dict, "Catalogue"], List[Union[dict, "Catalogue"]]]] = empty_list()
    homepage: Optional[Union[dict, "Document"]] = None
    language: Optional[Union[Union[dict, "LinguisticSystem"], List[Union[dict, "LinguisticSystem"]]]] = empty_list()
    licence: Optional[Union[dict, "LicenseDocument"]] = None
    modification_date: Optional[str] = None
    record: Optional[Union[Union[dict, "CatalogueRecord"], List[Union[dict, "CatalogueRecord"]]]] = empty_list()
    release_date: Optional[str] = None
    rights: Optional[Union[dict, "RightsStatement"]] = None
    service: Optional[Union[Union[dict, "DataService"], List[Union[dict, "DataService"]]]] = empty_list()
    temporal_coverage: Optional[Union[Union[dict, "PeriodOfTime"], List[Union[dict, "PeriodOfTime"]]]] = empty_list()
    themes: Optional[Union[Union[dict, "ConceptScheme"], List[Union[dict, "ConceptScheme"]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.description):
            self.MissingRequiredField("description")
        if not isinstance(self.description, list):
            self.description = [self.description] if self.description is not None else []
        self.description = [v if isinstance(v, str) else str(v) for v in self.description]

        if self._is_empty(self.publisher):
            self.MissingRequiredField("publisher")
        if not isinstance(self.publisher, Agent):
            self.publisher = Agent(**as_dict(self.publisher))

        if self._is_empty(self.title):
            self.MissingRequiredField("title")
        if not isinstance(self.title, list):
            self.title = [self.title] if self.title is not None else []
        self.title = [v if isinstance(v, str) else str(v) for v in self.title]

        if not isinstance(self.applicable_legislation, list):
            self.applicable_legislation = [self.applicable_legislation] if self.applicable_legislation is not None else []
        self.applicable_legislation = [v if isinstance(v, LegalResource) else LegalResource(**as_dict(v)) for v in self.applicable_legislation]

        if not isinstance(self.catalogue, list):
            self.catalogue = [self.catalogue] if self.catalogue is not None else []
        self.catalogue = [v if isinstance(v, Catalogue) else Catalogue(**as_dict(v)) for v in self.catalogue]

        if self.creator is not None and not isinstance(self.creator, Agent):
            self.creator = Agent(**as_dict(self.creator))

        if not isinstance(self.geographical_coverage, list):
            self.geographical_coverage = [self.geographical_coverage] if self.geographical_coverage is not None else []
        self.geographical_coverage = [v if isinstance(v, Location) else Location(**as_dict(v)) for v in self.geographical_coverage]

        if not isinstance(self.has_dataset, list):
            self.has_dataset = [self.has_dataset] if self.has_dataset is not None else []
        self.has_dataset = [v if isinstance(v, Dataset) else Dataset(**as_dict(v)) for v in self.has_dataset]

        if not isinstance(self.has_part, list):
            self.has_part = [self.has_part] if self.has_part is not None else []
        self.has_part = [v if isinstance(v, Catalogue) else Catalogue(**as_dict(v)) for v in self.has_part]

        if self.homepage is not None and not isinstance(self.homepage, Document):
            self.homepage = Document()

        if not isinstance(self.language, list):
            self.language = [self.language] if self.language is not None else []
        self.language = [v if isinstance(v, LinguisticSystem) else LinguisticSystem(**as_dict(v)) for v in self.language]

        if self.licence is not None and not isinstance(self.licence, LicenseDocument):
            self.licence = LicenseDocument(**as_dict(self.licence))

        if self.modification_date is not None and not isinstance(self.modification_date, str):
            self.modification_date = str(self.modification_date)

        if not isinstance(self.record, list):
            self.record = [self.record] if self.record is not None else []
        self.record = [v if isinstance(v, CatalogueRecord) else CatalogueRecord(**as_dict(v)) for v in self.record]

        if self.release_date is not None and not isinstance(self.release_date, str):
            self.release_date = str(self.release_date)

        if self.rights is not None and not isinstance(self.rights, RightsStatement):
            self.rights = RightsStatement()

        if not isinstance(self.service, list):
            self.service = [self.service] if self.service is not None else []
        self.service = [v if isinstance(v, DataService) else DataService(**as_dict(v)) for v in self.service]

        if not isinstance(self.temporal_coverage, list):
            self.temporal_coverage = [self.temporal_coverage] if self.temporal_coverage is not None else []
        self.temporal_coverage = [v if isinstance(v, PeriodOfTime) else PeriodOfTime(**as_dict(v)) for v in self.temporal_coverage]

        if not isinstance(self.themes, list):
            self.themes = [self.themes] if self.themes is not None else []
        self.themes = [v if isinstance(v, ConceptScheme) else ConceptScheme(**as_dict(v)) for v in self.themes]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ResearchCatalog(Catalogue):
    """
    A curated collection of metadata about data resources.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DCAT["Catalog"]
    class_class_curie: ClassVar[str] = "dcat:Catalog"
    class_name: ClassVar[str] = "ResearchCatalog"
    class_model_uri: ClassVar[URIRef] = NFDI4C.ResearchCatalog

    id: Union[str, ResearchCatalogId] = None
    description: Union[str, List[str]] = None
    publisher: Union[dict, "Agent"] = None
    title: Union[str, List[str]] = None
    has_dataset: Optional[Union[str, ResearchDatasetId]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, ResearchCatalogId):
            self.id = ResearchCatalogId(self.id)

        if self.has_dataset is not None and not isinstance(self.has_dataset, ResearchDatasetId):
            self.has_dataset = ResearchDatasetId(self.has_dataset)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class CatalogueRecord(YAMLRoot):
    """
    See [DCAT-AP specs:CatalogueRecord](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#CatalogueRecord)
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DCAT["CatalogRecord"]
    class_class_curie: ClassVar[str] = "dcat:CatalogRecord"
    class_name: ClassVar[str] = "CatalogueRecord"
    class_model_uri: ClassVar[URIRef] = NFDI4C.CatalogueRecord

    modification_date: str = None
    primary_topic: Union[dict, "CataloguedResource"] = None
    application_profile: Optional[Union[Union[dict, "Standard"], List[Union[dict, "Standard"]]]] = empty_list()
    change_type: Optional[Union[dict, "Concept"]] = None
    description: Optional[Union[str, List[str]]] = empty_list()
    language: Optional[Union[Union[dict, "LinguisticSystem"], List[Union[dict, "LinguisticSystem"]]]] = empty_list()
    listing_date: Optional[str] = None
    source_metadata: Optional[Union[dict, "CatalogueRecord"]] = None
    title: Optional[Union[str, List[str]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.modification_date):
            self.MissingRequiredField("modification_date")
        if not isinstance(self.modification_date, str):
            self.modification_date = str(self.modification_date)

        if self._is_empty(self.primary_topic):
            self.MissingRequiredField("primary_topic")
        if not isinstance(self.primary_topic, CataloguedResource):
            self.primary_topic = CataloguedResource()

        if not isinstance(self.application_profile, list):
            self.application_profile = [self.application_profile] if self.application_profile is not None else []
        self.application_profile = [v if isinstance(v, Standard) else Standard(**as_dict(v)) for v in self.application_profile]

        if self.change_type is not None and not isinstance(self.change_type, Concept):
            self.change_type = Concept(**as_dict(self.change_type))

        if not isinstance(self.description, list):
            self.description = [self.description] if self.description is not None else []
        self.description = [v if isinstance(v, str) else str(v) for v in self.description]

        if not isinstance(self.language, list):
            self.language = [self.language] if self.language is not None else []
        self.language = [v if isinstance(v, LinguisticSystem) else LinguisticSystem(**as_dict(v)) for v in self.language]

        if self.listing_date is not None and not isinstance(self.listing_date, str):
            self.listing_date = str(self.listing_date)

        if self.source_metadata is not None and not isinstance(self.source_metadata, CatalogueRecord):
            self.source_metadata = CatalogueRecord(**as_dict(self.source_metadata))

        if not isinstance(self.title, list):
            self.title = [self.title] if self.title is not None else []
        self.title = [v if isinstance(v, str) else str(v) for v in self.title]

        super().__post_init__(**kwargs)


class CataloguedResource(YAMLRoot):
    """
    See [DCAT-AP specs:CataloguedResource](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#CataloguedResource)
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DCAT["Resource"]
    class_class_curie: ClassVar[str] = "dcat:Resource"
    class_name: ClassVar[str] = "CataloguedResource"
    class_model_uri: ClassVar[URIRef] = NFDI4C.CataloguedResource


@dataclass(repr=False)
class DataService(YAMLRoot):
    """
    See [DCAT-AP specs:DataService](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#DataService)
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DCAT["DataService"]
    class_class_curie: ClassVar[str] = "dcat:DataService"
    class_name: ClassVar[str] = "DataService"
    class_model_uri: ClassVar[URIRef] = NFDI4C.DataService

    endpoint_URL: Union[Union[dict, "Resource"], List[Union[dict, "Resource"]]] = None
    title: Union[str, List[str]] = None
    access_rights: Optional[Union[dict, "RightsStatement"]] = None
    applicable_legislation: Optional[Union[Union[dict, "LegalResource"], List[Union[dict, "LegalResource"]]]] = empty_list()
    conforms_to: Optional[Union[Union[dict, "Standard"], List[Union[dict, "Standard"]]]] = empty_list()
    contact_point: Optional[Union[Union[dict, "Kind"], List[Union[dict, "Kind"]]]] = empty_list()
    description: Optional[Union[str, List[str]]] = empty_list()
    documentation: Optional[Union[Union[dict, "Document"], List[Union[dict, "Document"]]]] = empty_list()
    endpoint_description: Optional[Union[Union[dict, "Resource"], List[Union[dict, "Resource"]]]] = empty_list()
    format: Optional[Union[Union[dict, "MediaTypeOrExtent"], List[Union[dict, "MediaTypeOrExtent"]]]] = empty_list()
    keyword: Optional[Union[str, List[str]]] = empty_list()
    landing_page: Optional[Union[Union[dict, "Document"], List[Union[dict, "Document"]]]] = empty_list()
    licence: Optional[Union[dict, "LicenseDocument"]] = None
    publisher: Optional[Union[dict, "Agent"]] = None
    serves_dataset: Optional[Union[Union[dict, "Dataset"], List[Union[dict, "Dataset"]]]] = empty_list()
    theme: Optional[Union[Union[dict, "Concept"], List[Union[dict, "Concept"]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.endpoint_URL):
            self.MissingRequiredField("endpoint_URL")
        if not isinstance(self.endpoint_URL, list):
            self.endpoint_URL = [self.endpoint_URL] if self.endpoint_URL is not None else []
        self.endpoint_URL = [v if isinstance(v, Resource) else Resource(**as_dict(v)) for v in self.endpoint_URL]

        if self._is_empty(self.title):
            self.MissingRequiredField("title")
        if not isinstance(self.title, list):
            self.title = [self.title] if self.title is not None else []
        self.title = [v if isinstance(v, str) else str(v) for v in self.title]

        if self.access_rights is not None and not isinstance(self.access_rights, RightsStatement):
            self.access_rights = RightsStatement()

        if not isinstance(self.applicable_legislation, list):
            self.applicable_legislation = [self.applicable_legislation] if self.applicable_legislation is not None else []
        self.applicable_legislation = [v if isinstance(v, LegalResource) else LegalResource(**as_dict(v)) for v in self.applicable_legislation]

        if not isinstance(self.conforms_to, list):
            self.conforms_to = [self.conforms_to] if self.conforms_to is not None else []
        self.conforms_to = [v if isinstance(v, Standard) else Standard(**as_dict(v)) for v in self.conforms_to]

        if not isinstance(self.contact_point, list):
            self.contact_point = [self.contact_point] if self.contact_point is not None else []
        self.contact_point = [v if isinstance(v, Kind) else Kind(**as_dict(v)) for v in self.contact_point]

        if not isinstance(self.description, list):
            self.description = [self.description] if self.description is not None else []
        self.description = [v if isinstance(v, str) else str(v) for v in self.description]

        if not isinstance(self.documentation, list):
            self.documentation = [self.documentation] if self.documentation is not None else []
        self.documentation = [v if isinstance(v, Document) else Document(**as_dict(v)) for v in self.documentation]

        if not isinstance(self.endpoint_description, list):
            self.endpoint_description = [self.endpoint_description] if self.endpoint_description is not None else []
        self.endpoint_description = [v if isinstance(v, Resource) else Resource(**as_dict(v)) for v in self.endpoint_description]

        if not isinstance(self.format, list):
            self.format = [self.format] if self.format is not None else []
        self.format = [v if isinstance(v, MediaTypeOrExtent) else MediaTypeOrExtent(**as_dict(v)) for v in self.format]

        if not isinstance(self.keyword, list):
            self.keyword = [self.keyword] if self.keyword is not None else []
        self.keyword = [v if isinstance(v, str) else str(v) for v in self.keyword]

        if not isinstance(self.landing_page, list):
            self.landing_page = [self.landing_page] if self.landing_page is not None else []
        self.landing_page = [v if isinstance(v, Document) else Document(**as_dict(v)) for v in self.landing_page]

        if self.licence is not None and not isinstance(self.licence, LicenseDocument):
            self.licence = LicenseDocument(**as_dict(self.licence))

        if self.publisher is not None and not isinstance(self.publisher, Agent):
            self.publisher = Agent(**as_dict(self.publisher))

        if not isinstance(self.serves_dataset, list):
            self.serves_dataset = [self.serves_dataset] if self.serves_dataset is not None else []
        self.serves_dataset = [v if isinstance(v, Dataset) else Dataset(**as_dict(v)) for v in self.serves_dataset]

        if not isinstance(self.theme, list):
            self.theme = [self.theme] if self.theme is not None else []
        self.theme = [v if isinstance(v, Concept) else Concept(**as_dict(v)) for v in self.theme]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Dataset(YAMLRoot):
    """
    See [DCAT-AP specs:Dataset](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#Dataset)
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DCAT["Dataset"]
    class_class_curie: ClassVar[str] = "dcat:Dataset"
    class_name: ClassVar[str] = "Dataset"
    class_model_uri: ClassVar[URIRef] = NFDI4C.Dataset

    description: Union[str, List[str]] = None
    title: Union[str, List[str]] = None
    access_rights: Optional[Union[dict, "RightsStatement"]] = None
    applicable_legislation: Optional[Union[Union[dict, "LegalResource"], List[Union[dict, "LegalResource"]]]] = empty_list()
    conforms_to: Optional[Union[Union[dict, "Standard"], List[Union[dict, "Standard"]]]] = empty_list()
    contact_point: Optional[Union[Union[dict, "Kind"], List[Union[dict, "Kind"]]]] = empty_list()
    creator: Optional[Union[Union[dict, "Agent"], List[Union[dict, "Agent"]]]] = empty_list()
    dataset_distribution: Optional[Union[Union[dict, "Distribution"], List[Union[dict, "Distribution"]]]] = empty_list()
    documentation: Optional[Union[Union[dict, "Document"], List[Union[dict, "Document"]]]] = empty_list()
    frequency: Optional[Union[dict, "Frequency"]] = None
    geographical_coverage: Optional[Union[Union[dict, "Location"], List[Union[dict, "Location"]]]] = empty_list()
    has_version: Optional[Union[Union[dict, "Dataset"], List[Union[dict, "Dataset"]]]] = empty_list()
    identifier: Optional[Union[Union[str, URI], List[Union[str, URI]]]] = empty_list()
    in_series: Optional[Union[Union[dict, "DatasetSeries"], List[Union[dict, "DatasetSeries"]]]] = empty_list()
    is_referenced_by: Optional[Union[Union[dict, "Resource"], List[Union[dict, "Resource"]]]] = empty_list()
    keyword: Optional[Union[str, List[str]]] = empty_list()
    landing_page: Optional[Union[Union[dict, "Document"], List[Union[dict, "Document"]]]] = empty_list()
    language: Optional[Union[Union[dict, "LinguisticSystem"], List[Union[dict, "LinguisticSystem"]]]] = empty_list()
    modification_date: Optional[str] = None
    other_identifier: Optional[Union[Union[dict, "Identifier"], List[Union[dict, "Identifier"]]]] = empty_list()
    provenance: Optional[Union[Union[dict, "ProvenanceStatement"], List[Union[dict, "ProvenanceStatement"]]]] = empty_list()
    publisher: Optional[Union[dict, "Agent"]] = None
    qualified_attribution: Optional[Union[Union[dict, "Attribution"], List[Union[dict, "Attribution"]]]] = empty_list()
    qualified_relation: Optional[Union[Union[dict, "Relationship"], List[Union[dict, "Relationship"]]]] = empty_list()
    related_resource: Optional[Union[Union[dict, "Resource"], List[Union[dict, "Resource"]]]] = empty_list()
    release_date: Optional[str] = None
    sample: Optional[Union[Union[dict, "Distribution"], List[Union[dict, "Distribution"]]]] = empty_list()
    source: Optional[Union[Union[dict, "Dataset"], List[Union[dict, "Dataset"]]]] = empty_list()
    spatial_resolution: Optional[Decimal] = None
    temporal_coverage: Optional[Union[Union[dict, "PeriodOfTime"], List[Union[dict, "PeriodOfTime"]]]] = empty_list()
    temporal_resolution: Optional[str] = None
    theme: Optional[Union[Union[dict, "Concept"], List[Union[dict, "Concept"]]]] = empty_list()
    type: Optional[Union[Union[dict, "Concept"], List[Union[dict, "Concept"]]]] = empty_list()
    version: Optional[str] = None
    version_notes: Optional[Union[str, List[str]]] = empty_list()
    was_generated_by: Optional[Union[Union[dict, Activity], List[Union[dict, Activity]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.description):
            self.MissingRequiredField("description")
        if not isinstance(self.description, list):
            self.description = [self.description] if self.description is not None else []
        self.description = [v if isinstance(v, str) else str(v) for v in self.description]

        if self._is_empty(self.title):
            self.MissingRequiredField("title")
        if not isinstance(self.title, list):
            self.title = [self.title] if self.title is not None else []
        self.title = [v if isinstance(v, str) else str(v) for v in self.title]

        if self.access_rights is not None and not isinstance(self.access_rights, RightsStatement):
            self.access_rights = RightsStatement()

        if not isinstance(self.applicable_legislation, list):
            self.applicable_legislation = [self.applicable_legislation] if self.applicable_legislation is not None else []
        self.applicable_legislation = [v if isinstance(v, LegalResource) else LegalResource(**as_dict(v)) for v in self.applicable_legislation]

        if not isinstance(self.conforms_to, list):
            self.conforms_to = [self.conforms_to] if self.conforms_to is not None else []
        self.conforms_to = [v if isinstance(v, Standard) else Standard(**as_dict(v)) for v in self.conforms_to]

        if not isinstance(self.contact_point, list):
            self.contact_point = [self.contact_point] if self.contact_point is not None else []
        self.contact_point = [v if isinstance(v, Kind) else Kind(**as_dict(v)) for v in self.contact_point]

        if not isinstance(self.creator, list):
            self.creator = [self.creator] if self.creator is not None else []
        self.creator = [v if isinstance(v, Agent) else Agent(**as_dict(v)) for v in self.creator]

        if not isinstance(self.dataset_distribution, list):
            self.dataset_distribution = [self.dataset_distribution] if self.dataset_distribution is not None else []
        self.dataset_distribution = [v if isinstance(v, Distribution) else Distribution(**as_dict(v)) for v in self.dataset_distribution]

        if not isinstance(self.documentation, list):
            self.documentation = [self.documentation] if self.documentation is not None else []
        self.documentation = [v if isinstance(v, Document) else Document(**as_dict(v)) for v in self.documentation]

        if self.frequency is not None and not isinstance(self.frequency, Frequency):
            self.frequency = Frequency()

        if not isinstance(self.geographical_coverage, list):
            self.geographical_coverage = [self.geographical_coverage] if self.geographical_coverage is not None else []
        self.geographical_coverage = [v if isinstance(v, Location) else Location(**as_dict(v)) for v in self.geographical_coverage]

        if not isinstance(self.has_version, list):
            self.has_version = [self.has_version] if self.has_version is not None else []
        self.has_version = [v if isinstance(v, Dataset) else Dataset(**as_dict(v)) for v in self.has_version]

        if not isinstance(self.identifier, list):
            self.identifier = [self.identifier] if self.identifier is not None else []
        self.identifier = [v if isinstance(v, URI) else URI(v) for v in self.identifier]

        if not isinstance(self.in_series, list):
            self.in_series = [self.in_series] if self.in_series is not None else []
        self.in_series = [v if isinstance(v, DatasetSeries) else DatasetSeries(**as_dict(v)) for v in self.in_series]

        if not isinstance(self.is_referenced_by, list):
            self.is_referenced_by = [self.is_referenced_by] if self.is_referenced_by is not None else []
        self.is_referenced_by = [v if isinstance(v, Resource) else Resource(**as_dict(v)) for v in self.is_referenced_by]

        if not isinstance(self.keyword, list):
            self.keyword = [self.keyword] if self.keyword is not None else []
        self.keyword = [v if isinstance(v, str) else str(v) for v in self.keyword]

        if not isinstance(self.landing_page, list):
            self.landing_page = [self.landing_page] if self.landing_page is not None else []
        self.landing_page = [v if isinstance(v, Document) else Document(**as_dict(v)) for v in self.landing_page]

        if not isinstance(self.language, list):
            self.language = [self.language] if self.language is not None else []
        self.language = [v if isinstance(v, LinguisticSystem) else LinguisticSystem(**as_dict(v)) for v in self.language]

        if self.modification_date is not None and not isinstance(self.modification_date, str):
            self.modification_date = str(self.modification_date)

        if not isinstance(self.other_identifier, list):
            self.other_identifier = [self.other_identifier] if self.other_identifier is not None else []
        self.other_identifier = [v if isinstance(v, Identifier) else Identifier(**as_dict(v)) for v in self.other_identifier]

        if not isinstance(self.provenance, list):
            self.provenance = [self.provenance] if self.provenance is not None else []
        self.provenance = [v if isinstance(v, ProvenanceStatement) else ProvenanceStatement(**as_dict(v)) for v in self.provenance]

        if self.publisher is not None and not isinstance(self.publisher, Agent):
            self.publisher = Agent(**as_dict(self.publisher))

        if not isinstance(self.qualified_attribution, list):
            self.qualified_attribution = [self.qualified_attribution] if self.qualified_attribution is not None else []
        self.qualified_attribution = [v if isinstance(v, Attribution) else Attribution(**as_dict(v)) for v in self.qualified_attribution]

        if not isinstance(self.qualified_relation, list):
            self.qualified_relation = [self.qualified_relation] if self.qualified_relation is not None else []
        self.qualified_relation = [v if isinstance(v, Relationship) else Relationship(**as_dict(v)) for v in self.qualified_relation]

        if not isinstance(self.related_resource, list):
            self.related_resource = [self.related_resource] if self.related_resource is not None else []
        self.related_resource = [v if isinstance(v, Resource) else Resource(**as_dict(v)) for v in self.related_resource]

        if self.release_date is not None and not isinstance(self.release_date, str):
            self.release_date = str(self.release_date)

        if not isinstance(self.sample, list):
            self.sample = [self.sample] if self.sample is not None else []
        self.sample = [v if isinstance(v, Distribution) else Distribution(**as_dict(v)) for v in self.sample]

        if not isinstance(self.source, list):
            self.source = [self.source] if self.source is not None else []
        self.source = [v if isinstance(v, Dataset) else Dataset(**as_dict(v)) for v in self.source]

        if self.spatial_resolution is not None and not isinstance(self.spatial_resolution, Decimal):
            self.spatial_resolution = Decimal(self.spatial_resolution)

        if not isinstance(self.temporal_coverage, list):
            self.temporal_coverage = [self.temporal_coverage] if self.temporal_coverage is not None else []
        self.temporal_coverage = [v if isinstance(v, PeriodOfTime) else PeriodOfTime(**as_dict(v)) for v in self.temporal_coverage]

        if self.temporal_resolution is not None and not isinstance(self.temporal_resolution, str):
            self.temporal_resolution = str(self.temporal_resolution)

        if not isinstance(self.theme, list):
            self.theme = [self.theme] if self.theme is not None else []
        self.theme = [v if isinstance(v, Concept) else Concept(**as_dict(v)) for v in self.theme]

        if not isinstance(self.type, list):
            self.type = [self.type] if self.type is not None else []
        self.type = [v if isinstance(v, Concept) else Concept(**as_dict(v)) for v in self.type]

        if self.version is not None and not isinstance(self.version, str):
            self.version = str(self.version)

        if not isinstance(self.version_notes, list):
            self.version_notes = [self.version_notes] if self.version_notes is not None else []
        self.version_notes = [v if isinstance(v, str) else str(v) for v in self.version_notes]

        if not isinstance(self.was_generated_by, list):
            self.was_generated_by = [self.was_generated_by] if self.was_generated_by is not None else []
        self.was_generated_by = [v if isinstance(v, Activity) else Activity(**as_dict(v)) for v in self.was_generated_by]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ResearchDataset(Dataset):
    """
    A collection of data, published or curated by a single agent, and available for access or download in one or more
    representations.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DCAT["Dataset"]
    class_class_curie: ClassVar[str] = "dcat:Dataset"
    class_name: ClassVar[str] = "ResearchDataset"
    class_model_uri: ClassVar[URIRef] = NFDI4C.ResearchDataset

    id: Union[str, ResearchDatasetId] = None
    description: Union[str, List[str]] = None
    title: Union[str, List[str]] = None
    was_generated_by: Union[Union[dict, DataCreatingActivity], List[Union[dict, DataCreatingActivity]]] = None
    describes_entity: Optional[Union[Dict[Union[str, EvaluatedEntityId], Union[dict, EvaluatedEntity]], List[Union[dict, EvaluatedEntity]]]] = empty_dict()
    describes_activity: Optional[Union[Dict[Union[str, EvaluatedActivityId], Union[dict, EvaluatedActivity]], List[Union[dict, EvaluatedActivity]]]] = empty_dict()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, ResearchDatasetId):
            self.id = ResearchDatasetId(self.id)

        if self._is_empty(self.was_generated_by):
            self.MissingRequiredField("was_generated_by")
        if not isinstance(self.was_generated_by, list):
            self.was_generated_by = [self.was_generated_by] if self.was_generated_by is not None else []
        self.was_generated_by = [v if isinstance(v, DataCreatingActivity) else DataCreatingActivity(**as_dict(v)) for v in self.was_generated_by]

        self._normalize_inlined_as_list(slot_name="describes_entity", slot_type=EvaluatedEntity, key_name="id", keyed=True)

        self._normalize_inlined_as_list(slot_name="describes_activity", slot_type=EvaluatedActivity, key_name="id", keyed=True)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class AnalysisDataset(ResearchDataset):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DCAT["Dataset"]
    class_class_curie: ClassVar[str] = "dcat:Dataset"
    class_name: ClassVar[str] = "AnalysisDataset"
    class_model_uri: ClassVar[URIRef] = NFDI4C.AnalysisDataset

    id: Union[str, AnalysisDatasetId] = None
    description: Union[str, List[str]] = None
    title: Union[str, List[str]] = None
    was_generated_by: Union[Union[dict, DataAnalysis], List[Union[dict, DataAnalysis]]] = None
    # log.debug(f"AnalysisDatasetId: {AnalysisDatasetId}")

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, AnalysisDatasetId):
            self.id = AnalysisDatasetId(self.id)

        if self._is_empty(self.was_generated_by):
            self.MissingRequiredField("was_generated_by")
        if not isinstance(self.was_generated_by, list):
            self.was_generated_by = [self.was_generated_by] if self.was_generated_by is not None else []
        self.was_generated_by = [v if isinstance(v, DataAnalysis) else DataAnalysis(**as_dict(v)) for v in self.was_generated_by]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class NMRAnalysisDataset(AnalysisDataset):
    """
    A dataset that is the result of a NMRSpectralAnalysis of a ChemicalSample.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DCAT["Dataset"]
    class_class_curie: ClassVar[str] = "dcat:Dataset"
    class_name: ClassVar[str] = "NMRAnalysisDataset"
    class_model_uri: ClassVar[URIRef] = NFDI4C.NMRAnalysisDataset

    id: Union[str, NMRAnalysisDatasetId] = None
    description: Union[str, List[str]] = None
    title: Union[str, List[str]] = None
    was_generated_by: Optional[Union[Union[dict, NMRSpectralAnalysis], List[Union[dict, NMRSpectralAnalysis]]]] = empty_list()
    describes_entity: Optional[Union[Dict[Union[str, ChemicalSampleId], Union[dict, ChemicalSample]], List[Union[dict, ChemicalSample]]]] = empty_dict()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, NMRAnalysisDatasetId):
            self.id = NMRAnalysisDatasetId(self.id)

        if not isinstance(self.was_generated_by, list):
            self.was_generated_by = [self.was_generated_by] if self.was_generated_by is not None else []
        self.was_generated_by = [v if isinstance(v, NMRSpectralAnalysis) else NMRSpectralAnalysis(**as_dict(v)) for v in self.was_generated_by]

        self._normalize_inlined_as_list(slot_name="describes_entity", slot_type=ChemicalSample, key_name="id", keyed=True)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class DatasetSeries(YAMLRoot):
    """
    See [DCAT-AP specs:DatasetSeries](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#DatasetSeries)
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DCAT["DatasetSeries"]
    class_class_curie: ClassVar[str] = "dcat:DatasetSeries"
    class_name: ClassVar[str] = "DatasetSeries"
    class_model_uri: ClassVar[URIRef] = NFDI4C.DatasetSeries

    description: Union[str, List[str]] = None
    title: Union[str, List[str]] = None
    applicable_legislation: Optional[Union[Union[dict, "LegalResource"], List[Union[dict, "LegalResource"]]]] = empty_list()
    contact_point: Optional[Union[Union[dict, "Kind"], List[Union[dict, "Kind"]]]] = empty_list()
    frequency: Optional[Union[dict, "Frequency"]] = None
    geographical_coverage: Optional[Union[Union[dict, "Location"], List[Union[dict, "Location"]]]] = empty_list()
    modification_date: Optional[str] = None
    publisher: Optional[Union[dict, "Agent"]] = None
    release_date: Optional[str] = None
    temporal_coverage: Optional[Union[Union[dict, "PeriodOfTime"], List[Union[dict, "PeriodOfTime"]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.description):
            self.MissingRequiredField("description")
        if not isinstance(self.description, list):
            self.description = [self.description] if self.description is not None else []
        self.description = [v if isinstance(v, str) else str(v) for v in self.description]

        if self._is_empty(self.title):
            self.MissingRequiredField("title")
        if not isinstance(self.title, list):
            self.title = [self.title] if self.title is not None else []
        self.title = [v if isinstance(v, str) else str(v) for v in self.title]

        if not isinstance(self.applicable_legislation, list):
            self.applicable_legislation = [self.applicable_legislation] if self.applicable_legislation is not None else []
        self.applicable_legislation = [v if isinstance(v, LegalResource) else LegalResource(**as_dict(v)) for v in self.applicable_legislation]

        if not isinstance(self.contact_point, list):
            self.contact_point = [self.contact_point] if self.contact_point is not None else []
        self.contact_point = [v if isinstance(v, Kind) else Kind(**as_dict(v)) for v in self.contact_point]

        if self.frequency is not None and not isinstance(self.frequency, Frequency):
            self.frequency = Frequency()

        if not isinstance(self.geographical_coverage, list):
            self.geographical_coverage = [self.geographical_coverage] if self.geographical_coverage is not None else []
        self.geographical_coverage = [v if isinstance(v, Location) else Location(**as_dict(v)) for v in self.geographical_coverage]

        if self.modification_date is not None and not isinstance(self.modification_date, str):
            self.modification_date = str(self.modification_date)

        if self.publisher is not None and not isinstance(self.publisher, Agent):
            self.publisher = Agent(**as_dict(self.publisher))

        if self.release_date is not None and not isinstance(self.release_date, str):
            self.release_date = str(self.release_date)

        if not isinstance(self.temporal_coverage, list):
            self.temporal_coverage = [self.temporal_coverage] if self.temporal_coverage is not None else []
        self.temporal_coverage = [v if isinstance(v, PeriodOfTime) else PeriodOfTime(**as_dict(v)) for v in self.temporal_coverage]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class Distribution(YAMLRoot):
    """
    See [DCAT-AP specs:Distribution](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#Distribution)
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DCAT["Distribution"]
    class_class_curie: ClassVar[str] = "dcat:Distribution"
    class_name: ClassVar[str] = "Distribution"
    class_model_uri: ClassVar[URIRef] = NFDI4C.Distribution

    access_URL: Union[Union[dict, "Resource"], List[Union[dict, "Resource"]]] = None
    access_service: Optional[Union[Union[dict, DataService], List[Union[dict, DataService]]]] = empty_list()
    applicable_legislation: Optional[Union[Union[dict, "LegalResource"], List[Union[dict, "LegalResource"]]]] = empty_list()
    availability: Optional[Union[dict, "Concept"]] = None
    byte_size: Optional[int] = None
    checksum: Optional[Union[dict, "Checksum"]] = None
    compression_format: Optional[Union[dict, "MediaType"]] = None
    description: Optional[Union[str, List[str]]] = empty_list()
    documentation: Optional[Union[Union[dict, "Document"], List[Union[dict, "Document"]]]] = empty_list()
    download_URL: Optional[Union[Union[dict, "Resource"], List[Union[dict, "Resource"]]]] = empty_list()
    format: Optional[Union[dict, "MediaTypeOrExtent"]] = None
    has_policy: Optional[Union[dict, "Policy"]] = None
    language: Optional[Union[Union[dict, "LinguisticSystem"], List[Union[dict, "LinguisticSystem"]]]] = empty_list()
    licence: Optional[Union[dict, "LicenseDocument"]] = None
    linked_schemas: Optional[Union[Union[dict, "Standard"], List[Union[dict, "Standard"]]]] = empty_list()
    media_type: Optional[Union[dict, "MediaType"]] = None
    modification_date: Optional[str] = None
    packaging_format: Optional[Union[dict, "MediaType"]] = None
    release_date: Optional[str] = None
    rights: Optional[Union[dict, "RightsStatement"]] = None
    spatial_resolution: Optional[Decimal] = None
    status: Optional[Union[dict, "Concept"]] = None
    temporal_resolution: Optional[str] = None
    title: Optional[Union[str, List[str]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.access_URL):
            self.MissingRequiredField("access_URL")
        if not isinstance(self.access_URL, list):
            self.access_URL = [self.access_URL] if self.access_URL is not None else []
        self.access_URL = [v if isinstance(v, Resource) else Resource(**as_dict(v)) for v in self.access_URL]

        if not isinstance(self.access_service, list):
            self.access_service = [self.access_service] if self.access_service is not None else []
        self.access_service = [v if isinstance(v, DataService) else DataService(**as_dict(v)) for v in self.access_service]

        if not isinstance(self.applicable_legislation, list):
            self.applicable_legislation = [self.applicable_legislation] if self.applicable_legislation is not None else []
        self.applicable_legislation = [v if isinstance(v, LegalResource) else LegalResource(**as_dict(v)) for v in self.applicable_legislation]

        if self.availability is not None and not isinstance(self.availability, Concept):
            self.availability = Concept(**as_dict(self.availability))

        if self.byte_size is not None and not isinstance(self.byte_size, int):
            self.byte_size = int(self.byte_size)

        if self.checksum is not None and not isinstance(self.checksum, Checksum):
            self.checksum = Checksum(**as_dict(self.checksum))

        if self.compression_format is not None and not isinstance(self.compression_format, MediaType):
            self.compression_format = MediaType()

        if not isinstance(self.description, list):
            self.description = [self.description] if self.description is not None else []
        self.description = [v if isinstance(v, str) else str(v) for v in self.description]

        if not isinstance(self.documentation, list):
            self.documentation = [self.documentation] if self.documentation is not None else []
        self.documentation = [v if isinstance(v, Document) else Document(**as_dict(v)) for v in self.documentation]

        if not isinstance(self.download_URL, list):
            self.download_URL = [self.download_URL] if self.download_URL is not None else []
        self.download_URL = [v if isinstance(v, Resource) else Resource(**as_dict(v)) for v in self.download_URL]

        if self.format is not None and not isinstance(self.format, MediaTypeOrExtent):
            self.format = MediaTypeOrExtent()

        if self.has_policy is not None and not isinstance(self.has_policy, Policy):
            self.has_policy = Policy()

        if not isinstance(self.language, list):
            self.language = [self.language] if self.language is not None else []
        self.language = [v if isinstance(v, LinguisticSystem) else LinguisticSystem(**as_dict(v)) for v in self.language]

        if self.licence is not None and not isinstance(self.licence, LicenseDocument):
            self.licence = LicenseDocument(**as_dict(self.licence))

        if not isinstance(self.linked_schemas, list):
            self.linked_schemas = [self.linked_schemas] if self.linked_schemas is not None else []
        self.linked_schemas = [v if isinstance(v, Standard) else Standard(**as_dict(v)) for v in self.linked_schemas]

        if self.media_type is not None and not isinstance(self.media_type, MediaType):
            self.media_type = MediaType()

        if self.modification_date is not None and not isinstance(self.modification_date, str):
            self.modification_date = str(self.modification_date)

        if self.packaging_format is not None and not isinstance(self.packaging_format, MediaType):
            self.packaging_format = MediaType()

        if self.release_date is not None and not isinstance(self.release_date, str):
            self.release_date = str(self.release_date)

        if self.rights is not None and not isinstance(self.rights, RightsStatement):
            self.rights = RightsStatement()

        if self.spatial_resolution is not None and not isinstance(self.spatial_resolution, Decimal):
            self.spatial_resolution = Decimal(self.spatial_resolution)

        if self.status is not None and not isinstance(self.status, Concept):
            self.status = Concept(**as_dict(self.status))

        if self.temporal_resolution is not None and not isinstance(self.temporal_resolution, str):
            self.temporal_resolution = str(self.temporal_resolution)

        if not isinstance(self.title, list):
            self.title = [self.title] if self.title is not None else []
        self.title = [v if isinstance(v, str) else str(v) for v in self.title]

        super().__post_init__(**kwargs)


class SupportiveEntity(YAMLRoot):
    """
    The supportive entities are supporting the main entities in the Application Profile. They are included in the
    Application Profile because they form the range of properties.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = LINKMLDCATAP["SupportiveEntity"]
    class_class_curie: ClassVar[str] = "linkmldcatap:SupportiveEntity"
    class_name: ClassVar[str] = "SupportiveEntity"
    class_model_uri: ClassVar[URIRef] = NFDI4C.SupportiveEntity


@dataclass(repr=False)
class Agent(SupportiveEntity):
    """
    See [DCAT-AP specs:Agent](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#Agent)
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = FOAF["Agent"]
    class_class_curie: ClassVar[str] = "foaf:Agent"
    class_name: ClassVar[str] = "Agent"
    class_model_uri: ClassVar[URIRef] = NFDI4C.Agent

    name: Union[str, List[str]] = None
    type: Optional[Union[dict, "Concept"]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.name):
            self.MissingRequiredField("name")
        if not isinstance(self.name, list):
            self.name = [self.name] if self.name is not None else []
        self.name = [v if isinstance(v, str) else str(v) for v in self.name]

        if self.type is not None and not isinstance(self.type, Concept):
            self.type = Concept(**as_dict(self.type))

        super().__post_init__(**kwargs)


class Attribution(SupportiveEntity):
    """
    See [DCAT-AP specs:Attribution](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#Attribution)
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = PROV["Attribution"]
    class_class_curie: ClassVar[str] = "prov:Attribution"
    class_name: ClassVar[str] = "Attribution"
    class_model_uri: ClassVar[URIRef] = NFDI4C.Attribution


@dataclass(repr=False)
class Checksum(SupportiveEntity):
    """
    See [DCAT-AP specs:Checksum](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#Checksum)
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = SPDX["Checksum"]
    class_class_curie: ClassVar[str] = "spdx:Checksum"
    class_name: ClassVar[str] = "Checksum"
    class_model_uri: ClassVar[URIRef] = NFDI4C.Checksum

    algorithm: Union[dict, "ChecksumAlgorithm"] = None
    checksum_value: str = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.algorithm):
            self.MissingRequiredField("algorithm")
        if not isinstance(self.algorithm, ChecksumAlgorithm):
            self.algorithm = ChecksumAlgorithm()

        if self._is_empty(self.checksum_value):
            self.MissingRequiredField("checksum_value")
        if not isinstance(self.checksum_value, str):
            self.checksum_value = str(self.checksum_value)

        super().__post_init__(**kwargs)


class ChecksumAlgorithm(SupportiveEntity):
    """
    See [DCAT-AP specs:ChecksumAlgorithm](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#ChecksumAlgorithm)
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = SPDX["ChecksumAlgorithm"]
    class_class_curie: ClassVar[str] = "spdx:ChecksumAlgorithm"
    class_name: ClassVar[str] = "ChecksumAlgorithm"
    class_model_uri: ClassVar[URIRef] = NFDI4C.ChecksumAlgorithm


@dataclass(repr=False)
class Concept(SupportiveEntity):
    """
    See [DCAT-AP specs:Concept](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#Concept)
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = SKOS["Concept"]
    class_class_curie: ClassVar[str] = "skos:Concept"
    class_name: ClassVar[str] = "Concept"
    class_model_uri: ClassVar[URIRef] = NFDI4C.Concept

    preferred_label: Union[str, List[str]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.preferred_label):
            self.MissingRequiredField("preferred_label")
        if not isinstance(self.preferred_label, list):
            self.preferred_label = [self.preferred_label] if self.preferred_label is not None else []
        self.preferred_label = [v if isinstance(v, str) else str(v) for v in self.preferred_label]

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class ConceptScheme(SupportiveEntity):
    """
    See [DCAT-AP specs:ConceptScheme](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#ConceptScheme)
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = SKOS["ConceptScheme"]
    class_class_curie: ClassVar[str] = "skos:ConceptScheme"
    class_name: ClassVar[str] = "ConceptScheme"
    class_model_uri: ClassVar[URIRef] = NFDI4C.ConceptScheme

    title: Union[str, List[str]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.title):
            self.MissingRequiredField("title")
        if not isinstance(self.title, list):
            self.title = [self.title] if self.title is not None else []
        self.title = [v if isinstance(v, str) else str(v) for v in self.title]

        super().__post_init__(**kwargs)


class Document(SupportiveEntity):
    """
    See [DCAT-AP specs:Document](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#Document)
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = FOAF["Document"]
    class_class_curie: ClassVar[str] = "foaf:Document"
    class_name: ClassVar[str] = "Document"
    class_model_uri: ClassVar[URIRef] = NFDI4C.Document


class Frequency(SupportiveEntity):
    """
    See [DCAT-AP specs:Frequency](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#Frequency)
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DCTERMS["Frequency"]
    class_class_curie: ClassVar[str] = "dcterms:Frequency"
    class_name: ClassVar[str] = "Frequency"
    class_model_uri: ClassVar[URIRef] = NFDI4C.Frequency


class Geometry(SupportiveEntity):
    """
    See [DCAT-AP specs:Geometry](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#Geometry)
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = LOCN["Geometry"]
    class_class_curie: ClassVar[str] = "locn:Geometry"
    class_name: ClassVar[str] = "Geometry"
    class_model_uri: ClassVar[URIRef] = NFDI4C.Geometry


@dataclass(repr=False)
class Identifier(SupportiveEntity):
    """
    See [DCAT-AP specs:Identifier](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#Identifier)
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = ADMS["Identifier"]
    class_class_curie: ClassVar[str] = "adms:Identifier"
    class_name: ClassVar[str] = "Identifier"
    class_model_uri: ClassVar[URIRef] = NFDI4C.Identifier

    notation: Union[str, URI] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.notation):
            self.MissingRequiredField("notation")
        if not isinstance(self.notation, URI):
            self.notation = URI(self.notation)

        super().__post_init__(**kwargs)


class Kind(SupportiveEntity):
    """
    See [DCAT-AP specs:Kind](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#Kind)
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = VCARD["Kind"]
    class_class_curie: ClassVar[str] = "vcard:Kind"
    class_name: ClassVar[str] = "Kind"
    class_model_uri: ClassVar[URIRef] = NFDI4C.Kind


class LegalResource(SupportiveEntity):
    """
    See [DCAT-AP specs:LegalResource](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#LegalResource)
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = ELI["LegalResource"]
    class_class_curie: ClassVar[str] = "eli:LegalResource"
    class_name: ClassVar[str] = "LegalResource"
    class_model_uri: ClassVar[URIRef] = NFDI4C.LegalResource


@dataclass(repr=False)
class LicenseDocument(SupportiveEntity):
    """
    See [DCAT-AP specs:LicenseDocument](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#LicenseDocument)
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DCTERMS["LicenseDocument"]
    class_class_curie: ClassVar[str] = "dcterms:LicenseDocument"
    class_name: ClassVar[str] = "LicenseDocument"
    class_model_uri: ClassVar[URIRef] = NFDI4C.LicenseDocument

    type: Optional[Union[Union[dict, Concept], List[Union[dict, Concept]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if not isinstance(self.type, list):
            self.type = [self.type] if self.type is not None else []
        self.type = [v if isinstance(v, Concept) else Concept(**as_dict(v)) for v in self.type]

        super().__post_init__(**kwargs)


class LinguisticSystem(SupportiveEntity):
    """
    See [DCAT-AP specs:LinguisticSystem](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#LinguisticSystem)
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DCTERMS["LinguisticSystem"]
    class_class_curie: ClassVar[str] = "dcterms:LinguisticSystem"
    class_name: ClassVar[str] = "LinguisticSystem"
    class_model_uri: ClassVar[URIRef] = NFDI4C.LinguisticSystem


@dataclass(repr=False)
class Location(SupportiveEntity):
    """
    See [DCAT-AP specs:Location](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#Location)
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DCTERMS["Location"]
    class_class_curie: ClassVar[str] = "dcterms:Location"
    class_name: ClassVar[str] = "Location"
    class_model_uri: ClassVar[URIRef] = NFDI4C.Location

    bbox: Optional[str] = None
    centroid: Optional[str] = None
    geometry: Optional[Union[dict, Geometry]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.bbox is not None and not isinstance(self.bbox, str):
            self.bbox = str(self.bbox)

        if self.centroid is not None and not isinstance(self.centroid, str):
            self.centroid = str(self.centroid)

        if self.geometry is not None and not isinstance(self.geometry, Geometry):
            self.geometry = Geometry()

        super().__post_init__(**kwargs)


class MediaType(SupportiveEntity):
    """
    See [DCAT-AP specs:MediaType](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#MediaType)
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DCTERMS["MediaType"]
    class_class_curie: ClassVar[str] = "dcterms:MediaType"
    class_name: ClassVar[str] = "MediaType"
    class_model_uri: ClassVar[URIRef] = NFDI4C.MediaType


class MediaTypeOrExtent(SupportiveEntity):
    """
    See [DCAT-AP specs:MediaTypeOrExtent](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#MediaTypeOrExtent)
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DCTERMS["MediaTypeOrExtent"]
    class_class_curie: ClassVar[str] = "dcterms:MediaTypeOrExtent"
    class_name: ClassVar[str] = "MediaTypeOrExtent"
    class_model_uri: ClassVar[URIRef] = NFDI4C.MediaTypeOrExtent


@dataclass(repr=False)
class PeriodOfTime(SupportiveEntity):
    """
    See [DCAT-AP specs:PeriodOfTime](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#PeriodOfTime)
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DCTERMS["PeriodOfTime"]
    class_class_curie: ClassVar[str] = "dcterms:PeriodOfTime"
    class_name: ClassVar[str] = "PeriodOfTime"
    class_model_uri: ClassVar[URIRef] = NFDI4C.PeriodOfTime

    beginning: Optional[Union[dict, "TimeInstant"]] = None
    end: Optional[Union[dict, "TimeInstant"]] = None
    end_date: Optional[str] = None
    start_date: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.beginning is not None and not isinstance(self.beginning, TimeInstant):
            self.beginning = TimeInstant()

        if self.end is not None and not isinstance(self.end, TimeInstant):
            self.end = TimeInstant()

        if self.end_date is not None and not isinstance(self.end_date, str):
            self.end_date = str(self.end_date)

        if self.start_date is not None and not isinstance(self.start_date, str):
            self.start_date = str(self.start_date)

        super().__post_init__(**kwargs)


class Policy(SupportiveEntity):
    """
    See [DCAT-AP specs:Policy](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#Policy)
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = ODRL["Policy"]
    class_class_curie: ClassVar[str] = "odrl:Policy"
    class_name: ClassVar[str] = "Policy"
    class_model_uri: ClassVar[URIRef] = NFDI4C.Policy


class ProvenanceStatement(SupportiveEntity):
    """
    See [DCAT-AP specs:ProvenanceStatement](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#ProvenanceStatement)
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DCTERMS["ProvenanceStatement"]
    class_class_curie: ClassVar[str] = "dcterms:ProvenanceStatement"
    class_name: ClassVar[str] = "ProvenanceStatement"
    class_model_uri: ClassVar[URIRef] = NFDI4C.ProvenanceStatement


@dataclass(repr=False)
class Relationship(SupportiveEntity):
    """
    See [DCAT-AP specs:Relationship](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#Relationship)
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DCAT["Relationship"]
    class_class_curie: ClassVar[str] = "dcat:Relationship"
    class_name: ClassVar[str] = "Relationship"
    class_model_uri: ClassVar[URIRef] = NFDI4C.Relationship

    had_role: Union[Union[dict, "Role"], List[Union[dict, "Role"]]] = None
    relation: Union[Union[dict, "Resource"], List[Union[dict, "Resource"]]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.had_role):
            self.MissingRequiredField("had_role")
        if not isinstance(self.had_role, list):
            self.had_role = [self.had_role] if self.had_role is not None else []
        self.had_role = [v if isinstance(v, Role) else Role(**as_dict(v)) for v in self.had_role]

        if self._is_empty(self.relation):
            self.MissingRequiredField("relation")
        if not isinstance(self.relation, list):
            self.relation = [self.relation] if self.relation is not None else []
        self.relation = [v if isinstance(v, Resource) else Resource(**as_dict(v)) for v in self.relation]

        super().__post_init__(**kwargs)


class Resource(SupportiveEntity):
    """
    See [DCAT-AP specs:Resource](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#Resource)
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = RDFS["Resource"]
    class_class_curie: ClassVar[str] = "rdfs:Resource"
    class_name: ClassVar[str] = "Resource"
    class_model_uri: ClassVar[URIRef] = NFDI4C.Resource


class RightsStatement(SupportiveEntity):
    """
    See [DCAT-AP specs:RightsStatement](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#RightsStatement)
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DCTERMS["RightsStatement"]
    class_class_curie: ClassVar[str] = "dcterms:RightsStatement"
    class_name: ClassVar[str] = "RightsStatement"
    class_model_uri: ClassVar[URIRef] = NFDI4C.RightsStatement


class Role(SupportiveEntity):
    """
    See [DCAT-AP specs:Role](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#Role)
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DCAT["Role"]
    class_class_curie: ClassVar[str] = "dcat:Role"
    class_name: ClassVar[str] = "Role"
    class_model_uri: ClassVar[URIRef] = NFDI4C.Role


class Standard(SupportiveEntity):
    """
    See [DCAT-AP specs:Standard](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#Standard)
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DCTERMS["Standard"]
    class_class_curie: ClassVar[str] = "dcterms:Standard"
    class_name: ClassVar[str] = "Standard"
    class_model_uri: ClassVar[URIRef] = NFDI4C.Standard


class TimeInstant(SupportiveEntity):
    """
    See [DCAT-AP specs:TimeInstant](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#TimeInstant)
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = TIME["Instant"]
    class_class_curie: ClassVar[str] = "time:Instant"
    class_name: ClassVar[str] = "TimeInstant"
    class_model_uri: ClassVar[URIRef] = NFDI4C.TimeInstant


# Enumerations
class NMRAssayEnum(EnumDefinitionImpl):
    """
    NMR types from the Chemical Methods Ontology
    """
    _defn = EnumDefinition(
        name="NMRAssayEnum",
        description="NMR types from the Chemical Methods Ontology",
    )

    @classmethod
    def _addvals(cls):
        setattr(cls, "CHMO:0000595",
            PermissibleValue(
                text="CHMO:0000595",
                description="""Spectroscopy where the energy states of 13C nuclei placed in a static magnetic field are interrogated by inducing transitions between the states via radio frequency irradiation. Each experiment consists of a sequence of radio frequency pulses with delay periods in between them.""",
                meaning=CHMO["0000595"]))

class QUDTQuantityKindEnum(EnumDefinitionImpl):
    """
    Possible kinds of quantifiable attribute types provided as QUDT QualityKind instances.
    """
    _defn = EnumDefinition(
        name="QUDTQuantityKindEnum",
        description="Possible kinds of quantifiable attribute types provided as QUDT QualityKind instances.",
    )

class QUDTUnitEnum(EnumDefinitionImpl):
    """
    Possible kinds of QUDT unit instances.
    """
    _defn = EnumDefinition(
        name="QUDTUnitEnum",
        description="Possible kinds of QUDT unit instances.",
    )

class DatasetThemes(EnumDefinitionImpl):

    Energy = PermissibleValue(
        text="Energy",
        meaning=None)
    Environment = PermissibleValue(
        text="Environment",
        meaning=None)
    Health = PermissibleValue(
        text="Health",
        meaning=None)
    Transport = PermissibleValue(
        text="Transport",
        meaning=None)

    _defn = EnumDefinition(
        name="DatasetThemes",
    )

    @classmethod
    def _addvals(cls):
        setattr(cls, "Agriculture, fisheries, forestry and food",
            PermissibleValue(
                text="Agriculture, fisheries, forestry and food",
                meaning=None))
        setattr(cls, "Economy and finance",
            PermissibleValue(
                text="Economy and finance",
                meaning=None))
        setattr(cls, "Education, culture and sport",
            PermissibleValue(
                text="Education, culture and sport",
                meaning=None))
        setattr(cls, "Government and public sector",
            PermissibleValue(
                text="Government and public sector",
                meaning=None))
        setattr(cls, "International issues",
            PermissibleValue(
                text="International issues",
                meaning=None))
        setattr(cls, "Justice, legal system and public safety",
            PermissibleValue(
                text="Justice, legal system and public safety",
                meaning=None))
        setattr(cls, "Provisional data",
            PermissibleValue(
                text="Provisional data",
                meaning=None))
        setattr(cls, "Regions and cities",
            PermissibleValue(
                text="Regions and cities",
                meaning=None))
        setattr(cls, "Population and society",
            PermissibleValue(
                text="Population and society",
                meaning=None))
        setattr(cls, "Science and technology",
            PermissibleValue(
                text="Science and technology",
                meaning=None))

class TopLevelMediaTypes(EnumDefinitionImpl):

    application = PermissibleValue(text="application")
    audio = PermissibleValue(text="audio")
    example = PermissibleValue(text="example")
    font = PermissibleValue(text="font")
    haptics = PermissibleValue(text="haptics")
    image = PermissibleValue(text="image")
    message = PermissibleValue(text="message")
    model = PermissibleValue(text="model")
    multipart = PermissibleValue(text="multipart")
    text = PermissibleValue(text="text")
    video = PermissibleValue(text="video")

    _defn = EnumDefinition(
        name="TopLevelMediaTypes",
    )

# Slots
class slots:
    pass

slots.has_mass = Slot(uri=DCTERMS.relation, name="has_mass", curie=DCTERMS.curie('relation'),
                   model_uri=NFDI4C.has_mass, domain=None, range=Optional[Union[dict, Mass]])

slots.has_length = Slot(uri=DCTERMS.relation, name="has_length", curie=DCTERMS.curie('relation'),
                   model_uri=NFDI4C.has_length, domain=None, range=Optional[Union[dict, Length]])

slots.has_width = Slot(uri=DCTERMS.relation, name="has_width", curie=DCTERMS.curie('relation'),
                   model_uri=NFDI4C.has_width, domain=None, range=Optional[Union[dict, Width]])

slots.has_height = Slot(uri=DCTERMS.relation, name="has_height", curie=DCTERMS.curie('relation'),
                   model_uri=NFDI4C.has_height, domain=None, range=Optional[Union[dict, Height]])

slots.has_surface_area = Slot(uri=DCTERMS.relation, name="has_surface_area", curie=DCTERMS.curie('relation'),
                   model_uri=NFDI4C.has_surface_area, domain=None, range=Optional[Union[dict, SurfaceArea]])

slots.has_volume = Slot(uri=DCTERMS.relation, name="has_volume", curie=DCTERMS.curie('relation'),
                   model_uri=NFDI4C.has_volume, domain=None, range=Optional[Union[dict, Volume]])

slots.was_derived_from = Slot(uri=PROV.wasDerivedFrom, name="was_derived_from", curie=PROV.curie('wasDerivedFrom'),
                   model_uri=NFDI4C.was_derived_from, domain=None, range=Optional[str])

slots.id = Slot(uri=DCTERMS.identifier, name="id", curie=DCTERMS.curie('identifier'),
                   model_uri=NFDI4C.id, domain=None, range=URIRef)

slots.rdf_type = Slot(uri=RDF.type, name="rdf_type", curie=RDF.curie('type'),
                   model_uri=NFDI4C.rdf_type, domain=None, range=Optional[Union[dict, DefinedTerm]])

slots.evaluated_entity = Slot(uri=PROV.used, name="evaluated_entity", curie=PROV.curie('used'),
                   model_uri=NFDI4C.evaluated_entity, domain=None, range=Optional[Union[Dict[Union[str, EvaluatedEntityId], Union[dict, EvaluatedEntity]], List[Union[dict, EvaluatedEntity]]]])

slots.evaluated_activity = Slot(uri=PROV.wasInformedBy, name="evaluated_activity", curie=PROV.curie('wasInformedBy'),
                   model_uri=NFDI4C.evaluated_activity, domain=None, range=Optional[Union[Dict[Union[str, EvaluatedActivityId], Union[dict, EvaluatedActivity]], List[Union[dict, EvaluatedActivity]]]])

slots.used_tool = Slot(uri=PROV.used, name="used_tool", curie=PROV.curie('used'),
                   model_uri=NFDI4C.used_tool, domain=None, range=Optional[Union[Union[dict, Tool], List[Union[dict, Tool]]]])

slots.realized_plan = Slot(uri=PROV.used, name="realized_plan", curie=PROV.curie('used'),
                   model_uri=NFDI4C.realized_plan, domain=None, range=Optional[Union[dict, Plan]])

slots.occurred_in = Slot(uri=BFO['0000066'], name="occurred_in", curie=BFO.curie('0000066'),
                   model_uri=NFDI4C.occurred_in, domain=None, range=Optional[Union[dict, Environment]])

slots.has_qualitative_attribute = Slot(uri=DCTERMS.relation, name="has_qualitative_attribute", curie=DCTERMS.curie('relation'),
                   model_uri=NFDI4C.has_qualitative_attribute, domain=None, range=Optional[Union[Union[dict, QualitativeAttribute], List[Union[dict, QualitativeAttribute]]]])

slots.has_quantitative_attribute = Slot(uri=DCTERMS.relation, name="has_quantitative_attribute", curie=DCTERMS.curie('relation'),
                   model_uri=NFDI4C.has_quantitative_attribute, domain=None, range=Optional[Union[Union[dict, QuantitativeAttribute], List[Union[dict, QuantitativeAttribute]]]])

slots.value = Slot(uri=PROV.value, name="value", curie=PROV.curie('value'),
                   model_uri=NFDI4C.value, domain=None, range=Optional[str])

slots.describes_entity = Slot(uri=DCTERMS.relation, name="describes_entity", curie=DCTERMS.curie('relation'),
                   model_uri=NFDI4C.describes_entity, domain=None, range=Optional[Union[Dict[Union[str, EvaluatedEntityId], Union[dict, EvaluatedEntity]], List[Union[dict, EvaluatedEntity]]]])

slots.describes_activity = Slot(uri=DCTERMS.relation, name="describes_activity", curie=DCTERMS.curie('relation'),
                   model_uri=NFDI4C.describes_activity, domain=None, range=Optional[Union[Dict[Union[str, EvaluatedActivityId], Union[dict, EvaluatedActivity]], List[Union[dict, EvaluatedActivity]]]])

slots.access_URL = Slot(uri=DCAT.accessURL, name="access_URL", curie=DCAT.curie('accessURL'),
                   model_uri=NFDI4C.access_URL, domain=None, range=Optional[str])

slots.access_rights = Slot(uri=DCTERMS.accessRights, name="access_rights", curie=DCTERMS.curie('accessRights'),
                   model_uri=NFDI4C.access_rights, domain=None, range=Optional[str])

slots.access_service = Slot(uri=DCAT.accessService, name="access_service", curie=DCAT.curie('accessService'),
                   model_uri=NFDI4C.access_service, domain=None, range=Optional[str])

slots.algorithm = Slot(uri=SPDX.algorithm, name="algorithm", curie=SPDX.curie('algorithm'),
                   model_uri=NFDI4C.algorithm, domain=None, range=Optional[str])

slots.applicable_legislation = Slot(uri=DCATAP.applicableLegislation, name="applicable_legislation", curie=DCATAP.curie('applicableLegislation'),
                   model_uri=NFDI4C.applicable_legislation, domain=None, range=Optional[str])

slots.application_profile = Slot(uri=DCTERMS.conformsTo, name="application_profile", curie=DCTERMS.curie('conformsTo'),
                   model_uri=NFDI4C.application_profile, domain=None, range=Optional[str])

slots.availability = Slot(uri=DCATAP.availability, name="availability", curie=DCATAP.curie('availability'),
                   model_uri=NFDI4C.availability, domain=None, range=Optional[str])

slots.bbox = Slot(uri=DCAT.bbox, name="bbox", curie=DCAT.curie('bbox'),
                   model_uri=NFDI4C.bbox, domain=None, range=Optional[str])

slots.beginning = Slot(uri=TIME.hasBeginning, name="beginning", curie=TIME.curie('hasBeginning'),
                   model_uri=NFDI4C.beginning, domain=None, range=Optional[str])

slots.byte_size = Slot(uri=DCAT.byteSize, name="byte_size", curie=DCAT.curie('byteSize'),
                   model_uri=NFDI4C.byte_size, domain=None, range=Optional[str])

slots.catalogue = Slot(uri=DCAT.catalog, name="catalogue", curie=DCAT.curie('catalog'),
                   model_uri=NFDI4C.catalogue, domain=None, range=Optional[str])

slots.centroid = Slot(uri=DCAT.centroid, name="centroid", curie=DCAT.curie('centroid'),
                   model_uri=NFDI4C.centroid, domain=None, range=Optional[str])

slots.change_type = Slot(uri=ADMS.status, name="change_type", curie=ADMS.curie('status'),
                   model_uri=NFDI4C.change_type, domain=None, range=Optional[str])

slots.checksum = Slot(uri=SPDX.checksum, name="checksum", curie=SPDX.curie('checksum'),
                   model_uri=NFDI4C.checksum, domain=None, range=Optional[str])

slots.checksum_value = Slot(uri=SPDX.checksumValue, name="checksum_value", curie=SPDX.curie('checksumValue'),
                   model_uri=NFDI4C.checksum_value, domain=None, range=Optional[str])

slots.compression_format = Slot(uri=DCAT.compressFormat, name="compression_format", curie=DCAT.curie('compressFormat'),
                   model_uri=NFDI4C.compression_format, domain=None, range=Optional[str])

slots.conforms_to = Slot(uri=DCTERMS.conformsTo, name="conforms_to", curie=DCTERMS.curie('conformsTo'),
                   model_uri=NFDI4C.conforms_to, domain=None, range=Optional[str])

slots.contact_point = Slot(uri=DCAT.contactPoint, name="contact_point", curie=DCAT.curie('contactPoint'),
                   model_uri=NFDI4C.contact_point, domain=None, range=Optional[str])

slots.creator = Slot(uri=DCTERMS.creator, name="creator", curie=DCTERMS.curie('creator'),
                   model_uri=NFDI4C.creator, domain=None, range=Optional[str])

slots.dataset_distribution = Slot(uri=DCAT.distribution, name="dataset_distribution", curie=DCAT.curie('distribution'),
                   model_uri=NFDI4C.dataset_distribution, domain=None, range=Optional[str])

slots.description = Slot(uri=DCTERMS.description, name="description", curie=DCTERMS.curie('description'),
                   model_uri=NFDI4C.description, domain=None, range=Optional[str])

slots.documentation = Slot(uri=FOAF.page, name="documentation", curie=FOAF.curie('page'),
                   model_uri=NFDI4C.documentation, domain=None, range=Optional[str])

slots.download_URL = Slot(uri=DCAT.downloadURL, name="download_URL", curie=DCAT.curie('downloadURL'),
                   model_uri=NFDI4C.download_URL, domain=None, range=Optional[str])

slots.end = Slot(uri=TIME.hasEnd, name="end", curie=TIME.curie('hasEnd'),
                   model_uri=NFDI4C.end, domain=None, range=Optional[str])

slots.end_date = Slot(uri=DCAT.endDate, name="end_date", curie=DCAT.curie('endDate'),
                   model_uri=NFDI4C.end_date, domain=None, range=Optional[str])

slots.endpoint_URL = Slot(uri=DCAT.endpointURL, name="endpoint_URL", curie=DCAT.curie('endpointURL'),
                   model_uri=NFDI4C.endpoint_URL, domain=None, range=Optional[str])

slots.endpoint_description = Slot(uri=DCAT.endpointDescription, name="endpoint_description", curie=DCAT.curie('endpointDescription'),
                   model_uri=NFDI4C.endpoint_description, domain=None, range=Optional[str])

slots.format = Slot(uri=DCTERMS.format, name="format", curie=DCTERMS.curie('format'),
                   model_uri=NFDI4C.format, domain=None, range=Optional[str])

slots.frequency = Slot(uri=DCTERMS.accrualPeriodicity, name="frequency", curie=DCTERMS.curie('accrualPeriodicity'),
                   model_uri=NFDI4C.frequency, domain=None, range=Optional[str])

slots.geographical_coverage = Slot(uri=DCTERMS.spatial, name="geographical_coverage", curie=DCTERMS.curie('spatial'),
                   model_uri=NFDI4C.geographical_coverage, domain=None, range=Optional[str])

slots.geometry = Slot(uri=LOCN.geometry, name="geometry", curie=LOCN.curie('geometry'),
                   model_uri=NFDI4C.geometry, domain=None, range=Optional[str])

slots.had_role = Slot(uri=DCAT.hadRole, name="had_role", curie=DCAT.curie('hadRole'),
                   model_uri=NFDI4C.had_role, domain=None, range=Optional[str])

slots.has_dataset = Slot(uri=DCAT.dataset, name="has_dataset", curie=DCAT.curie('dataset'),
                   model_uri=NFDI4C.has_dataset, domain=None, range=Optional[str])

slots.has_part = Slot(uri=DCTERMS.hasPart, name="has_part", curie=DCTERMS.curie('hasPart'),
                   model_uri=NFDI4C.has_part, domain=None, range=Optional[str])

slots.has_policy = Slot(uri=ODRL.hasPolicy, name="has_policy", curie=ODRL.curie('hasPolicy'),
                   model_uri=NFDI4C.has_policy, domain=None, range=Optional[str])

slots.has_version = Slot(uri=DCAT.hasVersion, name="has_version", curie=DCAT.curie('hasVersion'),
                   model_uri=NFDI4C.has_version, domain=None, range=Optional[str])

slots.homepage = Slot(uri=FOAF.homepage, name="homepage", curie=FOAF.curie('homepage'),
                   model_uri=NFDI4C.homepage, domain=None, range=Optional[str])

slots.identifier = Slot(uri=DCTERMS.identifier, name="identifier", curie=DCTERMS.curie('identifier'),
                   model_uri=NFDI4C.identifier, domain=None, range=Optional[str])

slots.in_series = Slot(uri=DCAT.inSeries, name="in_series", curie=DCAT.curie('inSeries'),
                   model_uri=NFDI4C.in_series, domain=None, range=Optional[str])

slots.is_referenced_by = Slot(uri=DCTERMS.isReferencedBy, name="is_referenced_by", curie=DCTERMS.curie('isReferencedBy'),
                   model_uri=NFDI4C.is_referenced_by, domain=None, range=Optional[str])

slots.keyword = Slot(uri=DCAT.keyword, name="keyword", curie=DCAT.curie('keyword'),
                   model_uri=NFDI4C.keyword, domain=None, range=Optional[str])

slots.landing_page = Slot(uri=DCAT.landingPage, name="landing_page", curie=DCAT.curie('landingPage'),
                   model_uri=NFDI4C.landing_page, domain=None, range=Optional[str])

slots.language = Slot(uri=DCTERMS.language, name="language", curie=DCTERMS.curie('language'),
                   model_uri=NFDI4C.language, domain=None, range=Optional[str])

slots.licence = Slot(uri=DCTERMS.license, name="licence", curie=DCTERMS.curie('license'),
                   model_uri=NFDI4C.licence, domain=None, range=Optional[str])

slots.linked_schemas = Slot(uri=DCTERMS.conformsTo, name="linked_schemas", curie=DCTERMS.curie('conformsTo'),
                   model_uri=NFDI4C.linked_schemas, domain=None, range=Optional[str])

slots.listing_date = Slot(uri=DCTERMS.issued, name="listing_date", curie=DCTERMS.curie('issued'),
                   model_uri=NFDI4C.listing_date, domain=None, range=Optional[str])

slots.media_type = Slot(uri=DCAT.mediaType, name="media_type", curie=DCAT.curie('mediaType'),
                   model_uri=NFDI4C.media_type, domain=None, range=Optional[str])

slots.modification_date = Slot(uri=DCTERMS.modified, name="modification_date", curie=DCTERMS.curie('modified'),
                   model_uri=NFDI4C.modification_date, domain=None, range=Optional[str])

slots.name = Slot(uri=FOAF.name, name="name", curie=FOAF.curie('name'),
                   model_uri=NFDI4C.name, domain=None, range=Optional[str])

slots.notation = Slot(uri=SKOS.notation, name="notation", curie=SKOS.curie('notation'),
                   model_uri=NFDI4C.notation, domain=None, range=Optional[str])

slots.other_identifier = Slot(uri=ADMS.identifier, name="other_identifier", curie=ADMS.curie('identifier'),
                   model_uri=NFDI4C.other_identifier, domain=None, range=Optional[str])

slots.packaging_format = Slot(uri=DCAT.packageFormat, name="packaging_format", curie=DCAT.curie('packageFormat'),
                   model_uri=NFDI4C.packaging_format, domain=None, range=Optional[str])

slots.preferred_label = Slot(uri=SKOS.prefLabel, name="preferred_label", curie=SKOS.curie('prefLabel'),
                   model_uri=NFDI4C.preferred_label, domain=None, range=Optional[str])

slots.primary_topic = Slot(uri=FOAF.primaryTopic, name="primary_topic", curie=FOAF.curie('primaryTopic'),
                   model_uri=NFDI4C.primary_topic, domain=None, range=Optional[str])

slots.provenance = Slot(uri=DCTERMS.provenance, name="provenance", curie=DCTERMS.curie('provenance'),
                   model_uri=NFDI4C.provenance, domain=None, range=Optional[str])

slots.publisher = Slot(uri=DCTERMS.publisher, name="publisher", curie=DCTERMS.curie('publisher'),
                   model_uri=NFDI4C.publisher, domain=None, range=Optional[str])

slots.qualified_attribution = Slot(uri=PROV.qualifiedAttribution, name="qualified_attribution", curie=PROV.curie('qualifiedAttribution'),
                   model_uri=NFDI4C.qualified_attribution, domain=None, range=Optional[str])

slots.qualified_relation = Slot(uri=DCAT.qualifiedRelation, name="qualified_relation", curie=DCAT.curie('qualifiedRelation'),
                   model_uri=NFDI4C.qualified_relation, domain=None, range=Optional[str])

slots.record = Slot(uri=DCAT.record, name="record", curie=DCAT.curie('record'),
                   model_uri=NFDI4C.record, domain=None, range=Optional[str])

slots.related_resource = Slot(uri=DCTERMS.relation, name="related_resource", curie=DCTERMS.curie('relation'),
                   model_uri=NFDI4C.related_resource, domain=None, range=Optional[str])

slots.relation = Slot(uri=DCTERMS.relation, name="relation", curie=DCTERMS.curie('relation'),
                   model_uri=NFDI4C.relation, domain=None, range=Optional[str])

slots.release_date = Slot(uri=DCTERMS.issued, name="release_date", curie=DCTERMS.curie('issued'),
                   model_uri=NFDI4C.release_date, domain=None, range=Optional[str])

slots.rights = Slot(uri=DCTERMS.rights, name="rights", curie=DCTERMS.curie('rights'),
                   model_uri=NFDI4C.rights, domain=None, range=Optional[str])

slots.sample = Slot(uri=ADMS.sample, name="sample", curie=ADMS.curie('sample'),
                   model_uri=NFDI4C.sample, domain=None, range=Optional[str])

slots.serves_dataset = Slot(uri=DCAT.servesDataset, name="serves_dataset", curie=DCAT.curie('servesDataset'),
                   model_uri=NFDI4C.serves_dataset, domain=None, range=Optional[str])

slots.service = Slot(uri=DCAT.service, name="service", curie=DCAT.curie('service'),
                   model_uri=NFDI4C.service, domain=None, range=Optional[str])

slots.source = Slot(uri=DCTERMS.source, name="source", curie=DCTERMS.curie('source'),
                   model_uri=NFDI4C.source, domain=None, range=Optional[str])

slots.source_metadata = Slot(uri=DCTERMS.source, name="source_metadata", curie=DCTERMS.curie('source'),
                   model_uri=NFDI4C.source_metadata, domain=None, range=Optional[str])

slots.spatial_resolution = Slot(uri=DCAT.spatialResolutionInMeters, name="spatial_resolution", curie=DCAT.curie('spatialResolutionInMeters'),
                   model_uri=NFDI4C.spatial_resolution, domain=None, range=Optional[str])

slots.start_date = Slot(uri=DCAT.startDate, name="start_date", curie=DCAT.curie('startDate'),
                   model_uri=NFDI4C.start_date, domain=None, range=Optional[str])

slots.status = Slot(uri=ADMS.status, name="status", curie=ADMS.curie('status'),
                   model_uri=NFDI4C.status, domain=None, range=Optional[str])

slots.temporal_coverage = Slot(uri=DCTERMS.temporal, name="temporal_coverage", curie=DCTERMS.curie('temporal'),
                   model_uri=NFDI4C.temporal_coverage, domain=None, range=Optional[str])

slots.temporal_resolution = Slot(uri=DCAT.temporalResolution, name="temporal_resolution", curie=DCAT.curie('temporalResolution'),
                   model_uri=NFDI4C.temporal_resolution, domain=None, range=Optional[str])

slots.theme = Slot(uri=DCAT.theme, name="theme", curie=DCAT.curie('theme'),
                   model_uri=NFDI4C.theme, domain=None, range=Optional[str])

slots.themes = Slot(uri=DCAT.themeTaxonomy, name="themes", curie=DCAT.curie('themeTaxonomy'),
                   model_uri=NFDI4C.themes, domain=None, range=Optional[str])

slots.title = Slot(uri=DCTERMS.title, name="title", curie=DCTERMS.curie('title'),
                   model_uri=NFDI4C.title, domain=None, range=Optional[str])

slots.type = Slot(uri=DCTERMS.type, name="type", curie=DCTERMS.curie('type'),
                   model_uri=NFDI4C.type, domain=None, range=Optional[str])

slots.version = Slot(uri=DCAT.version, name="version", curie=DCAT.curie('version'),
                   model_uri=NFDI4C.version, domain=None, range=Optional[str])

slots.version_notes = Slot(uri=ADMS.versionNotes, name="version_notes", curie=ADMS.curie('versionNotes'),
                   model_uri=NFDI4C.version_notes, domain=None, range=Optional[str])

slots.was_generated_by = Slot(uri=PROV.wasGeneratedBy, name="was_generated_by", curie=PROV.curie('wasGeneratedBy'),
                   model_uri=NFDI4C.was_generated_by, domain=None, range=Optional[str])

slots.chemicalSubstance__composed_of = Slot(uri=RO['0002180'], name="chemicalSubstance__composed_of", curie=RO.curie('0002180'),
                   model_uri=NFDI4C.chemicalSubstance__composed_of, domain=None, range=Optional[Union[Union[dict, ChemicalEntity], List[Union[dict, ChemicalEntity]]]])

slots.chemicalEntity__inchi = Slot(uri=CHEMINF['000143'], name="chemicalEntity__inchi", curie=CHEMINF.curie('000143'),
                   model_uri=NFDI4C.chemicalEntity__inchi, domain=None, range=Optional[Union[dict, InChi]])

slots.chemicalEntity__inchikey = Slot(uri=CHEMINF['000143'], name="chemicalEntity__inchikey", curie=CHEMINF.curie('000143'),
                   model_uri=NFDI4C.chemicalEntity__inchikey, domain=None, range=Optional[Union[dict, InChIKey]])

slots.chemicalEntity__smiles = Slot(uri=CHEMINF['000143'], name="chemicalEntity__smiles", curie=CHEMINF.curie('000143'),
                   model_uri=NFDI4C.chemicalEntity__smiles, domain=None, range=Optional[Union[dict, SMILES]])

slots.chemicalEntity__iupac_formula = Slot(uri=CHEMINF['000143'], name="chemicalEntity__iupac_formula", curie=CHEMINF.curie('000143'),
                   model_uri=NFDI4C.chemicalEntity__iupac_formula, domain=None, range=Optional[Union[dict, IUPACChemicalFormula]])

slots.definedTerm__from_CV = Slot(uri=SCHEMA.inDefinedTermSet, name="definedTerm__from_CV", curie=SCHEMA.curie('inDefinedTermSet'),
                   model_uri=NFDI4C.definedTerm__from_CV, domain=None, range=Optional[Union[str, URIorCURIE]])

slots.quantitativeAttribute__has_quantity_type = Slot(uri=QUDT.hasQuantityKind, name="quantitativeAttribute__has_quantity_type", curie=QUDT.curie('hasQuantityKind'),
                   model_uri=NFDI4C.quantitativeAttribute__has_quantity_type, domain=None, range=Union[str, DefinedTermId])

slots.quantitativeAttribute__unit = Slot(uri=QUDT.unit, name="quantitativeAttribute__unit", curie=QUDT.curie('unit'),
                   model_uri=NFDI4C.quantitativeAttribute__unit, domain=None, range=Optional[Union[str, DefinedTermId]])

slots.NMRSpectrum_was_generated_by = Slot(uri=PROV.wasGeneratedBy, name="NMRSpectrum_was_generated_by", curie=PROV.curie('wasGeneratedBy'),
                   model_uri=NFDI4C.NMRSpectrum_was_generated_by, domain=NMRSpectrum, range=Optional[Union[Union[dict, "NMRSpectroscopy"], List[Union[dict, "NMRSpectroscopy"]]]])

slots.NMRAnalysisDataset_was_generated_by = Slot(uri=PROV.wasGeneratedBy, name="NMRAnalysisDataset_was_generated_by", curie=PROV.curie('wasGeneratedBy'),
                   model_uri=NFDI4C.NMRAnalysisDataset_was_generated_by, domain=NMRAnalysisDataset, range=Optional[Union[Union[dict, NMRSpectralAnalysis], List[Union[dict, NMRSpectralAnalysis]]]])

slots.NMRAnalysisDataset_describes_entity = Slot(uri=DCTERMS.relation, name="NMRAnalysisDataset_describes_entity", curie=DCTERMS.curie('relation'),
                   model_uri=NFDI4C.NMRAnalysisDataset_describes_entity, domain=NMRAnalysisDataset, range=Optional[Union[Dict[Union[str, ChemicalSampleId], Union[dict, ChemicalSample]], List[Union[dict, ChemicalSample]]]])

slots.NMRSpectralAnalysis_evaluated_entity = Slot(uri=PROV.used, name="NMRSpectralAnalysis_evaluated_entity", curie=PROV.curie('used'),
                   model_uri=NFDI4C.NMRSpectralAnalysis_evaluated_entity, domain=NMRSpectralAnalysis, range=Optional[Union[Dict[Union[str, NMRSpectrumId], Union[dict, NMRSpectrum]], List[Union[dict, NMRSpectrum]]]])

slots.NMRSpectroscopy_evaluated_entity = Slot(uri=PROV.used, name="NMRSpectroscopy_evaluated_entity", curie=PROV.curie('used'),
                   model_uri=NFDI4C.NMRSpectroscopy_evaluated_entity, domain=NMRSpectroscopy, range=Optional[Union[Dict[Union[str, ChemicalSampleId], Union[dict, ChemicalSample]], List[Union[dict, ChemicalSample]]]])

slots.NMRSpectroscopy_rdf_type = Slot(uri=RDF.type, name="NMRSpectroscopy_rdf_type", curie=RDF.curie('type'),
                   model_uri=NFDI4C.NMRSpectroscopy_rdf_type, domain=NMRSpectroscopy, range=Optional[Union[dict, DefinedTerm]])

slots.MaterialSample_was_derived_from = Slot(uri=PROV.wasDerivedFrom, name="MaterialSample_was_derived_from", curie=PROV.curie('wasDerivedFrom'),
                   model_uri=NFDI4C.MaterialSample_was_derived_from, domain=MaterialSample, range=Optional[Union[str, MaterialSampleId]])

slots.ClassifierMixin_type = Slot(uri=DCTERMS.type, name="ClassifierMixin_type", curie=DCTERMS.curie('type'),
                   model_uri=NFDI4C.ClassifierMixin_type, domain=None, range=Optional[Union[dict, "DefinedTerm"]])

slots.DefinedTerm_title = Slot(uri=SCHEMA.name, name="DefinedTerm_title", curie=SCHEMA.curie('name'),
                   model_uri=NFDI4C.DefinedTerm_title, domain=DefinedTerm, range=Optional[str])

slots.ResearchDataset_was_generated_by = Slot(uri=PROV.wasGeneratedBy, name="ResearchDataset_was_generated_by", curie=PROV.curie('wasGeneratedBy'),
                   model_uri=NFDI4C.ResearchDataset_was_generated_by, domain=ResearchDataset, range=Union[Union[dict, DataCreatingActivity], List[Union[dict, DataCreatingActivity]]])

slots.AnalysisDataset_was_generated_by = Slot(uri=PROV.wasGeneratedBy, name="AnalysisDataset_was_generated_by", curie=PROV.curie('wasGeneratedBy'),
                   model_uri=NFDI4C.AnalysisDataset_was_generated_by, domain=AnalysisDataset, range=Union[Union[dict, DataAnalysis], List[Union[dict, DataAnalysis]]])

slots.ResearchCatalog_has_dataset = Slot(uri=DCAT.dataset, name="ResearchCatalog_has_dataset", curie=DCAT.curie('dataset'),
                   model_uri=NFDI4C.ResearchCatalog_has_dataset, domain=ResearchCatalog, range=Optional[Union[str, ResearchDatasetId]])

slots.DataCreatingActivity_has_part = Slot(uri=DCTERMS.hasPart, name="DataCreatingActivity_has_part", curie=DCTERMS.curie('hasPart'),
                   model_uri=NFDI4C.DataCreatingActivity_has_part, domain=DataCreatingActivity, range=Optional[Union[dict, Activity]])

slots.DataCreatingActivity_other_identifier = Slot(uri=ADMS.identifier, name="DataCreatingActivity_other_identifier", curie=ADMS.curie('identifier'),
                   model_uri=NFDI4C.DataCreatingActivity_other_identifier, domain=DataCreatingActivity, range=Optional[Union[Union[dict, "Identifier"], List[Union[dict, "Identifier"]]]])

slots.DataAnalysis_evaluated_entity = Slot(uri=PROV.used, name="DataAnalysis_evaluated_entity", curie=PROV.curie('used'),
                   model_uri=NFDI4C.DataAnalysis_evaluated_entity, domain=DataAnalysis, range=Optional[Union[Dict[Union[str, AnalysisSourceDataId], Union[dict, AnalysisSourceData]], List[Union[dict, AnalysisSourceData]]]])

slots.EvaluatedEntity_other_identifier = Slot(uri=ADMS.identifier, name="EvaluatedEntity_other_identifier", curie=ADMS.curie('identifier'),
                   model_uri=NFDI4C.EvaluatedEntity_other_identifier, domain=EvaluatedEntity, range=Optional[Union[Union[dict, "Identifier"], List[Union[dict, "Identifier"]]]])

slots.EvaluatedEntity_was_generated_by = Slot(uri=PROV.wasGeneratedBy, name="EvaluatedEntity_was_generated_by", curie=PROV.curie('wasGeneratedBy'),
                   model_uri=NFDI4C.EvaluatedEntity_was_generated_by, domain=EvaluatedEntity, range=Optional[Union[Union[dict, "Activity"], List[Union[dict, "Activity"]]]])

slots.EvaluatedEntity_has_part = Slot(uri=DCTERMS.hasPart, name="EvaluatedEntity_has_part", curie=DCTERMS.curie('hasPart'),
                   model_uri=NFDI4C.EvaluatedEntity_has_part, domain=EvaluatedEntity, range=Optional[Union[str, EvaluatedEntityId]])

slots.AnalysisSourceData_was_generated_by = Slot(uri=PROV.wasGeneratedBy, name="AnalysisSourceData_was_generated_by", curie=PROV.curie('wasGeneratedBy'),
                   model_uri=NFDI4C.AnalysisSourceData_was_generated_by, domain=AnalysisSourceData, range=Optional[Union[Union[dict, "DataCreatingActivity"], List[Union[dict, "DataCreatingActivity"]]]])

slots.EvaluatedActivity_other_identifier = Slot(uri=ADMS.identifier, name="EvaluatedActivity_other_identifier", curie=ADMS.curie('identifier'),
                   model_uri=NFDI4C.EvaluatedActivity_other_identifier, domain=EvaluatedActivity, range=Optional[Union[Union[dict, "Identifier"], List[Union[dict, "Identifier"]]]])

slots.EvaluatedActivity_has_part = Slot(uri=DCTERMS.hasPart, name="EvaluatedActivity_has_part", curie=DCTERMS.curie('hasPart'),
                   model_uri=NFDI4C.EvaluatedActivity_has_part, domain=EvaluatedActivity, range=Optional[Union[str, EvaluatedActivityId]])

slots.Tool_has_part = Slot(uri=DCTERMS.hasPart, name="Tool_has_part", curie=DCTERMS.curie('hasPart'),
                   model_uri=NFDI4C.Tool_has_part, domain=Tool, range=Optional[Union[Union[dict, "Tool"], List[Union[dict, "Tool"]]]])

slots.Tool_other_identifier = Slot(uri=ADMS.identifier, name="Tool_other_identifier", curie=ADMS.curie('identifier'),
                   model_uri=NFDI4C.Tool_other_identifier, domain=Tool, range=Optional[Union[Union[dict, "Identifier"], List[Union[dict, "Identifier"]]]])

slots.Environment_other_identifier = Slot(uri=ADMS.identifier, name="Environment_other_identifier", curie=ADMS.curie('identifier'),
                   model_uri=NFDI4C.Environment_other_identifier, domain=Environment, range=Optional[Union[Union[dict, "Identifier"], List[Union[dict, "Identifier"]]]])

slots.QualitativeAttribute_value = Slot(uri=PROV.value, name="QualitativeAttribute_value", curie=PROV.curie('value'),
                   model_uri=NFDI4C.QualitativeAttribute_value, domain=QualitativeAttribute, range=str)

slots.QuantitativeAttribute_value = Slot(uri=PROV.value, name="QuantitativeAttribute_value", curie=PROV.curie('value'),
                   model_uri=NFDI4C.QuantitativeAttribute_value, domain=QuantitativeAttribute, range=float)

slots.Agent_name = Slot(uri=FOAF.name, name="Agent_name", curie=FOAF.curie('name'),
                   model_uri=NFDI4C.Agent_name, domain=Agent, range=Union[str, List[str]])

slots.Agent_type = Slot(uri=DCTERMS.type, name="Agent_type", curie=DCTERMS.curie('type'),
                   model_uri=NFDI4C.Agent_type, domain=Agent, range=Optional[Union[dict, "Concept"]])

slots.Catalogue_applicable_legislation = Slot(uri=DCATAP.applicableLegislation, name="Catalogue_applicable_legislation", curie=DCATAP.curie('applicableLegislation'),
                   model_uri=NFDI4C.Catalogue_applicable_legislation, domain=Catalogue, range=Optional[Union[Union[dict, "LegalResource"], List[Union[dict, "LegalResource"]]]])

slots.Catalogue_catalogue = Slot(uri=DCAT.catalog, name="Catalogue_catalogue", curie=DCAT.curie('catalog'),
                   model_uri=NFDI4C.Catalogue_catalogue, domain=Catalogue, range=Optional[Union[Union[dict, "Catalogue"], List[Union[dict, "Catalogue"]]]])

slots.Catalogue_creator = Slot(uri=DCTERMS.creator, name="Catalogue_creator", curie=DCTERMS.curie('creator'),
                   model_uri=NFDI4C.Catalogue_creator, domain=Catalogue, range=Optional[Union[dict, "Agent"]])

slots.Catalogue_description = Slot(uri=DCTERMS.description, name="Catalogue_description", curie=DCTERMS.curie('description'),
                   model_uri=NFDI4C.Catalogue_description, domain=Catalogue, range=Union[str, List[str]])

slots.Catalogue_geographical_coverage = Slot(uri=DCTERMS.spatial, name="Catalogue_geographical_coverage", curie=DCTERMS.curie('spatial'),
                   model_uri=NFDI4C.Catalogue_geographical_coverage, domain=Catalogue, range=Optional[Union[Union[dict, "Location"], List[Union[dict, "Location"]]]])

slots.Catalogue_has_dataset = Slot(uri=DCAT.dataset, name="Catalogue_has_dataset", curie=DCAT.curie('dataset'),
                   model_uri=NFDI4C.Catalogue_has_dataset, domain=Catalogue, range=Optional[Union[Union[dict, "Dataset"], List[Union[dict, "Dataset"]]]])

slots.Catalogue_has_part = Slot(uri=DCTERMS.hasPart, name="Catalogue_has_part", curie=DCTERMS.curie('hasPart'),
                   model_uri=NFDI4C.Catalogue_has_part, domain=Catalogue, range=Optional[Union[Union[dict, "Catalogue"], List[Union[dict, "Catalogue"]]]])

slots.Catalogue_homepage = Slot(uri=FOAF.homepage, name="Catalogue_homepage", curie=FOAF.curie('homepage'),
                   model_uri=NFDI4C.Catalogue_homepage, domain=Catalogue, range=Optional[Union[dict, "Document"]])

slots.Catalogue_language = Slot(uri=DCTERMS.language, name="Catalogue_language", curie=DCTERMS.curie('language'),
                   model_uri=NFDI4C.Catalogue_language, domain=Catalogue, range=Optional[Union[Union[dict, "LinguisticSystem"], List[Union[dict, "LinguisticSystem"]]]])

slots.Catalogue_licence = Slot(uri=DCTERMS.license, name="Catalogue_licence", curie=DCTERMS.curie('license'),
                   model_uri=NFDI4C.Catalogue_licence, domain=Catalogue, range=Optional[Union[dict, "LicenseDocument"]])

slots.Catalogue_modification_date = Slot(uri=DCTERMS.modified, name="Catalogue_modification_date", curie=DCTERMS.curie('modified'),
                   model_uri=NFDI4C.Catalogue_modification_date, domain=Catalogue, range=Optional[str])

slots.Catalogue_publisher = Slot(uri=DCTERMS.publisher, name="Catalogue_publisher", curie=DCTERMS.curie('publisher'),
                   model_uri=NFDI4C.Catalogue_publisher, domain=Catalogue, range=Union[dict, "Agent"])

slots.Catalogue_record = Slot(uri=DCAT.record, name="Catalogue_record", curie=DCAT.curie('record'),
                   model_uri=NFDI4C.Catalogue_record, domain=Catalogue, range=Optional[Union[Union[dict, "CatalogueRecord"], List[Union[dict, "CatalogueRecord"]]]])

slots.Catalogue_release_date = Slot(uri=DCTERMS.issued, name="Catalogue_release_date", curie=DCTERMS.curie('issued'),
                   model_uri=NFDI4C.Catalogue_release_date, domain=Catalogue, range=Optional[str])

slots.Catalogue_rights = Slot(uri=DCTERMS.rights, name="Catalogue_rights", curie=DCTERMS.curie('rights'),
                   model_uri=NFDI4C.Catalogue_rights, domain=Catalogue, range=Optional[Union[dict, "RightsStatement"]])

slots.Catalogue_service = Slot(uri=DCAT.service, name="Catalogue_service", curie=DCAT.curie('service'),
                   model_uri=NFDI4C.Catalogue_service, domain=Catalogue, range=Optional[Union[Union[dict, "DataService"], List[Union[dict, "DataService"]]]])

slots.Catalogue_temporal_coverage = Slot(uri=DCTERMS.temporal, name="Catalogue_temporal_coverage", curie=DCTERMS.curie('temporal'),
                   model_uri=NFDI4C.Catalogue_temporal_coverage, domain=Catalogue, range=Optional[Union[Union[dict, "PeriodOfTime"], List[Union[dict, "PeriodOfTime"]]]])

slots.Catalogue_themes = Slot(uri=DCAT.themeTaxonomy, name="Catalogue_themes", curie=DCAT.curie('themeTaxonomy'),
                   model_uri=NFDI4C.Catalogue_themes, domain=Catalogue, range=Optional[Union[Union[dict, "ConceptScheme"], List[Union[dict, "ConceptScheme"]]]])

slots.Catalogue_title = Slot(uri=DCTERMS.title, name="Catalogue_title", curie=DCTERMS.curie('title'),
                   model_uri=NFDI4C.Catalogue_title, domain=Catalogue, range=Union[str, List[str]])

slots.CatalogueRecord_application_profile = Slot(uri=DCTERMS.conformsTo, name="CatalogueRecord_application_profile", curie=DCTERMS.curie('conformsTo'),
                   model_uri=NFDI4C.CatalogueRecord_application_profile, domain=CatalogueRecord, range=Optional[Union[Union[dict, "Standard"], List[Union[dict, "Standard"]]]])

slots.CatalogueRecord_change_type = Slot(uri=ADMS.status, name="CatalogueRecord_change_type", curie=ADMS.curie('status'),
                   model_uri=NFDI4C.CatalogueRecord_change_type, domain=CatalogueRecord, range=Optional[Union[dict, "Concept"]])

slots.CatalogueRecord_description = Slot(uri=DCTERMS.description, name="CatalogueRecord_description", curie=DCTERMS.curie('description'),
                   model_uri=NFDI4C.CatalogueRecord_description, domain=CatalogueRecord, range=Optional[Union[str, List[str]]])

slots.CatalogueRecord_language = Slot(uri=DCTERMS.language, name="CatalogueRecord_language", curie=DCTERMS.curie('language'),
                   model_uri=NFDI4C.CatalogueRecord_language, domain=CatalogueRecord, range=Optional[Union[Union[dict, "LinguisticSystem"], List[Union[dict, "LinguisticSystem"]]]])

slots.CatalogueRecord_listing_date = Slot(uri=DCTERMS.issued, name="CatalogueRecord_listing_date", curie=DCTERMS.curie('issued'),
                   model_uri=NFDI4C.CatalogueRecord_listing_date, domain=CatalogueRecord, range=Optional[str])

slots.CatalogueRecord_modification_date = Slot(uri=DCTERMS.modified, name="CatalogueRecord_modification_date", curie=DCTERMS.curie('modified'),
                   model_uri=NFDI4C.CatalogueRecord_modification_date, domain=CatalogueRecord, range=str)

slots.CatalogueRecord_primary_topic = Slot(uri=FOAF.primaryTopic, name="CatalogueRecord_primary_topic", curie=FOAF.curie('primaryTopic'),
                   model_uri=NFDI4C.CatalogueRecord_primary_topic, domain=CatalogueRecord, range=Union[dict, "CataloguedResource"])

slots.CatalogueRecord_source_metadata = Slot(uri=DCTERMS.source, name="CatalogueRecord_source_metadata", curie=DCTERMS.curie('source'),
                   model_uri=NFDI4C.CatalogueRecord_source_metadata, domain=CatalogueRecord, range=Optional[Union[dict, "CatalogueRecord"]])

slots.CatalogueRecord_title = Slot(uri=DCTERMS.title, name="CatalogueRecord_title", curie=DCTERMS.curie('title'),
                   model_uri=NFDI4C.CatalogueRecord_title, domain=CatalogueRecord, range=Optional[Union[str, List[str]]])

slots.Checksum_algorithm = Slot(uri=SPDX.algorithm, name="Checksum_algorithm", curie=SPDX.curie('algorithm'),
                   model_uri=NFDI4C.Checksum_algorithm, domain=Checksum, range=Union[dict, "ChecksumAlgorithm"])

slots.Checksum_checksum_value = Slot(uri=SPDX.checksumValue, name="Checksum_checksum_value", curie=SPDX.curie('checksumValue'),
                   model_uri=NFDI4C.Checksum_checksum_value, domain=Checksum, range=str)

slots.Concept_preferred_label = Slot(uri=SKOS.prefLabel, name="Concept_preferred_label", curie=SKOS.curie('prefLabel'),
                   model_uri=NFDI4C.Concept_preferred_label, domain=Concept, range=Union[str, List[str]])

slots.ConceptScheme_title = Slot(uri=DCTERMS.title, name="ConceptScheme_title", curie=DCTERMS.curie('title'),
                   model_uri=NFDI4C.ConceptScheme_title, domain=ConceptScheme, range=Union[str, List[str]])

slots.DataService_access_rights = Slot(uri=DCTERMS.accessRights, name="DataService_access_rights", curie=DCTERMS.curie('accessRights'),
                   model_uri=NFDI4C.DataService_access_rights, domain=DataService, range=Optional[Union[dict, "RightsStatement"]])

slots.DataService_applicable_legislation = Slot(uri=DCATAP.applicableLegislation, name="DataService_applicable_legislation", curie=DCATAP.curie('applicableLegislation'),
                   model_uri=NFDI4C.DataService_applicable_legislation, domain=DataService, range=Optional[Union[Union[dict, "LegalResource"], List[Union[dict, "LegalResource"]]]])

slots.DataService_conforms_to = Slot(uri=DCTERMS.conformsTo, name="DataService_conforms_to", curie=DCTERMS.curie('conformsTo'),
                   model_uri=NFDI4C.DataService_conforms_to, domain=DataService, range=Optional[Union[Union[dict, "Standard"], List[Union[dict, "Standard"]]]])

slots.DataService_contact_point = Slot(uri=DCAT.contactPoint, name="DataService_contact_point", curie=DCAT.curie('contactPoint'),
                   model_uri=NFDI4C.DataService_contact_point, domain=DataService, range=Optional[Union[Union[dict, "Kind"], List[Union[dict, "Kind"]]]])

slots.DataService_description = Slot(uri=DCTERMS.description, name="DataService_description", curie=DCTERMS.curie('description'),
                   model_uri=NFDI4C.DataService_description, domain=DataService, range=Optional[Union[str, List[str]]])

slots.DataService_documentation = Slot(uri=FOAF.page, name="DataService_documentation", curie=FOAF.curie('page'),
                   model_uri=NFDI4C.DataService_documentation, domain=DataService, range=Optional[Union[Union[dict, "Document"], List[Union[dict, "Document"]]]])

slots.DataService_endpoint_URL = Slot(uri=DCAT.endpointURL, name="DataService_endpoint_URL", curie=DCAT.curie('endpointURL'),
                   model_uri=NFDI4C.DataService_endpoint_URL, domain=DataService, range=Union[Union[dict, "Resource"], List[Union[dict, "Resource"]]])

slots.DataService_endpoint_description = Slot(uri=DCAT.endpointDescription, name="DataService_endpoint_description", curie=DCAT.curie('endpointDescription'),
                   model_uri=NFDI4C.DataService_endpoint_description, domain=DataService, range=Optional[Union[Union[dict, "Resource"], List[Union[dict, "Resource"]]]])

slots.DataService_format = Slot(uri=DCTERMS.format, name="DataService_format", curie=DCTERMS.curie('format'),
                   model_uri=NFDI4C.DataService_format, domain=DataService, range=Optional[Union[Union[dict, "MediaTypeOrExtent"], List[Union[dict, "MediaTypeOrExtent"]]]])

slots.DataService_keyword = Slot(uri=DCAT.keyword, name="DataService_keyword", curie=DCAT.curie('keyword'),
                   model_uri=NFDI4C.DataService_keyword, domain=DataService, range=Optional[Union[str, List[str]]])

slots.DataService_landing_page = Slot(uri=DCAT.landingPage, name="DataService_landing_page", curie=DCAT.curie('landingPage'),
                   model_uri=NFDI4C.DataService_landing_page, domain=DataService, range=Optional[Union[Union[dict, "Document"], List[Union[dict, "Document"]]]])

slots.DataService_licence = Slot(uri=DCTERMS.license, name="DataService_licence", curie=DCTERMS.curie('license'),
                   model_uri=NFDI4C.DataService_licence, domain=DataService, range=Optional[Union[dict, "LicenseDocument"]])

slots.DataService_publisher = Slot(uri=DCTERMS.publisher, name="DataService_publisher", curie=DCTERMS.curie('publisher'),
                   model_uri=NFDI4C.DataService_publisher, domain=DataService, range=Optional[Union[dict, "Agent"]])

slots.DataService_serves_dataset = Slot(uri=DCAT.servesDataset, name="DataService_serves_dataset", curie=DCAT.curie('servesDataset'),
                   model_uri=NFDI4C.DataService_serves_dataset, domain=DataService, range=Optional[Union[Union[dict, "Dataset"], List[Union[dict, "Dataset"]]]])

slots.DataService_theme = Slot(uri=DCAT.theme, name="DataService_theme", curie=DCAT.curie('theme'),
                   model_uri=NFDI4C.DataService_theme, domain=DataService, range=Optional[Union[Union[dict, "Concept"], List[Union[dict, "Concept"]]]])

slots.DataService_title = Slot(uri=DCTERMS.title, name="DataService_title", curie=DCTERMS.curie('title'),
                   model_uri=NFDI4C.DataService_title, domain=DataService, range=Union[str, List[str]])

slots.Dataset_access_rights = Slot(uri=DCTERMS.accessRights, name="Dataset_access_rights", curie=DCTERMS.curie('accessRights'),
                   model_uri=NFDI4C.Dataset_access_rights, domain=Dataset, range=Optional[Union[dict, "RightsStatement"]])

slots.Dataset_applicable_legislation = Slot(uri=DCATAP.applicableLegislation, name="Dataset_applicable_legislation", curie=DCATAP.curie('applicableLegislation'),
                   model_uri=NFDI4C.Dataset_applicable_legislation, domain=Dataset, range=Optional[Union[Union[dict, "LegalResource"], List[Union[dict, "LegalResource"]]]])

slots.Dataset_conforms_to = Slot(uri=DCTERMS.conformsTo, name="Dataset_conforms_to", curie=DCTERMS.curie('conformsTo'),
                   model_uri=NFDI4C.Dataset_conforms_to, domain=Dataset, range=Optional[Union[Union[dict, "Standard"], List[Union[dict, "Standard"]]]])

slots.Dataset_contact_point = Slot(uri=DCAT.contactPoint, name="Dataset_contact_point", curie=DCAT.curie('contactPoint'),
                   model_uri=NFDI4C.Dataset_contact_point, domain=Dataset, range=Optional[Union[Union[dict, "Kind"], List[Union[dict, "Kind"]]]])

slots.Dataset_creator = Slot(uri=DCTERMS.creator, name="Dataset_creator", curie=DCTERMS.curie('creator'),
                   model_uri=NFDI4C.Dataset_creator, domain=Dataset, range=Optional[Union[Union[dict, "Agent"], List[Union[dict, "Agent"]]]])

slots.Dataset_dataset_distribution = Slot(uri=DCAT.distribution, name="Dataset_dataset_distribution", curie=DCAT.curie('distribution'),
                   model_uri=NFDI4C.Dataset_dataset_distribution, domain=Dataset, range=Optional[Union[Union[dict, "Distribution"], List[Union[dict, "Distribution"]]]])

slots.Dataset_description = Slot(uri=DCTERMS.description, name="Dataset_description", curie=DCTERMS.curie('description'),
                   model_uri=NFDI4C.Dataset_description, domain=Dataset, range=Union[str, List[str]])

slots.Dataset_documentation = Slot(uri=FOAF.page, name="Dataset_documentation", curie=FOAF.curie('page'),
                   model_uri=NFDI4C.Dataset_documentation, domain=Dataset, range=Optional[Union[Union[dict, "Document"], List[Union[dict, "Document"]]]])

slots.Dataset_frequency = Slot(uri=DCTERMS.accrualPeriodicity, name="Dataset_frequency", curie=DCTERMS.curie('accrualPeriodicity'),
                   model_uri=NFDI4C.Dataset_frequency, domain=Dataset, range=Optional[Union[dict, "Frequency"]])

slots.Dataset_geographical_coverage = Slot(uri=DCTERMS.spatial, name="Dataset_geographical_coverage", curie=DCTERMS.curie('spatial'),
                   model_uri=NFDI4C.Dataset_geographical_coverage, domain=Dataset, range=Optional[Union[Union[dict, "Location"], List[Union[dict, "Location"]]]])

slots.Dataset_has_version = Slot(uri=DCAT.hasVersion, name="Dataset_has_version", curie=DCAT.curie('hasVersion'),
                   model_uri=NFDI4C.Dataset_has_version, domain=Dataset, range=Optional[Union[Union[dict, "Dataset"], List[Union[dict, "Dataset"]]]])

slots.Dataset_identifier = Slot(uri=DCTERMS.identifier, name="Dataset_identifier", curie=DCTERMS.curie('identifier'),
                   model_uri=NFDI4C.Dataset_identifier, domain=Dataset, range=Optional[Union[Union[str, URI], List[Union[str, URI]]]])

slots.Dataset_in_series = Slot(uri=DCAT.inSeries, name="Dataset_in_series", curie=DCAT.curie('inSeries'),
                   model_uri=NFDI4C.Dataset_in_series, domain=Dataset, range=Optional[Union[Union[dict, "DatasetSeries"], List[Union[dict, "DatasetSeries"]]]])

slots.Dataset_is_referenced_by = Slot(uri=DCTERMS.isReferencedBy, name="Dataset_is_referenced_by", curie=DCTERMS.curie('isReferencedBy'),
                   model_uri=NFDI4C.Dataset_is_referenced_by, domain=Dataset, range=Optional[Union[Union[dict, "Resource"], List[Union[dict, "Resource"]]]])

slots.Dataset_keyword = Slot(uri=DCAT.keyword, name="Dataset_keyword", curie=DCAT.curie('keyword'),
                   model_uri=NFDI4C.Dataset_keyword, domain=Dataset, range=Optional[Union[str, List[str]]])

slots.Dataset_landing_page = Slot(uri=DCAT.landingPage, name="Dataset_landing_page", curie=DCAT.curie('landingPage'),
                   model_uri=NFDI4C.Dataset_landing_page, domain=Dataset, range=Optional[Union[Union[dict, "Document"], List[Union[dict, "Document"]]]])

slots.Dataset_language = Slot(uri=DCTERMS.language, name="Dataset_language", curie=DCTERMS.curie('language'),
                   model_uri=NFDI4C.Dataset_language, domain=Dataset, range=Optional[Union[Union[dict, "LinguisticSystem"], List[Union[dict, "LinguisticSystem"]]]])

slots.Dataset_modification_date = Slot(uri=DCTERMS.modified, name="Dataset_modification_date", curie=DCTERMS.curie('modified'),
                   model_uri=NFDI4C.Dataset_modification_date, domain=Dataset, range=Optional[str])

slots.Dataset_other_identifier = Slot(uri=ADMS.identifier, name="Dataset_other_identifier", curie=ADMS.curie('identifier'),
                   model_uri=NFDI4C.Dataset_other_identifier, domain=Dataset, range=Optional[Union[Union[dict, "Identifier"], List[Union[dict, "Identifier"]]]])

slots.Dataset_provenance = Slot(uri=DCTERMS.provenance, name="Dataset_provenance", curie=DCTERMS.curie('provenance'),
                   model_uri=NFDI4C.Dataset_provenance, domain=Dataset, range=Optional[Union[Union[dict, "ProvenanceStatement"], List[Union[dict, "ProvenanceStatement"]]]])

slots.Dataset_publisher = Slot(uri=DCTERMS.publisher, name="Dataset_publisher", curie=DCTERMS.curie('publisher'),
                   model_uri=NFDI4C.Dataset_publisher, domain=Dataset, range=Optional[Union[dict, "Agent"]])

slots.Dataset_qualified_attribution = Slot(uri=PROV.qualifiedAttribution, name="Dataset_qualified_attribution", curie=PROV.curie('qualifiedAttribution'),
                   model_uri=NFDI4C.Dataset_qualified_attribution, domain=Dataset, range=Optional[Union[Union[dict, "Attribution"], List[Union[dict, "Attribution"]]]])

slots.Dataset_qualified_relation = Slot(uri=DCAT.qualifiedRelation, name="Dataset_qualified_relation", curie=DCAT.curie('qualifiedRelation'),
                   model_uri=NFDI4C.Dataset_qualified_relation, domain=Dataset, range=Optional[Union[Union[dict, "Relationship"], List[Union[dict, "Relationship"]]]])

slots.Dataset_related_resource = Slot(uri=DCTERMS.relation, name="Dataset_related_resource", curie=DCTERMS.curie('relation'),
                   model_uri=NFDI4C.Dataset_related_resource, domain=Dataset, range=Optional[Union[Union[dict, "Resource"], List[Union[dict, "Resource"]]]])

slots.Dataset_release_date = Slot(uri=DCTERMS.issued, name="Dataset_release_date", curie=DCTERMS.curie('issued'),
                   model_uri=NFDI4C.Dataset_release_date, domain=Dataset, range=Optional[str])

slots.Dataset_sample = Slot(uri=ADMS.sample, name="Dataset_sample", curie=ADMS.curie('sample'),
                   model_uri=NFDI4C.Dataset_sample, domain=Dataset, range=Optional[Union[Union[dict, "Distribution"], List[Union[dict, "Distribution"]]]])

slots.Dataset_source = Slot(uri=DCTERMS.source, name="Dataset_source", curie=DCTERMS.curie('source'),
                   model_uri=NFDI4C.Dataset_source, domain=Dataset, range=Optional[Union[Union[dict, "Dataset"], List[Union[dict, "Dataset"]]]])

slots.Dataset_spatial_resolution = Slot(uri=DCAT.spatialResolutionInMeters, name="Dataset_spatial_resolution", curie=DCAT.curie('spatialResolutionInMeters'),
                   model_uri=NFDI4C.Dataset_spatial_resolution, domain=Dataset, range=Optional[Decimal])

slots.Dataset_temporal_coverage = Slot(uri=DCTERMS.temporal, name="Dataset_temporal_coverage", curie=DCTERMS.curie('temporal'),
                   model_uri=NFDI4C.Dataset_temporal_coverage, domain=Dataset, range=Optional[Union[Union[dict, "PeriodOfTime"], List[Union[dict, "PeriodOfTime"]]]])

slots.Dataset_temporal_resolution = Slot(uri=DCAT.temporalResolution, name="Dataset_temporal_resolution", curie=DCAT.curie('temporalResolution'),
                   model_uri=NFDI4C.Dataset_temporal_resolution, domain=Dataset, range=Optional[str])

slots.Dataset_theme = Slot(uri=DCAT.theme, name="Dataset_theme", curie=DCAT.curie('theme'),
                   model_uri=NFDI4C.Dataset_theme, domain=Dataset, range=Optional[Union[Union[dict, "Concept"], List[Union[dict, "Concept"]]]])

slots.Dataset_title = Slot(uri=DCTERMS.title, name="Dataset_title", curie=DCTERMS.curie('title'),
                   model_uri=NFDI4C.Dataset_title, domain=Dataset, range=Union[str, List[str]])

slots.Dataset_type = Slot(uri=DCTERMS.type, name="Dataset_type", curie=DCTERMS.curie('type'),
                   model_uri=NFDI4C.Dataset_type, domain=Dataset, range=Optional[Union[Union[dict, "Concept"], List[Union[dict, "Concept"]]]])

slots.Dataset_version = Slot(uri=DCAT.version, name="Dataset_version", curie=DCAT.curie('version'),
                   model_uri=NFDI4C.Dataset_version, domain=Dataset, range=Optional[str])

slots.Dataset_version_notes = Slot(uri=ADMS.versionNotes, name="Dataset_version_notes", curie=ADMS.curie('versionNotes'),
                   model_uri=NFDI4C.Dataset_version_notes, domain=Dataset, range=Optional[Union[str, List[str]]])

slots.Dataset_was_generated_by = Slot(uri=PROV.wasGeneratedBy, name="Dataset_was_generated_by", curie=PROV.curie('wasGeneratedBy'),
                   model_uri=NFDI4C.Dataset_was_generated_by, domain=Dataset, range=Optional[Union[Union[dict, Activity], List[Union[dict, Activity]]]])

slots.DatasetSeries_applicable_legislation = Slot(uri=DCATAP.applicableLegislation, name="DatasetSeries_applicable_legislation", curie=DCATAP.curie('applicableLegislation'),
                   model_uri=NFDI4C.DatasetSeries_applicable_legislation, domain=DatasetSeries, range=Optional[Union[Union[dict, "LegalResource"], List[Union[dict, "LegalResource"]]]])

slots.DatasetSeries_contact_point = Slot(uri=DCAT.contactPoint, name="DatasetSeries_contact_point", curie=DCAT.curie('contactPoint'),
                   model_uri=NFDI4C.DatasetSeries_contact_point, domain=DatasetSeries, range=Optional[Union[Union[dict, "Kind"], List[Union[dict, "Kind"]]]])

slots.DatasetSeries_description = Slot(uri=DCTERMS.description, name="DatasetSeries_description", curie=DCTERMS.curie('description'),
                   model_uri=NFDI4C.DatasetSeries_description, domain=DatasetSeries, range=Union[str, List[str]])

slots.DatasetSeries_frequency = Slot(uri=DCTERMS.accrualPeriodicity, name="DatasetSeries_frequency", curie=DCTERMS.curie('accrualPeriodicity'),
                   model_uri=NFDI4C.DatasetSeries_frequency, domain=DatasetSeries, range=Optional[Union[dict, "Frequency"]])

slots.DatasetSeries_geographical_coverage = Slot(uri=DCTERMS.spatial, name="DatasetSeries_geographical_coverage", curie=DCTERMS.curie('spatial'),
                   model_uri=NFDI4C.DatasetSeries_geographical_coverage, domain=DatasetSeries, range=Optional[Union[Union[dict, "Location"], List[Union[dict, "Location"]]]])

slots.DatasetSeries_modification_date = Slot(uri=DCTERMS.modified, name="DatasetSeries_modification_date", curie=DCTERMS.curie('modified'),
                   model_uri=NFDI4C.DatasetSeries_modification_date, domain=DatasetSeries, range=Optional[str])

slots.DatasetSeries_publisher = Slot(uri=DCTERMS.publisher, name="DatasetSeries_publisher", curie=DCTERMS.curie('publisher'),
                   model_uri=NFDI4C.DatasetSeries_publisher, domain=DatasetSeries, range=Optional[Union[dict, "Agent"]])

slots.DatasetSeries_release_date = Slot(uri=DCTERMS.issued, name="DatasetSeries_release_date", curie=DCTERMS.curie('issued'),
                   model_uri=NFDI4C.DatasetSeries_release_date, domain=DatasetSeries, range=Optional[str])

slots.DatasetSeries_temporal_coverage = Slot(uri=DCTERMS.temporal, name="DatasetSeries_temporal_coverage", curie=DCTERMS.curie('temporal'),
                   model_uri=NFDI4C.DatasetSeries_temporal_coverage, domain=DatasetSeries, range=Optional[Union[Union[dict, "PeriodOfTime"], List[Union[dict, "PeriodOfTime"]]]])

slots.DatasetSeries_title = Slot(uri=DCTERMS.title, name="DatasetSeries_title", curie=DCTERMS.curie('title'),
                   model_uri=NFDI4C.DatasetSeries_title, domain=DatasetSeries, range=Union[str, List[str]])

slots.Distribution_access_URL = Slot(uri=DCAT.accessURL, name="Distribution_access_URL", curie=DCAT.curie('accessURL'),
                   model_uri=NFDI4C.Distribution_access_URL, domain=Distribution, range=Union[Union[dict, "Resource"], List[Union[dict, "Resource"]]])

slots.Distribution_access_service = Slot(uri=DCAT.accessService, name="Distribution_access_service", curie=DCAT.curie('accessService'),
                   model_uri=NFDI4C.Distribution_access_service, domain=Distribution, range=Optional[Union[Union[dict, DataService], List[Union[dict, DataService]]]])

slots.Distribution_applicable_legislation = Slot(uri=DCATAP.applicableLegislation, name="Distribution_applicable_legislation", curie=DCATAP.curie('applicableLegislation'),
                   model_uri=NFDI4C.Distribution_applicable_legislation, domain=Distribution, range=Optional[Union[Union[dict, "LegalResource"], List[Union[dict, "LegalResource"]]]])

slots.Distribution_availability = Slot(uri=DCATAP.availability, name="Distribution_availability", curie=DCATAP.curie('availability'),
                   model_uri=NFDI4C.Distribution_availability, domain=Distribution, range=Optional[Union[dict, "Concept"]])

slots.Distribution_byte_size = Slot(uri=DCAT.byteSize, name="Distribution_byte_size", curie=DCAT.curie('byteSize'),
                   model_uri=NFDI4C.Distribution_byte_size, domain=Distribution, range=Optional[int])

slots.Distribution_checksum = Slot(uri=SPDX.checksum, name="Distribution_checksum", curie=SPDX.curie('checksum'),
                   model_uri=NFDI4C.Distribution_checksum, domain=Distribution, range=Optional[Union[dict, "Checksum"]])

slots.Distribution_compression_format = Slot(uri=DCAT.compressFormat, name="Distribution_compression_format", curie=DCAT.curie('compressFormat'),
                   model_uri=NFDI4C.Distribution_compression_format, domain=Distribution, range=Optional[Union[dict, "MediaType"]])

slots.Distribution_description = Slot(uri=DCTERMS.description, name="Distribution_description", curie=DCTERMS.curie('description'),
                   model_uri=NFDI4C.Distribution_description, domain=Distribution, range=Optional[Union[str, List[str]]])

slots.Distribution_documentation = Slot(uri=FOAF.page, name="Distribution_documentation", curie=FOAF.curie('page'),
                   model_uri=NFDI4C.Distribution_documentation, domain=Distribution, range=Optional[Union[Union[dict, "Document"], List[Union[dict, "Document"]]]])

slots.Distribution_download_URL = Slot(uri=DCAT.downloadURL, name="Distribution_download_URL", curie=DCAT.curie('downloadURL'),
                   model_uri=NFDI4C.Distribution_download_URL, domain=Distribution, range=Optional[Union[Union[dict, "Resource"], List[Union[dict, "Resource"]]]])

slots.Distribution_format = Slot(uri=DCTERMS.format, name="Distribution_format", curie=DCTERMS.curie('format'),
                   model_uri=NFDI4C.Distribution_format, domain=Distribution, range=Optional[Union[dict, "MediaTypeOrExtent"]])

slots.Distribution_has_policy = Slot(uri=ODRL.hasPolicy, name="Distribution_has_policy", curie=ODRL.curie('hasPolicy'),
                   model_uri=NFDI4C.Distribution_has_policy, domain=Distribution, range=Optional[Union[dict, "Policy"]])

slots.Distribution_language = Slot(uri=DCTERMS.language, name="Distribution_language", curie=DCTERMS.curie('language'),
                   model_uri=NFDI4C.Distribution_language, domain=Distribution, range=Optional[Union[Union[dict, "LinguisticSystem"], List[Union[dict, "LinguisticSystem"]]]])

slots.Distribution_licence = Slot(uri=DCTERMS.license, name="Distribution_licence", curie=DCTERMS.curie('license'),
                   model_uri=NFDI4C.Distribution_licence, domain=Distribution, range=Optional[Union[dict, "LicenseDocument"]])

slots.Distribution_linked_schemas = Slot(uri=DCTERMS.conformsTo, name="Distribution_linked_schemas", curie=DCTERMS.curie('conformsTo'),
                   model_uri=NFDI4C.Distribution_linked_schemas, domain=Distribution, range=Optional[Union[Union[dict, "Standard"], List[Union[dict, "Standard"]]]])

slots.Distribution_media_type = Slot(uri=DCAT.mediaType, name="Distribution_media_type", curie=DCAT.curie('mediaType'),
                   model_uri=NFDI4C.Distribution_media_type, domain=Distribution, range=Optional[Union[dict, "MediaType"]])

slots.Distribution_modification_date = Slot(uri=DCTERMS.modified, name="Distribution_modification_date", curie=DCTERMS.curie('modified'),
                   model_uri=NFDI4C.Distribution_modification_date, domain=Distribution, range=Optional[str])

slots.Distribution_packaging_format = Slot(uri=DCAT.packageFormat, name="Distribution_packaging_format", curie=DCAT.curie('packageFormat'),
                   model_uri=NFDI4C.Distribution_packaging_format, domain=Distribution, range=Optional[Union[dict, "MediaType"]])

slots.Distribution_release_date = Slot(uri=DCTERMS.issued, name="Distribution_release_date", curie=DCTERMS.curie('issued'),
                   model_uri=NFDI4C.Distribution_release_date, domain=Distribution, range=Optional[str])

slots.Distribution_rights = Slot(uri=DCTERMS.rights, name="Distribution_rights", curie=DCTERMS.curie('rights'),
                   model_uri=NFDI4C.Distribution_rights, domain=Distribution, range=Optional[Union[dict, "RightsStatement"]])

slots.Distribution_spatial_resolution = Slot(uri=DCAT.spatialResolutionInMeters, name="Distribution_spatial_resolution", curie=DCAT.curie('spatialResolutionInMeters'),
                   model_uri=NFDI4C.Distribution_spatial_resolution, domain=Distribution, range=Optional[Decimal])

slots.Distribution_status = Slot(uri=ADMS.status, name="Distribution_status", curie=ADMS.curie('status'),
                   model_uri=NFDI4C.Distribution_status, domain=Distribution, range=Optional[Union[dict, "Concept"]])

slots.Distribution_temporal_resolution = Slot(uri=DCAT.temporalResolution, name="Distribution_temporal_resolution", curie=DCAT.curie('temporalResolution'),
                   model_uri=NFDI4C.Distribution_temporal_resolution, domain=Distribution, range=Optional[str])

slots.Distribution_title = Slot(uri=DCTERMS.title, name="Distribution_title", curie=DCTERMS.curie('title'),
                   model_uri=NFDI4C.Distribution_title, domain=Distribution, range=Optional[Union[str, List[str]]])

slots.Identifier_notation = Slot(uri=SKOS.notation, name="Identifier_notation", curie=SKOS.curie('notation'),
                   model_uri=NFDI4C.Identifier_notation, domain=Identifier, range=Union[str, URI])

slots.LicenseDocument_type = Slot(uri=DCTERMS.type, name="LicenseDocument_type", curie=DCTERMS.curie('type'),
                   model_uri=NFDI4C.LicenseDocument_type, domain=LicenseDocument, range=Optional[Union[Union[dict, Concept], List[Union[dict, Concept]]]])

slots.Location_bbox = Slot(uri=DCAT.bbox, name="Location_bbox", curie=DCAT.curie('bbox'),
                   model_uri=NFDI4C.Location_bbox, domain=Location, range=Optional[str])

slots.Location_centroid = Slot(uri=DCAT.centroid, name="Location_centroid", curie=DCAT.curie('centroid'),
                   model_uri=NFDI4C.Location_centroid, domain=Location, range=Optional[str])

slots.Location_geometry = Slot(uri=LOCN.geometry, name="Location_geometry", curie=LOCN.curie('geometry'),
                   model_uri=NFDI4C.Location_geometry, domain=Location, range=Optional[Union[dict, Geometry]])

slots.PeriodOfTime_beginning = Slot(uri=TIME.hasBeginning, name="PeriodOfTime_beginning", curie=TIME.curie('hasBeginning'),
                   model_uri=NFDI4C.PeriodOfTime_beginning, domain=PeriodOfTime, range=Optional[Union[dict, "TimeInstant"]])

slots.PeriodOfTime_end = Slot(uri=TIME.hasEnd, name="PeriodOfTime_end", curie=TIME.curie('hasEnd'),
                   model_uri=NFDI4C.PeriodOfTime_end, domain=PeriodOfTime, range=Optional[Union[dict, "TimeInstant"]])

slots.PeriodOfTime_end_date = Slot(uri=DCAT.endDate, name="PeriodOfTime_end_date", curie=DCAT.curie('endDate'),
                   model_uri=NFDI4C.PeriodOfTime_end_date, domain=PeriodOfTime, range=Optional[str])

slots.PeriodOfTime_start_date = Slot(uri=DCAT.startDate, name="PeriodOfTime_start_date", curie=DCAT.curie('startDate'),
                   model_uri=NFDI4C.PeriodOfTime_start_date, domain=PeriodOfTime, range=Optional[str])

slots.Relationship_had_role = Slot(uri=DCAT.hadRole, name="Relationship_had_role", curie=DCAT.curie('hadRole'),
                   model_uri=NFDI4C.Relationship_had_role, domain=Relationship, range=Union[Union[dict, "Role"], List[Union[dict, "Role"]]])

slots.Relationship_relation = Slot(uri=DCTERMS.relation, name="Relationship_relation", curie=DCTERMS.curie('relation'),
                   model_uri=NFDI4C.Relationship_relation, domain=Relationship, range=Union[Union[dict, "Resource"], List[Union[dict, "Resource"]]])