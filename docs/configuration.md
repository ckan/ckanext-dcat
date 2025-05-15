### General settings

#### ckanext.dcat.rdf.profiles

Example:

```
ckanext.dcat.rdf.profiles = euro_dcat_ap_2 my_local_ap
```

Default value: `euro_dcat_ap_3`

RDF profiles to use when parsing and serializing. See [Profiles](profiles.md#profiles) for more details.


#### ckanext.dcat.translate_keys

Default value: `True`

If set to True, the plugin will automatically translate the keys of the DCAT
fields used in the frontend (at least those present in the `ckanext/dcat/i18n`
po files).


### Parsers / Serializers settings

#### ckanext.dcat.output_spatial_format

Default value: `wkt`

Format to use for geometries when serializing RDF documents. The default is
recommended as is the format expected by GeoDCAT, alternatively you can
use `geojson` (or both, which will make SHACL validation fail)


#### ckanext.dcat.resource.inherit.license

Default value: `False`

If there is no license defined for a resource / distribution, inherit it from
the dataset.


#### ckanext.dcat.normalize_ckan_format

Default value: `True`

When true, the resource label will be tried to match against the standard
list of CKAN formats (https://github.com/ckan/ckan/blob/master/ckan/config/resource_formats.json)
This allows for instance to populate the CKAN resource format field
with a value that view plugins, etc will understand (`csv`, `xml`, etc.)


#### ckanext.dcat.clean_tags

Default value: `False`

Remove special characters from keywords (use the old munge_tag() CKAN function).
This is generally not needed.


### Endpoints settings

#### ckanext.dcat.enable_rdf_endpoints

Default value: `True`

Whether to expose the catalog and dataset endpoints with the RDF DCAT
serializations.


#### ckanext.dcat.base_uri

Example:

```
ckanext.dcat.base_uri = https://my-site.org/uri/
```

Default value: none

Base URI to use when generating URIs for all entities. It needs to be a valid URI value.


#### ckanext.dcat.catalog_endpoint

Example:

```
ckanext.dcat.catalog_endpoint = /dcat/catalog/{_format}
```

Default value: `/catalog.{_format}`

Custom route for the catalog endpoint. It should start with `/` and include the
`{_format}` placeholder.


#### ckanext.dcat.datasets_per_page

Default value: `100`

Default number of datasets returned by the catalog endpoint.


#### ckanext.dcat.enable_content_negotiation

Default value: `False`

Enable content negotiation in the main catalog and dataset endpoints. Note that
setting this to True overrides the core `home.index` and `dataset.read` endpoints.


### Harvester settings

#### ckanext.dcat.max_file_size

Default value: `50`

Maximum file size that will be downloaded for parsing by the harvesters


#### ckanext.dcat.expose_subcatalogs

Default value: `False`

Store information about the origin catalog when harvesting datasets.
See https://github.com/ckan/ckanext-dcat#transitive-harvesting for more details.


### Deprecated options (will be removed in future versions)

#### ckanext.dcat.compatibility_mode

Default value: `False`

Whether to modify some fields to maintain compatibility with previous versions
of the ckanext-dcat parsers.


#### ckanext.dcat.json_endpoint

Default value: `/dcat.json`

Custom route to expose the legacy JSON endpoint


### Structured data settings

#### ckanext.dcat.structured_data.profiles

Example:

```
ckanext.dcat.structured_data.profiles = my_custom_structured_data_profile
```

Default value: `schemaorg`

Profiles to use when creating the [Structured Data](google-dataset-search.md) serializations


### Croissant ML settings

#### ckanext.dcat.croissant.profiles

Example:

```
ckanext.dcat.croissant.profiles = my_custom_croissant_profile
```

Default value: `croissant`

Profiles to use when creating the [Croissant](croissant.md) serializations



