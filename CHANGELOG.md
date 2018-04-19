# Changelog

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
