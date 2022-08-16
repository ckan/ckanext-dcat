from SPARQLWrapper import SPARQLWrapper, POST, GET, JSON
from SPARQLWrapper import SPARQLExceptions  # noqa: imported for convenience of SPARQLClient users
from ckanext.dcat.processors import RDFSerializer
import logging

log = logging.getLogger(__name__)


class SPARQLClient:
    def __init__(self, query_endpoint, update_endpoint=None, username=None, password=None):
        self.sparql = SPARQLWrapper(query_endpoint, update_endpoint)

        if username:
            self.sparql.setCredentials(username, password)

    def _query(self, q, return_format):
        self.sparql.setQuery(q)
        self.sparql.setReturnFormat(return_format)
        return self.sparql.query()

    def query(self, q, return_format=JSON):
        self.sparql.setMethod(GET)
        result = self._query(q, return_format)
        return result.response.read()

    def update(self, q, return_format=JSON):
        self.sparql.setMethod(POST)
        return self._query(q, return_format).response.read()

    def update_dataset(self, dataset_dict, profiles):
        serializer = RDFSerializer(profiles=profiles)
        dataset_ref = serializer.graph_from_dataset(dataset_dict)
        g = serializer.g

        prefix_fmt = 'PREFIX {}: {}'.format
        triple_fmt = '{} {} {}'.format

        prefixes = '\n'.join([prefix_fmt(prefix, ns.n3()) for prefix, ns in g.namespaces()])
        triples = ' .\n'.join([triple_fmt(s.n3(), p.n3(), o.n3())
                               for (s, p, o) in g.triples((dataset_ref, None, None))])
        dataset_id = dataset_dict['id']

        delete_query = ('{} DELETE WHERE {{ ?s ?p ?o ; dct:identifier "{}"}}'
                        .format(prefixes, dataset_id))
        self.update(delete_query)

        insert_query = '{} INSERT DATA {{ {} . }}'.format(prefixes, triples)
        self.update(insert_query)
