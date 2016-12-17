
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

from tests.resources import string_types



def test_delete_handling(api, auth1, cache):

    api.attach_authority('auth1', auth1)
    api.attach_cache(cache)

    with open('test_file.txt') as f:
        f.write('this is an upload test')

    var = api.create_archive('archive1', authority_name='auth1')
    var.update('test_file.txt', cache=True)

    assert os.path.isfile(api.cache.fs.getsyspath('archive1'))

    # try re-upload, with file deletion. Should be written to cache
    var.update('test_file.txt', delete=True)

    assert not os.path.isfile('test_file.txt')


def test_multi_api(api, api2, auth1, cache):

    api1 = api

    api1.attach_authority('auth1', auth1)
    api1.attach_cache(cache)
    api2.attach_authority('auth1', auth1)
    api2.attach_cache(cache)

    arch1 = api1.create_archive('arch', authority_name='auth1')

    arch2 = api2.get_archive('arch')

    with arch2.open('w+') as f2:
        f2.write(unicode('test 1'))

    with arch1.open('r') as f1:
        with arch2.open('w+') as f2:
            f2.write(unicode('test2'))

        assert unicode(f1.read()) == unicode('test1')

    with arch1.open('r') as f1:
        assert unicode(f1.read()) == unicode('test2')
