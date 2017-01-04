from __future__ import absolute_import
from datafs.managers.manager import BaseDataManager
from datafs.core.data_archive import DataArchive

import pytest


import xarray as xr
import numpy as np
import pandas as pd


np.random.seed(123)
times = pd.date_range('2000-01-01', '2001-12-31', name='time')
annual_cycle = np.sin(2 * np.pi * (times.dayofyear / 365.25 - 0.28))
base = 10 + 15 * annual_cycle.reshape(-1, 1)


tmin_values = base + 3 * np.random.randn(annual_cycle.size, 3)
tmax_values = base + 10 + 3 * np.random.randn(annual_cycle.size, 3)


ds = xr.Dataset({'tmin': (('time', 'location'), tmin_values), 
				 'tmax': (('time', 'location'), tmax_values)},
                {'time': times, 'location': ['IA', 'IN', 'IL']})




class TestVersionedMetadata(object):

	def test_versioned_metadata_open(self, api, opener):

		var = api.create_archive('my_archive')
		with open('test.txt', 'w+') as f:
			f.write(u'test test, this is a test')

		var.update('test.txt', remove=True, version='patch', dependencies={'arch1': '0.1.0', 'arch2': '0.2.0'})

		assert len(var.history[-1]['dependencies']) == 2

		with opener(var, 'w+', dependencies={'arch2': '0.1.2'}) as f:
			f.write(u'test and more test')


		assert var.history[-1]['dependencies']['arch2'] == '0.1.2'


		assert len(var.get_dependencies(version='0.0.1')) == 2


	def test_version_metadata_with_streaming(self,api,opener):

		var = api.create_archive('streaming_test')
		with var.get_local_path(bumpversion='patch', dependencies ={'arch1': '0.1.0', 'arch2': '0.2.0'}) as f:
			ds.to_netcdf(f)


		assert var.history[-1]['dependencies']['arch2'] == '0.1.2'

