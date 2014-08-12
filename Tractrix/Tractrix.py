# location in Abh.keit vom frame

#  ***** BEGIN GPL LICENSE BLOCK *****ewa 
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
    "name": "Tractrix_OT_Main",
    "author": "Eric Wahl",
    "version": (1, 0, 1),
    "blender": (2, 5, 7),
    "api": 36147,
    "location": "View3D >Objects > Tractrix",
    "category": "Curve",
    "description": "Calculate Tractrix for Trailer Object from Tractor Objekt.",
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


   


  
class Tractrix_OT_Main (bpy.types.Operator): # OT fuer Operator Type
   
    ''' Import selected curve '''
    bl_idname = "object.tractrix"
    bl_label = "Tractrix_OT_Main (TB)" #Toolbar - Label
    bl_description = "Calculate Tractrix for Trailer Object from Tractor Objekt." # Kommentar im Specials Kontextmenue
    bl_options = {'REGISTER', 'UNDO'} #Set this options, if you want to update  
    #                                  parameters of this operator interactively 
    #                                  (in the Tools pane) 

    
    def execute(self, context):  
        
        i= 0
        # 1. Schleife von start_frame to end_frame
        int_fStart = bpy.data.scenes['Scene'].frame_start
        int_fStop = bpy.data.scenes['Scene'].frame_end
        
        int_Count = int_fStop-int_fStart
        
        for i in range(0,int_Count,1):
            print("int_fcurrent: " + str(i))
            bpy.data.scenes['Scene'].frame_current= i
            
        
        #bpy.data.scenes['Scene'].frame_current
        
        
        # 1.1 Position von Traktor in Abh.keit vom aktuellen frame
        # 1.2 Traxtrix-Funktion fuettern
        # 1.3-a entweder Keyframe f�r jedes Frame des Trailers setzen
        # 1.3-b nur die Nurbspath Koordinaten nutzen und eine Trailer-Nurbs auf Basis der 
        # Traktor-Nurbs errechnen
       
       
       
        #Traktor = bpy.data.objects['Obj1']      
        #action_name = bpy.data.objects[Traktor.name].animation_data.action.name
        
        #action=bpy.data.actions[action_name]
        #locID, rotID = FindFCurveID(Traktor, action)
        #action.fcurves[locID[0]].keyframe_points[0].co      
        
        #bpy.data.curves[objCurve.name].splines
        
        #get_absolute()
        return {'FINISHED'} 
    writelog('- - Tractrix_OT_Main done- - - - - - -')
       

   


def get_absolute(Obj_Koord, Obj_Angle, BASEPos_Koord, BASEPos_Angle):
    # Obj_Koord und Obj_Angle sind lokale Angaben bezogen auf Base
    # Aufruf bei Import
    # Obj_Koord, Obj_Angle [rad]: relativ
    # BASEPos_Koord, BASEPos_Angle [rad]: absolut 
    
    # Transformation Local2World
    
    # Gegeben: Mtrans, Mrot = Base --> Mworld/ Mrot_rel, Vtrans_rel --> Mworld_rel
    # Ges:  Vtrans_abs, Mrot_abs
    #
    # Mworld  / Mworld_rel / Mworld_abs mit world = trans * rot
    # Mtrans  / Mtrans_rel / Mtrans_abs
    # Mrot    / Mrot_rel   / Mrot_abs
    
    # 01012014 objBase = bpy.data.objects['Sphere_BASEPos']
    #bpy.data.objects[Obj.name].rotation_mode =RotationModeTransform
    
    matrix_world =bpy.data.objects[objBase.name].matrix_world
    #point_local  = Obj_Koord 
    
    Mtrans     = mathutils.Matrix.Translation(Vector(BASEPos_Koord))
    Vtrans_rel = Obj_Koord                              #lokal 
    writelog('Vtrans_rel'+ str(Vtrans_rel))  # neuer Bezugspunkt
      
    MrotX = mathutils.Matrix.Rotation(BASEPos_Angle[0], 3, 'X') # C = -179 Global
    MrotY = mathutils.Matrix.Rotation(BASEPos_Angle[1], 3, 'Y') # B = -20
    MrotZ = mathutils.Matrix.Rotation(BASEPos_Angle[2], 3, 'Z') # A = -35
    Mrot = MrotZ * MrotY * MrotX
    writelog('Mrot'+ str(Mrot))
    
    Mworld = Mtrans * Mrot.to_4x4()
    
    Mrot_relX = mathutils.Matrix.Rotation(Obj_Angle[0], 3, 'X') # Local (bez. auf Base)
    Mrot_relY = mathutils.Matrix.Rotation(Obj_Angle[1], 3, 'Y') # 0,20,35 = X = -C, Y = -B, Z = -A
    Mrot_relZ = mathutils.Matrix.Rotation(Obj_Angle[2], 3, 'Z')
    Mrot_rel = Mrot_relZ * Mrot_relY * Mrot_relX # KUKA Erg.
    writelog('Mrot_rel'+ str(Mrot_rel))

    Mrot_abs = Mrot_rel.transposed() * Mrot.transposed()       
    Mrot_abs = Mrot_abs.transposed()
    rotEuler =Mrot_abs.to_euler('XYZ')
    
    writelog('rotEuler'+ str(rotEuler))
    writelog('rotEuler[0] :'+ str(rotEuler[0]*360/(2*math.pi)))
    writelog('rotEuler[1] :'+ str(rotEuler[1]*360/(2*math.pi)))
    writelog('rotEuler[2] :'+ str(rotEuler[2]*360/(2*math.pi)))
        
    Vtrans_abs = Mworld *Vtrans_rel
    writelog('Vtrans_abs :'+ str(Vtrans_abs))
       
    return Vtrans_abs, rotEuler

