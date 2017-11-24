
import ckan.model as model
import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.logic as logic


import logging
log = logging.getLogger(__name__)


def dcat_get_org (id):
    org_dict = logic.get_action('organization_show')({}, {'id': id})
    print org_dict
    return org_dict
