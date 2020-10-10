
import bpy

from bpy_extras.io_utils import ExportHelper
from bpy_extras.io_utils import ImportHelper
import time # um Zeitstempel im Logfile zu schreiben
import bpy, os
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
    writelog('- - parenttrailer_OT_Main done- - - - - - -') 


def register():
    for cls in classes:
        bpy.utils.register_class(operators)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(operators)

if __name__ == "__main__":
    register()

operators = [clearanimation_OT_Main]   
