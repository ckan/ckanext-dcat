# Changelog

## [Unreleased](https://github.com/ckan/ckanext-dcat/compare/v2.4.0...HEAD)


## [v2.4.0](https://github.com/ckan/ckanext-dcat/compare/v2.3.0...v2.4.0) - 2025-05-20

* Add support for [Dataset Series](https://docs.ckan.org/projects/ckanext-dcat/en/latest/dataset-series/) via integration with [ckanext-dataset-series](https://github.com/ckan/ckanext-dataset-series).
  Ckanext-dataset-series takes care of all the underlying management of the series, and ckanext-dcat exposes them
  using `dcat:DatasetSeries` classes. Check the [documentation](https://docs.ckan.org/projects/ckanext-dcat/en/latest/dataset-series/) for all details on how to set them up.
* Add `trusted_data_holder` field to HealthDCAT-AP schema ([#345](https://github.com/ckan/ckanext-dcat/pull/345))
* Fix TIME namespace definition to include trailing hash (`#`), ensuring compliance with W3C Time Ontology and DCAT-AP. This may require updates for custom profiles relying on the old variant. ([#344](https://github.com/ckan/ckanext-dcat/pull/344))
* Add missing URIRefOrLiteral import in profiles module. ([#343](https://github.com/ckan/ckanext-dcat/pull/343))

## [v2.3.0](https://github.com/ckan/ckanext-dcat/compare/v2.2.0...v2.3.0) - 2025-02-25

* New profile to support the [Croissant](https://mlcommons.org/working-groups/data/croissant/) format.
  Croissant is a community standard for describing ML datasets. The new `croissant` plugin allows a CKAN site to
  expose its datasets using the [Croissant format specification](https://docs.mlcommons.org/croissant/docs/croissant-spec.html). Check the [documentation](https://docs.ckan.org/projects/ckanext-dcat/en/latest/croissant/) for more information on schema mapping, features supported and examples. Thanks to [@Reikyo](https://github.com/Reikyo) for their contributions ([#339](https://github.com/ckan/ckanext-dcat/pull/339), [#341](https://github.com/ckan/ckanext-dcat/pull/341))
* Fix `has_version` in HealthDCAT schema ([#336](https://github.com/ckan/ckanext-dcat/pull/336))
* Include dependencies in pyproject.toml, publish extension on PyPI. This means that starting from ckanext-dcat 2.3.0 the extension can be installed by running:
    ```
      pip install ckanext-dcat
    ```
  The requirements files (`requirements.txt` and `dev-requirements.txt`) have been kept in place, so all
  existing installation workflows should keep working.


## [v2.2.0](https://github.com/ckan/ckanext-dcat/compare/v2.1.0...v2.2.0) - 2025-01-30

* New profile for the [HealthDCAT-AP](https://healthdcat-ap.github.io/) application profile. Check the
  [documentation](https://docs.ckan.org/projects/ckanext-dcat/en/latest/application-profiles/#healthdcat-ap) for all details. Thanks to folks at Health-RI for the contribution
  ([#326](https://github.com/ckan/ckanext-dcat/pull/326))
* Support for Qualified relations at the `dcat:Dataset` level in all DCAT base profiles ([97ca441](https://github.com/ckan/ckanext-dcat/commit/97ca441ec80bd68060638da9e84662da0c656de6))
* Fix parsing of spatial properties when using scheming ([#327](https://github.com/ckan/ckanext-dcat/pull/327))
* Add VCARD.hasURL property parsing/serialization ([#324](https://github.com/ckan/ckanext-dcat/pull/324))
* Support for rdflib 7.2 (date parsing) ([#323](https://github.com/ckan/ckanext-dcat/pull/323))
* Fix: Move has version from distribution to dataset ([#322](https://github.com/ckan/ckanext-dcat/pull/322))
* Decouple `dcat` and `structured_data` plugins ([#329](https://github.com/ckan/ckanext-dcat/pull/329))

## [v2.1.0](https://github.com/ckan/ckanext-dcat/compare/v2.0.0...v2.1.0) - 2024-10-31

* New base profile for the [DCAT US v3](https://doi-do.github.io/dcat-us/) specification.
  All mandatory properties and most of the recommended and optional ones are supported. During the
  implementation of this work a few adjustments have been done to the base DCAT profile ([#314](https://github.com/ckan/ckanext-dcat/pull/314)) :

    * Support for temporal and spatial resolutions in distributions, which were missing on the DCAT AP profiles
    * Allow multiple values for dct:creator in DCAT AP

* Multilingual support in DCAT profiles. Multilingual support is provided via integration
  with [ckanext-fluent](https://github.com/ckan/ckanext-fluent). Check the [documentation](https://docs.ckan.org/projects/ckanext-dcat/en/latest/profiles/#multilingual-support) for full details ([#318](https://github.com/ckan/ckanext-dcat/pull/318))
* At the serialization level, a new triple will be added for each of the defined languages
* Support for multiple agents when parsing ([#317](https://github.com/ckan/ckanext-dcat/pull/317))
* Improve serialization of statements, using RDFS.label in line with the DCAT 3 spec recommendation ([#313](https://github.com/ckan/ckanext-dcat/pull/313))
* Store UIDs from contact clases ([#312](https://github.com/ckan/ckanext-dcat/pull/312))
* Fix input issues for access_rights field ([#309](https://github.com/ckan/ckanext-dcat/pull/309))
* Add `has_version` to the full DCAT AP schema ([#306](https://github.com/ckan/ckanext-dcat/pull/306))
* Add pyproject.toml file ([#304](https://github.com/ckan/ckanext-dcat/pull/304))
* Decouple extension from ckanext-scheming ([#303](https://github.com/ckan/ckanext-dcat/pull/303))
* Add support for dct:creator in base DCAT profiles ([#302](https://github.com/ckan/ckanext-dcat/pull/302))
* Fix DCAT date validator on empty values ([#297](https://github.com/ckan/ckanext-dcat/pull/297))
* Add support for hydra collection type PartialCollectionView ([#299](https://github.com/ckan/ckanext-dcat/pull/299))

## [v2.0.0](https://github.com/ckan/ckanext-dcat/compare/v1.7.0...v2.0.0) - 2024-08-30

* New profile for [DCAT-AP v3](https://semiceu.github.io/DCAT-AP/releases/3.0.0), `euro_dcat_ap_3`, which is now
  the default. Existing sites willing to stick with DCAT-AP v2.x can specify the profile in the configuration if they
  are not doing so yet (`ckan.dcat.rdf.profiles = euro_dcat_ap_2`). The new `euro_dcat_ap_3` profile relies on
  ckanext-scheming metadata schemas (see below).
* Support for standard CKAN [ckanext-scheming](https://github.com/ckan/ckanext-scheming) schemas.
  The DCAT profiles now seamlessly integrate with fields defined via the YAML or JSON scheming files.
  Sites willing to migrate to a scheming based metadata schema can do
  so by adding the `euro_dcat_ap_scheming` profile at the end of their profile chain (e.g.
  `ckanext.dcat.rdf.profiles = euro_dcat_ap_2 euro_dcat_ap_scheming`), which will modify the existing profile
  outputs to the expected format by the scheming validators. Sample schemas are provided
  in the `ckanext/dcat/schemas` folder. See the [documentation](getting-started.md#schemas)
  for all details. Some highlights of the new scheming based profiles ([#281](https://github.com/ckan/ckanext-dcat/pull/281)):

    * Actual list support in the API output for list properties like `dct:language`
    * Multiple objects now allowed for properties like `dcat:ContactPoint`, `dct:spatial` or `dct:temporal`
    * Custom validators for date values that allow `xsd:gYear`, `xsd:gYearMonth`, `xsd:date` and `xsd:dateTime`

* [SHACL validation](https://github.com/SEMICeu/DCAT-AP/tree/master/releases/2.1.1) for DCAT-AP 2.1.1 profile (scheming and legacy).
  SHACL validation made surface the following issues in the existing profiles, which are now fixed ([#288](https://github.com/ckan/ckanext-dcat/pull/288)):
    * Cast `dcat:byteSize` and `dcat:spatialResolutionInMeters` as Decimal, not float
    * Allow only one value of `dcat:spatialResolutionInMeters` and  `dcat:temporalResolution`
    * Only output the WKT version of geometries in `locn:geometry`, `dcat:bbox` and `dcat:centroid`. Sites that for some reason
      require GeoJSON (or both) can use the `ckanext.dcat.output_spatial_format` config option
      to choose which format to use
    * When using the `euro_dcat_ap_2` profile, don't output temporal extent namespaced
    both with `schema` and `dcat`, just with the latter (`dcat:startDate` and `dcat:endDate`)
* CKAN 2.11 support and requirements updates ([#270](https://github.com/ckan/ckanext-dcat/pull/270))
* New `ckan dcat consume` and `ckan dcat produce` CLI commands ([#279](https://github.com/ckan/ckanext-dcat/pull/279))
* Revamped documentation, now hosted at [https://docs.ckan.org/projects/ckanext-dcat](https://docs.ckan.org/projects/ckanext-dcat) ([#296](https://github.com/ckan/ckanext-dcat/pull/296))
* Parse dcat:spatialResolutionInMeters as float ([#285](https://github.com/ckan/ckanext-dcat/pull/285))
* Split profile classes into their own separate files ([#282](https://github.com/ckan/ckanext-dcat/pull/282))
* Catch Not Authorized in View ([#280](https://github.com/ckan/ckanext-dcat/pull/280))


## [v1.7.0](https://github.com/ckan/ckanext-dcat/compare/v1.6.0...v1.7.0) - 2024-04-04

* Adds support for the latest Hydra vocabulary. For backward compatibility, the old properties are still supported but marked as deprecated. ([#267](https://github.com/ckan/ckanext-dcat/pull/267))

## [v1.6.0](https://github.com/ckan/ckanext-dcat/compare/v1.5.1...v1.6.0) - 2024-02-29

* Add support for `DCATAP.applicableLegislation` and `DCATAP.hvdCategory` to the `euro_dcat_ap_2` profile ([#262](https://github.com/ckan/ckanext-dcat/pull/262))
* Improve access service tests ([#258](https://github.com/ckan/ckanext-dcat/pull/258))
* Fix missing access service items when parsing dataset ([#256](https://github.com/ckan/ckanext-dcat/pull/256))

## [v1.5.1](https://github.com/ckan/ckanext-dcat/compare/v1.5.0...v1.5.1) - 2023-06-20

* Fix tests to work with `ckanext-harvest >= 1.5.4`. ([#250](https://github.com/ckan/ckanext-dcat/pull/250))
* Add references for dcat:accessService to the `euro_dcat_ap_2` profile ([#251](https://github.com/ckan/ckanext-dcat/pull/251))

## [v1.5.0](https://github.com/ckan/ckanext-dcat/compare/v1.4.0...v1.5.0) - 2023-05-02

* Remove support for old CKAN versions prior 2.9 and Python 2 ([#244](https://github.com/ckan/ckanext-dcat/pull/244))
* Update hooks to support CKAN 2.10 ([#241](https://github.com/ckan/ckanext-dcat/pull/241))
* Fix description for RDF endpoints in README ([#246](https://github.com/ckan/ckanext-dcat/pull/246))
* Fix media type for links to the Turtle representation in HTML templates ([#242](https://github.com/ckan/ckanext-dcat/pull/242))
* Ignore already deleted packages when deleting ([#238](https://github.com/ckan/ckanext-dcat/pull/238))
* Add support for dcat:accessService in dcat:Distribution ([#235](https://github.com/ckan/ckanext-dcat/pull/235))

## [v1.4.0](https://github.com/ckan/ckanext-dcat/compare/v1.3.0...v1.4.0) - 2022-12-05

* RDF serialization: Add fallback values for resource dates ([#233](https://github.com/ckan/ckanext-dcat/pull/233))
* Add option for fallback distribution license if missing ([#231](https://github.com/ckan/ckanext-dcat/pull/231))

## [v1.3.0](https://github.com/ckan/ckanext-dcat/compare/v1.2.0...v1.3.0) - 2022-08-01

* Fix assert expressions in tests ([#218](https://github.com/ckan/ckanext-dcat/pull/218))
* Fix unicode encoding error on Python 2 ([#225](https://github.com/ckan/ckanext-dcat/pull/225))
* Support (partial, not complete) for DCAT-AP 2.1 ([#220](https://github.com/ckan/ckanext-dcat/pull/220)). The following properties are additionally supported by default:
  * dcat:Dataset
    * dcat:bbox and dcat:centroid (in dct:Location of dct:spatial)
    * dcat:startDate, dcat:endDate, time:hasBeginning, time:hasEnd (in dct:PeriodOfTime of dct:temporal)
    * dcat:spatialResolutionInMeters
    * dcat:temporalResolution
    * dct:isReferencedBy
  * dcat:Distribution
    * dcatap:availability
    * dcat:compressFormat
    * dcat:packageFormat

!!! Note "Changed default profile"
    With ([#220](https://github.com/ckan/ckanext-dcat/pull/220)) the default profile has changed from `euro_dcat_ap` to `euro_dcat_ap_2`.

## [v1.2.0](https://github.com/ckan/ckanext-dcat/compare/v1.1.3...v1.2.0) - 2022-05-25

* Support for CKAN 2.10 and Python 3.9 ([#208](https://github.com/ckan/ckanext-dcat/pull/208))
* Upgrade RDFLib version ([#213](https://github.com/ckan/ckanext-dcat/pull/213))
* Support URIs in more fields of the default profile ([#214](https://github.com/ckan/ckanext-dcat/pull/214))
* Make HTTP-Response size configurable ([#215](https://github.com/ckan/ckanext-dcat/pull/215))
* Increase harvester get content chunk size ([#217](https://github.com/ckan/ckanext-dcat/pull/217))

## [v1.1.3](https://github.com/ckan/ckanext-dcat/compare/v1.1.3...v1.1.2) - 2021-11-05

* Fix behavior if `publisher_uri` is not available ([#201](https://github.com/ckan/ckanext-dcat/pull/201))
* Also process URIRef in rights statements ([#200](https://github.com/ckan/ckanext-dcat/pull/200))

## [v1.1.2](https://github.com/ckan/ckanext-dcat/compare/v1.1.2...v1.1.1) - 2021-06-22

* Use safer encoder for Structured Data output ([#198](https://github.com/ckan/ckanext-dcat/pull/198))
* Fix: use catalog_uri logic for pagination URIs ([#197](https://github.com/ckan/ckanext-dcat/pull/197))
* Introduce new interface method `after_parsing` ([#196](https://github.com/ckan/ckanext-dcat/pull/196))

## [v1.1.1](https://github.com/ckan/ckanext-dcat/compare/v1.1.0...v1.1.1) - 2021-03-17

* Fix harvest encoding error on py3 ([#189](https://github.com/ckan/ckanext-dcat/pull/189))
* Fix py3 syntax error ([#184](https://github.com/ckan/ckanext-dcat/pull/184))
* Fixed Internal server error on login ([#181](https://github.com/ckan/ckanext-dcat/pull/181))
* Remove Beautifulsoup requirement ([#195](https://github.com/ckan/ckanext-dcat/pull/195))
* Migrate tests to GitHub Actions

## [v1.1.0](https://github.com/ckan/ckanext-dcat/compare/v1.0.0...v1.1.0) - 2020-03-12

* Python 3 support and new pytest based test suite ([#174](https://github.com/ckan/ckanext-dcat/pull/174))painful
* Fix `after_show - set_titles` in plugins.py ([#172](https://github.com/ckan/ckanext-dcat/pull/172))
* Add support for DCT.rightsStatement in DCT.accessRights and DCT.rights ([#177](https://github.com/ckan/ckanext-dcat/pull/177))
* Add support for additional vcard representations ([#178](https://github.com/ckan/ckanext-dcat/pull/178))
* Fix format normalization configuration ([#175](https://github.com/ckan/ckanext-dcat/pull/175))
* Introduce the possibility to modify package update/create schema ([#176](https://github.com/ckan/ckanext-dcat/pull/176))

## [v1.0.0](https://github.com/ckan/ckanext-dcat/compare/v0.0.9...v1.0.0) - 2019-11-07

* Updating the URLs to dataportals.org ([#145](https://github.com/ckan/ckanext-dcat/pull/145))
* Handle import stage errors ([#149](https://github.com/ckan/ckanext-dcat/pull/149))
* Pass `q` and `fq` parameters in catalog endpoint ([#152](https://github.com/ckan/ckanext-dcat/pull/152))
* Include templates in package ([#154](https://github.com/ckan/ckanext-dcat/pull/154))
* Ignore auth in internal search call ([#156](https://github.com/ckan/ckanext-dcat/pull/156))
* Support URIRef for dct:language ([#158](https://github.com/ckan/ckanext-dcat/pull/158))
* Support JSON-LD catalogs with @graph ([#159](https://github.com/ckan/ckanext-dcat/pull/159))
* Make read keywords re-usable ([#160](https://github.com/ckan/ckanext-dcat/pull/160))
* Extract read datasets from db to make it re-usable ([#161](https://github.com/ckan/ckanext-dcat/pull/161))

## [v0.0.9](https://github.com/ckan/ckanext-dcat/compare/v0.0.8...v0.0.9) - 2019-01-10

* Make _object_value_int more robust by accepting decimals as well ([#133](https://github.com/ckan/ckanext-dcat/pull/133))
* Prefer default language values for some Literal nodes ([#143](https://github.com/ckan/ckanext-dcat/pull/143))
* Improved dct:format and dcat:mediaType handling ([#144](https://github.com/ckan/ckanext-dcat/pull/144))
* Assign URIRef or Literal types based on content ([#140](https://github.com/ckan/ckanext-dcat/pull/140))

## [v0.0.8](https://github.com/ckan/ckanext-dcat/compare/v0.0.7...v0.0.8) - 2018-10-05

* Support for CKAN >= 2.8
* Schema.org mapping improvements ([#120, #139](https://github.com/ckan/ckanext-dcat/pull/120, #139))
* Fix handling of downloadURL and accessURL ([#130](https://github.com/ckan/ckanext-dcat/pull/130))
* Improve support for custom schemas when generating guids
* Improvements and refactoring of data.json harvester ([#116](https://github.com/ckan/ckanext-dcat/pull/116))
* Add RDF.type to resource checksum ([#132](https://github.com/ckan/ckanext-dcat/pull/132))
* Improve email addresses handling ([#134](https://github.com/ckan/ckanext-dcat/pull/134))
* Escape and clean URL references ([#138](https://github.com/ckan/ckanext-dcat/pull/138))

## [v0.0.7](https://github.com/ckan/ckanext-dcat/compare/v0.0.6...v0.0.7) - 2018-02-16

* Support for embedding Schema.org structured data in dataset pages ([#75](https://github.com/ckan/ckanext-dcat/pull/75))
* Improve the error handling in the harvesting gather and import stage ([#95](https://github.com/ckan/ckanext-dcat/pull/95))
* Avoid resource re-creation on harvesting ([#91](https://github.com/ckan/ckanext-dcat/pull/91))
* Infer dataset licence from the distribution ones ([#42](https://github.com/ckan/ckanext-dcat/pull/42))
* Interface for requests Session in harvesters ([#98](https://github.com/ckan/ckanext-dcat/pull/98))
* Support for transitive harvesting ([#96](https://github.com/ckan/ckanext-dcat/pull/96))
* Support fot cleaning tags in harvester ([#103](https://github.com/ckan/ckanext-dcat/pull/103))


## [v0.0.6](https://github.com/ckan/ckanext-dcat/compare/v0.0.5...v0.0.6) - 2017-02-24

* Use Resources rather than Literals for dcat:landingPage, dcat:accessURL,
   dcat:downloadURL, foaf:homepage, dcat:theme ([#66](https://github.com/ckan/ckanext-dcat/pull/66))
* Support for pagination on RDF Harvester ([#70](https://github.com/ckan/ckanext-dcat/pull/70))
* Add missing DCAT fields on the serialization, dct:type and dct:provenance ([#71](https://github.com/ckan/ckanext-dcat/pull/71))
* Add MANIFEST.in to ensure i18n files are include in package ([#76](https://github.com/ckan/ckanext-dcat/pull/76))
* Add before/after create/update hooks to IDCATRDFHarvester ([#77](https://github.com/ckan/ckanext-dcat/pull/77))
* Fix serialization of numeric values ([#73](https://github.com/ckan/ckanext-dcat/pull/73))
