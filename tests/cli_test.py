from __future__ import absolute_import

from datafs.datafs import DataFSInterface
from datafs.config.parser import ConfigFile
import click
from click.testing import CliRunner
import pytest



@pytest.yield_fixture
def runner():
	return CliRunner()


#this sets the command line environment for 
@click.group()
@click.option('--config-file', envvar='CONFIG_FILE', type=str)
@click.option('--profile', envvar='PROFILE', type=str, default=None)
@click.pass_context
def datafs(ctx, config_file=None, profile=None):
    
    
    ctx.obj = DataFSInterface()

    ctx.obj.config_file = config_file

    config = ConfigFile(ctx.obj.config_file)
    config.read_config()

    ctx.obj.config = config
    
    if profile is None:
        profile = config.config['default-profile']

    ctx.obj.profile = profile

    api = config.generate_api_from_config(profile=ctx.obj.profile)
    
    config.attach_manager_from_config(api, profile=ctx.obj.profile)
    config.attach_services_from_config(api, profile=ctx.obj.profile)
    config.attach_cache_from_config(api, profile=ctx.obj.profile)

    ctx.obj.api = api


@datafs.command(context_settings=dict(ignore_unknown_options=True,allow_extra_args=True))
@click.option('--helper', envvar='HELPER', is_flag=True)
@click.option('--edit', envvar='EDIT', is_flag=True)
@click.pass_context
def configure(ctx, helper, edit):
    '''
    Update existing configuration or create a new default profile
    '''

    kwargs = {ctx.args[i][2:]: ctx.args[i+1] for i in xrange(0, len(ctx.args), 2)}
    ctx.obj.config.config['profiles'][ctx.obj.profile]['api']['user_config'].update(kwargs)

    if helper:
        interactive_configuration(ctx.obj.api, ctx.obj.config, profile=ctx.obj.profile)

    elif edit:
        ctx.obj.config.edit_config_file()

    else:
        for kw in ctx.obj.api.REQUIRED_USER_CONFIG:
            if not kw in ctx.obj.api.user_config:
                raise KeyError('Required configuration option "{}" not supplied. Use --helper to configure interactively'.format(kw))
    
    ctx.obj.config.write_config()


@datafs.command(context_settings=dict(ignore_unknown_options=True,allow_extra_args=True))
@click.argument('archive_name')
@click.option('--authority_name', envvar='AUTHORITY_NAME', default=None)
@click.pass_context
def create_archive(ctx, archive_name, authority_name):
    kwargs = parse_args_as_kwargs(ctx.args)
    var = ctx.obj.api.create_archive(archive_name, authority_name=authority_name, metadata=kwargs)
    click.echo('created archive {}'.format(var))


@datafs.command(context_settings=dict(ignore_unknown_options=True,allow_extra_args=True))
@click.argument('archive_name')
@click.argument('filepath')
@click.pass_context
def upload(ctx, archive_name, filepath):
    kwargs = parse_args_as_kwargs(ctx.args)
    var = ctx.obj.api.get_archive(archive_name)
    var.update(filepath, **kwargs)
    click.echo('uploaded data to {}'.format(var))


@datafs.command()
@click.argument('archive_name')
@click.argument('filepath')
@click.pass_context
def download(ctx, archive_name, filepath):
    var = ctx.obj.api.get_archive(archive_name)
    var.download(filepath)
    click.echo('downloaded {} to {}'.format(var, filepath))


@datafs.command()
@click.argument('archive_name')
@click.pass_context
def metadata(ctx, archive_name):
    var = ctx.obj.api.get_archive(archive_name)
    click.echo(pprint.pformat(var.metadata))


@datafs.command()
@click.argument('archive_name')
@click.pass_context
def versions(ctx, archive_name):
    var = ctx.obj.api.get_archive(archive_name)
    click.echo(var.versions)

@datafs.command()
@click.option('--prefix', envvar='PREFIX', default='')
@click.pass_context
def list(ctx, prefix):
    archives = ctx.obj.api.archives
    res = [var.archive_name for var in archives if var.archive_name.startswith(prefix)]
    click.echo(res)


def test_cli():

	runner = CliRunner()
	result = runner.invoke(datafs)
	print result.output
	assert 'Usage' and'Options' and 'Commands' in result.output

def test_list():
	runner= CliRunner()
	result = runner.invoke(datafs, ['list'])
	return result.output
