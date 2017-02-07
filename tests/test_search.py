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

    yield 'myapi', temp_file


def test_cli_search(test_config, monkeypatch):

    profile, config_file = test_config

    api = get_api(profile=profile, config_file=config_file)

    for i, j, k in itertools.product(*tuple([range(3) for _ in range(3)])):
        arch = 'team{}_archive{}_var{}'.format(i+1, j+1, k+1)
        api.create(arch, metadata={
                'description': 'archive_{}_{}_{} description'.format(i, j, k)})

        _arch = api.get_archive(arch)
        for _ in arch.split('_'):
            _arch.add_tags(_)

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
