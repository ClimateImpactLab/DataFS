
import pytest
has_special_dependencies = False

try:
    import netCDF4
    import xarray as xr
    has_special_dependencies = True

except ImportError:
    pass


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

        with archive.get_local_path() as f:
            with xr.open_dataset(f) as ds:
                ds.load()

        assert (ds == airtemps*(2^i)).all()

        with archive.get_local_path() as f:
            (ds*2).to_netcdf(f)

        ds.close()


    airtemps.close()