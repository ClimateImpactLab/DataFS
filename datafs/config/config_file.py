
from __future__ import absolute_import
from datafs._compat import open_filelike
import yaml
import os
import click


class ProfileNotFoundError(KeyError):
    pass


class ConfigFile(object):

    def __init__(self, config_file=None, default_profile='default'):
        self.default_profile = default_profile
        self.config = {
            'default-profile': self.default_profile,
            'requirements': None,
            'profiles': {}}

        if config_file:
            self.config_file = config_file
        else:
            self.config_file = os.path.join(
                click.get_app_dir('datafs'), 'config.yml')

    def parse_configfile_contents(self, config):
        if 'profiles' not in config:
            config = {'profiles': {'default': config}}

        self.default_profile = config.get(
            'default-profile', self.config['default-profile'])

        self.config['default-profile'] = self.default_profile

        self.config['requirements'] = config.get(
            'requirements', self.config['requirements'])

        self.config['profiles'].update(config['profiles'])

    def read_config(self):

        with open_filelike(self.config_file, 'r') as f:
            config = yaml.load(f)

        self.parse_configfile_contents(config)

    def edit_config_file(self):

        click.edit(filename=self.config_file)

    def write_config(self, fp=None):

        if fp is None:
            fp = os.path.join(click.get_app_dir('datafs'), 'config.yml')

        with open_filelike(fp, 'w+') as f:
            f.write(yaml.dump(self.config))

    def get_profile_config(self, profile=None):
        if profile is None:
            profile = self.default_profile

        if profile not in self.config['profiles']:
            raise ProfileNotFoundError(
                'Profile "{}" not found'.format(profile))

        profile_config = self.config['profiles'][profile]

        for kw in ['api', 'manager', 'authorities']:
            profile_config[kw] = profile_config.get(kw, {})

        return profile_config

    def get_config_from_api(self, api, profile=None):

        try:
            profile_config = self.get_profile_config(profile)
        except ProfileNotFoundError:

            self.config['profiles'][profile] = {
                'api': {}, 'manager': {}, 'authorities': {}}

            profile_config = self.config['profiles'][profile]

        if 'user_config' not in profile_config['api']:
            profile_config['api']['user_config'] = {}

        for kw in api.user_config.keys():
            profile_config['api']['user_config'][kw] = profile_config[
                'api']['user_config'].get(kw, api.user_config[kw])

        manager_cfg = {
            'class': api.manager.__class__.__name__,
            'args': [],
            'kwargs': api.manager.config
        }

        for kw in ['class', 'args', 'kwargs']:
            profile_config['manager'][kw] = profile_config[
                'manager'].get(kw, manager_cfg[kw])

        authorities_cfg = {}

        for service_name, service in api._authorities.items():

            authorities_cfg[service_name] = {
                'service': service.fs.__class__.__name__,
                'args': [],
                'kwargs': {}
            }

            if service.fs.hassyspath('/'):
                authorities_cfg[service_name]['args'] = [
                    service.fs.getsyspath('/')]

        for service_name in authorities_cfg.keys():
            if service_name not in profile_config['authorities']:
                profile_config['authorities'][service_name] = {}

            for kw in ['service', 'args', 'kwargs']:
                profile_config['authorities'][service_name][kw] = \
                    profile_config['authorities'][service_name].get(
                        kw, authorities_cfg[service_name][kw])

        if api.cache:
            cache_cfg = {
                'service': api.cache.fs.__class__.__name__,
                'args': [],
                'kwargs': {}
            }

            profile_config['cache'] = profile_config.get('cache', {})

            for kw in ['service', 'args', 'kwargs']:
                profile_config['cache'][kw] = profile_config[
                    'cache'].get(kw, cache_cfg[kw])

    def write_config_from_api(self, api, config_file=None, profile=None):
        '''
        Create/update the config file from a DataAPI object

        Parameters
        ----------

        api : object
            The :py:class:`datafs.DataAPI` object from which
            to create the config profile

        profile : str
            Name of the profile to use in the config file
            (default "default-profile")

        config_file : str or file
            Path or file in which to write config (default
            is your OS's default datafs application
            directory)

        Examples
        --------

        Create a simple API and then write the config to a
        buffer:

        .. code-block:: python

            >>> from datafs import DataAPI
            >>> from datafs.managers.manager_mongo import MongoDBManager
            >>> from fs.osfs import OSFS
            >>> from fs.tempfs import TempFS
            >>> import os
            >>> import tempfile
            >>> import shutil
            >>>
            >>> api = DataAPI(
            ...      username='My Name',
            ...      contact = 'me@demo.com')
            >>>
            >>> manager = MongoDBManager(
            ...     database_name = 'MyDatabase',
            ...     table_name = 'DataFiles')
            >>>
            >>> manager.create_archive_table(
            ...     'DataFiles',
            ...     raise_on_err=False)
            >>>
            >>> api.attach_manager(manager)
            >>>
            >>> tmpdir = tempfile.mkdtemp()
            >>> local = OSFS(tmpdir)
            >>>
            >>> api.attach_authority('local', local)
            >>>
            >>> # Create a StringIO object for the config file
            ...
            >>> try:
            ...   from StringIO import StringIO
            ... except ImportError:
            ...   from io import StringIO
            ...
            >>> conf = StringIO()
            >>>
            >>> config_file = ConfigFile(default_profile='my-api')
            >>> config_file.write_config_from_api(
            ...     api,
            ...     profile='my-api',
            ...     config_file=conf)
            >>>
            >>> print(conf.getvalue())   # doctest: +SKIP
            default-profile: my-api
            profiles:
              my-api:
                api:
                  user_config: {contact: me@demo.com, username: My Name}
                authorities:
                  local:
                    args: [...]
                    service: OSFS
                    kwargs: {}
                manager:
                  args: []
                  class: MongoDBManager
                  kwargs:
                    client_kwargs: {}
                    database_name: MyDatabase
                    table_name: DataFiles
            <BLANKLINE>
            >>> conf.close()
            >>> local.close()
            >>> shutil.rmtree(tmpdir)

        At this point, we can retrieve the api object from
        the configuration file:

        .. code-block:: python

            >>> try:
            ...   from StringIO import StringIO
            ... except ImportError:
            ...   from io import StringIO
            ...
            >>> conf = StringIO("""
            ... default-profile: my-api
            ... profiles:
            ...   my-api:
            ...     api:
            ...       user_config: {contact: me@demo.com, username: My Name}
            ...     authorities:
            ...       local:
            ...         args: []
            ...         service: TempFS
            ...         kwargs: {}
            ...     manager:
            ...       args: []
            ...       class: MongoDBManager
            ...       kwargs:
            ...         client_kwargs: {}
            ...         database_name: MyDatabase
            ...         table_name: DataFiles
            ... """)
            >>>
            >>> import datafs
            >>> from fs.tempfs import TempFS
            >>> api = datafs.get_api(profile='my-api', config_file=conf)
            >>>
            >>> cache = TempFS()
            >>> api.attach_cache(cache)
            >>>
            >>> conf2 = StringIO()
            >>>
            >>> config_file = ConfigFile(default_profile='my-api')
            >>> config_file.write_config_from_api(
            ...     api,
            ...     profile='my-api',
            ...     config_file=conf2)
            >>>
            >>> print(conf2.getvalue())   # doctest: +SKIP
            default-profile: my-api
            profiles:
              my-api:
                api:
                  user_config: {contact: me@demo.com, username: My Name}
                authorities:
                  local:
                    args: []
                    service: TempFS
                    kwargs: {}
                cache:
                    args: []
                    service: TempFS
                    kwargs: {}
                manager:
                  args: []
                  class: MongoDBManager
                  kwargs:
                    client_kwargs: {}
                    database_name: MyDatabase
                    table_name: DataFiles
            <BLANKLINE>
        '''

        if profile is None:
            profile = self.default_profile

        self.get_config_from_api(api, profile)
        self.write_config(config_file)
