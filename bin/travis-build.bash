#!/bin/bash
set -e

echo "This is travis-build.bash..."
echo "Targetting CKAN $CKANVERSION on Python $TRAVIS_PYTHON_VERSION"
if [ $CKANVERSION == 'master' ]
then
    export CKAN_MINOR_VERSION=100
else
    export CKAN_MINOR_VERSION=${CKANVERSION##*.}
fi

export PYTHON_MAJOR_VERSION=${TRAVIS_PYTHON_VERSION%.*}

echo "Installing CKAN and its Python dependencies..."
git clone https://github.com/ckan/ckan
cd ckan
if [ $CKANVERSION == 'master' ]
then
    echo "CKAN version: master"
else
    CKAN_TAG=$(git tag | grep ^ckan-$CKANVERSION | sort --version-sort | tail -n 1)
    git checkout $CKAN_TAG
    echo "CKAN version: ${CKAN_TAG#ckan-}"
fi

echo "Installing the recommended setuptools requirement"
if [ -f requirement-setuptools.txt ]
then
    pip install -r requirement-setuptools.txt
fi

python setup.py develop

if (( $CKAN_MINOR_VERSION >= 9 )) && (( $PYTHON_MAJOR_VERSION == 2 ))
then
    pip install -r requirements-py2.txt
else
    pip install -r requirements.txt
fi

pip install -r dev-requirements.txt
cd -

echo "Setting up Solr..."
docker run --name ckan-solr -p 8983:8983 -d openknowledge/ckan-solr-dev:$CKANVERSION

echo "Setting up Postgres..."
export PG_VERSION="$(pg_lsclusters | grep online | awk '{print $1}')"
export PG_PORT="$(pg_lsclusters | grep online | awk '{print $3}')"
echo "Using Postgres $PGVERSION on port $PG_PORT"
if [ $PG_PORT != "5432" ]
then
	echo "Using non-standard Postgres port, updating configuration..."
	sed -i -e "s/postgresql:\/\/ckan_default:pass@localhost\/ckan_test/postgresql:\/\/ckan_default:pass@localhost:$PG_PORT\/ckan_test/" ckan/test-core.ini
	sed -i -e "s/postgresql:\/\/ckan_default:pass@localhost\/datastore_test/postgresql:\/\/ckan_default:pass@localhost:$PG_PORT\/datastore_test/" ckan/test-core.ini
	sed -i -e "s/postgresql:\/\/datastore_default:pass@localhost\/datastore_test/postgresql:\/\/datastore_default:pass@localhost:$PG_PORT\/datastore_test/" ckan/test-core.ini
fi


echo "Creating the PostgreSQL user and database..."
sudo -u postgres psql -p $PG_PORT -c "CREATE USER ckan_default WITH PASSWORD 'pass';"
sudo -u postgres psql -p $PG_PORT -c "CREATE USER datastore_default WITH PASSWORD 'pass';"
sudo -u postgres psql -p $PG_PORT -c 'CREATE DATABASE ckan_test WITH OWNER ckan_default;'
sudo -u postgres psql -p $PG_PORT -c 'CREATE DATABASE datastore_test WITH OWNER ckan_default;'

echo "Initialising the database..."
cd ckan
if (( $CKAN_MINOR_VERSION >= 9 ))
then
    ckan -c test-core.ini db init
else
    paster db init -c test-core.ini
fi
cd -

echo "Installing ckanext-harvest and its requirements..."
git clone https://github.com/ckan/ckanext-harvest
cd ckanext-harvest
python setup.py develop
pip install -r pip-requirements.txt

if (( $CKAN_MINOR_VERSION >= 9 ))
then
    ckan -c test.ini harvester initdb
else
    paster harvester initdb -c test.ini
fi
cd -

echo "Installing ckanext-dcat and its requirements..."
pip install -r requirements.txt
pip install -r dev-requirements.txt
python setup.py develop


echo "Moving test.ini into a subdir..."
mkdir subdir
mv test.ini subdir

echo "travis-build.bash is done."
