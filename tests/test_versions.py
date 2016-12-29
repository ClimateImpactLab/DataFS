
from datafs._compat import string_types, u
from fs.errors import (ResourceNotFoundError, NoMetaError)
import pytest

def test_version_tracking(api1, auth1, opener):

    api1.attach_authority('auth', auth1)

    archive = api1.create_archive('test_versioned_archive')

    assert archive.versioned, "Archive not versioned, but should be by default"

    assert archive.latest_version is None
    assert len(archive.versions) == 0
    assert archive.latest_hash is None
    assert archive.get_version_hash() is None


    with opener(archive, 'w+', prerelease='alpha') as f:
        f.write(u('test content v0.0.1a1'))

    assert archive.latest_version == '0.0.1a1'
    assert len(archive.versions) == 1
    assert archive.latest_hash is not None
    assert archive.get_version_hash('0.0.1a1') == archive.latest_hash

    with opener(archive, 'r') as f:
        assert u(f.read()) == u('test content v0.0.1a1')


    with opener(archive, 'w+', bumpversion='minor', prerelease='beta') as f:
        f.write(u('test content v0.1b1'))

    assert archive.latest_version == '0.1b1'
    assert len(archive.versions) == 2
    assert archive.latest_hash is not None
    assert archive.get_version_hash('0.0.1a1') != archive.latest_hash
    assert archive.get_version_hash('0.1b1') == archive.latest_hash

    with opener(archive, 'r') as f:
        assert u(f.read()) == u('test content v0.1b1')

    with opener(archive, 'r', version='0.0.1a1') as f:
        assert u(f.read()) == u('test content v0.0.1a1')

    with opener(archive, 'a', version='0.0.1a1') as f:
        f.write(u(' --> v0.1.1'))

    assert archive.latest_version == '0.1.1'
    assert len(archive.versions) == 3
    assert archive.latest_hash is not None
    assert archive.get_version_hash('0.0.1a1') != archive.latest_hash
    assert archive.get_version_hash('0.1.1') == archive.latest_hash

    with opener(archive, 'r', version='0.0.1a1') as f:
        assert u(f.read()) == u('test content v0.0.1a1')

    with opener(archive, 'r') as f:
        assert u(f.read()) == u('test content v0.0.1a1 --> v0.1.1')

    with pytest.raises(ValueError) as excinfo:
        archive.get_version_hash('2.0')

    assert 'not found in archive history' in str(excinfo.value)


def test_versioned_fs_functions(api1, auth1, opener):

    api1.attach_authority('auth', auth1)

    archive = api1.create_archive('fs_funcs_test_archive')

    assert not archive.isfile()
    assert not archive.hasmeta()
    assert not archive.exists()
    assert archive.desc() is None

    with pytest.raises(ResourceNotFoundError):
        assert archive.getinfo()
    
    with pytest.raises(NoMetaError):
        assert archive.getmeta()

    with opener(archive, 'w+') as f:
        f.write(u('test content v0.0.1'))