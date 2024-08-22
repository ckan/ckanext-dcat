from ckanext.dcat.profiles import DCAT, XSD
from ckanext.dcat.processors import RDFSerializer
from ckanext.dcat.tests.utils import BaseSerializeTest

DCAT_AP_PROFILES = ["euro_dcat_ap_3"]


class TestEuroDCATAP2ProfileSerializeDataset(BaseSerializeTest):

    def test_byte_size_non_negative_integer(self):

        dataset = {
            "id": "4b6fe9ca-dc77-4cec-92a4-55c6624a5bd6",
            "name": "test-dataset",
            "title": "Test DCAT 2 dataset",
            "notes": "Lorem ipsum",
            "resources": [
                {
                    "id": "7fffe9b2-7a24-4d43-91f7-8bd58bad9615",
                    "url": "http://example.org/data.csv",
                    "size": 1234,
                }
            ],
        }

        s = RDFSerializer(profiles=DCAT_AP_PROFILES)
        g = s.g

        dataset_ref = s.graph_from_dataset(dataset)

        triple = [t for t in g.triples((None, DCAT.byteSize, None))][0]

        assert triple[2].datatype == XSD.nonNegativeInteger
        assert int(triple[2]) == 1234
