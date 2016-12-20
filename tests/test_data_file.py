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

from tests.resources import (
    string_types,
    u)

p = 'path/to/file/name.txt'


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
        def inner(
                auth,
                cache,
                update,
                service_path,
                version_check,
                hasher,
                *args,
                **kwargs):
            with data_file.get_local_path(auth, cache, update, service_path, version_check, hasher) as fp:
                assert isinstance(fp, string_types)

                with open(fp, *args, **kwargs) as f:
                    yield f

        return inner

    else:
        raise NameError('open_func "{}" not recognized'.format(open_func))


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


def test_file_io(local_auth, cache, opener):

    a1 = DataService(local_auth)
    csh = DataService(cache)

    # SUBTEST 1

    # Write data to a new system path. No files currently in csh.
    with opener(a1, csh, updater, p, get_checker(a1, p), DataAPI.hash_file, 'w+') as f:
        f.write(u('test data 1'))

    assert a1.fs.isfile(p)

    # We expect the contents to be written to the authority
    with open(a1.fs.getsyspath(p), 'r') as f:
        assert u('test data 1') == f.read()

    # We expect that the csh was left empty, because no file was present on
    # update.
    assert not os.path.isfile(csh.fs.getsyspath(p))

    # SUBTEST 2

    # Read from file and check contents multiple times

    for _ in range(5):

        with opener(a1, csh, updater, p, get_checker(a1, p), DataAPI.hash_file, 'r') as f:
            assert u('test data 1') == f.read()

        # We expect the contents to be left unchanged
        with open(a1.fs.getsyspath(p), 'r') as f:
            assert u('test data 1') == f.read()

        # We expect that the csh was left empty, because no file was present on
        # update.
        assert not os.path.isfile(csh.fs.getsyspath(p))

    # SUBTEST 3

    # Overwrite file and check contents again, this time with no csh

    with opener(a1, None, updater, p, get_checker(a1, p), DataAPI.hash_file, 'w+') as f:
        f.write(u('test data 2'))

    # We expect the contents to be written to the authority
    with open(a1.fs.getsyspath(p), 'r') as f:
        assert u('test data 2') == f.read()

    # We expect that the csh was left empty, because no file was present on
    # update.
    assert not os.path.isfile(csh.fs.getsyspath(p))

    # SUBTEST 4

    # Append to the file and test file contents

    for i in range(5):
        with opener(a1, csh, updater, p, get_checker(a1, p), DataAPI.hash_file, 'a') as f:
            f.write(u('appended data'))

        # We expect the contents to be left unchanged
        with open(a1.fs.getsyspath(p), 'r') as f:
            assert u('test data 2' + 'appended data' * (i + 1)) == f.read()

        # We expect that the csh was left empty, because no file was present on
        # update.
        assert not os.path.isfile(csh.fs.getsyspath(p))


