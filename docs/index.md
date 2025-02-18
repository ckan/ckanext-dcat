# ckanext-dcat


[![Tests](https://github.com/ckan/ckanext-dcat/actions/workflows/test.yml/badge.svg)](https://github.com/ckan/ckanext-dcat/actions)
[![Code Coverage](http://codecov.io/github/ckan/ckanext-dcat/coverage.svg?branch=master)](http://codecov.io/github/ckan/ckanext-dcat?branch=master)


Ckanext-dcat is a [CKAN](https://github.com/ckan/ckan) extension that helps data publishers expose and consume metadata as serialized RDF documents using [DCAT](https://www.w3.org/TR/vocab-dcat-3/), as well as others metadata formats like [Croissant ML](croissant.md) or [Schema.org](google-dataset-search.md).


=== "CKAN dataset"

    ``` json
    {
        "id": "425e361b-bad9-4a8f-8cc4-2e147c4e8c18",
        "name": "my-ckan-dataset",
        "title": "An example CKAN dataset",
        "description": "Some notes about the data",
        "temporal_coverage": [
            {
                "start": "2024-01-01",
                "end": "2024-12-31"
            }
        ],
        "resources": [
            {
                "id": "df0fc449-fddf-41af-910a-f972b458956c",
                "name": "Some data in CSV format",
                "url": "http://my-ckan-site.org/dataset/425e361b-bad9-4a8f-8cc4-2e147c4e8c18/resource/df0fc449-fddf-41af-910a-f972b458956c/download/data.csv",
                "format": "CSV"
            }
        ]
    }
    ```

=== "DCAT representation (Turtle)"

    ```turtle
    @prefix dcat: <http://www.w3.org/ns/dcat#> .
    @prefix dct: <http://purl.org/dc/terms/> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

    <http://my-ckan-site.org/dataset/425e361b-bad9-4a8f-8cc4-2e147c4e8c18> a dcat:Dataset ;
        dct:identifier "425e361b-bad9-4a8f-8cc4-2e147c4e8c18" ;
        dct:temporal [ a dct:PeriodOfTime ;
                dcat:endDate "2024-12-31"^^xsd:date ;
                dcat:startDate "2024-01-01"^^xsd:date ] ;
        dct:title "An example CKAN dataset" ;
        dcat:distribution <http://my-ckan-site.org/dataset/425e361b-bad9-4a8f-8cc4-2e147c4e8c18/resource/df0fc449-fddf-41af-910a-f972b458956c> .

    <http://my-ckan-site.org/dataset/425e361b-bad9-4a8f-8cc4-2e147c4e8c18/resource/df0fc449-fddf-41af-910a-f972b458956c> a dcat:Distribution ;
        dct:format "CSV" ;
        dct:title "Some data in CSV format" ;
        dcat:accessURL <http://my-ckan-site.org/dataset/425e361b-bad9-4a8f-8cc4-2e147c4e8c18/resource/df0fc449-fddf-41af-910a-f972b458956c/download/data.csv> .
    ```

=== "DCAT representation (JSON-LD)"

    ``` json
    {
      "@context": {
        "dcat": "http://www.w3.org/ns/dcat#",
        "dct": "http://purl.org/dc/terms/",
        "xsd": "http://www.w3.org/2001/XMLSchema#"
      },
      "@graph": [
        {
          "@id": "http://my-ckan-site.org/dataset/425e361b-bad9-4a8f-8cc4-2e147c4e8c18",
          "@type": "dcat:Dataset",
          "dcat:distribution": {
            "@id": "http://my-ckan-site.org/dataset/425e361b-bad9-4a8f-8cc4-2e147c4e8c18/resource/df0fc449-fddf-41af-910a-f972b458956c"
          },
          "dct:identifier": "425e361b-bad9-4a8f-8cc4-2e147c4e8c18",
          "dct:temporal": {
            "@id": "_:N1c32ba52ad1641d086101a4a4bcbe8a5"
          },
          "dct:title": "An example CKAN dataset"
        },
        {
          "@id": "_:N1c32ba52ad1641d086101a4a4bcbe8a5",
          "@type": "dct:PeriodOfTime",
          "dcat:endDate": {
            "@type": "xsd:date",
            "@value": "2024-12-31"
          },
          "dcat:startDate": {
            "@type": "xsd:date",
            "@value": "2024-01-01"
          }
        },
        {
          "@id": "http://my-ckan-site.org/dataset/425e361b-bad9-4a8f-8cc4-2e147c4e8c18/resource/df0fc449-fddf-41af-910a-f972b458956c",
          "@type": "dcat:Distribution",
          "dcat:accessURL": {
            "@id": "http://my-ckan-site.org/dataset/425e361b-bad9-4a8f-8cc4-2e147c4e8c18/resource/df0fc449-fddf-41af-910a-f972b458956c/download/data.csv"
          },
          "dct:format": "CSV",
          "dct:title": "Some data in CSV format"
        }
      ]
    }
    ```

In terms of CKAN features, this extension offers:

* [Pre-built CKAN schemas](getting-started.md#schemas) for common Application Profiles that can be adapted to each site requirements to provide out-of-the-box DCAT support in data portals, including tailored form fields, validation etc. (currently supporting **DCAT-AP** [v1.1](https://joinup.ec.europa.eu/asset/dcat_application_profile/asset_release/dcat-ap-v11), [v2.1](https://joinup.ec.europa.eu/collection/semantic-interoperability-community-semic/solution/dcat-application-profile-data-portals-europe/release/210) and [v3](https://semiceu.github.io/DCAT-AP/releases/3.0.0/) and **DCAT-US** [v3](https://doi-do.github.io/dcat-us/)).

* [DCAT Endpoints](endpoints.md) that expose the catalog datasets in different RDF serializations (`dcat` plugin).

* An [RDF Harvester](harvester.md) that allows importing RDF serializations from other catalogs to create CKAN datasets (`dcat_rdf_harvester` plugin).

* Other features like [Command Line Interface](cli.md), support for indexing in [Google Dataset Search](google-dataset-search.md) or endpoints for exposing dataets in the [Croissant ML](croissant.md) format.


These are implemented internally using:

* A base [mapping](mapping.md) between DCAT and CKAN datasets and viceversa (compatible with **DCAT-AP** [v1.1](https://joinup.ec.europa.eu/asset/dcat_application_profile/asset_release/dcat-ap-v11), [v2.1](https://joinup.ec.europa.eu/collection/semantic-interoperability-community-semic/solution/dcat-application-profile-data-portals-europe/release/210) and [v3](https://semiceu.github.io/DCAT-AP/releases/3.0.0/) and **DCAT-US** [v3](https://doi-do.github.io/dcat-us/)).

* An [RDF Parser](writing-profiles.md#rdf-dcat-parser) that allows to read RDF serializations in different formats and extract CKAN dataset dicts, using customizable [profiles](profiles.md#profiles).

* An [RDF Serializer](writing-profiles.md#rdf-dcat-serializer) that allows to transform CKAN datasets metadata to different semantic formats, also allowing customizable [profiles](profiles.md#profiles).
