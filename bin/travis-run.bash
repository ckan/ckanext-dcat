#!/bin/bash
set -e

if [ $CKANVERSION == 'master' ]
then
    export CKAN_MINOR_VERSION=100
else
    export CKAN_MINOR_VERSION=${CKANVERSION##*.}
fi


pytest --ckan-ini=subdir/test.ini --cov=ckanext.dcat ckanext/dcat/tests
