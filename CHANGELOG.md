
n.n.n / 2017-02-24
==================

  * Merge pull request #80 from ogdch/fix-typo
  * Merge pull request #79 from geosolutions-it/minor_fix_20161217
  * Fix typo in table of contents
  * Fix typo (publisher_uri)
  * Merge pull request #78 from geosolutions-it/77-improve-harvester-interface
  * Merge pull request #74 from geosolutions-it/73-serialize-numbers
  * [#77] Add more hooks in IDCATRDFHarvester
  * [#73] Fix serialization of numeric values (test)
  * Merge pull request #76 from insertjokehere/missing_i18n
  * Add MANIFEST.in to ensure i18n files are include in package
  * [#73] Fix serialization of numeric values
  * Merge branch 'vgammieri-vg/patch-missing-exports'
  * Add missing fields to test
  * Merge branch 'vg/patch-missing-exports' of https://github.com/vgammieri/ckanext-dcat into vgammieri-vg/patch-missing-exports
  * Merge branch 'ogdch-62-pagination-rdf-harvester'
  * [#62] Add a security break to avoid infinite loops
  * [#62] Add functional test for pagination
  * Emit provenance
  * Emit dcat_type
  * Add tests for next_page method
  * Initialize the parser for each call
  * Add URL to error message when downloading remote content
  * Return empty list instead of False if gather_stage fails
  * Handle HYDRA-paged RDFs in gather_stage
  * Install html5lib before ckan reqs
  * Install html5lib in the travis setup
  * Fix old tests
  * Downgrade html5lib
  * Pin html5lib
  * Fix old test
  * Merge branch 'vegvesen-feature/dcat-ap11'
  * Improve URIRef tests
  * Some last fixes
  * Fixing some tests
  * Making homepage and landingPage URIrefs
  * Updating tests for urls as URIRef
  * Making accessURL and downloadURL URIrefs instead of Literal
# Changelog


## v0.0.5 TBA

Thanks @erlingbo, @metaodi, @vgammieri, @insertjokehere, @etj and others for
all the contributions!

* Use Resources rather than Literals for dcat:landingPage, dcat:accessURL,
   dcat:downloadURL, foaf:homepage, dcat:theme (#66)
* Support for pagination on RDF Harvester (#70)
* Add missing DCAT fields on the serialization, dct:type and dct:provenance (#71)
* Add MANIFEST.in to ensure i18n files are include in package (#76)
* Add before/after create/update hooks to IDCATRDFHarvester (#77)
*
