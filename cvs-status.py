#!/usr/bin/python

"""
		Extract and print a list of files that are out-of-sync with CVS server.
		Uses 'cvs status' command. Expects user to be logged in to
		CVS, and current working dir to be the root of a CVS working dir.

		@author Viktor Lieskovsky
		@url http://javaflight.blogspot.com
"""

import re
from popen2 import Popen3

file_status = re.compile("""
	^               # beginning of string
	File:\s?        # static text
	([^\s]*)        # filename
	\s*Status:\s?   # static text
	(.*)            # status
	$               # eol
""", re.VERBOSE)

def __filter_spam(content):
	return [line for line in content if line[0] != '?' and "cvs status:" not in line]

def file_chunks(content):
	while len(content) > 0:
		chunk = content[0:9]
		del content[0:9]
		yield(chunk)

def filter_unchanged(content):
	chunks = file_chunks(__filter_spam(content.readlines()))
	return [file_status.search(chunk[1]).groups() for chunk in chunks if not "Up-to-date" in chunk[1]]

def report(changed):
	file_message = "File: %s%sStatus: %s"
	column_filling = lambda filename: (50 - len(filename)) * " "
	print "\n".join([file_message % (f[0], column_filling(f[0]), f[1]) for f in changed])
	print "\n", ("There are %s out-of-sync files in your working tree." % len(changed)), "\n"

def get_cvs_output():
	p = Popen3('cvs status')
	if p.wait():
		raise EnvironmentError
	return p.fromchild

if __name__ == '__main__':
	try:
		test = False
		fh = test and open('cvs-status.log') or get_cvs_output()
		report(filter_unchanged(fh))
	except (EnvironmentError, IOError), message:
		print message
