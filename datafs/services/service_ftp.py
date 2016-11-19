

from .datafs.services.service import DataService
from .datafs.core.data_file import DataFile
from fs.ftpfs import FTPFS

class FTPService(Service):
    '''
    Access files & directories on an FTP server
    '''
    
    FileConstructor = FTPDataFile

    def __init__(self, api, archive, *args, **kwargs):
        Service.__init__(self, api, archive, *args, **kwargs)

    def self._get_datafile(self, archive_name, version_id):
        raise NotImplementedError


class FTPDataFile(DataFile, FTPFS):
    '''
    FTPFS access files & directories on an FTP server
    '''
    def __init__(self, api, archive, *args, **kwargs):
        DataFile.__init__(self, api, archive)
        FTPFS.__init__(self, *args, **kwargs)