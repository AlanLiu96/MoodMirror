from __future__ import absolute_import

import os
import sys

import config
from google.cloud import storage


def _get_storage_client():
    return storage.Client(project=config.PROJECT_ID)


def upload(fileStream, filename):
    client = _get_storage_client()
    bucket = client.get_bucket(config.CLOUD_STORAGE_BUCKET)
    blob = bucket.blob(filename)

    blob.upload_from_string(fileStream)

    blob.make_public()

    url = blob.public_url
    print(url)

# curPath = os.path.dirname(os.path.realpath(__file__))

# fname = sys.argv[1]
# fpath = os.path.join(curPath, fname)
# print(fpath)

# try:
#     f = open(fpath, 'r')
# except:
#     print('cannot open file')
#     sys.exit(0)

# fileStream = f.read()

# upload(fileStream, 'test')

# f.close()
