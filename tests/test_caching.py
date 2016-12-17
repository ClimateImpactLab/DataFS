
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

    api1.attach_authority('auth1', auth1)
    api1.attach_cache(cache1)

    api2.attach_authority('auth1', auth1)
    api2.attach_cache(cache2)

    assert len(
        api1._authorities) == 1, 'api1 has more than 1 authority: "{}"'.format(
        api1._authorities.keys())
    assert len(
        api2._authorities) == 1, 'api2 has more than 1 authority: "{}"'.format(
        api2._authorities.keys())

    arch1 = api1.create_archive('arch')
    arch1.cache = True
    assert arch1.cache is True
    assert arch1.api.cache.fs is cache1
    assert arch1.service_path == 'arch'
    assert arch1.api.cache.fs.isfile('arch')

    with cache1.open('arch', 'r') as f1:
        assert u(f1.read()) == u('')

    with arch1.open('w+') as f1:
        f1.write(u('test1'))

    assert auth1.isfile('arch')
    assert cache1.isfile('arch')

    arch2 = api2.get_archive('arch')
    arch2.cache = True
    assert arch2.cache

    assert cache2.isfile('arch')
    with cache2.open('arch', 'r') as f2:
        assert u(f2.read()) == u('')

    with arch1.open('r') as f1:
        with arch2.open('w+') as f2:
            f2.write(u('test2'))

        assert u(f1.read()) == u('test1')

    with arch1.open('r') as f1:
        assert u(f1.read()) == u('test2')
