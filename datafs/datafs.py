# -*- coding: utf-8 -*-
import os 
import argparse
from datafs.core.data_api import DataAPI


def _download(args):
	DataAPI.download(args)

def _upload(args):
	DataAPI.upload(args)

def _create(args):
	DataAPI.create_archive(args)

def _list_archvies(args):
	DataAPI.archives(args)

def _metadata(args):
	DataAPI.managers.get_metadata(args)


def main(sysArgs=None):
	parser = argparse.ArgumentParser('Command Line tools for DataFS')


	actions = parser.add_subparsers(help='actions to perform on datafiles')

	#specify the list of arguments we need
	download = actions.add_parser('download', help='Download an archive')
	download.add_argument('--archive_name', required=True, nargs=1,default=None, help='Name of Archive/data_file')
	#some arguments to add
	#
	download.set_defaults(func=_download)

	#another action
	upload= actions.add_parser('upload', help='Upload an archive')
	upload.add_argument('--archive_name', required=True, nargs=1,default=None, help='Name of Archive/data_file')
	#some more arguments
	#
	upload.set_defaults(func=_upload)

	#another acttion
	create = actions.add_parser('create', help='Create an archive')
	create.add_argument('--archive_name', required=True, nargs=1,default=None, help='Name of Archive/data_file')
	#some more required arguments
	#
	create.set_defaults(func=_create)

	#another action
	metadata = actions.add_parser('metadata', help='view metadata for an archive')
	metadata.add_argument('--archive_name', required=True, nargs=1,default=None, help='Name of Archive/data_file')


	metadata.set_defaults(fun=_metadata)
	#another action
	_list = actions.add_parser('list', help='List all archives')
	_list.add_argument('--table_name', required=True, nargs=1, default=None, help='Table that stores all values')


	_list.set_defaults(func=_list_archvies)


	if sysargs is None:
	        args = parser.parse_args()
	    else:
	        args = parser.parse_args(sysargs)

	    args.func(args)



if __name__ == "__main__":
    main()




