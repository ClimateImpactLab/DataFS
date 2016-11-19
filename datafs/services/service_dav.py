

from .datafs.services.service import DataService
from .datafs.core.data_file import DataFile
from fs.davfs import DavFS


class DavService(DataService):
    '''
    Service providing an interface to files & directories on a WebDAV server
    '''
    
    FileConstructor = DavDataFile

    def __init__(self, api, archive, *args, **kwargs):
        Service.__init__(self, api, archive, *args, **kwargs)

    def self._get_datafile(self, archive_name, version_id):
        raise NotImplementedError


class DavDataFile(DataFile, DavFS):
    '''
    Access files & directories on a WebDAV server
    '''
    def __init__(self, api, archive, *args, **kwargs):
        DataFile.__init__(self, api, archive)
        DavFS.__init__(self, *args, **kwargs)
