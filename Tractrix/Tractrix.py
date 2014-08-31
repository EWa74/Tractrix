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
# - Code Cleaning
# - Laenge der Slave-Kurve automatisch anpassen
# - Pruefung ob das Ergebnis des Trailers noch sinnvoll ist (Astand zum Traktor, delta Weg (-> proportional zu delta T)
# - Parenting
# - Menuefuehrung (Kurve auswählen, Objetk auswählen)
# - Import/ Export
# - Erbegnis "baken"


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
    "description": "Calculate Tractrix for Trailer Object from Tractor Object.",
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
objTrailerPath = bpy.data.objects['TrailerPath']
objTraktorPath = bpy.data.objects['TraktorPath']
objTrailer = bpy.data.objects['Trailer']
objTraktor = bpy.data.objects['Traktor']
curTraktor = bpy.data.curves[objTraktorPath.data.name]
curTrailer = bpy.data.curves[objTrailerPath.data.name]

# create variable containing width
bpy.types.Scene.pyramide_width = FloatProperty( name = "pyramide's width", default = 2.0, subtype = 'DISTANCE', unit = 'LENGTH', description = "Enter the pyramide's width!" )
bpy.types.Scene.traktrix_curvetype = '1' 

def writelog(text=''):
    FilenameLog = bpy.data.filepath
    FilenameLog = FilenameLog.replace(".blend", '.log')
    fout = open(FilenameLog, 'a')
    localtime = time.asctime( time.localtime(time.time()) )
    fout.write(localtime + " : " + str(text) + '\n')
    fout.close();

class Tractrix_PT_Panel(bpy.types.Panel):
    writelog('_____________________________________________________________________________')
    writelog()
    writelog('Tractrix_PT_Panel....')
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
        row = layout.row(align=True)
        
        # Create two columns, by using a split layout.
        split = layout.split()

        # First column
        col = split.column()
        col.label(text="Schleppkurven:")
        
        # Import Button:
        col.operator("object.hundekurve", text="Hundekurve [OK]")
        col.operator("object.tractrix3d", text="3D Traktrix-Traktor-Leitkuve v const.[ongoing]")
        col.operator("object.tractrix3dinv", text="2D Traktrix-Traktor-Leitkurve d const[ongoing]")
        col.operator("object.tractrix3dtbd", text="tbd...")
        col.operator("object.parenttraktor", text="parent TRAKTOR...")
        col.operator("object.parenttrailer", text="parent TRAILER...")
        col.operator("object.clearparent", text="clear parents...")
           
    writelog('Tractrix_PT_Panel done')
    writelog('_____________________________________________________________________________')


def ReadCurve(objPath):
    curObj = bpy.data.curves[objPath.data.name]
    int_Curve = len(bpy.data.curves[objPath.data.name].splines[0].points)
    datPath = createMatrix(int_Curve,3)
    
    
    for int_PCurve in range(0,int_Curve,1):
        datPath[int_PCurve][0:3] = [curObj.splines[0].points[int_PCurve].co.x, curObj.splines[0].points[int_PCurve].co.y, curObj.splines[0].points[int_PCurve].co.z]
        print("Traktor"  + str(int_PCurve) + ": " + str(datPath[int_PCurve]))
    
    print("Traktor" )
    
    
    return int_Curve, datPath
    '''
    #bpy.data.objects[objTrailer.name].location
    int_fMerker = bpy.data.scenes['Scene'].frame_current
    # 1. Schleife von start_frame to end_frame
    int_fStart = bpy.data.scenes['Scene'].frame_start
    int_fStop = bpy.data.scenes['Scene'].frame_end
      
    int_Count = int_fStop-int_fStart
    
    for int_fcurrent in range(1,int_Count,1):
        print("int_fcurrent: " + str(int_fcurrent))
        bpy.data.scenes['Scene'].frame_current= int_fcurrent
    bpy.data.scenes['Scene'].frame_current = int_fMerker
    '''
    
    
