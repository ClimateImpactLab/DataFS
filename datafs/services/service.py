
import os
import fs.utils
from fs.osfs import OSFS
from fs.base import FS

class DataService(object):

    def __init__(self, fs):
        self.fs = fs

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

        target_name = fs.path.join(*tuple(archive_name.split('.') + [version_id + os.path.splitext()[1]]))

        self._get_datafile(self, archive_name, version_id)

    def upload(self, file, archive_name, version_id):
        '''

        Returns
        -------
        response : dict
            location of the object and other metadata

        '''

        current_fs = OSFS(os.path.dirname(file))
        current_path = os.path.basename(file)

        target_name = fs.path.join(*tuple(archive_name.split('.') + [version_id + os.path.splitext(file)[1]]))

        self.fs.makedir(fs.path.dirname(target_name), recursive=True, allow_recreate=True)
        fs.utils.copyfile(current_fs, current_path, self.fs, target_name)

        return {'path': target_name}

    # private methods to be implemented by subclasses

    def _get_datafile(self, archive_name, version_id):
        raise NotImplementedError('BaseService cannot be used directly. Use a subclass, such as OSService')

