from rdflib import Literal

from ckanext.dcat.profiles import EuropeanDCATAP2Profile, DCAT, XSD


class EuropeanDCATAP3Profile(EuropeanDCATAP2Profile):
    """
    An RDF profile based on the DCAT-AP 3 for data portals in Europe
    """

    def graph_from_dataset(self, dataset_dict, dataset_ref):

        # Call the DCAT AP 2 method
        super().graph_from_dataset(dataset_dict, dataset_ref)

        # byteSize decimal -> nonNegativeInteger
        for subject, predicate, object in self.g.triples((None, DCAT.byteSize, None)):
            if object and object.datatype == XSD.decimal:
                self.g.remove((subject, predicate, object))

                self.g.add(
                    (
                        subject,
                        predicate,
                        Literal(int(object), datatype=XSD.nonNegativeInteger),
                    )
                )
