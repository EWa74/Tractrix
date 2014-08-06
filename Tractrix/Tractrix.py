#  ***** BEGIN GPL LICENSE BLOCK *****
#  https://github.com/EWa74/KUKA_Simulator.git
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  ***** END GPL LICENSE BLOCK *****
# Version: 100R
# Next steps:    

# 


'''

${workspace_loc:KUKA_OT_Export/src/curve_export.py}

Bevel add-on
bpy.data.curves[bpy.context.active_object.data.name].splines[0].bezier_points[0].co=(0,1,1)
'''  
#--- ### Header 
bl_info = { 
    "name": "KUKA_OT_Export",
    "author": "Eric Wahl",
    "version": (1, 0, 1),
    "blender": (2, 5, 7),
    "api": 36147,
    "location": "View3D >Specials (W-key)",
    "category": "Curve",
    "description": "Import/ Export Kuka Bahnkurve",
    "warning": "",
    "wiki_url": "http://...",
    "tracker_url": "http://..."
    }

     
#--- ### Imports

import bpy
# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy_extras.io_utils import ImportHelper
import time # um Zeitstempel im Logfile zu schreiben
import bpy, os
import sys
from bpy.utils import register_module, unregister_module
from bpy.props import FloatProperty, IntProperty
from mathutils import Vector  
from mathutils import *
import mathutils
import math
import re  # zum sortieren de Objektliste
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
from symbol import except_clause
from copy import deepcopy # fuer OptimizeRotation

# Global Variables:

  


def writelog(text=''):
    FilenameLog = bpy.data.filepath
    FilenameLog = FilenameLog.replace(".blend", '.log')
    fout = open(FilenameLog, 'a')
    localtime = time.asctime( time.localtime(time.time()) )
    fout.write(localtime + " : " + str(text) + '\n')
    fout.close();

class ObjectSettings(bpy.types.PropertyGroup):
    ID = bpy.props.IntProperty()
    # type: BASEPos, PTP, HOMEPos, ADJUSTMENTPos
    type = bpy.props.StringProperty()
    
    PATHPTS = bpy.props.FloatVectorProperty(size=6)
    
    # LOADPTS[1]={FX NAN, FY NAN, FZ NAN, TX NAN, TY NAN, TZ NAN }
    # bpy.data.objects['PTPObj_001'].PATHPTS.LOADPTS[:] 
    LOADPTS = bpy.props.IntVectorProperty(size=6)
    LOADPTSmsk = bpy.props.BoolVectorProperty(size=6) # fuer NAN Eintrag
    LOADPTSmsk = (False, False, False, False, False, False)
    
    # TTIMEPTS[1]=0.2
    TIMEPTS = bpy.props.FloatProperty()
    
    # STOPPTS[1]=1
    STOPPTS = bpy.props.BoolProperty()
    STOPPTS = 'False'
    
    # ACTIONMSK[1]=0
    ACTIONMSK = bpy.props.BoolProperty()
    ACTIONMSK = 'False'
    
    # RouteName
    RouteName = bpy.props.StringProperty()
    
    # RouteNbr
    RouteNbr = bpy.props.IntProperty()  
    
bpy.utils.register_class(ObjectSettings)

bpy.types.Object.kuka = \
    bpy.props.PointerProperty(type=ObjectSettings)

class createMatrix(object):
    writelog('_____________________________________________________________________________')
    writelog('createMatrix')
    def __init__(self, rows, columns, default=0):
        self.m = []
        for i in range(rows):
            self.m.append([default for j in range(columns)])
    def __getitem__(self, index):
        return self.m[index]
    writelog('createMatrix done')
    writelog('_____________________________________________________________________________')  


   


  