def WriteCurveTrailer(int_Curve, Trailer):
    
    
    
    for int_PCurve in range(0,int_Curve-1,1):
        [curTrailer.splines[0].points[int_PCurve].co.x, curTrailer.splines[0].points[int_PCurve].co.y, curTrailer.splines[0].points[int_PCurve].co.z] = Trailer[int_PCurve][0]
        print("Trailer"  + str(int_PCurve) + ": " + str(Trailer[int_PCurve]))
    print("Trailer" )
    

def SetObjToCurve(TrailerObj, datTrailerCurve, TraktorObj, datTraktorCurve):
    # Set Objects to curve
        
    # parenting lösen, Obj positionieren, follow path wieder herstellen:
    
    ClearParenting(objTrailer,objTrailerPath )
    ClearParenting(objTrailer,objTraktorPath )
    ClearParenting(objTrailer,objTraktor )
    
    ClearParenting(objTraktor,objTrailerPath )
    ClearParenting(objTraktor,objTraktorPath )
    ClearParenting(objTraktor,objTrailer )
    
    
    bpy.data.scenes['Scene'].frame_current = bpy.data.scenes['Scene'].frame_start
    objTrailer.location, objTrailer.rotation_euler = get_absolute(Vector(datTrailerCurve[0][0]), (0,0,0), objTrailerPath)
    objTraktor.location, objTraktor.rotation_euler = get_absolute(Vector(datTraktorCurve[0]), (0,0,0), objTraktorPath)
     
    '''   
    Parenting(objTraktorPath, objTraktor)
    Parenting(objTraktorPath, objTraktor)
    Parenting(objTrailerPath, objTrailer)
    Parenting(objTrailerPath, objTrailer)
    '''
    
        
class Hundekurve_OT_Main (bpy.types.Operator): # OT fuer Operator Type
   
    bl_idname = "object.hundekurve"
    bl_label = "Tractrix_OT_Main (TB)" #Toolbar - Label
    bl_description = "Calculate Tractrix for Trailer Object from Tractor Object." # Kommentar im Specials Kontextmenue
    bl_options = {'REGISTER', 'UNDO'} #Set this options, if you want to update  parameters of this operator interactively  (in the Tools pane) 

    def execute(self, context):  
        
        int_Curve, datTraktorCurve = ReadCurve(objTraktorPath)  
        
        datTrailerStart = [curTrailer.splines[0].points[0].co.x, curTrailer.splines[0].points[0].co.y, curTrailer.splines[0].points[0].co.z]
        
        datTrailerCurve= Hundekurve3D(datTraktorCurve, datTrailerStart)
        
        WriteCurveTrailer(int_Curve, datTrailerCurve)
        
        SetObjToCurve(objTrailer, datTrailerCurve, objTraktor, datTraktorCurve)
        
        return {'FINISHED'} 
    writelog('- - Tractrix_OT_Main done- - - - - - -')
    
    
class Tractrix3d_OT_Main (bpy.types.Operator): # OT fuer Operator Type
    # Arbeitsblatt 'Gewoehnliche DGL'
    bl_idname = "object.tractrix3d"
    bl_label = "Tractrix_OT_Main (TB)" #Toolbar - Label
    bl_description = "Calculate Tractrix for Trailer Object from Tractor Object." # Kommentar im Specials Kontextmenue
    bl_options = {'REGISTER', 'UNDO'} #Set this options, if you want to update  parameters of this operator interactively  (in the Tools pane) 

    def execute(self, context):  
        
        int_Curve, datTraktorCurve = ReadCurve(objTraktorPath)  
          
        datTrailerStart = [curTrailer.splines[0].points[0].co.x, curTrailer.splines[0].points[0].co.y, curTrailer.splines[0].points[0].co.z]
        
        datTrailerCurve= tractrix3D(datTraktorCurve, datTrailerStart)
        
        WriteCurveTrailer(int_Curve, datTrailerCurve)
        
        SetObjToCurve(objTrailer, datTrailerCurve, objTraktor, datTraktorCurve)
        
        return {'FINISHED'} 
    writelog('- - Tractrix_OT_Main done- - - - - - -')


