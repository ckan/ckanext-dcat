import pytest

import ckan.plugins as p

@pytest.fixture
def clean_db(reset_db, migrate_db_for):
    reset_db()
    if p.get_plugin('harvest'):
        migrate_db_for('harvest')