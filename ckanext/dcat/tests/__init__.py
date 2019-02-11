from ckan.tests.helpers import FunctionalTestBase

from ckanext.harvest.model import setup as harvest_setup


class DCATFunctionalTestBase(FunctionalTestBase):

    def setup(self):

        super(DCATFunctionalTestBase, self).setup()

        harvest_setup()
