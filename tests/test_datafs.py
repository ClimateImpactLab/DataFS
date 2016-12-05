#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_datafs
----------------------------------

Tests for `datafs` module.
"""

import pytest

from datafs.managers.manager_mongo import MongoDBManager
from datafs import DataAPI
from fs.tempfs import TempFS
from ast import literal_eval
import os
import tempfile
import shutil
import hashlib
import random

try:
    unicode
except NameError:
    unicode = str

'''
This is an example of a fixture/test pair

@pytest.fixture
def response():
    """Sample pytest fixture.
    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')

def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument.
    """
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string
'''

def get_counter():
    counter = 0
    while True:
        yield counter
        counter += 1

counter = get_counter()

@pytest.fixture(scope="module")
def api():

    api = DataAPI(
         username='My Name',
         contact = 'my.email@example.com')

    manager = MongoDBManager(
        database_name = 'MyDatabase',
        table_name = 'DataFiles')

    api.attach_manager(manager)

    local = TempFS()
    api.attach_authority('local', local)

@pytest.fixture
def archive(api):

    test_id = next(counter)

    archive_name = 'test_archive_{}'.format(test_id)

    api.create_archive(
        archive_name,
        metadata = dict(description = 'My test data archive #{}'.format(test_id)))

    return api.get_archive(archive_name)


def do_hashtest(arch, contents):
    direct = hashlib.md5(contents.encode('utf-8')).hexdigest()

    with tempfile.NamedTemporaryFile() as f:
        with open(f.name, 'w+') as w:
            w.write(contents)
        alg, apihash = api.hash_file(f.name)
        archive.update(f.name)
    
    assert direct == apihash, 'Manual hash "{}" != api hash "{}"'.format(direct, apihash)

    assert direct == arch.latest_hash, 'Manual hash "{}" != archive hash "{}"'.format(direct, archive.latest_hash)




def test_hash_functions(archive):
    do_hashtest(archive, unicode(''))
    do_hashtest(archive, unicode('another test'))
    do_hashtest(archive, unicode('9872387932487913874031713470304'))

