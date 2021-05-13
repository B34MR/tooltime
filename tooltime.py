#!/usr/bin/env python3

from concurrent import futures
from functools import wraps
# To rename r to Console.
from utils import richard as r
from utils import cparse as cp
from utils import download
# To deprecate.
import time
import logging
import apt
import subprocess


# Confgfile values.
GITHUB_URLS = [k for k in cp.config['github_urls']]
BINARY_URLS = [k for k in cp.config['binary_urls']]
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


class PackageExistsError(Exception):
	''' Error for apt module, package exists.'''
	pass


class Installer():
	''' Installer for Pip and Apt packages. '''

	def __init__(self):
		pass


	def is_installed(self, package, cmd='pip show'):
		''' 
		Return bool for Pip package status. 
		arg(s): packages:str  
		'''

		cmd = cmd.split(' ')
		cmd.append(package)
		warning_msg = f'WARNING: Package(s) not found: {package}'

		try:
			result = subprocess.run(cmd,
				shell=False,
				check=False,
				capture_output=True,
				text=True)
		except subprocess.CalledProcessError as e:
			# Set check=True for the exception to catch.
			logging.exception(f'{e}')
			pass
		else:
			if warning_msg in result.stderr:
				return False
			else:
				logging.debug(result.stdout)
				return True


	def pip_install(self, package, cmd='pip install'):
		''' 
		Install Pip packages. arg(s):package:str
		'''

		cmd = cmd.split(' ')
		cmd.append(package)

		if self.is_installed(package) == True:
			logging.info(f'Package already installed: {package}')
		else:
			try:
				result = subprocess.run(cmd,
					shell=False,
					check=False,
					capture_output=True,
					text=True)
			except subprocess.CalledProcessError as e:
				# Set check=True for the exception to catch.
				logging.exception(f'{e}')
				pass
			else:
				logging.info(result.stdout)
				logging.warning(result.stderr)

	
	def apt_install(self, package):
		''' 
		Install packages for apt. arg(s): packages:lst 
		'''

		cache = apt.cache.Cache()
		cache.update()
		cache.open()

		try:
			apt_package = cache[package]
			if apt_package.is_installed:
				raise PackageExistsError(f'Package already installed: {apt_package}')
			else:
				apt_package.mark_install()
				cache.commit()
				r.console.log(f'Installed: {cache.get_changes()}')
		except Exception as e:
			logging.info(f'{e}')
			pass #raise e



def get_apt(packages):
	''' 
	Download and install packages for Apt.
	arg: packages:lst
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
			logging.info(f'{e}')
			pass #raise e


@timeit
def make_threaded(func, urls):
	''' Threaded func for Downloader class '''

	# Executor-pool used with content manager to ensure threads are cleaned up promptly.
	with futures.ThreadPoolExecutor() as executor:
		# Load operations and mark each future with its URL.
		future_to_url = {executor.submit(func, url): url for url in urls}
		# Obtain results as they're completed.
		for future in futures.as_completed(future_to_url):
			url = future_to_url[future]
			try:
				data = future.result()
			except Exception as e:
				logging.info(f'{e}')
			else:
				r.console.log(f'{data}')


@timeit
def main():
	''' Main func '''

	# Pause, mainly used for testing.
	r.ctrl_c()

	# Downloader init.
	dl = download.Downloader(DEST_DIR)
	
	# Github-Downloads.
	r.banner('Github Downloads')
	with r.console.status(status=f'[txt.spinner]Downloading') as status:
		make_threaded(dl.get_gitrepo, GITHUB_URLS)

	# URL-Downloads.
	r.banner('URL Downloads')
	with r.console.status(status=f'[txt.spinner]Downloading') as status:
		make_threaded(dl.get_binary, BINARY_URLS)

	# Installer init.
	installer = Installer()

	# Pip Download/Install.
	r.banner('Pip Downloads/Installs')
	with r.console.status(status=f'[txt.spinner]Processing...') as status:
		results = list(map(installer.pip_install, PIP_PACKAGES))

	# APT Download/Install.
	r.banner('APT Downloads/Installs')
	with r.console.status(status=f'[txt.spinner]Processing...') as status:
		results = list(map(installer.apt_install, APT_PACKAGES))
	


if __name__ == '__main__':
	main()
