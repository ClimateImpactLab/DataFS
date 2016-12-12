
import fs.utils
import fs.path
import tempfile
import shutil
import time
# from fs.osfs import OSFS
from fs.tempfs import TempFS
from fs.multifs import MultiFS

from fs.errors import (ResourceLockedError, ResourceInvalidError)

class NoCacheError(IOError):
    pass


def clear_outdated_cache_files(cache, service_path, latest_version_check):
    '''
    Check if file at service_path exists and is up to date

    Parameters
    ----------

    cache : object

        :py:mod:`fs` filesystem object to use a cache (default None)
    '''

    # Check the hash (if one exists) for a local version of the file
    if cache is None:
        raise NoCacheError

    # Check to see if there is a valid system file in the cache at the service 
    # path. If so, check if it is up to date. If not, raise NoCacheError.
    if cache.fs.exists(service_path) and cache.fs.hassyspath():
        up_to_date = latest_version_check(cache.fs.getsyspath(service_path))

    else:
        raise NoCacheError
    
    # Delete the file in the local cache if it is out of date.
    if not up_to_date:
        self.cache.fs.remove(self.service_path)

def determine_cache_state(cache, service_path, latest_version_check):

    try:
        clear_outdated_cache_files(cache, service_path, latest_version_check)
        use_cache = True
    except NoCacheError:
        use_cache = False

    return use_cache

def create_downloader(authority, cache, use_cache):


    fs_wrapper = MultiFS()
    fs_wrapper.addfs('authority', authority.fs)

    if use_cache:
        fs_wrapper.addfs('cache', cache.fs)

    return fs_wrapper

def create_writer(service_path):
    
    write_fs = TempFS()
    write_fs.makedir(
        fs.path.dirname(service_path),
        recursive=True,
        allow_recreate=True)

    return write_fs


def open(mode, authority, cache, update, service_path, latest_version_check, **kwargs):
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

         update, service_pathh, latest_version_check, **kwargs
    '''

    use_cache = determine_cache_state(cache, service_path, latest_version_check)
    fs_wrapper = create_downloader(authority, cache, use_cache):
    write_fs = create_writer(service_path)

    fs_wrapper.setwritefs(write_fs)

    yield fs_wrapper.open(mode, **kwargs)

    if write_fs.isfile(service_path):
        update(write_fs.getsyspath(service_path))

    write_fs.close()



def get_local_path(authority, cache, use_cache, update, service_path, latest_version_check, **kwargs):
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

         update, service_pathh, latest_version_check, **kwargs
    '''

    
    use_cache = determine_cache_state(cache, service_path, latest_version_check)
    fs_wrapper = create_downloader(authority, cache, use_cache):
    write_fs = create_writer(service_path)

    if use_cache and cache.fs.isfile(service_path):
        fs.utils.movefile(cache.fs, service_path, write_fs, service_path)
    else:
        fs.utils.copyfile(fs_wrapper, service_path, write_fs, service_path)

    local_path = write_fs.getsyspath(service_path)

    yield local_path

    if not latest_version_check(write_fs.getsyspath(service_path)):
        update(write_fs.getsyspath(service_path))
    
    write_fs.close()



'''
Usage
-----

in DataArchive(object):
    def get_local_path(self):
        current_latest_hash = self.latest_hash
        get_local_path(latest_version_check=lambda fp: api.hash_file(fp) == current_latest_hash)


with var.get_local_path() as fp:
    ds = xr.open_dataset(fp)
    other_var = do_something_complex(ds)

    other_var.to_netcdf('var2.nc')

    api.create_archive()

meanwhile...

do_some_update(var)

then...

