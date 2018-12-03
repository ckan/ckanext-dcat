# -*- coding: utf-8 -*-
import logging
from sqlalchemy import or_

from ckan import model

# from ckan.model import meta

log = logging.getLogger(__name__)


class DCATPackageExtra(model.PackageExtra):
    def __init__(self, **kw):
        super(DCATPackageExtra, self).__init__(self, **kw)

    @classmethod
    def get_extra_keys(cls, package_id):

        query = model.Session.query(cls) \
            .filter(cls.package_id == package_id) \
            .filter(or_(
            cls.key == 'language',
            cls.key == 'purpose_of_collecting_information',
            cls.key == 'update_frequency',
            cls.key == 'tag_string',
        ))

        result = {}
        for item in query.all():
            result[item.key] = item.value

        return result

model.meta.mapper(DCATPackageExtra, model.package_extra.package_extra_table)

