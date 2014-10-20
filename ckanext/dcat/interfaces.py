from ckan.plugins.interfaces import Interface


class IRDFDCATHarvester(Interface):

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
