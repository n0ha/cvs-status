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

def filter_content(fh):
	status_lines = []
	for line in [line for line in fh.readlines() if line[0] != '?' and "cvs status:" not in line]:
		status_lines.append(line)
	return status_lines
		
def file_chunks(status_lines):
	if "[status aborted]" in status_lines[0]:
		raise EnvironmentError(status_lines[0])
	while len(status_lines) > 0:
		result = status_lines[1]
		del status_lines[0:9]
		yield(result)

def filter_changed(status_lines):		
	changed = []
	chunk_regex = re.compile("""
		^				# beginning of string
		File:\s?		# static text
		([^\s]*)		# filename
		\s*Status:\s?	# static text
		(.*)			# status
		$				# eol
	""", re.VERBOSE) 
	for chunk in file_chunks(status_lines):
		if chunk != None and not "Up-to-date" in chunk:
			changed.append(chunk_regex.search(chunk).groups())
	return changed

def print_changed(changed):
	for f in changed:
		column_filling = (50 - len(f[0])) * " "
		print "File: %s%sStatus: %s" % (f[0], column_filling, f[1])
	print "\n", ("There are %s out-of-sync files in your working tree." % len(changed)), "\n"

if __name__ == '__main__':
	exec_cmd = popen2.popen4('cvs status')
	content = filter_content(exec_cmd[0])
	print_changed(filter_changed(content))
