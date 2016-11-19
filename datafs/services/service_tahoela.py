

from .datafs.services.service import DataService
from .datafs.core.data_file import DataFile
from fs.tahoelafs import TahoeLAFS


class TahoeLAService(Service):
    '''
    Access files & directories stored on a Tahoe distributed filesystem
    '''
    
    FileConstructor = TahoeLADataFile

    def __init__(self, api, archive, *args, **kwargs):
        Service.__init__(self, api, archive, *args, **kwargs)

    def self._get_datafile(self, archive_name, version_id):
        raise NotImplementedError


class TahoeLADataFile(DataFile, TahoeLAFS):
    '''
    TahoeLAFS access files & directories stored on a Tahoe distributed filesystem
    '''
    def __init__(self, api, archive, *args, **kwargs):
        DataFile.__init__(self, api, archive)
        TahoeLAFS.__init__(self, *args, **kwargs)


