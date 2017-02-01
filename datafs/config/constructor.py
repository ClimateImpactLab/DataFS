
from datafs import DataAPI
import importlib
import fs
import pkgutil


class APIConstructor(object):

    @staticmethod
    def generate_api_from_config(config):

        for kw in ['user_config']:
            if kw not in config['api']:
                config['api'][kw] = {}

        api = DataAPI(**config['api']['user_config'])

        return api

    @classmethod
    def attach_manager_from_config(cls, api, config):

        if 'manager' in config:

            manager = cls._generate_manager(config['manager'])
            api.attach_manager(manager)

    @classmethod
    def attach_services_from_config(cls, api, config):

        for service_name, service_config in config.get(
                'authorities', {}).items():

            service = cls._generate_service(service_config)
            api.attach_authority(service_name, service)

    @classmethod
    def attach_cache_from_config(cls, api, config):

        if 'cache' in config:

            service = cls._generate_service(config['cache'])
            api.attach_cache(service)

    @staticmethod
    def _generate_manager(manager_config):
        '''
        Generate a manager from a manager_config dictionary

        Parameters
        ----------

        manager_config : dict
            Configuration with keys class, args, and kwargs
            used to generate a new datafs.manager object

        Returns
        -------

        manager : object
            datafs.managers.MongoDBManager or
            datafs.managers.DynamoDBManager object
            initialized with *args, **kwargs

        Examples
        --------

        Generate a dynamo manager:

        .. code-block:: python

        >>> mgr = APIConstructor._generate_manager({
        ...     'class': 'DynamoDBManager',
        ...     'kwargs': {
        ...         'table_name': 'data-from-yaml',
        ...         'session_args': {
        ...             'aws_access_key_id': "access-key-id-of-your-choice",
        ...             'aws_secret_access_key': "secret-key-of-your-choice"},
        ...         'resource_args': {
        ...             'endpoint_url':'http://localhost:8000/',
        ...             'region_name':'us-east-1'}
        ...     }
        ... })
        >>>
        >>> from datafs.managers.manager_dynamo import DynamoDBManager
        >>> assert isinstance(mgr, DynamoDBManager)
        >>>
        >>> 'data-from-yaml' in mgr.table_names
        False
        >>> mgr.create_archive_table('data-from-yaml')
        >>> 'data-from-yaml' in mgr.table_names
        True
        >>> mgr.delete_table('data-from-yaml')

        '''

        if 'class' not in manager_config:
            raise ValueError(
                'Manager not fully specified. Give '
                '"class:manager_name", e.g. "class:MongoDBManager".')

        mgr_class_name = manager_config['class']

        if mgr_class_name.lower()[:5] == 'mongo':
            from datafs.managers.manager_mongo import (
                MongoDBManager as mgr_class)

        elif mgr_class_name.lower()[:6] == 'dynamo':
            from datafs.managers.manager_dynamo import (
                DynamoDBManager as mgr_class)

        else:
            raise KeyError(
                'Manager class "{}" not recognized. Choose from {}'.format(
                    mgr_class_name, 'MongoDBManager or DynamoDBManager'))

        manager = mgr_class(
            *manager_config.get('args', []),
            **manager_config.get('kwargs', {}))

        return manager

    @staticmethod
    def _generate_service(service_config):
        '''
        Generate a service from a service_config dictionary

        Parameters
        ----------

        service_config : dict
            Configuration with keys service, args, and
            kwargs used to generate a new fs service
            object

        Returns
        -------

        service : object
            fs service object initialized with *args,
            **kwargs

        Examples
        --------

        Generate a temporary filesystem (no arguments
        required):

        .. code-block:: python

            >>> tmp = APIConstructor._generate_service(
            ...     {'service': 'TempFS'})
            ...
            >>> from fs.tempfs import TempFS
            >>> assert isinstance(tmp, TempFS)
            >>> import os
            >>> assert os.path.isdir(tmp.getsyspath('/'))
            >>> tmp.close()

        Generate a system filesystem in a temporary
        directory:

        .. code-block:: python

            >>> import tempfile
            >>> tempdir = tempfile.mkdtemp()
            >>> local = APIConstructor._generate_service(
            ...     {
            ...         'service': 'OSFS',
            ...         'args': [tempdir]
            ...     })
            ...
            >>> from fs.osfs import OSFS
            >>> assert isinstance(local, OSFS)
            >>> import os
            >>> assert os.path.isdir(local.getsyspath('/'))
            >>> local.close()
            >>> import shutil
            >>> shutil.rmtree(tempdir)

        Mock an S3 filesystem with moto:

        .. code-block:: python

            >>> import moto
            >>> m = moto.mock_s3()
            >>> m.start()
            >>> s3 = APIConstructor._generate_service(
            ...     {
            ...         'service': 'S3FS',
            ...         'args': ['bucket-name'],
            ...         'kwargs': {
            ...             'aws_access_key':'MY_KEY',
            ...             'aws_secret_key':'MY_SECRET_KEY'
            ...         }
            ...     })
            ...
            >>> from fs.s3fs import S3FS
            >>> assert isinstance(s3, S3FS)
            >>> m.stop()

        '''

        filesystems = []

        for _, modname, _ in pkgutil.iter_modules(fs.__path__):
            if modname.endswith('fs'):
                filesystems.append(modname)

        service_mod_name = service_config['service'].lower()

        assert_msg = 'Filesystem "{}" not found in pyFilesystem {}'.format(
            service_mod_name, fs.__version__)

        assert service_mod_name in filesystems, assert_msg

        svc_module = importlib.import_module('fs.{}'.format(service_mod_name))
        svc_class = svc_module.__dict__[service_config['service']]

        service = svc_class(*service_config.get('args', []),
                            **service_config.get('kwargs', {}))

        return service
