'''
FILE:	wrap_Guppy_CPU.py
AUTHOR:	J.R. Hendrix
URL: 	http://stronglab.org
DESC:	This script initiates a hack method for 
		Running Guppy Basecaller on CPU-based cluster
		Input: Directory of FAST5 files
'''


# IMPORT FROM PYTHON STANDARD LIBRARY
import argparse
import datetime
import logging
import numpy as np
import operator
import os
import subprocess
import sys
import time
from tempfile import TemporaryFile
from subprocess import call

# DEFINE DIR CLASS
class Dir:
	""" Base class for system directories """

	def __init__(self, path):
		self._path = None
		self.path = path

	@property
	def path(self):
		return self._path

	@path.setter
	def path(self, value):
		if not os.path.isabs(value):
			value = os.path.join(os.getcwd(), value)
		if os.path.isdir(value):
			self._path = value
		else:
			raise NotADirectoryError(value)

	@property
	def dirname(self):
		return self.path.strip("/").split("/")[-1]


	def join(self, *args):
		return os.path.join(self.path, *args)


	def make_subdir(self, *args):
		""" Makes recursive subdirectories from 'os.path.join' like arguments """
		subdir = self.join(*args)
		return self.make(subdir)

	@classmethod
	def make(cls, path):
		try:
			os.makedirs(path)
			return cls(path)
		except FileExistsError:
 			return cls(path)


	def __repr__(self):
		return self.path


# INITIATE LOG FILE
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')


def set_up(args):
	'''Set up output dierectory and log file'''	
	IN_DIR = Dir(args.i)
	TOP_DIR = Dir(args.p)

	now = datetime.datetime.now()
	outDate = now.strftime("%Y%m%d")
	outDir = (args.o, outDate)
	outDir = '_'.join(outDir)

	# FIND NAME FOR BASE DIRECTORY
	notValid = True
	count = 0
	newDir = outDir
	while notValid:
		path = (str(TOP_DIR), newDir)
		path = '/'.join(path)
		if os.path.isdir(path):
			count = count + 1
			newDir = (outDir, str(count))
			newDir = '_'.join(newDir)
			
		else:
			notValid = False

	BASE_DIR = TOP_DIR.make_subdir(newDir)

	# FINISH LOG CONFIGURATION
	LOG_FILE = BASE_DIR.join("guppy_wrapper.log")
	file_handler = logging.FileHandler(LOG_FILE)
	file_handler.setFormatter(formatter)

	LOG.addHandler(file_handler)

	intro = 'This is a wrapper function for Guppy.'
	LOG.info(intro)
	LOG.info('Output directory: {}'.format(str(BASE_DIR)))

	return IN_DIR, BASE_DIR


def main():
	'''Identify fast5 files and call guppy basecaller '''
	cwd = os.getcwd()

	# PARSER : ROOT
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--flowcell', default='FLO-MIN106')
	parser.add_argument('-g', '--guppy_path', help='Path to Guppy basecaller', required=True)
	parser.add_argument('-i', help='Directory of input fast5', type=str, required=True)
	parser.add_argument('-k', '--kit', default='SQK-LSK109')
	parser.add_argument('-o', default="basecall_guppy", help='Prefix of output directory', type=str)
	parser.add_argument('-p', default=cwd, help='Path to output', type=str)

	args = parser.parse_args()
	IN_DIR, BASE_DIR = set_up(args)

	out_path = (str(BASE_DIR.path))
	tmp_dir = BASE_DIR.make_subdir('file_dump')

	# GET LIST OF FAST5 FILES
	try:
		task = "GET LIST OF FAST5 FILES"
		LOG.info(task)
		fp = TemporaryFile('w+t')	# create temp file
		LOG.info('Made temperary file to list FAST5 files')
		command = ['ls', IN_DIR.path]
		process = subprocess.run(command, stdout = fp)
		if process.returncode == 0:
			LOG.info(f"{task} : ...DONE")
		elif process.returncode == 1:
			LOG.info(f"{task} : ...FAILED")
			exit()
	except Exception as e:
		LOG.warning(f"{task} ...FAILED : {e}")
		exit(e)
	

	f = BASE_DIR.join("jobs.tsv")
	fo = open(f, 'w')

	fp.seek(0)
	count = 0
	for line in fp:
		# CREATE DIR FOR GUPPY TO WORK IN
		name = line.replace('\n', '')
		target = (IN_DIR.path, name)
		target = '/'.join(target)


		# CREATE LINK TO FAST5 FILE
		outName = ('fastq_', str(count))
		outName = ''.join(outName)
		out_dir = tmp_dir.make_subdir(outName)
		linkName = (out_dir.path, 'link.fast5')
		linkName = '/'.join(linkName)
		command = ["ln", "-s", target, linkName]
		process = subprocess.run(command)

		# CALL GUPPY
		guppy_input = out_dir.path
		program = args.guppy_path
		myCommand = ('bsub "', program, "-i", guppy_input, "-s", out_dir.path, "--flowcell", args.flowcell, "--kit", args.kit, "--cpu_threads_per_caller", str(8), "--num_callers", str(8), '"')
		command = ' '.join(myCommand)
		process = call(command, shell=True, stdout = fo)
		count = count + 1

	fp.close()	# automatically removes temp file
	fo.close()


#----------------------------------------------------------------------------------------
# start function
#		
#----------------------------------------------------------------------------------------
if __name__ == "__main__":
	start_time = time.time()
	main()
	LOG.info('Done.')
	LOG.info('\n\tExecution time: {} seconds'.format(time.time() - start_time))


