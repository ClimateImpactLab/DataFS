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
import time

try:
    unicode
except NameError:
    unicode = str


def get_counter():
    '''
    Counts up. Ensure we don't have name collisions
    '''

    counter = random.randint(0,10000)
    while True:
        yield counter
        counter += 1

counter = get_counter()


@pytest.fixture(scope="module")
def api():
    '''
    Build an API connection for use in testing
    '''

    api = DataAPI(
         username='My Name',
         contact = 'my.email@example.com')

    manager = MongoDBManager(
        database_name = 'MyDatabase',
        table_name = 'DataFiles')

    api.attach_manager(manager)

    local = TempFS()
    api.attach_authority('local', local)

    return api

@pytest.fixture
def archive(api):
    '''
    Create a temporary archive for use in testing
    '''

    test_id = next(counter)

    archive_name = 'test_archive_{}'.format(test_id)

    api.create_archive(
        archive_name,
        metadata = dict(description = 'My test data archive #{}'.format(test_id)))

    return api.get_archive(archive_name)


class TestHashFunctions(object):

    def update_and_hash(self, arch, contents):
        
        f = tempfile.NamedTemporaryFile(delete=False)
        
        try:
            f.write(contents)
            f.close()

            alg, apihash = arch.api.hash_file(f.name)
            arch.update(f.name)

        finally:
            os.remove(f.name)

        return apihash

    def do_hashtest(self, arch, contents):

        contents = unicode(contents)

        direct = hashlib.md5(contents.encode('utf-8')).hexdigest()
        apihash = self.update_and_hash(arch, contents)

        assert direct == apihash, 'Manual hash "{}" != api hash "{}"'.format(direct, apihash)
        assert direct == arch.latest_hash, 'Manual hash "{}" != archive hash "{}"'.format(direct, arch.latest_hash)

        # Try uploading the same file
        apihash = self.update_and_hash(arch, contents)

        assert direct == apihash, 'Manual hash "{}" != api hash "{}"'.format(direct, apihash)
        assert direct == arch.latest_hash, 'Manual hash "{}" != archive hash "{}"'.format(direct, arch.latest_hash)

        # Update and test again!

        contents = unicode((os.linesep).join([contents, contents, 'line 3!' + contents]))

        direct = hashlib.md5(contents.encode('utf-8')).hexdigest()
        apihash = self.update_and_hash(arch, contents)

        with arch.open('rb') as f:
            current = f.read()

        assert contents == current, 'Latest updates "{}" !=  archive contents "{}"'.format(contents, current)

        assert direct == apihash, 'Manual hash "{}" != api hash "{}"'.format(direct, apihash)
        assert direct == arch.latest_hash, 'Manual hash "{}" != archive hash "{}"'.format(direct, arch.latest_hash)

        # Update and test a different way!

        contents = unicode((os.linesep).join([contents, 'more!!!', contents]))
        direct = hashlib.md5(contents.encode('utf-8')).hexdigest()

        with arch.open('wb+') as f:
            f.write(contents)

        with arch.open('rb') as f2:
            current = f2.read()

        assert contents == current, 'Latest updates "{}" !=  archive contents "{}"'.format(contents, current)

        assert direct == arch.latest_hash, 'Manual hash "{}" != archive hash "{}"'.format(direct, arch.latest_hash)


    def test_hash_functions(self, archive):
        self.do_hashtest(archive, '')
        self.do_hashtest(archive, 'another test')
        self.do_hashtest(archive, '9872387932487913874031713470304')
        self.do_hashtest(archive, os.linesep.join(['ajfdsaion','daf','adfadsffdadsf']))

