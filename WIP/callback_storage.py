# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys


def callback_data(request):
	# [START functions_callback_data]
	"""HTTP Cloud Function.
  Args:
       data (dict): The dictionary with data specific to the given event.
       context (google.cloud.functions.Context): The Cloud Functions event
       metadata.
  """
	import os
	import json
	import base64
	import datetime
	from flask import abort
	from rfc3339 import rfc3339
	from google.cloud import datastore, pubsub_v1, storage

	def upload_blob(bucket_name, blob_text, destination_blob_name):
		"""Uploads a file to the bucket."""
		storage_client = storage.Client()
		bucket = storage_client.get_bucket(bucket_name)
		blob = bucket.blob(destination_blob_name)

		blob.upload_from_string(blob_text)

		print('File uploaded to {}.'.format(destination_blob_name))

	if request.method == 'POST':
		http_user = os.environ.get('HTTP_USER')
		http_passwd = os.environ.get('HTTP_PASSWD')
		request_user = request.authorization["username"]
		request_passwd = request.authorization["password"]

		if request_user == http_user and request_passwd == http_passwd:

			from google.cloud import storage

			BUCKET_NAME = 'wyschc'

			print("Creating blob")

			BLOB_NAME = 'test-blob'
			BLOB_STR = '{"blob": "some json"}'

			print("Uploading blob")

			upload_blob(BUCKET_NAME, BLOB_STR, BLOB_NAME)

			print("Success!")

			return '', 204
		else:
			print('Invalid HTTP Basic Authentication: '
				  '{}'.format(request.authorization))
			return abort(401)
	else:
		print('Invalid HTTP Method to invoke Cloud Function. '
			  'Only POST supported')
		return abort(405)
	# [END functions_callback_data]

