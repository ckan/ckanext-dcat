As part of the CKAN ecosystem, ckanext-dcat is entirely open source and welcomes all forms of contributions from the community.
Besides the general guidance provided in the [CKAN documentation](https://docs.ckan.org/en/latest/contributing/index.html) follow these points:

* Format your code with [Black](https://github.com/psf/black).
* Make sure to include tests for your changes. The extension has an extensive test suite so in most cases you just need to copy some of the existing tests and adapt them.
* It's better to submit a pull request early, even if in draft state, to get feedback and make sure the contribution will be accepted.

### Including new profiles


New [profiles](profiles.md) that are useful to the wider community are welcome, provided that they are sustainable long term. A maintainer unfamiliar with the profile should be able to know what the profile does and be confident that everything works as expected. The way to achieve this is with tests (lots of them!) and documentation.

More localized profiles are better placed in dedicated extensions.

A contribution that adds a new profile should include:

* A new [profile class](https://github.com/ckan/ckanext-dcat/tree/master/ckanext/dcat/profiles) with parse and serialize methods (extending the DCAT v3 one)
* A new dataset [schema](https://github.com/ckan/ckanext-dcat/tree/master/ckanext/dcat/schemas) that contains all new properties supported in the new profile (it can contain just the base DCAT 3 recommended ones)
* [Example](https://github.com/ckan/ckanext-dcat/tree/master/examples) CKAN dataset and DCAT serialization of the new profile
* Tests:
    * [SHACL validation](https://github.com/ckan/ckanext-dcat/tree/1e945b6e79f0e0bae1ff76989ef9789abb5e32a8/ckanext/dcat/tests/shacl) if SHACL shapes are provided
    * [End to end](https://github.com/ckan/ckanext-dcat/blob/1e945b6e79f0e0bae1ff76989ef9789abb5e32a8/ckanext/dcat/tests/profiles/dcat_ap_3/test_euro_dcatap_3_profile_serialize.py#L44) tests covering parsing and serialization
    * Parsing and serialization tests covering [specific functionality](https://github.com/ckan/ckanext-dcat/blob/1e945b6e79f0e0bae1ff76989ef9789abb5e32a8/ckanext/dcat/tests/profiles/dcat_ap_3/test_euro_dcatap_3_profile_serialize.py#L368) for the profile
* [Documentation](https://github.com/ckan/ckanext-dcat/tree/1e945b6e79f0e0bae1ff76989ef9789abb5e32a8/docs) about the new profile (compatibility with DCAT AP versions, other profiles required, config options etc)

This might seem like a lot of requirements but using the existing linked resources as template should make things much easier. Do not hesitate to ask for help if unsure about one point.

