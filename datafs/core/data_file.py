
import fs.utils
import tempfile
from fs.tempfs import TempFS
from fs.multifs import MultiFS

class BaseVersionedFile(object):
    def __init__(self, archive, cache=False, *args, **kwargs):
        self.archive = archive
        self.cache = cache

        self.args = args
        self.kwargs = kwargs


    def _get_file_wrapper(self):

        # Check the hash (if one exists) for a local version of the file
        if self.archive.api.cache:

            # Delete the file in the local cache if it is out of date.
            local_hash = self.archive.api.cache.get_hash(self.archive.service_path)
            latest_hash = self.archive.latest_hash()
            if local_hash != latest_hash:
                self.archive.api.cache.fs.remove(self.archive.service_path)

        # Create a read-only wrapper with download priority cache, then authority
        self.fs_wrapper = MultiFS()
        self.fs_wrapper.addfs('authority', self.archive.authority.fs)
        if self.archive.api.cache:
            self.fs_wrapper.addfs('cache', self.archive.api.cache.fs)
        
        # Add a temporary filesystem as the write filesystem
        self.temp_fs = TempFS()
        self.fs_wrapper.setwritefs(self.temp_fs)
        
    def open(self):
        self._get_file_wrapper()
        
        return self.fs_wrapper.open(self.archive.service_path, *self.args, **self.kwargs)

    def get_sys_path(self):
        self._get_file_wrapper()

        #  create a temporary file and save the data to the temporary file
        self.temp_fs = TempFS()
        fs.utils.copyfile(self.fs_wrapper, self.service_path, self.temp_fs, self.service_path)

        return self.temp_fs.getsyspath(self.service_path)


    def close(self):
        # If nothing was written, exit
        if not self.temp_fs.exists(self.archive.service_path):
            self.temp_fs.close()
            return True

        # If cache exists:
        if self.cache:

            # Move the file to the cache before uploading
            fs.utils.movefile(self.temp_fs, self.archive.service_path, self.archive.api.cache.fs, self.archive.service_path)

            # Update the archive with the new version
            self.archive.update(self.archive.api.cache.fs.getsyspath(self.archive.service_path))

        else:
            # Update the archive with the new version
            self.archive.update(self.temp_fs.getsyspath(self.archive.service_path))


        self.temp_fs.close()
        return True

    
class DataFile(BaseVersionedFile):
    def __enter__(self):
        return self.open()

    def __exit__(self, exception_type, exception_value, traceback):
        self.close()
        return True


class LocalFile(DataFile):
    def __enter__(self):
        return self.get_sys_path()

    def __exit__(self, exception_type, exception_value, traceback):
        self.close()
        return True
