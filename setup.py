from setuptools import setup, find_packages

version = '0.0.4'

setup(
    name='ckanext-dcat',
    version=version,
    description="Plugins for exposing and consuming DCAT metadata on CKAN",
    long_description='''\
    ''',
    classifiers=[],
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
    entry_points='''

    [ckan.plugins]
    dcat_xml_harvester=ckanext.dcat.harvesters:DCATXMLHarvester
    dcat_json_harvester=ckanext.dcat.harvesters:DCATJSONHarvester

    dcat_rdf_harvester=ckanext.dcat.harvesters:DCATRDFHarvester

    dcat_json_interface=ckanext.dcat.plugins:DCATJSONInterface

    dcat=ckanext.dcat.plugins:DCATPlugin

    # Test plugins
    test_rdf_harvester=ckanext.dcat.tests.test_harvester:TestRDFHarvester

    [ckan.rdf.profiles]
    euro_dcat_ap=ckanext.dcat.profiles:EuropeanDCATAPProfile

    [paste.paster_command]
    generate_static = ckanext.dcat.commands:GenerateStaticDCATCommand

    [babel.extractors]
    ckan = ckan.lib.extract:extract_ckan
    ''',
    message_extractors={
        'ckanext': [
            ('**.py', 'python', None),
            ('**.js', 'javascript', None),
            ('**/templates/**.html', 'ckan', None),
        ],
    },
)
