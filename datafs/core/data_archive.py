from __future__ import absolute_import

from datafs.core import data_file
from datafs.core.versions import BumpableVersion
from datafs._compat import string_types
from contextlib import contextmanager
from fs.osfs import OSFS
import fs.utils
import fs.path
import click
import os
import textwrap
import time


def _process_version(self, version):
    if not self.versioned and version is None:
        return None

    elif not self.versioned and version is not None:
        raise ValueError('Cannot specify version on an unversioned archive.')

    elif version is None:
        return self.get_default_version()

    elif isinstance(version, BumpableVersion):
        return version

    elif isinstance(version, string_types) and version == 'latest':
        return self.get_latest_version()

    elif isinstance(version, string_types):
        return BumpableVersion(version)


class DataArchive(object):

    def __init__(
            self,
            api,
            archive_name,
            authority_name,
            archive_path,
            versioned=True,
            default_version=None):

        self.api = api
        self.archive_name = archive_name

        self._authority_name = authority_name
        self._archive_path = archive_path

        self._versioned = versioned
        self._default_version = default_version

    def __repr__(self):
        return "<{} {}://{}>".format(self.__class__.__name__,
                                     self.authority_name, self.archive_name)

    @property
    def versioned(self):
        return self._versioned

    def get_latest_version(self):

        versions = self.get_versions()

        if len(versions) == 0:
            return None

        else:
            return max(versions)

    def get_versions(self):

        versions = self.get_history()

        if len(versions) == 0:
            return []

        elif not self.versioned:
            return [None]

        else:
            return sorted(map(BumpableVersion, set(
                [v['version'] for v in versions])))

    def get_default_version(self):

        if not self.versioned:
            return None

        versions = self.get_versions()

        if self._default_version is None or self._default_version == 'latest':
            if len(versions) == 0:
                return None

            return max(versions)

        matches = filter(
            lambda v: v == self._default_version,
            self.get_versions())

        if len(matches) > 0:
            return max(matches)

        raise ValueError('Archive "{}" version {} not found'.format(
            self.archive_name, self._default_version))

    def get_version_path(self, version=None):
        '''
        Returns a storage path for the archive and version

        If the archive is versioned, the version number is used as the file
        path and the archive path is the directory. If not, the archive path is
        used as the file path.

        Parameters
        ----------
        version : str or object
            Version number to use as file name on versioned archives (default
            latest unless ``default_version`` set)

        Examples
        --------

        .. code-block:: python

            >>> arch = DataArchive(None, 'arch', None, 'a1', versioned=False)
            >>> print(arch.get_version_path())
            a1
            >>>
            >>> ver = DataArchive(None, 'ver', None, 'a2', versioned=True)
            >>> print(ver.get_version_path('0.0.0'))
            a2/0.0
            >>>
            >>> print(ver.get_version_path('0.0.1a1'))
            a2/0.0.1a1
            >>>
            >>> print(ver.get_version_path('latest')) # doctest: +ELLIPSIS
            Traceback (most recent call last):
            ...
            AttributeError: 'NoneType' object has no attribute 'manager'

        '''

        version = _process_version(self, version)

        if self.versioned:
            return fs.path.join(self.archive_path, str(version))

        else:
            return self.archive_path

    @property
    def authority_name(self):
        return self._authority_name

    @property
    def authority(self):
        return self.api._authorities[self.authority_name]

    @property
    def archive_path(self):
        return self._archive_path

    def get_metadata(self):
        return self.api.manager.get_metadata(self.archive_name)

    def get_history(self):
        return self.api.manager.get_version_history(self.archive_name)

    def get_latest_hash(self):
        return self.api.manager.get_latest_hash(self.archive_name)

    def get_version_hash(self, version=None):
        version = _process_version(self, version)
        if self.versioned:

            if version is None:
                return None

            for ver in self.get_history():
                if BumpableVersion(ver['version']) == version:
                    return ver['checksum']

            raise ValueError(
                'Version "{}" not found in archive history'.format(version))

        else:
            return self.get_latest_hash()

    def update(
            self,
            filepath,
            cache=False,
            remove=False,
            bumpversion=None,
            prerelease=None,
            dependencies=None,
            metadata=None,
            message=None):
        '''
        Enter a new version to a DataArchive

        Parameters
        ----------

        filepath : str
            The path to the file on your local file system

        cache : bool
            Turn on caching for this archive if not already on before update

        remove : bool
            removes a file from your local directory

        bumpversion : str
            Version component to update on write if archive is versioned. Valid
            bumpversion values are 'major', 'minor', and 'patch', representing
            the three components of the strict version numbering system (e.g.
            "1.2.3"). If bumpversion is None the version number is not updated
            on write. Either bumpversion or prerelease (or both) must be a
            non-None value. If the archive is not versioned, bumpversion is
            ignored.

        prerelease : str
            Prerelease component of archive version to update on write if
            archive is versioned. Valid prerelease values are 'alpha' and
            'beta'. Either bumpversion or prerelease (or both) must be a
            non-None value. If the archive is not versioned, prerelease is
            ignored.

        metadata : dict
            Updates to archive metadata. Pass {key: None} to remove a key from
            the archive's metadata.
        '''

        if metadata is None:
            metadata = {}

        latest_version = self.get_latest_version()

        hashval = self.api.hash_file(filepath)

        checksum = hashval['checksum']
        algorithm = hashval['algorithm']

        if checksum == self.get_latest_hash():
            self.update_metadata(metadata)

            if remove and os.path.isfile(filepath):
                os.remove(filepath)

            return

        if self.versioned:
            if latest_version is None:
                latest_version = BumpableVersion()

            next_version = latest_version.bump(
                kind=bumpversion,
                prerelease=prerelease,
                inplace=False)

        else:
            next_version = None

        next_path = self.get_version_path(next_version)

        if cache:
            self.cache(next_version)

        if self.is_cached(next_version):
            self.authority.upload(filepath, next_path)
            self.api.cache.upload(filepath, next_path, remove=remove)

        else:
            self.authority.upload(filepath, next_path, remove=remove)

        self._update_manager(
            archive_metadata=metadata,
            version_metadata=dict(
                checksum=checksum,
                algorithm=algorithm,
                version=next_version,
                dependencies=dependencies,
                message=message))

    def _get_default_dependencies(self):
        '''
        Get default dependencies for archive

        Get default dependencies from requirements file or (if no requirements
        file) from previous version
        '''

        # Get default dependencies from requirements file
        default_dependencies = {
            k: v for k,
            v in self.api._default_versions.items() if k != self.archive_name}

        # If no requirements file or is empty:
        if len(default_dependencies) == 0:

            # Retrieve dependencies from last archive record
            history = self.get_history()

            if len(history) > 0:
                default_dependencies = history[-1].get('dependencies', {})

        return default_dependencies

    def _set_version_defaults(self, version_metadata):

        version_metadata['user_config'] = self.api.user_config

        if version_metadata.get('dependencies', None) is None:
            version_metadata['dependencies'] = self._get_default_dependencies()

    def _update_manager(self, archive_metadata=None, version_metadata=None):

        if archive_metadata is None:
            archive_metadata = {}

        if version_metadata is None:
            version_metadata = {}

        self._set_version_defaults(version_metadata)

        # update records in self.api.manager
        self.api.manager.update(self.archive_name, version_metadata)
        self.update_metadata(archive_metadata)

    def update_metadata(self, metadata):

        # just update records in self.api.manager

        self.api.manager.update_metadata(self.archive_name, metadata)

    # File I/O methods

    @contextmanager
    def open(
            self,
            mode='r',
            version=None,
            bumpversion=None,
            prerelease=None,
            dependencies=None,
            metadata=None,
            message=None,
            *args,
            **kwargs):
        '''
        Opens a file for read/write

        Parameters
        ----------
        mode : str
            Specifies the mode in which the file is opened (default 'r')

        version : str
            Version number of the file to open (default latest)

        bumpversion : str
            Version component to update on write if archive is versioned. Valid
            bumpversion values are 'major', 'minor', and 'patch', representing
            the three components of the strict version numbering system (e.g.
            "1.2.3"). If bumpversion is None the version number is not updated
            on write. Either bumpversion or prerelease (or both) must be a
            non-None value. If the archive is not versioned, bumpversion is
            ignored.

        prerelease : str
            Prerelease component of archive version to update on write if
            archive is versioned. Valid prerelease values are 'alpha' and
            'beta'. Either bumpversion or prerelease (or both) must be a
            non-None value. If the archive is not versioned, prerelease is
            ignored.

        metadata : dict
            Updates to archive metadata. Pass {key: None} to remove a key from
            the archive's metadata.


        args, kwargs sent to file system opener

        '''

        if metadata is None:
            metadata = {}

        latest_version = self.get_latest_version()
        version = _process_version(self, version)

        version_hash = self.get_version_hash(version)

        if self.versioned:

            if latest_version is None:
                latest_version = BumpableVersion()

            next_version = latest_version.bump(
                kind=bumpversion,
                prerelease=prerelease,
                inplace=False)

            msg = "Version must be bumped on write. " \
                "Provide bumpversion and/or prerelease."

            assert next_version > latest_version, msg

            read_path = self.get_version_path(version)
            write_path = self.get_version_path(next_version)

        else:
            read_path = self.archive_path
            write_path = self.archive_path
            next_version = None

        # version_check returns true if fp's hash is current as of read
        def version_check(chk):
            return chk['checksum'] == version_hash

        # Updater updates the manager with the latest version number
        def updater(checksum, algorithm):
            self._update_manager(
                archive_metadata=metadata,
                version_metadata=dict(
                    version=next_version,
                    dependencies=dependencies,
                    checksum=checksum,
                    algorithm=algorithm,
                    message=message))

        opener = data_file.open_file(
            self.authority,
            self.api.cache,
            updater,
            version_check,
            self.api.hash_file,
            read_path,
            write_path,
            mode=mode,
            *args,
            **kwargs)

        with opener as f:
            yield f

    @contextmanager
    def get_local_path(
            self,
            version=None,
            bumpversion=None,
            prerelease=None,
            dependencies=None,
            metadata=None,
            message=None):
        '''
        Returns a local path for read/write

        Parameters
        ----------
        version : str
            Version number of the file to retrieve (default latest)

        bumpversion : str
            Version component to update on write if archive is versioned. Valid
            bumpversion values are 'major', 'minor', and 'patch', representing
            the three components of the strict version numbering system (e.g.
            "1.2.3"). If bumpversion is None the version number is not updated
            on write. Either bumpversion or prerelease (or both) must be a
            non-None value. If the archive is not versioned, bumpversion is
            ignored.

        prerelease : str
            Prerelease component of archive version to update on write if
            archive is versioned. Valid prerelease values are 'alpha' and
            'beta'. Either bumpversion or prerelease (or both) must be a
            non-None value. If the archive is not versioned, prerelease is
            ignored.

        metadata : dict
            Updates to archive metadata. Pass {key: None} to remove a key from
            the archive's metadata.

        '''

        if metadata is None:
            metadata = {}

        latest_version = self.get_latest_version()
        version = _process_version(self, version)

        version_hash = self.get_version_hash(version)

        if self.versioned:

            if latest_version is None:
                latest_version = BumpableVersion()

            next_version = latest_version.bump(
                kind=bumpversion,
                prerelease=prerelease,
                inplace=False)

            msg = "Version must be bumped on write. " \
                "Provide bumpversion and/or prerelease."

            assert next_version > latest_version, msg

            read_path = self.get_version_path(version)
            write_path = self.get_version_path(next_version)

        else:
            read_path = self.archive_path
            write_path = self.archive_path
            next_version = None

        # version_check returns true if fp's hash is current as of read
        def version_check(chk):
            return chk['checksum'] == version_hash

        # Updater updates the manager with the latest version number
        def updater(checksum, algorithm):
            self._update_manager(
                archive_metadata=metadata,
                version_metadata=dict(
                    version=next_version,
                    dependencies=dependencies,
                    checksum=checksum,
                    algorithm=algorithm,
                    message=message))

        path = data_file.get_local_path(
            self.authority,
            self.api.cache,
            updater,
            version_check,
            self.api.hash_file,
            read_path,
            write_path)

        with path as fp:
            yield fp

    def download(self, filepath, version=None):
        '''
        Downloads a file from authority to local path

        1. First checks in cache to check if file is there and if it is, is it
           up to date
        2. If it is not up to date, it will download the file to cache
        '''

        version = _process_version(self, version)

        dirname, filename = os.path.split(
            os.path.abspath(os.path.expanduser(filepath)))

        assert os.path.isdir(dirname), 'Directory  not found: "{}"'.format(
            dirname)

        local = OSFS(dirname)

        version_hash = self.get_version_hash(version)

        # version_check returns true if fp's hash is current as of read
        def version_check(chk):
            return chk['checksum'] == version_hash

        if os.path.exists(filepath):
            if version_check(self.api.hash_file(filepath)):
                return

        read_path = self.get_version_path(version)

        with data_file._choose_read_fs(
                self.authority,
                self.api.cache,
                read_path,
                version_check,
                self.api.hash_file) as read_fs:

            fs.utils.copyfile(
                read_fs,
                read_path,
                local,
                filename)

    def log(self):

        history = self.get_history()

        outputs = []

        for i, record in enumerate(history):
            output = ''

            record['timestamp'] = time.strftime(
                '%a, %d %b %Y %H:%M:%S +0000',
                time.strptime(record['updated'], '%Y%m%d-%H%M%S'))

            checksum = (
                ' ({algorithm} {checksum})\nDate:      {timestamp}'.format(
                    **record))

            if self.versioned:
                output = output + '\n' + (
                    click.style(
                        'version {}'.format(record['version']) + checksum,
                        fg='green'))

            else:
                output = output + '\n' + (
                    click.style(
                        'update {}'.format(len(history) - i) + checksum,
                        fg='green'))

            for attr, val in sorted(record['user_config'].items()):
                output = output + '\n' + (
                    '{:<10} {}'.format(attr+':', val))

            if 'message' in record:
                wrapper = textwrap.TextWrapper(
                    initial_indent='    ',
                    subsequent_indent='    ',
                    width=66)

                output = output + '\n\n'
                output = output + '\n'.join(wrapper.wrap(record['message']))

            outputs.append(output)

        click.echo_via_pager('\n\n'.join(reversed(outputs)) + '\n')

    def delete(self):
        '''
        Delete the archive

        .. warning::

            Deleting an archive will erase all data and metadata permanently.
            For help setting user permissions, see
            :ref:`Administrative Tools <admin>`

        '''

        versions = self.get_versions()
        self.api.manager.delete_archive_record(self.archive_name)

        for version in versions:
            if self.authority.fs.exists(self.get_version_path(version)):
                self.authority.fs.remove(self.get_version_path(version))

            if self.api.cache:
                if self.api.cache.fs.exists(self.get_version_path(version)):
                    self.api.cache.fs.remove(self.get_version_path(version))

    def isfile(self, version=None, *args, **kwargs):
        '''
        Check whether the path exists and is a file
        '''
        version = _process_version(self, version)

        path = self.get_version_path(version)
        self.authority.fs.isfile(path, *args, **kwargs)

    def getinfo(self, version=None, *args, **kwargs):
        '''
        Return information about the path e.g. size, mtime
        '''
        version = _process_version(self, version)

        path = self.get_version_path(version)
        self.authority.fs.getinfo(path, *args, **kwargs)

    def desc(self, version=None, *args, **kwargs):
        '''
        Return a short descriptive text regarding a path
        '''
        version = _process_version(self, version)

        path = self.get_version_path(version)
        self.authority.fs.desc(path, *args, **kwargs)

    def exists(self, version=None, *args, **kwargs):
        '''
        Check whether a path exists as file or directory
        '''
        version = _process_version(self, version)

        path = self.get_version_path(version)
        self.authority.fs.exists(path, *args, **kwargs)

    def getmeta(self, version=None, *args, **kwargs):
        '''
        Get the value of a filesystem meta value, if it exists
        '''
        version = _process_version(self, version)

        path = self.get_version_path(version)
        self.authority.fs.getmeta(path, *args, **kwargs)

    def hasmeta(self, version=None, *args, **kwargs):
        '''
        Check if a filesystem meta value exists
        '''
        version = _process_version(self, version)

        path = self.get_version_path(version)
        self.authority.fs.hasmeta(path, *args, **kwargs)

    def is_cached(self, version=None):
        '''
        Set the cache property to start/stop file caching for this archive
        '''
        version = _process_version(self, version)

        if self.api.cache and self.api.cache.fs.isfile(
                self.get_version_path(version)):
            return True

        return False

    def cache(self, version=None):
        version = _process_version(self, version)

        if not self.api.cache:
            raise ValueError('No cache attached')

        if not self.api.cache.fs.isfile(self.get_version_path(version)):
            data_file._touch(self.api.cache.fs, self.get_version_path(version))

        assert self.api.cache.fs.isfile(
            self.get_version_path(version)), "Cache creation failed"

    def remove_from_cache(self, version=None):
        version = _process_version(self, version)

        if self.api.cache.fs.isfile(self.get_version_path(version)):
            self.api.cache.fs.remove(self.get_version_path(version))

    def get_dependencies(self, version=None):
        '''
        Parameters
        ----------
        version: str
            string representing version number whose dependencies you are
            looking up
        '''

        version = _process_version(self, version)
        history = self.get_history()

        for v in reversed(history):
            if BumpableVersion(v['version']) == version:
                return v['dependencies']

        raise ValueError('Version {} not found'.format(version))

    def set_dependencies(self, dependencies=None):

        if dependencies is None:
            dependencies = {}

        history = self.get_history()
        if len(history) == 0:
            raise ValueError('Cannot set dependencies on an empty archive')

        version_metadata = history[-1]

        version_metadata['dependencies'] = dependencies
        version_metadata['user_config'] = self.api.user_config

        self.api.manager.update(self.archive_name, version_metadata)

    def get_tags(self):
        '''
        Returns a list of tags for the archive
        '''

        return self.api.manager.get_tags(self.archive_name)

    def add_tags(self, *tags):
        '''
        Set tags for a given archive
        '''

        for tag in tags:
            assert isinstance(tag, string_types), 'tags must be strings'

        self.api.manager.add_tags(self.archive_name, tags)

    def delete_tags(self, *tags):
        '''

        Deletes tags for a given archive

        '''
        for tag in tags:
            assert isinstance(tag, string_types), 'tags must be strings'

        self.api.manager.delete_tags(self.archive_name, tags)
