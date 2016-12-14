from __future__ import absolute_import

import fs.utils
import fs.path
import tempfile
import shutil
import time
import os

from fs.osfs import OSFS
from fs.multifs import MultiFS

from datafs import DataAPI
from datafs.core import data_file
from datafs.services.service import DataService

from contextlib import contextmanager

import pytest

try:
    u = unicode
    string_types = (unicode, str)
except NameError:
    u = str
    string_types = (str,)


def upload(tfs, fp):
    fs.utils.copyfile(tfs, fp, a, fp)

@pytest.yield_fixture(scope='function')
def auth1():
    t = tempfile.mkdtemp()
    f = OSFS(t)
    yield DataService(f)
    f.close()
    shutil.rmtree(t)


@pytest.yield_fixture(scope='function')
def cache():
    t = tempfile.mkdtemp()
    f = OSFS(t)
    yield DataService(f)
    f.close()
    shutil.rmtree(t)


@pytest.fixture
def opener(open_func):
    '''
    Fixture for opening files using each of the available methods

    open_func is parameterized in conftest.py
    '''

    if open_func == 'open_file':
        
        return data_file.open_file

    elif open_func == 'get_local_path':

        @contextmanager
        def inner(auth, cache, update, service_path, version_check, hasher, *args, **kwargs):
            with data_file.get_local_path(auth, cache, update, service_path, version_check, hasher) as fp:
                assert isinstance(fp, string_types)

                with open(fp, *args, **kwargs) as f:
                    yield f

        return inner

    else:
        raise NameError('open_func "{}" not recognized'.format(open_func))


p = 'path/to/file/name.txt'


def get_checker(service, service_path):
    if service.fs.isfile(service_path):
        checksum = DataAPI.hash_file(service.fs.getsyspath(service_path))
    else:
        checksum = None

    def check(chk):
        return chk == checksum

    return check

def updater(checksum, metadata={}):
    pass


def test_file_io(auth1, cache, opener):

    # SUBTEST 1

    # Write data to a new system path. No files currently in cache.
    with opener(auth1, cache, updater, p, get_checker(auth1, p), DataAPI.hash_file, 'w+') as f:
        f.write(u('test data 1'))

    assert auth1.fs.isfile(p)

    # We expect the contents to be written to the authority
    with open(auth1.fs.getsyspath(p), 'r') as f:
        assert u('test data 1') == f.read()

    # We expect that the cache was left empty, because no file was present on update.
    assert not os.path.isfile(cache.fs.getsyspath(p))



    # SUBTEST 2

    # Read from file and check contents multiple times

    for _ in range(5):
        
        with opener(auth1, cache, updater, p, get_checker(auth1, p), DataAPI.hash_file, 'r') as f:
            assert u('test data 1') == f.read()

        # We expect the contents to be left unchanged
        with open(auth1.fs.getsyspath(p), 'r') as f:
            assert u('test data 1') == f.read()

        # We expect that the cache was left empty, because no file was present on update.
        assert not os.path.isfile(cache.fs.getsyspath(p))


    # SUBTEST 3

    # Overwrite file and check contents again, this time with no cache

    with opener(auth1, None, updater, p, get_checker(auth1, p), DataAPI.hash_file, 'w+') as f:
        f.write(u('test data 2'))

    # We expect the contents to be written to the authority
    with open(auth1.fs.getsyspath(p), 'r') as f:
        assert u('test data 2') == f.read()

    # We expect that the cache was left empty, because no file was present on update.
    assert not os.path.isfile(cache.fs.getsyspath(p))


    # SUBTEST 4

    # Append to the file and test file contents

    for i in range(5):
        with opener(auth1, cache, updater, p, get_checker(auth1, p), DataAPI.hash_file, 'a') as f:
            f.write(u('appended data'))

        # We expect the contents to be left unchanged
        with open(auth1.fs.getsyspath(p), 'r') as f:
            assert u('test data 2' + 'appended data'*(i+1)) == f.read()

        # We expect that the cache was left empty, because no file was present on update.
        assert not os.path.isfile(cache.fs.getsyspath(p))



