
[Croissant](https://mlcommons.org/working-groups/data/croissant/) is a community standard for describing ML datasets. It combines information about the dataset metadata, its resources and data structure to make existing datasets easier to find and use across different tools. It builds on [schema.org](https://schema.org) and its Dataset vocabulary.


## Configuration

The `croissant` plugin enables exposing a CKAN site datasets metadata following the [Croissant format specification](https://docs.mlcommons.org/croissant/docs/croissant-spec.html):

```ini
ckan.plugins = [...] croissant
```


!!! Note
    The `croissant` plugin can be used on its own or alongside other plugins like `dcat` or `structured_data` to provide multiple representations of a site metadata.
    ```ini
    ckan.plugins = [...] dcat croissant structured_data
    ```

Once the plugin is enabled, the Croissant output will be embedded in the source code of each dataset page, and additionally will also be available in a dedicated endpoint:

    https://{ckan-instance-host}/dataset/{dataset-id}/croissant.jsonld

The extension includes a [schema](getting-started.md#schemas) ([`ckanext/dcat/schemas/croissant.yaml`](https://github.com/ckan/ckanext-dcat/tree/master/ckanext/dcat/schemas/croissant.yml)) for sites that want to take advantage of all the entities and properties of the Croissant spec.

## Customizing

If you want to modify the Croissant output you can [write your own profile](profiles.md/#writing-custom-profiles) extending the builtin `ckanext.dcat.profiles.croissant.CroissantProfile` class and register it.

In order to use the new profile use the following config option:

```ini
ckanext.dcat.croissant.profiles = my_custom_croissant_profile
```

## Examples

* The [`examples/ckan/ckan_full_dataset_croissant.json`](https://github.com/ckan/ckanext-dcat/tree/master/examples/ckan/ckan_full_dataset_croissant.json) file contains a full CKAN dataset dict that implements the custom Croissant schema.
* Below is the Croissant serialization resulting from the dataset above:

TODO
