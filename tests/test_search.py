import pytest
import os
import itertools
from click.testing import CliRunner
from datafs.datafs import cli
from datafs import get_api, to_config_file


@pytest.yield_fixture(scope='module')
def test_config(api1_module, local_auth_module, temp_dir_mod):

    api1_module.attach_authority('local', local_auth_module)

    temp_file = os.path.join(temp_dir_mod, 'config.yml')

    to_config_file(api1_module, config_file=temp_file, profile='myapi')

    for i, j, k in itertools.product(*tuple([range(3) for _ in range(3)])):
        arch = 'team{}_archive{}_var{}'.format(i+1, j+1, k+1)
        api1_module.create(
            arch,
            tags=list(arch.split('_')),
            metadata={
                'description': 'archive_{}_{}_{} description'.format(i, j, k)})

    yield 'myapi', temp_file


@pytest.mark.search
@pytest.mark.cli
def test_cli_search(test_config, monkeypatch):

    profile, config_file = test_config

    api = get_api(profile=profile, config_file=config_file)

    runner = CliRunner()
    prefix = ['--config-file', config_file, '--profile', 'myapi']

    # Test the helper with the appropriate input stream
    result = runner.invoke(
        cli,
        prefix + ['search', 'team2', 'var2', 'archive2']
    )

    assert result.exit_code == 0
    assert 'team2_archive2_var2' in result.output.strip().split('\n')[0]

    res = list(api.search('team2', 'var3', 'archive1'))

    assert 'team2_archive1_var3' in res

    # Test the helper with the appropriate input stream
    result = runner.invoke(
        cli,
        prefix + ['search', 'var2', 'team2', 'archive2']
    )

    assert result.exit_code == 0
    assert 'team2_archive2_var2' in result.output.strip().split('\n')[0]


@pytest.mark.search
@pytest.mark.cli
def test_cli_tagging(test_config):

    profile, config_file = test_config

    runner = CliRunner()
    prefix = ['--config-file', config_file, '--profile', profile]

    # Add a tag to one archive
    result = runner.invoke(
        cli,
        prefix + ['add_tags', 'team2_archive2_var2', 'newtag']
    )

    assert result.exit_code == 0

    # Search using the new tag
    result = runner.invoke(
        cli,
        prefix + ['search', 'newtag']
    )

    assert result.exit_code == 0
    assert 'team2_archive2_var2' in result.output.strip().split('\n')[0]

    # search using multiple tags
    result = runner.invoke(
        cli,
        prefix + ['search', 'newtag', 'team2', 'archive2']
    )

    assert result.exit_code == 0
    assert 'team2_archive2_var2' in result.output.strip().split('\n')[0]

    # Search using the old tags
    result = runner.invoke(
        cli,
        prefix + ['search', 'var2', 'team2', 'archive2']
    )

    assert result.exit_code == 0
    assert 'team2_archive2_var2' in result.output.strip().split('\n')[0]

    # Search using a bad tag combo
    result = runner.invoke(
        cli,
        prefix + ['search', 'newtag', 'team3']
    )

    assert result.exit_code == 0
    assert '' == result.output.strip()

    # test get_tags
    result = runner.invoke(
        cli,
        prefix + ['get_tags', 'team2_archive2_var2']
    )

    assert result.exit_code == 0

    tags = {'newtag', 'team2', 'archive2', 'var2'}
    assert set(result.output.strip().split('\n')[0].split(' ')) == tags

    # test delete_tags
    result = runner.invoke(
        cli,
        prefix + ['delete_tags', 'team2_archive2_var2', 'newtag']
    )

    assert result.exit_code == 0

    # test get_tags
    result = runner.invoke(
        cli,
        prefix + ['get_tags', 'team2_archive2_var2']
    )

    assert result.exit_code == 0

    tags = {'team2', 'archive2', 'var2'}
    assert set(result.output.strip().split('\n')[0].split(' ')) == tags
