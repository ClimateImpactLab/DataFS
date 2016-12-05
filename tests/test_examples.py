
from __future__ import absolute_import

import doctest
import datafs
from examples import (local,multifs,s3,ondisk)


def test_local():
    doctest.testmod(local)


def test_multifs():
    doctest.testmod(multifs)


def test_s3():
    doctest.testmod(s3)


def test_ondisk():

    has_special_dependencies = False

    try:
        import xarray as xr
        import netCDF4
        has_special_dependencies = True

    except ImportError:
        pass

    if has_special_dependencies:
        doctest.testmod(ondisk)