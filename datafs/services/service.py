


class DataService(object):
    def __init__(self, api, archive, *args, **kwargs):
        self.api = api
        self.archive = archive
        
        self.service_config = {
            'args': args,
            'kwargs': kwargs
        }

    def get_datafile(self, archive_name, version_id):
        '''
        Retrieve a :py:class:`~datafs.core.data_file.DataFile` object

        Parameters
        ----------
        archive_name : str
            archive name for requested file

        version_id : str
            version ID of requested file

        Returns
        -------
        datafile : object
            :py:class:`~datafs.core.data_file.DataFile` object
        
        '''

        self._get_datafile(self, archive_name, version_id)


    def _get_datafile(self, archive_name, version_id):
        raise NotImplementedError('BaseService cannot be used directly. Use a subclass, such as OSService')



