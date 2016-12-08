


def pytest_generate_tests(metafunc):
    '''
    Build an API connection for use in testing
    '''

    if 'mgr_name' in metafunc.fixturenames:

        metafunc.parametrize('mgr_name', ['mongo', 'dynamo'])
        # metafunc.parametrize('mgr_name', ['mongo'])

    if 'fs_name' in metafunc.fixturenames:

        # metafunc.parametrize('fs_name', ['OSFS', 'TempFS', 'S3FS'])
        metafunc.parametrize('fs_name', ['OSFS', 'S3FS', 'OSFS', 'OSFS', 'OSFS', 'S3FS', 'OSFS', 'OSFS'])
        

