from __future__ import absolute_import

from datafs.services.service import DataService
from datafs.core.data_file import DataFile
from fs.zipfs import ZipFS


class ZipDataFile(DataFile, ZipFS):
    '''
    Access files and directories contained in a zip file
    '''
    def __init__(self, api, archive, *args, **kwargs):
        DataFile.__init__(self, api, archive)
        ZipFS.__init__(self, *args, **kwargs)



class ZipService(DataService):
    '''
    Service providing an interface to files and directories contained in a zip file
    '''
    
    FileConstructor = ZipDataFile

    def __init__(self, api, *args, **kwargs):
        Service.__init__(self, api, *args, **kwargs)

    def _get_datafile(self, archive_name, version_id):
        raise NotImplementedError
