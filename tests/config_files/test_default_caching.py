
import pytest
import os

from datafs._compat import u


@pytest.yield_fixture
def api_with_cached_archives(api_cached_by_default):

    arch = api_cached_by_default.create('archives/archive1.txt')

    with arch.open('w+', bumpversion='minor') as f:
        f.write(u('first version'))

    with arch.open('w+', bumpversion='minor', cache=False) as f:
        f.write(u('second version'))

    with arch.open('w+', bumpversion='minor', cache=True) as f:
        f.write(u('third version'))

    with arch.open('w+', bumpversion='minor') as f:
        f.write(u('fourth version'))

    yield api_cached_by_default

    arch.delete()


@pytest.mark.cache
def test_default_read(api_with_cached_archives):
    '''
    Tests cache write for explicitly versioned archive (:issue:`167`)
    '''

    assert os.path.isfile('tests/test1/archives/archive1.txt/0.1')
    assert os.path.isfile('tests/test2/archives/archive1.txt/0.1')


@pytest.mark.cache
def test_versioned_read(api_with_cached_archives):
    '''
    Tests caching when cache=False (:issue:`167`)
    '''

    assert os.path.isfile('tests/test1/archives/archive1.txt/0.2')
    assert not os.path.isfile('tests/test2/archives/archive1.txt/0.2')


@pytest.mark.cache
def test_not_cached_read(api_with_cached_archives):
    '''
    Tests caching when cache=True(:issue:`167`)
    '''

    assert os.path.isfile('tests/test1/archives/archive1.txt/0.3')
    assert os.path.isfile('tests/test2/archives/archive1.txt/0.3')


@pytest.mark.cache
def test_cached_read(api_with_cached_archives):
    '''
    Tests caching for latest version (:issue:`167`)
    '''

    assert os.path.isfile('tests/test1/archives/archive1.txt/0.4')
    assert os.path.isfile('tests/test2/archives/archive1.txt/0.4')
