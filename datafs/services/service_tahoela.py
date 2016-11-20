from __future__ import absolute_import

from datafs.services.service import DataService
from datafs.core.data_file import DataFile
from fs.contrib.tahoelafs import TahoeLAFS


class TahoeLADataFile(DataFile, TahoeLAFS):
    '''
    Access files & directories stored on a Tahoe distributed filesystem
    '''
    def __init__(self, api, archive, *args, **kwargs):
        DataFile.__init__(self, api, archive)
        TahoeLAFS.__init__(self, *args, **kwargs)



class TahoeLAService(DataService):
    '''
    Service providing an interface to files & directories stored on a Tahoe distributed filesystem
    '''
    
    FileConstructor = TahoeLADataFile

    def __init__(self, api, *args, **kwargs):
        Service.__init__(self, api, *args, **kwargs)

    def _get_datafile(self, archive_name, version_id):
        raise NotImplementedError


