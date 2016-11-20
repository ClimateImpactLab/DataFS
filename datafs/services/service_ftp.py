from __future__ import absolute_import

from datafs.services.service import DataService
from datafs.core.data_file import DataFile
from fs.ftpfs import FTPFS


class FTPDataFile(DataFile, FTPFS):
    '''
    Access files & directories on an FTP server
    '''
    def __init__(self, api, archive, *args, **kwargs):
        DataFile.__init__(self, api, archive)
        FTPFS.__init__(self, *args, **kwargs)


        
class FTPService(DataService):
    '''
    Service providing an interface to files & directories on an FTP server
    '''
    
    FileConstructor = FTPDataFile

    def __init__(self, api, *args, **kwargs):
        Service.__init__(self, api, *args, **kwargs)

    def _get_datafile(self, archive_name, version_id):
        raise NotImplementedError