def FindFCurveID(objEmpty_A6, action):
    writelog('_____________________________________________________________________________')
    writelog('FindFCurveID')
   
    #ob_target = objEmpty_A6
    # todo: Unklar: mehrere Actions moeglich?! -> fuehrt ggf. zu einer Liste als Rueckgabewert:
    
    writelog(action.name)
    
    locID  =[9999, 9999, 9999]
    rotID  =[9999, 9999, 9999, 9999]
    scaleID=[9999, 9999, 9999]
    dlocID =[9999, 9999, 9999]
         
    action_data =action.fcurves
    writelog(action_data)
    
    for v,action_data in enumerate(action_data):
        if action_data.data_path == "location":
            locID[action_data.array_index] = v
            #ob_target.delta_location[action_data.array_index]=v
            writelog("location[" + str(action_data.array_index) + "] to (" + str(v) + ").")
        elif action_data.data_path == "rotation_quaternion":
            rotID[action_data.array_index] = v
            #ob_target.delta_rotation_euler[action_data.array_index]=v
            writelog("rotation_quaternion[" + str(action_data.array_index) + "] to (" + str(v) + ").")
        elif action_data.data_path == "scale":
            scaleID[action_data.array_index] = v
            #ob_target.delta_scale[action_data.array_index]=v
            writelog("scale[" + str(action_data.array_index) + "] to (" + str(v) + ").")
        elif action_data.data_path == "delta_location":
            dlocID[action_data.array_index] = v
            #ob_target.delta_scale[action_data.array_index]=v
            writelog("delta_location[" + str(action_data.array_index) + "] to (" + str(v) + ").")
        else:
            writelog("Unsupported data_path [" + action_data.data_path + "].")
    
      
class Tractrx_PT_Panel(bpy.types.Panel):
    writelog('_____________________________________________________________________________')
    writelog()
    writelog('Tractrx_PT_Panel....')
    writelog()
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Tractrix Panel" # heading of panel
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
        
        
        # Import Button:
        
        layout.label(text="object.tractrix:")
        row = layout.row(align=True)
        
        row.operator("object.tractrix")  
        
           
    writelog('Tractrx_PT_Panel done')
    writelog('_____________________________________________________________________________')


#class CURVE_OT_RefreshButtonButton(bpy.types.Operator):
 



    



# ________________________________________________________________________________________________________________________


#--- ### Register
#ToDo: KUKA Operator nicht regestriert....
def register():
    bpy.utils.register_class(Tractrx_PT_Panel)  
    register_module(__name__)
    
def unregister():
    bpy.utils.unregister_class(Tractrx_PT_Panel) 
    unregister_module(__name__)

#--- ### Main code    
if __name__ == '__main__':
    register()

