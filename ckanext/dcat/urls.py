import six
from ckan.plugins import toolkit as tk
from ckantoolkit import url_for as core_url_for


def url_for(*args, **kwargs):

    if not tk.check_ckan_version(min_version='2.9'):

        external = kwargs.pop('_external', False)
        if external is not None and 'qualified' not in kwargs:
            kwargs['qualified'] = external

        if len(args) and args[0] == 'dcat.read_dataset':
            return core_url_for('dcat_dataset', **kwargs)
        elif len(args) and args[0] == 'dcat.read_catalog':
            return core_url_for('dcat_catalog', **kwargs)
        elif len(args) and args[0] == 'dataset.new':
            return core_url_for(controller='package', action='new', **kwargs)
        elif len(args) and args[0] == 'dataset.read':
            return core_url_for(controller='package', action='read', **kwargs)

    return core_url_for(*args, **kwargs)
