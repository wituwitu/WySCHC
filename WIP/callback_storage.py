def callback_data(request):

	import sys
	import os
	import json
	import base64
	import datetime
	from flask import abort
	from rfc3339 import rfc3339
	from google.cloud import storage

	def upload_blob(bucket_name, blob_text, destination_blob_name):
		"""Uploads a file to the bucket."""
		storage_client = storage.Client()
		bucket = storage_client.get_bucket(bucket_name)
		blob = bucket.blob(destination_blob_name)
		blob.upload_from_string(blob_text)
		print('File uploaded to {}.'.format(destination_blob_name))

	def read_blob(bucket_name, blob_name):
		storage_client = storage.Client()
		bucket = storage_client.get_bucket(bucket_name)
		blob = bucket.get_blob(blob_name)
		return blob.download_as_string()

	def delete_blob(bucket_name, blob_name):
		storage_client = storage.Client()
		bucket = storage_client.get_bucket(bucket_name)
		blob = bucket.get_blob(blob_name)
		blob.delete()

	if request.method == 'POST':
		http_user = os.environ.get('HTTP_USER')
		http_passwd = os.environ.get('HTTP_PASSWD')
		request_user = request.authorization["username"]
		request_passwd = request.authorization["password"]

		if request_user == http_user and request_passwd == http_passwd:

			BUCKET_NAME = 'wyschc'
			request_dict = request.get_json()
			print('Received Sigfox message: {}'.format(request_dict))

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

