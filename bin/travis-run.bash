#!/bin/bash
set -e

pytest --ckan-ini=subdir/test.ini --cov=ckanext.dcat ckanext/dcat/tests