def test_file_caching(auth1, cache, opener):

    # SUBTEST 1

    # Write data to a new system path. No files currently in cache.
    with opener(auth1, cache, updater, p, get_checker(auth1, p), DataAPI.hash_file, 'w+') as f:
        f.write(u('test data 1'))

    assert auth1.fs.isfile(p)

    # We expect the contents to be written to the authority
    with open(auth1.fs.getsyspath(p), 'r') as f:
        assert u('test data 1') == f.read()

    # We expect that the cache was left empty, because no file was present on update.
    assert not os.path.isfile(cache.fs.getsyspath(p))


    # SUBTEST 2

    # Create a blank file in the cache location. Then test reading from authority.

    # "touch" the cache file
    cache.fs.makedir(fs.path.dirname(p),recursive=True,allow_recreate=True)
    with open(cache.fs.getsyspath(p), 'w+') as f:
        f.write('')

    # Read file, and ensure we read from the authority
    with opener(auth1, cache, updater, p, get_checker(auth1, p), DataAPI.hash_file, 'r') as f:
        assert u('test data 1') == f.read()

    # We expect the contents to be left unchanged
    with open(auth1.fs.getsyspath(p), 'r') as f:
        assert u('test data 1') == f.read()

    # We expect the cache to have been updated by read
    with open(cache.fs.getsyspath(p), 'r') as f:
        assert u('test data 1') == f.read()


    # SUBTEST 3

    # Write, and check consistency across authority and cache

    with opener(auth1, cache, updater, p, get_checker(auth1, p), DataAPI.hash_file, 'w+') as f:
        f.write(u('test data 2'))

    # We expect the contents to be written to the authority
    with open(auth1.fs.getsyspath(p), 'r') as f:
        assert u('test data 2') == f.read()

    # We expect the contents to be written to the cache
    with open(cache.fs.getsyspath(p), 'r') as f:
        assert u('test data 2') == f.read()


    # SUBTEST 4

    # Manually modify the cache, then ensure data was replaced

    with open(cache.fs.getsyspath(p), 'w+') as f:
        f.write(u('erroneous cache data'))

    with opener(auth1, cache, updater, p, get_checker(auth1, p), DataAPI.hash_file, 'r') as f:
        assert u('test data 2') == f.read()

    # We expect authority to be unaffected
    with open(auth1.fs.getsyspath(p), 'r') as f:
        assert u('test data 2') == f.read()

    # We expect the cache to be overwritten on read
    with open(cache.fs.getsyspath(p), 'r') as f:
        assert u('test data 2') == f.read()


    # SUBTEST 5

    # During read, manually modify the authority. Ensure updated data not overwritten
    with opener(auth1, cache, updater, p, get_checker(auth1, p), DataAPI.hash_file, 'r') as f:

        # Overwrite auth1
        with open(auth1.fs.getsyspath(p), 'w+') as f2:
            f2.write(u('test data 3'))
        
        assert u('test data 2') == f.read()

    # We expect authority to reflect changed made
    with open(auth1.fs.getsyspath(p), 'r') as f:
        assert u('test data 3') == f.read()

    # We expect the cache to be unaffected by write to authority
    with open(cache.fs.getsyspath(p), 'r') as f:
        assert u('test data 2') == f.read()

    # On second read, we expect the data to be updated
    with opener(auth1, cache, updater, p, get_checker(auth1, p), DataAPI.hash_file, 'r') as f:
        assert u('test data 3') == f.read()

    with open(auth1.fs.getsyspath(p), 'r') as f:
        assert u('test data 3') == f.read()

    with open(cache.fs.getsyspath(p), 'r') as f:
        assert u('test data 3') == f.read()


    # SUBTEST 6

    # During write, manually modify the authority. Overwrite the authority with new version.
    with opener(auth1, cache, updater, p, get_checker(auth1, p), DataAPI.hash_file, 'w+') as f:

        # Overwrite auth1
        with open(auth1.fs.getsyspath(p), 'w+') as f2:
            f2.write(u('test data 4'))
        
        f.write(u('test data 5'))

    # We expect authority to reflect the local change
    with open(auth1.fs.getsyspath(p), 'r') as f:
        assert u('test data 5') == f.read()

    # We expect the cache to reflect the local change
    with open(cache.fs.getsyspath(p), 'r') as f:
        assert u('test data 5') == f.read()


def test_delete_handling(auth1, cache):

    # "touch" the cache file
    cache.fs.makedir(fs.path.dirname(p),recursive=True,allow_recreate=True)
    with open(cache.fs.getsyspath(p), 'w+') as f:
        f.write('')

    with data_file.get_local_path(auth1, cache, updater, p, get_checker(auth1, p), DataAPI.hash_file) as fp:
        with open(fp, 'w+') as f:
            f.write(u('test data 1'))

    assert auth1.fs.isfile(p)

    # We expect authority to contain the new data
    with open(auth1.fs.getsyspath(p), 'r') as f:
        assert u('test data 1') == f.read()

    # We expect cache to contain the new data
    with open(cache.fs.getsyspath(p), 'r') as f:
        assert u('test data 1') == f.read()


    # Test error handling of file deletion within a 
    # get_local_path context manager

    with pytest.raises(OSError) as excinfo:

        with data_file.get_local_path(auth1, cache, updater, p, get_checker(auth1, p), DataAPI.hash_file) as fp:
            with open(fp, 'r') as f:
                assert u('test data 1') == f.read()

            with open(fp, 'w+') as f:
                f.write(u('test data 2'))

            with open(fp, 'r') as f:
                assert u('test data 2') == f.read()

            os.remove(fp)
    
    assert "removed during execution" in str(excinfo.value)

    # We expect authority to be unchanged
    with open(auth1.fs.getsyspath(p), 'r') as f:
        assert u('test data 1') == f.read()

    # Unexpected things may have happened to the cache. But we expect it to be
    # back to normal after another read:
    with data_file.open_file(auth1, cache, updater, p, get_checker(auth1, p), DataAPI.hash_file, 'r') as f:
        assert u('test data 1') == f.read()

    with open(auth1.fs.getsyspath(p), 'r') as f:
        assert u('test data 1') == f.read()

    with open(cache.fs.getsyspath(p), 'r') as f:
        assert u('test data 1') == f.read()