## Google Dataset Search indexing

The `structured_data` and `croissant` plugins will add [structured data](https://developers.google.com/search/docs/guides/intro-structured-data) JSON-LD markup snippets to dataset pages, which allow your datasets to be indexed by [Google Dataset Search](https://toolbox.google.com/datasetsearch). With reference to [Profiles](profiles.md#profiles), the `structured_data` plugin adds markup determined by the `schemaorg` profile, based on the [schema.org](https://schema.org) vocabulary, and the `croissant` plugin adds markup determined by the `croissant` profile, based on the [Croissant](https://docs.mlcommons.org/croissant/docs/croissant-spec.html) vocabulary. The `dcat`, `structured_data` and `croissant` plugins are all independent, and you can load any or all of them in your `ckan.ini` file depending on your needs:

    ckan.plugins = dcat structured_data croissant

To use a custom profile, which should live in [`profiles/`](https://github.com/ckan/ckanext-dcat/blob/master/ckanext/dcat/profiles/), you can either enable the `structured_data` plugin and override the Jinja template block called `structured_data` in [`templates/structured_data/package/read_base.html`](https://github.com/ckan/ckanext-dcat/blob/master/ckanext/dcat/templates/structured_data/package/read_base.html), or you can enable the `croissant` plugin and override the Jinja template block called `croissant` in [`templates/croissant/package/read_base.html`](https://github.com/ckan/ckanext-dcat/blob/master/ckanext/dcat/templates/croissant/package/read_base.html). Either way, replace the existing script in your chosen block with the following, and change `my_custom_profile` to whatever you called your custom profile:

    <script type="application/ld+json">
    {{ h.structured_data(pkg, ['my_custom_profile']) | safe }}
    </script>

### Example using the `structured_data` plugin

Using the `structured_data` plugin, the JSON-LD embedded in the dataset page source is as follows:

```html
    <!-- Structured data -->
    <script type="application/ld+json">
    {
        "@context": {
            "brick": "https://brickschema.org/schema/Brick#",
            "csvw": "http://www.w3.org/ns/csvw#",
            "dc": "http://purl.org/dc/elements/1.1/",
            "dcam": "http://purl.org/dc/dcam/",
            "dcat": "http://www.w3.org/ns/dcat#",
            "dcmitype": "http://purl.org/dc/dcmitype/",
            "dcterms": "http://purl.org/dc/terms/",
            "doap": "http://usefulinc.com/ns/doap#",
            "foaf": "http://xmlns.com/foaf/0.1/",
            "geo": "http://www.opengis.net/ont/geosparql#",
            "odrl": "http://www.w3.org/ns/odrl/2/",
            "org": "http://www.w3.org/ns/org#",
            "owl": "http://www.w3.org/2002/07/owl#",
            "prof": "http://www.w3.org/ns/dx/prof/",
            "prov": "http://www.w3.org/ns/prov#",
            "qb": "http://purl.org/linked-data/cube#",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "schema": "http://schema.org/",
            "sh": "http://www.w3.org/ns/shacl#",
            "skos": "http://www.w3.org/2004/02/skos/core#",
            "sosa": "http://www.w3.org/ns/sosa/",
            "ssn": "http://www.w3.org/ns/ssn/",
            "time": "http://www.w3.org/2006/time#",
            "vann": "http://purl.org/vocab/vann/",
            "void": "http://rdfs.org/ns/void#",
            "wgs": "https://www.w3.org/2003/01/geo/wgs84_pos#",
            "xsd": "http://www.w3.org/2001/XMLSchema#"
        },
        "@graph": [
            {
                "@id": "http://demo.ckan.org/organization/34ab2c70-7815-450e-ade4-3cd829297301",
                "@type": "schema:Organization",
                "schema:contactPoint": [
                    {
                        "@id": "_:N7936bff54c874207a8f81f9924489b04"
                    },
                    {
                        "@id": "_:Ne35537c8986f454fac9428ad26056ea0"
                    }
                ],
                "schema:name": "Public Transport Organization"
            },
            {
                "@id": "_:N7936bff54c874207a8f81f9924489b04",
                "@type": "schema:ContactPoint",
                "schema:contactType": "customer service",
                "schema:email": "contact@example.com",
                "schema:name": "Public Transport Organization",
                "schema:url": "http://demo.ckan.org"
            },
            {
                "@id": "_:Ne35537c8986f454fac9428ad26056ea0",
                "@type": "schema:ContactPoint",
                "schema:contactType": "customer service",
                "schema:email": "contact@example.com",
                "schema:name": "Public Transport Organization",
                "schema:url": "http://demo.ckan.org"
            },
            {
                "@id": "http://demo.ckan.org/dataset/5fbc24dd-deb9-4b8b-a145-0708e74fc3c7/resource/8597cd81-bb01-424c-8aa2-b23d457c88a2",
                "@type": "schema:DataDownload",
                "schema:description": "Information about all stations locations (addresses and geo coordinates) and facilities (parking, toilets, cycle storage, shops).",
                "schema:encodingFormat": "JSON",
                "schema:name": "stations-locations-and-facilities.json",
                "schema:url": "http://demo.ckan.org/dataset/5fbc24dd-deb9-4b8b-a145-0708e74fc3c7/resource/8597cd81-bb01-424c-8aa2-b23d457c88a2/download/stations-locations-and-facilities.json"
            },
            {
                "@id": "http://demo.ckan.org/dataset/5fbc24dd-deb9-4b8b-a145-0708e74fc3c7/resource/42fb066a-48a6-4233-be0c-ffdc3131d6a9",
                "@type": "schema:DataDownload",
                "schema:description": "Information about all stations scheduled engineering works (location, start date and time, duration).",
                "schema:encodingFormat": "JSON",
                "schema:name": "stations-scheduled-engineering.json",
                "schema:url": "http://demo.ckan.org/dataset/5fbc24dd-deb9-4b8b-a145-0708e74fc3c7/resource/42fb066a-48a6-4233-be0c-ffdc3131d6a9/download/stations-scheduled-engineering.json"
            },
            {
                "@id": "http://demo.ckan.org/dataset/5fbc24dd-deb9-4b8b-a145-0708e74fc3c7",
                "@type": "schema:Dataset",
                "schema:creator": {
                    "@id": "http://demo.ckan.org/organization/34ab2c70-7815-450e-ade4-3cd829297301"
                },
                "schema:dateModified": "2025-01-13T18:19:53.984608",
                "schema:datePublished": "2025-01-13T17:07:40.203736",
                "schema:description": "Information about all stations, including locations and details of facilities where available, as well as scheduled engineering works.",
                "schema:distribution": [
                    {
                        "@id": "http://demo.ckan.org/dataset/5fbc24dd-deb9-4b8b-a145-0708e74fc3c7/resource/42fb066a-48a6-4233-be0c-ffdc3131d6a9"
                    },
                    {
                        "@id": "http://demo.ckan.org/dataset/5fbc24dd-deb9-4b8b-a145-0708e74fc3c7/resource/8597cd81-bb01-424c-8aa2-b23d457c88a2"
                    }
                ],
                "schema:includedInDataCatalog": {
                    "@id": "_:Nd8e5fe40ab564606a4277beeee154fc9"
                },
                "schema:keywords": "transport",
                "schema:license": "http://www.opendefinition.org/licenses/cc-by-sa",
                "schema:name": "Stations",
                "schema:publisher": {
                    "@id": "http://demo.ckan.org/organization/34ab2c70-7815-450e-ade4-3cd829297301"
                },
                "schema:url": "http://demo.ckan.org/dataset/stations"
            },
            {
                "@id": "_:Nd8e5fe40ab564606a4277beeee154fc9",
                "@type": "schema:DataCatalog",
                "schema:description": "",
                "schema:name": "CKAN",
                "schema:url": "http://demo.ckan.org"
            }
        ]
    }
    </script>
```

### Example using the `croissant` plugin

Using the `croissant` plugin, the JSON-LD embedded in the dataset page source is as follows:

```html
    <!-- Croissant ML -->
    <script type="application/ld+json">
    {
        "@context": {
            "brick": "https://brickschema.org/schema/Brick#",
            "cr": "http://mlcommons.org/croissant/",
            "csvw": "http://www.w3.org/ns/csvw#",
            "dc": "http://purl.org/dc/elements/1.1/",
            "dcam": "http://purl.org/dc/dcam/",
            "dcat": "http://www.w3.org/ns/dcat#",
            "dcmitype": "http://purl.org/dc/dcmitype/",
            "dcterms": "http://purl.org/dc/terms/",
            "doap": "http://usefulinc.com/ns/doap#",
            "foaf": "http://xmlns.com/foaf/0.1/",
            "geo": "http://www.opengis.net/ont/geosparql#",
            "odrl": "http://www.w3.org/ns/odrl/2/",
            "org": "http://www.w3.org/ns/org#",
            "owl": "http://www.w3.org/2002/07/owl#",
            "prof": "http://www.w3.org/ns/dx/prof/",
            "prov": "http://www.w3.org/ns/prov#",
            "qb": "http://purl.org/linked-data/cube#",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "schema": "http://schema.org/",
            "sh": "http://www.w3.org/ns/shacl#",
            "skos": "http://www.w3.org/2004/02/skos/core#",
            "sosa": "http://www.w3.org/ns/sosa/",
            "ssn": "http://www.w3.org/ns/ssn/",
            "time": "http://www.w3.org/2006/time#",
            "vann": "http://purl.org/vocab/vann/",
            "void": "http://rdfs.org/ns/void#",
            "wgs": "https://www.w3.org/2003/01/geo/wgs84_pos#",
            "xsd": "http://www.w3.org/2001/XMLSchema#"
        },
        "@graph": [
            {
                "@id": "34ab2c70-7815-450e-ade4-3cd829297301",
                "@type": "schema:Organization",
                "schema:email": "contact@example.com",
                "schema:name": "Public Transport Organization",
                "schema:url": "http://demo.ckan.org"
            },
            {
                "@id": "http://demo.ckan.org/dataset/5fbc24dd-deb9-4b8b-a145-0708e74fc3c7/resource/8597cd81-bb01-424c-8aa2-b23d457c88a2",
                "@type": "cr:FileObject",
                "schema:contentUrl": "http://demo.ckan.org/dataset/5fbc24dd-deb9-4b8b-a145-0708e74fc3c7/resource/8597cd81-bb01-424c-8aa2-b23d457c88a2/download/stations-locations-and-facilities.json",
                "schema:description": "Information about all stations locations (addresses and geo coordinates) and facilities (parking, toilets, cycle storage, shops).",
                "schema:encodingFormat": "JSON",
                "schema:name": "stations-locations-and-facilities.json"
            },
            {
                "@id": "http://demo.ckan.org/dataset/5fbc24dd-deb9-4b8b-a145-0708e74fc3c7/resource/42fb066a-48a6-4233-be0c-ffdc3131d6a9",
                "@type": "cr:FileObject",
                "schema:contentUrl": "http://demo.ckan.org/dataset/5fbc24dd-deb9-4b8b-a145-0708e74fc3c7/resource/42fb066a-48a6-4233-be0c-ffdc3131d6a9/download/stations-scheduled-engineering.json",
                "schema:description": "Information about all stations scheduled engineering works (location, start date and time, duration).",
                "schema:encodingFormat": "JSON",
                "schema:name": "stations-scheduled-engineering.json"
            },
            {
                "@id": "http://demo.ckan.org/dataset/5fbc24dd-deb9-4b8b-a145-0708e74fc3c7",
                "@type": "schema:Dataset",
                "dcterms:conformsTo": "http://mlcommons.org/croissant/1.0",
                "schema:creator": {
                    "@id": "34ab2c70-7815-450e-ade4-3cd829297301"
                },
                "schema:dateModified": "2025-01-13T18:19:53.984608",
                "schema:datePublished": "2025-01-13T17:07:40.203736",
                "schema:description": "Information about all stations, including locations and details of facilities where available, as well as scheduled engineering works.",
                "schema:distribution": [
                    {
                        "@id": "http://demo.ckan.org/dataset/5fbc24dd-deb9-4b8b-a145-0708e74fc3c7/resource/8597cd81-bb01-424c-8aa2-b23d457c88a2"
                    },
                    {
                        "@id": "http://demo.ckan.org/dataset/5fbc24dd-deb9-4b8b-a145-0708e74fc3c7/resource/42fb066a-48a6-4233-be0c-ffdc3131d6a9"
                    }
                ],
                "schema:includedInDataCatalog": {
                    "@id": "_:Nce9d53b44f65459688f3175a9a17b2e1"
                },
                "schema:keywords": "transport",
                "schema:license": "http://www.opendefinition.org/licenses/cc-by-sa",
                "schema:name": "Stations",
                "schema:url": "http://demo.ckan.org/dataset/stations"
            },
            {
                "@id": "_:Nce9d53b44f65459688f3175a9a17b2e1",
                "@type": "schema:DataCatalog",
                "schema:description": "",
                "schema:name": "CKAN",
                "schema:url": "http://demo.ckan.org"
            }
        ]
    }
    </script>
```

Additionally, this `croissant` output is available at a dedicated endpoint:

    https://{ckan-instance-host}/dataset/{dataset-id}/croissant.jsonld