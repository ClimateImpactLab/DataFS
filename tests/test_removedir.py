
from __future__ import absolute_import

import os

from datafs._compat import u
from fs.tempfs import TempFS
from fs.errors import ResourceNotFoundError
import pytest


@pytest.mark.remove_dir
def test_delete_handling(api, auth1):

    cache = TempFS()
    api.attach_authority('auth1', auth1)
    api.attach_cache(cache)

    with open('test_file.txt', 'w+') as f:
        f.write(u'this is an upload test')

    var = api.create('archive1', authority_name='auth1', versioned=False)
    var.update('test_file.txt', cache=True)

    assert os.path.isfile(api.cache.fs.getsyspath('archive1'))

    var.update('test_file.txt', remove=True)
    assert not os.path.isfile('test_file.txt')

    var.delete()
    with pytest.raises(KeyError):
        api.get_archive('archive1')

    with pytest.raises(ResourceNotFoundError):
        f = api._authorities['auth1'].fs.open('archive1', 'r')

    with pytest.raises(ResourceNotFoundError):
        f = api.cache.fs.open('archive1', 'r')


@pytest.mark.remove_dir
def test_versioned_no_cache(api, auth1):

    api.attach_authority('auth1', auth1)

    with open('test_file1.txt', 'w+') as f:
        f.write(u'this is another upload test')

    assert os.path.isfile('test_file1.txt')

    var2 = api.create('archive2', authority_name='auth1', versioned=True)
    var2.update('test_file1.txt')

    assert var2.get_version_path() == 'archive2/0.0.1'

    var2.delete()
    with pytest.raises(KeyError):
        api.get_archive('archive2')

    with pytest.raises(ResourceNotFoundError):
        api._authorities['auth1'].fs.open('archive2' 'r')

    assert api.listdir('', authority_name='auth1') == []


@pytest.mark.remove_dir
def test_remove_dir_multi_versions_remove(api, auth1):

    cache = TempFS()
    api.attach_authority('auth1', auth1)
    api.attach_cache(cache)

    with open('test_file.txt', 'w+') as f:
        f.write(u'this is an upload test')

    var = api.create('archive1', authority_name='auth1', versioned=True)
    var.update('test_file.txt', cache=True)

    with var.open('w') as f:
        f.write(u'update update')

    assert len(var.get_versions()) == 2

    var.delete()

    with pytest.raises(KeyError):
        api.get_archive('archive1')

    with pytest.raises(ResourceNotFoundError):
        api._authorities['auth1'].fs.open('archive1', 'r')

    with pytest.raises(ResourceNotFoundError):
        api.cache.fs.open('archive1', 'r')

    assert api.listdir('', authority_name='auth1') == []


@pytest.mark.remove_dir
def test_multi_api(api1, api2, auth1, cache1, cache2, opener):
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

    with open('text_file.txt', 'w') as f:
        f.write(u'Stay Stoked')

    archive1 = api1.create('myArchive', versioned=False)
    archive1.update('text_file.txt')

    # Turn on caching in archive 1 and assert creation

    archive1.cache()
    assert archive1.is_cached() is True
    assert archive1.api.cache.fs is cache1

    with opener(archive1, 'w+') as f1:
        f1.write(u('Be happy and Stay Stoked'))

    assert auth1.isfile('myArchive')
    assert cache1.isfile('myArchive')

    archive2 = api2.get_archive('myArchive')

    # Turn on caching in archive 2 and assert creation
    archive2.cache()
    assert archive2.is_cached() is True
    assert archive2.api.cache.fs is cache2

    with archive2.open('r') as f:
        assert u(f.read()) == u'Be happy and Stay Stoked'

    archive2.delete()

    with pytest.raises(ResourceNotFoundError):
        api2._authorities['auth1'].fs.open('myArchive', 'r')

    with pytest.raises(ResourceNotFoundError):
        api2.cache.fs.open('myArchive', 'r')

    assert cache1.isfile('myArchive')

    with pytest.raises(ResourceNotFoundError):
        api1._authorities['auth1'].fs.open('myArchive', 'r')

    # using remove_from_cache because this archive is no longer in the manager
    archive1.remove_from_cache()

    with pytest.raises(ResourceNotFoundError):
        api1.cache.fs.open('myArchive', 'r')
