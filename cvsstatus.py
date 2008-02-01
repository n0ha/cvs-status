"""Module to extract and print a list of out-of-sync files in CVS repo.

Usage:
from cvsstatus import cvs_status
cvs_status()

Uses 'cvs status' command. Expects user to be logged in to
CVS, and current working dir to be the root of a CVS working dir.

@author Viktor Lieskovsky
@url http://javaflight.blogspot.com

"""

import re
from popen2 import Popen3

# regular expression to extract filename and its status
# from CVS output
_FILE_STATUS = re.compile("""
        ^               # beginning of string
        File:\s?        # static text
        ([^\s]*)        # filename
        \s*Status:\s?   # static text
        (.*)            # status
        $               # eol
""", re.VERBOSE)

# Enables test mode
_TEST = True

def cvs_status():
    """Extract and print a list of out-of-sync files in CVS repo.

    Can use cvs-status.log file in the script's directory as an input
    for testing purposes. To switch set _TEST to True.

    """
    try:
        fh = _TEST and open('cvs-status.log') or _get_cvs_output()
        _report(_filter_unchanged(fh))
    except (EnvironmentError, IOError), message:
        print message

def _filter_spam(content):
    """Filter out non-relevant lines from CVS output."""
    return [line for line in content 
            if not line.startswith('?') and "cvs status:" not in line]

def _file_chunks(content):
    """Split content into chunks, and return the informational line.

    CVS spits out information on a single file in 8 lines.
    To process this information, we split the output to file-related
    chunks.

    """
    while len(content) > 0:
        chunk = content[0:9]
        del content[0:9]
        yield(chunk[1])

def _filter_unchanged(content):
    """Filter out Up-to-date files from CVS output.

    From relevant non-up-to-date files, the filename and
    status are parsed and fed into a list of tuples.

    [(filename1, status1), (filename2, status2), ..]

    """
    chunks = _file_chunks(_filter_spam(content.readlines()))
    return [_FILE_STATUS.search(chunk).groups() for chunk in chunks 
            if not "Up-to-date" in chunk]

def _report(changed):
    """Print out-of-sync files in two pretty columns.

    Extracted filenames and statuses are printed in two columns,
    along with a total count at the end.
    
    Expects list of tuples.

    """
    file_msg = "File: %s%sStatus: %s"
    info_msg = "There are %s out-of-sync files in your working tree."
    column_filling = lambda text: (50 - len(text)) * " "
    
    status_list = [file_msg % (filename, column_filling(filename), status) 
                   for filename, status in changed]
    print "\n".join(status_list)
    print "\n", (info_msg % len(changed)), "\n"

def _get_cvs_output():
    """Runs 'CVS status' command and returns its output.

    If the command has a non-zero return code, an EnvironmentError
    exception is raised.

    """
    p = Popen3('cvs status')
    if p.wait():
        raise EnvironmentError
    return p.fromchild

