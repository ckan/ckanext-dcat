import os
import json
import difflib

from ckanext.dcat import converters


class TestConverters(object):

    def _get_file_as_dict(self, file_name):
        path = os.path.join(os.path.dirname(__file__),
                            '..', '..', '..', 'examples',
                            file_name)
        with open(path, 'r') as f:
            return json.load(f)

    def _poor_mans_dict_diff(self, d1, d2):
        def _get_lines(d):
            return sorted([l.strip().rstrip(',')
                           for l in json.dumps(d, indent=0).split('\n')
                           if not l.startswith(('{', '}', '[', ']'))])

        d1_lines = _get_lines(d1)
        d2_lines = _get_lines(d2)

        return '\n' + '\n'.join([l for l in difflib.ndiff(d1_lines, d2_lines)
                                 if l.startswith(('-', '+'))])

    def test_ckan_to_dcat(self):
        ckan_dict = self._get_file_as_dict('full_ckan_dataset.json')
        expected_dcat_dict = self._get_file_as_dict('dataset.json')

        dcat_dict = converters.ckan_to_dcat(ckan_dict)

        assert dcat_dict == expected_dcat_dict, self._poor_mans_dict_diff(
            expected_dcat_dict, dcat_dict)

    def test_dcat_to_ckan(self):
        dcat_dict = self._get_file_as_dict('dataset.json')
        expected_ckan_dict = self._get_file_as_dict('ckan_dataset.json')

        # Pop CKAN specific fields
        expected_ckan_dict.pop('id', None)
        expected_ckan_dict['resources'][0].pop('id', None)
        expected_ckan_dict['resources'][0].pop('package_id', None)

        ckan_dict = converters.dcat_to_ckan(dcat_dict)

        assert ckan_dict == expected_ckan_dict, self._poor_mans_dict_diff(
            expected_ckan_dict, ckan_dict)
