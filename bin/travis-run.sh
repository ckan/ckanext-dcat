#!/bin/sh -e

if [ $CKAN_MINOR_VERSION >= 9 ]
then
    pytest --ckan-ini=subdir/test.ini --cov=ckanext.dcat ckanext/dcat/tests
else
    nosetests --ckan --nologcapture --with-pylons=subdir/test-nose.ini --with-coverage --cover-package=ckanext.dcat --cover-inclusive --cover-erase --cover-tests ckanext/dcat/tests/nose
fi
