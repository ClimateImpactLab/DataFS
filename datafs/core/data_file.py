
import fs.utils
import fs.path
import tempfile
import shutil
import time
from fs.osfs import OSFS
from fs.multifs import MultiFS

from fs.errors import (ResourceLockedError)

from contextlib import contextmanager


# HELPER FUNCTIONS

def _close(filesys):

    closed = False

    for _ in range(5):
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
def _choose_read_fs(authority, cache, read_path, version_check, hasher):
    '''
    Context manager returning the appropriate up-to-date readable filesystem

    Use ``cache`` if it is a valid filessystem and has a file at
    ``read_path``, otherwise use ``authority``. If the file at
    ``read_path`` is out of date, update the file in ``cache`` before
    returning it.
    '''

    if cache and cache.fs.isfile(read_path):
        if version_check(hasher(cache.fs.open(read_path, 'rb'))):
            yield cache.fs

        elif authority.fs.isfile(read_path):
            fs.utils.copyfile(
                authority.fs,
                read_path,
                cache.fs,
                read_path)
            yield cache.fs

        else:
            _makedirs(authority.fs, fs.path.dirname(read_path))
            _makedirs(cache.fs, fs.path.dirname(read_path))
            yield cache.fs

    else:
        if not authority.fs.isfile(read_path):
            _makedirs(authority.fs, fs.path.dirname(read_path))

        yield authority.fs


@contextmanager
def _get_write_fs():
    '''
    Context manager returning a writable filesystem

    Use a temporary directory and clean on exit.

    .. todo::

        Evaluate options for using a cached memoryFS or streaming object
        instead of an OSFS(tmp). This could offer significant performance
        improvements. Writing to the cache is less of a problem since this
        would be done in any case, though performance could be improved by
        writing to an in-memory filesystem and then writing to both cache and
        auth.

    '''

    tmp = tempfile.mkdtemp()

    try:
        # Create a writeFS and path to the directory containing the archive
        write_fs = OSFS(tmp)

        try:

            yield write_fs

        finally:
            _close(write_fs)

    finally:
        shutil.rmtree(tmp)


@contextmanager
def _prepare_write_fs(read_fs, cache, read_path, readwrite_mode=True):
    '''
    Prepare a temporary filesystem for writing to read_path

    The file will be moved to write_path on close if modified.
    '''

    with _get_write_fs() as write_fs:

        # If opening in read/write or append mode, make sure file data is
        # accessible
        if readwrite_mode:

            if not write_fs.isfile(read_path):
                _touch(write_fs, read_path)

                if read_fs.isfile(read_path):
                    fs.utils.copyfile(
                        read_fs, read_path, write_fs, read_path)

        else:
            _touch(write_fs, read_path)

        yield write_fs


# AVAILABLE I/O CONTEXT MANAGERS

@contextmanager
def open_file(
        authority,
        cache,
        update,
        version_check,
        hasher,
        read_path,
        write_path=None,
        cache_on_write=False,
        mode='r',
        *args,
        **kwargs):
    '''

    Context manager for reading/writing an archive and uploading on changes

    Parameters
    ----------
    authority : object

        :py:mod:`pyFilesystem` filesystem object to use as the authoritative,
        up-to-date source for the archive

    cache : object

        :py:mod:`pyFilesystem` filesystem object to use as the cache. Default
        ``None``.

    use_cache : bool

         update, service_path, version_check, \*\*kwargs
    '''

    if write_path is None:
        write_path = read_path

    with _choose_read_fs(
            authority, cache, read_path, version_check, hasher) as read_fs:

        write_mode = ('w' in mode) or ('a' in mode) or ('+' in mode)

        if write_mode:

            readwrite_mode = (
                ('a' in mode) or (
                    ('r' in mode) and (
                        '+' in mode)))

            with _prepare_write_fs(
                    read_fs, cache, read_path, readwrite_mode) as write_fs:

                wrapper = MultiFS()
                wrapper.addfs('reader', read_fs)
                wrapper.setwritefs(write_fs)

                with wrapper.open(read_path, mode, *args, **kwargs) as f:

                    yield f

                info = write_fs.getinfokeys(read_path, 'size')
                if 'size' in info:
                    if info['size'] == 0:
                        return

                with write_fs.open(read_path, 'rb') as f:
                    checksum = hasher(f)

                if not version_check(checksum):
                    if (
                        cache_on_write or
                        (
                            cache
                            and (
                                fs.path.abspath(read_path) ==
                                fs.path.abspath(write_path))
                            and cache.fs.isfile(read_path)
                        )
                    ):
                        _makedirs(cache.fs, fs.path.dirname(write_path))
                        fs.utils.copyfile(
                            write_fs, read_path, cache.fs, write_path)

                        _makedirs(authority.fs, fs.path.dirname(write_path))
                        fs.utils.copyfile(
                            cache.fs, write_path, authority.fs, write_path)

                    else:
                        _makedirs(authority.fs, fs.path.dirname(write_path))
                        fs.utils.copyfile(
                            write_fs, read_path, authority.fs, write_path)

                    update(**checksum)

        else:

            with read_fs.open(read_path, mode, *args, **kwargs) as f:

                yield f


@contextmanager
def get_local_path(
        authority,
        cache,
        update,
        version_check,
        hasher,
        read_path,
        write_path=None,
        cache_on_write=False):
    '''
    Context manager for retrieving a system path for I/O and updating on change


    Parameters
    ----------
    authority : object

        :py:mod:`pyFilesystem` filesystem object to use as the authoritative,
        up-to-date source for the archive

    cache : object

        :py:mod:`pyFilesystem` filesystem object to use as the cache. Default
        ``None``.

    use_cache : bool

         update, service_path, version_check, \*\*kwargs
    '''

    if write_path is None:
        write_path = read_path

    with _choose_read_fs(
            authority, cache, read_path, version_check, hasher) as read_fs:

        with _prepare_write_fs(
                read_fs, cache, read_path, readwrite_mode=True) as write_fs:

            yield write_fs.getsyspath(read_path)

            if write_fs.isfile(read_path):

                info = write_fs.getinfokeys(read_path, 'size')
                if 'size' in info:
                    if info['size'] == 0:
                        return

                with write_fs.open(read_path, 'rb') as f:
                    checksum = hasher(f)

                if not version_check(checksum):

                    if (
                        cache_on_write or
                        (
                            cache
                            and (
                                fs.path.abspath(read_path) ==
                                fs.path.abspath(write_path))
                            and cache.fs.isfile(read_path)
                        )
                    ):

                        _makedirs(cache.fs, fs.path.dirname(write_path))
                        fs.utils.copyfile(
                            write_fs, read_path, cache.fs, write_path)

                        _makedirs(authority.fs, fs.path.dirname(write_path))
                        fs.utils.copyfile(
                            cache.fs, write_path, authority.fs, write_path)
                    else:
                        _makedirs(authority.fs, fs.path.dirname(write_path))
                        fs.utils.copyfile(
                            write_fs, read_path, authority.fs, write_path)
                    update(**checksum)

            else:
                raise OSError(
                    'Local file removed during execution. '
                    'Archive not updated.')
