#!/usr/bin/env python3
import os
import subprocess

def has_zip(contents):
    return any(map(
        lambda x: x.endswith('.zip'),
        contents
    ))

def extract_name(somefile):
    return '.'.join(somefile.split('.')[:-1])

def extract_in_place(zipfile, parent):
    dirname = os.path.join(parent, extract_name(zipfile))
    zipname = os.path.join(parent, zipfile)

    if not os.path.exists(dirname):
        os.mkdir(dirname)

    # now extract the zip
    subprocess.run('unzip {} -d {}'.format(zipname, dirname).split(' '))

if __name__ == '__main__':
    for parent, nose, contents in os.walk('data'):
        if has_zip(contents):
            for zipfile in contents:
                extract_in_place(zipfile, parent)
