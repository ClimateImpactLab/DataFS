from __future__ import absolute_import

import fs.utils
import fs.path
import tempfile
import shutil
import time
from fs.tempfs import TempFS
from fs.multifs import MultiFS
from datafs import DataAPI
from datafs.core.data_file import FileOpener, FilePathOpener
from datafs.services.service import DataService

import pytest

try:
    u = unicode
except NameError:
    u = str


def upload(tfs, fp):
    fs.utils.copyfile(tfs, fp, a, fp)

@pytest.yield_fixture
def temp():
    f = TempFS()
    yield DataService(f, DataAPI)
    f.close()

@pytest.fixture
def auth1(temp):
    return auth

@pytest.fixture
def auth2(temp):
    return auth

@pytest.fixture
def cache(temp):
    return cache

p = 'path/to/file/name.txt'

def test_file_caching(auth1, cache):

    with FileOpener('w+', auth1, cache, True, upload, p) as f:
        f.write(u('test data 1'))

    with open(auth1.fs.getsyspath(p), 'r') as f:
        assert u('test data 1') == f.read()

    with open(cache.fs.getsyspath(p), 'r') as f:
        assert u('test data 1') == f.read()

    with FileOpener('r', auth1, None, True, upload, p) as f:
        assert u('test data 1') == f.read()

    with open(auth1.fs.getsyspath(p), 'w+') as f:
        assert u('test data 1') == f.read()

    with open(cache.fs.getsyspath(p), 'r') as f:
        assert u('test data 1') == f.read()

    with FileOpener('r', auth1, None, True, upload, p) as f:
        assert u('test data 1') == f.read()


