# Application profiles

Besides the [base profiles](profiles.md) there are other profiles included to support other domain
specific application profiles.

!!! Note
    If you are interested in contributing a profile that might be useful for the wider community
    check the documentation on [writing custom profiles](writing-profiles.md) and the 
    [contribution guidelines](contributing.md#including-new-profiles).

## HealthDCAT-AP

### Introduction

This extension contains a profile (`euro_health_dcat_ap`) for the proposed 
[HealthDCAT-AP](https://healthdcat-ap.github.io/) specification.
This is a health-related extension of the DCAT application profile for sharing information about
Catalogues containing Datasets and Data Services descriptions in Europe (DCAT-AP).

The development of a Health DCAT application profile aims to standardize health metadata within 
the scope of the [European Health Data Space](https://health.ec.europa.eu/ehealth-digital-health-and-care/european-health-data-space_en)
(EHDS), fostering greater interoperability, findability and accessibility of electronic health 
data across the EU.

The goal of this profile is to provide the wider FAIR community and other EU portals with a starting
point for implementing HealthDCAT-AP within their own data catalogs.

!!! Note
    HealthDCAT-AP is still under active development and not finalized yet. Cardinalities,
    certain vocabularies and the namespace have not been officially ratified yet. These are
    expected to be finalized after the public consultation in Q1 2025.


### Usage

Use the included `euro_health_dcat_ap` profile in your configuration:

```ini
ckanext.dcat.rdf.profiles = euro_health_dcat_ap
```

The HealthDCAT-AP profile is an extension of the DCAT-AP v3 profile and requires ckanext-scheming.
See the [documentation](getting-started.md#schemas) on how to set it up. You can use the included
`health_dcat_ap.yaml` schema file as a starting point to adapt it to your needs:

```ini
scheming.dataset_schemas = ckanext.dcat.schemas:health_dcat_ap.yaml
```

This profile has currently no additional settings. 

### Limitations and deviations

As HealthDCAT-AP is still a draft, it is bound to change. There are currently still some
inconsistencies in the standard and unclarities regarding certain properties. Below is a short summary
of limitations and implementaiton decisions made during development of this profile.

1. Cardinalities have not yet been finalized for HealthDCAT-AP. This CKAN schema has taken a very
   liberal approach and takes all values as strictly optional (no failed validation for missing
   fields). Note that some mandatory fields are currently impossible to fill with real data e.g. the
   Health Data Access Body (HDAB) field: the EHDS legislation has not been implemented yet and no HDABs
   have been formally appointed.
2. The HealthDCAT-AP namespace is not formally defined yet. For now,
   `http://healthdataportal.eu/ns/health#` is used. This will be updated once the final namespace is
   standardized.
3. The official examples of the standard uses the `dct:description` property to encode the data
   purpose. This does not seem to be according to the Data Privacy Vocabulary specification, which
   proposes a controlled vocabulary. See [this issue](https://github.com/HealthDCAT-AP-de/healthdcat-ap.de/issues/11) 
   for the German perspective on this.
4. The distributions proposed by HealthDCAT-AP, *analytics* and *sample*, are not specifically
   implemented. URIs are linked, the resources themselves are not loaded. For *sample*, as this is
   an upstream DCAT-AP property, this can be included once picked up there.
5. Documentation (*foaf:page*) is implemented as an URI. There is some HealthDCAT-AP example data
  out in the wild that uses a blank node for this and adds several properties, however this is
   inconsistent with other DCAT implementations.
6. DatasetSeries are not supported yet by CKAN, and also not by this profile.
7. The *quality annotation* property has not been implemented due to usage not being completely
defined yet.
8. There is no multilingual support yet.
9. For other properties, any limitations from the DCAT-AP profiles still apply.
