#!/usr/bin/env python3

import apt
import logging
import subprocess


class PackageExistsError(Exception):
	''' Error for apt module, package exists.'''
	pass


class Installer():
	''' Installer for Pip and Apt packages. '''

	
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
			logging.warning(f'Package already installed: {package}')
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
		Install package for apt. arg(s): packages:lst 
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
				logging.info(f'Installed: {cache.get_changes()}')
		except Exception as e:
			logging.warning(f'{e}')
			pass #raise e