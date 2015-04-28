import sys
import argparse
import xml
import json
from pkg_resources import iter_entry_points

from pylons import config

import rdflib
from rdflib import URIRef, BNode
from rdflib.namespace import Namespace, RDF

import ckan.plugins as p

DCAT = Namespace("http://www.w3.org/ns/dcat#")


RDF_PROFILES_ENTRY_POINT_GROUP = 'ckan.rdf.profiles'
RDF_PROFILES_CONFIG_OPTION = 'ckanext.dcat.rdf.profiles'
COMPAT_MODE_CONFIG_OPTION = 'ckanext.dcat.compatibility_mode'

DEFAULT_RDF_PROFILES = ['euro_dcat_ap']


class RDFParserException(Exception):
    pass


class RDFProfileException(Exception):
    pass


class RDFParser(object):
    '''
    An RDF to CKAN parser based on rdflib

    Supports different profiles which are the ones that will generate
    CKAN dicts from the RDF graph.
    '''

    def __init__(self, profiles=None, compatibility_mode=False):
        '''
        Creates a parser instance

        You can optionally pass a list of profiles to be used.

        In compatibility mode, some fields are modified to maintain
        compatibility with previous versions of the ckanext-dcat parsers
        (eg adding the `dcat_` prefix or storing comma separated lists instead
        of JSON dumps).

        '''
        if not profiles:
            profiles = config.get(RDF_PROFILES_CONFIG_OPTION, None)
            if profiles:
                profiles = profiles.split(' ')
            else:
                profiles = DEFAULT_RDF_PROFILES
        self._profiles = self._load_profiles(profiles)
        if not self._profiles:
            raise RDFProfileException(
                'No suitable RDF profiles could be loaded')

        if not compatibility_mode:
            compatibility_mode = p.toolkit.asbool(
                config.get(COMPAT_MODE_CONFIG_OPTION, False))
        self.compatibility_mode = compatibility_mode

        self.g = rdflib.Graph()

    def _load_profiles(self, profile_names):
        '''
        Loads the specified RDF parser profiles

        These are registered on ``entry_points`` in setup.py, under the
        ``[ckan.rdf.profiles]`` group.
        '''
        profiles = []
        loaded_profiles_names = []

        for profile in iter_entry_points(group=RDF_PROFILES_ENTRY_POINT_GROUP):
            if profile.name in profile_names:
                profile_class = profile.load()
                # Set a reference to the profile name
                profile_class.name = profile.name
                profiles.append(profile_class)
                loaded_profiles_names.append(profile.name)

        unknown_profiles = set(profile_names) - set(loaded_profiles_names)
        if unknown_profiles:
            raise RDFProfileException(
                'Unknown RDF profiles: {0}'.format(
                    ', '.join(sorted(unknown_profiles))))

        return profiles

    def _datasets(self):
        '''
        Generator that returns all DCAT datasets on the graph

        Yields rdflib.term.URIRef objects that can be used on graph lookups
        and queries
        '''
        for dataset in self.g.subjects(RDF.type, DCAT.Dataset):
            yield dataset

    def parse(self, data, _format=None):
        '''
        Parses and RDF graph serialization and into the class graph

        It calls the rdflib parse function with the provided data and format.

        Data is a string with the serialized RDF graph (eg RDF/XML, N3
        ... ). By default RF/XML is expected. The optional parameter _format
        can be used to tell rdflib otherwise.

        It raises a ``RDFParserException`` if there was some error during
        the parsing.

        Returns nothing.
        '''
        try:
            self.g.parse(data=data, format=_format)
        # Apparently there is no single way of catching exceptions from all
        # rdflib parsers at once, so if you use a new one and the parsing
        # exceptions are not cached, add them here.
        except (SyntaxError, xml.sax.SAXParseException), e:

            raise RDFParserException(e)

    def datasets(self):
        '''
        Generator that returns CKAN datasets parsed from the RDF graph

        Each dataset is passed to all the loaded profiles before being
        yielded, so it can be further modified by each one of them.

        Returns a dataset dict that can be passed to eg `package_create`
        or `package_update`
        '''
        for dataset_ref in self._datasets():
            dataset_dict = {}
            for profile_class in self._profiles:
                profile = profile_class(self.g, self.compatibility_mode)
                profile.parse_dataset(dataset_dict, dataset_ref)

            yield dataset_dict

    def graph_from_dataset(self, dataset_dict):
        '''
        Given a CKAN dataset dict, creates a graph using the loaded profiles

        The class RDFLib graph (accessible via `parser.g`) will be updated by
        the loaded profiles.

        Returns the reference to the dataset, which will be an rdflib URIRef
        or BNode object.
        '''

        uri_value = dataset_dict.get('uri')
        if not uri_value:
            for extra in dataset_dict.get('extras', []):
                if extra['key'] == 'uri':
                    uri_value = extra['value']
                    break

        # TODO: create a CKAN URI if not present
        dataset_ref = URIRef(uri_value) if uri_value else BNode()

        for profile_class in self._profiles:
            profile = profile_class(self.g, self.compatibility_mode)
            profile.graph_from_dataset(dataset_dict, dataset_ref)

        return dataset_ref

    def graph_from_catalog(self, catalog_dict):
        '''
        Creates a graph for the catalog (CKAN site) using the loaded profiles

        The class RDFLib graph (accessible via `parser.g`) will be updated by
        the loaded profiles.

        Returns the reference to the catalog, which will be an rdflib URIRef
        or BNode object.
        '''

        # TODO: create a CKAN URI if not present
        catalog_ref = URIRef('http://my-catalog')

        for profile_class in self._profiles:
            profile = profile_class(self.g, self.compatibility_mode)
            profile.graph_from_catalog(catalog_dict, catalog_ref)

        return catalog_ref

    def serialize_dataset(self, dataset_dict, _format='xml'):
        '''
        Given a CKAN dataset dict, returns an RDF serialization

        The serialization format can be defined using the `_format` parameter.
        It must be one of the ones supported by RDFLib, defaults to `xml`.

        Returns a string with the serialized dataset
        '''

        self.graph_from_dataset(dataset_dict)

        output = self.g.serialize(format=_format)

        return output

    def serialize_catalog(self, catalog_dict, dataset_dicts=[],
                          _format='xml'):
        '''
        Returns an RDF serialization of the whole catalog

        `catalog_dict` can contain literal values for the dcat:Catalog class
        like `title`, `homepage`, etc. If not provided these would get default
        values from the CKAN config (eg from `ckan.site_title`).

        If passed a list of CKAN dataset dicts, these will be also serializsed
        as part of the catalog.
        **Note:** There is no hard limit on the number of datasets at this
        level, this should be handled upstream.

        The serialization format can be defined using the `_format` parameter.
        It must be one of the ones supported by RDFLib, defaults to `xml`.

        Returns a string with the serialized catalog
        '''

        catalog_ref = self.graph_from_catalog(catalog_dict)
        if dataset_dicts:
            for dataset_dict in dataset_dicts:
                dataset_ref = self.graph_from_dataset(dataset_dict)

                self.g.add((catalog_ref, DCAT.dataset, dataset_ref))

        output = self.g.serialize(format=_format)

        return output


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='DCAT RDF - CKAN operations')
    parser.add_argument('mode',
                        default='consume',
                        help='''
Operation mode.
`consume` parses DCAT RDF graphs to CKAN dataset JSON objects.
`produce` serializes CKAN dataset JSON objects into DCAT RDF.
                        ''')
    parser.add_argument('file', nargs='?', type=argparse.FileType('r'),
                        default=sys.stdin,
                        help='Input file. If omitted will read from stdin')
    parser.add_argument('-f', '--format',
                        default='xml',
                        help='''Serialization format (as understood by rdflib)
                                eg: xml, n3 ... Defaults to \'xml\'.''')
    parser.add_argument('-P', '--pretty',
                        action='store_true',
                        help='Make the output more human readable')
    parser.add_argument('-p', '--profile', nargs='*',
                        action='store',
                        help='RDF Profiles to use, defaults to euro_dcat_ap')
    parser.add_argument('-m', '--compat-mode',
                        action='store_true',
                        help='Enable compatibility mode')

    args = parser.parse_args()

    contents = args.file.read()

    parser = RDFParser(profiles=args.profile,
                       compatibility_mode=args.compat_mode)
    if args.mode == 'produce':
        dataset = json.loads(contents)
        out = parser.serialize_dataset(dataset, _format=args.format)
        print out
    else:
        parser.parse(contents, _format=args.format)

        ckan_datasets = [d for d in parser.datasets()]

        indent = 4 if args.pretty else None
        print json.dumps(ckan_datasets, indent=indent)
