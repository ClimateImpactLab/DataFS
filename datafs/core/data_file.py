
import fs.utils
import fs.path
import tempfile
import shutil
import time
from fs.osfs import OSFS
from fs.multifs import MultiFS

from fs.errors import (ResourceLockedError, ResourceInvalidError)

from contextlib import contextmanager


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
    if cache.fs.exists(service_path) and cache.fs.hassyspath(service_path):
        up_to_date = latest_version_check(cache.fs.getsyspath(service_path))

    else:
        raise NoCacheError
    
    # Delete the file in the local cache if it is out of date.
    if not up_to_date:
        cache.fs.remove(service_path)

def determine_cache_state(authority, cache, service_path, latest_version_check):

    try:
        clear_outdated_cache_files(cache, service_path, latest_version_check)
        
        if (not cache.fs.isfile(service_path)) and authority.fs.isfile(service_path):
            cache.fs.makedir(
                fs.path.dirname(service_path),
                recursive=True,
                allow_recreate=True)

            fs.utils.copyfile(authority.fs, service_path, cache.fs, service_path)

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


def close(filesys):

    closed = False

    for i in range(5):
        try:
            filesys.close()
            closed = True
            break
        except ResourceLockedError as e:
            time.sleep(0.5)

    if not closed:
        raise e




@contextmanager
def open_file(authority, cache, update, service_path, latest_version_check, *args, **kwargs):
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

         update, service_path, latest_version_check, **kwargs
    '''

    use_cache = determine_cache_state(authority, cache, service_path, latest_version_check)
    fs_wrapper = create_downloader(authority, cache, use_cache)
    
    tmp = tempfile.mkdtemp()
    try:
        write_fs = OSFS(tmp)
        write_fs.makedir(
            fs.path.dirname(service_path),
            recursive=True,
            allow_recreate=True)

        fs_wrapper.setwritefs(write_fs)


        try:
            
            f = fs_wrapper.open(service_path, *args, **kwargs)
            yield f

            f.close()

            if write_fs.isfile(service_path):
                update(write_fs.getsyspath(service_path))

        finally:
            close(write_fs)

    finally:
        shutil.rmtree(tmp)

@contextmanager
def get_local_path(authority, cache, update, service_path, latest_version_check):
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

         update, service_path, latest_version_check, **kwargs
    '''

    
    use_cache = determine_cache_state(authority, cache, service_path, latest_version_check)
    fs_wrapper = create_downloader(authority, cache, use_cache)
    
    tmp = tempfile.mkdtemp()
    try:
        write_fs = OSFS(tmp)
        write_fs.makedir(
            fs.path.dirname(service_path),
            recursive=True,
            allow_recreate=True)


        if use_cache and cache.fs.isfile(service_path):
            fs.utils.movefile(cache.fs, service_path, write_fs, service_path)
        
        elif fs_wrapper.isfile(service_path):
            fs.utils.copyfile(fs_wrapper, service_path, write_fs, service_path)

        else:
            write_fs.createfile(service_path)

        local_path = write_fs.getsyspath(service_path)

        yield local_path

        try:
            if write_fs.isfile(service_path):
                if not latest_version_check(write_fs.getsyspath(service_path)):
                    update(write_fs.getsyspath(service_path))

            else:
                raise OSError('Local file removed during execution. Archive not updated.') 

        finally:

            close(write_fs)


    finally:
        shutil.rmtree(tmp)