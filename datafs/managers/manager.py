

class BaseDataManager(object):
    '''
    Base class for DataManager metadata store objects

    Should be subclassed. Not intended to be used directly.
    '''

    def __init__(self, api):
        self.api = api


    def update(self, archive_name, file, **kwargs):
        '''
        Register a new version for archive ``archive_name``
        '''

        self._update(self, archive_name, file, **kwargs)

    def update_metadata(self, archive_name, **kwargs):
        '''
        Update metadata for archive ``archive_name``
        '''

        self._update_metadata(self, archive_name, **kwargs)

    def get_services_for_version(self, archive_name, version_id):
        '''
        Return services available for version ``version_id`` of archive ``archive_name``
        
        Returns
        -------
        services : list
            list of available service obejcts

        .. note ::

            this method does not check to make sure the version is available 
            with this service. This is the responsibility of the consumer of the 
            service list.

        '''

        self._get_services_for_version(self, archive_name, version_id)


    def get_datafile_from_service(self, archive_name, version_id, service):
        '''
        Return a DataFile object from a specific service
        '''

        self._get_datafile_from_service(self, archive_name, version_id, service)


    def get_all_version_ids(self, archive_name):
        '''
        List version IDs available for ``archive_name``

        Returns
        -------
        version_ids : list

        '''

        self._get_all_version_ids(self, archive_name)


    def get_version(self, archive_name, version_id):
        '''
        Retrieve a DataFile for the specified version from available services

        Parameters
        ----------
        archive_name : str
            name of the archive

        version_id : str
            data version to retrieve from services

        Returns
        -------
        version : object
            DataFile object corresponding to version ``version_id``

        '''

        for service in self.api._manager.get_services_for_version(self, archive_name, version_id):
            try:
                self.api._manager.get_datafile_from_service(self, archive_name, version_id, serice)
            except ServiceNotAvailableError as e:
                logging.warn('service "{}" not available when retrieving "{}" version "{}"'.format(service.name, archive_name, version_id))
            except VersionNotAvailableError as e:
                pass


    def create_archive(self, archive_name):
        '''
        Create a new data archive

        Returns
        -------
        archive : object
            new :py:class:`~datafs.core.data_archive.DataArchive` object

        '''

        self._create_archvie(archive_name)


    def get_archive(self, archive_name):
        '''
        Get a data archive given an archive name

        Returns
        -------
        archive : object
            :py:class:`~datafs.core.data_archive.DataArchive` object

        '''

        self._get_archvie(archive_name)



    # Private methods (to be implemented by subclasses of DataManager)
    
    def _update(self, archive_name, file, **kwargs):
        raise NotImplementedError('BaseDataManager cannot be used directly. Use a subclass, such as MongoDBManager')

    def _update_metadata(self, archive_name, **kwargs):
        raise NotImplementedError('BaseDataManager cannot be used directly. Use a subclass, such as MongoDBManager')

    def _get_services_for_version(self, archive_name, version_id):
        raise NotImplementedError('BaseDataManager cannot be used directly. Use a subclass, such as MongoDBManager')

    def _get_datafile_from_service(self, archive_name, version_id, service):
        raise NotImplementedError('BaseDataManager cannot be used directly. Use a subclass, such as MongoDBManager')

    def _get_all_version_ids(self, archive_name):
        raise NotImplementedError('BaseDataManager cannot be used directly. Use a subclass, such as MongoDBManager')

    def _create_archvie(self, archive_name):
        raise NotImplementedError('BaseDataManager cannot be used directly. Use a subclass, such as MongoDBManager')

    def _get_archvie(self, archive_name):
        raise NotImplementedError('BaseDataManager cannot be used directly. Use a subclass, such as MongoDBManager')


