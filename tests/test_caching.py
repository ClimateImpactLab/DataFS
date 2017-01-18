
from __future__ import absolute_import

import os

from datafs._compat import u


def test_delete_handling(api, auth1, cache):

    api.attach_authority('auth1', auth1)
    api.attach_cache(cache)

    with open('test_file.txt', 'w+') as f:
        f.write('this is an upload test')

    var = api.create('archive1', authority_name='auth1', versioned=False)
    var.update('test_file.txt', cache=True)

    assert os.path.isfile(api.cache.fs.getsyspath('archive1'))

    # try re-upload, with file deletion. Should be written to cache
    var.update('test_file.txt', remove=True)

    assert not os.path.isfile('test_file.txt')


def test_versioned_cache_handling(api, auth1, cache, opener):

    api.attach_authority('auth1', auth1)
    api.attach_cache(cache)

    with open('test_file.txt', 'w+') as f:
        f.write('this is an upload test')

    var = api.create('archive1', authority_name='auth1', versioned=True)
    var.update('test_file.txt', cache=True)

    assert os.path.isfile(
        api.cache.fs.getsyspath(var.get_version_path('latest')))

    var.remove_from_cache('latest')

    assert not os.path.isfile(
        api.cache.fs.getsyspath(var.get_version_path('latest')))

    # try re-upload, with file deletion. Should be written to cache
    var.update('test_file.txt', remove=True)

    assert not os.path.isfile('test_file.txt')

    with opener(var, 'w+') as f:
        f.write(u'this is a new test')

    var.cache('latest')

    assert var.is_cached('latest')
    assert var.is_cached(var.get_latest_version())
    assert not var.is_cached(var.get_versions()[0])

    assert os.path.isfile(
        api.cache.fs.getsyspath(var.get_version_path('latest')))

    var.remove_from_cache('latest')

    assert not os.path.isfile(
        api.cache.fs.getsyspath(var.get_version_path('latest')))

    var.cache(var.get_versions()[-2])

    assert os.path.isfile(
        api.cache.fs.getsyspath(var.get_version_path(var.get_versions()[-2])))

    var.remove_from_cache(var.get_versions()[-2])

    assert not os.path.isfile(
        api.cache.fs.getsyspath(var.get_version_path(var.get_versions()[-2])))


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

    archive1 = api1.create('myArchive', versioned=False)

    # Turn on caching in archive 1 and assert creation

    archive1.cache()
    assert archive1.is_cached() is True
    assert archive1.api.cache.fs is cache1
    assert cache1.isfile('myArchive')

    with cache1.open('myArchive', 'r') as f1:
        assert u(f1.read()) == u('')

    with opener(archive1, 'w+') as f1:
        f1.write(u('test1'))

    assert auth1.isfile('myArchive')
    assert cache1.isfile('myArchive')

    archive2 = api2.get_archive('myArchive')

    # Turn on caching in archive 2 and assert creation

    archive2.cache()
    assert archive2.is_cached() is True
    assert archive2.api.cache.fs is cache2
    assert cache2.isfile('myArchive')

    # Since we have not yet read from the authority, the
    # cache version has been 'touched' but is not up to date
    # with the archive's contents.

    with cache2.open('myArchive', 'r') as f2:
        assert u(f2.read()) == u('')

    # When we open the archive, the data is correct:

    with opener(archive2, 'r') as f2:
        assert u(f2.read()) == u('test1')

    # Furthermore, the cache has been updated:

    with cache2.open('myArchive', 'r') as f2:
        assert u(f2.read()) == u('test1')

    # If cached, the file is downloaded on open, then read
    # from the cache. Therefore, if the file is modified
    # by another user after the first user has downloaded
    # to the cache, a stale copy will be served.
    # No good way to guard against this since the file has
    # already been opened for reading. A lock on new writes
    # would not solve the problem, since that would have an
    # identical result.

    with opener(archive1, 'r') as f1:
        with opener(archive2, 'w+') as f2:
            f2.write(u('test2'))

        assert u(f1.read()) == u('test1')

    with opener(archive1, 'r') as f1:
        assert u(f1.read()) == u('test2')

    # Turn off caching in archive 2, and do the same test.
    # We expect the same result because the cached file is
    # already open in archive 1

    archive2.remove_from_cache()

    assert archive1.api.cache.fs.isfile('myArchive')
    assert not archive2.api.cache.fs.isfile('myArchive')

    with opener(archive1, 'r') as f1:
        with opener(archive2, 'w+') as f2:
            f2.write(u('test3'))

        assert u(f1.read()) == u('test2')

    with opener(archive1, 'r') as f1:
        assert u(f1.read()) == u('test3')

    # Turn off caching in archive 1, and do the same test.
    # This time, we expect the change made in archvie 2 to
    # be reflected in archive 1 because both are reading
    # and writing from the same authority.

    archive1.remove_from_cache()

    assert not archive1.api.cache.fs.isfile('myArchive')
    assert not archive2.api.cache.fs.isfile('myArchive')

    # NOTE: Here, archive 1 uses the method
    #       `archive.open('r')` explicitly. This test would
    #       not pass on
    #       `open(archive.get_local_path(), 'r')`, which is
    #       tested below.

    with archive1.open('r') as f1:
        with opener(archive2, 'w+') as f2:
            f2.write(u('test4'))

        assert u(f1.read()) == u('test4')

    with opener(archive1, 'r') as f1:
        assert u(f1.read()) == u('test4')

    # NOTE: Here, archive 1 uses the method
    #       `archive.get_local_path('r')` explicitly. This
    #       test would not pass on
    #       `archive.open('r')`, which is tested above.

    with archive1.get_local_path() as fp1:
        with open(fp1, 'r') as f1:
            with opener(archive2, 'w+') as f2:
                f2.write(u('test5'))

            assert u(f1.read()) == u('test4')

    with opener(archive1, 'r') as f1:
        assert u(f1.read()) == u('test5')

    # If we begin reading from the file, the file is locked,
    # and changes are not made until after the file has been
    # closed.

    first_char = u('t').encode('utf-8')

    with opener(archive1, 'r') as f1:
        f1.read(len(first_char))

        with opener(archive2, 'w+') as f2:
            f2.write(u('test6'))

        assert u(f1.read()) == u('est5')

    with opener(archive1, 'r') as f1:
        assert u(f1.read()) == u('test6')

    # This prevents problems in simultaneous read/write by
    # different parties. If someone is in the middle of
    # reading a file that is currently being written to,
    # they will not get garbage.

    test_str_1 = u('1234567890')
    test_str_2 = u('abcdefghij')

    str_length = len(test_str_1.encode('utf-8'))
    assert str_length == len(test_str_2.encode('utf-8'))

    with opener(archive1, 'w+') as f1:
        f1.write(test_str_1)

    with opener(archive1, 'r') as f1:

        assert len(archive1.get_history()) == 7
        assert u('12345') == u(f1.read(str_length / 2))

        with opener(archive2, 'w+') as f2:
            f2.write(test_str_2)

        assert len(archive1.get_history()) == 8
        assert u('67890') == u(f1.read())
