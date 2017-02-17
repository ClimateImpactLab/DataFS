
from __future__ import absolute_import

import pytest

import tempfile
import moto
import itertools
import os

from fs.osfs import OSFS
from fs.s3fs import S3FS

from datafs import DataAPI
from datafs._compat import string_types
from datafs.core import data_file
from tests.resources import prep_manager, _close
import shutil

from contextlib import contextmanager


@pytest.yield_fixture(scope='session')
def example_snippet_working_dirs():

    test_dirs = ['tests/test1', 'tests/test2', 'tests/test3']

    for td in test_dirs:
        if not os.path.isdir(td):
            os.makedirs(td)

    try:
        yield
    finally:
        for td in test_dirs:
            if os.path.isdir(td):
                shutil.rmtree(td)


def pytest_generate_tests(metafunc):
    '''
    Build an API connection for use in testing
    '''

    if 'mgr_name' in metafunc.fixturenames:

        metafunc.parametrize('mgr_name', ['mongo', 'dynamo'])
        # metafunc.parametrize('mgr_name', ['mongo'])

    if 'fs_name' in metafunc.fixturenames:

        metafunc.parametrize(
            'fs_name', ['OSFS', 'S3FS'])

    if 'open_func' in metafunc.fixturenames:
        metafunc.parametrize('open_func', ['open_file', 'get_local_path'])


@contextmanager
def make_temp_dir():
    tmpdir = tempfile.mkdtemp()

    try:
        yield tmpdir.replace(os.sep, '/')

    finally:
        _close(tmpdir)


@pytest.yield_fixture(scope='function')
def tempdir():
    with make_temp_dir() as tmp:
        yield tmp


@pytest.yield_fixture(scope='module')
def temp_dir_mod():
    with make_temp_dir() as tmp:
        yield tmp


@pytest.yield_fixture(scope='module')
def temp_file():
    tmp = tempfile.NamedTemporaryFile(delete=False)

    try:
        yield tmp.name.replace(os.sep, '/')

    finally:
        tmp.close()
        _close(tmp.name)


@contextmanager
def prep_filesystem(fs_name):

    if fs_name == 'OSFS':

        with make_temp_dir() as tmp:
            local = OSFS(tmp)

            yield local

            local.close()

    elif fs_name == 'S3FS':

        m = moto.mock_s3()
        m.start()

        try:

            s3 = S3FS(
                'test-bucket',
                aws_access_key='MY_KEY',
                aws_secret_key='MY_SECRET_KEY')

            yield s3
            s3.close()

        finally:
            m.stop()


@pytest.yield_fixture
def api(mgr_name, fs_name):

    with prep_manager(mgr_name) as manager:

        api = DataAPI(
            username='My Name',
            contact='my.email@example.com')

        api.attach_manager(manager)

        with prep_filesystem(fs_name) as filesystem:
            api.attach_authority('filesys', filesystem)

            yield api


@pytest.yield_fixture(scope='module')
def api1_module():

    with prep_manager('mongo') as manager:

        api = DataAPI(
            username='My Name',
            contact='my.email@example.com')

        api.attach_manager(manager)

        yield api


@pytest.yield_fixture
def api1(mgr_name):

    with prep_manager(mgr_name) as manager:

        api = DataAPI(
            username='My Name',
            contact='my.email@example.com')

        api.attach_manager(manager)

        yield api


@pytest.yield_fixture
def api2(mgr_name):

    with prep_manager(mgr_name) as manager:

        api = DataAPI(
            username='My Name',
            contact='my.email@example.com')

        api.attach_manager(manager)

        yield api


@pytest.yield_fixture(scope='function')
def local_auth():

    with prep_filesystem('OSFS') as filesystem:
        yield filesystem


@pytest.yield_fixture(scope='module')
def local_auth_module():

    with prep_filesystem('OSFS') as filesystem:
        yield filesystem


@pytest.yield_fixture(scope='function')
def auth1(fs_name):

    with prep_filesystem(fs_name) as filesystem:
        yield filesystem


@pytest.yield_fixture(scope='function')
def auth2(fs_name):

    with prep_filesystem(fs_name) as filesystem:
        yield filesystem


@pytest.yield_fixture(scope='function')
def cache():

    with prep_filesystem('OSFS') as filesystem:
        yield filesystem


@pytest.yield_fixture(scope='function')
def cache1():

    with prep_filesystem('OSFS') as filesystem:
        yield filesystem


@pytest.yield_fixture(scope='function')
def cache2():

    with prep_filesystem('OSFS') as filesystem:
        yield filesystem


@pytest.yield_fixture
def manager_with_spec(mgr_name):

    with prep_manager(mgr_name, table_name='spec-test') as manager:

        metadata_config = {
            'description': 'some metadata'
        }

        user_config = {
            'username': 'Your Name',
            'contact': 'my.email@example.com'

        }

        manager.set_required_user_config(user_config)
        manager.set_required_archive_metadata(metadata_config)

        yield manager


