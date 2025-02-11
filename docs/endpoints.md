# RDF DCAT endpoints

By default, when the `dcat` plugin is enabled, the following RDF endpoints are available on your CKAN instance. The schema used on the serializations can be customized using [profiles](profiles.md#profiles).

To disable the RDF endpoints, you can set the [`ckanext.dcat.enable_rdf_endpoints`](configuration.md#ckanextdcatenable_rdf_endpoints) option in your ini file.


## Dataset endpoints

RDF representations of a particular dataset can be accessed using the following endpoint:

    https://{ckan-instance-host}/dataset/{dataset-id}.{format}

The extension will determine the RDF serialization format returned. The currently supported values are:

| Extension | Format                                                      | Media Type          |
|-----------|-------------------------------------------------------------|---------------------|
| `xml`     | [RDF/XML](https://en.wikipedia.org/wiki/RDF/XML)            | application/rdf+xml |
| `ttl`     | [Turtle](https://en.wikipedia.org/wiki/Turtle_%28syntax%29) | text/turtle         |
| `n3`      | [Notation3](https://en.wikipedia.org/wiki/Notation3)        | text/n3             |
| `jsonld`  | [JSON-LD](http://json-ld.org/)                              | application/ld+json |

The fallback `rdf` format defaults to RDF/XML.

Here's an example of the different formats:

* [https://opendata.swiss/en/dataset/verbreitung-der-steinbockkolonien.rdf](https://opendata.swiss/en/dataset/verbreitung-der-steinbockkolonien.rdf)
* [https://opendata.swiss/en/dataset/verbreitung-der-steinbockkolonien.xml](https://opendata.swiss/en/dataset/verbreitung-der-steinbockkolonien.xml)
* [https://opendata.swiss/en/dataset/verbreitung-der-steinbockkolonien.ttl](https://opendata.swiss/en/dataset/verbreitung-der-steinbockkolonien.ttl)
* [https://opendata.swiss/en/dataset/verbreitung-der-steinbockkolonien.n3](https://opendata.swiss/en/dataset/verbreitung-der-steinbockkolonien.n3)
* [https://opendata.swiss/en/dataset/verbreitung-der-steinbockkolonien.jsonld](https://opendata.swiss/en/dataset/verbreitung-der-steinbockkolonien.jsonld)

RDF representations will be advertised using `<link rel="alternate">` tags on the `<head>` section of the dataset page source code, e.g.:

```html
<head>

    <link rel="alternate" type="application/rdf+xml" href="http://demo.ckan.org/dataset/34315559-2b08-44eb-a2e6-ebe9ce1a266b.rdf"/>
    <link rel="alternate" type="text/turtle" href="http://demo.ckan.org/dataset/34315559-2b08-44eb-a2e6-ebe9ce1a266b.ttl"/>
    <!-- ... -->

</head>
```

Check the [RDF DCAT Serializer](writing-profiles.md#rdf-dcat-serializer) section for more details about how these are generated and how to customize the output using [profiles](profiles.md#profiles).


You can specify the profile by using the `profiles=<profile1>,<profile2>` query parameter on the dataset endpoint (as a comma-separated list):

* [https://opendata.swiss/en/dataset/verbreitung-der-steinbockkolonien.xml?profiles=euro_dcat_ap](https://opendata.swiss/en/dataset/verbreitung-der-steinbockkolonien.xml?profiles=euro_dcat_ap)
* [https://opendata.swiss/en/dataset/verbreitung-der-steinbockkolonien.jsonld?profiles=schemaorg](https://opendata.swiss/en/dataset/verbreitung-der-steinbockkolonien.jsonld?profiles=schemaorg)



## Catalog endpoint

Additionally to the individual dataset representations, the extension also offers a catalog-wide endpoint for retrieving multiple datasets at the same time (the datasets are paginated, see below for details):

    https://{ckan-instance-host}/catalog.{format}?[page={page}]&[modified_since={date}]&[profiles={profile1},{profile2}]&[q={query}]&[fq={filter query}]

This endpoint base path can be customized if necessary using the [`ckanext.dcat.catalog_endpoint`](configuration.md#ckanextdcatcatalog_endpoint) configuration option, eg:

    ckanext.dcat.catalog_endpoint = /dcat/catalog/{_format}

The custom endpoint **must** start with a forward slash (`/`) and contain the `{_format}` placeholder.

As described previously, the extension will determine the RDF serialization format returned.

* http://demo.ckan.org/catalog.rdf
* http://demo.ckan.org/catalog.xml
* http://demo.ckan.org/catalog.ttl

RDF representations will be advertised using `<link rel="alternate">` tags on the `<head>` section of the catalog homepage and the dataset search page source code, eg:

```html
<head>

    <link rel="alternate" type="application/rdf+xml" href="http://demo.ckan.org/catalog.rdf"/>
    <link rel="alternate" type="application/rdf+xml" href="http://demo.ckan.org/catalog.xml"/>
    <link rel="alternate" type="text/turtle" href="http://demo.ckan.org/catalog.ttl"/>
    <!-- ... -->

</head>
```

The number of datasets returned is limited. The response will include paging info, serialized using the [Hydra](http://www.w3.org/ns/hydra/spec/latest/core/) vocabulary. The different properties are self-explanatory, and can be used by clients to iterate the catalog:

```turtle
@prefix hydra: <http://www.w3.org/ns/hydra/core#> .

<http://example.com/catalog.ttl?page=1> a hydra:PagedCollection ;
    hydra:first "http://example.com/catalog.ttl?page=1" ;
    hydra:last "http://example.com/catalog.ttl?page=3" ;
    hydra:next "http://example.com/catalog.ttl?page=2" ;
    hydra:totalItems 283 .
```

The default number of datasets returned (100) can be modified by CKAN site maintainers using [`ckanext.dcat.datasets_per_page`](configuration.md#ckanextdcatdatasets_per_page)

The catalog endpoint also supports a `modified_since` parameter to restrict datasets to those modified from a certain date. The parameter value should be a valid ISO-8601 date:

    http://demo.ckan.org/catalog.xml?modified_since=2015-07-24

It is possible to specify the profile(s) to use for the serialization using the `profiles` parameter:

    http://demo.ckan.org/catalog.xml?profiles=euro_dcat_ap,sweden_dcat_ap

To filter the output, the catalog endpoint supports the `q` and `fq` parameters to specify a [search query](https://solr.apache.org/guide/solr/latest/query-guide/dismax-query-parser.html#q-parameter) or [filter query](https://solr.apache.org/guide/solr/latest/query-guide/common-query-parameters.html#fq-filter-query-parameter):



    http://demo.ckan.org/catalog.xml?q=budget
    http://demo.ckan.org/catalog.xml?fq=tags:economy



## URIs

Whenever possible, URIs are generated for the relevant entities. To try to generate them, the extension will use the first found of the following for each entity:

* Catalog:
    - [`ckanext.dcat.base_uri`](configuration.md#ckanextdcatbase_uri) configuration option value. This is the recommended approach. Value should be a valid URI.
    - [`ckan.site_url`](https://docs.ckan.org/en/latest/maintaining/configuration.html#ckan-site-url) configuration option value.
    - 'http://' + `app_instance_uuid` configuration option value. This is not recommended, and a warning log message will be shown.

* Dataset:
    - The value of the `uri` field (note that this is not included in the default CKAN schema)
    - The value of an extra with key `uri`
    - Catalog URI (see above) + '/dataset/' + `id` field

* Resource:
    - The value of the `uri` field (note that this is not included in the default CKAN schema)
    - Catalog URI (see above) + '/dataset/' + `package_id` field + '/resource/ + `id` field

Note that if you are using the [RDF DCAT harvester](harvester.md) to import datasets from other catalogs and these define a proper URI for each dataset or resource, these will be stored as `uri` fields in your instance, and so used when generating serializations for them.


## Content negotiation

The extension supports returning different representations of the datasets based on the value of the `Accept` header ([Content negotiation](https://en.wikipedia.org/wiki/Content_negotiation)). This is turned off by default, to enable it, set [`ckanext.dcat.enable_content_negotiation`](configuration.md#ckanextdcatenable_content_negotiation).

!!! Note
    
    This feature overrides the CKAN core home page and dataset page view routes, 
    so you probably don't want to enable it if your own extension is also doing it.


When enabled, client applications can request a particular format via the `Accept` header on requests to the main dataset page, eg:

    curl https://{ckan-instance-host}/dataset/{dataset-id} -H Accept:text/turtle

    curl https://{ckan-instance-host}/dataset/{dataset-id} -H Accept:"application/rdf+xml; q=1.0, application/ld+json; q=0.6"

This is also supported on the [catalog endpoint](#catalog-endpoint), in this case when making a request to the CKAN root URL (home page). This won't support the pagination and filter parameters:

    curl https://{ckan-instance-host} -H Accept:text/turtle
