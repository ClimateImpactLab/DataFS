#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_datafs
----------------------------------

Tests for `datafs` module.
"""

from __future__ import absolute_import

import pytest

from datafs._compat import u
from tests.resources import prep_manager
import os
import tempfile
import hashlib
import random

from six import b

try:
    PermissionError
except NameError:
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


def update_and_hash(arch, contents):
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
def test_hashfuncs(archive, contents):
    '''
    Run through a number of iterations of the hash functions
    '''

    contents = u(contents)

    direct = hashlib.md5(contents.encode('utf-8')).hexdigest()
    apihash = update_and_hash(archive, contents)

    assert direct == apihash, 'Manual hash "{}" != api hash "{}"'.format(
        direct, apihash)

    msg = (
        'Manual hash "{}"'.format(direct) +
        ' != archive hash "{}"'.format(archive.get_latest_hash()))
    assert direct == archive.get_latest_hash(), msg

    # Try uploading the same file
    apihash = update_and_hash(archive, contents)

    assert direct == apihash, 'Manual hash "{}" != api hash "{}"'.format(
        direct, apihash)

    msg = (
        'Manual hash "{}"'.format(direct) +
        ' != archive hash "{}"'.format(archive.get_latest_hash()))
    assert direct == archive.get_latest_hash(), msg

    # Update and test again!

    contents = u((os.linesep).join(
        [contents, contents, 'line 3!' + contents]))

    direct = hashlib.md5(contents.encode('utf-8')).hexdigest()
    apihash = update_and_hash(archive, contents)

    with archive.open('rb') as f:
        current = f.read()

    msg = 'Latest updates "{}" !=  archive contents "{}"'.format(
        contents, current)
    assert contents == current, msg

    assert direct == apihash, 'Manual hash "{}" != api hash "{}"'.format(
        direct, apihash)

    msg = (
        'Manual hash "{}"'.format(direct) +
        ' != archive hash "{}"'.format(archive.get_latest_hash()))
    assert direct == archive.get_latest_hash(), msg

    # Update and test a different way!

    contents = u((os.linesep).join([contents, 'more!!!', contents]))

    direct = hashlib.md5(contents.encode('utf-8')).hexdigest()

    with archive.open('wb+') as f:
        f.write(b(contents))

    with archive.open('rb') as f2:
        current = f2.read()

    msg = 'Latest updates "{}" !=  archive contents "{}"'.format(
        contents, current)
    assert contents == current, msg

    msg = (
        'Manual hash "{}"'.format(direct) +
        ' != archive hash "{}"'.format(archive.get_latest_hash()))
    assert direct == archive.get_latest_hash(), msg


def test_create_archive(api):
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

    msg = "Test archive was not updated!"
    assert var.get_metadata()['testval'] == 'a different test value', msg

    # Test archive deletion
    var.delete()

    with pytest.raises(KeyError):
        api.get_archive(archive_name)


def test_api_locks(api, local_auth):

    api.lock_manager()
    api.lock_authorities()

    with pytest.raises((PermissionError, NameError)):
        with prep_manager('mongo') as manager:
            api.attach_manager(manager)

    with pytest.raises((PermissionError, NameError)):
        api.attach_authority('auth', local_auth)
