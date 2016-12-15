
from __future__ import absolute_import
from datafs.core.data_api import DataAPI
import yaml
import os
import importlib
import click

try:
    PermissionError
except NameError:
    from datafs.core.data_api import PermissionError

class ConfigFile(object):

    def __init__(self, config_file = None):
        self.config = {'default-profile': 'default', 'profiles': {}}

        if config_file:
            self.config_file = config_file
        else:
            self.config_file = os.path.join(click.get_app_dir('datafs'), 'config.yml')

    def parse_configfile_contents(self, config):
        if not 'profiles' in config:
            config = {'profiles': {'default': config}}


        self.config['default-profile'] = config.get('default-profile', self.config['default-profile'])
        self.config['profiles'].update(config['profiles'])


    def read_config(self, contents=None):

        try:
            with open(self.config_file, 'r') as y:
                config = yaml.load(y)
                self.parse_configfile_contents(config)

        except IOError:
            pass

    def edit_config_file(self):
        self.write_config()

        click.edit(filename=self.config_file)
        

    def write_config(self, fp=None):

        read_fp = os.path.join(click.get_app_dir('datafs'), 'config.yml')

        if fp is not None:
            read_fp = fp

        if not os.path.isdir(os.path.dirname(os.path.expanduser(read_fp))):
            os.makedirs(os.path.dirname(os.path.expanduser(read_fp)))

        with open(os.path.expanduser(read_fp), 'w+') as f:
            f.write(yaml.dump(self.config))

    def get_profile_config(self, profile=None):
        if profile is None:
            profile = self.config['default-profile']

        if profile not in self.config['profiles']:
            self.config['profiles'][profile] = {}

        profile_config= self.config['profiles'][profile]

        for kw in ['api', 'manager', 'authorities', 'cache']:
            profile_config[kw] = profile_config.get(kw, {})

        return profile_config


    def get_default_config_from_api(self, api, profile=None):
        profile_config = self.get_profile_config(profile)

        
        if not 'user_config' in profile_config['api']:
            profile_config['api']['user_config'] = {}

        for kw in api.user_config.keys():
            profile_config['api']['user_config'][kw] = profile_config['api']['user_config'].get(kw, api.user_config[kw])
            
        
        if not 'constructor' in profile_config['api']:
            profile_config['api']['constructor'] = {
                'module': api.__class__.__module__, 
                'class': api.__class__.__name__
            }


        manager_cfg = {
            'module': api.manager.__class__.__module__,
            'class': api.manager.__class__.__name__,
            'args': [],
            'kwargs': api.manager.config
        }

        for kw in ['module', 'class', 'args', 'kwargs']:
            profile_config['manager'][kw] = profile_config['manager'].get(kw, manager_cfg[kw])

        authorities_cfg = {
            service_name: {
                'module': service.fs.__class__.__module__,
                'class': service.fs.__class__.__name__,
                'args': [],
                'kwargs': {}
            }
        for service_name, service in api._authorities.items()}

        for service_name in authorities_cfg.keys():
            if service_name not in profile_config['authorities']:
                profile_config['authorities'][service_name] = {}

            for kw in ['module', 'class', 'args', 'kwargs']:
                profile_config['authorities'][service_name][kw] = profile_config['authorities'][service_name].get(kw, authorities_cfg[service_name][kw])

        if api.cache:
            cache_cfg = {
                'module': api.cache.fs.__class__.__module__,
                'class': api.cache.fs.__class__.__name__,
                'args': [],
                'kwargs': {}
            }

            for kw in ['module', 'class', 'args', 'kwargs']:
                profile_config['cache'][kw] = profile_config['cache'].get(kw, cache_cfg[kw])


    def generate_api_from_config(self, profile=None):
        profile_config = self.get_profile_config(profile)

        for kw in ['user_config', 'constructor']:
            if not kw in profile_config['api']:
                profile_config['api'][kw] = {}

        try:
            api_mod = importlib.import_module(profile_config['api']['constructor']['module'])
            api_cls = api_mod.__dict__[profile_config['api']['constructor']['class']]

        except KeyError:
            api_cls = DataAPI

        api = api_cls(**profile_config['api']['user_config'])

        return api

    def attach_manager_from_config(self, api, profile=None):
        profile_config = self.get_profile_config(profile)

        if 'manager' in profile_config:

            try:
                manager = self._generate_manager(profile_config['manager'])
                api.attach_manager(manager)

            except (PermissionError, KeyError):
                pass

    def attach_services_from_config(self, api, profile=None):
        profile_config = self.get_profile_config(profile)

        for service_name, service_config in profile_config.get('authorities', {}).items():

            try:
                service = self._generate_service(service_config)
                api.attach_authority(service_name, service)

            except PermissionError:
                pass

    def attach_cache_from_config(self, api, profile=None):
        profile_config = self.get_profile_config(profile)

        if 'cache' in profile_config:

            try:
                service = self._generate_service(profile_config['cache'])
                api.attach_cache(service)

            except (PermissionError, KeyError):
                pass


    def _generate_manager(self, manager_config):

        mgr_module = importlib.import_module(manager_config['module'])
        mgr_class = mgr_module.__dict__[manager_config['class']]

        manager = mgr_class(*manager_config.get('args',[]), **manager_config.get('kwargs',{}))

        return manager

    def _generate_service(self, service_config):

        svc_module = importlib.import_module(service_config['module'])
        svc_class = svc_module.__dict__[service_config['class']]
        service = svc_class(*service_config.get('args',[]), **service_config.get('kwargs',{}))

        return service
