__author__ = 'jumo'

from os.path import splitext
import os
import re
from tempfile import mkstemp
import shutil


MD_EXT = 'md'
MD_RE = re.compile(r'[^\.]+\.{}$'.format(MD_EXT))
REFERENCE_EXT_RE = re.compile(r'(?P<pre>.*?<a href=\")(?P<ref>[^\.]+\.md)(?P<post>\">.*)', re.IGNORECASE)


def convert_ref_in_file(html_filepath):
    with open(html_filepath, 'r', encoding='UTF-8') as in_file:
        # Create temp file
        tmp_file, tmp_filepath = mkstemp()
        try:
            for line in in_file:
                match = REFERENCE_EXT_RE.search(line)
                if match:
                    m = match.groupdict()
                    new_ref = splitext(m['ref'])[0].replace('\\', '/') + '.html'
                    line = m['pre'] + new_ref + m['post']
                os.write(tmp_file, bytes(line, 'UTF-8'))
            shutil.copy(tmp_filepath, html_filepath)
        finally:
            # always clean our mess
            os.close(tmp_file)
            os.remove(tmp_filepath)