class Tractrix3dinv_OT_Main (bpy.types.Operator): # OT fuer Operator Type
    # Traktrix-Traktor-Leitkurve-v-const
    bl_idname = "object.tractrix3dinv"
    bl_label = "Tractrix_OT_Main (TB)" #Toolbar - Label
    bl_description = "Calculate Tractrix for Trailer Object from Tractor Object." # Kommentar im Specials Kontextmenue
    bl_options = {'REGISTER', 'UNDO'} #Set this options, if you want to update  parameters of this operator interactively  (in the Tools pane) 

    def execute(self, context):  
        int_Curve, datTraktorCurve = ReadCurve(objTraktorPath)  
        
        datTrailerStart = [curTrailer.splines[0].points[0].co.x, curTrailer.splines[0].points[0].co.y, curTrailer.splines[0].points[0].co.z]
       
        datTrailerCurve= tractrix3Dinv(datTraktorCurve, datTrailerStart)
       
        WriteCurveTrailer(int_Curve, datTrailerCurve)
        
        SetObjToCurve(objTrailer, datTrailerCurve, objTraktor, datTraktorCurve)
       
        return {'FINISHED'} 
    writelog('- - Tractrix_OT_Main done- - - - - - -')

class Tractrix3dtbd_OT_Main (bpy.types.Operator): # OT fuer Operator Type
    bl_idname = "object.tractrix3dtbd"
    bl_label = "Tractrix_OT_Main (TB)" #Toolbar - Label
    bl_description = "Calculate Tractrix for Trailer Object from Tractor Object." # Kommentar im Specials Kontextmenue
    bl_options = {'REGISTER', 'UNDO'} #Set this options, if you want to update  parameters of this operator interactively  (in the Tools pane) 

    def execute(self, context):  
        int_Curve, datTraktorCurve = ReadCurve(objTraktorPath)  
        
        datTrailerStart = [curTrailer.splines[0].points[0].co.x, curTrailer.splines[0].points[0].co.y, curTrailer.splines[0].points[0].co.z]
       
        datTrailerCurve= tractrix3Dtbd(datTraktorCurve, datTrailerStart)
       
        WriteCurveTrailer(int_Curve, datTrailerCurve)
        
        SetObjToCurve(objTrailer, datTrailerCurve, objTraktor, datTraktorCurve)
       
        return {'FINISHED'} 
    writelog('- - Tractrix_OT_Main done- - - - - - -')   

class parenttraktor_OT_Main (bpy.types.Operator): # OT fuer Operator Type
    bl_idname = "object.parenttraktor"
    bl_label = "parent traktor" #Toolbar - Label
    bl_description = "parent traktor to curve" # Kommentar im Specials Kontextmenue
    bl_options = {'REGISTER', 'UNDO'} #Set this options, if you want to update  parameters of this operator interactively  (in the Tools pane) 

    def execute(self, context):
        

        ClearParenting(objTraktorPath, objTraktor )
        bpy.data.scenes['Scene'].frame_current = bpy.data.scenes['Scene'].frame_start
        datTraktorCurve = [curTraktor.splines[0].points[0].co.x, curTraktor.splines[0].points[0].co.y, curTraktor.splines[0].points[0].co.z]
        objTraktor.location, objTraktor.rotation_euler = get_absolute(Vector(datTraktorCurve), (0,0,0), bpy.data.objects[objTraktorPath])
         
            
        Parenting(objTraktorPath, objTraktor.name)    
        #Parenting(objTrailerPath, objTrailer.name) 
       
        return {'FINISHED'} 
    writelog('- - parenttraktor_OT_Main done- - - - - - -')   

