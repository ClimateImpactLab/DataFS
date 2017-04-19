'''
Tests pushing what can reasonably be expected from users to the limits

Guidelines for writing tests in this module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


'''

from __future__ import absolute_import

import pytest
from datafs._compat import u


def test_archive_creation_naming_conventions(api):
    '''
    Addresses :issue:`220`
    '''

    arch = api.create('my/new/archive.txt')

    try:
        # Make sure we can get the archive:
        arch1 = api.get_archive('my/new/archive.txt')
        assert arch1 == arch

        # Make sure str/unicode isn't a problem:
        arch2 = api.get_archive(u('my/new/archive.txt'))
        assert arch2 == arch

        # Make sure leading slash isn't a problem:
        arch3 = api.get_archive('/my/new/archive.txt')
        assert arch3 == arch

        # Make sure authority name isn't a problem:
        arch4 = api.get_archive('filesys://my/new/archive.txt')
        assert arch4 == arch

    finally:
        arch.delete()


def test_archive_creation_with_authority(api):
    '''
    Addresses :issue:`220`
    '''

    arch = api.create('filesys://my/new/archive.txt')

    try:
        # Make sure we can get the archive:
        arch1 = api.get_archive('filesys://my/new/archive.txt')
        assert arch1 == arch

        # Make sure str/unicode isn't a problem:
        arch2 = api.get_archive(u('my/new/archive.txt'))
        assert arch2 == arch

        # Make sure leading slash isn't a problem:
        arch3 = api.get_archive('/my/new/archive.txt')
        assert arch3 == arch

        # Make sure authority name isn't a problem:
        arch4 = api.get_archive('filesys://my/new/archive.txt')
        assert arch4 == arch

        # Make sure the wrong authority name is a problem:
        with pytest.raises(ValueError):
            api.get_archive('localhost://my/new/archive.txt')

    finally:
        arch.delete()


def test_archive_creation_with_multiple_authorities(api_dual_auth):
    '''
    Addresses :issue:`220`
    '''

    arch = api_dual_auth.create('auth1://my/new/archive.txt')

    try:
        # Make sure we can get the archive:
        arch1 = api_dual_auth.get_archive('my/new/archive.txt')
        assert arch1 == arch

        # Make sure str/unicode isn't a problem:
        arch2 = api_dual_auth.get_archive(u('my/new/archive.txt'))
        assert arch2 == arch

        # Make sure leading slash isn't a problem:
        arch3 = api_dual_auth.get_archive('/my/new/archive.txt')
        assert arch3 == arch

        # Make sure authority name matters
        with pytest.raises(ValueError):
            api_dual_auth.get_archive('auth2://my/new/archive.txt')

        # Make sure authority name prefix isn't a problem:
        arch4 = api_dual_auth.get_archive('auth1://my/new/archive.txt')
        assert arch4 == arch

        # Make sure bad authority names are a problem:
        with pytest.raises(ValueError):
            api_dual_auth.get_archive('non_authority://my/new/archive.txt')

    finally:
        arch.delete()


def test_bad_archive_names(api):
    '''
    Addresses :issue:`235`
    '''

    with pytest.raises(ValueError):
        arch = api.create('auth1://my\\~$archive...txt')
        arch.delete()