@pytest.yield_fixture
def manager_with_pattern(mgr_name):

    with prep_manager(mgr_name, table_name='pattern-test') as manager:

        GCP_PATTERNS = [r'^(TLD1/(sub1|sub2|sub3)|TLD2/(sub1|sub2|sub3))']
        manager.set_required_archive_patterns(GCP_PATTERNS)

        yield manager


@pytest.yield_fixture
def api_with_spec(manager_with_spec, auth1):

    api = DataAPI(
        username='My Name',
        contact='my.email@example.com')

    api.attach_manager(manager_with_spec)
    api.attach_authority('auth', auth1)

    yield api


@pytest.yield_fixture
def api_with_pattern(manager_with_pattern, auth1):

    api = DataAPI()

    api.attach_manager(manager_with_pattern)
    api.attach_authority('auth', auth1)

    yield api


@pytest.fixture
def opener(open_func):
    '''
    Fixture for opening files using each of the available methods

    open_func is parameterized in conftest.py
    '''

    if open_func == 'open_file':

        @contextmanager
        def inner(
                archive,
                mode='r',
                version=None,
                bumpversion='patch',
                prerelease=None,
                dependencies=None,
                *args,
                **kwargs):

            with archive.open(
                *args,
                mode=mode,
                version=version,
                bumpversion=bumpversion,
                prerelease=prerelease,
                dependencies=dependencies,
                    **kwargs) as f:

                yield f

        return inner

    elif open_func == 'get_local_path':

        @contextmanager
        def inner(
                archive,
                mode='r',
                version=None,
                bumpversion='patch',
                prerelease=None,
                dependencies=None,
                *args,
                **kwargs):

            with archive.get_local_path(
                    version=version,
                    bumpversion=bumpversion,
                    prerelease=prerelease,
                    dependencies=dependencies) as fp:

                with open(fp, mode=mode, *args, **kwargs) as f:
                    yield f

        return inner

    else:
        raise NameError('open_func "{}" not recognized'.format(open_func))


@pytest.fixture
def datafile_opener(open_func):
    '''
    Fixture for opening files using each of the available methods

    open_func is parameterized in conftest.py
    '''

    if open_func == 'open_file':

        return data_file.open_file

    elif open_func == 'get_local_path':

        @contextmanager
        def inner(
                auth,
                cache,
                update,
                version_check,
                hasher,
                read_path,
                write_path=None,
                cache_on_write=False,
                *args,
                **kwargs):

            with data_file.get_local_path(
                    auth,
                    cache,
                    update,
                    version_check,
                    hasher,
                    read_path,
                    write_path,
                    cache_on_write) as fp:

                assert isinstance(fp, string_types)

                with open(fp, *args, **kwargs) as f:
                    yield f

        return inner

    else:
        raise NameError('open_func "{}" not recognized'.format(open_func))


@pytest.yield_fixture(scope='session', params=['mongo', 'dynamo'])
def api_with_diverse_archives(request):

    ITERATIONS = 7
    VARS = 5
    PARS = 5
    CONF = 3

    with prep_manager(request.param, table_name='diverse') as manager:

        api = DataAPI(
            username='My Name',
            contact='my.email@example.com')

        api.attach_manager(manager)

        def direct_create_archive_spec(archive_name):
            return api.manager._create_archive_metadata(
                archive_name=archive_name,
                authority_name='auth',
                archive_path='/'.join(archive_name.split('_')),
                versioned=True,
                raise_on_err=True,
                metadata={},
                user_config={},
                helper=False,
                tags=os.path.splitext(archive_name)[0].split('_'))

        with prep_filesystem('OSFS') as auth1:

            api.attach_authority('auth', auth1)

            archive_names = []

            for indices in itertools.product(*(
                    range(1, ITERATIONS+1) for _ in range(VARS))):

                archive_name = (
                    'team{}_project{}_task{}_variable{}_scenario{}.nc'.format(
                        *indices))

                archive_names.append(archive_name)

            for indices in itertools.product(*(
                    range(1, ITERATIONS+1) for _ in range(PARS))):

                archive_name = (
                    'team{}_project{}_task{}_' +
                    'parameter{}_scenario{}.csv').format(*indices)

                archive_names.append(archive_name)

            for indices in itertools.product(*(
                    range(1, ITERATIONS+1) for _ in range(CONF))):

                archive_name = (
                    'team{}_project{}_task{}_config.txt'.format(
                        *indices))

                archive_names.append(archive_name)

            batch_size = 500

            for st_ind in range(0, len(archive_names), batch_size):
                current_batch = archive_names[st_ind:st_ind+batch_size]

                new_archives = list(map(
                    direct_create_archive_spec, current_batch))

                if request.param == 'mongo':
                    api.manager.collection.insert_many(new_archives)

                elif request.param == 'dynamo':
                    with api.manager._table.batch_writer() as batch:
                        for item in new_archives:
                            batch.put_item(Item=item)

                else:
                    raise ValueError('Manager "{}" not recognized'.format(
                        request.param))

            api.TEST_ATTRS = {
                'archives.variable': ITERATIONS**VARS,
                'archives.parameter': ITERATIONS**PARS,
                'archives.config': ITERATIONS**CONF,
                'count.variable': ITERATIONS,
                'count.parameter': ITERATIONS,
                'count.config': 1
            }

            yield api