class parenttrailer_OT_Main (bpy.types.Operator): # OT fuer Operator Type
    bl_idname = "object.parenttrailer"
    bl_label = "parent trailer" #Toolbar - Label
    bl_description = "parent trailer to curve" # Kommentar im Specials Kontextmenue
    bl_options = {'REGISTER', 'UNDO'} #Set this options, if you want to update  parameters of this operator interactively  (in the Tools pane) 

    def execute(self, context):
        
        ClearParenting(bpy.data.objects[objTrailerPath],bpy.data.objects[objTrailer.name] )
        
        bpy.data.scenes['Scene'].frame_current = bpy.data.scenes['Scene'].frame_start
        datTrailerrCurve = [curTrailer.splines[0].points[0].co.x, curTrailer.splines[0].points[0].co.y, curTrailer.splines[0].points[0].co.z]
        
        objTrailer.location,objTrailer.rotation_euler = get_absolute(Vector(datTrailerrCurve), (0,0,0), bpy.data.objects[objTrailerPath])
           
        #Parenting(objTraktorPath, objTraktor.name)    
        Parenting(objTrailerPath, objTrailer.name) 
       
        return {'FINISHED'} 
    writelog('- - parenttrailer_OT_Main done- - - - - - -') 
    
    
class clearparent_OT_Main (bpy.types.Operator): # OT fuer Operator Type
    bl_idname = "object.clearparent"
    bl_label = "parent trailer" #Toolbar - Label
    bl_description = "clear parent from curve" # Kommentar im Specials Kontextmenue
    bl_options = {'REGISTER', 'UNDO'} #Set this options, if you want to update  parameters of this operator interactively  (in the Tools pane) 

    def execute(self, context):
        ClearParenting(objTrailerPath,objTrailer )
        ClearParenting(objTrailerPath,objTraktor )
        ClearParenting(objTraktorPath,objTraktor )
        ClearParenting(objTraktorPath,objTrailer )
        ClearParenting(objTrailerPath,objTraktorPath )
        ClearParenting(objTraktorPath,objTrailerPath )
        
       
        return {'FINISHED'} 
    writelog('- - parenttrailer_OT_Main done- - - - - - -') 
      
    
