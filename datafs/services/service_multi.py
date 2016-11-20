from __future__ import absolute_import

from datafs.services.service import DataService
from datafs.core.data_file import DataFile
from fs.multifs import MultiFS


class MultiDataFile(DataFile, MultiFS):
    '''
    MultiFS a virtual filesystem that combines a list of filesystems into one, and checks them in order when opening files
    '''
    def __init__(self, api, archive, *args, **kwargs):
        DataFile.__init__(self, api, archive)
        MultiFS.__init__(self, *args, **kwargs)



class MultiService(DataService):
    '''
    Service providing an interface to a virtual filesystem that combines a list of filesystems into one, and checks them in order when opening files
    '''
    
    FileConstructor = MultiDataFile

    def __init__(self, api, *args, **kwargs):
        Service.__init__(self, api, *args, **kwargs)

    def _get_datafile(self, archive_name, version_id):
        raise NotImplementedError
