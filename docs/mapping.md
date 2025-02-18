## RDF DCAT to CKAN dataset mapping

The following table provides a generic mapping between the fields of the `dcat:Dataset` and `dcat:Distribution` classes and
their equivalents in the CKAN model. In most cases this mapping is deliberately a loose one. For instance, it does not try to link
the DCAT publisher property with a CKAN dataset author, maintainer or organization, as the link between them is not straight-forward
and may depend on a particular instance needs. When mapping from CKAN metadata to DCAT though, there are in some cases fallback fields
that are used if the default field is not present (see [RDF Serializer](writing-profiles.md#rdf-dcat-serializer) for more details on this).

This mapping is compatible with **DCAT-AP** [v1.1](https://joinup.ec.europa.eu/asset/dcat_application_profile/asset_release/dcat-ap-v11), [v2.1](https://joinup.ec.europa.eu/collection/semantic-interoperability-community-semic/solution/dcat-application-profile-data-portals-europe/release/210) and [v3](https://semiceu.github.io/DCAT-AP/releases/3.0.0/) and **DCAT-US** [v3](https://doi-do.github.io/dcat-us/). It depends on the active [profile(s)](profiles.md#profiles) and the fields present in your custom [schema](getting-started.md#schemas) which DCAT properties are mapped.

Sites are encouraged to use ckanext-scheming to manage their metadata schema (see [Schemas](getting-started.md#schemas) for all details). This changes in
some cases the way metadata is stored internally and presented at the CKAN API level, but should not affect the RDF DCAT output.

!!! Note
    Fields prefixed with `custom:` are custom metadata fields defined via ckanext-scheming. When using `euro_dcat_ap`
    and `euro_dcat_ap_2` based profiles, these could also be actual extra fields (e.g. `extras=[{"key": "issued", "value": "2024"}]`).
    It is recommended that site maintainers start to migrate to custom fields by using the `euro_dcat_ap_scheming` profile as this
    fields are properly validated, can use the scheming snippets etc. See [Schemas](getting-started.md#schemas) for more details.


| DCAT class        | DCAT property                  | CKAN dataset field                         | CKAN fallback fields           | Stored as |                                                                                                                                                               |
|-------------------|--------------------------------|--------------------------------------------|--------------------------------|-----------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| dcat:Dataset      | -                              | custom:uri                                 |                                | text      |  See [URIs](mapping.md#uris)                                                                                                                                           |
| dcat:Dataset      | dct:title                      | title                                      |                                | text      |                                                                                                                                                               |
| dcat:Dataset      | dct:description                | notes                                      |                                | text      |                                                                                                                                                               |
| dcat:Dataset      | dcat:keyword                   | tags                                       |                                | text      |                                                                                                                                                               |
| dcat:Dataset      | dcat:theme                     | custom:theme                               |                                | list      |  See [Lists](#lists)                                                                                                                                          |
| dcat:Dataset      | dct:identifier                 | custom:identifier                          | custom:guid, id                | text      |                                                                                                                                                               |
| dcat:Dataset      | adms:identifier                | custom:alternate_identifier                |                                | text      |                                                                                                                                                               |
| dcat:Dataset      | dct:issued                     | custom:issued                              | metadata_created               | text      |                                                                                                                                                               |
| dcat:Dataset      | dct:modified                   | custom:modified                            | metadata_modified              | text      |                                                                                                                                                               |
| dcat:Dataset      | owl:versionInfo                | version                                    | custom:dcat_version            | text      |                                                                                                                                                               |
| dcat:Dataset      | adms:versionNotes              | custom:version_notes                       |                                | text      |                                                                                                                                                               |
| dcat:Dataset      | dct:language                   | custom:language                            |                                | list      |  See [Lists](#lists)                                                                                                                                          |
| dcat:Dataset      | dcat:landingPage               | url                                        |                                | text      |                                                                                                                                                               |
| dcat:Dataset      | dct:accrualPeriodicity         | custom:frequency                           |                                | text      |                                                                                                                                                               |
| dcat:Dataset      | dct:conformsTo                 | custom:conforms_to                         |                                | list      |  See [Lists](#lists)                                                                                                                                          |
| dcat:Dataset      | dct:accessRights               | custom:access_rights                       |                                | text      |                                                                                                                                                               |
| dcat:Dataset      | foaf:page                      | custom:documentation                       |                                | list      |  See [Lists](#lists)                                                                                                                                          |
| dcat:Dataset      | dct:provenance                 | custom:provenance                          |                                | text      |                                                                                                                                                               |
| dcat:Dataset      | dcat-us:liabilityStatement     | custom:liability                           |                                | text      | DCAT-US v3 and higher only
| dcat:Dataset      | dcat-us:purpose                | custom:purpose                             |                                | text      | DCAT-US v3 and higher only
| dcat:Dataset      | skos:scopeNote                 | custom:usage                               |                                | text      | DCAT-US v3 and higher only
| dcat:Dataset      | dct:type                       | custom:dcat_type                           |                                | text      |                                                                                             |
| dcat:Dataset      | dct:hasVersion                 | custom:has_version                         |                                | list      |  See [Lists](#lists). It is assumed that these are one or more URIs referring to another dcat:Dataset                                                         |
| dcat:Dataset      | dct:isVersionOf                | custom:is_version_of                       |                                | list      |  See [Lists](#lists). It is assumed that these are one or more URIs referring to another dcat:Dataset                                                         |
| dcat:Dataset      | dct:source                     | custom:source                              |                                | list      |  See [Lists](#lists). It is assumed that these are one or more URIs referring to another dcat:Dataset                                                         |
| dcat:Dataset      | adms:sample                    | custom:sample                              |                                | list      |  See [Lists](#lists). It is assumed that these are one or more URIs referring to dcat:Distribution instances                                                  |
| dcat:Dataset      | dct:spatial                    | custom:spatial_uri                         |                                | text      | See [Spatial coverage](#spatial-coverage) |
| dcat:Dataset      | dct:temporal                   | custom:temporal_start + custom:temporal_end |                                | text      | None, one or both extras can be present                                                                                                                       |
| dcat:Dataset      | dcat-us:geographicBoundingBox  | custom:bbox                                |                                 | list of objects | DCAT-US v3 and higher only
| dcat:Dataset      | dcat-us:describedBy            | custom:data_dictionary                     |                                 | list of objects | DCAT-US v3 and higher only
| dcat:Dataset      | dcat:temporalResolution        | custom:temporal_resolution                 |                                | list      |                                                                                                                                                               |
| dcat:Dataset      | dcat:spatialResolutionInMeters | custom:spatial_resolution_in_meters        |                                | list      |                                                                                                                                                               |
| dcat:Dataset      | dct:isReferencedBy             | custom:is_referenced_by                    |                                | list      |                                                                                                                                                               |
| dcat:Dataset      | dct:publisher                  | custom:publisher_uri                       |                                | list of objects      |  See [URIs](mapping.md#uris) and [Publisher](#contact-points-and-publisher)                                                                                                                                           |
| foaf:Agent        | foaf:name                      | custom:publisher_name                      |                                | text      |                                                                                                                                                               |
| foaf:Agent        | foaf:mbox                      | custom:publisher_email                     | organization:title             | text      |                                                                                                                                                               |
| foaf:Agent        | foaf:homepage                  | custom:publisher_url                       |                                | text      |                                                                                                                                                               |
| foaf:Agent        | dct:type                       | custom:publisher_type                      |                                | text      |                                                                                                                                                               |
| foaf:Agent        | dct:identifier                 | custom:publisher_id                        |                                | text      |
| dcat:Dataset      | dct:creator                    | custom:creator_uri                         |                                | list of objects      |  See [URIs](mapping.md#uris) |
| foaf:Agent        | foaf:name                      | custom:creator_name                        |                                | text      |                                                                                                                                                               |
| foaf:Agent        | foaf:mbox                      | custom:creator_email                       | organization:title             | text      |                                                                                                                                                               |
| foaf:Agent        | foaf:homepage                  | custom:creator_url                         |                                | text      |                                                                                                                                                               |
| foaf:Agent        | dct:type                       | custom:creator_type                        |                                | text      |                                                                                                                                                               |
| foaf:Agent        | dct:identifier                 | custom:creator_id                          |                                | text      |
| dcat:Dataset      | dct:contributor                | custom:contributor                         |                                | list of objects    |  See [URIs](mapping.md#uris). The object properties are the same than publishers and creators. DCAT-US v3 and higher only                                                                                                                                            |
| dcat:Dataset      | dcat:contactPoint              | custom:contact_uri                         |                                | list of objects     |  See [URIs](mapping.md#uris) and [Contact points](#contact-points-and-publisher)                                                                                                                                          |
| vcard:Kind        | vcard:fn                       | custom:contact_name                        | maintainer, author             | text      |                                                                                                                                                               |
| vcard:Kind        | vcard:hasEmail                 | custom:contact_email                       | maintainer_email, author_email | text      |                                                                                                                                                               |
| vcard:Kind        | vcard:hasUID                   | custom:contact_identifier                  |                                | text      |                                                                                                                                                               |
| dcat:Dataset      | dcat:distribution              | resources                                  |                                | text      |                                                                                                                                                               |
| dcat:Distribution | -                              | resource:uri                               |                                | text      |  See [URIs](mapping.md#uris)                                                                                                                                           |
| dcat:Distribution | dct:title                      | resource:name                              |                                | text      |                                                                                                                                                               |
| dcat:Distribution | dcat:accessURL                 | resource:access_url                        | resource:url                   | text      | If downloadURL is not present, accessURL will be used as resource url                                                                                         |
| dcat:Distribution | dcat:downloadURL               | resource:download_url                      |                                | text      | If present, downloadURL will be used as resource url                                                                                                          |
| dcat:Distribution | dct:description                | resource:description                       |                                | text      |                                                                                                                                                               |
| dcat:Distribution | dcat:mediaType                 | resource:mimetype                          |                                | text      |                                                                                                                                                               |
| dcat:Distribution | dct:format                     | resource:format                            |                                | text      |                                                     |
| dcat:Distribution | dct:license                    | resource:license                           |                                | text      | See [Licenses](#licenses)                                                                                                                                |
| dcat:Distribution | adms:status                    | resource:status                            |                                | text      |                                                                                                                                                               |
| dcat:Distribution | dcat:byteSize                  | resource:size                              |                                | number    |                                                                                                                                                               |
| dcat:Distribution | dct:issued                     | resource:issued                            | created                        | text      |                                                                                                                                                               |
| dcat:Distribution | dct:modified                   | resource:modified                          | metadata_modified              | text      |                                                                                                                                                               |
| dcat:Distribution | dct:rights                     | resource:rights                            |                                | text      |                                                                                                                                                               |
| dcat:Distribution | foaf:page                      | resource:documentation                     |                                | list      |  See [Lists](#lists)                                                                                                                                          |
| dcat:Distribution | dct:language                   | resource:language                          |                                | list      |  See [Lists](#lists)                                                                                                                                          |
| dcat:Distribution | dct:conformsTo                 | resource:conforms_to                       |                                | list      |  See [Lists](#lists)                                                                                                                                          |
| dcat:Distribution | dcatap:availability            | resource:availability                      |                                | text      |                                                                                                                                                               |
| dcat:Distribution | dcat:compressFormat            | resource:compress_format                   |                                | text      |                                                                                                                                                               |
| dcat:Distribution | dcat:packageFormat             | resource:package_format                    |                                | text      |                                                                                                                                                               |
| dcat:Distribution | cnt:characterEncoding          | resource:package_format                    |                                | text      | DCAT-US v3 and higher only
| dcat:Distribution | dct:identifier                 | custom:identifier                          | custom:guid, id                | text      | DCAT-US v3 and higher only
| dcat:Distribution | dcat-us:describedBy            | custom:data_dictionary                     |                                 | list of objects | DCAT-US v3 and higher only
| dcat:Distribution | dcat:accessService             | resource:access_services                   |                                | list of objects      |                                                                                                                                                               |
| dcat:DataService  | dct:title                      | access_service:title                       |                                | text      |                                                                                                                                                               |
| dcat:DataService  | dcat:endpointURL               | access_service:endpoint_url                |                                | list      |                                                                                                                                                               |
| dcat:DataService  | dcat:endpointDescription       | access_service:endpoint_description        |                                | text      |                                                                                                                                                               |
| dcat:DataService  | dcatap:availability            | access_service:availability                |                                | text      |                                                                                                                                                               |
| dcat:DataService  | dcat:servesDataset             | access_service:serves_dataset              |                                | list      |                                                                                                                                                               |
| dcat:DataService  | dct:description                | access_service:description                 |                                | text      |                                                                                                                                                               |
| dcat:DataService  | dct:license                    | access_service:license                     |                                | text      |                                                                                                                                                               |
| dcat:DataService  | dct:accessRights               | access_service:access_rights               |                                | text      |                                                                                                                                                               |
| spdx:Checksum     | spdx:checksumValue             | resource:hash                              |                                | text      |                                                                                                                                                               |
| spdx:Checksum     | spdx:algorithm                 | resource:hash_algorithm                    |                                | text      |                                                                                                                                                               |

### Custom fields

Fields marked as `custom:` are stored as free form extras in the `euro_dcat_ap` and `euro_dcat_ap_2` profiles,
but stored as first level custom fields when using the scheming based profile (`euro_dcat_ap_scheming`), i.e:

```json
{
    "name": "test_dataset_dcat",
    "extras": [
         {"key": "version_notes", "value": "Some version notes"}
    ]
}
```

  vs:

```json
{
    "name": "test_dataset_dcat",
    "version_notes": "Some version notes"
}
```

### URIs

Whenever possible, URIs are extracted and stored so there is a clear reference to the original RDF resource.
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

```turtle
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

### Lists

On the legacy profiles, lists are stored as a JSON string, eg:

```turtle
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
        {"key": "uri", "value": "http://data.some.org/catalog/datasets/1"},
        {"key": "language", "value": "[\"ca\", \"en\", \"es\"]"},
        {"key": "theme", "value": "[\"Earth Sciences\", \"http://eurovoc.europa.eu/209065\", \"http://eurovoc.europa.eu/100142\"]"}
    ]
}
```

On the scheming-based ones, these are shown as actual lists:

```json
{
    "title": "Dataset 1",
    "uri": "http://data.some.org/catalog/datasets/1"},
    "language": ["ca", "en", "es"],
    "theme": ["Earth Sciences", "http://eurovoc.europa.eu/209065", "http://eurovoc.europa.eu/100142"]
}
```
### Contact points and Publisher

Properties for `dcat:contactPoint` and `dct:publisher` are stored as namespaced extras in the legacy profiles. When using
a scheming-based profile, these are stored as proper objects (and multiple instances are allowed for contact point):

```json
{
    "name": "test_dataset_dcat",
    "title": "Test dataset DCAT",
    "extras": [
        {"key":"contact_name","value":"PointofContact"},
        {"key":"contact_email","value":"contact@some.org"}
    ],
}
```

vs:

```json
{
    "name": "test_dataset_dcat",
    "title": "Test dataset DCAT",
    "contact": [
        {
            "name": "Point of Contact 1",
            "email": "contact1@some.org"
        },
        {
            "name": "Point of Contact 2",
            "email": "contact2@some.org"
        },
    ]
}
```

If no `publisher` or `publisher_*` fields are found, the serializers will fall back to getting the publisher properties from the organization the CKAN dataset belongs to. The organization schema can be customized with the schema located in `ckanext/dcat/schemas/publisher_organization.yaml` to provide the extra properties supported (this will additionally require loading the `scheming_organizations` plugin in `ckan.plugins`).


### Spatial coverage


The following formats for `dct:spatial` are supported by the default [parser](writing-profiles.md#rdf-dcat-parser). Note that the default [serializer](writing-profiles.md#rdf-dcat-serializer) will return the single `dct:spatial` instance form by default.

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

If the RDF provides them, profiles should store the textual and geometric representation of the location in:

* For legacy profiles in `spatial_text`, `spatial_bbox`, `spatial_centroid` or `spatial` (for any other geometries) extra fields
* For scheming-based profiles in objects in the `spatial_coverage` field, for instance:

```json
{
    "name": "test_dataset_dcat",
    "title": "Test dataset DCAT",
    "spatial_coverage": [
        {
            "geom": {
                "type": "Polygon",
                "coordinates": [...]
            },
            "text": "Tarragona",
            "uri": "https://sws.geonames.org/6361390/",
            "bbox": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-2.1604, 42.7611],
                        [-2.0938, 42.7611],
                        [-2.0938, 42.7931],
                        [-2.1604, 42.7931],
                        [-2.1604, 42.7611],
                    ]
                ],
            },
            "centroid": {"type": "Point", "coordinates": [1.26639, 41.12386]},
        }
    ]
}
```


### Licenses

In the CKAN model, the license field is stored at the dataset level whereas in the DCAT model it
is stored at Distributions level. By default, the RDF parser will try to find a
distribution with a license that matches one of those registered in CKAN
and attach this license to the dataset. The first matching distribution's
license is used, meaning that any discrepancy accross distributions license
will not be accounted for. This behavior can be customized by overridding the
`_license()` method on a custom profile.

When serializing, distributions can inherit the license from the dataset
if [`ckanext.dcat.resource.inherit.license`](configuration.md#ckanextdcatresourceinheritlicense) is set to true.