def test_file_caching(local_auth, cache, opener):

    a1 = DataService(local_auth)
    csh = DataService(cache)

    # SUBTEST 1

    # Write data to a new system path. No files currently in csh.
    with opener(a1, csh, updater, p, get_checker(a1, p), DataAPI.hash_file, 'w+') as f:
        f.write(u('test data 1'))

    assert a1.fs.isfile(p)

    # We expect the contents to be written to the authority
    with open(a1.fs.getsyspath(p), 'r') as f:
        assert u('test data 1') == f.read()

    # We expect that the csh was left empty, because no file was present on
    # update.
    assert not os.path.isfile(csh.fs.getsyspath(p))

    # SUBTEST 2

    # Create a blank file in the csh location. Then test reading from
    # authority.

    # "touch" the csh file
    csh.fs.makedir(fs.path.dirname(p), recursive=True, allow_recreate=True)
    with open(csh.fs.getsyspath(p), 'w+') as f:
        f.write('')

    # Read file, and ensure we read from the authority
    with opener(a1, csh, updater, p, get_checker(a1, p), DataAPI.hash_file, 'r') as f:
        assert u('test data 1') == f.read()

    # We expect the contents to be left unchanged
    with open(a1.fs.getsyspath(p), 'r') as f:
        assert u('test data 1') == f.read()

    # We expect the csh to have been updated by read
    with open(csh.fs.getsyspath(p), 'r') as f:
        assert u('test data 1') == f.read()

    # SUBTEST 3

    # Write, and check consistency across authority and csh

    with opener(a1, csh, updater, p, get_checker(a1, p), DataAPI.hash_file, 'w+') as f:
        f.write(u('test data 2'))

    # We expect the contents to be written to the authority
    with open(a1.fs.getsyspath(p), 'r') as f:
        assert u('test data 2') == f.read()

    # We expect the contents to be written to the csh
    with open(csh.fs.getsyspath(p), 'r') as f:
        assert u('test data 2') == f.read()

    # SUBTEST 4

    # Manually modify the csh, then ensure data was replaced

    with open(csh.fs.getsyspath(p), 'w+') as f:
        f.write(u('erroneous csh data'))

    with opener(a1, csh, updater, p, get_checker(a1, p), DataAPI.hash_file, 'r') as f:
        assert u('test data 2') == f.read()

    # We expect authority to be unaffected
    with open(a1.fs.getsyspath(p), 'r') as f:
        assert u('test data 2') == f.read()

    # We expect the csh to be overwritten on read
    with open(csh.fs.getsyspath(p), 'r') as f:
        assert u('test data 2') == f.read()

    # SUBTEST 5

    # During read, manually modify the authority. Ensure updated data not
    # overwritten
    with opener(a1, csh, updater, p, get_checker(a1, p), DataAPI.hash_file, 'r') as f:

        # Overwrite a1
        with open(a1.fs.getsyspath(p), 'w+') as f2:
            f2.write(u('test data 3'))

        assert u('test data 2') == f.read()

    # We expect authority to reflect changed made
    with open(a1.fs.getsyspath(p), 'r') as f:
        assert u('test data 3') == f.read()

    # We expect the csh to be unaffected by write to authority
    with open(csh.fs.getsyspath(p), 'r') as f:
        assert u('test data 2') == f.read()

    # On second read, we expect the data to be updated
    with opener(a1, csh, updater, p, get_checker(a1, p), DataAPI.hash_file, 'r') as f:
        assert u('test data 3') == f.read()

    with open(a1.fs.getsyspath(p), 'r') as f:
        assert u('test data 3') == f.read()

    with open(csh.fs.getsyspath(p), 'r') as f:
        assert u('test data 3') == f.read()

    # SUBTEST 6

    # During write, manually modify the authority. Overwrite the authority
    # with new version.
    with opener(a1, csh, updater, p, get_checker(a1, p), DataAPI.hash_file, 'w+') as f:

        # Overwrite a1
        with open(a1.fs.getsyspath(p), 'w+') as f2:
            f2.write(u('test data 4'))

        f.write(u('test data 5'))

    # We expect authority to reflect the local change
    with open(a1.fs.getsyspath(p), 'r') as f:
        assert u('test data 5') == f.read()

    # We expect the csh to reflect the local change
    with open(csh.fs.getsyspath(p), 'r') as f:
        assert u('test data 5') == f.read()


def test_delete_handling(local_auth, cache):

    a1 = DataService(local_auth)
    csh = DataService(cache)

    # "touch" the csh file
    csh.fs.makedir(fs.path.dirname(p), recursive=True, allow_recreate=True)
    with open(csh.fs.getsyspath(p), 'w+') as f:
        f.write('')

    with data_file.get_local_path(a1, csh, updater, p, get_checker(a1, p), DataAPI.hash_file) as fp:
        with open(fp, 'w+') as f:
            f.write(u('test data 1'))

    assert a1.fs.isfile(p)

    # We expect authority to contain the new data
    with open(a1.fs.getsyspath(p), 'r') as f:
        assert u('test data 1') == f.read()

    # We expect csh to contain the new data
    with open(csh.fs.getsyspath(p), 'r') as f:
        assert u('test data 1') == f.read()

    # Test error handling of file deletion within a
    # get_local_path context manager

    with pytest.raises(OSError) as excinfo:

        with data_file.get_local_path(a1, csh, updater, p, get_checker(a1, p), DataAPI.hash_file) as fp:
            with open(fp, 'r') as f:
                assert u('test data 1') == f.read()

            with open(fp, 'w+') as f:
                f.write(u('test data 2'))

            with open(fp, 'r') as f:
                assert u('test data 2') == f.read()

            os.remove(fp)

    assert "removed during execution" in str(excinfo.value)

    # We expect authority to be unchanged
    with open(a1.fs.getsyspath(p), 'r') as f:
        assert u('test data 1') == f.read()

    # Unexpected things may have happened to the csh. But we expect it to be
    # back to normal after another read:
    with data_file.open_file(a1, csh, updater, p, get_checker(a1, p), DataAPI.hash_file, 'r') as f:
        assert u('test data 1') == f.read()

    with open(a1.fs.getsyspath(p), 'r') as f:
        assert u('test data 1') == f.read()

    with open(csh.fs.getsyspath(p), 'r') as f:
        assert u('test data 1') == f.read()
