

class BaseDataManager(object):
    def __init__(self, api):
        self.api = api

    def update(self, service, service_object):
        raise NotImplementedError

    # Private methods (to be implemented by subclasses of DataManager)

    def get_services_for_version(self, version_id):
        raise NotImplementedError

    def get_file_handler_from_service(self, version_id, service):
        raise NotImplementedError

    def get_all_version_ids(self):
        raise NotImplementedError

    def get_version(self, version_id):
        '''
        Retrieve a DataFile for the specified version from available services

        Parameters
        ----------
        version_id : str
            data version to retrieve from services

        Returns
        -------
        version : object
            DataFile object corresponding to version ``version_id``

        '''

        for service in self.api._manager.get_services_for_version(self, archive_id, version_id):
            try:
                self.api._manager.get_file_handler_from_service(self, archive_id, version_id, serice)
            except ServiceNotAvailableError as e:
                logging.warn('service {} not available when retrieving {}'.format(service.name, version_id))

            except VersionNotAvailableError as e:
                pass

