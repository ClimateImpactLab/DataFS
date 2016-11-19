from __future__ import absolute_import

from datafs.services.service import DataService
from datafs.core.data_file import DataFile
from fs.sftpfs import SFTPFS


class SFTPDataFile(DataFile, SFTPFS):
    '''
    Access files & directories stored on a Secure FTP server
    '''
    def __init__(self, api, archive, *args, **kwargs):
        DataFile.__init__(self, api, archive)
        SFTPFS.__init__(self, *args, **kwargs)



class SFTPService(DataService):
    '''
    Service providing an interface to files & directories stored on a Secure FTP server
    '''
    
    FileConstructor = SFTPDataFile

    def __init__(self, api, archive, *args, **kwargs):
        Service.__init__(self, api, archive, *args, **kwargs)

    def _get_datafile(self, archive_name, version_id):
        raise NotImplementedError
