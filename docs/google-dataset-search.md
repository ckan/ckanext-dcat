## Structured data and Google Dataset Search indexing

The `structured_data` plugin will add the necessary markup to dataset pages in order to get your datasets indexed by [Google Dataset Search](https://toolbox.google.com/datasetsearch). This markup is a [structured data](https://developers.google.com/search/docs/guides/intro-structured-data) JSON-LD snippet that uses the [schema.org](https://schema.org) vocabulary to describe the dataset.

    ckan.plugins = structured_data

You don't need to load the `dcat` plugin to use the `structured_data` plugin, but you can load them both to enable both functionalities.

The plugin uses the `schemaorg` profile by default (see [Profiles](profiles.md#profiles)) to serialize the dataset to JSON-LD, which is then added to the dataset detail page.

To use a custom profile, you have to override the Jinja template block called `structured_data` in [`templates/package/read_base.html`](https://github.com/ckan/ckanext-dcat/blob/master/ckanext/dcat/templates/structured_data/package/read_base.html) and call the template helper function with different parameters:

    {% block structured_data %}
      <script type="application/ld+json">
      {{ h.structured_data(pkg, ['my_custom_schema']) | safe }}
      </script>
    {% endblock %}


Below is an example of the structured data in JSON-LD embedded in the dataset page source:

```html
    <script type="application/ld+json">
    {
        "@context": {
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "schema": "http://schema.org/",
            "xsd": "http://www.w3.org/2001/XMLSchema#"
        },
        "@graph": [
            {
                "@id": "http://demo.ckan.org/organization/c64835bf-b3b7-496d-a7cf-ed645dbf4b08",
                "@type": "schema:Organization",
                "schema:contactPoint": {
                    "@id": "_:Nb9677036512840e1a00c9fec2818abe4"
                },
                "schema:name": "Public Transport Organization"
            },
            {
                "@id": "http://demo.ckan.org/dataset/69a5bc23-3abd-4af7-8d3d-8f0d08698307/resource/5f1cafa2-3c92-4e89-85d1-60f014c23e0f",
                "@type": "schema:DataDownload",
                "schema:dateModified": "2018-01-18T00:00:00",
                "schema:datePublished": "2018-01-02T00:00:00",
                "schema:description": "API for all the public transport stations",
                "schema:encodingFormat": "JSON",
                "schema:inLanguage": [
                    "de",
                    "it",
                    "fr",
                    "en"
                ],
                "schema:license": "https://creativecommons.org/licenses/by/4.0/",
                "schema:name": "Stations API",
                "schema:url": "http://stations.example.com/api"
            },
            {
                "@id": "http://demo.ckan.org/dataset/69a5bc23-3abd-4af7-8d3d-8f0d08698307",
                "@type": "schema:Dataset",
                "schema:dateModified": "2018-01-18T09:41:21.076522",
                "schema:datePublished": "2017-01-01T00:00:00",
                "schema:distribution": [
                    {
                        "@id": "http://demo.ckan.org/dataset/69a5bc23-3abd-4af7-8d3d-8f0d08698307/resource/5f1cafa2-3c92-4e89-85d1-60f014c23e0f"
                    },
                    {
                        "@id": "http://demo.ckan.org/dataset/69a5bc23-3abd-4af7-8d3d-8f0d08698307/resource/bf3a0b61-415b-47b8-9cd0-86a14f8dc165"
                    }
                ],
                "schema:identifier": "69a5bc23-3abd-4af7-8d3d-8f0d08698307",
                "schema:inLanguage": [
                    "en",
                    "de",
                    "fr",
                    "it"
                ],
                "schema:name": "Station list",
                "schema:publisher": {
                    "@id": "http://demo.ckan.org/organization/c64835bf-b3b7-496d-a7cf-ed645dbf4b08"
                }
            },
            {
                "@id": "_:Nb9677036512840e1a00c9fec2818abe4",
                "@type": "schema:ContactPoint",
                "schema:contactType": "customer service",
                "schema:email": "contact@example.com",
                "schema:name": "Public Transport Support",
                "schema:url": "https://public-transport.example.com"
            }
        ]
    }
    </script>
  </body>
</html>
```
