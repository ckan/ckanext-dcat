from pylons import config

from ckan import plugins as p

from ckanext.dcat.logic import dcat_datasets_list


class DCATJSONInterface(p.SingletonPlugin):

    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IActions)

    # IRoutes
    def after_map(self, map):

        controller = 'ckanext.dcat.plugins:DCATController'
        route = config.get('ckanext.dcat.json_endpoint', '/dcat.json')
        map.connect(route, controller=controller, action='dcat_json')

        return map

    # IActions
    def get_actions(self):
        return {
            'dcat_datasets_list': dcat_datasets_list,
        }
