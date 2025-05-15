
[Croissant](https://mlcommons.org/working-groups/data/croissant/) is a community standard for describing ML datasets. It combines information about the dataset metadata, its resources and data structure to make existing datasets easier to find and use across different tools. It builds on [schema.org](https://schema.org) and its Dataset vocabulary.


## Configuration

The `croissant` plugin allows a CKAN site dataset's metadata to be exposed following the [Croissant format specification](https://docs.mlcommons.org/croissant/docs/croissant-spec.html):

```ini
ckan.plugins = [...] croissant
```


!!! Note
    The `croissant` plugin can be used on its own or alongside other plugins like `dcat` or `structured_data` to provide multiple representations of a dataset's metadata.
    ```ini
    ckan.plugins = [...] dcat croissant structured_data
    ```

Once the plugin is enabled, the Croissant output will be embedded in the source code of each dataset page, and additionally will also be available in a dedicated endpoint:

    https://{ckan-instance-host}/dataset/{dataset-id}/croissant.jsonld

## Schema mapping

The extension includes a [schema](getting-started.md#schemas) ([`ckanext/dcat/schemas/croissant.yaml`](https://github.com/ckan/ckanext-dcat/tree/master/ckanext/dcat/schemas/croissant.yml)) for sites that want to take advantage of all the entities and properties of the Croissant spec.

This maps CKAN's datasets to [schema.org Datasets](https://docs.mlcommons.org/croissant/docs/croissant-spec.html#dataset-level-information) and resources to [Croissant resources](https://docs.mlcommons.org/croissant/docs/croissant-spec.html#resources), which can have type `FileObject` or `FileSet`. For `FileSet` resources, use the "Sub-resources" repeating subfield to describe the contents of the file set.

Additionally, for resources that have been imported to the CKAN [DataStore](https://docs.ckan.org/en/latest/maintaining/datastore.html), the resource will also expose Croissant's [RecordSet](https://docs.mlcommons.org/croissant/docs/croissant-spec.html#recordset) objects with information about the data fields (e.g. column names and types).


## Customizing

If you want to modify the Croissant output you can [write your own profile](writing-profiles.md) extending the builtin `ckanext.dcat.profiles.croissant.CroissantProfile` class and register it.

In order to use the new profile use the following config option:

```ini
ckanext.dcat.croissant.profiles = my_custom_croissant_profile
```

## Examples

* The [`examples/ckan/ckan_full_dataset_croissant.json`](https://github.com/ckan/ckanext-dcat/tree/master/examples/ckan/ckan_full_dataset_croissant.json) file contains a full CKAN dataset dict that implements the custom Croissant schema.
* Below is the Croissant serialization resulting from the dataset above, and assuming the resource has a DataStore tableassociated with the following structure:

```json
{
	"fields": [
		{"id": "name", "type": "text", "schema": {"is_index": True}},
		{"id": "age", "type": "int", "schema": {"is_index": False}},
		{"id": "temperature", "type": "float", "schema": {"is_index": False}},
		{"id": "timestamp", "type": "timestamp", "schema": {"is_index": False}},
	]
}

```


```json
{
    "@context": {
        "@vocab": "https://schema.org/",
        "citeAs": "cr:citeAs",
        "column": "cr:column",
        "conformsTo": "dct:conformsTo",
        "cr": "http://mlcommons.org/croissant/",
        "data": {
            "@id": "cr:data",
            "@type": "@json"
        },
        "dataType": {
            "@id": "cr:dataType",
            "@type": "@vocab"
        },
        "dct": "http://purl.org/dc/terms/",
        "examples": {
            "@id": "cr:examples",
            "@type": "@json"
        },
        "excludes": "cr:excludes",
        "extract": "cr:extract",
        "field": "cr:field",
        "fileObject": "cr:fileObject",
        "fileProperty": "cr:fileProperty",
        "fileSet": "cr:fileSet",
        "format": "cr:format",
        "includes": "cr:includes",
        "isLiveDataset": "cr:isLiveDataset",
        "jsonPath": "cr:jsonPath",
        "key": "cr:key",
        "md5": "cr:md5",
        "parentField": "cr:parentField",
        "path": "cr:path",
        "rai": "http://mlcommons.org/croissant/RAI/",
        "recordSet": "cr:recordSet",
        "references": "cr:references",
        "regex": "cr:regex",
        "repeated": "cr:repeated",
        "replace": "cr:replace",
        "sc": "https://schema.org/",
        "separator": "cr:separator",
        "source": "cr:source",
        "subField": "cr:subField",
        "transform": "cr:transform"
    },
    "@id": "my-custom-id",
    "@type": "Dataset",
    "citeAs": "@Article{bloggs24data, author=\"Joe Bloggs and Sally Biggs\"}",
    "conformsTo": "http://mlcommons.org/croissant/1.0",
    "creator": {
        "@id": "custom-creator-id",
        "@type": "Person",
        "email": "creator@example.org",
        "identifier": "http://example.org/creator-id",
        "name": "Test Creator",
        "url": "https://example.org"
    },
    "dateCreated": {
        "@type": "http://www.w3.org/2001/XMLSchema#date",
        "@value": "2024-05-01"
    },
    "dateModified": {
        "@type": "http://www.w3.org/2001/XMLSchema#date",
        "@value": "2024-05-05"
    },
    "datePublished": {
        "@type": "http://www.w3.org/2001/XMLSchema#date",
        "@value": "2024-05-02"
    },
    "description": "Lorem ipsum",
    "distribution": [
        {
            "@id": "my-custom-subresource-id-2",
            "@type": "cr:FileSet",
            "containedIn": {
                "@id": "my-custom-resource-id",
            },
            "description": "Test subresource 2",
            "encodingFormat": "CSV",
            "excludes": "**.txt",
            "includes": "**.csv"
        },
        {
            "@id": "my-custom-subresource-id-1",
            "@type": "cr:FileObject",
            "containedIn": {
                "@id": "my-custom-resource-id"
            },
            "contentSize": "890",
            "contentUrl": "data.txt",
            "description": "Test subresource 1",
            "encodingFormat": "TXT",
            "name": "data.txt"
        },
        {
            "@id": "my-custom-resource-id",
            "@type": "cr:FileObject",
            "contentSize": "12323",
            "contentUrl": "https://example.com/data.zip",
            "description": "Some description",
            "encodingFormat": "ZIP",
            "name": "Resource 1",
            "sha256": "b221d9dbb083a7f33428d7c2a3c3198ae925614d70210e28716ccaa7cd4ddb79"

        }
    ],
    "inLanguage": [
        "en",
        "ca",
        "es"
    ],
    "includedInDataCatalog": {
        "@type": "DataCatalog",
        "description": "",
        "name": "CKAN",
        "url": "http://test.ckan.net"
    },
    "isLiveDataset": true,
    "keywords": [
        "Tag 2",
        "Tag 1"
    ],
    "license": "http://creativecommons.org/licenses/by/3.0/",
    "name": "Test Croissant dataset",
    "publisher": {
        "@id": "custom-publisher-id",
        "@type": "Person",
        "email": "publisher@example.org",
        "identifier": "http://example.org/publisher-id",
        "name": "Test Publisher",
        "url": "https://example.org"
    },
    "recordSet": {
      "@id": "568b8ac9-8c69-4475-b35e-d7f812a63c32/records",
      "@type": "cr:RecordSet",
      "field": [
        {
          "@id": "568b8ac9-8c69-4475-b35e-d7f812a63c32/records/temperature",
          "@type": "cr:Field",
          "dataType": "Float",
          "source": {
            "extract": {
              "column": "temperature"
            },
            "fileObject": {
              "@id": "my-custom-resource-id",
            }
          }
        },
        {
          "@id": "568b8ac9-8c69-4475-b35e-d7f812a63c32/records/timestamp",
          "@type": "cr:Field",
          "dataType": "Date",
          "source": {
            "extract": {
              "column": "timestamp"
            },
            "fileObject": {
              "@id": "my-custom-resource-id"
            }
          }
        },
        {
          "@id": "568b8ac9-8c69-4475-b35e-d7f812a63c32/records/name",
          "@type": "cr:Field",
          "dataType": "Text",
          "source": {
            "extract": {
              "column": "name"
            },
            "fileObject": {
              "@id": "my-custom-resource-id"
            }
          }
        },
        {
          "@id": "568b8ac9-8c69-4475-b35e-d7f812a63c32/records/age",
          "@type": "cr:Field",
          "dataType": "Integer",
          "source": {
            "extract": {
              "column": "age"
            },
            "fileObject": {
              "@id": "my-custom-resource-id"
            }
          }
        }
      ],
      "key": {
        "@id": "568b8ac9-8c69-4475-b35e-d7f812a63c32/records/name"
      },
      "name": "568b8ac9-8c69-4475-b35e-d7f812a63c32/records"
    },
    "sameAs": [
        "https://some.other.catalog/dataset/123",
        "https://yet.another.catalog/dataset/xyz"
    ],
    "sdLicense": "http://creativecommons.org/licenses/by/3.0/",
    "url": "http://test.ckan.net/dataset/test-dataset-croissant",
    "version": "1.0.0"
}
```
