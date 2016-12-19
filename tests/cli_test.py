from __future__ import absolute_import

from datafs.datafs import DataFSInterface
from datafs.config.parser import ConfigFile
import click
from click.testing import CliRunner
import pytest




import click
from click.testing import CliRunner
from datafs.datafs import cli

runner = CliRunner()
result = runner.invoke(cli, ['--profile', 'impactlab', 'list'])
assert result.output == '[<DataArchive osdc://my_file.txt>]'