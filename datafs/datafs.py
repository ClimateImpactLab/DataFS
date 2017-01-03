# -*- coding: utf-8 -*-

from __future__ import absolute_import
from datafs.core.data_api import DataAPI
from datafs.config.config_file import ConfigFile
from datafs.config.constructor import APIConstructor
import os
import click
import yaml
import pprint
import requirements as requirement_parser


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


class DataFSInterface(object):

    def __init__(self, config={}, api=None, config_file=None, profile=None):
        self.config = config
        self.api = api
        self.config_file = config_file




#this sets the command line environment for 
@click.group()
@click.option('--config-file', envvar='CONFIG_FILE', type=str)
@click.option('--requirements', envvar='REQUIREMENTS', type=str)
@click.option('--profile', envvar='PROFILE', type=str, default=None)
@click.pass_context
def cli(ctx, config_file=None, requirements=None, profile=None):

    ctx.obj = DataFSInterface()

    ctx.obj.config_file = config_file

    config = ConfigFile(ctx.obj.config_file)
    config.read_config()

    if requirements is None:
        requirements = config.config.get('requirements', None)

    if requirements is not None:
        ctx.obj.requirements = dict(map(
            lambda tup: tuple(tup[:1]), requirement_parser.parse(requirements)))

    else:
        ctx.obj.requirements = {}


    ctx.obj.config = config

    if profile is None:
        profile = config.config['default-profile']

    ctx.obj.profile = profile

    profile_config = ctx.obj.config.get_profile_config(ctx.obj.profile)

    api = APIConstructor.generate_api_from_config(profile_config)

    APIConstructor.attach_manager_from_config(api, profile_config)
    APIConstructor.attach_services_from_config(api, profile_config)
    APIConstructor.attach_cache_from_config(api, profile_config)

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
                    'Required configuration option "{}" not supplied. Use --helper to configure interactively'.format(kw))

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
    reqs = ctx.obj.requirements.get(archive_name, None)
    var = ctx.obj.api.create_archive(
        archive_name,
        authority_name=authority_name,
        versioned=versioned,
        metadata=kwargs,
        default_version=reqs)

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
@click.pass_context
def upload(ctx, archive_name, filepath, bumpversion='patch', prerelease=None):
    kwargs = parse_args_as_kwargs(ctx.args)

    reqs = ctx.obj.requirements.get(archive_name, None)
    var = ctx.obj.api.get_archive(archive_name, default_version=reqs)
    latest_version = var.latest_version

    var.update(filepath, bumpversion=bumpversion, prerelease=prerelease, **kwargs)
    new_version = var.latest_version
    
    if new_version != latest_version:
        bumpmsg = ' version bumped {} --> {}.'.format(latest_version, new_version)
    elif var.versioned:
        bumpmsg = ' version remains {}.'.format(latest_version)
    else:
        bumpmsg = ''

    click.echo('uploaded data to {}.{}'.format(var, bumpmsg))


@cli.command()
@click.argument('archive_name')
@click.argument('filepath')
@click.option('--version', envvar='VERSION', default=None)
@click.pass_context
def download(ctx, archive_name, filepath, version):
    reqs = ctx.obj.requirements.get(archive_name, None)
    var = ctx.obj.api.get_archive(archive_name, default_version=reqs)

    if version is None:
        version = var.latest_version

    var.download(filepath, version=version)

    archstr = var.archive_name +\
        '' if (not var.versioned) else ' v{}'.format(version)

    click.echo('downloaded {} to {}'.format(archstr, filepath))


@cli.command()
@click.argument('archive_name')
@click.pass_context
def metadata(ctx, archive_name):
    reqs = ctx.obj.requirements.get(archive_name, None)
    var = ctx.obj.api.get_archive(archive_name, default_version=reqs)
    click.echo(pprint.pformat(var.metadata))


@cli.command()
@click.argument('archive_name')
@click.pass_context
def history(ctx, archive_name):
    reqs = ctx.obj.requirements.get(archive_name, None)
    var = ctx.obj.api.get_archive(archive_name, default_version=reqs)
    click.echo(var.history)


@cli.command()
@click.argument('archive_name')
@click.pass_context
def versions(ctx, archive_name):
    reqs = ctx.obj.requirements.get(archive_name, None)
    var = ctx.obj.api.get_archive(archive_name, default_version=reqs)
    click.echo(pprint.pformat(map(str, var.versions)))


@cli.command()
@click.option('--prefix', envvar='PREFIX', default='')
@click.pass_context
def list(ctx, prefix):
    archives = ctx.obj.api.archives
    res = [
        var.archive_name for var in archives if var.archive_name.startswith(prefix)]
    click.echo(res)


if __name__ == "__main__":
    cli()
