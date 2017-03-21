
import pytest
from datafs._compat import u


@pytest.mark.cache
def test_default_cache(api_with_cache):

    arch = api_with_cache.create('archives/achive1.txt')

    with arch.open('w+', bumpversion='minor') as f:
        f.write(u('first version'))

    with arch.open('w+', bumpversion='minor', cache=False) as f:
        f.write(u('second version'))

    with arch.open('w+', bumpversion='minor') as f:
        f.write(u('third version'))

    with arch.get_local_path() as f:
        assert 'test1' not in f.split('/')
        assert 'test2' in f.split('/')

    with arch.get_local_path(version='0.1') as f:
        assert 'test1' not in f.split('/')
        assert 'test2' in f.split('/')

    with arch.get_local_path(version='0.2') as f:
        assert 'test1' in f.split('/')
        assert 'test2' not in f.split('/')
