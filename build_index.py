#!/usr/bin/env python3

__author__ = 'jumo'

import argparse
import logging
import os
from os.path import join, splitext, abspath, isfile, isdir, exists
import re
# from tempfile import mkstemp
# import shutil

MD_EXT = 'md'
MD_RE = re.compile(r'[^\.]+\.{}$'.format(MD_EXT))


def create_index(input_dirpath):
    index = {}
    in_dir_list = [e for e in os.listdir(input_dirpath)]
    md_file_list = [f for f in in_dir_list if isfile(join(input_dirpath, f)) and MD_RE.match(f)]
    subdir_list = [d for d in in_dir_list if isdir(join(input_dirpath, d))]
    index['name'] = os.path.basename(input_dirpath)
    index['path'] = input_dirpath
    index['files'] = md_file_list
    subdirs_index = {}
    for subdir in subdir_list:
        subdirs_index[subdir] = create_index(join(input_dirpath, subdir))
    index['subsections'] = subdirs_index
    return index


def format_index_to_md(toc, root=[], level=1, dot='*', indent_char='  '):
    md_txt = ''
    indent = indent_char * level
    root_name = '/'.join(root)
    if root_name:
        md_txt += indent_char * (level - 1) + '{} {}\n'.format(dot, root_name)
    for md_filename in toc['files']:
        md_path = root + [md_filename]
        md_txt += indent + '{} [{}]({})\n'.format(dot, splitext(md_filename)[0], join(*md_path))
    subsections = toc['subsections']
    for subsection_name in subsections:
        md_txt += format_index_to_md(
            subsections[subsection_name],
            root + [subsection_name],
            level+1,
            dot,
            indent_char)
    return md_txt


# def replace_index_in_file(html_filepath, toc_txt):
#     REFERENCE_INDEX_RE = re.compile(r'\[INDEX\]', re.IGNORECASE)
#     with open(html_filepath, 'r', encoding='UTF-8') as in_file:
#         # Create temp file
#         tmp_file, tmp_filepath = mkstemp()
#         for line in in_file:
#             line = REFERENCE_INDEX_RE.sub(toc_txt, line)
#             os.write(tmp_file, bytes(line, 'UTF-8'))
#         shutil.copy(tmp_filepath, html_filepath)
#         os.close(tmp_file)
#         # os.remove(tmp_file)


def make_index_file(input_dirpath, output_filename='index.md'):
    output_filepath = join(input_dirpath, output_filename)
    # clear output file if already exists (avoid listing itself)
    if exists(output_filepath):
        os.remove(output_filepath)
    # parse files to create index
    toc = create_index(input_dirpath)
    # format the index
    content = format_index_to_md(toc)
    logging.info('writing index file {}'.format(output_filepath))
    with open(output_filepath, 'w') as output_file:
        output_file.write(content)


def main():
    try:
        parser = argparse.ArgumentParser(description='Description of the program.')
        parser.add_argument('-v', '--verbose', action='store_true', help='verbose message')
        parser.add_argument('-i', '--input_dirpath', help='input')
        parser.add_argument('-o', '--output_filename', default='index.md', help='index filename')

        args = parser.parse_args()

        if args.verbose:
            if __debug__:
                logging.getLogger().setLevel(logging.DEBUG)
            else:
                logging.getLogger().setLevel(logging.INFO)

        # get input directory from user (or its default value)
        input_dirpath = abspath(args.input_dirpath)
        # get output directory from user (or its default value)
        output_filename = args.output_filename
        make_index_file(input_dirpath, output_filename)

    except Exception as e:
        logging.critical(e)
        if __debug__:
            raise


if __name__ == '__main__':
    main()