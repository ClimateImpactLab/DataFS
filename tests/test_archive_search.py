
def test_substr_search(api_with_diverse_archives):

    # Test the total number of "variable" archives
    variables = api_with_diverse_archives.list('_variable', engine='str')
    assert len(variables) == api_with_diverse_archives.TEST_ATTRS[
        'archives.variable']

    # Test the total number of "variable1" archives
    var1 = api_with_diverse_archives.list('_variable1_', engine='str')
    assert len(var1) == (
        api_with_diverse_archives.TEST_ATTRS['archives.variable'] / 
        api_with_diverse_archives.TEST_ATTRS['count.variable'])


    # Test the total number of "parameter" archives
    parameters = api_with_diverse_archives.list('_parameter', engine='str')
    assert len(parameters) == api_with_diverse_archives.TEST_ATTRS[
        'archives.parameter']

    # Test the total number of "parameter1" archives
    var1 = api_with_diverse_archives.list('_parameter1_', engine='str')
    assert len(var1) == (
        api_with_diverse_archives.TEST_ATTRS['archives.parameter'] / 
        api_with_diverse_archives.TEST_ATTRS['count.parameter'])


    # Test the total number of "config" archives
    config_files = api_with_diverse_archives.list('_config', engine='str')
    assert len(config_files) == api_with_diverse_archives.TEST_ATTRS[
        'archives.config']



def test_regex_search(api_with_diverse_archives):

    # Test the total number of "variable" archives
    variables = api_with_diverse_archives.list(r'^.*_variable[0-9]+_.*$', engine='regex')
    assert len(variables) == api_with_diverse_archives.TEST_ATTRS[
        'archives.variable']

    # Test the total number of "variable1" archives
    var1 = api_with_diverse_archives.list(r'^.*_variable1_.*$', engine='regex')
    assert len(var1) == (
        api_with_diverse_archives.TEST_ATTRS['archives.variable'] / 
        api_with_diverse_archives.TEST_ATTRS['count.variable'])


    # Test the total number of "parameter" archives
    parameters = api_with_diverse_archives.list(r'^.*_parameter[0-9]+_.*$', engine='regex')
    assert len(parameters) == api_with_diverse_archives.TEST_ATTRS[
        'archives.parameter']

    # Test the total number of "parameter1" archives
    var1 = api_with_diverse_archives.list(r'^.*_parameter1_.*$', engine='regex')
    assert len(var1) == (
        api_with_diverse_archives.TEST_ATTRS['archives.parameter'] / 
        api_with_diverse_archives.TEST_ATTRS['count.parameter'])


    # Test the total number of "config" archives
    config_files = api_with_diverse_archives.list(r'^.*_config.*$', engine='regex')
    assert len(config_files) == api_with_diverse_archives.TEST_ATTRS[
        'archives.config']




def test_fn_search(api_with_diverse_archives):

    # Test the total number of "variable" archives
    variables = api_with_diverse_archives.list('*_variable?*_*', engine='path')
    assert len(variables) == api_with_diverse_archives.TEST_ATTRS[
        'archives.variable']

    # Test the total number of "variable1" archives
    var1 = api_with_diverse_archives.list('*_variable1_*', engine='path')
    assert len(var1) == (
        api_with_diverse_archives.TEST_ATTRS['archives.variable'] / 
        api_with_diverse_archives.TEST_ATTRS['count.variable'])


    # Test the total number of "parameter" archives
    parameters = api_with_diverse_archives.list('*_parameter?*_*', engine='path')
    assert len(parameters) == api_with_diverse_archives.TEST_ATTRS[
        'archives.parameter']

    # Test the total number of "parameter1" archives
    var1 = api_with_diverse_archives.list('*_parameter1_*', engine='path')
    assert len(var1) == (
        api_with_diverse_archives.TEST_ATTRS['archives.parameter'] / 
        api_with_diverse_archives.TEST_ATTRS['count.parameter'])


    # Test the total number of "config" archives
    config_files = api_with_diverse_archives.list('*_config*', engine='path')
    assert len(config_files) == api_with_diverse_archives.TEST_ATTRS[
        'archives.config']

