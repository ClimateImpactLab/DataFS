

from .datafs.services.service import DataService
from .datafs.core.data_file import DataFile
from fs.zipfs import ZipFS


class ZipService(DataService):
    '''
    Service providing an interface to files and directories contained in a zip file
    '''
    
    FileConstructor = ZipDataFile

    def __init__(self, api, archive, *args, **kwargs):
        Service.__init__(self, api, archive, *args, **kwargs)

    def self._get_datafile(self, archive_name, version_id):
        raise NotImplementedError


class ZipDataFile(DataFile, ZipFS):
    '''
    Access files and directories contained in a zip file
    '''
    def __init__(self, api, archive, *args, **kwargs):
        DataFile.__init__(self, api, archive)
        ZipFS.__init__(self, *args, **kwargs)
