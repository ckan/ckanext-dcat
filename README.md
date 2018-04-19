# ckanext-dcat

[![Build Status](https://travis-ci.org/ckan/ckanext-dcat.svg?branch=master)](https://travis-ci.org/ckan/ckanext-dcat)
[![Code Coverage](http://codecov.io/github/ckan/ckanext-dcat/coverage.svg?branch=master)](http://codecov.io/github/ckan/ckanext-dcat?branch=master)


This extension provides plugins that allow CKAN to expose and consume metadata from other catalogs using RDF documents serialized using DCAT. The Data Catalog Vocabulary (DCAT) is "an RDF vocabulary designed to facilitate interoperability between data catalogs published on the Web". More information can be found on the following W3C page:

[http://www.w3.org/TR/vocab-dcat](http://www.w3.org/TR/vocab-dcat)

## Contents

- [Overview](#overview)
- [Installation](#installation)
- [RDF DCAT endpoints](#rdf-dcat-endpoints)
    - [Dataset endpoints](#dataset-endpoints)
    - [Catalog endpoint](#catalog-endpoint)
    - [URIs](#uris)
    - [Content negotiation](#content-negotiation)
- [RDF DCAT harvester](#rdf-dcat-harvester)
    - [Transitive harvesting](#transitive-harvesting)
    - [Extending the RDF harvester](#extending-the-rdf-harvester)
- [JSON DCAT harvester](#json-dcat-harvester)
- [RDF DCAT to CKAN dataset mapping](#rdf-dcat-to-ckan-dataset-mapping)
- [RDF DCAT Parser](#rdf-dcat-parser)
- [RDF DCAT Serializer](#rdf-dcat-serializer)
- [Profiles](#profiles)
    - [Writing custom profiles](#writing-custom-profiles)
    - [Command line interface](#command-line-interface)
    - [Compatibility mode](#compatibility-mode)
- [XML DCAT harvester (deprecated)](#xml-dcat-harvester-deprecated)
- [Translation of fields](#translation-of-fields)
- [Structured Data](#structured-data)
- [Running the Tests](#running-the-tests)
- [Acknowledgements](#acknowledgements)
- [Copying and License](#copying-and-license)

## Overview

With the emergence of Open Data initiatives around the world, the need to share metadata across different catalogs has became more evident. Sites like [http://publicdata.eu](http://publicdata.eu) aggregate datasets from different portals, and there has been a growing demand to provide a clear and standard interface to allow incorporating metadata into them automatically.

There is growing consensus around [DCAT](http://www.w3.org/TR/vocab-dcat) being the right way forward, but actual implementations are needed. This extension aims to provide tools and guidance to allow publishers to publish and share DCAT based metadata easily.

In terms of CKAN features, this extension offers:

* [RDF DCAT Endpoints](#rdf-dcat-endpoints) that expose the catalog's datasets in different RDF serializations (`dcat` plugin).

* An [RDF Harvester](#rdf-dcat-harvester) that allows importing RDF serializations from other catalogs to create CKAN datasets (`dcat_rdf_harvester` plugin).

* An [JSON DCAT Harvester](#json-dcat-harvester) that allows importing JSON objects that are based on DCAT terms but are not defined as JSON-LD, using the serialization described in the [spec.datacatalogs.org](http://spec.datacatalogs.org/#datasets_serialization_format) site (`dcat_json_harvester` plugin)..


These are implemented internally using:

* A base [mapping](#rdf-dcat-to-ckan-dataset-mapping) between DCAT and CKAN datasets and viceversa (compatible with [DCAT-AP v1.1](https://joinup.ec.europa.eu/asset/dcat_application_profile/asset_release/dcat-ap-v11)).

* An [RDF Parser](#rdf-dcat-parser) that allows to read RDF serializations in different formats and extract CKAN dataset dicts, using customizable [profiles](#profiles).

* An [RDF Serializer](#rdf-dcat-serializer) that allows to transform CKAN datasets metadata to different semantic formats, also allowing customizable [profiles](#profiles).



## Installation

1.  Install ckanext-harvest ([https://github.com/ckan/ckanext-harvest#installation](https://github.com/ckan/ckanext-harvest#installation)) (Only if you want to use the RDF harvester)

2.  Install the extension on your virtualenv:

        (pyenv) $ pip install -e git+https://github.com/ckan/ckanext-dcat.git#egg=ckanext-dcat

3.  Install the extension requirements:

        (pyenv) $ pip install -r ckanext-dcat/requirements.txt

4.  Enable the required plugins in your ini file:

        ckan.plugins = dcat dcat_rdf_harvester dcat_json_harvester dcat_json_interface structured_data

## RDF DCAT endpoints

By default when the `dcat` plugin is enabled, the following RDF endpoints are available on your CKAN instance. The schema used on the serializations can be customized using [profiles](#profiles).

To disable the RDF endpoints, you can set the following config in your ini file:

    ckanext.dcat.enable_rdf_endpoints = False


### Dataset endpoints

RDF representations of a particular dataset can accessed using the following endpoint:

    https://{ckan-instance-host}/dataset/{dataset-id}.{format}

The extension will determine the RDF serialization format returned. The currently supported values are:

| Extension | Format                                                      | Media Type          |
|-----------|-------------------------------------------------------------|---------------------|
| `xml`     | [RDF/XML](https://en.wikipedia.org/wiki/RDF/XML)            | application/rdf+xml |
| `ttl`     | [Turtle](https://en.wikipedia.org/wiki/Turtle_%28syntax%29) | text/turtle         |
| `n3`      | [Notation3](https://en.wikipedia.org/wiki/Notation3)        | text/n3             |
| `jsonld`  | [JSON-LD](http://json-ld.org/)                              | application/ld+json |

The fallback `rdf` format defaults to RDF/XML.

Here's an example of the different formats available (links might not be live as they link to a demo site):

* http://demo.ckan.org/dataset/newcastle-city-council-payments-over-500.rdf
* http://demo.ckan.org/dataset/newcastle-city-council-payments-over-500.xml
* http://demo.ckan.org/dataset/newcastle-city-council-payments-over-500.ttl
* http://demo.ckan.org/dataset/newcastle-city-council-payments-over-500.n3

RDF representations will be advertised using `<link rel="alternate">` tags on the `<head>` sectionon the dataset page source code, eg:

    <head>

        <link rel="alternate" type="application/rdf+xml" href="http://demo.ckan.org/dataset/34315559-2b08-44eb-a2e6-ebe9ce1a266b.rdf"/>
        <link rel="alternate" type="text/ttl" href="http://demo.ckan.org/dataset/34315559-2b08-44eb-a2e6-ebe9ce1a266b.ttl"/>
        <!-- ... -->

    </head>


Check the [RDF DCAT Serializer](#rdf-dcat-serializer) section for more details about how these are generated and how to customize the output using [profiles](#profiles).


You can specify the profile by using the `profiles=<profile1>,<profile2>` query parameter on the dataset endpoint (as a comma-separated list):

* `http://demo.ckan.org/dataset/newcastle-city-council-payments-over-500.xml?profiles=euro_dcat_ap,sweden_dcat_ap`
* `http://demo.ckan.org/dataset/newcastle-city-council-payments-over-500.jsonld?profiles=schemaorg`

*Note*: When using this plugin, the above endpoints will replace the old deprecated ones that were part of CKAN core.


### Catalog endpoint

Additionally to the individual dataset representations, the extension also offers a catalog-wide endpoint for retrieving multiple datasets at the same time (the datasets are paginated, see below for details):

    https://{ckan-instance-host}/catalog.{format}?[page={page}]&[modified_since={date}]&[profiles={profile1},{profile2}]

This endpoint can be customized if necessary using the `ckanext.dcat.catalog_endpoint` configuration option, eg:

    ckanext.dcat.catalog_endpoint = /dcat/catalog/{_format}

The custom endpoint **must** start with a backslash (`/`) and contain the `{_format}` placeholder.

As described previously, the extension will determine the RDF serialization format returned.

* http://demo.ckan.org/catalog.rdf
* http://demo.ckan.org/catalog.xml
* http://demo.ckan.org/catalog.ttl

RDF representations will be advertised using `<link rel="alternate">` tags on the `<head>` sectionon the homepage and the dataset search page source code, eg:

    <head>


        <link rel="alternate" type="application/rdf+xml" href="http://demo.ckan.org/catalog.rdf"/>
        <link rel="alternate" type="application/rdf+xml" href="http://demo.ckan.org/catalog.xml"/>
        <link rel="alternate" type="text/ttl" href="http://demo.ckan.org/catalog.ttl"/>
        <!-- ... -->

    </head>

The number of datasets returned is limited. The response will include paging info, serialized using the [Hydra](http://www.w3.org/ns/hydra/spec/latest/core/) vocabulary. The different terms are self-explanatory, and can be used by clients to iterate the catalog:

    @prefix hydra: <http://www.w3.org/ns/hydra/core#> .

    <http://example.com/catalog.ttl?page=1> a hydra:PagedCollection ;
        hydra:firstPage "http://example.com/catalog.ttl?page=1" ;
        hydra:itemsPerPage 100 ;
        hydra:lastPage "http://example.com/catalog.ttl?page=3" ;
        hydra:nextPage "http://example.com/catalog.ttl?page=2" ;
        hydra:totalItems 283 .

The default number of datasets returned (100) can be modified by CKAN site maintainers using the following configuration option on your ini file:

    ckanext.dcat.datasets_per_page = 20

The catalog endpoint also supports a `modified_since` parameter to restrict datasets to those modified from a certain date. The parameter value should be a valid ISO-8601 date:

http://demo.ckan.org/catalog.xml?modified_since=2015-07-24

It's possible to specify the profile(s) to use for the serialization using the `profiles` parameter:

http://demo.ckan.org/catalog.xml?profiles=euro_dcat_ap,sweden_dcat_ap



### URIs

Whenever possible, URIs are generated for the relevant entities. To try to generate them, the extension will use the first found of the following for each entity:

* Catalog:
    - `ckanext.dcat.base_uri` configuration option value. This is the recommended approach. Value should be a valid URI
    - `ckan.site_url` configuration option value.
    - 'http://' + `app_instance_uuid` configuration option value. This is not recommended, and a warning log message will be shown.

* Dataset:
    - The value of the `uri` field (note that this is not included in the default CKAN schema)
    - The value of an extra with key `uri`
    - Catalog URI (see above) + '/dataset/' + `id` field

* Resource:
    - The value of the `uri` field (note that this is not included in the default CKAN schema)
    - Catalog URI (see above) + '/dataset/' + `package_id` field + '/resource/ + `id` field

Note that if you are using the [RDF DCAT harvester](#rdf-dcat-harvester) to import datasets from other catalogs and these define a proper URI for each dataset or resource, these will be stored as `uri` fields in your instance, and thus used when generating serializations for them.


### Content negotiation

The extension supports returning different representations of the datasets based on the value of the `Accept` header ([Content negotiation](https://en.wikipedia.org/wiki/Content_negotiation)).

When enabled, client applications can request a particular format via the `Accept` header on requests to the main dataset page, eg:

    curl https://{ckan-instance-host}/dataset/{dataset-id} -H Accept:text/turtle

    curl https://{ckan-instance-host}/dataset/{dataset-id} -H Accept:"application/rdf+xml; q=1.0, application/ld+json; q=0.6"

This is also supported on the [catalog endpoint](#catalog-endpoint), in this case when making a request to the CKAN root URL (home page). This won't support the pagination and filter parameters:

    curl https://{ckan-instance-host} -H Accept:text/turtle

Note that this feature overrides the CKAN core home page and dataset page controllers, so you probably don't want to enable it if your own extension is also doing it.

To enable content negotiation, set the following configuration option on your ini file:

    ckanext.dcat.enable_content_negotiation = True


## RDF DCAT harvester

The RDF parser described in the previous section has been integrated into a harvester,
to allow automatic import of datasets from remote sources. To enable the RDF harvester, add the `dcat_rdf_harvester` plugin to your CKAN configuration file:

    ckan.plugins = ... dcat_rdf_harvester

The harvester will download the remote file, extract all datasets using the parser and create or update actual CKAN datasets based on that.
It will also handle deletions, ie if a dataset is not present any more in the DCAT dump anymore it will get deleted from CKAN.

The harvester will look at the `content-type` HTTP header field to determine the used RDF format. Any format understood by the [RDFLib](https://rdflib.readthedocs.org/en/stable/plugin_parsers.html) library can be parsed. It is possible to override this functionality and provide a specific format using the harvester configuration. This is useful when the server does not return the correct `content-type` or when harvesting a file on the local file system without a proper extension. The harvester configuration is a JSON object that you fill into the harvester configuration form field.

    {"rdf_format":"text/turtle"}

*TODO*: configure profiles.


### Transitive harvesting

In transitive harvesting (i.e., when you harvest a catalog A, and a catalog X harvests your catalog), you may want to provide the original catalog info for each harvested dataset.

By setting the configuration option `ckanext.dcat.expose_subcatalogs = True` in your ini file, you'll enable the storing and publication of the source catalog for each harvested dataset.

The information contained in the harvested `dcat:Catalog` node will be stored as extras into the harvested datasets.
When serializing, your Catalog will expose the harvested Catalog using the `dct:hasPart` relation. This means that your catalog will have this structure:
- `dcat:Catalog` (represents your current catalog)
  - `dcat:dataset` (1..n, the dataset created withing your catalog)
  - `dct:hasPart` 
     - `dcat:Catalog` (info of one of the harvested catalogs)
        - `dcat:dataset` (dataset in the harvested catalog)
  - `dct:hasPart` 
     - `dcat:Catalog` (info of one of another harvester catalog)
     ...   


### Extending the RDF harvester

The DCAT RDF harvester has extension points that allow to modify its behaviour from other extensions. These can be used by extensions implementing
the `IDCATRDFHarvester` interface. Right now it provides the following methods:

* `before_download` and `after_download`: called just before and after retrieving the remote file, and can be used for instance to validate the contents.
* `update_session`: called before making the remote requests to update the `requests` session object, useful to add additional headers or for setting client certificates. Check the [`requests` documentation](http://docs.python-requests.org/en/master/user/advanced/#session-objects) for details.
* `before_create` / `after_create`: called before and after the `package_create` action has been performed
* `before_update` / `after_update`: called before and after the `package_update` action has been performed

To know more about these methods, please check the source of [`ckanext-dcat/ckanext/dcat/interfaces.py`](https://github.com/ckan/ckanext-dcat/blob/master/ckanext/dcat/interfaces.py).

## JSON DCAT harvester

The DCAT JSON harvester supports importing JSON objects that are based on DCAT terms but are not defined as JSON-LD. The exact format for these JSON files
is the one described in the [spec.datacatalogs.org](http://spec.datacatalogs.org/#datasets_serialization_format) site. There are [example files](https://github.com/ckan/ckanext-dcat/blob/master/examples/dataset.json) in the `examples` folder.

To enable the JSON harvester, add the `dcat_json_harvester` plugin to your CKAN configuration file:

    ckan.plugins = ... dcat_json_harvester

*TODO*: align the fields created by this harvester with the base mapping (ie the ones created by the RDF harvester).

## RDF DCAT to CKAN dataset mapping

The following table provides a generic mapping between the fields of the `dcat:Dataset` and `dcat:Distribution` classes and
their equivalents on the CKAN model. In most cases this mapping is deliberately a loose one. For instance, it does not try to link
the DCAT publisher property with a CKAN dataset author, maintainer or organization, as the link between them is not straight-forward
and may depend on a particular instance needs. When mapping from CKAN metadata to DCAT though, there are in some cases fallback fields
that are used if the default field is not present (see [RDF Serializer](#rdf-dcat-serializer) for more details on this.

This mapping is compatible with the [DCAT-AP v1.1](https://joinup.ec.europa.eu/asset/dcat_application_profile/asset_release/dcat-ap-v11).


| DCAT class        | DCAT property          | CKAN dataset field                        | CKAN fallback fields           | Stored as |                                                                                                                                                               |
|-------------------|------------------------|-------------------------------------------|--------------------------------|-----------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| dcat:Dataset      | -                      | extra:uri                                 |                                | text      | See note about URIs                                                                                                                                           |
| dcat:Dataset      | dct:title              | title                                     |                                | text      |                                                                                                                                                               |
| dcat:Dataset      | dct:description        | notes                                     |                                | text      |                                                                                                                                                               |
| dcat:Dataset      | dcat:keyword           | tags                                      |                                | text      |                                                                                                                                                               |
| dcat:Dataset      | dcat:theme             | extra:theme                               |                                | list      | See note about lists                                                                                                                                          |
| dcat:Dataset      | dct:identifier         | extra:identifier                          | extra:guid, id                 | text      |                                                                                                                                                               |
| dcat:Dataset      | adms:identifier        | extra:alternate_identifier                |                                | text      |                                                                                                                                                               |
| dcat:Dataset      | dct:issued             | extra:issued                              | metadata_created               | text      |                                                                                                                                                               |
| dcat:Dataset      | dct:modified           | extra:modified                            | metadata_modified              | text      |                                                                                                                                                               |
| dcat:Dataset      | owl:versionInfo        | version                                   | extra:dcat_version             | text      |                                                                                                                                                               |
| dcat:Dataset      | adms:versionNotes      | extra:version_notes                       |                                | text      |                                                                                                                                                               |
| dcat:Dataset      | dct:language           | extra:language                            |                                | list      | See note about lists                                                                                                                                          |
| dcat:Dataset      | dcat:landingPage       | url                                       |                                | text      |                                                                                                                                                               |
| dcat:Dataset      | dct:accrualPeriodicity | extra:frequency                           |                                | text      |                                                                                                                                                               |
| dcat:Dataset      | dct:conformsTo         | extra:conforms_to                         |                                | list      | See note about lists                                                                                                                                          |
| dcat:Dataset      | dct:accessRights       | extra:access_rights                       |                                | text      |                                                                                                                                                               |
| dcat:Dataset      | foaf:page              | extra:documentation                       |                                | list      | See note about lists                                                                                                                                          |
| dcat:Dataset      | dct:provenance         | extra:provenance                          |                                | text      |                                                                                                                                                               |
| dcat:Dataset      | dct:type               | extra:dcat_type                           |                                | text      | As of DCAT-AP v1.1 there's no controlled vocabulary for this field                                                                                            |
| dcat:Dataset      | dct:hasVersion         | extra:has_version                         |                                | list      | See note about lists. It is assumed that these are one or more URIs referring to another dcat:Dataset                                                         |
| dcat:Dataset      | dct:isVersionOf        | extra:is_version_of                       |                                | list      | See note about lists. It is assumed that these are one or more URIs referring to another dcat:Dataset                                                         |
| dcat:Dataset      | dct:source             | extra:source                              |                                | list      | See note about lists. It is assumed that these are one or more URIs referring to another dcat:Dataset                                                         |
| dcat:Dataset      | adms:sample            | extra:sample                              |                                | list      | See note about lists. It is assumed that these are one or more URIs referring to dcat:Distribution instances                                                  |
| dcat:Dataset      | dct:spatial            | extra:spatial_uri                         |                                | text      | If the RDF provides them, profiles should store the textual and geometric representation of the location in extra:spatial_text and extra:spatial respectively |
| dcat:Dataset      | dct:temporal           | extra:temporal_start + extra:temporal_end |                                | text      | None, one or both extras can be present                                                                                                                       |
| dcat:Dataset      | dct:publisher          | extra:publisher_uri                       |                                | text      | See note about URIs                                                                                                                                           |
| foaf:Agent        | foaf:name              | extra:publisher_name                      |                                | text      |                                                                                                                                                               |
| foaf:Agent        | foaf:mbox              | extra:publisher_email                     | organization:title             | text      |                                                                                                                                                               |
| foaf:Agent        | foaf:homepage          | extra:publisher_url                       |                                | text      |                                                                                                                                                               |
| foaf:Agent        | dct:type               | extra:publisher_type                      |                                | text      |                                                                                                                                                               |
| dcat:Dataset      | dcat:contactPoint      | extra:contact_uri                         |                                | text      | See note about URIs                                                                                                                                           |
| vcard:Kind        | vcard:fn               | extra:contact_name                        | maintainer, author             | text      |                                                                                                                                                               |
| vcard:Kind        | vcard:hasEmail         | extra:contact_email                       | maintainer_email, author_email | text      |                                                                                                                                                               |
| dcat:Dataset      | dcat:distribution      | resources                                 |                                | text      |                                                                                                                                                               |
| dcat:Distribution | -                      | resource:uri                              |                                | text      | See note about URIs                                                                                                                                           |
| dcat:Distribution | dct:title              | resource:name                             |                                | text      |                                                                                                                                                               |
| dcat:Distribution | dcat:accessURL         | resource:url                              |                                | text      | If accessURL is not present, downloadURL will be used as resource url                                                                                         |
| dcat:Distribution | dcat:downloadURL       | resource:download_url                     |                                | text      |                                                                                                                                                               |
| dcat:Distribution | dct:description        | resource:description                      |                                | text      |                                                                                                                                                               |
| dcat:Distribution | dcat:mediaType         | resource:mimetype                         |                                | text      |                                                                                                                                                               |
| dcat:Distribution | dct:format             | resource:format                           |                                | text      | This is likely to require extra logic to accommodate how CKAN deals with formats (eg ckan/ckanext-dcat#18)                                                    |
| dcat:Distribution | dct:license            | resource:license                          |                                | text      | See note about dataset license                                                                                                                                |
| dcat:Distribution | adms:status            | resource:status                           |                                | text      |                                                                                                                                                               |
| dcat:Distribution | dcat:byteSize          | resource:size                             |                                | number    |                                                                                                                                                               |
| dcat:Distribution | dct:issued             | resource:issued                           |                                | text      |                                                                                                                                                               |
| dcat:Distribution | dct:modified           | resource:modified                         |                                | text      |                                                                                                                                                               |
| dcat:Distribution | dct:rights             | resource:rights                           |                                | text      |                                                                                                                                                               |
| dcat:Distribution | foaf:page              | resource:documentation                    |                                | list      | See note about lists                                                                                                                                          |
| dcat:Distribution | dct:language           | resource:language                         |                                | list      | See note about lists                                                                                                                                          |
| dcat:Distribution | dct:conformsTo         | resource:conforms_to                      |                                | list      | See note about lists                                                                                                                                          |
| spdx:Checksum     | spdx:checksumValue     | resource:hash                             |                                | text      |                                                                                                                                                               |
| spdx:Checksum     | spdx:algorithm         | resource:hash_algorithm                   |                                | text      |                                                                                                                                                               |

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

* The following formats for `dct:spatial` are supported by the default [parser](#rdf-dcat-parser). Note that the default [serializer](#rdf-dcat-serializer) will return the single `dct:spatial` instance form by default.

    - One `dct:spatial` instance, URI only

        ```xml
        <dct:spatial rdf:resource="http://geonames/Newark"/>
        ```

    - One `dct:spatial` instance with text (this should not be used anyway)

        ```xml
        <dct:spatial>Newark</dct:spatial>
        ```

    - One `dct:spatial` instance with label and/or geometry

        ```xml
        <dct:spatial rdf:resource="http://geonames/Newark">
            <dct:Location>
                <locn:geometry rdf:datatype="https://www.iana.org/assignments/media-types/application/vnd.geo+json">
                    {"type": "Polygon", "coordinates": [[[175.0, 17.5], [-65.5, 17.5], [-65.5, 72.0], [175.0, 72.0], [175.0, 17.5]]]}
                </locn:geometry>
                <locn:geometry rdf:datatype="http://www.opengis.net/ont/geosparql#wktLiteral">
                    POLYGON ((175.0000 17.5000, -65.5000 17.5000, -65.5000 72.0000, 175.0000 72.0000, 175.0000 17.5000))
                </locn:geometry>
                <skos:prefLabel>Newark</skos:prefLabel>
            </dct:Location>
        </dct:spatial>
        ```

    - Multiple `dct:spatial` instances (as in GeoDCAT-AP)

        ```xml
        <dct:spatial rdf:resource="http://geonames/Newark"/>
        <dct:spatial>
            <dct:Location>
                <locn:geometry rdf:datatype="https://www.iana.org/assignments/media-types/application/vnd.geo+json">
                    {"type": "Polygon", "coordinates": [[[175.0, 17.5], [-65.5, 17.5], [-65.5, 72.0], [175.0, 72.0], [175.0, 17.5]]]}
                </locn:geometry>
                <locn:geometry rdf:datatype="http://www.opengis.net/ont/geosparql#wktLiteral">
                    POLYGON ((175.0000 17.5000, -65.5000 17.5000, -65.5000 72.0000, 175.0000 72.0000, 175.0000 17.5000))
                </locn:geometry>
            </dct:Location>
        </dct:spatial>
        <dct:spatial>
            <dct:Location rdf:nodeID="N8c2a57d92e2d48fca3883053f992f0cf">
                <skos:prefLabel>Newark</skos:prefLabel>
            </dct:Location>
        </dct:spatial>
        ```

*  On the CKAN model, license is at the dataset level whereas in DCAT model it
   is at distributions level. By default the RDF parser will try to find a
   distribution with a license that matches one of those registered in CKAN
   and attach this license to the dataset. The first matching distribution's
   license is used, meaning that any discrepancy accross distributions license
   will not be accounted for. This behavior can be customized by overridding the
   `_license` method on a custom profile.


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

## RDF DCAT Serializer

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
By default these use the [mapping](#rdf-dcat-to-ckan-dataset-mapping) described in the previous section.

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

## Profiles

Both the parser and the serializer use profiles to allow customization of how the values defined in the RDF graph are mapped to CKAN and viceversa.

Profiles define :

* How the RDF graph values map into CKAN fields, ie how the RDF is parsed into CKAN datasets
* How CKAN fields map to an RDF graph, which can be then serialized
* How the CKAN catalog metadata maps to an RDF graph, which can be then serialized

They essentially define the mapping between DCAT and CKAN.

In most cases the default profile will provide a good mapping that will cover most properties described in the DCAT standard. If you want to extract extra fields defined in the RDF, are using a custom schema or
need custom logic, you can write a custom to profile that extends or replaces the default one.

The default profile is mostly based in the
[DCAT application profile for data portals in Europe](https://joinup.ec.europa.eu/asset/dcat_application_profile/description). It is actually fully-compatible with [DCAT-AP v1.1](https://joinup.ec.europa.eu/asset/dcat_application_profile/asset_release/dcat-ap-v11). As mentioned before though, it should be generic enough for most DCAT based representations.

This plugin also contains a profile to serialize a CKAN dataset to a [schema.org Dataset](http://schema.org/Dataset) called `schemaorg`. This is especially useful to provide [JSON-LD structured data](#structured-data).

To define which profiles to use you can:

1. Set the `ckanext.dcat.rdf.profiles` configuration option on your CKAN configuration file:

    ckanext.dcat.rdf.profiles = euro_dcat_ap sweden_dcat_ap

2. When initializing a parser or serializer class, pass the profiles to be used as a parameter, eg:

```python

   parser = RDFParser(profiles=['euro_dcat_ap', 'sweden_dcat_ap'])

   serializer = RDFSerializer(profiles=['euro_dcat_ap', 'sweden_dcat_ap'])
```

Note that in both cases the order in which you define them is important, as it will be the one that the profiles will be run on.


### Writing custom profiles

Internally, profiles are classes that define a particular set of methods called during the parsing process.
For instance, the `parse_dataset` method is called on each DCAT dataset found when parsing an RDF file, and should return a CKAN dataset.
Conversely, the `graph_from_dataset` will be called when requesting an RDF representation for a dataset, and will need to generate the necessary RDF graph.

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

Extensions define their available profiles using the `ckan.rdf.profiles` in the `setup.py` file, as in this [example](https://github.com/ckan/ckanext-dcat/blob/cc5fcc7be0be62491301db719ce597aec7c684b0/setup.py#L37:L38) from this same extension:

    [ckan.rdf.profiles]
    euro_dcat_ap=ckanext.dcat.profiles:EuropeanDCATAPProfile

### Command line interface

The parser and serializer can also be accessed from the command line via `python ckanext-dcat/ckanext/dcat/processors.py`.

You can point to RDF files:

    python ckanext-dcat/ckanext/dcat/processors.py consume catalog_pod_2.jsonld -P -f json-ld

    python ckanext/dcat/processors.py produce examples/ckan_dataset.json

or pipe them to the script:

    http http://localhost/dcat/catalog.rdf | python ckanext-dcat/ckanext/dcat/processors.py consume -P > ckan_datasets.json

    http http://demo.ckan.org/api/action/package_show id=afghanistan-election-data | jq .result | python ckanext/dcat/processors.py produce


To see all available options, run the script with the `-h` argument:

    python ckanext-dcat/ckanext/dcat/processors.py -h
    usage: processors.py [-h] [-f FORMAT] [-P] [-p [PROFILE [PROFILE ...]]] [-m]
                         mode [file]

    DCAT RDF - CKAN operations

    positional arguments:
      mode                  Operation mode. `consume` parses DCAT RDF graphs to
                            CKAN dataset JSON objects. `produce` serializes CKAN
                            dataset JSON objects into DCAT RDF.
      file                  Input file. If omitted will read from stdin

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



## XML DCAT harvester (deprecated)

The old DCAT XML harvester (`dcat_xml_harvester`) is now deprecated, in favour of the [RDF harvester](#rdf-dcat-harvester).
Loading it on the ini file will result in an exception on startup.

The XML serialization described in the [spec.datacatalogs.org](http://spec.datacatalogs.org/#datasets_serialization_format) site is a valid RDF/XML one, so changing the harvester should have no effect. There might be slight differences in the way CKAN fields are created though, check [Compatibility mode](#compatibility-mode) for more details.

## Translation of fields

The `dcat` plugin automatically translates the keys of the dcat fields used in the frontend.
This makes it very easy to display the fields in the current language.

To disable this behavior, you can set the following config value in your ini file (default: True):

    ckanext.dcat.translate_keys = False


## Structured data

To add [structured data](https://developers.google.com/search/docs/guides/intro-structured-data) to dataset pages, activate the `structured_data` and `dcat` plugins in your ini file:

        ckan.plugins = dcat structured_data

By default this uses the `schemaorg` profile (see [profiles](#profiles)) to serialize the dataset to JSON-LD, which is then added to the dataset detail page.
To change the schema, you have to override the Jinja template block called `structured_data` in [`templates/package/read_base.html`](https://github.com/ckan/ckanext-dcat/blob/master/ckanext/dcat/templates/package/read_base.html) and call the template helper function with different parameters:

    {% block structured_data %}
      <script type="application/ld+json">
      {{ h.structured_data(pkg.id, ['my_custom_schema'])|safe }}
      </script>
    {% endblock %}

Example output of structured data in JSON-LD:

    < ... >
        <script type="application/ld+json">
        {
            "@context": {
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "schema": "http://schema.org/",
                "xsd": "http://www.w3.org/2001/XMLSchema#"
            },
            "@graph": [
                {
                    "@id": "http://demo.ckan.org/organization/c64835bf-b3b7-496d-a7cf-ed645dbf4b08",
                    "@type": "schema:Organization",
                    "schema:contactPoint": {
                        "@id": "_:Nb9677036512840e1a00c9fec2818abe4"
                    },
                    "schema:name": "Public Transport Organization"
                },
                {
                    "@id": "http://demo.ckan.org/dataset/69a5bc23-3abd-4af7-8d3d-8f0d08698307/resource/5f1cafa2-3c92-4e89-85d1-60f014c23e0f",
                    "@type": "schema:DataDownload",
                    "schema:dateModified": "2018-01-18T00:00:00",
                    "schema:datePublished": "2018-01-02T00:00:00",
                    "schema:description": "API for all the public transport stations",
                    "schema:encodingFormat": "JSON",
                    "schema:inLanguage": [
                        "de",
                        "it",
                        "fr",
                        "en"
                    ],
                    "schema:license": "https://creativecommons.org/licenses/by/4.0/",
                    "schema:name": "Stations API",
                    "schema:url": "http://stations.example.com/api"
                },
                {
                    "@id": "http://demo.ckan.org/dataset/69a5bc23-3abd-4af7-8d3d-8f0d08698307",
                    "@type": "schema:Dataset",
                    "schema:dateModified": "2018-01-18T09:41:21.076522",
                    "schema:datePublished": "2017-01-01T00:00:00",
                    "schema:distribution": [
                        {
                            "@id": "http://demo.ckan.org/dataset/69a5bc23-3abd-4af7-8d3d-8f0d08698307/resource/5f1cafa2-3c92-4e89-85d1-60f014c23e0f"
                        },
                        {
                            "@id": "http://demo.ckan.org/dataset/69a5bc23-3abd-4af7-8d3d-8f0d08698307/resource/bf3a0b61-415b-47b8-9cd0-86a14f8dc165"
                        }
                    ],
                    "schema:identifier": "69a5bc23-3abd-4af7-8d3d-8f0d08698307",
                    "schema:inLanguage": [
                        "en",
                        "de",
                        "fr",
                        "it"
                    ],
                    "schema:name": "Station list",
                    "schema:publisher": {
                        "@id": "http://demo.ckan.org/organization/c64835bf-b3b7-496d-a7cf-ed645dbf4b08"
                    }
                },
                {
                    "@id": "_:Nb9677036512840e1a00c9fec2818abe4",
                    "@type": "schema:ContactPoint",
                    "schema:contactType": "customer service",
                    "schema:email": "contact@example.com",
                    "schema:name": "Public Transport Support",
                    "schema:url": "https://public-transport.example.com"
                }
            ]
        }
        </script>
      </body>
    </html>


## Running the Tests

To run the tests, do:

    nosetests --nologcapture --ckan --with-pylons=test.ini ckanext

## Acknowledgements

Work on ckanext-dcat has been made possible by:

* the Government of Sweden and Vinnova, as part of work on [Öppnadata.se](http://oppnadata.se), the Swedish Open Data Portal.
* [FIWARE](https://www.fiware.org), a project funded by the European Commission to integrate different technologies to offer connected cloud services from a single platform.

If you can fund new developments or contribute please get in touch.


## Copying and License

This material is copyright (c) Open Knowledge.

It is open and licensed under the GNU Affero General Public License (AGPL) v3.0 whose full text may be found at:

http://www.fsf.org/licensing/licenses/agpl-3.0.html
