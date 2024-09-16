The `ckan dcat` command offers utilites to transform between DCAT RDF Serializations and CKAN datasets (`ckan dcat consume`) and
viceversa (`ckan dcat produce`). In both cases the input can be provided as a path to a file:

    ckan dcat consume -f ttl examples/dcat/dataset.ttl

    ckan dcat produce -f jsonld examples/ckan/ckan_datasets.json

or be read from stdin:

    ckan dcat consume -

The latter form allows chaininig commands for more complex metadata processing, e.g.:

    curl https://demo.ckan.org/api/action/package_search | jq .result.results | ckan dcat produce -f jsonld -

For the full list of options check `ckan dcat consume --help` and  `ckan dcat produce --help`.