def Hundekurve3D(datTraktor, datTrailerStart):
    # Ableitung aus Java-Script (link einfuegen...)
    
    # ACHTUNG: Abstand NICHT konstant! Damit KEINE Tractrix (-> Hundekurve)
    
    Mx = createMatrix(2,1)
    My = createMatrix(2,1)
    Mz = createMatrix(2,1)
    Sx = createMatrix(2,1)
    Sy = createMatrix(2,1)
    Sz = createMatrix(2,1)
    
    T1 = 0
    T2 = 1
    Term = float()
    
    Sx[T1][0] = datTrailerStart[0]
    Sy[T1][0] = datTrailerStart[1]
    Sz[T1][0] = datTrailerStart[2]
    
    int_Count = len(datTraktor[:][:])
    datTrailer = createMatrix(int_Count,1)
    datTrailer[0][0] = [Sx[T1][0], Sy[T1][0], Sz[T1][0]]
    
    # y0 =((D4*G3-D4*D3+D3*D3-D3*G3)+(E4*H3-E4*E3+E3*E3-E3*H3)+(F4*I3-F4*F3+F3*F3-F3*I3))*(G3-D3)+G3
    # y1 =((D4*G3-D4*D3+D3*D3-D3*G3)+(E4*H3-E4*E3+E3*E3-E3*H3)+(F4*I3-F4*F3+F3*F3-F3*I3))*(H3-E3)+H3
    # y2 =((D4*G3-D4*D3+D3*D3-D3*G3)+(E4*H3-E4*E3+E3*E3-E3*H3)+(F4*I3-F4*F3+F3*F3-F3*I3))*(I3-F3)+I3 
    #
    # mit DEF = Traktor(x,y,z) = M(x,y,z) und GHI = Trailer(x,y,z) = S(x,y,z) zum Zeitpunkt T1, T2
    
    
    for int_PCurve in range(0,int_Count-1,1):
        
        
        
        Mx[T1][0], My[T1][0], Mz[T1][0] = [datTraktor[int_PCurve][0], datTraktor[int_PCurve][1], datTraktor[int_PCurve][2]]
        Mx[T2][0], My[T2][0], Mz[T2][0] = [datTraktor[int_PCurve+1][0], datTraktor[int_PCurve+1][1], datTraktor[int_PCurve+1][2]]
        
        # Term =((D4       *G3       -D4       *D3       +D3       *D3       -D3       *G3       )+(E4       *H3       -E4       *E3       +E3       *E3       -E3       *H3       )+(F4       *I3       -F4       *F3       +F3       *F3       -F3       *I3       ))
        Term = [((Mx[T2][0]*Sx[T1][0]-Mx[T2][0]*Mx[T1][0]+Mx[T1][0]*Mx[T1][0]-Mx[T1][0]*Sx[T1][0])+(My[T2][0]*Sy[T1][0]-My[T2][0]*My[T1][0]+My[T1][0]*My[T1][0]-My[T1][0]*Sy[T1][0])+(Mz[T2][0]*Sz[T1][0]-Mz[T2][0]*Mz[T1][0]+Mz[T1][0]*Mz[T1][0]-Mz[T1][0]*Sz[T1][0]))] 
        print("Term : " + str(Term))
        Sx[T2][0] = Term[0] * (Sx[T1][0]-Mx[T1][0])+Sx[T1][0]
        Sy[T2][0] = Term[0] * (Sy[T1][0]-My[T1][0])+Sy[T1][0]
        Sz[T2][0] = Term[0] * (Sz[T1][0]-Mz[T1][0])+Sz[T1][0]
        
        datTrailer[int_PCurve][0] = Sx[T2][0], Sy[T2][0], Sz[T2][0]
        print("Trailer"  + str(int_PCurve) + ": " + str(datTrailer[int_PCurve]))
        
        Sx[T1][0] = deepcopy(Sx[T2][0])
        Sy[T1][0] = deepcopy(Sy[T2][0])
        Sz[T1][0] = deepcopy(Sz[T2][0])
        
    return datTrailer

