
import fs.utils
import fs.path
import tempfile
import shutil
import time
# from fs.osfs import OSFS
from fs.tempfs import TempFS
from fs.multifs import MultiFS

from fs.errors import (ResourceLockedError, ResourceInvalidError)


class BaseVersionedFile(object):
    '''
    .. todo:: 

        Enable caching

    '''

    def __init__(self, archive, *args, **kwargs):
        self.archive = archive
        self.cache = False

        self.args = args
        self.kwargs = kwargs

    def _get_file_wrapper(self):

        self.archive.authority.fs.makedir(
            fs.path.dirname(self.archive.service_path),
            recursive=True,
            allow_recreate=True)

        # Check the hash (if one exists) for a local version of the file
        if self.archive.api.cache:

            # Delete the file in the local cache if it is out of date.
            local_hash = self.archive.api.cache.get_hash(
                self.archive.service_path)
            latest_hash = self.archive.latest_hash()
            if local_hash != latest_hash:
                self.archive.api.cache.fs.remove(self.archive.service_path)

        # Create a read-only wrapper with download priority cache, then
        # authority
        self.fs_wrapper = MultiFS()
        self.fs_wrapper.addfs('authority', self.archive.authority.fs)
        if self.archive.api.cache:
            self.fs_wrapper.addfs('cache', self.archive.api.cache.fs)

        # Add a temporary filesystem as the write filesystem
        # self.tempdir = tempfile.mkdtemp()
        # self.temp_fs = OSFS(self.tempdir)
        self.temp_fs = TempFS()

        self.temp_fs.makedir(
            fs.path.dirname(self.archive.service_path),
            recursive=True,
            allow_recreate=True)

        self.fs_wrapper.setwritefs(self.temp_fs)

    def open(self):
        self._get_file_wrapper()

        return self.fs_wrapper.open(
            self.archive.service_path,
            *self.args,
            **self.kwargs)

    def get_sys_path(self):
        self._get_file_wrapper()

        #  create a temporary file and save the data to the temporary file
        self.temp_fs = TempFS()
        self.temp_fs.makedir(
            fs.path.dirname(self.archive.service_path),
            recursive=True,
            allow_recreate=True)

        # Check if the file already exists. If so, copy it into the temporary
        # directory
        if self.fs_wrapper.exists(self.archive.service_path):
            fs.utils.copyfile(
                self.fs_wrapper,
                self.archive.service_path,
                self.temp_fs,
                self.archive.service_path)

        return self.temp_fs.getsyspath(self.archive.service_path)


    def _close_temp_fs(self):
        try:
            self.temp_fs.close()
        except (ResourceLockedError, ResourceInvalidError):
            time.sleep(0.5)
            self.temp_fs.close()


    def close(self):

        # If nothing was written, exit
        if not self.temp_fs.exists(self.archive.service_path):
            for p in self.temp_fs.listdir('/'):
                if self.temp_fs.isfile(p):
                    self.temp_fs.remove(p)
                elif self.temp_fs.isdir(p):
                    self.temp_fs.removedir(p, recursive=True, force=True)

            self.fs_wrapper.clearwritefs()
            self._close_temp_fs()
            # shutil.rmtree(self.tempdir)
            return

        # If cache exists:
        if self.cache:

            if self.api.cache:
                raise IOError('Cannot save to cache - cache not set')

            # Move the file to the cache before uploading
            fs.utils.movefile(
                self.temp_fs,
                self.archive.service_path,
                self.archive.api.cache.fs,
                self.archive.service_path)

            # Update the archive with the new version
            self.archive.update(
                self.archive.api.cache.fs.getsyspath(
                    self.archive.service_path))

        else:
            # Update the archive with the new version
            self.archive.update(
                self.temp_fs.getsyspath(
                    self.archive.service_path))

        for p in self.temp_fs.listdir('/'):
            if self.temp_fs.isfile(p):
                self.temp_fs.remove(p)
            elif self.temp_fs.isdir(p):
                self.temp_fs.removedir(p, recursive=True, force=True)

        self.fs_wrapper.clearwritefs()
        self._close_temp_fs()
        # del self.temp_fs.close()
        # shutil.rmtree(self.tempdir)


class DataFile(BaseVersionedFile):

    def __enter__(self):
        self._f_obj = self.open()
        return self._f_obj

    def __exit__(self, exception_type, exception_value, traceback):
        self._f_obj.close()
        self.close()
        return False


class LocalFile(DataFile):

    def __enter__(self):
        return self.get_sys_path()

    def __exit__(self, exception_type, exception_value, traceback):
        self.close()
        return False
