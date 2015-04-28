# ckanext-dcat

[![Build Status](https://travis-ci.org/ckan/ckanext-dcat.png)](https://travis-ci.org/ckan/ckanext-dcat)

[![Coverage Status](https://img.shields.io/coveralls/ckan/ckanext-dcat.svg)](https://coveralls.io/r/ckan/ckanext-dcat?branch=master)


This extension provides plugins that allow CKAN to expose and consume metadata from other catalogs using RDF documents serialized using DCAT. The Data Catalog Vocabulary (DCAT) is "an RDF vocabulary designed to facilitate interoperability between data catalogs published on the Web". More information can be found on the following W3C page:

[http://www.w3.org/TR/vocab-dcat](http://www.w3.org/TR/vocab-dcat)

*NOTE*: Both this extension and the serializations and protocol are a work in progress. All comments are welcome, just create an issue on the GitHub repository or send an email to the CKAN dev list:

[http://lists.okfn.org/mailman/listinfo/ckan-dev](http://lists.okfn.org/mailman/listinfo/ckan-dev)

## Overview

With the emergence of Open Data initiatives around the world, the need to share metadata across different catalogs has became more evident. Sites like [http://publicdata.eu](http://publicdata.eu) aggregate datasets from different portals, and there has been a growing demand to provide a clear and standard interface to allow incorporating metadata into them automatically.

There is growing consensus around [DCAT](http://www.w3.org/TR/vocab-dcat) being the right way forward, but actual implementations are needed. This extension aims to provide tools and guidance to allow publishers to publish and share DCAT based metadata easily. 

In terms of CKAN, this extension offers:

* A base [mapping](#rdf-dcat-to-ckan-dataset-mapping) between DCAT and CKAN datasets.

* An [RDF Parser](#rdf-dcat-parser) that allows to read RDF serializations in different formats and extract CKAN dataset dicts, using customizable plugins.

* An [RDF Harvester](#rdf-dcat-harvester) that allows importing RDF serializations from other catalogs to create CKAN datasets.

* An [JSON DCAT Harvester](#json-dcat-harvester) that allows importing JSON objects that are based on DCAT terms but are not defined as JSON-LD, using the serialization described in the [spec.datacatalogs.org](http://spec.datacatalogs.org/#datasets_serialization_format) site.

* *TODO*: Endpoints for (paginated) dumps of all the catalog's datasets metadata in RDF/XML and JSON format. (`dcat_json_interface` plugin)

* *TODO*: Individual endpoints for describing a dataset metadata in RDF/XML and JSON format. (Note: CKAN core already offers a RDF/XML representation, need to decide how they fit together).


## Installation

1.  Install ckanext-harvest ([https://github.com/ckan/ckanext-harvest#installation](https://github.com/ckan/ckanext-harvest#installation))

2.  Install the extension on your virtualenv:

        (pyenv) $ pip install -e git+https://github.com/ckan/ckanext-dcat.git#egg=ckanext-dcat

3.  Install the extension requirements:

        (pyenv) $ pip install -r ckanext-dcat/requirements.txt

4.  Enable the required plugins in your ini file:

        ckan.plugins = dcat_rdf_harvester dcat_json_harvester dcat_json_interface


## RDF DCAT to CKAN dataset mapping

The following table provides a generic mapping between the fields of the `dcat:Dataset` and `dcat:Distribution` classes and
their equivalents on the CKAN model. In most cases this mapping is deliberately a loose one. For instance, it does not try to link
the DCAT publisher property with a CKAN dataset author, maintainer or organization, as the link between them is not straight-forward
and may depend on a particular instance needs.



| DCAT class        | DCAT property          | CKAN dataset field                        | Stored as | Comments
|-------------------|------------------------|-------------------------------------------|-----------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| dcat:Dataset      | -                      | extra:uri                                 | text      | See note about URIs                                                                                                                                           |
| dcat:Dataset      | dct:title              | title                                     | text      |                                                                                                                                                               |
| dcat:Dataset      | dct:description        | notes                                     | text      |                                                                                                                                                               |
| dcat:Dataset      | dcat:landingPage       | url                                       | text      |                                                                                                                                                               |
| dcat:Dataset      | dcat:keyword           | tags                                      | text      |                                                                                                                                                               |
| dcat:Dataset      | dcat:theme             | extra:theme                               | list      | See note about lists                                                                                                                                          |
| dcat:Dataset      | dct:identifier         | extra:identifier                          | text      |                                                                                                                                                               |
| dcat:Dataset      | adms:identifier        | extra:alternate_identifier                | text      |                                                                                                                                                               |
| dcat:Dataset      | dct:issued             | extra:issued                              | text      |                                                                                                                                                               |
| dcat:Dataset      | dct:modified           | extra:modified                            | text      |                                                                                                                                                               |
| dcat:Dataset      | adms:version           | extra:dcat_version                        | text      | Prefixed "dcat_" to avoid confusion with the default version field                                                                                            |
| dcat:Dataset      | adms:versionNotes      | extra:version_notes                       | text      |                                                                                                                                                               |
| dcat:Dataset      | dct:language           | extra:language                            | list      | See note about lists                                                                                                                                          |
| dcat:Dataset      | dct:accrualPeriodicity | extra:frequency                           | text      |                                                                                                                                                               |
| dcat:Dataset      | dct:conformsTo         | extra:conforms_to                         | list      | See note about lists                                                                                                                                          |
| dcat:Dataset      | dct:spatial            | extra:spatial_uri                         | text      | If the RDF provides them, profiles should store the textual and geometric representation of the location in extra:spatial_text and extra:spatial respectively |
| dcat:Dataset      | dct:temporal           | extra:temporal_start + extra:temporal_end | text      | None, one or both extras can be present                                                                                                                       |
| dcat:Dataset      | dct:publisher          | extra:publisher_uri                       | text      | See note about URIs                                                                                                                                           |
| foaf:Agent        | foaf:name              | extra:publisher_name                      | text      |                                                                                                                                                               |
| foaf:Agent        | foaf:mbox              | extra:publisher_email                     | text      |                                                                                                                                                               |
| foaf:Agent        | foaf:homepage          | extra:publisher_url                       | text      |                                                                                                                                                               |
| foaf:Agent        | dct:type               | extra:publisher_type                      | text      |                                                                                                                                                               |
| dcat:Dataset      | adms:contactPoint      | extra:contact_uri                         | text      | See note about URIs                                                                                                                                           |
| vcard:Kind        | vcard:fn               | extra:contact_name                        | text      |                                                                                                                                                               |
| vcard:Kind        | vcard:hasEmail         | extra:contact_email                       | text      |                                                                                                                                                               |
| dcat:Dataset      | dcat:distribution      | resources                                 | text      |                                                                                                                                                               |
| dcat:Distribution | -                      | resource:uri                              | text      | See note about URIs                                                                                                                                           |
| dcat:Distribution | dct:title              | resource:name                             | text      |                                                                                                                                                               |
| dcat:Distribution | dcat:accessURL         | resource:url                              | text      | If accessURL is not present, downloadURL will be used as resource url                                                                                         |
| dcat:Distribution | dcat:downloadURL       | resource:download_url                     | text      |                                                                                                                                                               |
| dcat:Distribution | dct:description        | resource:description                      | text      |                                                                                                                                                               |
| dcat:Distribution | dcat:mediaType         | resource:mimetype                         | text      |                                                                                                                                                               |
| dcat:Distribution | dct:format             | resource:format                           | text      | This is likely to require extra logic to accommodate how CKAN deals with formats (eg ckan/ckanext-dcat#18)                                                    |
| dcat:Distribution | dct:license            | resource:license                          | text      | Note that on the CKAN model, license is a field at the dataset level                                                                                          |
| dcat:Distribution | adms:status            | resource:status                           | text      |                                                                                                                                                               |
| dcat:Distribution | dcat:byteSize          | resource:size                             | number    |                                                                                                                                                               |
| dcat:Distribution | dct:issued             | resource:issued                           | text      |                                                                                                                                                               |
| dcat:Distribution | dct:modified           | resource:modified                         | text      |                                                                                                                                                               |
| dcat:Distribution | dct:rights             | resource:rights                           | text      |                                                                                                                                                               |

*Notes*

* Whenever possible, URIs are extracted and stored so there is a clear reference to the original RDF resource.
  For instance:

    ```xml
    <?xml version="1.0" encoding="utf-8" ?>
        <rdf:RDF
         xmlns:dct="http://purl.org/dc/terms/"
	     xmlns:dcat="http://www.w3.org/ns/dcat#"
         xmlns:foaf="http://xmlns.com/foaf/0.1/"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">

        <dcat:Dataset rdf:about="http://data.some.org/catalog/datasets/1">
          <dct:title>Dataset 1</dct:title>
          <dct:publisher>
            <foaf:Organization rdf:about="http://orgs.vocab.org/some-org">
              <foaf:name>Publishing Organization for dataset 1</foaf:name>
            </foaf:Organization>
          </dct:publisher>
        <!-- ... -->
        </dcat:Dataset>
        </rdf:RDF>
    ```

    ```json
    {
        "title": "Dataset 1",
        "extras": [
            {"key": "uri", "value": "http://data.some.org/catalog/datasets/1"},
            {"key": "publisher_uri", "value": "http://orgs.vocab.org/some-org"},
            {"key": "publisher_name", "value": "Publishing Organization for dataset 1"}
        ]
    }
    ```

    Another example:

    ```
    @prefix dcat:    <http://www.w3.org/ns/dcat#> .
    @prefix dct:     <http://purl.org/dc/terms/> .
    @prefix rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

    <http://data.some.org/catalog/datasets/1>
          a       dcat:Dataset ;
          dct:title "Dataset 1" ;
          dcat:distribution
                  <http://data.some.org/catalog/datasets/1/d/1> .


    <http://data.some.org/catalog/datasets/1/d/1>
          a       dcat:Distribution ;
          dct:title "Distribution for dataset 1" ;
          dcat:accessURL <http://data.some.org/catalog/datasets/1/downloads/1.csv> .
    ```

    ```json
    {
        "title": "Dataset 1",
        "extras": [
            {"key": "uri", "value": "http://data.some.org/catalog/datasets/1"}
        ],
        "resources": [{
            "name": "Distribution for dataset 1",
            "url": "http://data.some.org/catalog/datasets/1/downloads/1.csv",
            "uri": "http://data.some.org/catalog/datasets/1/d/1"
        }]
    }
    ```

* Lists are stored as a JSON string, eg:

    ```
    @prefix dcat:  <http://www.w3.org/ns/dcat#> .
    @prefix dct:   <http://purl.org/dc/terms/> .
    @prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

    <http://example.com/data/test-dataset-1>
        a                  dcat:Dataset ;
        dct:title       "Dataset 1" ;
        dct:language    "ca" , "en" , "es" ;
        dcat:theme      "http://eurovoc.europa.eu/100142" , "http://eurovoc.europa.eu/209065", "Earth Sciences" ;
    ```

    ```json
    {
        "title": "Dataset 1",
        "extras": [
            {"key": "uri", "value": "http://data.some.org/catalog/datasets/1"}
            {"key": "language", "value": "[\"ca\", \"en\", \"es\"]"}
            {"key": "theme", "value": "[\"Earth Sciences\", \"http://eurovoc.europa.eu/209065\", \"http://eurovoc.europa.eu/100142\"]"}
        ],
    }
    ```


## RDF DCAT Parser

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

The parser uses profiles to allow customization of how the values defined in the RDF graph are mapped to CKAN. In most cases
the default profile will be good enough if you just want to generate datasets with the basic metadata (title, description, keywords, ...)
and store the rest of the fields as dataset extras. If you want to extract extra fields defined in the RDF, are using a custom schema or
need custom logic, you can write a custom to profile that extends or replaces the default one.

The default profile uses the mapping defined in the previous section to create the CKAN dataset dictionary. It is mostly based in the
[DCAT application profile for data portals in Europe](https://joinup.ec.europa.eu/asset/dcat_application_profile/description),
but as mentioned before it should be generic enough for most DCAT based representations.

### Parser Profiles

Profiles define how the RDF graph values map into CKAN. Right now this means how the RDF is parsed into CKAN datasets, but that could be
extended in the future, for instance to extract catalog information, or generate RDF serializations from CKAN datasets.

To define which profiles to use you can:

1. Set the `ckanext.dcat.rdf.profiles` configuration option on your CKAN configuration file:

    ckanext.dcat.rdf.profiles = euro_dcat_ap sweden_dcat_ap

2. When initializing a parser class, pass the profiles to be used as a parameter, eg:

```python

   parser = RDFParser(profiles=['euro_dcat_ap', 'sweden_dcat_ap'])
```

Note that in both cases the order in which you define them is important, as it will be the one that the profiles will be run on.


### Writing custom profiles

Internally, profiles are classes that define a particular set of methods called during the parsing process.
For instance, the `parse_dataset` method is called on each DCAT dataset found when parsing an RDF file, and should return a CKAN dataset.

Custom profiles should always extend the `ckanext.dcat.profiles.RDFProfile` class. This class has several helper
functions to make getting metadata from the RDF graph easier. These include helpers for getting fields for FOAF and VCard entities like the ones
used to define publishers or contact points. Check the source code of `ckanex.dcat.profiles.py` to see what is available.

Profiles can extend other profiles to avoid repeating rules, or can be completely independent.

The following example shows a complete example of a profile built on top of the default one (`euro_dcat_ap`):

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
```

Note how the dataset dict is passed between profiles so it can be further tweaked.

Extensions define their available profiles using the `ckan.rdf.profiles` in the `setup.py` file, as in this [example](https://github.com/ckan/ckanext-dcat/blob/cc5fcc7be0be62491301db719ce597aec7c684b0/setup.py#L37:L38) from this same extension:

    [ckan.rdf.profiles]
    euro_dcat_ap=ckanext.dcat.profiles:EuropeanDCATAPProfile

### Command line interface

The parser can also be accessed from the command line via `python ckanext-dcat/ckanext/dcat/parsers.py`.
You can point to RDF files:

    python ckanext-dcat/ckanext/dcat/parsers.py catalog_pod_2.jsonld -P -f json-ld

or pipe them to the script:

    http http://localhost/dcat/catalog.rdf | python ckanext-dcat/ckanext/dcat/parsers.py -P > ckan_datasets.json

To see all available options, run the script with the `-h` argument:

    python ckanext-dcat/ckanext/dcat/parsers.py -h
    usage: parsers.py [-h] [-f FORMAT] [-P] [-p [PROFILE [PROFILE ...]]] [-m]
                      [file]

    Parse DCAT RDF graphs to CKAN dataset JSON objects

    positional arguments:
      file

    optional arguments:
      -h, --help            show this help message and exit
      -f FORMAT, --format FORMAT
                            Serialization format (as understood by rdflib) eg:
                            xml, n3 ... Defaults to 'xml'.
      -P, --pretty          Make the output more human readable
      -p [PROFILE [PROFILE ...]], --profile [PROFILE [PROFILE ...]]
                            RDF Profiles to use, defaults to euro_dcat_ap
      -m, --compat-mode     Enable compatibility mode


### Compatibility mode

In compatibility mode, some fields are modified to maintain compatibility with previous versions of the ckanext-dcat parsers
(eg adding the `dcat_` prefix or storing comma separated lists instead
of JSON blobs).

CKAN instances that were using the legacy XML and JSON harvesters (`dcat_json_harvester` and `dcat_xml_harvester`)
and want to move to the RDF based one may want to turn compatibility mode on to ensure that CKAN dataset fields are created as before.
Users are encouraged to migrate their applications to support the new DCAT to CKAN mapping.

To turn compatibility mode on add this to the CKAN configuration file:

    ckanext.dcat.compatibility_mode = True


## RDF DCAT harvester

The RDF parser described in the previous section has been integrated into a harvester, 
to allow automatic import of datasets from remote sources. To enable the RDF harvester, add the `dcat_rdf_harvester` plugin to your CKAN configuration file:

    ckan.plugins = ... dcat_rdf_harvester

The harvester will download the remote file, extract all datasets using the parser and create or update actual CKAN datasets based on that.
It will also handle deletions, ie if a dataset is not present any more in the DCAT dump anymore it will get deleted from CKAN.

*TODO*: configure formats and profiles.

### Extending the RDF harvester

The DCAT RDF harvester has extension points that allow to modify its behaviour from other extensions. These can be used by extensions implementing
the `IDCATRDFHarvester` interface. Right now it provides the `before_download` and `after_download` methods that are called just before and after
retrieving the remote file, and can be used for instance to validate the contents.

To know more about these methods, please check the source of [`ckanext-dcat/ckanext/dcat/interfaces.py`](https://github.com/ckan/ckanext-dcat/blob/master/ckanext/dcat/interfaces.py).

## JSON DCAT harvester

The DCAT JSON harvester supports importing JSON objects that are based on DCAT terms but are not defined as JSON-LD. The exact format for these JSON files
is the one described in the [spec.datacatalogs.org](http://spec.datacatalogs.org/#datasets_serialization_format) site. There are [example files](https://github.com/ckan/ckanext-dcat/blob/master/examples/dataset.json) in the `examples` folder.

To enable the JSON harvester, add the `dcat_json_harvester` plugin to your CKAN configuration file:

    ckan.plugins = ... dcat_json_harvester

*TODO*: align the fields created by this harvester with the base mapping (ie the ones created by the RDF harvester).
                    
## XML DCAT harvester (deprecated)

The DCAT XML harvester (`dcat_xml_harvester`) is now deprecated, in favour of the [RDF harvester](#rdf-dcat-harvester). The XML serialization described in the [spec.datacatalogs.org](http://spec.datacatalogs.org/#datasets_serialization_format) site is a valid RDF/XML one, so changing the harvester should have no effect. There might be slight differences in the way CKAN fields are created though, check [Compatibility mode](#compatibility-mode) for more details.


## Running the Tests

To run the tests, do:

    nosetests --nologcapture --ckan --with-pylons=test.ini ckanext

## Acknowledgements

The work on the RDF parser and harvester has been made possible by the Government of Sweden and Vinnova, as part of work on the upcoming version of [Öppnadata.se](http://oppnadata.se), the Swedish Open Data Portal.


## Copying and License

This material is copyright (c) Open Knowledge.

It is open and licensed under the GNU Affero General Public License (AGPL) v3.0 whose full text may be found at:

http://www.fsf.org/licensing/licenses/agpl-3.0.html
