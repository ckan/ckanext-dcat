import sys
import argparse
import xml
import json
from pkg_resources import iter_entry_points

from pylons import config

import rdflib
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


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Parse DCAT RDF graphs to CKAN dataset JSON objects')
    parser.add_argument('file', nargs='?', type=argparse.FileType('r'),
                        default=sys.stdin)
    parser.add_argument('-f', '--format',
                        help='''Serialization format (as understood by rdflib)
                                eg: xml, n3 ...'). Defaults to \'xml\'.''')
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
    parser.parse(contents, _format=args.format)

    ckan_datasets = [d for d in parser.datasets()]

    indent = 4 if args.pretty else None
    print json.dumps(ckan_datasets, indent=indent)
