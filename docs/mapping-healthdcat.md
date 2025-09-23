## Mapping between CKAN fields and HealthDCAT-AP

This section defines how CKAN fields map to the [HealthDCAT-AP](http://healthdataportal.eu/ns/health#) extension of DCAT-AP, used to support health-specific metadata needs in CKAN datasets. These mappings are implemented in the `EuropeanHealthDCATAPProfile` class and extend the core DCAT-AP 3.0 logic.

| DCAT Class     | RDF Property                           | CKAN Dataset Field                  | Stored as | Notes |
|----------------|----------------------------------------|-------------------------------------|-----------|-------|
| dcat:Dataset   | healthdcatap:analytics                 | analytics                           | list      | Publishers are encouraged to provide URLs pointing to document repositories where users can access or request associated resources such as technical reports of the dataset, quality measurements, usability indicators,... Note that HealthDCAT-AP mentions also API endpoints or analytics services, but these would not be Distriutions but rather DatasetServices. |
| dcat:Dataset   | healthdcatap:qualityAnnotation         | quality_annotation                  | list      | This field allows annotations or notes about the quality of the dataset, such as data completeness, known issues, or validation methods. |
| dcat:Dataset   | healthdcatap:hasCodeValues             | code_values                         | list      | Inside this property, you can provide the coding system of the dataset in the form of wikidata URI (example: https://www.wikidata.org/entity/P494 for ICD-10 ID) and the URI of the value that describes the dataset (example: https://icd.who.int/browse10/2019/en#/Y59.0 for viral vaccines) |
| dcat:Dataset   | healthdcatap:hasCodingSystem           | coding_system                       | list      | This property provides informatio on which coding systems are in use inside your dataset. For this, wikidata URIs must be used.|
| dcat:Dataset   | healthdcatap:healthCategory            | health_category                     | list      | Health-specific category values. |
| dcat:Dataset   | healthdcatap:healthTheme               | health_theme                        | list      | This property is a structured way to tag the dataset with different health themes. This could include, for example, the specific disease the dataset is about. More details can be provided, if desirable, in the keywords property. Current status: the HealthDCAT-AP working group is currently exploring is other sources (ontologies, thesauri) can be used for this, next to Wikidata. To access Wikidata, click on the link in the controlled vocabulary column and search for your desired theme there. |
| dcat:Dataset   | dpv:hasLegalBasis                      | legal_basis                         | list      | The legal basis can be provided as a value from the dpv taxonomy (see Controlled vocabulary column).
While the applicable legislation indicates which legislation mandates the publication of the dataset, the legal basis property described the legal basis for initial collection and processing of (personal) data.
Example value for this property could be: dpv:Consent|
| dcat:Dataset   | dpv:hasPersonalData                    | personal_data                       | list      | The different types of personal information that are collected in the dataset can be indicated with this property. Values can be picked from the dpv taxonomy (see controlled vocabulary column).
For example: dpv-pd:Gender |
| dcat:Dataset   | healthdcatap:populationCoverage        | population_coverage                 | list      | This field is a free text description of the population covered in the dataset. For example, "Adults aged 18–65 diagnosed with type 2 diabetes in the Netherlands between 2015 and 2020". |
| dcat:Dataset   | healthdcatap:publisherNote             | publisher_note                      | list      | This property can be repeated for parallel language versions of the publisher notes. Example: "Sciensano is a research institute and the national public health institute of Belgium. It is a so-called federal scientific institution that operates under the authority of the federal minister of Public Health and the federal minister of Agriculture of Belgium."|
| dcat:Dataset   | healthdcatap:publisherType             | publisher_type                      | list      |Current status: Specifically for the health domain, a controlled vocabulary is being developed to include commonly recognised health publishers. This vocabulary is currently under development. Version 1.0 includes the following types: Academia-ScientificOrganisation, Company, IndustryConsortium, LocalAuthority, NationalAuthority, NonGovernmentalOrganisation, NonProfitOrganisation, PrivateIndividual, RegionalAuthority, StandardisationBody and SupraNationalAuthority. These should use the following URL: http://purl.org/adms/publishertype/[type]. |
| dcat:Dataset   | dpv:hasPurpose                         | purpose                             | list      | One (or many) category or sub-category of the purposes can be chosen from the taxonomy provided by dpv (see controlled vocabulary column).
Example value could be: dpv:ResearchAndDevelopment. |
| dcat:Dataset   | healthdcatap:minTypicalAge             | min_typical_age                     | integer   | The approximate minimum age of subjects in the dataset, if applicable. Approximate age is given to protect potentially sensitive information of subjects in the dataset.|
| dcat:Dataset   | healthdcatap:maxTypicalAge             | max_typical_age                     | integer   | The approximate maximum age of subjects in the dataset, if applicable. Approximate age is given to protect potentially sensitive information of subjects in the dataset. |
| dcat:Dataset   | healthdcatap:numberOfRecords           | number_of_records                   | integer   | Number of records inside a Dataset. |
| dcat:Dataset   | healthdcatap:numberOfUniqueIndividuals | number_of_unique_individuals       | integer   | This property is not mandatory, since not all datasets might include data from individuals. |
| dcat:Dataset   | healthdcatap:hdab                      | hdab                                | agent     | Health Data Access Body responsible. |
| dcat:Dataset   | healthdcatap:retentionPeriod           | retention_period                    | interval  | This property makes use of the class dct:PeriodOfTime, in which a start and end date should be provided. |
| dcat:Distribution | healthdcatap:retentionPeriod     | resources_retention_period       | interval  | This property makes use of the class dct:PeriodOfTime, in which a start and end date should be provided. |

### Notes

- All `list` values are exported using `rdf:List`, supporting multi-valued entries.
- `hdab` is parsed as an `foaf:Agent` and may include structured details.
- `retention_period` expects a nested dictionary like `{ "start": <date>, "end": <date> }`.
- When language-specific literals are needed (eg `population_coverage`, `publisher_note`, `title`, resource `rights`), enable the Fluent-aware schema `ckanext.dcat.schemas:health_dcat_ap_multilingual.yaml` together with the `fluent` plugin and include `ckanext.fluent:presets.json` in `scheming.presets`. This ensures translated values round-trip when harvesting and serializing HealthDCAT-AP content.

!!! Note
    See [EuropeanHealthDCATAPProfile](https://github.com/ckan/ckanext-dcat/blob/master/ckanext/dcat/profiles/euro_health_dcat_ap.py) for implementation details.
