#!/usr/bin/env python3

from concurrent import futures
from functools import wraps
# To rename r to Console.
from utils import richard as r
from utils import cparse as cp
from utils import install
from utils import download
import logging
# To deprecate.
import time


# Confgfile values.
GITHUB_URLS = [k for k in cp.config['github_urls']]
BINARY_URLS = [k for k in cp.config['binary_urls']]
PIP_PACKAGES = [k for k in cp.config['pip_packages']]
APT_PACKAGES = [k for k in cp.config['apt_packages']]
DEST_DIR = ''.join([k for k in cp.config['tools_dir']])


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
				logging.info(f'{e}')
			else:
				logging.info(f'{data}')


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
	installer = install.Installer()
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
