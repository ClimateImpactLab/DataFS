from __future__ import absolute_import

from datafs.services.service import DataService
from datafs.core.data_archive import DataArchive
from datafs._compat import open_filelike

import hashlib
import fnmatch
import re
import fs.path
from fs.osfs import OSFS

try:
    PermissionError
except NameError:
    class PermissionError(NameError):
        pass

_VALID_AUTHORITY_PATTERNS = r'[\w\-]+'


class DataAPI(object):

    DefaultAuthorityName = None

    _ArchiveConstructor = DataArchive

    def __init__(self, default_versions=None, **kwargs):

        if default_versions is None:
            default_versions = {}

        self.user_config = kwargs

        self._manager = None
        self._cache = None
        self._authorities = {}

        self.default_versions = default_versions

        self._authorities_locked = False
        self._manager_locked = False

    def attach_authority(self, service_name, service):

        if self._authorities_locked:
            raise PermissionError('Authorities locked')

        self._validate_authority_name(service_name)

        self._authorities[service_name] = DataService(service)

    def lock_authorities(self):
        self._authorities_locked = True

    def lock_manager(self):
        self._manager_locked = True

    def attach_cache(self, service):

        if service in self._authorities.values():
            raise ValueError('Cannot attach an authority as a cache')
        else:
            self._cache = DataService(service)

    @property
    def manager(self):
        return self._manager
    # set cache attr

    @property
    def cache(self):
        return self._cache
    # get the default athority setting

    @property
    def default_authority_name(self):

        if self.DefaultAuthorityName is not None:
            return self.DefaultAuthorityName

        if len(self._authorities) == 0:
            raise ValueError(
                'No authorities found. See attach_authority.')

        if len(self._authorities) > 1:
            raise ValueError(
                'Authority ambiguous. Set authority or DefaultAuthorityName.')
        # get the zeroth key
        return list(self._authorities.keys())[0]

    # Do we want to provide a method for setting authorities
    @property
    def default_authority(self):
        return self._authorities[self.default_authority_name]

    @property
    def default_versions(self):
        return self._default_versions

    @default_versions.setter
    def default_versions(self, default_versions):
        '''
        Set archive default read versions

        Parameters
        ----------
        default_versions: dict
            Dictionary of archive_name, version pairs. On read/download,
            archives in this dictionary will download the specified version
            by default. Before assignment, archive_names are checked and
            normalized.
        '''

        default_versions = {
            self._normalize_archive_name(arch)[1]: v
            for arch, v in default_versions.items()}

        self._default_versions = default_versions

    def attach_manager(self, manager):

        if self._manager_locked:
            raise PermissionError('Manager locked')

        self._manager = manager

    def create(
            self,
            archive_name,
            authority_name=None,
            versioned=True,
            raise_on_err=True,
            metadata=None,
            tags=None,
            helper=False):
        '''
        Create a DataFS archive

        Parameters
        ----------

        archive_name: str
            Name of the archive

        authority_name: str
            Name of the data service to use as the archive's data authority

        versioned: bool
            If true, store all versions with explicit version numbers (defualt)

        raise_on_err: bool
            Raise an error if the archive already exists (default True)

        metadata: dict
            Dictionary of additional archive metadata

        helper: bool
            If true, interactively prompt for required metadata (default False)


        '''

        authority_name, archive_name = self._normalize_archive_name(
            archive_name, authority_name=authority_name)

        if authority_name is None:
            authority_name = self.default_authority_name

        self._validate_archive_name(archive_name)

        if metadata is None:
            metadata = {}

        res = self.manager.create_archive(
            archive_name,
            authority_name,
            archive_path=archive_name,
            versioned=versioned,
            raise_on_err=raise_on_err,
            metadata=metadata,
            user_config=self.user_config,
            tags=tags,
            helper=helper)

        return self._ArchiveConstructor(
            api=self,
            **res)

    def get_archive(self, archive_name, default_version=None):
        '''
        Retrieve a data archive

        Parameters
        ----------

        archive_name: str
            Name of the archive to retrieve

        default_version: version
            str or :py:class:`~distutils.StrictVersion` giving the default
            version number to be used on read operations

        Returns
        -------
        archive: object
            New :py:class:`~datafs.core.data_archive.DataArchive` object

        Raises
        ------

        KeyError:
            A KeyError is raised when the ``archive_name`` is not found

        '''

        auth, archive_name = self._normalize_archive_name(archive_name)

        res = self.manager.get_archive(archive_name)

        if default_version is None:
            default_version = self._default_versions.get(archive_name, None)

        if (auth is not None) and (auth != res['authority_name']):
            raise ValueError(
                'Archive "{}" not found on {}.'.format(archive_name, auth) +
                ' Did you mean "{}://{}"?'.format(
                    res['authority_name'], archive_name))

        return self._ArchiveConstructor(
            api=self,
            default_version=default_version,
            **res)

    def batch_get_archive(self, archive_names, default_versions=None):
        '''
        Batch version of :py:meth:`~DataAPI.get_archive`

        Parameters
        ----------

        archive_names: list

            Iterable of archive names to retrieve

        default_versions: str, object, or dict

            Default versions to assign to each returned archive. May be a dict
            with archive names as keys and versions as values, or may be a
            version, in which case the same version is used for all archives.
            Versions must be a strict version number string, a
            :py:class:`~distutils.version.StrictVersion`, or a
            :py:class:`~datafs.core.versions.BumpableVersion` object.

        Returns
        -------

        archives: list

            List of :py:class:`~datafs.core.data_archive.DataArchive` objects.
            If an archive is not found, it is omitted (``batch_get_archive``
            does not raise a ``KeyError`` on invalid archive names).

        '''

        # toss prefixes and normalize names
        archive_names = map(
            lambda arch: self._normalize_archive_name(arch)[1],
            archive_names)

        responses = self.manager.batch_get_archive(archive_names)

        archives = {}

        if default_versions is None:
            default_versions = {}

        for res in responses:
            res['archive_name'] = self._normalize_archive_name(
                res['archive_name'])

            archive_name = res['archive_name']

            if hasattr(default_versions, 'get'):

                # Get version number from default_versions or
                # self._default_versions if key not present.
                default_version = default_versions.get(
                    archive_name,
                    self._default_versions.get(archive_name, None))

            else:
                default_version = default_versions

            archive = self._ArchiveConstructor(
                api=self,
                default_version=default_version,
                **res)

            archives[archive_name] = archive

        return archives

    def listdir(self, location, authority_name=None):
        '''
        List archive path components at a given location

        .. Note ::

            When using listdir on versioned archives, listdir will provide the
            version numbers when a full archive path is supplied as the
            location argument. This is because DataFS stores the archive path
            as a directory and the versions as the actual files when versioning
            is on.

        Parameters
        ----------

        location: str

            Path of the "directory" to search

            `location` can be a path relative to the authority root (e.g
            `/MyFiles/Data`) or can include authority as a protocol (e.g.
            `my_auth://MyFiles/Data`). If the authority is specified as a
            protocol, the `authority_name` argument is ignored.

        authority_name: str

            Name of the authority to search (optional)

            If no authority is specified, the default authority is used (if
            only one authority is attached or if
            :py:attr:`DefaultAuthorityName` is assigned).

        Returns
        -------

        list

            Archive path components that exist at the given "directory"
            location on the specified authority

        Raises
        ------

        ValueError

            A ValueError is raised if the authority is ambiguous or invalid


        '''

        authority_name, location = self._normalize_archive_name(
            location,
            authority_name=authority_name)

        if authority_name is None:
            authority_name = self.default_authority_name

        return self._authorities[authority_name].fs.listdir(location)

    def filter(self, pattern=None, engine='path', prefix=None):
        '''

        Performs a filtered search on entire universe of archives
        according to pattern or prefix.

        Parameters
        ----------
        prefix: str
            string matching beginning characters of the archive or set of
            archives you are filtering. Note that authority prefixes, e.g.
            ``local://my/archive.txt`` are not supported in prefix searches.

        pattern: str
            string matching the characters within the archive or set of
            archives you are filtering on. Note that authority prefixes, e.g.
            ``local://my/archive.txt`` are not supported in pattern searches.

        engine: str
            string of value 'str', 'path', or 'regex'. That indicates the
            type of pattern you are filtering on


        Returns
        -------
        generator

        '''

        if pattern is not None:
            pattern = fs.path.relpath(pattern)

        if prefix is not None:
            prefix = fs.path.relpath(prefix)

        archives = self.manager.search(tuple([]), begins_with=prefix)

        if not pattern:
            for archive in archives:
                yield archive

        if engine == 'str':
            for arch in archives:
                if pattern in arch:
                    yield arch

        elif engine == 'path':
            # Change to generator version of fnmatch.filter

            for arch in archives:
                if fnmatch.fnmatch(arch, pattern):
                    yield arch

        elif engine == 'regex':
            for arch in archives:
                if re.search(pattern, arch):
                    yield arch

        else:
            raise ValueError(
                'search engine "{}" not recognized. '.format(engine) +
                'choose "str", "fn", or "regex"')

    def search(self, *query, **kwargs):
        '''
        Searches based on tags specified by users



        Parameters
        ---------
        query: str
            tags to search on. If multiple terms, provided in comma delimited
            string format

        prefix: str
            start of archive name. Providing a start string improves search
            speed.

        '''

        prefix = kwargs.get('prefix')

        if prefix is not None:
            prefix = fs.path.relpath(prefix)

        return self.manager.search(query, begins_with=prefix)

    def _validate_archive_name(self, archive_name):
        '''
        Utility function for creating and validating archive names

        Parameters
        ----------

        archive_name: str
            Name of the archive from which to create a service path

        Returns
        -------

        archive_path: str
            Internal path used by services to reference archive data
        '''
        archive_name = fs.path.normpath(archive_name)
        patterns = self.manager.required_archive_patterns

        for pattern in patterns:
            if not re.search(pattern, archive_name):
                raise ValueError(
                    "archive name does not match pattern '{}'".format(pattern))

    def delete_archive(self, archive_name):
        '''
        Delete an archive

        Parameters
        ----------

        archive_name: str
            Name of the archive to delete

        '''

        archive = self.get_archive(archive_name)

        archive.delete()

    @staticmethod
    def hash_file(f):
        '''
        Utility function for hashing file contents

        Overload this function to change the file equality checking algorithm

        Parameters
        ----------

        f: file-like
            File-like object or file path from which to compute checksum value


        Returns
        -------
        checksum: dict
            dictionary with {'algorithm': 'md5', 'checksum': hexdigest}

        '''

        md5 = hashlib.md5()

        with open_filelike(f, 'rb') as f_obj:
            for chunk in iter(lambda: f_obj.read(128 * md5.block_size), b''):
                md5.update(chunk)

        return {'algorithm': 'md5', 'checksum': md5.hexdigest()}

    def close(self):
        for service in self._authorities:
            self._authorities[service].fs.close()

        if self.cache:
            self.cache.fs.close()

    @staticmethod
    def _validate_authority_name(authority_name):
        matched = re.match(
            r'^{}$'.format(_VALID_AUTHORITY_PATTERNS),
            authority_name)

        if matched:
            return

        raise ValueError('"{}" not a valid authority name'.format(
            authority_name))

    @staticmethod
    def _split_authority(archive_name):
        matched = re.match(
            r'^((?P<auth>{})\:\/\/)?(?P<archive>.*)$'.format(
                _VALID_AUTHORITY_PATTERNS),
            archive_name)

        return matched.group('auth'), matched.group('archive')

    def _normalize_archive_name(self, archive_name, authority_name=None):

        full_archive_arg = archive_name

        str_authority_name, archive_name = self._split_authority(archive_name)

        if ((str_authority_name is not None)
                and (authority_name is not None)
                and (str_authority_name != authority_name)):

            raise ValueError(
                'authority name "{}" not found in archive: "{}"'.format(
                    authority_name, full_archive_arg))

        relpath = fs.path.relpath(fs.path.normpath(archive_name))

        if str_authority_name is None:
            str_authority_name = authority_name

        if str_authority_name is None:
            try:
                str_authority_name = self.default_authority_name
            except ValueError:
                pass

        if str_authority_name is not None:
            if str_authority_name not in self._authorities:
                raise ValueError('Authority "{}" not found'.format(
                    str_authority_name))

            self._authorities[str_authority_name].fs.validatepath(relpath)

        # additional check - not all fs.validatepath functions do anything:
        OSFS('').isvalidpath(relpath)

        return str_authority_name, relpath
