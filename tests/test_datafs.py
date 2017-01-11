#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_datafs
----------------------------------

Tests for `datafs` module.
"""

from __future__ import absolute_import

import pytest

from datafs.managers.manager_mongo import MongoDBManager
from datafs.managers.manager_dynamo import DynamoDBManager
from datafs._compat import string_types, u
from datafs import DataAPI
from fs1.osfs import OSFS
from fs1.tempfs import TempFS
from fs1.s3fs import S3FS
from ast import literal_eval
import os
import tempfile
import shutil
import hashlib
import random
import itertools
import time
import boto
import moto

from six import b

try:
    PermissionError
except:
    class PermissionError(NameError):
        pass

def get_counter():
    '''
    Counts up. Ensure we don't have name collisions
    '''

    counter = random.randint(0, 10000)
    while True:
        yield counter
        counter += 1

counter = get_counter()


@pytest.yield_fixture(scope='function')
def archive(api):
    '''
    Create a temporary archive for use in testing
    '''

    test_id = next(counter)

    archive_name = 'test_archive_{}'.format(test_id)

    var = api.create(
        archive_name,
        metadata=dict(description='My test data archive #{}'.format(test_id)))

    try:
        yield var

    finally:
        var.delete()


string_tests = [
    '',
    'another test',
    '9872387932487913874031713470304',
    os.linesep.join(['ajfdsaion', 'daf', 'adfadsffdadsf'])]


class TestHashFunction(object):

    def update_and_hash(self, arch, contents):
        '''
        Save contents to archive ``arch`` and return the DataAPI's hash value
        '''

        f = tempfile.NamedTemporaryFile(delete=False)

        try:
            f.write(contents)
            f.close()

            apihash = arch.api.hash_file(f.name)['checksum']
            arch.update(f.name)

        finally:
            os.remove(f.name)

        return apihash

    @pytest.mark.parametrize('contents', string_tests)
    def test_hashfuncs(self, archive, contents):
        '''
        Run through a number of iterations of the hash functions
        '''

        contents = u(contents)

        direct = hashlib.md5(contents.encode('utf-8')).hexdigest()
        apihash = self.update_and_hash(archive, contents)

        assert direct == apihash, 'Manual hash "{}" != api hash "{}"'.format(
            direct, apihash)
        assert direct == archive.get_latest_hash(), 'Manual hash "{}" != archive hash "{}"'.format(
            direct, archive.get_latest_hash())

        # Try uploading the same file
        apihash = self.update_and_hash(archive, contents)

        assert direct == apihash, 'Manual hash "{}" != api hash "{}"'.format(
            direct, apihash)
        assert direct == archive.get_latest_hash(), 'Manual hash "{}" != archive hash "{}"'.format(
            direct, archive.get_latest_hash())

        # Update and test again!

        contents = u((os.linesep).join(
            [contents, contents, 'line 3!' + contents]))

        direct = hashlib.md5(contents.encode('utf-8')).hexdigest()
        apihash = self.update_and_hash(archive, contents)

        with archive.open('rb') as f:
            current = f.read()

        assert contents == current, 'Latest updates "{}" !=  archive contents "{}"'.format(
            contents, current)

        assert direct == apihash, 'Manual hash "{}" != api hash "{}"'.format(
            direct, apihash)
        assert direct == archive.get_latest_hash(), 'Manual hash "{}" != archive hash "{}"'.format(
            direct, archive.get_latest_hash())

        # Update and test a different way!

        contents = u((os.linesep).join([contents, 'more!!!', contents]))

        direct = hashlib.md5(contents.encode('utf-8')).hexdigest()

        with archive.open('wb+') as f:
            f.write(b(contents))

        with archive.open('rb') as f2:
            current = f2.read()

        assert contents == current, 'Latest updates "{}" !=  archive contents "{}"'.format(
            contents, current)

        assert direct == archive.get_latest_hash(), 'Manual hash "{}" != archive hash "{}"'.format(
            direct, archive.get_latest_hash())


class TestArchiveCreation(object):

    def test_create_archive(self, api):
        archive_name = 'test_recreation_error'

        api.create(archive_name, metadata={'testval': 'my test value'})
        var = api.get_archive(archive_name)

        testval = var.get_metadata()['testval']

        with pytest.raises(KeyError) as excinfo:
            api.create(archive_name)

        assert "already exists" in str(excinfo.value)

        api.create(
            archive_name,
            metadata={
                'testval': 'a different test value'},
            raise_on_err=False)
        var = api.get_archive(archive_name)

        assert testval == var.get_metadata()[
            'testval'], "Test archive was incorrectly updated!"

        var.update_metadata({'testval': 'a different test value'})

        assert var.get_metadata()[
            'testval'] == 'a different test value', "Test archive was not updated!"

        # Test archive deletion
        var.delete()

        with pytest.raises(KeyError) as excinfo:
            api.get_archive(archive_name)


    def test_api_locks(self, api, auth1, mgr_name):

        api.lock_manager()
        api.lock_authorities()

        with pytest.raises((PermissionError, NameError)) as excinfo:
            with prep_manager(mgr_name) as manager:
                api.attach_manager(manager)

        with pytest.raises((PermissionError, NameError)) as excinfo:
            api.attach_authority('auth', auth1)

