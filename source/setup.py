#!/usr/bin/python
# -*- coding: utf-8 -*-

# Christophe Foyer 2017

from distutils.core import setup
import py2exe

import numpy
import os
import sys

# add any numpy directory containing a dll file to sys.path
def numpy_dll_paths_fix():
    paths = set()
    np_path = numpy.__path__[0]
    for dirpath, _, filenames in os.walk(np_path):
        for item in filenames:
            if item.endswith('.dll'):
                paths.add(dirpath)

    sys.path.append(*list(paths))

numpy_dll_paths_fix()

import matplotlib

setup(
    options = {'build': {'build_base': 'build'},
            "py2exe":{
            'includes': 'matplotlib.backends.backend_tkagg',
            
            #'compressed':1,  
            #'bundle_files': 2, 
            'dist_dir': "../dist",
            
            'packages': ['FileDialog'],
            'excludes': [],
            "dll_excludes": ["MSVCP90.dll",'libgdk-win32-2.0-0.dll','libgobject-2.0-0.dll']
            
        }
    },
    data_files=matplotlib.get_py2exe_datafiles(),
    windows = [{'script': 'Control Panel.py'}]
    ## If you want to display the console
    #console = [{'script': 'Control Panel.py'}]
)
