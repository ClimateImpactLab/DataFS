'''
Tests for package deployment and first-time configuration

Tests in this module pertain to issues/use cases facing users first installing
and/or upgrading the package. This may include:

    - installation
    - command line help system
    - initial datafs.yml configuration file setup
    - issues specific to first-time initialization of managers/services on a
      new system
    - new user connection to an existing manager/service

Tests pertaining to the use/modification of configuration files, managers,
services, and other datafs components that are not directly related to setup
and first-use circumstances should be located in other testing modules.

All tests should include an issue number they address. For more information,
see the datafs :ref:`contributing guidelines <contributing>`.

'''

import pytest
import traceback
import os
from datafs.datafs import cli
from click.testing import CliRunner


@pytest.yield_fixture
def app_config_dir(tmpdir, monkeypatch):
    '''
    Monkeypatches click.get_app_dir to provide a blank datafs config directory

    This fixture should be used any time the creation of a new datafs
    config.yml file is being tested, including in deployment/installation
    tests.

    This fixture was created to address :issue:`265`
    '''

    config_path = tmpdir.mkdir('appdir')

    def tmp_app_dir(app_name):
        return os.path.join(str(config_path), app_name)

    monkeypatch.setattr('click.get_app_dir', tmp_app_dir)

    yield str(config_path)


def test_config_file_creation(app_config_dir):
    '''
    Tests the creation of a new datafs config.yml file in a fresh install

    Addresses :issue:`265`
    '''

    # Check to make sure the config file does not exist
    if os.path.isdir(os.path.join(app_config_dir, 'datafs')):
        raise OSError('config file exists before creation')

    runner = CliRunner()

    # attempt configure command with a blank config dir
    result = runner.invoke(
        cli,
        ['configure', '--username', 'my_name', '--contact', 'me@email.com'])

    if result.exit_code != 0:
        traceback.print_exception(*result.exc_info)
        raise OSError('Errors encountered during execution')

    # Check to make sure the config file does not exist
    if not os.path.exists(
            os.path.join(app_config_dir, 'datafs', 'config.yml')):

        raise OSError('config file does not exist after creation')
