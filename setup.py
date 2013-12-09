from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
	name='ckanext-dcat',
	version=version,
	description="Plugins for exposing and consuming DCAT metadata on CKAN",
	long_description="""\
	""",
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='',
	author='Open Knowledge Foundation',
	author_email='info@ckan.org',
	url='https://github.com/okfn/ckanext-dcat',
	license='AGPL',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	namespace_packages=['ckanext', 'ckanext.dcat'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		# -*- Extra requirements: -*-
	],
	entry_points=\
	"""
    [ckan.plugins]
    dcat_xml_harvester=ckanext.dcat.harvesters:DCATXMLHarvester
    dcat_json_harvester=ckanext.dcat.harvesters:DCATJSONHarvester
    dcat_json_interface=ckanext.dcat.plugins:DCATJSONInterface

    [paste.paster_command]
    generate_static = ckanext.dcat.commands:GenerateStaticDCATCommand

	""",
)
