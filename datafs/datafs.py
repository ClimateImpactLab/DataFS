# -*- coding: utf-8 -*-

from __future__ import absolute_import
from datafs.core.data_api import DataAPI
from datafs.cli.config import Config
import os 
import argparse
import click
import yaml



def _download(args):
    #DataAPI.download(args)
    print('Your Archive named {} is being downloaded to {}'.format(args.archive_name, args.download_path))

class Uploader(object):
    def __init__(self, metadata={}):
        self.metadata = metadata

    def upload(self, args):
        
        
        if args.helper:
            metadata = _get_metadata(self.metadata)

        #DataAPI.update(args, metadata)
        print('Your Archive named {} is being uploaded to DataAPI.authority in location DataAPI.ser with metadata: {}'.format(args.archive_name, metadata))
        print(metadata)

    

class CreateArchive(object):
    def __init__(self,metadata={}):
        self.metadata = metadata


    def create(self,args):

        if args.helper:
            metadata = _get_metadata(self.metadata)
            print(metadata)
        #api_constructor.create_archive(args)
        print('Your Archive named {} is being created to DataAPI.authority in location DataAPI.ser with metadata: {}'.format(args.archive_name, metadata))

    


def _list_archvies(args):
    #DataAPI.archives(args)
    print(args)

def _metadata(args):
    #DataAPI.managers.get_metadata(args)
    print(args)



def _get_metadata(metadata):

    #set default
    interactive = {k: click.prompt(v, type=str, default='None') for k, v in metadata.items()}
    return interactive


#initialize and mock out a config 
#this will change but needed to see how this could work
def initialize_api_settings(api_constructor=DataAPI):


    username = click.prompt('Please enter a username', type=str)
    contact = click.prompt('Please enter contact info', type=str)
    
    api = DataAPI(username=username, contact=contact)
    return api

    
def main(api_constructor=DataAPI, sysArgs=None):

    api = initialize_api_settings(DataAPI)

    parser = argparse.ArgumentParser('Command Line tools for DataFS')


    actions = parser.add_subparsers(help='actions to perform on datafiles')

    #specify the list of arguments we need
    download = actions.add_parser('download', help='Download an archive')
    download.add_argument('archive_name',default=None, help='Name of Archive/data_file')
    download.add_argument('download_path', help='Path to your destination directory')


    #some sort of confirmation to let them know the file is downloading
    #some arguments to add
    #
    download.set_defaults(func=_download)

    #another action
    upload= actions.add_parser('upload', help='Upload an archive')
    upload.add_argument('archive_name', default=None, help='Name of Archive/data_file')
    upload.add_argument('--username', default='DataAPI.username', help='Your username')
    upload.add_argument('--contact', default='DataAPI.contact', help='Your contact info')
    upload.add_argument('upload_path', help='Path to your destination directory')

    for kw, desc in api_constructor._api_metadata.items():
        upload.add_argument('--{}'.format(kw), help=desc)

    upload.add_argument('--helper', help='Run interactive upload helper', action='store_true')
    #how to create a metadata subparser so that it will 


    #some more arguments
    



    uploader = Uploader(metadata=api_constructor._api_metadata)

    upload.set_defaults(func=uploader.upload)

    #another acttion
    create = actions.add_parser('create', help='Create an archive')
    create.add_argument('archive_name',default=None, help='Name of Archive/data_file')
    create.add_argument('--username', default='Big Pete', help='Your username')
    create.add_argument('--contact', default='Big_Pete_', help='Your contact info')
    create.add_argument('local_path', default=None, help='Path to directory where file is located')
    
    for kw, desc in api_constructor._api_metadata.items():
        create.add_argument('--{}'.format(kw), help=desc)

    create.add_argument('--helper', help='Run interactive create helper', action='store_true')

    creater = CreateArchive(metadata=api_constructor._api_metadata)
    #some more required arguments
    #
    create.set_defaults(func=creater.create)

    #another action
    metadata = actions.add_parser('metadata', help='view metadata for an archive')
    metadata.add_argument('archive_name', default=None, help='Name of Archive/data_file')


    metadata.set_defaults(fun=_metadata)
    #another action
    _list = actions.add_parser('list', help='List all archives')
    _list.add_argument('table_name', default=None, help='Table that stores all values')


    _list.set_defaults(func=_list_archvies)

    if sysArgs is None:
        args = parser.parse_args()

    else: 
        args = parser.parse_args(sysArgs)
    
    args.func(args)



class DataFSInterface(object):
    def __init__(self, config, api):
        self.config = config
        self.api = api


@click.group()
@click.option('--config-file', envvar='CONFIG_FILE', type=str)
@click.pass_context
def cli(ctx, config_file=None):
    
    if config_file is not None:
        addl_config = [config_file]
    else:
        addl_config = []

    config = Config()
    config.read_config(addl_config)
    api = config.generate_api_from_config()
    ctx.obj = DataFSInterface(config, api)

@click.command()
@click.pass_context
def configure(ctx):
    '''
    Update existing configuration or create a new default profile
    '''
    pass


@cli.command(context_settings=dict(ignore_unknown_options=True,allow_extra_args=True))
@click.argument('archive_name')
@click.option('--authority_name', envvar='AUTHORITY_NAME', default=None)
@click.pass_context
def create_archive(ctx, archive_name, authority_name):
    kwargs = {ctx.args[i][2:]: ctx.args[i+1] for i in xrange(0, len(ctx.args), 2)}
    var = ctx.obj.api.create_archive(archive_name, authority_name=authority_name, **kwargs)
    click.echo('created archive {}'.format(var))


@cli.command(context_settings=dict(ignore_unknown_options=True,allow_extra_args=True))
@click.argument('archive_name')
@click.argument('filepath')
@click.pass_context
def upload(ctx, archive_name, filepath):
    kwargs = {ctx.args[i][2:]: ctx.args[i+1] for i in xrange(0, len(ctx.args), 2)}
    var = ctx.obj.api.get_archive(archive_name)
    var.update(filepath, **kwargs)
    click.echo('uploaded data to {}'.format(var))


@cli.command
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
    click.echo(var.metadata)


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




