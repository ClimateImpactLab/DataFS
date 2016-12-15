# -*- coding: utf-8 -*-

from __future__ import absolute_import
from datafs.core.data_api import DataAPI
from datafs.config.parser import ConfigFile
import os 
import click
import yaml
import pprint

def process_kwargs(kwarg_name):
    def decorator(func):
        def inner(*args, **kwargs):
            keyword_arguments = kwargs.pop(kwarg_name, {})

            assert len(keyword_arguments)%2==0
            for i in range(0, len(keyword_arguments), 2):
                kwargs[keyword_arguments[i].lstrip('-')] = keyword_arguments[i+1]

            return func(*args, **kwargs)
        return inner
    return decorator


def parse_args_as_kwargs(args):
    assert len(args)%2==0
    kwargs = {}
    for i in range(0, len(args), 2):
        kwargs[args[i].lstrip('-')] = args[i+1]
    return kwargs

def interactive_configuration(api, config, profile=None):
    profile_config = config.get_profile_config(profile)

    for kw in api.REQUIRED_USER_CONFIG:
        if not kw in api.user_config:
            profile_config['api']['user_config'][kw] = click.prompt(
                api.REQUIRED_USER_CONFIG[kw])
        
        else:
            profile_config['api']['user_config'][kw] = click.prompt(
                api.REQUIRED_USER_CONFIG[kw], 
                default=profile_config['api']['user_config'][kw])



class DataFSInterface(object):
    def __init__(self, config={}, api=None, config_file=None, profile=None):
        self.config = config
        self.api = api
        self.config_file = config_file


@click.group()
@click.option('--config-file', envvar='CONFIG_FILE', type=str)
@click.option('--profile', envvar='PROFILE', type=str, default=None)
@click.pass_context
def cli(ctx, config_file=None, profile=None):
    
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


@cli.command(context_settings=dict(ignore_unknown_options=True,allow_extra_args=True))
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


@cli.command(context_settings=dict(ignore_unknown_options=True,allow_extra_args=True))
@click.argument('archive_name')
@click.option('--authority_name', envvar='AUTHORITY_NAME', default=None)
@click.pass_context
def create_archive(ctx, archive_name, authority_name):
    kwargs = parse_args_as_kwargs(ctx.args)
    var = ctx.obj.api.create_archive(archive_name, authority_name=authority_name, metadata=kwargs)
    click.echo('created archive {}'.format(var))


@cli.command(context_settings=dict(ignore_unknown_options=True,allow_extra_args=True))
@click.argument('archive_name')
@click.argument('filepath')
@click.pass_context
def upload(ctx, archive_name, filepath):
    kwargs = parse_args_as_kwargs(ctx.args)
    var = ctx.obj.api.get_archive(archive_name)
    var.update(filepath, **kwargs)
    click.echo('uploaded data to {}'.format(var))


@cli.command()
@click.argument('archive_name')
@click.argument('filepath')
@click.pass_context
def download(ctx, archive_name, filepath):
    var = ctx.obj.api.get_archive(archive_name)
    var.download(filepath)
    click.echo('downloaded {} to {}'.format(var, filepath))


@cli.command()
@click.argument('archive_name')
@click.pass_context
def metadata(ctx, archive_name):
    var = ctx.obj.api.get_archive(archive_name)
    click.echo(pprint.pformat(var.metadata))


@cli.command()
@click.argument('archive_name')
@click.pass_context
def versions(ctx, archive_name):
    var = ctx.obj.api.get_archive(archive_name)
    click.echo(var.versions)

@cli.command()
@click.option('--prefix', envvar='PREFIX', default='')
@click.pass_context
def list(ctx, prefix):
    archives = ctx.obj.api.archives
    res = [var.archive_name for var in archives if var.archive_name.startswith(prefix)]
    click.echo(res)



if __name__ == "__main__":
    cli()




