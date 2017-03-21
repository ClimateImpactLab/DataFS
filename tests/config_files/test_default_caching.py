
import pytest
import os

from datafs._compat import u


def write_archives(api):

    arch = api.create('archives/archive1.txt')

    with arch.open('w+', bumpversion='minor') as f:
        f.write(u('first version'))

    with arch.open('w+', bumpversion='minor', cache=False) as f:
        f.write(u('second version'))

    with arch.open('w+', bumpversion='minor', cache=True) as f:
        f.write(u('third version'))

    with arch.open('w+', bumpversion='minor') as f:
        f.write(u('fourth version'))

    return arch


@pytest.yield_fixture(scope='function')
def api_with_cached_archives(api_cached_by_default):
    '''
    Writes a number of archives to an api object that caches by default
    '''
    arch = write_archives(api_cached_by_default)

    yield api_cached_by_default

    arch.delete()


@pytest.mark.cache
def test_defaultcached_default_read(api_with_cached_archives):
    '''
    Tests cache write for archive when cached (:issue:`167`)
    '''

    assert os.path.isfile('tests/test1/archives/archive1.txt/0.1')
    assert os.path.isfile('tests/test2/archives/archive1.txt/0.1')


@pytest.mark.cache
def test_defaultcached_versioned_read(api_with_cached_archives):
    '''
    Tests caching when cache=False when cached (:issue:`167`)
    '''

    assert os.path.isfile('tests/test1/archives/archive1.txt/0.2')
    assert not os.path.isfile('tests/test2/archives/archive1.txt/0.2')


@pytest.mark.cache
def test_defaultcached_not_cached_read(api_with_cached_archives):
    '''
    Tests caching when cache=True when cached (:issue:`167`)
    '''

    assert os.path.isfile('tests/test1/archives/archive1.txt/0.3')
    assert os.path.isfile('tests/test2/archives/archive1.txt/0.3')


@pytest.mark.cache
def test_defaultcached_cached_read(api_with_cached_archives):
    '''
    Tests caching for latest version when cached (:issue:`167`)
    '''

    assert os.path.isfile('tests/test1/archives/archive1.txt/0.4')
    assert os.path.isfile('tests/test2/archives/archive1.txt/0.4')


@pytest.yield_fixture(scope='function')
def api_with_uncached_archives(api_with_cache):
    '''
    Writes a number of archives to an api object that does not cache by default
    '''

    arch = write_archives(api_with_cache)

    yield api_with_cache

    arch.delete()


@pytest.mark.cache
def test_uncached_default_read(api_with_uncached_archives):
    '''
    Tests cache write for archive when uncached (:issue:`167`)
    '''

    api_with_uncached_archives.cache_by_default = True

    assert os.path.isfile('tests/test1/archives/archive1.txt/0.1')
    assert not os.path.isfile('tests/test3/archives/archive1.txt/0.1')

    arch = api_with_uncached_archives.get_archive('archives/archive1.txt')

    with arch.open('r', version='0.1') as f:
        f.read()

    assert os.path.isfile('tests/test3/archives/archive1.txt/0.1')

    api_with_uncached_archives.cache_by_default = False


@pytest.mark.cache
def test_uncached_versioned_read(api_with_uncached_archives):
    '''
    Tests caching when cache=False when uncached (:issue:`167`)
    '''

    api_with_uncached_archives.cache_by_default = True

    assert os.path.isfile('tests/test1/archives/archive1.txt/0.2')
    assert not os.path.isfile('tests/test3/archives/archive1.txt/0.2')

    arch = api_with_uncached_archives.get_archive('archives/archive1.txt')

    with arch.open('r', version='0.2') as f:
        f.read()

    assert os.path.isfile('tests/test3/archives/archive1.txt/0.2')

    api_with_uncached_archives.cache_by_default = False


@pytest.mark.cache
def test_uncached_not_cached_read(api_with_uncached_archives):
    '''
    Tests caching when cache=True when uncached (:issue:`167`)
    '''

    api_with_uncached_archives.cache_by_default = True

    assert os.path.isfile('tests/test1/archives/archive1.txt/0.3')
    assert os.path.isfile('tests/test3/archives/archive1.txt/0.3')

    arch = api_with_uncached_archives.get_archive('archives/archive1.txt')

    with arch.open('r', version='0.3') as f:
        f.read()

    assert os.path.isfile('tests/test3/archives/archive1.txt/0.3')

    api_with_uncached_archives.cache_by_default = False


@pytest.mark.cache
def test_uncached_cached_read(api_with_uncached_archives):
    '''
    Tests caching for latest version when uncached (:issue:`167`)
    '''

    api_with_uncached_archives.cache_by_default = True

    assert os.path.isfile('tests/test1/archives/archive1.txt/0.4')
    assert not os.path.isfile('tests/test3/archives/archive1.txt/0.4')

    arch = api_with_uncached_archives.get_archive('archives/archive1.txt')

    with arch.open('r', version='0.4') as f:
        f.read()

    assert os.path.isfile('tests/test3/archives/archive1.txt/0.4')

    api_with_uncached_archives.cache_by_default = False
