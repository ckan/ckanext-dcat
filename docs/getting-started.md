# Getting started

## Installation


1.  Install the extension in your virtualenv:

        pip install ckanext-dcat


    !!! Note

        For versions older than **ckanext-dcat 2.3.0** use the old legacy version of the install:

            pip install -e git+https://github.com/ckan/ckanext-dcat.git#egg=ckanext-dcat

            pip install -r ckanext-dcat/requirements.txt


2.  Enable the required plugins in your ini file:

        ckan.plugins = dcat dcat_rdf_harvester structured_data

3. To use the pre-built schemas, install [ckanext-scheming](https://github.com/ckan/ckanext-scheming):

        pip install -e "git+https://github.com/ckan/ckanext-scheming.git#egg=ckanext-scheming"

Check the [Schemas](#schemas) section for extra configuration needed.

Optionally, if you want to use the RDF harvester, install [ckanext-harvest](https://github.com/ckan/ckanext-harvest#installation) as well.

For further configuration options available, see [Configuration reference](configuration.md).

## Schemas

The extension includes ready to use [ckanext-scheming](https://github.com/ckan/ckanext-scheming) schemas
that enable DCAT support. These include a schema definition file (located
in [`ckanext/dcat/schemas`](https://github.com/ckan/ckanext-dcat/tree/master/ckanext/dcat/schemas))
plus extra validators and other custom logic that integrates the metadata modifications with the
RDF DCAT [Parsers](writing-profiles.md#rdf-dcat-parser) and [Serializers](writing-profiles.md#rdf-dcat-serializer) and other CKAN features and extensions.

There are the following schemas currently included with the extension:

* *dcat_ap_recommended.yaml*: Includes the recommended properties for `dcat:Dataset` and `dcat:Distribution` according to the DCAT AP specification. You can use this schema with the `euro_dcat_ap_2` (+ `euro_dcat_ap_scheming`) and `euro_dcat_ap_3` profiles.
* *dcat_ap_full.yaml*: Includes most of the properties defined for `dcat:Dataset` and `dcat:Distribution` in the [DCAT AP v2.1](https://semiceu.github.io/DCAT-AP/releases/2.1.1/) and [DCAT AP v3](https://semiceu.github.io/DCAT-AP/releases/3.0.0/) specification. You can use this schema with the `euro_dcat_ap_2` (+ `euro_dcat_ap_scheming`) and `euro_dcat_ap_3` profiles.
* *dcat_ap_multilingual.yaml*: An example schema implementing multilingual metadata in some fields using [ckanext-fluent](https://github.com/ckan/ckanext-fluent). See [Multilingual support](profiles.md#multilingual-support) for more information.
* *dcat_us_recommended.yaml*: Includes the recommended properties for `dcat:Dataset` and `dcat:Distribution` according to the [DCAT US](https://doi-do.github.io/dcat-us/) specification. You can use this schema with the `dcat_us_3` profile.
* *dcat_us_full.yaml*: Includes most of the properties for `dcat:Dataset` and `dcat:Distribution` according to the [DCAT US](https://doi-do.github.io/dcat-us/) specification. You can use this schema with the `dcat_us_3` profile.
* *croissant.yaml*: An example schema adding all properties defined in the [Croissant format specification](https://docs.mlcommons.org/croissant/docs/croissant-spec.html). You can use this schema with the [`croissant` profile](croissant.md).

Most sites will want to use these as a base to create their own custom schema to address their own requirements, perhaps alongside a [custom profile](profiles.md#profiles). Of course site maintainers can add or remove schema fields, as well as change the existing validators.

In any case, the schema file used should be defined in the configuration file, alongside these configuration options:
```ini
# Make sure to add scheming_datasets after the dcat plugin
ckan.plugins = activity dcat [...] scheming_datasets

# Point to one of the defaults or your own version of the schema file
scheming.dataset_schemas = ckanext.dcat.schemas:dcat_ap_recommended.yaml

# Include the dcat presets as well as the standard scheming ones
scheming.presets = ckanext.scheming:presets.json ckanext.dcat.schemas:presets.yaml

# Sites using the euro_dcat_ap and euro_dcat_ap_2 profiles must add the
# euro_dcat_ap_scheming profile if they want to use ckanext-scheming schemas (see next section)
ckanext.dcat.rdf.profiles = euro_dcat_ap_2 euro_dcat_ap_scheming
```

### Compatibility with existing profiles

Sites using the existing `euro_dcat_ap` and `euro_dcat_ap_2` profiles should not see any change in their
current parsing, and serialization functionalities and these profiles will not change their outputs going
forward (unless a bug is being fixed).

Sites willing to migrate to a ckanext-scheming based metadata schema can do
so by adding the `euro_dcat_ap_scheming` profile at the end of their profile chain (e.g.
`ckanext.dcat.rdf.profiles = euro_dcat_ap_2 euro_dcat_ap_scheming`), which will modify the existing profile
outputs to the format expected by the scheming validators.

Note that the scheming profile will only affect fields defined in the schema definition file, so sites can start migrating gradually different metadata fields.

