

from .datafs.services.service import DataService
from .datafs.core.data_file import DataFile
from fs.mountfs import MountFS


class MountService(DataService):
    '''
    Service providing an interface to a virtual directory structure built from other filesystems
    '''
    
    FileConstructor = MountDataFile

    def __init__(self, api, archive, *args, **kwargs):
        DataService.__init__(self, api, archive, *args, **kwargs)

    def self._get_datafile(self, archive_name, version_id):
        raise NotImplementedError


class MountDataFile(DataFile, MountFS):
    '''
    MountFS creates a virtual directory structure built from other filesystems
    '''
    def __init__(self, api, archive, *args, **kwargs):
        DataFile.__init__(self, api, archive)
        MountFS.__init__(self, *args, **kwargs)