============
ckanext-dcat
============

This extension provides plugins that allow CKAN to expose and consume metadata
from other catalogs using documents serialized using DCAT. The Data Catalog
Vocabulary (DCAT) is "an RDF vocabulary designed to facilitate interoperability
between data catalogs published on the Web". More information can be found on
the following W3C page:

    http://www.w3.org/TR/vocab-dcat/


NOTE: Both this extension and the serializations and protocol are a work in
progress. All comments are welcome, just create an issue on the GitHub
repository or send an email to the CKAN discussion list:

    http://lists.okfn.org/mailman/listinfo/ckan-discuss


Overview
========

With the emergence of Open Data initiatives around the world, the need to share
metadata across different catalogs has became more evident. Sites like
http://publicdata.eu aggregate datasets from different portals, and there has
been a growing demand to provide a clear and standard interface to allow
incorporating metadata into them automatically.

There is growing consensus around DCAT being the right way forward, but an
actual implementation is needed. In designing the following guidelines, the
main requirement has been in all cases to keep it extremely simple, making as
easy as possible for catalogs to implement them. 

This extension offers the following Implementation Guidelines:

* A serialization format for dataset metadata in RDF/XML and JSON format, both
  based on standard DCAT properties.

* A simple mechanism for exposing a catalog metadata dumps, with optional
  methods for pagination and filtering.


In terms of CKAN, this extension offers:

* TODO: Endpoints for (paginated) dumps of all the catalog's datasets metadata
  in RDF/XML and JSON format. (``dcat_json_interface`` plugin)

* TODO: Individual endpoints for describing a dataset metadata in RDF/XML and
  JSON format. (Note: CKAN core already offers a RDF/XML representation, need
  to decide hwo they fit together).

* Harvesters that allow importing similar dumps in RDF/XML or JSON from other
  catalogs to create CKAN datasets (``dcat_json_harvester`` and ``dcat_xml_harvester`` plugins).


Install
=======

1. Install ckanext-harvest (https://github.com/ckan/ckanext-harvest#installation)

2. Install the extension on your virtualenv::

    (pyenv) $ pip install -e git+https://github.com/ckan/ckanext-dcat.git#egg=ckanext-dcat

3. Enable the required plugins in your ini file::

    ckan.plugins = dcat_xml_harvester dcat_json_harvester dcat_json_interface



