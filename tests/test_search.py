

import pytest
import tempfile
import os
import shutil
import click.termui
from click.testing import CliRunner
from tests.resources import _close
from datafs.datafs import cli
from datafs import get_api, to_config_file

@pytest.yield_fixture(scope='module')
def temp_dir():

    # setup data directory

    temp = tempfile.mkdtemp()

    try:
        yield temp.replace(os.sep, '/')

    finally:
        _close(temp)





@pytest.yield_fixture(scope='module')
def test_config(api1_module, local_auth_module, temp_dir):
    
    api1_module.attach_authority('local', local_auth_module)

    temp_file = os.path.join(temp_dir, 'config.yml')

    to_config_file(api1_module, config_file=temp_file, profile='myapi')

    yield 'myapi', temp_file


def test_cli_search(test_config, monkeypatch):

    profile, config_file = test_config

    api = get_api(profile=profile, config_file=config_file)

    api.create('team1_archive1_var1')
    api.create('team1_archive2_var1')
    api.create('team1_archive3_var1')
    api.create('team2_archive1_var1')
    api.create('team2_archive2_var1')
    api.create('team2_archive3_var1')
    api.create('team3_archive1_var1')
    api.create('team3_archive2_var1')
    api.create('team3_archive3_var1')
    api.create('team1_archive1_var2')
    api.create('team1_archive2_var2')
    api.create('team1_archive3_var2')
    api.create('team2_archive1_var2')
    api.create('team2_archive2_var2')
    api.create('team2_archive3_var2')
    api.create('team3_archive1_var2')
    api.create('team3_archive2_var2')
    api.create('team3_archive3_var2')
    api.create('team1_archive1_var3')
    api.create('team1_archive2_var3')
    api.create('team1_archive3_var3')
    api.create('team2_archive1_var3')
    api.create('team2_archive2_var3')
    api.create('team2_archive3_var3')
    api.create('team3_archive1_var3')
    api.create('team3_archive2_var3')
    api.create('team3_archive3_var3')


    runner = CliRunner()
    prefix = ['--config-file', config_file, '--profile', 'myapi']

    # Test the helper with the appropriate input stream
    result = runner.invoke(
        cli,
        prefix + ['search'],
        input='var2 team2 archive2'
    )

    assert result.exit_code == 0
    assert 'team2_archive2_var2' in result.output.split('\n')[-2], result.output


    res = api.search('var2 team2 archive2')

    assert res[0] == 'team2_archive2_var2'

    # down = '\x1b' + chr(91) + chr(65) #'\x50' # + chr(27) + chr(91) + chr(65)
    # up = '\x1b' + chr(91) + chr(66) # '\x48' # + chr(27) + chr(91) + chr(66)

    # # up = chr(945) + chr(72)
    # # down = chr(945) + chr(80)
    # enter = '\x1b' + chr(13)

    # result = runner.invoke(
    #     cli,
    #     prefix + ['search'],
    #     # input='var2 team3' + enter
    #     input='var2 team3 ' + down + down + down + up + enter
    # )

    # assert 'team3_archive2_var2' in result.output.split('\n')[-2], result.output


    # Test the helper with the appropriate input stream
    result = runner.invoke(
        cli,
        prefix + ['search'],
        input='var2 team22' + chr(8) + ' archive2' + chr(27)
    )

    assert result.exit_code == 0
    assert 'team2_archive2_var2' in result.output.split('\n')[-2], result.output