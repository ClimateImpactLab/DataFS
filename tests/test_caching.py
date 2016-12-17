
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

from tests.resources import string_types, u


def test_delete_handling(api, auth1, cache):

    api.attach_authority('auth1', auth1)
    api.attach_cache(cache)

    with open('test_file.txt', 'w+') as f:
        f.write('this is an upload test')

    var = api.create_archive('archive1', authority_name='auth1')
    var.update('test_file.txt', cache=True)

    assert os.path.isfile(api.cache.fs.getsyspath('archive1'))

    # try re-upload, with file deletion. Should be written to cache
    var.update('test_file.txt', remove=True)

    assert not os.path.isfile('test_file.txt')


def test_multi_api(api1, api2, auth1, cache1, cache2):
    '''
    Test upload/download/cache operations with two users
    '''

    # Create two separate users. Each user connects to the 
    # same authority and the same manager table (apis are 
    # initialized with the same manager table but different 
    # manager instance objects). Each user has its own 
    # separate cache.

    api1.attach_authority('auth1', auth1)
    api1.attach_cache(cache1)

    api2.attach_authority('auth1', auth1)
    api2.attach_cache(cache2)

    archive1 = api1.create_archive('myArchive')
    
    # Turn on caching in archive 1 and assert creation
    
    archive1.cache = True
    assert archive1.cache is True
    assert archive1.api.cache.fs is cache1
    assert cache1.isfile('myArchive')

    with cache1.open('myArchive', 'r') as f1:
        assert u(f1.read()) == u('')

    with archive1.open('w+') as f1:
        f1.write(u('test1'))

    assert auth1.isfile('myArchive')
    assert cache1.isfile('myArchive')

    archive2 = api2.get_archive('myArchive')

    # Turn on caching in archive 2 and assert creation

    archive2.cache = True
    assert archive2.cache is True
    assert archive2.api.cache.fs is cache2
    assert cache2.isfile('myArchive')

    # Since we have not yet read from the authority, the 
    # cache version has been 'touched' but is not up to date 
    # with the archive's contents.

    with cache2.open('myArchive', 'r') as f2:
        assert u(f2.read()) == u('')

    # When we open the archive, the data is correct:

    with archive2.open('r') as f2:
        assert u(f2.read()) == u('test1')

    # Furthermore, the cache has been updated:

    with cache2.open('myArchive', 'r') as f2:
        assert u(f2.read()) == u('test1')
    

    # If cached, the file is downloaded on open, then read 
    # from the cache. Therefore, if the file is modified
    # by another user after the first user has downloaded
    # to the cache, a stale copy will be served.
    # No good way to guard against this since the file has 
    # already been opened for reading. A lock on new writes 
    # would not solve the problem, since that would have an 
    # identical result.

    with archive1.open('r') as f1:
        with archive2.open('w+') as f2:
            f2.write(u('test2'))

        assert u(f1.read()) == u('test1')

    with archive1.open('r') as f1:
        assert u(f1.read()) == u('test2')

    # Turn off caching in archive 2, and do the same test. 
    # We expect the same result because the cached file is 
    # already open in archive 1

    archive2.cache=False

    assert archive1.api.cache.fs.isfile('myArchive')
    assert not archive2.api.cache.fs.isfile('myArchive')

    with archive1.open('r') as f1:
        with archive2.open('w+') as f2:
            f2.write(u('test3'))

        assert u(f1.read()) == u('test2')

    with archive1.open('r') as f1:
        assert u(f1.read()) == u('test3')



    # Turn off caching in archive 1, and do the same test. 
    # This time, we expect the change made in archvie 2 to 
    # be reflected in archive 1 because both are reading 
    # and writing from the same authority.

    archive1.cache=False

    assert not archive1.api.cache.fs.isfile('myArchive')
    assert not archive2.api.cache.fs.isfile('myArchive')

    with archive1.open('r') as f1:
        with archive2.open('w+') as f2:
            f2.write(u('test4'))

        assert u(f1.read()) == u('test4')

    with archive1.open('r') as f1:
        assert u(f1.read()) == u('test4')


    # This presents a problem. If someone is in the middle 
    # of reading a file that is currently being written to, 
    # they will get garbage.

    test_str_1 = u('1234567890')
    test_str_2 = u('abcdefghij')

    str_length = len(test_str_1.encode('utf-8'))
    assert str_length == len(test_str_2.encode('utf-8'))

    with archive1.open('w+') as f1:
        f1.write(test_str_1)

    with archive1.open('r') as f1:

        assert len(archive1.versions) == 5
        assert u('12345') == u(f1.read(str_length/2))
        
        with archive2.open('w+') as f2:
            f2.write(test_str_2)

        assert len(archive1.versions) == 6
        assert u('67890') == u(f1.read())   # I expected this to fail

