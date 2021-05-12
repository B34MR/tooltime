#!/usr/bin/env python3

from concurrent import futures
from functools import wraps
from pygit2 import clone_repository
from utils import richard as r
from utils import cparse as cp
import apt
import os
import requests
import subprocess
import time


# Confgfile values.
GIT_URLS = [k for k in cp.config['github_tools']]
URLS = [k for k in cp.config['url_tools']]
PIP_PACKAGES = [k for k in cp.config['pip_packages']]
APT_PACKAGES = [k for k in cp.config['apt_packages']]
DEST_DIR = ''.join([k for k in cp.config['tools_dir']])


def timeit(method):
	'''Wrapper to calculate execution time'''
	@wraps(method)
	def wrapper(*args, **kargs):
		starttime = time.time()
		result = method(*args, **kargs)
		endtime = time.time()
		print(f'\n')
		r.console.print(f'Completed in: {(endtime-starttime)*1000} ms')

		return result
	return wrapper


class StatusCodeError(Exception):
	''' Error for requests module,  status return code.'''
	pass


class PackageExistsError(Exception):
	''' Error for apt module, package exists.'''
	pass


class Downloader():
	''' ''' 

	def __init__(self, dest_dir):
		self.dest_dir = dest_dir

	
	def filepath(self, url):
		''' 
		Return filepath. args(s) url:str 
		'''

		# Parse url for filename.
		filename = url.split("/")[-1]
		# Define filepath
		return os.path.join(self.dest_dir, filename)

	
	def get_git(self, url):
		''' 
		Requests a Github repo and download contents to the local filesystem.
		arg(s): url:str, dest_dir:str 
		'''

		# Define local filepath.
		filepath = self.filepath(url)
		# Clone remote repo to local filesystem.
		clone_repository(url, filepath)

		return filepath

	
	def get_url(self, url):
		''' 
		Requests a URL and download contents to the local filesystem. 
		arg(s): url:str, dest_dir:str
		'''

		# Define local filepath.
		filepath = self.filepath(url)
		# Check if filepath exists before downloading.
		if os.path.isfile(filepath):
			raise FileExistsError(f"'{filepath}' exists and is not an empty directory ")

		# Request URL.
		req = requests.get(f'{url}', stream=True)

		# Raise if not 200 OK / 302 REDIRECT.
		if not req.status_code == 200 or\
		 req.status_code == 302:
			raise StatusCodeError(f"'{url}' Responded with '{req.status_code}' ")

		# Get content-length
		r_contentlen = req.headers['Content-length']
		# Print requests and response code.
		r.logging.info(f'Request: {url}')
		r.logging.info(f'Content-length: {r_contentlen}')
		r.logging.info(f'Response: {req.status_code}')
		
		# Save file as binary via chucks.
		with open(filepath, 'wb') as f1:
			for chunk in req.iter_content(chunk_size=1024):
				if chunk:
					f1.write(chunk)
		return f1.name


downloader = Downloader(DEST_DIR)

result1 = downloader.get_git(url='https://github.com/cddmp/enum4linux-ng')
print(result1)

result2 = downloader.get_url(url='https://github.com/ropnop/kerbrute/releases/download/v1.0.3/kerbrute_linux_amd64')
print(result2)

exit()


def get_git(url, dest_dir):
	'''
	Requests a Github repo and download contents to the local filesystem.
	arg(s):
	- url:str
	- dest_dir:str
	'''
	
	# Parse url for filename.
	filename = f'{url.split("/")[-1]}'
	# Define filepath
	repo_path = f'{dest_dir}/{filename}'
	# Clone remote repo to local filesystem.
	repo = clone_repository(url, repo_path)
	
	return repo_path