class KUKA_OT_Export (bpy.types.Operator, ExportHelper):
    writelog('KUKA_OT_Export - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ') 
    writelog('- - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
    #bpy.ops.curve.KUKA_OT_Export(
                              
    # Export selected curve of the mesh
    bl_idname = "object.kuka_export"
    bl_label = "KUKA_OT_Export (TB)" #Toolbar - Label
    bl_description = "Export selected Curve1" # Kommentar im Specials Kontextmenue
    bl_options = {'REGISTER', 'UNDO'} #Set this options, if you want to update  
    #                                  parameters of this operator interactively 
    #                                  (in the Tools pane) 
    
    # ExportHelper mixin class uses this
    filename_ext = ".dat"

    filter_glob = StringProperty(
            default="*.dat",
            options={'HIDDEN'},
            )

    def execute(self, context):
        
        writelog('FUNKTIONSAUFRUF - KUKA_OT_Export')
        
        
        # Wichtig: Vor dem Export muss die Lokale-Skalierung erst mit der Global-Skalierung in uebereinstimmung gebracht werden.
        # Entspricht [STRG] + A (Apply Scale)
        # um nicht auch das Tool selber zu beeinflussen muss das parenting dafuer geloest werden. (--> def ApplyScale)
        
        # nur fuer Scaling, da Location, Rotatation (mit Hilfe des Mesh-Objektes 'Sphere_BASEPos') beim Export in *.src file geschrieben wird:
        # --> [STRG] + A (Apply Location, Rotation) wird nicht normiert sondern wieder eingelesen! (KUKA BASEPosition)
        writelog('- - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
        writelog(' FUNKTIONSAUFRUF KUKA_OT_Export KUKA_Tools')
        writelog('- - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
        
        
        
        return {'FINISHED'}
    writelog('KUKA_OT_Export done')  

class KUKA_OT_Import (bpy.types.Operator, ImportHelper): # OT fuer Operator Type
    writelog('KUKA_OT_Import- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ') 
    writelog('- - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
    ''' Import selected curve '''
    bl_idname = "object.kuka_import"
    bl_label = "KUKA_OT_Import (TB)" #Toolbar - Label
    bl_description = "Import selected Curve2" # Kommentar im Specials Kontextmenue
    bl_options = {'REGISTER', 'UNDO'} #Set this options, if you want to update  
    #                                  parameters of this operator interactively 
    #                                  (in the Tools pane) 

    # ImportHelper mixin class uses this
    filename_ext = ".dat"

    filter_glob = StringProperty(
            default="*.dat",
            options={'HIDDEN'},
            )
 
    def execute(self, context):  
        writelog('- - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
        writelog(' FUNKTIONSAUFRUF KUKA_OT_Import')
        writelog('- - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
       
        return {'FINISHED'} 
    writelog('KUKA_OT_Import done')

class KUKA_OT_RefreshButton (bpy.types.Operator):
    writelog('KUKA_OT_RefreshButton- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ') 
    writelog('- - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
    
    
    ''' Import selected curve '''
    bl_idname = "object.refreshbutton"
    bl_label = "Refresh (TB)" #Toolbar - Label
    bl_description = "Set Animation Data" # Kommentar im Specials Kontextmenue
    bl_options = {'REGISTER', 'UNDO'} #Set this options, if you want to update  
    #                                  parameters of this operator interactively 
    #                                  (in the Tools pane) 
 
    def execute(self, context):  
        writelog('- - -refreshbutton - - - - - - -')
        writelog('Testlog von KUKA_OT_RefreshButton')
        
        
        
        
        return {'FINISHED'} 
    writelog('- - -KUKA_OT_RefreshButton done- - - - - - -')     



class KUKA_OT_animateptps (bpy.types.Operator):
    writelog('KUKA_OT_animatePTPs - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ') 
    writelog('- - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
    ''' Import selected curve '''
    bl_idname = "object.animateptps"
    bl_label = "animatePTPs (TB)" #Toolbar - Label
    bl_description = "Set Animation Data for PathPoints (PTPs)" # Kommentar im Specials Kontextmenue
    bl_options = {'REGISTER', 'UNDO'} #Set this options, if you want to update  
    #                                  parameters of this operator interactively 
    #                                  (in the Tools pane) 
 
    def execute(self, context):  
        writelog('- - -animatePTPs - - - - - - -')
        writelog('Testlog von KUKA_OT_animatePTPs')
        PATHPTSObjList, countPATHPTSObj  = count_PATHPTSObj(PATHPTSObjName)
        
        # TODO: TargetObjList um Basepos erweitern ggf defroute funktion ueberarbeiten/ ueberbehmen
        filepath ='none'
        Route_ObjList = DefRoute(objEmpty_A6, filepath)
        
        #TargetObjList= PATHPTSObjList
        #AnimateOBJScaling(TargetObjList)
        AnimateOBJScaling(Route_ObjList)
        return {'FINISHED'} 
    writelog('- - -KUKA_OT_animatePTPs done- - - - - - -') 


       
class KUKA_PT_Panel(bpy.types.Panel):
    writelog('_____________________________________________________________________________')
    writelog()
    writelog('KUKA_PT_Panel....')
    writelog()
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "KUKA Panel" # heading of panel
    #bl_idname = "SCENE_PT_layout"
    bl_idname = "OBJECT_PT_layout"
    
    # bpy.ops.OBJECT_PT_layout.module....
    
    bl_space_type = 'PROPERTIES' # window type panel is displayed in
    bl_region_type = 'WINDOW' # region of window panel is displayed in
    bl_context = "object"
    #bl_context = "scene"
    
    # check poll() to avoid exception.
    '''
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='EDIT')
    '''
    
    #@classmethod
    #def poll(cls, context):
    #    return (bpy.context.active_object.type == 'CURVE') # Test, ob auch wirklich ein 'CURVE' Objekt aktiv ist.

    
    def draw(self, context):
        
        ob = context.object
        
        layout = self.layout

        scene = context.scene
        #scene = context.object
        # Create a simple row.
        layout.label(text=" EWa: Simple Row:")

        row = layout.row()
        row.prop(scene, "frame_start")
        row.prop(scene, "frame_end")

        # Create an row where the buttons are aligned to each other.
        layout.label(text=" Aligned Row:")

        row = layout.row(align=True)
        row.prop(scene, "frame_start")
        row.prop(scene, "frame_end")

        # Create two columns, by using a split layout.
        layout.label(text="Tool location / orientation:")
        row = layout.row()

        row.column().prop(ob, "delta_location")
        if ob.rotation_mode == 'QUATERNION':
            row.column().prop(ob, "delta_rotation_quaternion", text="Rotation")
        elif ob.rotation_mode == 'AXIS_ANGLE':
            #row.column().label(text="Tool_Rotation")
            #row.column().prop(pchan, "delta_rotation_angle", text="Angle")
            #row.column().prop(pchan, "delta_rotation_axis", text="Axis")
            #row.column().prop(ob, "delta_rotation_axis_angle", text="Rotation")
            row.column().label(text="Not for Axis-Angle")
        else:
            row.column().prop(ob, "delta_rotation_euler", text="Delta Rotation")
        
        
        layout.label(text="Base location / orientation:")
        row = layout.row()

        row.column().prop(ob, "delta_location")
        if ob.rotation_mode == 'QUATERNION':
            row.column().prop(ob, "delta_rotation_quaternion", text="Rotation")
        elif ob.rotation_mode == 'AXIS_ANGLE':
            #row.column().label(text="Tool_Rotation")
            #row.column().prop(pchan, "delta_rotation_angle", text="Angle")
            #row.column().prop(pchan, "delta_rotation_axis", text="Axis")
            #row.column().prop(ob, "delta_rotation_axis_angle", text="Rotation")
            row.column().label(text="Not for Axis-Angle")
        else:
            row.column().prop(ob, "delta_rotation_euler", text="Delta Rotation")
            
        #row.column().prop(ob, "delta_scale")
        
        # Import/ Export Button:
        layout.label(text="Curvepath Import/ Export:")
        row = layout.row(align=True)        
        sub = row.row()
        sub.scale_x = 1.0
        sub.operator("object.kuka_import")  
        row.operator("object.kuka_export") 
        
        # Set KeyFrames Button:
        layout.label(text="Refresh Button:")
        row = layout.row(align=True)
        
        row.operator("object.refreshbutton")  
        
        # Animate PTPs Button:
        layout.label(text="Animate PTPs:")
        row = layout.row(align=True)
        
        row.operator("object.animateptps")  
        
        # Set BGE Action Button:
        layout.label(text="create BGE (Euler) Action:")
        row = layout.row(align=True)
        
        row.operator("object.bge_actionbutton")  
           
    writelog('KUKA_PT_Panel done')
    writelog('_____________________________________________________________________________')


#class CURVE_OT_RefreshButtonButton(bpy.types.Operator):
 



    



# ________________________________________________________________________________________________________________________


#--- ### Register
#ToDo: KUKA Operator nicht regestriert....
def register():
    bpy.utils.register_class(KUKA_PT_Panel)  
    register_module(__name__)
    
def unregister():
    bpy.utils.unregister_class(KUKA_PT_Panel) 
    unregister_module(__name__)

#--- ### Main code    
if __name__ == '__main__':
    register()

