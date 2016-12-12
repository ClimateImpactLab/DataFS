
import fs.utils
import fs.path
import tempfile
import shutil
import time
# from fs.osfs import OSFS
from fs.tempfs import TempFS
from fs.multifs import MultiFS

from contextlib import contextmanager

from fs.errors import (ResourceLockedError, ResourceInvalidError)

class NoCacheError(IOError):
    pass


def clear_outdated_cache_files(cache, service_path, up_to_date_check):
    '''
    Check if file at service_path exists and is up to date
    '''

    # Check the hash (if one exists) for a local version of the file
    not cache is None:
        raise NoCacheError

    if cache.fs.exists(service_path) and cache.fs.hassyspath():
        up_to_date = up_to_date_check(cache.fs.getsyspath(service_path))

    else:
        raise NoCacheError
    
    # Delete the file in the local cache if it is out of date.
    if not up_to_date:
        self.cache.fs.remove(self.service_path)

@contextmanager
def open(mode, authority, cache, update, service_path, up_to_date_check, local_path=None, **kwargs):
    '''

    Context manager for reading/writing from an archive and uploading on changes
    
    case: Remote file

        on open:
            
            if cache and cache up to date:
            
                use_cache = True
                return cache opener
            
            elif cache and cache out of date:

                delete cache
                use_cache = True
                return authority opener
            
            else:
            
                use_cache = False
                return authority opener

        on write:
            
            if use_cache:
            
                write to cache
                copy to authority

            else:
            
                write to authority

            update manager
    Parameters
    ----------
    authority : object
        
        :py:mod:`pyFilesystem` filesystem object to use as the authoritative, 
        up-to-date source for the archive

    cache : object

        :py:mod:`pyFilesystem` filesystem object to use as the cache. Default 
        ``None``.

    use_cache : bool

         update, service_pathh, up_to_date_check, **kwargs
    '''

    try:
        clear_outdated_cache_files(cache, service_path, up_to_date_check)
        use_cache = True
    except NoCacheError:
        use_cache = False

    fs_wrapper = MultiFS()
    fs_wrapper.addfs('authority', authority.fs)
    
    if use_cache:
        fs_wrapper.addfs('cache', cache.fs)
        fs_wrapper.setwritefs(cache.fs)

    else:
        fs_wrapper.setwritefs(authority.fs)

    yield fs_wrapper.open(mode, **kwargs)

    if use_cache:
        fs.utils.copyfile(cache.fs, service_path, authority.fs, service_path)
    
    update()


@contextmanager
def get_local_path(authority, cache, use_cache, update, service_path, up_to_date_check, **kwargs):
    '''
    Context manager for retrieving a system path for I/O and updating on changes    

    case: required local path

        on open:

            if cache and cache up to date:
                use_cache = True

                return cache path
            
            elif cache and cache out of date:
                delete cache
                use_cache = True

                download to cache
                return cache path
            
            else:
                use_cache = False

                create temporary file
                download authority to temp file
                return temp file

        on write:
            if use_cache:
                write to cache
                copy to authority
                update manager
            else:
                copy temp file to authority
                update manager 


    Parameters
    ----------
    authority : object
        
        :py:mod:`pyFilesystem` filesystem object to use as the authoritative, 
        up-to-date source for the archive
 
    cache : object

        :py:mod:`pyFilesystem` filesystem object to use as the cache. Default 
        ``None``.

    use_cache : bool

         update, service_pathh, up_to_date_check, **kwargs
    '''

    try:
        clear_outdated_cache_files(cache, service_path, up_to_date_check)
        use_cache = True
    except NoCacheError:
        use_cache = False

    fs_wrapper = MultiFS()
    fs_wrapper.addfs('authority', authority.fs)
    
    if use_cache:
        fs_wrapper.addfs('cache', cache.fs)

        tmp = None
        write_fs = cache.fs
        local_path = cache.fs.getsyspath(service_path)

    else:
        tmp = TempFS()
        tmp.makedir(
            fs.path.dirname(service_path),
            recursive=True,
            allow_recreate=True)
        write_fs = tmp
        local_path = tmp.getsyspath(service_path)

    fs.utils.copyfile(fs_wrapper, service_path, tmp, service_path)

    yield local_path

    if use_cache:
        fs.utils.copyfile(write_fs, service_path, cache, service_path)

    fs.utils.copyfile(write_fs, service_path, authority, service_path)

    if tmp:
        tmp.close()

    update()

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