def tractrix3D(datTraktor, datTrailerStart):
    # Arbeitsblatt 'Gewoehnliche DGL'
    # Anstand konstant
    # v (Geschw.) immer in Richtung Traktor
    
    # ACHTUNG: Abstand NICHT konstant! Damit KEINE Tractrix (-> Hundekurve)
    # todo: Ergebnis 'seltsam'.....
    
    Mx = createMatrix(2,1)
    My = createMatrix(2,1)
    Mz = createMatrix(2,1)
    Sx = createMatrix(2,1)
    Sy = createMatrix(2,1)
    Sz = createMatrix(2,1)
    
    T1 = 0
    T2 = 1
    Term = float()
    
    Sx[T1][0] = datTrailerStart[0]
    Sy[T1][0] = datTrailerStart[1]
    Sz[T1][0] = datTrailerStart[2]
    
    int_Count = len(datTraktor[:][:])
    datTrailer = createMatrix(int_Count,1)
    datTrailer[0][0] = [Sx[T1][0], Sy[T1][0], Sz[T1][0]]
    
    
    # y0 = (((D6-D5)*(D5-G5)+(E6-E5)*(E5-H5))/(D5-H5)^2+(E5-H5)^2)*(D5-G5)+G5
    # y1 = (((D6-D5)*(D5-G5)+(E6-E5)*(E5-H5))/(D5-H5)^2+(E5-H5)^2)*(E5-H5)+H5
    # y2 = (((D6-D5)*(D5-G5)+(E6-E5)*(E5-H5))/(D5-H5)^2+(E5-H5)^2)*(f5-g5)+i5
    
    # y2 = (((D6-D5)*(D5-G5)+(E6-E5)*(E5-H5)+(f6-f5)*(f5-g5))/((D5-H5)^2+(E5-H5)^2+(f5-g5)^2)))*(f5-g5)+i5
    #
    # mit DEF = Traktor(x,y,z) = M(x,y,z) und GHI = Trailer(x,y,z) = S(x,y,z) zum Zeitpunkt T1, T2
    
    
    for int_PCurve in range(0,int_Count-1,1):
        
        Mx[T1][0], My[T1][0], Mz[T1][0] = [datTraktor[int_PCurve][0], datTraktor[int_PCurve][1], datTraktor[int_PCurve][2]]
        Mx[T2][0], My[T2][0], Mz[T2][0] = [datTraktor[int_PCurve+1][0], datTraktor[int_PCurve+1][1], datTraktor[int_PCurve+1][2]]
        
        # Schleppkurve V1 - Term = (((D6-D5)*(D5-G5)+(E6-E5)*(E5-H5))                /((D5-H5)^2+(E5-H5)^2))
        # Schleppkurve V1 - Term = (((D6-D5)*(D5-G5)+(E6-E5)*(E5-H5)+(f6-f5)*(f5-g5))/((D5-H5)^2+(E5-H5)^2+(f5-g5)^2)))
        # math.pow(PathPointA[i], 2)
        
        Term = ((Mx[T2][0]-Mx[T1][0])*(Mx[T1][0]-Sx[T1][0])+(My[T2][0]-My[T1][0])*(My[T1][0]-Sy[T1][0])+(Mz[T2][0]-Mz[T1][0])*(Mz[T1][0]-Sz[T1][0]))/(math.pow((Mx[T1][0]-Sx[T1][0]),2)+ math.pow((My[T1][0]-Sy[T1][0]),2)+ math.pow((Mz[T1][0]-Sz[T1][0]),2))
        
       
        # Hundekurve - Term = [((Mx[T2][0]*Sx[T1][0]-Mx[T2][0]*Mx[T1][0]+Mx[T1][0]*Mx[T1][0]-Mx[T1][0]*Sx[T1][0])+(My[T2][0]*Sy[T1][0]-My[T2][0]*My[T1][0]+My[T1][0]*My[T1][0]-My[T1][0]*Sy[T1][0])+(Mz[T2][0]*Sz[T1][0]-Mz[T2][0]*Mz[T1][0]+Mz[T1][0]*Mz[T1][0]-Mz[T1][0]*Sz[T1][0]))] 
        print("Term : " + str(Term))
        
        # y0 = (((D6-D5)*(D5-G5)+(E6-E5)*(E5-H5))/(D5-H5)^2+(E5-H5)^2)*(D5-G5)+G5
        # y1 = (((D6-D5)*(D5-G5)+(E6-E5)*(E5-H5))/(D5-H5)^2+(E5-H5)^2)*(E5-H5)+H5
        # y2 = (((D6-D5)*(D5-G5)+(E6-E5)*(E5-H5))/(D5-H5)^2+(E5-H5)^2)*(f5-i5)+i5
    
        Sx[T2][0] = Term * (Mx[T1][0]-Sx[T1][0])+Sx[T1][0] # *(D5-G5)+G5
        Sy[T2][0] = Term * (My[T1][0]-Sy[T1][0])+Sy[T1][0] # *(E5-H5)+H5
        Sz[T2][0] = Term * (Mz[T1][0]-Sz[T1][0])+Sz[T1][0] # *(f5-i5)+i5
        
        datTrailer[int_PCurve][0] = Sx[T2][0], Sy[T2][0], Sz[T2][0]
        print("Trailer"  + str(int_PCurve) + ": " + str(datTrailer[int_PCurve]))
        
        Sx[T1][0] = deepcopy(Sx[T2][0])
        Sy[T1][0] = deepcopy(Sy[T2][0])
        Sz[T1][0] = deepcopy(Sz[T2][0])
        
    return datTrailer



