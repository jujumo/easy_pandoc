#!/usr/bin/env python3

__author__ = 'jumo'

import argparse
import logging
import os
from os.path import splitext, abspath, dirname, exists, realpath
import re
from tempfile import mkstemp
import shutil
try:
    import pypandoc
except ImportError as e:
    logging.critical('pypandoc not installed. install Pandoc, and pypandoc.')
    raise

MD_EXT = 'md'
HTML_EXT = 'html'
MD_RE = re.compile(r'[^\.]+\.{}$'.format(MD_EXT))


def replace_ref_in_file(html_filepath):
    REFERENCE_EXT_RE = re.compile(r'(?P<pre>.*?<a href=\")(?P<ref>[^\.]+\.md)(?P<post>\">.*)', re.IGNORECASE)
    with open(html_filepath, 'r', encoding='UTF-8') as in_file:
        # Create temp file
        tmp_file, tmp_filepath = mkstemp()
        for line in in_file:
            match = REFERENCE_EXT_RE.search(line)
            if match:
                m = match.groupdict()
                new_ref = splitext(m['ref'])[0].replace('\\', '/') + '.html'
                line = m['pre'] + new_ref + m['post']
            os.write(tmp_file, bytes(line, 'UTF-8'))
        shutil.copy(tmp_filepath, html_filepath)
        os.close(tmp_file)


def convert_md2html(input_filepath, output_filepath, css_filepath='',
                    skip_ref=False,
                    no_toc=False,
                    options=[]):
    logging.debug('convert {} to {}'.format(input_filepath, output_filepath))

    input_filepath = realpath(input_filepath)
    output_filepath = realpath(output_filepath)
    css_filepath = realpath(css_filepath)
    prev_path = os.getcwd()
    try:
        # change current dir to MD file dir, to enable all relative path to this one
        os.chdir(dirname(input_filepath))

        # prepare constant arguments for pandoc
        pandoc_extra_args = ['--smart', '--standalone', '--self-contained']
        if not no_toc:
            pandoc_extra_args += ['--toc']

        if css_filepath:
            pandoc_extra_args += ['--css='+css_filepath]

        pandoc_extra_args += options

        # make sur output path exists
        dirpath = dirname(output_filepath)
        if not exists(dirpath):
            logging.info('creating directory {}'.format(dirpath))
            os.makedirs(dirpath)

        # process the conversion
        pypandoc.convert(
            input_filepath,
            format='markdown_github',
            to='html5',
            extra_args=pandoc_extra_args,
            outputfile=output_filepath)

        if not skip_ref:
            # replace href to md file with ref to html
            replace_ref_in_file(output_filepath)

    finally:
        os.chdir(prev_path)


def main():
    try:
        parser = argparse.ArgumentParser(description='Description of the program.')
        parser.add_argument('-v', '--verbose', action='store_true', help='verbose message')
        parser.add_argument('-i', '--input', required=True, help='input')
        parser.add_argument('-o', '--output', help='output')
        parser.add_argument('--css', help='css filepath')
        parser.add_argument('--no_toc', action='store_true', help='do not insert table of content in header section')
        parser.add_argument('--skip_ref', action='store_true', help='do not convert link.')

        args = parser.parse_args()

        if args.verbose:
            if __debug__:
                logging.getLogger().setLevel(logging.DEBUG)
            else:
                logging.getLogger().setLevel(logging.INFO)

        # get input directory from user (or its default value)
        input_filepath = args.input
        # get output directory from user (or its default value)
        if args.output:
            output_filepath = args.output
        else:
            output_filepath = splitext(input_filepath)[0] + HTML_EXT

        if args.css:
            css_filepath = args.css
        else:
            css_filepath = None

        convert_md2html(
            input_filepath, output_filepath, css_filepath,
            skip_ref=args.skip_ref,
            no_toc=args.no_toc)

    except Exception as e:
        logging.critical(e)
        if __debug__:
            raise


if __name__ == '__main__':
    main()