

from .datafs.services.service import DataService
from .datafs.core.data_file import DataFile
from fs.multifs import MultiFS


class MultiService(Service):
    '''
    A virtual filesystem that combines a list of filesystems into one, and checks them in order when opening files
    '''
    
    FileConstructor = MultiDataFile

    def __init__(self, api, archive, *args, **kwargs):
        Service.__init__(self, api, archive, *args, **kwargs)

    def self._get_datafile(self, archive_name, version_id):
        raise NotImplementedError


class MultiDataFile(DataFile, MultiFS):
    '''
    MultiFS a virtual filesystem that combines a list of filesystems into one, and checks them in order when opening files
    '''
    def __init__(self, api, archive, *args, **kwargs):
        DataFile.__init__(self, api, archive)
        MultiFS.__init__(self, *args, **kwargs)
