## Profiles

Both the parsers and the serializers use profile classes to allow customization of how the values defined in the RDF graph are mapped to CKAN and viceversa.

Profiles define :

* How the RDF graph values map to CKAN fields, i.e. how the RDF is parsed into CKAN datasets
* How CKAN fields map to an RDF graph, which can be then serialized
* How the CKAN catalog metadata maps to an RDF graph, which can be then serialized

They essentially define the mapping between DCAT and CKAN.

In most cases the default profile will provide a good mapping that will cover most properties described in the DCAT standard. If you want to extract extra fields defined in the RDF, are using a custom schema or
need custom logic, you can write a [custom profile](#writing-custom-profiles) that extends or replaces one of the default ones.

The profiles currently shipped with the extension are mostly based in the
[DCAT application profile for data portals in Europe](https://joinup.ec.europa.eu/asset/dcat_application_profile/description). As mentioned before though, they should be generic enough for most DCAT based representations.

Sites that want to support a particular version of the DCAT-AP can enable a specific profile using one of the profiles below:

* [DCAT-AP v3](https://semiceu.github.io/DCAT-AP/releases/3.0.0) (default): `euro_dcat_ap_3`
* [DCAT-AP v2.1.0](https://joinup.ec.europa.eu/collection/semantic-interoperability-community-semic/solution/dcat-application-profile-data-portals-europe/release/210): `euro_dcat_ap_2`
* [DCAT-AP v1.1.1](https://joinup.ec.europa.eu/asset/dcat_application_profile/asset_release/dcat-ap-v11): `euro_dcat_ap`

This plugin also contains a profile to serialize a CKAN dataset to a [schema.org Dataset](http://schema.org/Dataset) called `schemaorg`. This is especially useful to provide [JSON-LD structured data](google-dataset-search.md).

To define which profiles to use you can:


1. Set the [`ckanext.dcat.rdf.profiles`](configuration.md#ckanextdcatrdfprofiles) configuration option on your CKAN configuration file:

```ini
ckanext.dcat.rdf.profiles = euro_dcat_ap sweden_dcat_ap
```

2. When initializing a parser or serializer class, pass the profiles to be used as a parameter, eg:

```python

parser = RDFParser(profiles=['euro_dcat_ap', 'sweden_dcat_ap'])

serializer = RDFSerializer(profiles=['euro_dcat_ap', 'sweden_dcat_ap'])
```

Note that in both cases the order in which you define them is important, as it will be the one that the profiles will be run on.


### Writing custom profiles

Internally, profiles are classes that define a particular set of methods called during the parsing process.
For instance, the `parse_dataset()` method is called on each DCAT dataset found when parsing an RDF file, and should return a CKAN dataset.
Conversely, the `graph_from_dataset()` will be called when requesting an RDF representation for a dataset, and will need to generate the necessary RDF graph.

Custom profiles should always extend the `ckanext.dcat.profiles.RDFProfile` class. This class has several helper
functions to make getting metadata from the RDF graph easier. These include helpers for getting fields for FOAF and VCard entities like the ones
used to define publishers or contact points. Check the source code of `ckanex.dcat.profiles.base.py` to see what is available.

Profiles can extend other profiles to avoid repeating rules, or can be completely independent.

The following example shows a complete example of a profile built on top of the European DCAT-AP profile (`euro_dcat_ap`):

```python

from rdflib.namespace import Namespace
from ckanext.dcat.profiles import RDFProfile

DCT = Namespace("http://purl.org/dc/terms/")


class SwedishDCATAPProfile(RDFProfile):
    '''
    An RDF profile for the Swedish DCAT-AP recommendation for data portals

    It requires the European DCAT-AP profile (`euro_dcat_ap`)
    '''

    def parse_dataset(self, dataset_dict, dataset_ref):

        # Spatial label
        spatial = self._object(dataset_ref, DCT.spatial)
        if spatial:
            spatial_label = self.g.label(spatial)
            if spatial_label:
                dataset_dict['extras'].append({'key': 'spatial_text',
                                               'value': str(spatial_label)})

        return dataset_dict

    def graph_from_dataset(self, dataset_dict, dataset_ref):

        g = self.g

        spatial_uri = self._get_dataset_value(dataset_dict, 'spatial_uri')
        spatial_text = self._get_dataset_value(dataset_dict, 'spatial_text')

        if spatial_uri:
            spatial_ref = URIRef(spatial_uri)
        else:
            spatial_ref = BNode()

        if spatial_text:
            g.add((dataset_ref, DCT.spatial, spatial_ref))
            g.add((spatial_ref, RDF.type, DCT.Location))
            g.add((spatial_ref, RDFS.label, Literal(spatial_text)))
```

Note how the dataset dict is passed between profiles so it can be further tweaked.

Extensions define their available profiles using the `ckan.rdf.profiles` entrypoint in the `setup.py` file, as in this [example](https://github.com/ckan/ckanext-dcat/blob/cc5fcc7be0be62491301db719ce597aec7c684b0/setup.py#L37:L38) from this same extension:

    [ckan.rdf.profiles]
    euro_dcat_ap=ckanext.dcat.profiles:EuropeanDCATAPProfile
    euro_dcat_ap_2=ckanext.dcat.profiles:EuropeanDCATAP2Profile
    euro_dcat_ap_3=ckanext.dcat.profiles:EuropeanDCATAP3Profile
    euro_dcat_ap_scheming=ckanext.dcat.profiles:EuropeanDCATAPSchemingProfile
    schemaorg=ckanext.dcat.profiles:SchemaOrgProfile

## Multilingual support

Support for parsing and serializing multilingual properties is provided by integrating with
[ckanext-fluent](https://github.com/ckan/ckanext-fluent), which provides a way to store multilingual
data in CKAN entities like datasets and resources.

Multilingual fields need to use one of the fluent [presets](https://github.com/ckan/ckanext-fluent#fluent_text-fields) (like `fluent_text`, `fluent_markdown` or `fluent_tags`) in their schema, e.g.:

```yaml
- field_name: provenance
  preset: fluent_markdown
  label:
    en: Provenance
    ca: Procedència
    es: Procedencia
```

This will make CKAN store the values for the different languages separately. The parsers will
import properties from DCAT serializations in this format if the field is defined as fluent in
the schema:

```json
{
    "name": "test-dataset",
    "provenance": {
        "en": "Statement about provenance",
        "ca": "Una declaració sobre la procedència",
        "es": "Una declaración sobre la procedencia"
    }
}
```

!!! Note
    If one of the languages is missing in the DCAT serialization, an empty string will be
    returned for that language. Also if the DCAT serialization does not define the language
    used, the default CKAN language will be used ([`ckan.locale_default`](https://docs.ckan.org/en/latest/maintaining/configuration.html#ckan-locale-default)).


Conversely, when serializing the CKAN dataset, a new triple will be added for each of the
defined languages (if the translation is present):

```turtle
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix vcard: <http://www.w3.org/2006/vcard/ns#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<https://example.org/dataset/0112cf32-bce0-4071-9504-923375f9f2ad> a dcat:Dataset ;
    dct:title "Conjunt de dades de prova DCAT"@ca,
        "Test DCAT dataset"@en,
        "Conjunto de datos de prueba DCAT"@es ;
    dct:description "Una descripció qualsevol"@ca,
        "Some description"@en,
        "Una descripción cualquiera"@es ;
    dct:language "ca",
        "en",
        "es" ;
    dct:provenance [ a dct:ProvenanceStatement ;
        rdfs:label "Una declaració sobre la procedència"@ca,
            "Statement about provenance"@en,
            "Una declaración sobre la procedencia"@es ] ;
```

See [*examples/ckan/ckan_dataset_multilingual.json*](https://github.com/ckan/ckanext-dcat/blob/master/examples/ckan/ckan_dataset_multilingual.json) and [*examples/dcat/dataset_multilingual.ttl*](https://github.com/ckan/ckanext-dcat/blob/master/examples/dcat/dataset_multilingual.ttl)
for examples of a multilingual CKAN dataset and DCAT serialization.


Users [writing custom profiles](#writing-custom-profiles) can make use of the `_object_value_multilingual()`
and `_object_value_list_multilingual()` functions of the profile class to handle custom fields not defined
in the base profiles.


## Internals

### RDF DCAT Parser

The `ckanext.dcat.processors.RDFParser` class allows to read RDF serializations in different
formats and extract CKAN dataset dicts. It will look for DCAT datasets and distributions
and create CKAN datasets and resources, as dictionaries that can be passed to [`package_create`](http://docs.ckan.org/en/latest/api/index.html#ckan.logic.action.create.package_create) or [`package_update`](http://docs.ckan.org/en/latest/api/index.html#ckan.logic.action.update.package_update).

Here is a quick overview of how it works:

```python

from ckanext.dcat.processors import RDFParser, RDFParserException

parser = RDFParser()

# Parsing a local RDF/XML file

with open('datasets.rdf', 'r') as f:
    try:
        parser.parse(f.read())

        for dataset in parser.datasets():
            print('Got dataset with title {0}'.format(dataset['title'])

    except RDFParserException, e:
        print ('Error parsing the RDF file: {0}'.format(e))

# Parsing a remote JSON-LD file

import requests

parser = RDFParser()

content = requests.get('https://some.catalog.org/datasets.jsonld').content

try:
    parser.parse(content, _format='json-ld')

    for dataset in parser.datasets():
        print('Got dataset with title {0}'.format(dataset['title'])

except RDFParserException, e:
    print ('Error parsing the RDF file: {0}'.format(e))

```

The parser is implemented using [RDFLib](https://rdflib.readthedocs.org/), a Python library for working with RDF. Any
RDF serialization format supported by RDFLib can be parsed into CKAN datasets. The `examples` folder contains
serializations in different formats including RDF/XML, Turtle or JSON-LD.

### RDF DCAT Serializer

The `ckanext.dcat.processors.RDFSerializer` class generates RDF serializations in different
formats from CKAN dataset dicts, like the ones returned by [`package_show`](http://docs.ckan.org/en/latest/api/index.html#ckan.logic.action.get.package_show) or [`package_search`](http://docs.ckan.org/en/latest/api/index.html#ckan.logic.action.get.package_search).

Here is an example of how to use it:

```python

from ckanext.dcat.processors import RDFSerializer

# Serializing a single dataset

dataset = get_action('package_show')({}, {'id': 'my-dataset'})

serializer = RDFserializer()

dataset_ttl = serializer.serialize_dataset(dataset, _format='turtle')


# Serializing the whole catalog (or rather part of it)

datasets = get_action('package_search')({}, {'q': '*:*', 'rows': 50})

serializer = RDFserializer()

catalog_xml = serializer.serialize_catalog({'title': 'My catalog'},
                                           dataset_dicts=datasets,
                                           _format='xml')

# Creating and RDFLib graph from a single dataset

dataset = get_action('package_show')({}, {'id': 'my-dataset'})

serializer = RDFserializer()

dataset_reference = serializer.graph_from_dataset(dataset)

# serializer.g now contains the full dataset graph, an RDFLib Graph class

```

The serializer uses customizable [profiles](#profiles) to generate an RDF graph (an [RDFLib Graph class](https://rdflib.readthedocs.org/en/latest/apidocs/rdflib.html#rdflib.graph.Graph)).
By default these use the [mapping](mapping.md) described in the previous section.

In some cases, if the default CKAN field that maps to a DCAT property is not present, some other fallback
values will be used instead. For instance, if the `contact_email` field is not found, `maintainer_email`
and `author_email` will be used (if present) for the email property of the `adms:contactPoint` property.

Note that the serializer will look both for a first level field or an extra field with the same key, ie both
the following values will be used for `dct:accrualPeriodicity`:

    {
        "name": "my-dataset",
        "frequency": "monthly",
        ...
    }

    {
        "name": "my-dataset",
        "extras": [
            {"key": "frequency", "value": "monthly"},
        ]
        ...
    }

Once the dataset graph has been obtained, this is serialized into a text format using [RDFLib](https://rdflib.readthedocs.org/),
so any format it supports can be obtained (common formats are 'xml', 'turtle' or 'json-ld').