def get_url(url, dest_dir):
	''' 
	Requests a URL and download contents to the local filesystem.
	arg(s):
	- url:str
	- dest_dir:str
	'''

	# Parse url for filename.
	filename = url.split("/")[-1]
	# Define filepath
	filepath = os.path.join(dest_dir, filename)

	# Check if file exists before downloading.
	if os.path.isfile(filepath):
		raise FileExistsError(f"'{filepath}' exists and is not an empty directory ")

	# Request URL.
	req = requests.get(f'{url}', stream=True)

	# Raise if not 200 OK / 302 REDIRECT.
	if not req.status_code == 200 or\
	 req.status_code == 302:
		raise StatusCodeError(f"'{url}' Responded with '{req.status_code}' ")

	# Get content-length
	r_contentlen = req.headers['Content-length']
	# Print requests and response code.
	r.logging.info(f'Request: {url}')
	r.logging.info(f'Content-length: {r_contentlen}')
	r.logging.info(f'Response: {req.status_code}')
	
	# Save file as binary via chucks.
	with open(filepath, 'wb') as f1:
		for chunk in req.iter_content(chunk_size=1024):
			if chunk:
				f1.write(chunk)
	return f1.name


def is_installed(package):
	''' 
	Used in get_pip(), returns boolean based on package's installed status.
	arg(s):
	- packages:str 
	'''
	
	try:
		result = subprocess.run(['pip', 'show', package],
			shell=False,
			check=False,
			capture_output=True,
			text=True)
	except Exception as e:
		# Set check=True for the exception to catch.
		r.logging.exception(f'{e}')
		pass
	else:
		if f'WARNING: Package(s) not found: {package}' in result.stderr:
			return False
		else:
			return True


@timeit
def get_pip(packages):
	'''
	Download and install packages for Pip.
	arg(s):
	- packages:lst
	'''

	with r.console.status(status=f'[txt.spinner]Processing...') as status:
		for package in packages:
			if is_installed(package):
				r.logging.warning(f'Package already installed: {package}')
			else:
				try:
					result = subprocess.run(['pip', 'install', package],
						shell=False,
						check=False,
						capture_output=True,
						text=True)
					r.console.log(result.stderr)
					r.console.log(result.stdout)
				except Exception as e:
					# Set check=True for the exception to catch.
					r.logging.exception(f'{e}')
					pass #raise e


@timeit
def get_apt(packages):
	''' 
	Download and install packages for APT.
	arg:
	- packages:lst
	'''

	cache = apt.cache.Cache()
	cache.update()
	cache.open()

	for package in packages:
		try:
			apt_package = cache[package]
			if apt_package.is_installed:
				raise PackageExistsError(f'Package already installed: {apt_package}')
			else:
				apt_package.mark_install()
				cache.commit()
				r.console.log(f'Installed: {cache.get_changes()}')
		except Exception as e:
			r.logging.warning(f'{e}')
			pass #raise e


@timeit
def make_threaded(func, urls, dest_dir):
	''' Threaded func for get_git() and get_url()'''

	with r.console.status(status=f'[txt.spinner]Downloading') as status:
		# Executor-pool used with content manager to ensure threads are cleaned up promptly.
		with futures.ThreadPoolExecutor() as executor:
			# Load operations and mark each future with its URL.
			future_to_url = {executor.submit(func, url, dest_dir): url for url in urls}
			# Obtain results as they're completed.
			for future in futures.as_completed(future_to_url):
				url = future_to_url[future]
				try:
					data = future.result()
				except Exception as e:
					r.logging.warning(f'{e}')
				else:
					r.console.log(f'{data}')


@timeit
def main():
	''' Main func '''

	# Pause, mainly used for testing.
	r.ctrl_c()
	
	# Github-Downloads.
	r.banner('Github Downloads')
	make_threaded(get_git, GIT_URLS, DEST_DIR)

	# URL-Downloads.
	r.banner('URL Downloads')
	make_threaded(get_url, URLS, DEST_DIR)

	# Pip Download/Install.
	r.banner('Pip Downloads/Installs')
	get_pip(PIP_PACKAGES)

	# APT Download/Install.
	r.banner('APT Downloads/Installs')
	get_apt(APT_PACKAGES)


if __name__ == '__main__':
	main()
