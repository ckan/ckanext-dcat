# Changelog

## [Unreleased](https://github.com/ckan/ckanext-dcat/compare/v1.7.0...HEAD)

## [v1.7.0](https://github.com/ckan/ckanext-dcat/compare/v1.6.0...v1.7.0) - 2024-04-04

* Adds support for the latest Hydra vocabulary. For backward compatibility, the old properties are still supported but marked as deprecated. (#267)

## [v1.6.0](https://github.com/ckan/ckanext-dcat/compare/v1.5.1...v1.6.0) - 2024-02-29

* Add support for `DCATAP.applicableLegislation` and `DCATAP.hvdCategory` to the `euro_dcat_ap_2` profile (#262)
* Improve access service tests (#258)
* Fix missing access service items when parsing dataset (#256)

## [v1.5.1](https://github.com/ckan/ckanext-dcat/compare/v1.5.0...v1.5.1) - 2023-06-20

* Fix tests to work with `ckanext-harvest >= 1.5.4`. (#250)
* Add references for dcat:accessService to the `euro_dcat_ap_2` profile (#251)

## [v1.5.0](https://github.com/ckan/ckanext-dcat/compare/v1.4.0...v1.5.0) - 2023-05-02

* Remove support for old CKAN versions prior 2.9 and Python 2 (#244)
* Update hooks to support CKAN 2.10 (#241)
* Fix description for RDF endpoints in README (#246)
* Fix media type for links to the Turtle representation in HTML templates (#242)
* Ignore already deleted packages when deleting (#238)
* Add support for dcat:accessService in dcat:Distribution (#235)

## [v1.4.0](https://github.com/ckan/ckanext-dcat/compare/v1.3.0...v1.4.0) - 2022-12-05

* RDF serialization: Add fallback values for resource dates (#233)
* Add option for fallback distribution license if missing (#231)

## [v1.3.0](https://github.com/ckan/ckanext-dcat/compare/v1.2.0...v1.3.0) - 2022-08-01

* Fix assert expressions in tests (#218)
* Fix unicode encoding error on Python 2 (#225)
* Support (partial, not complete) for DCAT-AP 2.1 (#220)

#### Changed default profile
With #220 the default profile has changed from `euro_dcat_ap` to `euro_dcat_ap_2`. The following properties are additionally supported by default:
* dcat:Dataset
  * dcat:bbox und dcat:centroid (in dct:Location of dct:spatial)
  * dcat:startDate, dcat:endDate, time:hasBeginning, time:hasEnd (in dct:PeriodOfTime of dct:temporal)
  * dcat:spatialResolutionInMeters
  * dcat:temporalResolution
  * dct:isReferencedBy
* dcat:Distribution
  * dcatap:availability
  * dcat:compressFormat
  * dcat:packageFormat

How the default profile can be changed is described in the Documentation under [profiles](https://github.com/ckan/ckanext-dcat/#profiles).

## [v1.2.0](https://github.com/ckan/ckanext-dcat/compare/v1.1.3...v1.2.0) - 2022-05-25

* Support for CKAN 2.10 and Python 3.9 (#208)
* Upgrade RDFLib version (#213)
* Support URIs in more fields of the default profile (#214)
* Make HTTP-Response size configurable (#215)
* Increase harvester get content chunk size (#217)

## [v1.1.3](https://github.com/ckan/ckanext-dcat/compare/v1.1.3...v1.1.2) - 2021-11-05

* Fix behavior if `publisher_uri` is not available (#201)
* Also process URIRef in rights statements (#200)

## [v1.1.2](https://github.com/ckan/ckanext-dcat/compare/v1.1.2...v1.1.1) - 2021-06-22

* Use safer encoder for Structured Data output (#198)
* Fix: use catalog_uri logic for pagination URIs (#197)
* Introduce new interface method `after_parsing` (#196)

## [v1.1.1](https://github.com/ckan/ckanext-dcat/compare/v1.1.0...v1.1.1) - 2021-03-17

* Fix harvest encoding error on py3 (#189)
* Fix py3 syntax error (#184)
* Fixed Internal server error on login (#181)
* Remove Beautifulsoup requirement (#195)
* Migrate tests to GitHub Actions

## [v1.1.0](https://github.com/ckan/ckanext-dcat/compare/v1.0.0...v1.1.0) - 2020-03-12

* Python 3 support and new pytest based test suite (#174)
* Fix `after_show - set_titles` in plugins.py (#172)
* Add support for DCT.rightsStatement in DCT.accessRights and DCT.rights (#177)
* Add support for additional vcard representations (#178)
* Fix format normalization configuration (#175)
* Introduce the possibility to modify package update/create schema (#176)

## [v1.0.0](https://github.com/ckan/ckanext-dcat/compare/v0.0.9...v1.0.0) - 2019-11-07

* Updating the URLs to dataportals.org (#145)
* Handle import stage errors (#149)
* Pass `q` and `fq` parameters in catalog endpoint (#152)
* Include templates in package (#154)
* Ignore auth in internal search call (#156)
* Support URIRef for dct:language (#158)
* Support JSON-LD catalogs with @graph (#159)
* Make read keywords re-usable (#160)
* Extract read datasets from db to make it re-usable (#161)

## [v0.0.9](https://github.com/ckan/ckanext-dcat/compare/v0.0.8...v0.0.9) - 2019-01-10

* Make _object_value_int more robust by accepting decimals as well (#133)
* Prefer default language values for some Literal nodes (#143)
* Improved dct:format and dcat:mediaType handling (#144)
* Assign URIRef or Literal types based on content (#140)

## [v0.0.8](https://github.com/ckan/ckanext-dcat/compare/v0.0.7...v0.0.8) - 2018-10-05

* Support for CKAN >= 2.8
* Schema.org mapping improvements (#120, #139)
* Fix handling of downloadURL and accessURL (#130)
* Improve support for custom schemas when generating guids
* Improvements and refactoring of data.json harvester (#116)
* Add RDF.type to resource checksum (#132)
* Improve email addresses handling (#134)
* Escape and clean URL references (#138)

## [v0.0.7](https://github.com/ckan/ckanext-dcat/compare/v0.0.6...v0.0.7) - 2018-02-16

* Support for embedding Schema.org structured data in dataset pages (#75)
* Improve the error handling in the harvesting gather and import stage (#95)
* Avoid resource re-creation on harvesting (#91)
* Infer dataset licence from the distribution ones (#42)
* Interface for requests Session in harvesters (#98)
* Support for transitive harvesting (#96)
* Support fot cleaning tags in harvester (#103)


## [v0.0.6](https://github.com/ckan/ckanext-dcat/compare/v0.0.5...v0.0.6) - 2017-02-24

* Use Resources rather than Literals for dcat:landingPage, dcat:accessURL,
   dcat:downloadURL, foaf:homepage, dcat:theme (#66)
* Support for pagination on RDF Harvester (#70)
* Add missing DCAT fields on the serialization, dct:type and dct:provenance (#71)
* Add MANIFEST.in to ensure i18n files are include in package (#76)
* Add before/after create/update hooks to IDCATRDFHarvester (#77)
* Fix serialization of numeric values (#73)
