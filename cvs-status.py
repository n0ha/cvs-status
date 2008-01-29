#!/usr/bin/python

""" 
		Extract and print a list of files that are out-of-sync with CVS server.
		Uses 'cvs status' command. Assumes user is logged in to
		CVS, and current working dir is set to the root of a CVS
		working dir.
		
		@author Viktor Lieskovsky
"""

import re
import popen2

chunk_regex = re.compile("""
	^               # beginning of string
	File:\s?        # static text
	([^\s]*)        # filename
	\s*Status:\s?   # static text
	(.*)            # status
	$               # eol
""", re.VERBOSE) 

def filter_content(fh):
	return [line for line in fh.readlines() if line[0] != '?' and "cvs status:" not in line]
		
def file_chunks(status_lines):
	if "[status aborted]" in status_lines[0]:
		raise EnvironmentError(status_lines[0])
	while len(status_lines) > 0:
		result = status_lines[1]
		del status_lines[0:9]
		yield(result)

def filter_changed(status_lines):		
	return [chunk_regex.search(chunk).groups() for chunk in file_chunks(status_lines) if not "Up-to-date" in chunk]

def print_changed(changed):
	text = "File: %s%sStatus: %s"
	column_filling = lambda filename: (50 - len(filename)) * " "
	print "\n".join([text % (f[0], column_filling(f[0]), f[1]) for f in changed])
	print "\n", ("There are %s out-of-sync files in your working tree." % len(changed)), "\n"

if __name__ == '__main__':
	exec_cmd = popen2.popen4('cvs status')
	content = filter_content(exec_cmd[0])
	print_changed(filter_changed(content))
