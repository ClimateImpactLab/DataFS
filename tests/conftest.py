


def pytest_generate_tests(metafunc):
    '''
    Build an API connection for use in testing
    '''

    if 'mgr_name' in metafunc.fixturenames:

        metafunc.parametrize('mgr_name', ['mongo', 'dynamo'])
        # metafunc.parametrize('mgr_name', ['mongo'])

    if 'fs_name' in metafunc.fixturenames:

        metafunc.parametrize('fs_name', ['OSFS', 'S3FS', 'OSFS', 'OSFS', 'S3FS'])
        

    if 'open_func' in metafunc.fixturenames:
        metafunc.parametrize('open_func', ['open_file', 'get_local_path'])
