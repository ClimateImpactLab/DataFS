
from __future__ import absolute_import

import os
import fs.utils
import fs.path
from fs.osfs import OSFS


class DataService(object):

    def __init__(self, fs, api=None):
        self.fs = fs
        self.api = api

    def upload(self, filepath, service_path):
        local = OSFS(os.path.dirname(filepath))
        self.fs.makedir(
            fs.path.dirname(service_path),
            recursive=True,
            allow_recreate=True)
        fs.utils.copyfile(
            local,
            os.path.basename(filepath),
            self.fs,
            service_path)


class CachingService(DataService):
    def cache(self, authority, service_path):
        fs.utils.copyfile(
            authority.fs,
            service_path,
            self.fs,
            service_path,
            overwrite=True)
