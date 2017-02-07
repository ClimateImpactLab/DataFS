
import pytest
from tests.resources import has_special_dependencies

if has_special_dependencies:
    import xarray as xr


@pytest.mark.big
@pytest.mark.skipif(
    not has_special_dependencies,
    reason='No modules netCDF4, xarray')
def test_xarray_upload(api1, auth1):
    # def test_xarray_upload(api1, local_auth):

    api1.attach_authority('auth', auth1)
    # api1.attach_authority('auth', local_auth)

    airtemps = xr.tutorial.load_dataset('air_temperature')

    archive = api1.create('big_archive')

    with archive.get_local_path() as f:
        airtemps.to_netcdf(f)

    for i in range(2):

        # try reading from the archive
        with archive.get_local_path() as f:
            with xr.open_dataset(f) as ds:
                print(ds)

        assert len(archive.get_versions()) == i + 1

        # try reading from & doing math on the archive
        with archive.get_local_path() as f:
            with xr.open_dataset(f) as ds:
                ds = ds * 2

        assert len(archive.get_versions()) == i + 1

        # try dask read
        with archive.get_local_path() as f:
            with xr.open_dataset(f) as ds:
                air2 = ds.air * 2
                ds.load()
                assert (ds.air * 2 == air2).all()

        # try clearing file. we do not consider this an update.
        with archive.get_local_path() as f:
            with open(f, 'w+') as w:
                pass

        assert len(archive.get_versions()) == i + 1

        # try writing nothing. we do not consider this an update.
        with archive.get_local_path() as f:
            with open(f, 'w+') as w:
                w.write('')

        assert len(archive.get_versions()) == i + 1

        assert (ds.air == airtemps.air * (2**(i))).all()

        with archive.get_local_path() as f:
            ds['air'] = ds.air * 2
            ds.to_netcdf(f)

        assert len(archive.get_versions()) == i + 2

        ds.close()

    airtemps.close()

    assert len(archive.get_versions()) == i + 2

    # make sure old version is still ok too
    with archive.get_local_path(version='0.0.1') as f:
        with xr.open_dataset(f) as ds:
            assert (ds.air == airtemps.air).all()
