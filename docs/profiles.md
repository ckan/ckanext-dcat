## Profiles

Both the parsers and the serializers use profile classes to allow customization of how the values defined in the RDF graph are mapped to CKAN and viceversa.

Profiles define :

* How the RDF graph values map to CKAN fields, i.e. how the RDF is parsed into CKAN datasets
* How CKAN fields map to an RDF graph, which can be then serialized
* How the CKAN catalog metadata maps to an RDF graph, which can be then serialized

They essentially define the mapping between DCAT and CKAN.

In most cases the default profile will provide a good mapping that will cover most properties described in the DCAT standard. If you want to extract extra fields defined in the RDF, are using a custom schema or
need custom logic, you can write a [custom profile](writing-profiles.md) that extends or replaces one of the default ones.

The profiles currently shipped with the extension are mostly based in the
DCAT application profiles for data portals in [Europe](https://joinup.ec.europa.eu/asset/dcat_application_profile/description) and the [US](https://doi-do.github.io/dcat-us/). As mentioned before though, they should be generic enough for most DCAT based representations.

Sites that want to support a particular version of the DCAT-AP can enable a specific profile using one of the profiles below:

* [DCAT-AP v3](https://semiceu.github.io/DCAT-AP/releases/3.0.0) (default): `euro_dcat_ap_3`
* [DCAT-US v3](https://doi-do.github.io/dcat-us/): `dcat_us_3` 
* [DCAT-AP v2.1.0](https://joinup.ec.europa.eu/collection/semantic-interoperability-community-semic/solution/dcat-application-profile-data-portals-europe/release/210): `euro_dcat_ap_2`
* [DCAT-AP v1.1.1](https://joinup.ec.europa.eu/asset/dcat_application_profile/asset_release/dcat-ap-v11): `euro_dcat_ap`

This plugin also contains a profile to serialize a CKAN dataset to a [schema.org Dataset](http://schema.org/Dataset) called `schemaorg`. This is especially useful to provide [JSON-LD structured data](google-dataset-search.md).

To define which profiles to use you can:


1. Set the [`ckanext.dcat.rdf.profiles`](configuration.md#ckanextdcatrdfprofiles) configuration option on your CKAN configuration file:

```ini
ckanext.dcat.rdf.profiles = euro_dcat_ap sweden_dcat_ap
```

2. When initializing a parser or serializer class, pass the profiles to be used as a parameter, eg:

```python

parser = RDFParser(profiles=['euro_dcat_ap', 'sweden_dcat_ap'])

serializer = RDFSerializer(profiles=['euro_dcat_ap', 'sweden_dcat_ap'])
```

Note that in both cases the order in which you define them is important, as it will be the one that the profiles will be run on.



## Multilingual support

Support for parsing and serializing multilingual properties is provided by integrating with
[ckanext-fluent](https://github.com/ckan/ckanext-fluent), which provides a way to store multilingual
data in CKAN entities like datasets and resources.

Multilingual fields need to use one of the fluent [presets](https://github.com/ckan/ckanext-fluent#fluent_text-fields) (like `fluent_text`, `fluent_markdown` or `fluent_tags`) in their schema, e.g.:

```yaml
- field_name: provenance
  preset: fluent_markdown
  label:
    en: Provenance
    ca: Procedència
    es: Procedencia
```

This will make CKAN store the values for the different languages separately. The parsers will
import properties from DCAT serializations in this format if the field is defined as fluent in
the schema:

```json
{
    "name": "test-dataset",
    "provenance": {
        "en": "Statement about provenance",
        "ca": "Una declaració sobre la procedència",
        "es": "Una declaración sobre la procedencia"
    }
}
```

!!! Note
    If one of the languages is missing in the DCAT serialization, an empty string will be
    returned for that language. Also if the DCAT serialization does not define the language
    used, the default CKAN language will be used ([`ckan.locale_default`](https://docs.ckan.org/en/latest/maintaining/configuration.html#ckan-locale-default)).


Conversely, when serializing the CKAN dataset, a new triple will be added for each of the
defined languages (if the translation is present):

```turtle
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix vcard: <http://www.w3.org/2006/vcard/ns#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<https://example.org/dataset/0112cf32-bce0-4071-9504-923375f9f2ad> a dcat:Dataset ;
    dct:title "Conjunt de dades de prova DCAT"@ca,
        "Test DCAT dataset"@en,
        "Conjunto de datos de prueba DCAT"@es ;
    dct:description "Una descripció qualsevol"@ca,
        "Some description"@en,
        "Una descripción cualquiera"@es ;
    dct:language "ca",
        "en",
        "es" ;
    dct:provenance [ a dct:ProvenanceStatement ;
        rdfs:label "Una declaració sobre la procedència"@ca,
            "Statement about provenance"@en,
            "Una declaración sobre la procedencia"@es ] ;
```

See [*examples/ckan/ckan_dataset_multilingual.json*](https://github.com/ckan/ckanext-dcat/blob/master/examples/ckan/ckan_dataset_multilingual.json) and [*examples/dcat/dataset_multilingual.ttl*](https://github.com/ckan/ckanext-dcat/blob/master/examples/dcat/dataset_multilingual.ttl)
for examples of a multilingual CKAN dataset and DCAT serialization.


Users [writing custom profiles](writing-profiles.md) can make use of the `_object_value_multilingual()`
and `_object_value_list_multilingual()` functions of the profile class to handle custom fields not defined
in the base profiles.
