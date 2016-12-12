
from datafs.managers.manager_mongo import MongoDBManager
from datafs import DataAPI
from fs.tempfs import TempFS
from fs.osfs import OSFS
from ast import literal_eval
import os
import tempfile
import shutil

api = DataAPI(
     username='My Name',
     contact = 'my.email@example.com')

manager = MongoDBManager(
    database_name = 'MyDatabase',
    table_name = 'DataFiles')

manager.create_archive_table('DataFiles', raise_if_exists=False)
api.attach_manager(manager)

tmp = tempfile.mkdtemp()
local1 = OSFS(tmp)
api.attach_authority('local1', local1)

var = api.create_archive(
    'my_first_archive',
    metadata = dict(description = 'My test data archive'), 
    authority_name='local1',
    raise_if_exists=False)

var = api.get_archive('my_first_archive')

with var.open('w+') as f:
  res = f.write(u'hello')

with var.open('r') as f:
  print(f.read())

cache = TempFS()

api.attach_cache(cache)
var.cache()


shutil.rmtree(tmp)