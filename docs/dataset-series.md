
Ckanext-dcat integrates seamlessly with [ckanext-dataset-series](https://github.com/ckan/ckanext-dataset-series), a light-way extensions that implements Dataset Series in a fast and efficient way. Ckanext-dataset-series takes care of all the underlying management of the series, and ckanext-dcat exposes them using [`dcat:DatasetSeries`](https://www.w3.org/TR/vocab-dcat-3/#Class:Dataset_Series) classes.

!!! Note
    ckanext-dataset-series requires at least CKAN 2.10


## Requirements

You will need to install ckanext-dataset-series:

    pip install ckanext-dataset-series

In addition to that, there are two changes needed at the schema level. Both will require that you load the ckanext-dataset-series presets in your ini file:

    scheming.presets =
        ckanext.scheming:presets.json
        ckanext.dcat.schemas:presets.yaml
        ckanext.dataset_series.schemas:presets.yaml

1. You will need a separate schema for Dataset Series. Internally these are just a type of CKAN dataset and can have any properties. Both [DCAT-AP](https://semiceu.github.io/DCAT-AP/releases/3.0.0/#DatasetSeries) and [DCAT-US](https://doi-do.github.io/dcat-us/#properties-for-dataset-series) have recommended properties for Dataset Series, and you can find an example in [`examples/ckan/ckan_dcat_ap_dataset_series.json`](https://github.com/ckan/ckanext-dcat/blob/master/examples/ckan/ckan_dcat_ap_dataset_series.json). But if you plan on using **ordered** Dataset Series, the schema must contain the following series management fields:



    ```yaml
	scheming_version: 2
	dataset_type: dataset_series

	dataset_fields:

	# [...]

    - field_name: series_order_field
      preset: dataset_series_order
      help_text: If the series is ordered, the field in the member datasets that will be used for sorting.

    - field_name: series_order_type
      preset: dataset_series_order_type
      help_text: The type of sorting that needs to be performed on series members.
    ```
	!!! Note
		Currently the dataset type value needs to be `dataset_type`. Other values might be allowed in the future.

2. The Dataset schema (or schemas) must contain the field used to link datasets to series:


    ```yaml
    # Series fields

    - field_name: in_series
      preset: dataset_series_in_series

    ```

Once the schemas are set up like this, new Dataset Series can be created at `/dataset_series/new`, and datasets can be assigned to them. For ordered dataset series, the extension will compute the navigation properties (`dcat:first` and `dcat:last` for Dataset Series, and `dcat:prev` and `dcat:next` for Datasets) at show time, based on the ordering of field provided with the `series_order_field` property.


## Serialization

Datasets of type `dataset_series` are serialized as `dcat:DatasetSeries`, and member Datasets include the `dcat:inSeries` property. If the series is ordered, navigation is included for both entities (`dcat:first` / `dcat:last` and `dcat:previous` / `dcat:next` respectively):

Example Dataset Series (e.g. `http://localhost:5000/dataset_series/test-dataset-series.ttl`):

```turtle
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<http://localhost:5017/dataset/20f41df2-0b50-4b6b-9a75-44eb39411dca> a dcat:DatasetSeries ;
    dct:description "Testing" ;
    dct:identifier "20f41df2-0b50-4b6b-9a75-44eb39411dca" ;
    dct:issued "2025-01-22T13:43:38.208410"^^xsd:dateTime ;
    dct:modified "2025-01-28T13:53:03.900418"^^xsd:dateTime ;
    dct:publisher <http://localhost:5017/organization/a27490ed-4abf-46bd-a80a-d6e19d7fff18> ;
    dct:title "Test Dataset series" ;
    dcat:distribution <http://localhost:5017/dataset/20f41df2-0b50-4b6b-9a75-44eb39411dca/resource/0a526400-7a45-4c2c-a1db-7058acb270b0> ;
    dcat:first <http://localhost:5017/dataset/826bd499-40e5-4d92-bfa1-f777775f0d76> ;
    dcat:last <http://localhost:5017/dataset/ce8fb09a-f285-4ba8-952e-46dbde08c509> .

<http://localhost:5017/dataset/20f41df2-0b50-4b6b-9a75-44eb39411dca/resource/0a526400-7a45-4c2c-a1db-7058acb270b0> a dcat:Distribution ;
    dct:issued "2025-01-22T13:43:49.560508"^^xsd:dateTime ;
    dct:modified "2025-01-22T13:43:49.555378"^^xsd:dateTime ;
    dct:title "need to drop this" .

<http://localhost:5017/organization/a27490ed-4abf-46bd-a80a-d6e19d7fff18> a foaf:Agent ;
    foaf:name "Test org 1" .
```

Example member Dataset (e.g. `http://localhost:5000/dataset/test-series-member-2.ttl`)

```turtle
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<http://localhost:5017/dataset/de9cb401-5fc7-47cd-83ac-f7fd154b2cee> a dcat:Dataset ;
    dct:description "sdas" ;
    dct:identifier "de9cb401-5fc7-47cd-83ac-f7fd154b2cee" ;
    dct:issued "2025-01-22T13:57:13.319491"^^xsd:dateTime ;
    dct:modified "2025-01-24T10:42:00.788016"^^xsd:dateTime ;
    dct:publisher <http://localhost:5017/organization/a27490ed-4abf-46bd-a80a-d6e19d7fff18> ;
    dct:title "Test series member 2" ;
    dcat:distribution <http://localhost:5017/dataset/de9cb401-5fc7-47cd-83ac-f7fd154b2cee/resource/aab3cabd-69b9-40e9-b922-1b0548de6cfc> ;
    dcat:inSeries <http://localhost:5017/dataset/20f41df2-0b50-4b6b-9a75-44eb39411dca> ;
    dcat:next <http://localhost:5017/dataset/ce8fb09a-f285-4ba8-952e-46dbde08c509> ;
    dcat:prev <http://localhost:5017/dataset/826bd499-40e5-4d92-bfa1-f777775f0d76> .

<http://localhost:5017/dataset/de9cb401-5fc7-47cd-83ac-f7fd154b2cee/resource/aab3cabd-69b9-40e9-b922-1b0548de6cfc> a dcat:Distribution ;
    dct:issued "2025-01-22T13:57:18.992071"^^xsd:dateTime ;
    dct:modified "2025-01-22T13:57:18.990029"^^xsd:dateTime ;
    dcat:accessURL <https://data.gov.ie> .

<http://localhost:5017/organization/a27490ed-4abf-46bd-a80a-d6e19d7fff18> a foaf:Agent ;
    foaf:name "Test org 1" .
```

!!! Note
	When requesting the catalog endpoint (e.g. `/catalog.ttl`), Dataset Series are typed as `dcat:DatasetSeries` and member datasets contain the `dcat:inSeries` property, but the navigation properties are not provided for performance reasons.
