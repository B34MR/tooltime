#!/usr/bin/env python3

from concurrent import futures
from configparser import ConfigParser
from functools import wraps
from utils import arguments
from utils import download
from utils import install
from utils import richard as r
import os
import logging
import time


def timeit(method):
	''' Wrapper to calculate execution time '''
	@wraps(method)
	def wrapper(*args, **kargs):
		starttime = time.time()
		result = method(*args, **kargs)
		endtime = time.time()
		print(f'\n')
		r.console.print(f'Completed in: {(endtime-starttime)*1000} ms')

		return result
	return wrapper


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
				logging.warning(f'{e}')
			else:
				logging.info(f'Downloaded: {data}')


def append_str(mystr, filepath):
	''' 
	Append string to file.
	arg(s) filepath:str, mystr:str

	'''
	with open(filepath, 'a+') as f1:
		f1.write(f'\n{mystr}')
	
	return mystr


def append_lst(mylst, filepath):
	''' 
	Append a list of strs to a file.
	arg(s) mylst:list, filename:str
	'''

	# Custom comment.
	comment = f'### Modified by: {os.path.realpath(__file__)} ###'
	# Append comment to file.
	append_str(comment, filepath)
	# Append item:str to file.
	result = [append_str(item, filepath) for item in mylst]

	return result


@timeit
def main():
	''' Main func '''

	# Args
	args = arguments.parse_args()

	# Args - Configfile path
	filepath = args.configfile

	# Set delimiter ':' for 'aliases.ini' configfile.
	filename = os.path.basename(filepath)
	if filename == 'aliases.ini':
		config = ConfigParser(allow_no_value=True, delimiters=':')
		config.optionxform = str
		config.read(filepath)
		# Config file values.
		ALIASES = [k for k in config['aliases']]
		EXPORTS = [k for k in config['bashrc']]
		# Check if aliases are in configfile.
		r.banner('Aliases')
		if ALIASES:
			filepath = os.path.join(os.path.expanduser('~'), '.bash_aliases')
			# Append list to file.
			results = append_lst(ALIASES, filepath)
			# Print results.
			[logging.info(f'Append {filepath}: {result}') for result in results]
		# Check if exposts are in configfile.
		r.banner('Exports')
		if EXPORTS:
			filepath = os.path.join(os.path.expanduser('~'), f'.bashrc')
			# Append list to file.
			results = append_lst(EXPORTS, filepath)
			# Print results.
			[logging.info(f'Appended {filepath}: {result}') for result in results]

	# Set delimiter '=' for all other configfiles.
	else:
		config = ConfigParser(allow_no_value=True, delimiters='=')
		config.optionxform = str
		config.read(filepath)
		# Config file values.
		DEST_DIR = ''.join([k for k in config['tools_dir']][0])
		GITHUB_URLS = [k for k in config['github_urls']]
		BINARY_URLS = [k for k in config['binary_urls']]
		PIP_PACKAGES = [k for k in config['pip_packages']]
		APT_PACKAGES = [k for k in config['apt_packages']]

		# Pause, mainly used for testing.
		r.ctrl_c()

		# Downloader init.
		dl = download.Downloader(DEST_DIR)
		# Github-Downloads.
		r.banner('Github Downloads')
		with r.console.status(status=f'[status.text]Downloading') as status:
			make_threaded(dl.get_gitrepo, GITHUB_URLS)
		# URL-Downloads.
		r.banner('URL Downloads')
		with r.console.status(status=f'[status.text]Downloading') as status:
			make_threaded(dl.get_binary, BINARY_URLS)

		# Installer init.
		installer = install.Installer()
		# Pip Download/Install.
		r.banner('Pip Downloads/Installs')
		with r.console.status(status=f'[status.text]Processing...') as status:
			results = list(map(installer.pip_install, PIP_PACKAGES))
		# APT Download/Install.
		r.banner('APT Downloads/Installs')
		with r.console.status(status=f'[status.text]Processing...') as status:
			results = list(map(installer.apt_install, APT_PACKAGES))


if __name__ == '__main__':
	main()
