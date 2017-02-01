import os
import re
import argparse
import logging
from tempfile import mkstemp
import shutil
from bs4 import BeautifulSoup

__author__ = 'jumo'

MD_EXT = 'md'
HTML_EXT = 'html'
MD_RE = re.compile(r'([^\.]+\.)({})$'.format(MD_EXT))


def fix_ref_in_html(input_filepath, output_filepath=''):
    with open(input_filepath, 'r', encoding='UTF-8') as in_file:
        # Create temp file
        tmp_file_descriptor, tmp_filepath = mkstemp()
        try:
            # load the html tree
            content_tree = BeautifulSoup(in_file, "html.parser")
            for aref in content_tree.find_all('a'):
                if MD_RE.match(aref['href']):
                    # here whe have a reference to md file
                    # replace the extension by HTML
                    logging.debug('fixing ref to {}'.format(aref['href']))
                    aref['href'] = MD_RE.sub(r'\1{}'.format(HTML_EXT), aref['href'])
            # rewrite the html content
            with open(tmp_filepath, 'wb') as tmp_file:
                content_str = content_tree.prettify('latin-1')
                tmp_file.write(content_str)
            shutil.copy(tmp_filepath, input_filepath)
        finally:
            # always clean our mess
            os.close(tmp_file_descriptor)
            os.remove(tmp_filepath)


def main():
    try:
        parser = argparse.ArgumentParser(description='replace all HREF links toMD files by link to HTML files.')
        parser.add_argument('-v', '--verbose', action='store_true', help='verbose message')
        parser.add_argument('-i', '--input', required=True, help='input file path')
        parser.add_argument('-o', '--output', help='output file path (same as input if not defined)')
        args = parser.parse_args()

        if args.verbose:
            if __debug__:
                logging.getLogger().setLevel(logging.DEBUG)
            else:
                logging.getLogger().setLevel(logging.INFO)

        # get input directory from user (or its default value)
        input_filepath = args.input
        # get output directory from user (or its default value)
        output_filepath = args.output

        fix_ref_in_html(input_filepath, output_filepath)

    except Exception as e:
        logging.critical(e)
        if __debug__:
            raise


if __name__ == '__main__':
    main()