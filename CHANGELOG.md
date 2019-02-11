# Changelog

## v0.0.8

* Support for CKAN >= 2.8
* Schema.org mapping improvements (#120, #139)
* Fix handling of downloadURL and accessURL (#130)
* Improve support for custom schemas when generating guids
* Improvements and refactoring of data.json harvester (#116)
* Add RDF.type to resource checksum (#132)
* Improve email addresses handling (#134)
* Escape and clean URL references (#138)

## v0.0.7

* Support for embedding Schema.org structured data in dataset pages (#75)
* Improve the error handling in the harvesting gather and import stage (#95)
* Avoid resource re-creation on harvesting (#91)
* Infer dataset licence from the distribution ones (#42)
* Interface for requests Session in harvesters (#98)
* Support for transitive harvesting (#96)
* Support fot cleaning tags in harvester (#103)


## v0.0.6

* Use Resources rather than Literals for dcat:landingPage, dcat:accessURL,
   dcat:downloadURL, foaf:homepage, dcat:theme (#66)
* Support for pagination on RDF Harvester (#70)
* Add missing DCAT fields on the serialization, dct:type and dct:provenance (#71)
* Add MANIFEST.in to ensure i18n files are include in package (#76)
* Add before/after create/update hooks to IDCATRDFHarvester (#77)
* Fix serialization of numeric values (#73)
