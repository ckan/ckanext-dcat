import os

from rdflib import URIRef, BNode, Literal


class BaseParseTest(object):

    def _extras(self, dataset):
        extras = {}
        for extra in dataset.get('extras'):
            extras[extra['key']] = extra['value']
        return extras

    def _get_file_contents(self, file_name):
        path = os.path.join(os.path.dirname(__file__),
                            '..', '..', '..', 'examples',
                            file_name)
        with open(path, 'r') as f:
            return f.read()


class BaseSerializeTest(object):

    def _extras(self, dataset):
        extras = {}
        for extra in dataset.get('extras'):
            extras[extra['key']] = extra['value']
        return extras

    def _triples(self, graph, subject, predicate, _object, data_type=None):

        if not (isinstance(_object, URIRef) or isinstance(_object, BNode) or _object is None):
            if data_type:
                _object = Literal(_object, datatype=data_type)
            else:
                _object = Literal(_object)
        triples = [t for t in graph.triples((subject, predicate, _object))]
        return triples

    def _triple(self, graph, subject, predicate, _object, data_type=None):
        triples = self._triples(graph, subject, predicate, _object, data_type)
        return triples[0] if triples else None

    def _get_typed_list(self, list, datatype):
        """ returns the list with the given rdf type """
        return [datatype(x) for x in list]

    def _get_dict_from_list(self, dict_list, key, value):
        """ returns the dict with the given key-value """
        for dict in dict_list:
            if(dict.get(key) == value):
                return dict
        return None
