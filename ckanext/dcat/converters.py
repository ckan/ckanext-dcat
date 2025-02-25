import logging

log = logging.getLogger(__name__)


def dcat_to_ckan(dcat_dict):

    package_dict = {}

    package_dict['title'] = dcat_dict.get('title')
    package_dict['notes'] = dcat_dict.get('description')
    package_dict['url'] = dcat_dict.get('landingPage')


    package_dict['tags'] = []
    for keyword in dcat_dict.get('keyword', []):
        package_dict['tags'].append({'name': keyword})

    package_dict['extras'] = []
    for key in ['issued', 'modified']:
        package_dict['extras'].append({'key': 'dcat_{0}'.format(key), 'value': dcat_dict.get(key)})

    package_dict['extras'].append({'key': 'guid', 'value': dcat_dict.get('identifier')})

    dcat_publisher = dcat_dict.get('publisher')
    if isinstance(dcat_publisher, str):
        package_dict['extras'].append({'key': 'dcat_publisher_name', 'value': dcat_publisher})
    elif isinstance(dcat_publisher, dict) and dcat_publisher.get('name'):
        package_dict['extras'].append({'key': 'dcat_publisher_name', 'value': dcat_publisher.get('name')})

        if dcat_publisher.get('email'):
            package_dict['extras'].append({'key': 'dcat_publisher_email', 'value': dcat_publisher.get('email')})

        if dcat_publisher.get('identifier'):
            package_dict['extras'].append({
                'key': 'dcat_publisher_id',
                'value': dcat_publisher.get('identifier')  # This could be a URI like https://ror.org/05wg1m734
            })

    dcat_creator = dcat_dict.get('creator')
    if isinstance(dcat_creator, str):
        package_dict['extras'].append({'key': 'dcat_creator_name', 'value': dcat_creator})
    elif isinstance(dcat_creator, dict) and dcat_creator.get('name'):
        if dcat_creator.get('name'):
            package_dict['extras'].append({'key': 'dcat_creator_name', 'value': dcat_creator.get('name')})

        if dcat_creator.get('email'):
            package_dict['extras'].append({'key': 'dcat_creator_email', 'value': dcat_creator.get('email')})

        if dcat_creator.get('identifier'):
            package_dict['extras'].append({
                'key': 'dcat_creator_id',
                'value': dcat_creator.get('identifier')
            })

    package_dict['extras'].append({
        'key': 'language',
        'value': ','.join(dcat_dict.get('language', []))
    })

    package_dict['resources'] = []
    for distribution in dcat_dict.get('distribution', []):
        resource = {
            'name': distribution.get('title'),
            'description': distribution.get('description'),
            'url': distribution.get('downloadURL') or distribution.get('accessURL'),
            'format': distribution.get('format'),
        }

        if distribution.get('byteSize'):
            try:
                resource['size'] = int(distribution.get('byteSize'))
            except ValueError:
                pass
        package_dict['resources'].append(resource)

    return package_dict


def ckan_to_dcat(package_dict):
    dcat_dict = {}

    dcat_dict['title'] = package_dict.get('title')
    dcat_dict['description'] = package_dict.get('notes')
    dcat_dict['landingPage'] = package_dict.get('url')

    # Keywords
    dcat_dict['keyword'] = []
    for tag in package_dict.get('tags', []):
        dcat_dict['keyword'].append(tag['name'])

    # Publisher
    dcat_dict['publisher'] = {}
    dcat_dict['creator'] = {}

    for extra in package_dict.get('extras', []):
        if extra['key'] in ['dcat_issued', 'dcat_modified']:
            dcat_dict[extra['key'].replace('dcat_', '')] = extra['value']

        elif extra['key'] == 'language':
            dcat_dict['language'] = extra['value'].split(',')

        # Publisher fields
        elif extra['key'] == 'dcat_publisher_name':
            dcat_dict['publisher']['name'] = extra['value']

        elif extra['key'] == 'dcat_publisher_email':
            dcat_dict['publisher']['email'] = extra['value']

        elif extra['key'] == 'dcat_publisher_id':
            dcat_dict['publisher']['identifier'] = extra['value']

        # Creator fields
        elif extra['key'] == 'dcat_creator_name':
            dcat_dict['creator']['name'] = extra['value']

        elif extra['key'] == 'dcat_creator_email':
            dcat_dict['creator']['email'] = extra['value']

        elif extra['key'] == 'dcat_creator_id':
            dcat_dict['creator']['identifier'] = extra['value']

        # Identifier
        elif extra['key'] == 'guid':
            dcat_dict['identifier'] = extra['value']

    # Fallback for publisher (if no name in extras, use maintainer)
    if not dcat_dict['publisher'].get('name') and package_dict.get('maintainer'):
        dcat_dict['publisher']['name'] = package_dict.get('maintainer')
        if package_dict.get('maintainer_email'):
            dcat_dict['publisher']['email'] = package_dict.get('maintainer_email')

    # Fallback for creator (if no name in extras, optionally use author)
    if not dcat_dict['creator'].get('name') and package_dict.get('author'):
        dcat_dict['creator']['name'] = package_dict.get('author')
        if package_dict.get('author_email'):
            dcat_dict['creator']['email'] = package_dict.get('author_email')

    dcat_dict['distribution'] = []
    for resource in package_dict.get('resources', []):
        distribution = {
            'title': resource.get('name'),
            'description': resource.get('description'),
            'format': resource.get('format'),
            'byteSize': resource.get('size'),
            # TODO: downloadURL or accessURL depending on resource type?
            'accessURL': resource.get('url'),
        }
        dcat_dict['distribution'].append(distribution)

    return dcat_dict
