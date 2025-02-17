## Writing custom profiles

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

The serializer uses customizable [profiles](profiles.md) to generate an RDF graph (an [RDFLib Graph class](https://rdflib.readthedocs.org/en/latest/apidocs/rdflib.html#rdflib.graph.Graph)).
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

