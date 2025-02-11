# ckanext-dcat


[![Tests](https://github.com/ckan/ckanext-dcat/actions/workflows/test.yml/badge.svg)](https://github.com/ckan/ckanext-dcat/actions)


Ckanext-dcat is a [CKAN](https://github.com/ckan/ckan) extension that helps data publishers expose and consume metadata as serialized RDF documents using [DCAT](https://github.com/ckan/ckan).


> [!IMPORTANT]
> Read the documentation for a full user guide:
> https://docs.ckan.org/projects/ckanext-dcat


## Overview

In terms of CKAN features, this extension offers:

* [Pre-built CKAN schemas](https://docs.ckan.org/projects/ckanext-dcat/en/latest/getting-started#schemas) for common Application Profiles that can be adapted to each site requirements to provide out-of-the-box DCAT support in data portals, including tailored form fields, validation etc. (currently supporting DCAT AP v1, v2, and v3).

* [DCAT Endpoints](https://docs.ckan.org/projects/ckanext-dcat/en/latest/endpoints) that expose the catalog datasets in different RDF serializations (`dcat` plugin).

* An [RDF Harvester](https://docs.ckan.org/projects/ckanext-dcat/en/latest/harvester) that allows importing RDF serializations from other catalogs to create CKAN datasets (`dcat_rdf_harvester` plugin).

* Other features like [Command Line Interface](https://docs.ckan.org/projects/ckanext-dcat/en/latest/cli) or support for indexing in [Google Dataset Search](https://docs.ckan.org/projects/ckanext-dcat/en/latest/google-dataset-search).


These are implemented internally using:

* A base [mapping](https://docs.ckan.org/projects/ckanext-dcat/en/latest/mapping) between DCAT and CKAN datasets and viceversa (compatible with [DCAT-AP v1.1](https://joinup.ec.europa.eu/asset/dcat_application_profile/asset_release/dcat-ap-v11), [DCAT-AP v2.1](https://joinup.ec.europa.eu/collection/semantic-interoperability-community-semic/solution/dcat-application-profile-data-portals-europe/release/210) and [DCAT-AP v3](https://semiceu.github.io/DCAT-AP/releases/3.0.0/)).

* An [RDF Parser](https://docs.ckan.org/projects/ckanext-dcat/en/latest/profiles#rdf-dcat-parser) that allows to read RDF serializations in different formats and extract CKAN dataset dicts, using customizable [profiles](https://docs.ckan.org/projects/ckanext-dcat/en/latest/profiles#profiles).

* An [RDF Serializer](https://docs.ckan.org/projects/ckanext-dcat/en/latest/profiles#rdf-dcat-serializer) that allows to transform CKAN datasets metadata to different semantic formats, also allowing customizable [profiles](https://docs.ckan.org/projects/ckanext-dcat/en/latest/profiles#profiles).




## Running the Tests

To run the tests do:

    pytest --ckan-ini=test.ini ckanext/dcat/tests

Note that there are tests relying on having [ckanext-harvest](https://github.com/ckan/ckanext-harvest), [ckanext-scheming](https://github.com/ckan/ckanext-scheming) and [ckanext-fluent](https://github.com/ckan/ckanext-fluent) installed.

## Releases

To create a new release, follow these steps:

* Determine new release number based on the rules of [semantic versioning](http://semver.org)
* Update the CHANGELOG, especially the link for the "Unreleased" section
* Update the version number in `setup.py`
* Create a new release on GitHub and add the CHANGELOG of this release as release notes

## Acknowledgements

Work on ckanext-dcat has been made possible in part by:

* the Government of Sweden and Vinnova, as part of work on [Öppnadata.se](http://oppnadata.se), the Swedish Open Data Portal.
* [FIWARE](https://www.fiware.org), a project funded by the European Commission to integrate different technologies to offer connected cloud services from a single platform.

If you can fund new developments or contribute please get in touch.


## Copying and License

This material is copyright (c) Open Knowledge.

It is open and licensed under the GNU Affero General Public License (AGPL) v3.0 whose full text may be found at:

http://www.fsf.org/licensing/licenses/agpl-3.0.html