def tractrix3Dinv(datTraktor, datTrailerStart):
    # Leipnitzschule Hannover Schleppkurve 2D
    # Abstand konstant 
    
    # ACHTUNG: Leitkurve ist Trailer; Traktor wird berechnet
    # under constr...
    
    Mx = createMatrix(2,1)
    My = createMatrix(2,1)
    Mz = createMatrix(2,1)
    Sx = createMatrix(2,1)
    Sy = createMatrix(2,1)
    Sz = createMatrix(2,1)
    
    T1 = 0
    T2 = 1
    Term = float()
    
    Sx[T1][0] = datTrailerStart[0]
    Sy[T1][0] = datTrailerStart[1]
    Sz[T1][0] = datTrailerStart[2]
    
    d = math.sqrt(math.pow((Mx[T1][0]-Sx[T1][0]),2) + math.pow((My[T1][0]-Sy[T1][0]),2)+ math.pow((Mz[T1][0]-Sz[T1][0]),2))
    
    int_Count = len(datTraktor[:][:])
    datTrailer = createMatrix(int_Count,1)
    datTrailer[0][0] = [Sx[T1][0], Sy[T1][0], Sz[T1][0]]
      
    # y0 = D5+($B$5/((((E5-E4)/(D5-D4))^2+1)^0.5))
    # y1 = E5+($B$5*(E5-E4)/((D5-D4)*(((E5-E4)/(D5-D4))^2+1)^0.5))
    # mit B5 = d = Abstand Traktor/Trailer
    
    # mit DEF = Traktor(x,y,z) = M(x,y,z) und GHI = Trailer(x,y,z) = S(x,y,z) zum Zeitpunkt T1, T2
    
    
    for int_PCurve in range(0,int_Count-1,1):
        
        Mx[T1][0], My[T1][0], Mz[T1][0] = [datTraktor[int_PCurve][0], datTraktor[int_PCurve][1], datTraktor[int_PCurve][2]]
        Mx[T2][0], My[T2][0], Mz[T2][0] = [datTraktor[int_PCurve+1][0], datTraktor[int_PCurve+1][1], datTraktor[int_PCurve+1][2]]
        
        # Schleppkurve V2 - Term = ((E5-E4)/(D5-D4))^2+1)^0.5)
        # math.pow(PathPointA[i], 2)
        
        # todo....
        #   
               
        Term = math.pow((math.pow( (My[T2][0]-My[T1][0])/(Mx[T2][0]-Mx[T1][0]),2)+1),0.5)
        
        # Hundekurve - Term = [((Mx[T2][0]*Sx[T1][0]-Mx[T2][0]*Mx[T1][0]+Mx[T1][0]*Mx[T1][0]-Mx[T1][0]*Sx[T1][0])+(My[T2][0]*Sy[T1][0]-My[T2][0]*My[T1][0]+My[T1][0]*My[T1][0]-My[T1][0]*Sy[T1][0])+(Mz[T2][0]*Sz[T1][0]-Mz[T2][0]*Mz[T1][0]+Mz[T1][0]*Mz[T1][0]-Mz[T1][0]*Sz[T1][0]))] 
        print("Term : " + str(Term))
        
        # y0 = D5+($B$5/(term)
        # 
        # y1 = E5+($B$5*(E5-E4)/((D5-D4)*Term)
        #
    
        Sx[T2][0] = Mx[T2][0] + d / Term  # 
        Sy[T2][0] = My[T2][0] + d * ((My[T2][0]-My[T1][0]) / ((Mx[T2][0]-Mx[T1][0])*Term))
        Sz[T2][0] = Sz[T1][0] # 
        
        datTrailer[int_PCurve][0] = Sx[T2][0], Sy[T2][0], Sz[T2][0]
        print("Trailer"  + str(int_PCurve) + ": " + str(datTrailer[int_PCurve]))
        
        Sx[T1][0] = deepcopy(Sx[T2][0])
        Sy[T1][0] = deepcopy(Sy[T2][0])
        Sz[T1][0] = deepcopy(Sz[T2][0])
        
    return datTrailer

