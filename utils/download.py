#!/usr/bin/env python3

from pygit2 import clone_repository
import os
import logging
import requests


class StatusCodeError(Exception):
	''' Error for requests module,  status return code.'''
	pass

class Downloader():
	''' Downloader for Github repos and binaries ''' 

	def __init__(self, dest_dir):
		self.dest_dir = dest_dir

	
	def save_file(self, filepath, response):
		'''  
		Save binary file from 'Requests' via chucks.
		arg(s): filepath:str, response: class 'requests.models.Response
		'''
		
		with open(filepath, 'wb') as f1:
			for chunk in response.iter_content(chunk_size=1024):
				if chunk:
					f1.write(chunk)
		return f1.name


	def filepath(self, url):
		''' 
		Return filepath. args(s) url:str 
		'''

		# Parse url for filename.
		filename = url.split("/")[-1]
		# Define filepath
		filepath = os.path.join(self.dest_dir, filename)
		if os.path.isfile(filepath):
			raise FileExistsError(f"'{filepath}' exists and is not an empty directory! ")

		return filepath

	
	def get_gitrepo(self, url):
		''' 
		Clone a Github repo to the local filesystem.
		arg(s): url:str
		'''

		# Define local filepath.
		filepath = self.filepath(url)
		# Clone remote repo to local filesystem.
		clone_repository(url, filepath)

		return filepath

	
	def get_binary(self, url):
		''' 
		Download a binary file to the local filesystem. 
		arg(s): url:str 
		'''

		# Define local filepath.
		filepath = self.filepath(url)

		# Request URL.
		res = requests.get(url, stream=True)

		# Raise if not 200 OK / 302 REDIRECT.
		if not res.status_code == 200 or\
		 res.status_code == 302:
			raise StatusCodeError(f"'{url}' Responded with '{res.status_code}' ")
		# Debugging.
		contentlen = res.headers['Content-length']
		logging.debug(f'Request: {url}')
		logging.debug(f'Content-length: {contentlen}')
		logging.debug(f'Response: {res.status_code}')
		# Save response as binary file.
		filename = self.save_file(filepath, res)

		return filename