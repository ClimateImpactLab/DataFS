
import fs.utils
import fs.path
import tempfile
import shutil
import time
# from fs.osfs import OSFS
from fs.tempfs import TempFS
from fs.multifs import MultiFS

from fs.errors import (ResourceLockedError, ResourceInvalidError)


class BaseVersionedFileOpener(object):
    '''
    .. todo::

        Enable caching

    '''

    def __init__(self, archive, *args, **kwargs):
        self.archive = archive
        self.cache = False

        self.args = args
        self.kwargs = kwargs

    def _create_service_paths(self):

        self.archive.authority.fs.makedir(
            fs.path.dirname(self.archive.service_path),
            recursive=True,
            allow_recreate=True)
        
        if self.archive.api.cache:
            self.archive.authority.fs.makedir(
                fs.path.dirname(self.archive.service_path),
                recursive=True,
                allow_recreate=True)

    def _prune_outdated_cache_files(self):
        '''
        Delete service path from cache if hash does not match latest
        '''

        # Check the hash (if one exists) for a local version of the file
        if self.archive.api.cache:

            try:
                local_hash = self.archive.api.cache.get_hash(
                    self.archive.service_path)
            except OSError:
                return

            latest_hash = self.archive.latest_hash()
            
            # Delete the file in the local cache if it is out of date.
            if local_hash != latest_hash:
                self.archive.api.cache.fs.remove(self.archive.service_path)

    def _get_file_wrapper(self):

        # Make sure we don't have any old data in the cache
        self._prune_outdated_cache_files()

        # Make sure services have the directory for our file
        self._create_service_paths()

        # Create a read-only wrapper with download priority cache, then
        # authority
        self.fs_wrapper = MultiFS()
        self.fs_wrapper.addfs('authority', self.archive.authority.fs)
        if self.archive.api.cache:
            self.fs_wrapper.addfs('cache', self.archive.api.cache.fs)

    def _attach_temporary_write_dir(self):
        # Add a temporary filesystem as the write filesystem
        self.temp_write_fs = TempFS()
        self.temp_write_fs.makedir(
            fs.path.dirname(self.archive.service_path),
            recursive=True,
            allow_recreate=True)

        self.fs_wrapper.setwritefs(self.temp_write_fs)

    def _open(self):
        self._get_file_wrapper()
        self._attach_temporary_write_dir()

        return self.fs_wrapper.open(
            self.archive.service_path,
            *self.args,
            **self.kwargs)

    def _get_sys_path(self):
        self._get_file_wrapper()
        self._attach_temporary_write_dir()

        # Check if the file already exists. If so, copy it into the temporary
        # directory
        if self.fs_wrapper.exists(self.archive.service_path):
            fs.utils.copyfile(
                self.fs_wrapper,
                self.archive.service_path,
                self.temp_write_fs,
                self.archive.service_path)

        return self.temp_write_fs.getsyspath(self.archive.service_path)

    def _close_temp_write_fs(self):
        try:
            self.temp_write_fs.close()
        except (ResourceLockedError, ResourceInvalidError):
            time.sleep(0.5)
            self.temp_write_fs.close()

    def _close(self):

        # If nothing was written, exit
        if not self.temp_write_fs.exists(self.archive.service_path):
            for p in self.temp_write_fs.listdir('/'):
                if self.temp_write_fs.isfile(p):
                    self.temp_write_fs.remove(p)
                elif self.temp_write_fs.isdir(p):
                    self.temp_write_fs.removedir(p, recursive=True, force=True)

            self.fs_wrapper.clearwritefs()
            self._close_temp_write_fs()
            # shutil.rmtree(self.tempdir)
            return

        # If cache exists:
        if self.cache:

            if self.api.cache:
                raise IOError('Cannot save to cache - cache not set')

            # Move the file to the cache before uploading
            fs.utils.movefile(
                self.temp_write_fs,
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
                self.temp_write_fs.getsyspath(
                    self.archive.service_path))

        for p in self.temp_write_fs.listdir('/'):
            if self.temp_write_fs.isfile(p):
                self.temp_write_fs.remove(p)
            elif self.temp_write_fs.isdir(p):
                self.temp_write_fs.removedir(p, recursive=True, force=True)

        self.fs_wrapper.clearwritefs()
        self._close_temp_write_fs()
        # del self.temp_write_fs.close()
        # shutil.rmtree(self.tempdir)


class FileOpener(BaseVersionedFileOpener):

    def __enter__(self):
        self._f_obj = self._open()
        return self._f_obj

    def __exit__(self, exception_type, exception_value, traceback):
        self._f_obj.close()
        self._close()
        return False


class FilePathOpener(FileOpener):

    def __enter__(self):
        return self._get_sys_path()

    def __exit__(self, exception_type, exception_value, traceback):
        self._close()
        return False
