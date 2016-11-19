

from .datafs.services.service import DataService
from .datafs.core import DataFile
from fs.memoryfs import MemoryFS


class MemoryService(DataService):
    '''
    Access files & directories stored in memory (non-permanent but very fast)
    '''
    
    FileConstructor = MemoryDataFile

    def __init__(self, api, archive, *args, **kwargs):
        DataService.__init__(self, api, archive, *args, **kwargs)

    def self._get_datafile(self, archive_name, version_id):
        raise NotImplementedError


class MemoryDataFile(DataFile, MemoryFS):
    '''
    MemoryFS access files & directories stored in memory (non-permanent but very fast)
    '''
    def __init__(self, api, archive, *args, **kwargs):
        DataFile.__init__(self, api, archive)
        MemoryFS.__init__(self, *args, **kwargs)