# Changelog


## [Unreleased](https://github.com/ckan/ckanext-dcat/compare/v1.1.3...HEAD)


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
