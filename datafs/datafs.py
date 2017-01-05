# -*- coding: utf-8 -*-

from __future__ import absolute_import
from datafs.core.data_api import DataAPI
from datafs.config.config_file import ConfigFile
from datafs.config.helpers import get_api, parse_requirement
import os
import re
import click
import yaml
import pprint


def parse_args_as_kwargs(args):
    assert len(args) % 2 == 0
    kwargs = {}
    for i in range(0, len(args), 2):
        kwargs[args[i].lstrip('-')] = args[i + 1]
    return kwargs


def interactive_configuration(api, config, profile=None):
    profile_config = config.get_profile_config(profile)

    #read from the required config settings in DataAPI
    for kw in api.REQUIRED_USER_CONFIG:
        if kw not in api.user_config:
            profile_config['api']['user_config'][kw] = click.prompt(
                api.REQUIRED_USER_CONFIG[kw])

        else:
            profile_config['api']['user_config'][kw] = click.prompt(
                api.REQUIRED_USER_CONFIG[kw],
                default=profile_config['api']['user_config'][kw])


def parse_dependencies(dependency_args):
    
    if len(dependency_args) == 0: 
        return None

    # dependencies = {}
    return dict(map(parse_requirement, dependency_args))
    #     if len(arg) == 2: 
    #         split = arg.split('==')
    #         dependencies[split[0]] = split[1]
    #     dependencies[arg] = None

    # return dependencies

class DataFSInterface(object):

    def __init__(self, config={}, api=None, config_file=None, profile=None):
        self.config = config
        self.api = api
        self.config_file = config_file




#this sets the command line environment for 
@click.group()
@click.option('--config-file', envvar='CONFIG_FILE', type=str)
@click.option('--requirements', envvar='REQUIREMENTS', type=str, default='requirements_data.txt')
@click.option('--profile', envvar='PROFILE', type=str, default=None)
@click.pass_context
def cli(ctx, config_file=None, requirements='requirements_data.txt', profile=None):

    ctx.obj = DataFSInterface()

    ctx.obj.config_file = config_file

    config = ConfigFile(ctx.obj.config_file)
    config.read_config()

    ctx.obj.config = config

    if profile is None:
        profile = config.config['default-profile']

    ctx.obj.profile = profile

    api = get_api(profile=profile, config_file=config_file, requirements=requirements)

    ctx.obj.api = api


    @ctx.call_on_close
    def teardown():
        ctx.obj.api.close()


@cli.command(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True))
@click.option('--helper', envvar='HELPER', is_flag=True)
@click.option('--edit', envvar='EDIT', is_flag=True)
@click.pass_context
def configure(ctx, helper, edit):
    '''
    Update existing configuration or create a new default profile
    '''

    kwargs = {ctx.args[i][2:]: ctx.args[i + 1]
              for i in xrange(0, len(ctx.args), 2)}
    ctx.obj.config.config['profiles'][ctx.obj.profile][
        'api']['user_config'].update(kwargs)

    if helper:
        interactive_configuration(
            ctx.obj.api,
            ctx.obj.config,
            profile=ctx.obj.profile)

    elif edit:
        ctx.obj.config.edit_config_file()

    else:
        for kw in ctx.obj.api.REQUIRED_USER_CONFIG:
            if kw not in ctx.obj.api.user_config:
                raise KeyError(
                    'Required configuration option "{}" not supplied. '
                    'Use --helper to configure interactively'.format(kw))

    ctx.obj.config.write_config()


@cli.command(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True))
@click.argument('archive_name')
@click.option('--authority_name', envvar='AUTHORITY_NAME', default=None)
@click.option('--versioned', envvar='VERSIONED', default=True)
@click.pass_context
def create_archive(ctx, archive_name, authority_name, versioned=True):
    kwargs = parse_args_as_kwargs(ctx.args)
    var = ctx.obj.api.create_archive(
        archive_name,
        authority_name=authority_name,
        versioned=versioned,
        metadata=kwargs)

    verstring = 'versioned archive' if versioned else 'archive'
    click.echo('created {} {}'.format(verstring, var))


@cli.command(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True))
@click.argument('archive_name')
@click.argument('filepath')
@click.option('--bumpversion', envvar='BUMPVERSION', default='patch')
@click.option('--prerelease', envvar='PRERELEASE', default=None)
@click.option('--dependency', multiple=True)
@click.pass_context
def upload(ctx, archive_name, filepath, bumpversion='patch', prerelease=None, dependency=None):
    kwargs = parse_args_as_kwargs(ctx.args)
    dependencies_dict = parse_dependencies(dependency)

    var = ctx.obj.api.get_archive(archive_name)
    latest_version = var.get_latest_version()

    var.update(filepath, bumpversion=bumpversion, prerelease=prerelease, dependencies=dependencies_dict, **kwargs)
    new_version = var.get_latest_version()

    
    if new_version != latest_version:
        bumpmsg = ' version bumped {} --> {}.'.format(
            latest_version, new_version)

    elif var.versioned:
        bumpmsg = ' version remains {}.'.format(latest_version)
    else:
        bumpmsg = ''

    click.echo('uploaded data to {}.{}'.format(var, bumpmsg))


@cli.command(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True))
@click.argument('archive_name')
@click.pass_context
def update_metadata(ctx, archive_name):
    kwargs = parse_args_as_kwargs(ctx.args)

    var = ctx.obj.api.get_archive(archive_name)

    var.update_metadata(metadata=kwargs)



@cli.command(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True))
@click.argument('archive_name')
@click.option('--version')
@click.option('--dependency', multiple=True)
@click.pass_context
def set_dependencies(ctx, archive_name, version=None, dependency=None):
    kwargs = parse_dependencies(dependency)

    var = ctx.obj.api.get_archive(archive_name)

    var.set_dependencies(version=version, dependencies=kwargs)


@cli.command()
@click.argument('archive_name')
@click.argument('filepath')
@click.option('--version', envvar='VERSION', default=None)
@click.pass_context
def download(ctx, archive_name, filepath, version):
    var = ctx.obj.api.get_archive(archive_name)

    if version is None:
        version = var.get_default_version()


    var.download(filepath, version=version)

    archstr = var.archive_name +\
        '' if (not var.versioned) else ' v{}'.format(version)

    click.echo('downloaded {} to {}'.format(archstr, filepath))


@cli.command()
@click.argument('archive_name')
@click.pass_context
def metadata(ctx, archive_name):
    var = ctx.obj.api.get_archive(archive_name)
    click.echo(pprint.pformat(var.get_metadata()))


@cli.command()
@click.argument('archive_name')
@click.pass_context
def history(ctx, archive_name):
    var = ctx.obj.api.get_archive(archive_name)
    click.echo(pprint.pformat(var.get_history()))


@cli.command()
@click.argument('archive_name')
@click.pass_context
def versions(ctx, archive_name):
    var = ctx.obj.api.get_archive(archive_name)
    click.echo(pprint.pformat(map(str, var.get_versions())))


@cli.command()
@click.option('--prefix', envvar='PREFIX', default='')
@click.pass_context
def list(ctx, prefix):
    archives = ctx.obj.api.archives
    res = [
        var.archive_name 
        for var in archives if var.archive_name.startswith(prefix)]

    click.echo(res)


if __name__ == "__main__":
    cli()
