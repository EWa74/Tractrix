# -*- coding: utf-8 -*-    
#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# coding Angabe in Zeilen 1 und 2 fuer Eclipse Luna/ Pydev 3.9 notwendig
# cp1252

import bpy

from bpy_extras.io_utils import ExportHelper
from bpy_extras.io_utils import ImportHelper
import time # um Zeitstempel im Logfile zu schreiben
import os
import sys

from bpy.types import (
        Operator,
        #Panel,
        #PropertyGroup,
        )   
   

class clearanimation_OT_Main (Operator): 
    bl_idname = "tractrix.clearanimation"
    bl_label = "clear animations" 
    bl_description = "clear animations of traktor and trailer" 
    bl_options = {'REGISTER', 'UNDO'} 
    
    def execute(self, context):

        objTraktor = bpy.data.objects[bpy.context.scene.tractrix.traktor] 
        objTrailer = bpy.data.objects[bpy.context.scene.tractrix.trailer] 
        
        # clear keyfframe from Trakor and Trailer
        bpy.ops.object.select_all(action='DESELECT')
        objTraktor.select_set(True)
        objTrailer.select_set(True)
        bpy.ops.anim.keyframe_clear_v3d()
        bpy.ops.object.select_all(action='DESELECT')
        
        bpy.context.scene.tractrix.way_traktor = 0
        bpy.context.scene.tractrix.way_trailer = 0
          
        return {'FINISHED'} 
    #writelog('- - parenttrailer_OT_Main done- - - - - - -') 


def register():
    for cls in operators:
        bpy.utils.register_class(cls)

def unregister():
    for cls in operators:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()

operators = [clearanimation_OT_Main]   
