#!/usr/bin/env python

from distutils.core import setup

install_dir="/usr/bin"

import os,sys

setup(name='ProTK',
      version='0.3.0',
      description='Linguistic analysis toolkit',
      author='Jacob Okamoto',
      author_email='okam0013@umn.edu',
      url='https://github.com/oko/protk',
      packages=['protk2','protk2.db'],
     )
