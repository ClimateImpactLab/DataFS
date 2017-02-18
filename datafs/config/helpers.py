
from datafs.config.config_file import ConfigFile
from datafs.config.constructor import APIConstructor
from datafs._compat import open_filelike

import os
import re
import click


def _parse_requirement(requirement_line):

    # should we do archive name checking here? If the statement
    # doesn't split, the entire thing gets passed to api.create
    # or get_archive as the archive_name.

    version_stmt = map(lambda s: s.strip(), requirement_line.split('=='))

    if len(version_stmt) == 1:
        return version_stmt[0], None
    else:
        return version_stmt[0], version_stmt[1]


def get_api(
        profile=None,
        config_file=None,
        requirements=None):
    '''
    Generate a datafs.DataAPI object from a config profile

    ``get_api`` generates a DataAPI object based on a
    pre-configured datafs profile specified in your datafs
    config file.

    To create a datafs config file, use the command line
    tool ``datafs configure --helper`` or export an existing
    DataAPI object with
    :py:meth:`datafs.ConfigFile.write_config_from_api`

    Parameters
    ----------
    profile : str
        (optional) name of a profile in your datafs config
        file. If profile is not provided, the default
        profile specified in the file will be used.

    config_file : str or file
        (optional) path to your datafs configuration file.
        By default, get_api uses your OS's default datafs
        application directory.

    Examples
    --------

    The following specifies a simple API with a MongoDB
    manager and a temporary storage service:

    .. code-block:: python

        >>> try:
        ...   from StringIO import StringIO
        ... except ImportError:
        ...   from io import StringIO
        ...
        >>> import tempfile
        >>> tempdir = tempfile.mkdtemp()
        >>>
        >>> config_file = StringIO("""
        ... default-profile: my-data
        ... profiles:
        ...     my-data:
        ...         manager:
        ...             class: MongoDBManager
        ...             kwargs:
        ...                 database_name: 'MyDatabase'
        ...                 table_name: 'DataFiles'
        ...
        ...         authorities:
        ...             local:
        ...                 service: OSFS
        ...                 args: ['{}']
        ... """.format(tempdir))
        >>>
        >>> # This file can be read in using the datafs.get_api helper function
        ...
        >>>
        >>> api = get_api(profile='my-data', config_file=config_file)
        >>> api.manager.create_archive_table(
        ...     'DataFiles',
        ...     raise_on_err=False)
        >>>
        >>> archive = api.create(
        ...     'my_first_archive',
        ...     metadata = dict(description = 'My test data archive'),
        ...     raise_on_err=False)
        >>>
        >>> with archive.open('w+') as f:
        ...     res = f.write(u'hello!')
        ...
        >>> with archive.open('r') as f:
        ...     print(f.read())
        ...
        hello!
        >>>
        >>> # clean up
        ...
        >>> archive.delete()
        >>> import shutil
        >>> shutil.rmtree(tempdir)

    '''

    config = ConfigFile(config_file=config_file)
    config.read_config()

    if profile is None:
        profile = config.config['default-profile']

    profile_config = config.get_profile_config(profile)

    default_versions = {}

    if requirements is None:
        requirements = config.config.get('requirements', None)

    if requirements is not None and not os.path.isfile(requirements):
        for reqline in re.split(r'[\r\n;]+', requirements):
            if re.search(r'^\s*$', reqline):
                continue

            archive, version = _parse_requirement(reqline)
            default_versions[archive] = version

    else:
        if requirements is None:
            requirements = 'requirements_data.txt'

        if os.path.isfile(requirements):
            with open_filelike(requirements, 'r') as reqfile:
                for reqline in reqfile.readlines():
                    if re.search(r'^\s*$', reqline):
                        continue

                    archive, version = _parse_requirement(reqline)
                    default_versions[archive] = version

    api = APIConstructor.generate_api_from_config(profile_config)
    api._default_versions.update(default_versions)

    APIConstructor.attach_manager_from_config(api, profile_config)
    APIConstructor.attach_services_from_config(api, profile_config)
    APIConstructor.attach_cache_from_config(api, profile_config)

    return api


def _interactive_config(to_populate, prompts):
    '''
    Interactively populates to_populate with user-entered values

    Parameters
    ----------

    to_populate : dict
        Data dictionary to fill. Default values are taken from this dictionary.

    prompts : dict
        Keys and prompts to use when filling ``to_populate``
    '''

    for kw, prompt in prompts.items():
        to_populate[kw] = click.prompt(
            prompt,
            default=to_populate.get(kw))


def check_requirements(to_populate, prompts, helper=False):

    for kw, prompt in prompts.items():
        if helper:
            if kw not in to_populate:
                to_populate[kw] = click.prompt(prompt)
        else:
            msg = (
                'Required value "{}" not found. '
                'Use helper=True or the --helper '
                'flag for assistance.'.format(kw))

            assert kw in to_populate, msg


def to_config_file(api, config_file=None, profile='default'):

    config = ConfigFile(config_file=config_file, default_profile=profile)
    config.write_config_from_api(api, config_file=config_file, profile=profile)
