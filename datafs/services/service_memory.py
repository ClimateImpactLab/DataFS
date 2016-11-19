from __future__ import absolute_import

from datafs.services.service import DataService
from datafs.core.data_file import DataFile
from fs.memoryfs import MemoryFS


class MemoryDataFile(DataFile, MemoryFS):
    '''
    Access files & directories stored in memory (non-permanent but very fast)
    '''
    def __init__(self, api, archive, *args, **kwargs):
        DataFile.__init__(self, api, archive)
        MemoryFS.__init__(self, *args, **kwargs)



class MemoryService(DataService):
    '''
    Service providing an interface to files & directories stored in memory (non-permanent but very fast)
    '''
    
    FileConstructor = MemoryDataFile

    def __init__(self, api, archive, *args, **kwargs):
        DataService.__init__(self, api, archive, *args, **kwargs)

    def _get_datafile(self, archive_name, version_id):
        raise NotImplementedError