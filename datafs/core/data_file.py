
import logging

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

class DataFile(object):
    '''
    Base class for DataFile objects

    Should be subclassed, along with fs filesystem classes

    '''


    def __init__(self, api, archive):
        self.api = api
        self.archive = archive

    @property
    def metadata(self):
        return self.archive.metadata

    @metadata.setter
    def metadata(self, value):
        raise AttributeError('metadata attribute cannot be set')


    def delete_local(self):
        raise NotImplementedError




class DavDataFile(DataFile, DavFS):
    '''
    DavFS access files & directories on a WebDAV server
    '''
    def __init__(self, api, archive, *args, **kwargs):
        DataFile.__init__(self, api, archive)
        DavFS.__init__(self, *args, **kwargs)


class FTPDataFile(DataFile, FTPFS):
    '''
    FTPFS access files & directories on an FTP server
    '''
    def __init__(self, api, archive, *args, **kwargs):
        DataFile.__init__(self, api, archive)
        FTPFS.__init__(self, *args, **kwargs)


class MemoryDataFile(DataFile, MemoryFS):
    '''
    MemoryFS access files & directories stored in memory (non-permanent but very fast)
    '''
    def __init__(self, api, archive, *args, **kwargs):
        DataFile.__init__(self, api, archive)
        MemoryFS.__init__(self, *args, **kwargs)


class MountDataFile(DataFile, MountFS):
    '''
    MountFS creates a virtual directory structure built from other filesystems
    '''
    def __init__(self, api, archive, *args, **kwargs):
        DataFile.__init__(self, api, archive)
        MountFS.__init__(self, *args, **kwargs)


class MultiDataFile(DataFile, MultiFS):
    '''
    MultiFS a virtual filesystem that combines a list of filesystems into one, and checks them in order when opening files
    '''
    def __init__(self, api, archive, *args, **kwargs):
        DataFile.__init__(self, api, archive)
        MultiFS.__init__(self, *args, **kwargs)


class OSDataFile(DataFile, OSFS):
    '''
    OSFS the native filesystem
    '''
    def __init__(self, api, archive, *args, **kwargs):
        DataFile.__init__(self, api, archive)
        OSFS.__init__(self, *args, **kwargs)


class SFTPDataFile(DataFile, SFTPFS):
    '''
    SFTPFS access files & directories stored on a Secure FTP server
    '''
    def __init__(self, api, archive, *args, **kwargs):
        DataFile.__init__(self, api, archive)
        SFTPFS.__init__(self, *args, **kwargs)


class S3DataFile(DataFile, S3FS):
    '''
    S3FS access files & directories stored on Amazon S3 storage
    '''
    def __init__(self, api, archive, *args, **kwargs):
        DataFile.__init__(self, api, archive)
        S3FS.__init__(self, *args, **kwargs)


class TahoeLADataFile(DataFile, TahoeLAFS):
    '''
    TahoeLAFS access files & directories stored on a Tahoe distributed filesystem
    '''
    def __init__(self, api, archive, *args, **kwargs):
        DataFile.__init__(self, api, archive)
        TahoeLAFS.__init__(self, *args, **kwargs)


class ZipDataFile(DataFile, ZipFS):
    '''
    ZipFS access files and directories contained in a zip file
    '''
    def __init__(self, api, archive, *args, **kwargs):
        DataFile.__init__(self, api, archive)
        ZipFS.__init__(self, *args, **kwargs)


