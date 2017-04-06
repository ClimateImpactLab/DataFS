
from __future__ import absolute_import

import os

from datafs._compat import u
from fs.tempfs import TempFS 
from fs.errors import ResourceNotFoundError
import pytest



#test delete/noversion/delete after remove from local file system
def test_delete_handling(api, auth1):

    cache = TempFS()
    api.attach_authority('auth1', auth1)
    api.attach_cache(cache)

    with open('test_file.txt', 'w+') as f:
        f.write(u'this is an upload test')

    var = api.create('archive1', authority_name='auth1', versioned=False)
    var.update('test_file.txt', cache=True)

    assert os.path.isfile(api.cache.fs.getsyspath('archive1'))

    # try re-upload, with file deletion. Should be written to cache
    var.update('test_file.txt', remove=True)
    assert not os.path.isfile('test_file.txt')

    var.delete()
    with pytest.raises(KeyError):
        arch = api.get_archive('archive1')



def test_versioned_no_cache(api, auth1):

    api.attach_authority('auth1', auth1)

    with open('test_file1.txt', 'w+') as f:
        f.write(u'this is another upload test')

    assert os.path.isfile('test_file1.txt')

    var2 = api.create('archive2', authority_name='auth1', versioned=True)
    var2.update('test_file1.txt')


    assert var2.get_version_path() == 'archive2/0.0.1'

    assert os.path.isfile('test_file1.txt')


    #print var2.authority_name
    var2.delete()
    with pytest.raises(KeyError):
        arch = api.get_archive('archive2')


def test_remove_dir_multi_versions_remove_then_delete(api, auth1):

    api.attach_authority('auth1', auth1)

    with open('test_file.txt', 'w+') as f:
        f.write(u'this is an upload test')

    var = api.create('archive1', authority_name='auth1', versioned=True)
    var.update('test_file.txt')

    with var.open('w') as f:
        f.write(u'update update')
    # try re-upload, with file deletion. Should be written to cache
    assert len(var.get_versions()) == 2

    api.remove_dir('archive1',  'auth1', force=True)
    var.delete()

    with pytest.raises(KeyError):
        arch = api.get_archive('archive1')

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
    assert cache1.isfile('myArchive')

    with opener(archive1, 'w+') as f1:
        f1.write(u('Be happy and Stoked'))

    assert auth1.isfile('myArchive')
    assert cache1.isfile('myArchive')


    archive2 = api2.get_archive('myArchive')

    # Turn on caching in archive 2 and assert creation

    archive2.cache()
    assert archive2.is_cached() is True
    assert archive2.api.cache.fs is cache2
    assert cache2.isfile('myArchive')

    with archive2.open('r') as f:
        assert u(f.read()) == u'Be happy and Stoked'


    archive2.delete()

    assert cache1.isfile('myArchive')

    with pytest.raises(KeyError):
        with archive1.open('r') as f:
            f.read()

    with pytest.raises(ResourceNotFoundError):
        api1.remove_dir('myArchive', 'auth1')










