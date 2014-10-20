import os
import uuid
import logging

import requests

from ckan import plugins as p
from ckan import logic
from ckan import model


from ckanext.harvest.harvesters import HarvesterBase
from ckanext.harvest.model import HarvestObject, HarvestObjectExtra


log = logging.getLogger(__name__)


class DCATHarvester(HarvesterBase):

    MAX_FILE_SIZE = 1024 * 1024 * 50  # 50 Mb
    CHUNK_SIZE = 1024

    force_import = False

    _user_name = None

    def _get_content(self, url, harvest_job, page=1):
        if not url.lower().startswith('http'):
            # Check local file
            if os.path.exists(url):
                with open(url, 'r') as f:
                    content = f.read()
                return content
            else:
                self._save_gather_error('Could not get content for this url', harvest_job)
                return None

        try:
            if page > 1:
                url = url + '&' if '?' in url else url + '?'
                url = url + 'page={0}'.format(page)


            log.debug('Getting file %s', url)

            # first we try a HEAD request which may not be supported
            did_get = False
            r = requests.head(url)
            if r.status_code == 405 or r.status_code == 400:
                r = requests.get(url, stream=True)
                did_get = True
            r.raise_for_status()

            cl = r.headers.get('content-length')
            if cl and int(cl) > self.MAX_FILE_SIZE:
                msg = '''Remote file is too big. Allowed
                    file size: {allowed}, Content-Length: {actual}.'''.format(
                    allowed=self.MAX_FILE_SIZE, actual=cl)
                self._save_gather_error(msg, harvest_job)
                return None

            if not did_get:
                r = requests.get(url, stream=True)

            length = 0
            content = ''
            for chunk in r.iter_content(chunk_size=self.CHUNK_SIZE):
                content = content + chunk
                length += len(chunk)

                if length >= self.MAX_FILE_SIZE:
                    self._save_gather_error('Remote file is too big.', harvest_job)
                    return None

            return content

        except requests.exceptions.HTTPError, error:
            if page > 1 and error.response.status_code == 404:
                # We want to catch these ones later on
                raise

            msg = 'Could not get content. Server responded with %s %s' % (
                error.response.status_code, error.response.reason)
            self._save_gather_error(msg, harvest_job)
            return None
        except requests.exceptions.ConnectionError, error:
            msg = '''Could not get content because a
                                connection error occurred. %s''' % error
            self._save_gather_error(msg, harvest_job)
            return None
        except requests.exceptions.Timeout, error:
            msg = 'Could not get content because the connection timed out.'
            self._save_gather_error(msg, harvest_job)
            return None

    def _get_user_name(self):
        if self._user_name:
            return self._user_name

        user = p.toolkit.get_action('get_site_user')(
            {'ignore_auth': True, 'defer_commit': True},
            {})
        self._user_name = user['name']

        return self._user_name

    def _get_object_extra(self, harvest_object, key):
        '''
        Helper function for retrieving the value from a harvest object extra,
        given the key
        '''
        for extra in harvest_object.extras:
            if extra.key == key:
                return extra.value
        return None

    def _get_package_name(self, harvest_object, title):

        package = harvest_object.package
        if package is None or package.title != title:
            name = self._gen_new_name(title)
            if not name:
                raise Exception('Could not generate a unique name from the title or the GUID. Please choose a more unique title.')
        else:
            name = package.name

        return name

    def get_original_url(self, harvest_object_id):
        obj = model.Session.query(HarvestObject).\
                                    filter(HarvestObject.id==harvest_object_id).\
                                    first()
        if obj:
            return obj.source.url
        return None

    ## Start hooks

    def modify_package_dict(self, package_dict, dcat_dict, harvest_object):
        '''
            Allows custom harvesters to modify the package dict before
            creating or updating the actual package.
        '''
        return package_dict

    ## End hooks

    def gather_stage(self,harvest_job):
        log.debug('In DCATHarvester gather_stage')


        ids = []

        # Get the previous guids for this source
        query = model.Session.query(HarvestObject.guid, HarvestObject.package_id).\
                                    filter(HarvestObject.current==True).\
                                    filter(HarvestObject.harvest_source_id==harvest_job.source.id)
        guid_to_package_id = {}

        for guid, package_id in query:
            guid_to_package_id[guid] = package_id

        guids_in_db = guid_to_package_id.keys()
        guids_in_source = []


        # Get file contents
        url = harvest_job.source.url

        previous_guids = []
        page = 1
        while True:

            try:
                content = self._get_content(url, harvest_job, page)
            except requests.exceptions.HTTPError, error:
                if error.response.status_code == 404:
                    if page > 1:
                        # Server returned a 404 after the first page, no more
                        # records
                        log.debug('404 after first page, no more pages')
                        break
                    else:
                        # Proper 404
                        msg = 'Could not get content. Server responded with 404 Not Found'
                        self._save_gather_error(msg, harvest_job)
                        return None
                else:
                    # This should never happen. Raising just in case.
                    raise

            if not content:
                return None


            try:

                batch_guids = []
                for guid, as_string in self._get_guids_and_datasets(content):

                    log.debug('Got identifier: {0}'.format(guid.encode('utf8')))
                    batch_guids.append(guid)

                    if guid not in previous_guids:

                        if guid in guids_in_db:
                            # Dataset needs to be udpated
                            obj = HarvestObject(guid=guid, job=harvest_job,
                                            package_id=guid_to_package_id[guid],
                                            content=as_string,
                                            extras=[HarvestObjectExtra(key='status', value='change')])
                        else:
                            # Dataset needs to be created
                            obj = HarvestObject(guid=guid, job=harvest_job,
                                            content=as_string,
                                            extras=[HarvestObjectExtra(key='status', value='new')])
                        obj.save()
                        ids.append(obj.id)

                if len(batch_guids) > 0:
                    guids_in_source.extend(set(batch_guids) - set(previous_guids))
                else:
                    log.debug('Empty document, no more records')
                    # Empty document, no more ids
                    break

            except ValueError, e:
                msg = 'Error parsing file: {0}'.format(str(e))
                self._save_gather_error(msg, harvest_job)
                return None

            if sorted(previous_guids) == sorted(batch_guids):
                # Server does not support pagination or no more pages
                log.debug('Same content, no more pages')
                break


            page = page + 1

            previous_guids = batch_guids

        # Check datasets that need to be deleted
        guids_to_delete = set(guids_in_db) - set(guids_in_source)
        for guid in guids_to_delete:
            obj = HarvestObject(guid=guid, job=harvest_job,
                                package_id=guid_to_package_id[guid],
                                extras=[HarvestObjectExtra(key='status', value='delete')])
            ids.append(obj.id)
            model.Session.query(HarvestObject).\
                  filter_by(guid=guid).\
                  update({'current': False}, False)
            obj.save()


        return ids

    def fetch_stage(self,harvest_object):
        return True

    def import_stage(self,harvest_object):
        log.debug('In DCATHarvester import_stage')
        if not harvest_object:
            log.error('No harvest object received')
            return False

        if self.force_import:
            status = 'change'
        else:
            status = self._get_object_extra(harvest_object, 'status')

        if status == 'delete':
            # Delete package
            context = {'model': model, 'session': model.Session, 'user': self._get_user_name()}

            p.toolkit.get_action('package_delete')(context, {'id': harvest_object.package_id})
            log.info('Deleted package {0} with guid {1}'.format(harvest_object.package_id, harvest_object.guid))

            return True


        if harvest_object.content is None:
            self._save_object_error('Empty content for object %s' % harvest_object.id,harvest_object,'Import')
            return False

        # Get the last harvested object (if any)
        previous_object = model.Session.query(HarvestObject) \
                          .filter(HarvestObject.guid==harvest_object.guid) \
                          .filter(HarvestObject.current==True) \
                          .first()

        # Flag previous object as not current anymore
        if previous_object and not self.force_import:
            previous_object.current = False
            previous_object.add()


        package_dict, dcat_dict = self._get_package_dict(harvest_object)
        if not package_dict:
            return False

        if not package_dict.get('name'):
            package_dict['name'] = self._get_package_name(harvest_object, package_dict['title'])

        # Allow custom harvesters to modify the package dict before creating
        # or updating the package
        package_dict = self.modify_package_dict(package_dict,
                                                dcat_dict,
                                                harvest_object)

        # Flag this object as the current one
        harvest_object.current = True
        harvest_object.add()

        context = {
            'user': self._get_user_name(),
            'return_id_only': True,
            'ignore_auth': True,
        }

        if status == 'new':


            package_schema = logic.schema.default_create_package_schema()
            context['schema'] = package_schema

            # We need to explicitly provide a package ID
            package_dict['id'] = unicode(uuid.uuid4())
            package_schema['id'] = [unicode]

            # Save reference to the package on the object
            harvest_object.package_id = package_dict['id']
            harvest_object.add()

            # Defer constraints and flush so the dataset can be indexed with
            # the harvest object id (on the after_show hook from the harvester
            # plugin)
            model.Session.execute('SET CONSTRAINTS harvest_object_package_id_fkey DEFERRED')
            model.Session.flush()

            package_id = p.toolkit.get_action('package_create')(context, package_dict)
            log.info('Created dataset with id %s', package_id)
        elif status == 'change':

            package_dict['id'] = harvest_object.package_id
            package_id = p.toolkit.get_action('package_update')(context, package_dict)
            log.info('Updated dataset with id %s', package_id)

        model.Session.commit()

        return True
