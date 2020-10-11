# -*- coding: utf-8 -*-    
#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# coding Angabe in Zeilen 1 und 2 fuer Eclipse Luna/ Pydev 3.9 notwendig
# cp1252

import bpy
import os, sys

from bpy_extras.io_utils import ExportHelper
from bpy_extras.io_utils import ImportHelper

#from bpy.utils import register_module, unregister_module

import time # um Zeitstempel im Logfile zu schreiben


myDir = os.path.dirname(os.path.abspath(__file__))
parentDir = os.path.split(myDir)[0]
if(sys.path.__contains__(parentDir)):
    print('parent already in path')
    pass
else:
    print('parent directory added')
    sys.path.append(parentDir)
    
#import src.tractrix_internal


# Exported function
def as_int(a):
    return int(a)

# Test function for module  
def _test():
    assert as_int('1') == 1

    
def writelog(text=''):
    FilenameLog = bpy.data.filepath
    FilenameLog = FilenameLog.replace(".blend", '.log')
    fout = open(FilenameLog, 'a')
    localtime = time.asctime( time.localtime(time.time()) )
    fout.write(localtime + " : " + str(text) + '\n')
    fout.close();
    

'''   
def register():
    bpy.utils.register_module(__name__)  
    
def unregister():
    bpy.utils.unregister_module(__name__)
    
if __name__ == "__main__":
    register()
'''
    
if __name__ == '__main__':
    _test()