def tractrix3Dtbd(datTraktorCurve, datTrailerStart):
    print('under construction...')
 
class createMatrix(object):
    #writelog('_____________________________________________________________________________')
    #writelog('createMatrix')
    def __init__(self, rows, columns, default=0):
        self.m = []
        for i in range(rows):
            self.m.append([default for j in range(columns)])
    def __getitem__(self, index):
        return self.m[index]
    writelog('createMatrix done')
    writelog('_____________________________________________________________________________')  


def Parenting(Mother, Child):
    
    bpy.ops.object.select_all(action='DESELECT')
    Mother.select= True
    Child.select = True
    bpy.context.scene.objects.active = Mother
    # Parenting wieder herstellen    
    bpy.ops.object.parent_set(type='FOLLOW', xmirror=False, keep_transform=True)
    #bpy.ops.object.parent_set(type='FOLLOW', xmirror=False, keep_transform=True)
    bpy.ops.object.select_all(action='DESELECT')

    
def ClearParenting(Mother, Child):
    
    # - Deselect alle Objekte und in Objekte in richtiger Reihenfolge auswählen
    bpy.ops.object.select_all(action='DESELECT')
    Child.select= True
    Mother.select = True
    # - Parenting lösen    
    bpy.ops.object.parent_clear(type='CLEAR') # CLEAR_KEEP_TRANSFORM
    # - deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    # - Kurve selektieren
    #Mother.select = True


def get_absolute(Obj_Koord, Obj_Angle, objBase):
    BASEPos_Koord = objBase.location
    BASEPos_Angle = objBase.rotation_euler
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

   
      

#class CURVE_OT_RefreshButtonButton(bpy.types.Operator):
 



    



# ________________________________________________________________________________________________________________________


#--- ### Register
#ToDo: KUKA Operator nicht regestriert....
def register():
    bpy.utils.register_class(Tractrix_PT_Panel)  
    bpy.utils.register_class(Hundekurve_OT_Main) 
    bpy.utils.register_class(Tractrix3d_OT_Main) 
    bpy.utils.register_class(Tractrix3dinv_OT_Main) 
    bpy.utils.register_class(Tractrix3dtbd_OT_Main) 
    bpy.utils.register_class(parenttraktor_OT_Main)
    bpy.utils.register_class(parenttrailer_OT_Main)
    register_module(__name__)
    
def unregister():
    bpy.utils.unregister_class(Tractrix_PT_Panel) 
    bpy.utils.unregister_class(Hundekurve_OT_Main) 
    bpy.utils.unregister_class(Tractrix3d_OT_Main) 
    bpy.utils.unregister_class(Tractrix3dinv_OT_Main) 
    bpy.utils.unregister_class(Tractrix3dtbd_OT_Main) 
    bpy.utils.unregister_class(parenttraktor_OT_Main)
    bpy.utils.unregister_class(parenttrailer_OT_Main)
    unregister_module(__name__)

#--- ### Main code    
if __name__ == '__main__':
    register()

#todo: code cleaning
#Loesungsweg A):
# B1 Die Nurbspath Koordinaten nutzen und eine Trailer-Nurbs auf Basis der 
# Traktor-Nurbs errechnen
# Beachte: ggf. später Koordinaten von local auf world transformieren       
#Loesungsweg B):
# B1.1 Position von Traktor in Abh.keit vom aktuellen frame bestimmen (-> local2world transformation -> Kuka -> get_absolute())
# und die Traxtrix-Funktion fuettern. 
# für (jeden?) Frame des Traktors ein Keyframe für den Trailers setzen

#Traktor = bpy.data.objects['Obj1']      
#action_name = bpy.data.objects[Traktor.name].animation_data.action.name
 
#action=bpy.data.actions[action_name]
#locID, rotID = FindFCurveID(Traktor, action)
#action.fcurves[locID[0]].keyframe_points[0].co   