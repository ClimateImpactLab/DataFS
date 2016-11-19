from __future__ import absolute_import

from datafs.services.service import DataService
from datafs.core.data_file import DataFile
from fs.contrib.davfs import DavFS


class DavDataFile(DataFile, DavFS):
    '''
    Access files & directories on a WebDAV server
    '''
    def __init__(self, api, archive, *args, **kwargs):
        DataFile.__init__(self, api, archive)
        DavFS.__init__(self, *args, **kwargs)



class DavService(DataService):
    '''
    Service providing an interface to files & directories on a WebDAV server
    '''
    
    FileConstructor = DavDataFile

    def __init__(self, api, archive, *args, **kwargs):
        Service.__init__(self, api, archive, *args, **kwargs)

    def _get_datafile(self, archive_name, version_id):
        raise NotImplementedError
