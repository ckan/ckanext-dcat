import os

from rdflib import URIRef, BNode, Literal


def get_file_contents(file_name):
    path = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "examples", file_name
    )
    with open(path, "r") as f:
        return f.read()


class BaseParseTest(object):
    def _extras(self, dataset):
        extras = {}
        for extra in dataset.get("extras"):
            extras[extra["key"]] = extra["value"]
        return extras

    def _get_file_contents(self, file_name):
        return get_file_contents(file_name)


class BaseSerializeTest(object):
    def _extras(self, dataset):
        extras = {}
        for extra in dataset.get("extras"):
            extras[extra["key"]] = extra["value"]
        return extras

    def _triples(self, graph, subject, predicate, _object, data_type=None, lang=None):

        if not (
            isinstance(_object, URIRef) or isinstance(_object, BNode) or _object is None
        ):
            _object = Literal(_object, datatype=data_type, lang=lang)
        triples = [t for t in graph.triples((subject, predicate, _object))]
        return triples

    def _triple(self, graph, subject, predicate, _object, data_type=None, lang=None):
        triples = self._triples(graph, subject, predicate, _object, data_type, lang)
        return triples[0] if triples else None

    def _triples_list_values(self, graph, subject, predicate):
        return [str(t[2]) for t in graph.triples((subject, predicate, None))]

    def _triples_list_python_values(self, graph, subject, predicate):
        return [
            t[2].value if isinstance(t[2], Literal) else str(t[2])
            for t in graph.triples((subject, predicate, None))
        ]

    def _get_typed_list(self, list, datatype):
        """ returns the list with the given rdf type """
        return [datatype(x) for x in list]

    def _get_dict_from_list(self, dict_list, key, value):
        """ returns the dict with the given key-value """
        for dict in dict_list:
            if dict.get(key) == value:
                return dict
        return None

    def _get_file_contents(self, file_name):
        return get_file_contents(file_name)
