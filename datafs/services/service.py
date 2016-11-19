
from datafs.core import DataFile


from fs.davfs import DavFS
from fs.ftpfs import FTPFS
from fs.memoryfs import MemoryFS
from fs.mountfs import MountFS
from fs.multifs import MultiFS
from fs.osfs import OSFS
from fs.sftpfs import SFTPFS
from fs.s3fs import S3FS
from fs.tahoelafs import TahoeLAFS
from fs.zipfs import ZipFS


class Service(object):
    def __init__(self, api, archive, *args, **kwargs):
        self.api = api
        self.archive = archive
        
        self.service_config = {
            'args': args,
            'kwargs': kwargs
        }


class DavService(DataFile, DavFS):
    '''
    DavFS access files & directories on a WebDAV server
    '''
    FileConstructor = DavDataFile
    def __init__(self, api, archive, *args, **kwargs):
        Service.__init__(self, api, archive, *args, **kwargs)


class FTPService(DataFile, FTPFS):
    '''
    FTPFS access files & directories on an FTP server
    '''
    FileConstructor = FTPDataFile
    def __init__(self, api, archive, *args, **kwargs):
        Service.__init__(self, api, archive, *args, **kwargs)


class MemoryService(DataFile, MemoryFS):
    '''
    MemoryFS access files & directories stored in memory (non-permanent but very fast)
    '''
    FileConstructor = MemoryDataFile
    def __init__(self, api, archive, *args, **kwargs):
        Service.__init__(self, api, archive, *args, **kwargs)


class MountService(DataFile, MountFS):
    '''
    MountFS creates a virtual directory structure built from other filesystems
    '''
    FileConstructor = MountDataFile
    def __init__(self, api, archive, *args, **kwargs):
        Service.__init__(self, api, archive, *args, **kwargs)


class MultiService(DataFile, MultiFS):
    '''
    MultiFS a virtual filesystem that combines a list of filesystems into one, and checks them in order when opening files
    '''
    FileConstructor = MultiDataFile
    def __init__(self, api, archive, *args, **kwargs):
        Service.__init__(self, api, archive, *args, **kwargs)


class OSService(DataFile, OSFS):
    '''
    OSFS the native filesystem
    '''
    FileConstructor = OSDataFile
    def __init__(self, api, archive, *args, **kwargs):
        Service.__init__(self, api, archive, *args, **kwargs)


class SFTPService(DataFile, SFTPFS):
    '''
    SFTPFS access files & directories stored on a Secure FTP server
    '''
    FileConstructor = SFTPDataFile
    def __init__(self, api, archive, *args, **kwargs):
        Service.__init__(self, api, archive, *args, **kwargs)


class S3Service(DataFile, S3FS):
    '''
    S3FS access files & directories stored on Amazon S3 storage
    '''
    FileConstructor = S3DataFile
    def __init__(self, api, archive, *args, **kwargs):
        Service.__init__(self, api, archive, *args, **kwargs)


class TahoeLAService(DataFile, TahoeLAFS):
    '''
    TahoeLAFS access files & directories stored on a Tahoe distributed filesystem
    '''
    FileConstructor = TahoeLADataFile
    def __init__(self, api, archive, *args, **kwargs):
        Service.__init__(self, api, archive, *args, **kwargs)


class ZipService(DataFile, ZipFS):
    '''
    ZipFS access files and directories contained in a zip file
    '''
    FileConstructor = ZipDataFile
    def __init__(self, api, archive, *args, **kwargs):
        Service.__init__(self, api, archive, *args, **kwargs)


