
import fs.utils
import fs.path
import tempfile
import shutil
import time
from fs.osfs import OSFS
from fs.multifs import MultiFS

from fs.errors import (ResourceLockedError, ResourceInvalidError)

from contextlib import contextmanager


# HELPER FUNCTIONS

def _close(filesys):

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


def _makedirs(filesystem, path):
    filesystem.makedir(path, recursive=True, allow_recreate=True)


def _touch(filesystem, path):
    _makedirs(filesystem, fs.path.dirname(path))
    if not filesystem.isfile(path):
        filesystem.createfile(path)


# HELPER CONTEXT MANAGERS


@contextmanager
def _choose_read_fs(authority, cache, service_path, version_check, hasher):
    '''
    Context manager returning the appropriate up-to-date readable filesystem

    Use ``cache`` if it is a valid filessystem and has a file at
    ``service_path``, otherwise use ``authority``. If the file at
    ``service_path`` is out of date, update the file in ``cache`` before
    returning it.
    '''

    if cache and cache.fs.isfile(service_path):
        if version_check(hasher(cache.fs.open(service_path, 'rb'))):
            yield cache.fs

        elif authority.fs.isfile(service_path):
            fs.utils.copyfile(
                authority.fs,
                service_path,
                cache.fs,
                service_path)
            yield cache.fs

        else:
            _touch(authority.fs, service_path)
            _touch(cache.fs, service_path)
            yield cache.fs

    else:
        if not authority.fs.isfile(service_path):
            _touch(authority.fs, service_path)

        yield authority.fs


@contextmanager
def _choose_write_fs(cache, service_path):
    '''
    Context manager returning a writable filesystem

    Use the cache if the cache is a valid filessystem and caching is enabled for
    this archive, otherwise use a temporary directory and clean on exit.

    .. todo::

        Evaluate options for using a cached memoryFS or streaming object instead
        of an OSFS(tmp). This could offer significant performance improvements.
        Writing to the cache is less of a problem since this would be done in
        any case, though performance could be improved by writing to an
        in-memory filesystem and then writing to both cache and auth.

    '''

    if cache and cache.fs.isfile(service_path):

        yield cache.fs

    else:
        tmp = tempfile.mkdtemp()

        # Create a writeFS and path to the directory containing the archive
        write_fs = OSFS(tmp)

        yield write_fs

        _close(write_fs)
        shutil.rmtree(tmp)



@contextmanager
def _prepare_write_fs(read_fs, cache, service_path, readwrite_mode=True):

    with _choose_write_fs(cache, service_path) as write_fs:

        # If opening in read/write or append mode, make sure file data is
        # accessible
        if readwrite_mode:

            if not write_fs.isfile(service_path):
                _touch(write_fs, service_path)
                fs.utils.copyfile(
                    read_fs, service_path, write_fs, service_path)

        else:
            _touch(write_fs, service_path)

        yield write_fs


# AVAILABLE I/O CONTEXT MANAGERS

@contextmanager
def open_file(
        authority,
        cache,
        update,
        service_path,
        version_check,
        hasher,
        mode='r',
        *args,
        **kwargs):
    '''

    Context manager for reading/writing from an archive and uploading on changes

    Parameters
    ----------
    authority : object

        :py:mod:`pyFilesystem` filesystem object to use as the authoritative,
        up-to-date source for the archive

    cache : object

        :py:mod:`pyFilesystem` filesystem object to use as the cache. Default
        ``None``.

    use_cache : bool

         update, service_path, version_check, **kwargs
    '''

    with _choose_read_fs(authority, cache, service_path, version_check, hasher) as read_fs:

        write_mode = ('w' in mode) or ('a' in mode) or ('+' in mode)

        if write_mode:

            readwrite_mode = (
                ('a' in mode) or (
                    ('r' in mode) and (
                        '+' in mode)))

            with _prepare_write_fs(read_fs, cache, service_path, readwrite_mode) as write_fs:

                wrapper = MultiFS()
                wrapper.addfs('reader', read_fs)
                wrapper.setwritefs(write_fs)

                with wrapper.open(service_path, mode, *args, **kwargs) as f:

                    yield f

                with write_fs.open(service_path, 'rb') as f:
                    checksum = hasher(f)

                if not version_check(checksum):
                    fs.utils.copyfile(
                        write_fs, service_path, authority.fs, service_path)
                    update(checksum=checksum)

        else:

            with read_fs.open(service_path, mode, *args, **kwargs) as f:

                yield f


@contextmanager
def get_local_path(
        authority,
        cache,
        update,
        service_path,
        version_check,
        hasher):
    '''
    Context manager for retrieving a system path for I/O and updating on changes


    Parameters
    ----------
    authority : object

        :py:mod:`pyFilesystem` filesystem object to use as the authoritative,
        up-to-date source for the archive

    cache : object

        :py:mod:`pyFilesystem` filesystem object to use as the cache. Default
        ``None``.

    use_cache : bool

         update, service_path, version_check, **kwargs
    '''

    with _choose_read_fs(authority, cache, service_path, version_check, hasher) as read_fs:

        with _prepare_write_fs(read_fs, cache, service_path, readwrite_mode=True) as write_fs:

            yield write_fs.getsyspath(service_path)

            if write_fs.isfile(service_path):

                with write_fs.open(service_path, 'rb') as f:
                    checksum = hasher(f)

                if not version_check(checksum):
                    fs.utils.copyfile(
                        write_fs, service_path, authority.fs, service_path)
                    update(checksum=checksum)

            else:
                _touch(write_fs, service_path)
                raise OSError(
                    'Local file removed during execution. Archive not updated.')
