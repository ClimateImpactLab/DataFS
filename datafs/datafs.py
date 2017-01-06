# -*- coding: utf-8 -*-

from __future__ import absolute_import
from datafs.core.data_api import DataAPI
from datafs.config.config_file import ConfigFile
from datafs.config.helpers import (
    get_api, 
    _parse_requirement, 
    _interactive_config)

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

    if profile is None:
        profile = self.default_profile

    profile_config = config.get_profile_config(profile)

    #read from the required config settings in DataAPI
    _interactive_config(
        to_populate=profile_config['api']['user_config'], 
        prompts=api.manager.required_user_config)

    config.config['profiles'][profile] = profile_config

def parse_dependencies(dependency_args):
    
    if len(dependency_args) == 0: 
        return None

    # dependencies = {}
    return dict(map(_parse_requirement, dependency_args))

class DataFSInterface(object):

    def __init__(self):
        pass

#this sets the command line environment for 
@click.group()
@click.option('--config-file', envvar='DATAFS_CONFIG_FILE', type=str)
@click.option('--requirements', envvar='DATAFS_REQUIREMENTS_FILE', type=str, default='requirements_data.txt')
@click.option('--profile', envvar='DATAFS_DEFAULT_PROFILE', type=str, default=None)
@click.pass_context
def cli(ctx, config_file=None, requirements='requirements_data.txt', profile=None):

    ctx.obj = DataFSInterface()

    ctx.obj.config_file = config_file
    ctx.obj.config = ConfigFile(ctx.obj.config_file)

    ctx.obj.requirements = requirements
    ctx.obj.profile = profile

    @ctx.call_on_close
    def teardown():
        if hasattr(ctx.obj, 'api'):
            ctx.obj.api.close()

def generate_api(ctx):


    ctx.obj.config.read_config()

    if ctx.obj.profile is None:
        ctx.obj.profile = ctx.obj.config.config['default-profile']

    ctx.obj.api = get_api(
        profile=ctx.obj.profile, 
        config_file=ctx.obj.config_file, 
        requirements=ctx.obj.requirements)


@cli.command(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True))
@click.option('--helper', is_flag=True)
@click.option('--edit', is_flag=True)
@click.pass_context
def configure(ctx, helper, edit):
    '''
    Update existing configuration or create a new default profile
    '''


    if edit:
        ctx.obj.config.edit_config_file()
        return

    generate_api(ctx)

    kwargs = {ctx.args[i][2:]: ctx.args[i + 1]
              for i in xrange(0, len(ctx.args), 2)}
    ctx.obj.config.config['profiles'][ctx.obj.profile][
        'api']['user_config'].update(kwargs)

    ctx.obj.api.user_config.update(kwargs)

    if helper:
        interactive_configuration(
            ctx.obj.api,
            ctx.obj.config,
            profile=ctx.obj.profile)

    else:
        for kw in ctx.obj.api.manager.required_user_config:
            if kw not in ctx.obj.api.user_config:
                raise KeyError(
                    'Required configuration option "{}" not supplied. '
                    'Use --helper to configure interactively'.format(kw))

    ctx.obj.config.write_config(ctx.obj.config_file)


@cli.command(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True))
@click.argument('archive_name')
@click.option('--authority_name', default=None)
@click.option('--versioned', default=True)
@click.option('--helper', is_flag=True)
@click.pass_context
def create_archive(ctx, archive_name, authority_name, versioned=True, helper=False):
    generate_api(ctx)
    kwargs = parse_args_as_kwargs(ctx.args)
    var = ctx.obj.api.create_archive(
        archive_name,
        authority_name=authority_name,
        versioned=versioned,
        metadata=kwargs,
        helper=helper)

    verstring = 'versioned archive' if versioned else 'archive'
    click.echo('created {} {}'.format(verstring, var))


@cli.command(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True))
@click.argument('archive_name')
@click.argument('filepath')
@click.option('--bumpversion', default='patch')
@click.option('--prerelease', default=None)
@click.option('--dependency', multiple=True)
@click.pass_context
def update(ctx, archive_name, filepath, bumpversion='patch', prerelease=None, dependency=None):
    generate_api(ctx)
    kwargs = parse_args_as_kwargs(ctx.args)
    dependencies_dict = parse_dependencies(dependency)

    var = ctx.obj.api.get_archive(archive_name)
    latest_version = var.get_latest_version()

    var.update(filepath, bumpversion=bumpversion, prerelease=prerelease, dependencies=dependencies_dict, **kwargs)
    new_version = var.get_latest_version()

    if latest_version is None and new_version is not None:
        bumpmsg = ' new version {} created.'.format(
            latest_version, new_version)
    
    elif new_version != latest_version:
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
    generate_api(ctx)
    kwargs = parse_args_as_kwargs(ctx.args)

    var = ctx.obj.api.get_archive(archive_name)

    var.update_metadata(metadata=kwargs)



@cli.command(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True))
@click.argument('archive_name')
@click.option('--dependency', multiple=True)
@click.pass_context
def set_dependencies(ctx, archive_name, dependency=None):
    generate_api(ctx)
    kwargs = parse_dependencies(dependency)

    var = ctx.obj.api.get_archive(archive_name)

    var.set_dependencies(dependencies=kwargs)


@cli.command()
@click.argument('archive_name')
@click.argument('filepath')
@click.option('--version', default=None)
@click.pass_context
def download(ctx, archive_name, filepath, version):
    generate_api(ctx)
    var = ctx.obj.api.get_archive(archive_name)

    if version is None:
        version = var.get_default_version()


    var.download(filepath, version=version)

    archstr = var.archive_name +\
        '' if (not var.versioned) else ' v{}'.format(version)

    click.echo('downloaded {} to {}'.format(archstr, filepath))


@cli.command()
@click.argument('archive_name')
@click.option('--version', default=None)
@click.pass_context
def cat(ctx, archive_name, version):
    generate_api(ctx)
    var = ctx.obj.api.get_archive(archive_name)

    with var.open('r', version=version) as f:
        for chunk in iter(lambda: f_obj.read(1024*1024), ''):
            click.echo(chunk)


@cli.command()
@click.argument('archive_name')
@click.pass_context
def metadata(ctx, archive_name):
    generate_api(ctx)
    var = ctx.obj.api.get_archive(archive_name)
    click.echo(pprint.pformat(var.get_metadata()))


@cli.command()
@click.argument('archive_name')
@click.pass_context
def history(ctx, archive_name):
    generate_api(ctx)
    var = ctx.obj.api.get_archive(archive_name)
    click.echo(pprint.pformat(var.get_history()))


@cli.command()
@click.argument('archive_name')
@click.pass_context
def versions(ctx, archive_name):
    generate_api(ctx)
    var = ctx.obj.api.get_archive(archive_name)
    click.echo(pprint.pformat(map(str, var.get_versions())))


@cli.command()
@click.option('--prefix', default='')
@click.pass_context
def list(ctx, prefix):
    generate_api(ctx)
    archives = ctx.obj.api.archives
    res = [
        var.archive_name 
        for var in archives if var.archive_name.startswith(prefix)]

    click.echo(res)


@cli.command()
@click.argument('archive_name')
@click.pass_context
def delete(ctx, archive_name):
    generate_api(ctx)
    var = ctx.obj.api.get_archive(archive_name)

    var.delete()
    click.echo('deleted archive {}'.format(var))


if __name__ == "__main__":
    cli()
