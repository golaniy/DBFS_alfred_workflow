from argparse import ArgumentParser
import logging
import os
import json
from databricks_cli.sdk.api_client import ApiClient
from databricks_cli.dbfs.api import DbfsApi
from databricks_cli.dbfs.dbfs_path import DbfsPath
from pathlib import Path


BLANK_ITEM = {
        "type": "default",
        "title": "",
        "subtitle": "",
        "arg": "",
        "autocomplete": "",
        "match": "",
        "icon": None
}
FOLDER_ICON = {
            "path": "./folder.icns"
                }

FILE_ICON = {
            "path": "./file.icns"
                }

api_client = ApiClient(
  host  = os.getenv('DATABRICKS_HOST'),
  token = os.getenv('DATABRICKS_TOKEN')
)

dbfs_api = DbfsApi(api_client)


def get_dir(path = None):
  if path is None:
    dbfs_source_file_path = 'dbfs:/'
  else:
    dbfs_source_file_path = path
  
  dbfs_path = DbfsPath(dbfs_source_file_path)
  result = []
  dirs = dbfs_api.list_files(dbfs_path)
  
  for dir in dirs:
    is_folder = False
    if dir.is_dir:
      is_folder = True
      
    dir_item = BLANK_ITEM.copy()
    dir_item['title'] = dir.dbfs_path.basename
    dir_item['subtitle'] = dir.dbfs_path.absolute_path
    dir_item['match'] = dir.dbfs_path.absolute_path
    dir_item['autocomplete'] = dir.dbfs_path.absolute_path
    
    dir_item['icon'] = FOLDER_ICON if is_folder else FILE_ICON
    dir_item['arg'] = dir.dbfs_path.absolute_path+'/' if is_folder else dir.dbfs_path.absolute_path

    result.append(dir_item)
  alfred_filter = {'items': result}
  print(json.dumps(alfred_filter))

def download_file(file):
  dbfs_path = DbfsPath(file)
  downloads_path = str(Path.home() / "Downloads") + '/'
  local_path = downloads_path + dbfs_path.basename
  
  def check_and_rename(file, add=0):
    original_file = file
    if add != 0:
        split = file.split(".")
        part_1 = split[0] + "_" + str(add)
        file = ".".join([part_1, split[1]])
    if not os.path.isfile(file):
        return file
    else:
        add = add + 1
        return check_and_rename(original_file, add)

  local_path = check_and_rename(local_path)
  
  dbfs_api.get_file(dbfs_path, local_path, overwrite=False)
  logging.log(msg = local_path, level=logging.ERROR)
  print(local_path)

if __name__ == "__main__":
  parser = ArgumentParser(prog='dfbs_alfred_workflow')
  parser.add_argument('-p', type=str, required=False, default=None, nargs='?')
  parser.add_argument('-f', type=str, required=False)


  args = parser.parse_args()
  logging.log(msg = args, level=logging.ERROR)
  if args.f is not None:
    download_file(args.f)
  else:
    get_dir(args.p)