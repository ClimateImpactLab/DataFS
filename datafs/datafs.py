# -*- coding: utf-8 -*-

from __future__ import absolute_import
#from datafs.core.data_api import DataAPI
import os 
import argparse
import getpass


CACHE='path/to/cache/dir'


def _download(args):
	#DataAPI.download(args)
	print('Your Archive named {} is being downloaded to {}'.format(args.archive_name, args.download_path))

def _upload(args):
	#DataAPI.upload(args)
	print('Your Archive named {} is being uploaded to DataAPI.authority in location DataAPI.ser'.format(args.archive_name, args.download_path))
	

def _create(args):
	#DataAPI.create_archive(args)
	print(args)

def _list_archvies(args):
	#DataAPI.archives(args)
	print(args)

def _metadata(args):
	#DataAPI.managers.get_metadata(args)
	print(args)

def main(sysArgs=None):

	

	parser = argparse.ArgumentParser('Command Line tools for DataFS')


	actions = parser.add_subparsers(help='actions to perform on datafiles')

	#specify the list of arguments we need
	download = actions.add_parser('download', help='Download an archive')
	download.add_argument('archive_name',default=None, help='Name of Archive/data_file')
	download.add_argument('download_path', help='Path to your default cache directory')


	#some sort of confirmation to let them know the file is downloading
	#some arguments to add
	#
	download.set_defaults(func=_download)

	#another action
	upload= actions.add_parser('upload', help='Upload an archive')
	upload.add_argument('archive_name', default=None, help='Name of Archive/data_file')
	upload.add_argument('--username', default='DataAPI.username', help='Your username')
	upload.add_argument('--contact', default='DataAPI.contact', help='Your contact info')
	upload.add_argument('--service_path', default='DataArchive.service_path', help='bucket/service_path for object')
	upload.add_argument('--metadata', default=None, help='Archive metadata')
	#how to create a metadata subparser so that it will 


	#some more arguments
	#
	upload.set_defaults(func=_upload)

	#another acttion
	create = actions.add_parser('create', help='Create an archive')
	create.add_argument('archive_name',default=None, help='Name of Archive/data_file')
	create.add_argument('--username', default='Big Pete', help='Your username')
	create.add_argument('--contact', default='Big_Pete_', help='Your contact info')
	upload.add_argument('--service_path', default='DataArchive.service_path', help='bucket/service_path for object')
	create.add_argument('--metadata', default=None, help='Archive metadata')
	#some more required arguments
	#
	create.set_defaults(func=_create)

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


if __name__ == "__main__":
    main()




