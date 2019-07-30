# Changelog

## [Unreleased](https://github.com/ckan/ckanext-dcat/compare/v0.0.9...HEAD)

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
