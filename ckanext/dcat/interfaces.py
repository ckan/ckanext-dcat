from ckan.plugins.interfaces import Interface


class IDCATRDFHarvester(Interface):

    def before_download(self, url, harvest_job):
        '''
        Called just before the remote RDF file is downloaded

        It returns a tuple with the url (which can be modified) and an
        optional list of error messages.

        If the url value evaluates to False the gather stage will be stop.

        This extension point can be useful to validate the URL using an
        external service.

        :param url: The harvest source URL, ie the remote RDF file location
        :type url: string
        :param harvest_job: A ``HarvestJob`` domain object which contains a
                            reference to the harvest source
                            (``harvest_job.source``).
        :type harvest_job: object


        :returns: A tuple with two items:
                    * The url. If this is False the gather stage will stop.
                    * A list of error messages. These will get stored as gather
                      errors by the harvester
        :rtype: tuple
        '''
        return url, []

    def update_session(self, session):
        '''
        Called before making the HTTP request to the remote site to download
        the RDF file.

        It returns a valid `requests` session object.

        This extension point can be useful to add special parameters to the 
        request (e.g. add client certificates).

        :param session: The requests session object
        :type session: object

        :returns: The updated requests session object
        :rtype: object
        '''
        return session

    def after_download(self, content, harvest_job):
        '''
        Called just after the remote RDF file has been downloaded

        It returns a tuple with the content (which can be modified) and an
        optional list of error messages.

        If the content value evaluates to False the gather stage will stop.

        This extension point can be useful to validate the file contents using
        an external service.

        :param content: The remote RDF file contents
        :type content: string
        :param harvest_job: A ``HarvestJob`` domain object which contains a
                            reference to the harvest source
                            (``harvest_job.source``).
        :type harvest_job: object


        :returns: A tuple with two items:
                    * The file content. If this is False the gather stage will
                      stop.
                    * A list of error messages. These will get stored as gather
                      errors by the harvester
        :rtype: tuple
        '''
        return content, []

    def before_update(self, harvest_object, dataset_dict, temp_dict):
        '''
        Called just before the ``package_update`` action.
        It may be used to preprocess the dataset dict.

        If the content of the dataset dict is emptied (i.e. set to ``None``), 
        the dataset will not be updated in CKAN, but simply ignored.

        Implementations may store some temp values in temp_dict, that will be
        then passed back in the ``after_update`` call.

        :param harvest_object: A ``HarvestObject`` domain object.
        :type harvest_job: object
        :param dataset_dict: The dataset dict already parsed by the RDF parser
                             (and related plugins).
        :type dataset_dict: dict
        :param temp_dict: A dictionary, shared among all plugins, for storing
                          temp data. Such dict will be passed back in the
                          ``after_update`` call.
        :type temp_dict: dict
        '''
        pass

    def after_update(self, harvest_object, dataset_dict, temp_dict):
        '''
        Called just after a successful ``package_update`` action has been
        performed.

        :param harvest_object: A ``HarvestObject`` domain object.
        :type harvest_job: object
        :param dataset_dict: The dataset dict that has just been stored into
                             the DB.
        :type dataset_dict: dict
        :param temp_dict: A dictionary, shared among all plugins, for storing
                          temp data. 
        :type temp_dict: dict

        :returns: A string containing an error message, or None. If the error
                  string is not None, it will be saved as an import error,
                  and dataset importing will be rolled back,
        :rtype: string
        '''

        return None

    def before_create(self, harvest_object, dataset_dict, temp_dict):
        '''
        Called just before the ``package_create`` action.
        It may be used to preprocess the dataset dict.

        If the content of the dataset dict is emptied (i.e. set to ``None``), 
        the dataset will not be created in CKAN, but simply ignored.

        Implementations may store some temp values in temp_dict, that will be
        then passed back in the ``after_create`` call.

        :param harvest_object: A ``HarvestObject`` domain object.
        :type harvest_job: object
        :param dataset_dict: The dataset dict already parsed by the RDF parser
                             (and related plugins).
        :type dataset_dict: dict
        :param temp_dict: A dictionary, shared among all plugins, for storing
                          temp data. Such dict will be passed back in the
                          ``after_create`` call.
        :type temp_dict: dict
        '''
        pass

    def after_create(self, harvest_object, dataset_dict, temp_dict):
        '''
        Called just after a successful ``package_create`` action has been
        performed.

        :param harvest_object: A ``HarvestObject`` domain object.
        :type harvest_job: object
        :param dataset_dict: The dataset dict that has just been stored into
                             the DB.
        :type dataset_dict: dict
        :param temp_dict: A dictionary, shared among all plugins, for storing
                          temp data.
        :type temp_dict: dict

        :returns: A string containing an error message, or None. If the error
                  string is not None, it will be saved as an import error,
                  and dataset importing will be rolled back,
        :rtype: string
        '''
        return None
