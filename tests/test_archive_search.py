


def test_substr_search(api_with_diverse_archives):

    # Test the total number of "variable" archives
    variables = list(api_with_diverse_archives.filter(pattern='_variable', engine='str'))
    assert len(variables) == api_with_diverse_archives.TEST_ATTRS[
        'archives.variable']

    # Test the total number of "variable1" archives
    var1 = list(api_with_diverse_archives.filter(pattern='_variable1_', engine='str'))
    assert len(var1) == (
        api_with_diverse_archives.TEST_ATTRS['archives.variable'] /
        api_with_diverse_archives.TEST_ATTRS['count.variable'])

    # Test the total number of "parameter" archives
    parameters = list(api_with_diverse_archives.filter(pattern='_parameter', engine='str'))
    assert len(parameters) == api_with_diverse_archives.TEST_ATTRS[
        'archives.parameter']

    # Test the total number of "parameter1" archives
    var1 = list(api_with_diverse_archives.filter(pattern='_parameter1_', engine='str'))
    assert len(var1) == (
        api_with_diverse_archives.TEST_ATTRS['archives.parameter'] /
        api_with_diverse_archives.TEST_ATTRS['count.parameter'])

    # Test the total number of "config" archives
    config_files = list(api_with_diverse_archives.filter(pattern='_config', engine='str'))
    assert len(config_files) == api_with_diverse_archives.TEST_ATTRS[
        'archives.config']


def test_regex_search(api_with_diverse_archives):

    # Test the total number of "variable" archives
    variables = list(api_with_diverse_archives.filter(pattern=
        r'^.*_variable[0-9]+_.*$', engine='regex'))
    assert len(variables) == api_with_diverse_archives.TEST_ATTRS[
        'archives.variable']

    # Test the total number of "variable1" archives
    var1 = list(api_with_diverse_archives.filter(pattern=r'^.*_variable1_.*$', engine='regex'))
    assert len(var1) == (
        api_with_diverse_archives.TEST_ATTRS['archives.variable'] /
        api_with_diverse_archives.TEST_ATTRS['count.variable'])

    # Test the total number of "parameter" archives
    parameters = list(api_with_diverse_archives.filter(pattern=
        r'^.*_parameter[0-9]+_.*$', engine='regex'))
    assert len(parameters) == api_with_diverse_archives.TEST_ATTRS[
        'archives.parameter']

    # Test the total number of "parameter1" archives
    var1 = list(api_with_diverse_archives.filter(pattern=
        r'^.*_parameter1_.*$', engine='regex'))
    assert len(var1) == (
        api_with_diverse_archives.TEST_ATTRS['archives.parameter'] /
        api_with_diverse_archives.TEST_ATTRS['count.parameter'])

    # Test the total number of "config" archives
    config_files = list(api_with_diverse_archives.filter(pattern=
        r'^.*_config.*$', engine='regex'))
    assert len(config_files) == api_with_diverse_archives.TEST_ATTRS[
        'archives.config']


def test_fn_search(api_with_diverse_archives):

    # Test the total number of "variable" archives
    variables = list(api_with_diverse_archives.filter(pattern='*_variable?*_*', engine='path'))
    assert len(variables) == api_with_diverse_archives.TEST_ATTRS[
        'archives.variable']

    # Test the total number of "variable1" archives
    var1 = list(api_with_diverse_archives.filter(pattern='*_variable1_*', engine='path'))
    assert len(var1) == (
        api_with_diverse_archives.TEST_ATTRS['archives.variable'] /
        api_with_diverse_archives.TEST_ATTRS['count.variable'])

    # Test the total number of "parameter" archives
    parameters = list(api_with_diverse_archives.filter(pattern=
        '*_parameter?*_*', engine='path'))
    assert len(parameters) == api_with_diverse_archives.TEST_ATTRS[
        'archives.parameter']

    # Test the total number of "parameter1" archives
    var1 = list(api_with_diverse_archives.filter(pattern='*_parameter1_*', engine='path'))
    assert len(var1) == (
        api_with_diverse_archives.TEST_ATTRS['archives.parameter'] /
        api_with_diverse_archives.TEST_ATTRS['count.parameter'])

    # Test the total number of "config" archives
    config_files = list(api_with_diverse_archives.filter(pattern='*_config*', engine='path'))
    assert len(config_files) == api_with_diverse_archives.TEST_ATTRS[
        'archives.config']



def test_tagging_update_and_get(api_with_spec):
    
    api_with_spec.create('tagged_archive', metadata=dict(description='archive description'))

    arch = api_with_spec.get_archive('tagged_archive')
    arch.add_tags('tag1', 'tag2')
    
    res = api_with_spec.search('tag1', 'tag2')

    assert 'tagged_archive' in list(res)

    arch.add_tags('tag3', 'tag1')

    result = arch.get_tags()
    assert 'tag1' and 'tag2' and  'tag3' in result
    assert len(result) == 3

    arch.delete_tags('tag1')
    result_delete = arch.get_tags()
    assert 'tag1' not in result_delete
    assert len(result_delete) == 2













