
from __future__ import absolute_import
from datafs.core.data_api import DataAPI
import yaml
import os
import importlib

try:
    PermissionError
except NameError:
    from datafs.core.data_api import PermissionError

class Config(object):

    CONFIG_FILE_LIST = ['~/.datafs/config.yml', '/env/datafs/config.yml']
    API_CONSTRUCTOR = DataAPI

    def __init__(self):
        self.config = {}

    def read_config(self, additional_fps = []):

        for fp in map(os.path.expanduser, self.CONFIG_FILE_LIST+additional_fps):
            try:
                with open(fp, 'r') as y:
                    self.config.update(yaml.load(y))

            except IOError:
                pass

    def write_config(self, fp=None):

        read_fp = self.CONFIG_FILE_LIST[0]

        if fp is not None:
            read_fp = fp

        if not os.path.isdir(os.path.dirname(os.path.expanduser(read_fp))):
            os.makedirs(os.path.dirname(os.path.expanduser(read_fp)))

        with open(os.path.expanduser(read_fp), 'w+') as f:
            f.write(yaml.dump(self.config))

    def get_default_config_from_api(self, api):

        for kw in ['api', 'manager', 'authorities', 'cache']:
            self.config[kw] = self.config.get(kw, {})
        
            
        for kw in api.user_config.keys():
            self.config['api'][kw] = self.config['api'].get(kw, api.user_config[kw])


        manager_cfg = {
            'module': api.manager.__class__.__module__,
            'class': api.manager.__class__.__name__,
            'args': [],
            'kwargs': api.manager.config
        }

        for kw in ['module', 'class', 'args', 'kwargs']:
            self.config['manager'][kw] = self.config['manager'].get(kw, manager_cfg[kw])

        authorities_cfg = {
            service_name: {
                'module': service.fs.__class__.__module__,
                'class': service.fs.__class__.__name__,
                'args': [],
                'kwargs': {}
            }
        for service_name, service in api._authorities.items()}

        for service_name in authorities_cfg.keys():
            if service_name not in self.config['authorities']:
                self.config['authorities'][service_name] = {}

            for kw in ['module', 'class', 'args', 'kwargs']:
                self.config['authorities'][service_name][kw] = self.config['authorities'][service_name].get(kw, authorities_cfg[service_name][kw])

        if api.cache:
            cache_cfg = {
                'module': api.cache.fs.__class__.__module__,
                'class': api.cache.fs.__class__.__name__,
                'args': [],
                'kwargs': {}
            }

            for kw in ['module', 'class', 'args', 'kwargs']:
                self.config['cache'][kw] = self.config['cache'].get(kw, cache_cfg[kw])


    def generate_api_from_config(self):

        api = self.API_CONSTRUCTOR(**self.config['api'])

        if 'manager' in self.config:

            try:
                manager = self.generate_manager_from_config(self.config['manager'])
                api.attach_manager(manager)

            except PermissionError:
                pass

        for service_name, service_config in self.config.get('authorities', {}).items():

            try:
                service = self.generate_service_from_config(service_config)
                api.attach_authority(service_name, service)

            except PermissionError:
                pass

        if 'cache' in self.config:

            try:
                service = self.generate_service_from_config(self.config['cache'])
                api.attach_cache(service)

            except (PermissionError, KeyError):
                pass

        return api

    def generate_manager_from_config(self, manager_config):

        mgr_module = importlib.import_module(manager_config['module'])
        mgr_class = mgr_module.__dict__[manager_config['class']]

        manager = mgr_class(*manager_config['args'], **manager_config['kwargs'])

        return manager

    def generate_service_from_config(self, service_config):

        svc_module = importlib.import_module(service_config['module'])
        svc_class = svc_module.__dict__[service_config['class']]

        service = svc_class(*service_config['args'], **service_config['kwargs'])

        return service
