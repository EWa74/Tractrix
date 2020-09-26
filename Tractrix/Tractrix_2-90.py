# -*- coding: utf-8 -*-    
#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# coding Angabe in Zeilen 1 und 2 fuer Eclipse Luna/ Pydev 3.9 notwendig
# cp1252

#  ***** BEGIN GPL LICENSE BLOCK ***** 
#  https://github.com/EWa74/Tractrix.git
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
# Version: 101R - Laeuft auf 2.90


# Beschreibung   
# Die Nurbspath Koordinaten des Trailers werden basierend auf den   
# Traktor-Nurbs errechnen
# Die Objekte werden unter beruecksichtigung der Kurven im World-Space 
# auf den ersten Spline-Koordinaten der Kurven gesetzt
# die Schleppkurve ist vom Typ Traktrix. D.h. der Abstand bleibt konstant.

# Traktor: Objekt das der Leitkurve folgt.
# Traktorpath: Leikurve
# Trailer: .
# Trailerpath: 3d-Radiodrome? (d.h. Verfolgekurve mit konst. Geschw.; aber nicht gleich zum Leitpunkt; gleicher Abstand)


 
# Beachte: 
#   Wenn die Punkte die die Kurve beschreiben zu weit auseinander liegen, 
#   erhaelt man ein unsinniges Ergebnis. Loesung:
#   fuer beide Kurven: -> EditMode [TAB] -> [A] alle auswaehlen 
#   [w] fuer specials menue druecken -> Subdivide 
#   (Achtung: die Kurvenpunkte fuer Trailer muss >= der des Traktors sein)

# ToDo:
# - Pruefung ob das Ergebnis des Trailers noch sinnvoll ist (Astand zum Traktor, delta Weg (-> proportional zu delta T)
# - Akutell arbeitet das Programm nur mit NURBSPATH. D.h. die Rotation des Splines wird nicht bruecksichtigt.
#   Traktor/ Trailer kann man über follow path constraint mit rotation animieren.
# - Laenge der Slave-Kurve automatisch anpassen
# - Import/ Export
# - Erbegnis "baken"
# - Abstand Abpruefen bei Berechnung und auf Fehler hinweisen
# - Kurven funktonieren z.Zt. NUR wenn der Origin auf [0,0,0] ist!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# - laesst sich noch nicht als AddOn starten, wegen initialisierungsproblem von filepath (ggf. writelog raus)

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
    "blender": (2, 90, 0),
    "api": 36147,
    "location": "View3D >Tools > Create",
    "category": "Curve",
    "description": "Calculate the path for Trailer Object following the Tractor Object.",
    "warning": "",
    "wiki_url": "http://...",
    "tracker_url": "http://..."
    }

#import pydevd 
#pydevd.settrace()  #<-- debugger stops at the next statement 
#import pydevd;pydevd.settrace() # notwendig weil breakpoints uebersprungen werden. warum auch immer
     
#--- ### Imports
import bpy

# https://blender.stackexchange.com/questions/8702/attributeerror-restrictdata-object-has-no-attribute-filepath
#from bpy.app.handlers import persistent

'''
from bpy.app.handlers import persistent
@persistent
def foobar(scene):
    bpy.data.filepath
'''

# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy_extras.io_utils import ImportHelper
import time # um Zeitstempel im Logfile zu schreiben
import bpy, os
import sys
# from bpy.utils import register_module, unregister_module
from mathutils import Vector  
from mathutils import *
import mathutils
import math
import re  # zum sortieren de Objektliste
from symbol import except_clause
from copy import deepcopy # fuer OptimizeRotation


from bpy.types import (
        Operator,
        Panel,
        PropertyGroup,
        )

from bpy.props import (
        BoolProperty,
        IntProperty,
        FloatProperty,
        EnumProperty,
        CollectionProperty,
        StringProperty,
        PointerProperty
        #FloatVectorProperty,
        )


def writelog(text=''):
    #print('auskommentiert....')
    '''
    FilenameLog = bpy.data.filepath
    FilenameLog = FilenameLog.replace(".blend", '.log')
    fout = open(FilenameLog, 'a')
    localtime = time.asctime( time.localtime(time.time()) )
    fout.write(localtime + " : " + str(text) + '\n')
    fout.close();
    '''

class Tractrix_PT_Panel(bpy.types.Panel):
    writelog('_____________________________________________________________________________')
    writelog()
    writelog('Tractrix_PT_Panel....')
    writelog()
    
    """Creates a Panel in the Tool-panel under the <creates> tab of the 3D-View"""
    bl_idname = "VIEW3D_PT_layout"
    bl_label = "Tractrix" # heading of panel
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "Create"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        
        ob = context.object
        layout = self.layout
        scene = context.scene
        
        split = layout.split()
        col = split.column()
        col.label(text="Schleppkurven:")
        
        col.operator("tractrix.clearanimation", text="1. clear Animations")  
        
        col.prop_search(scene.tractrix, "traktor", scene, "objects", icon = 'OBJECT_DATA', text = "Traktor")
        col.prop_search(scene.tractrix, "traktorpath", scene, "objects", icon = 'CURVE_BEZCURVE', text = "Traktor path")
        col.prop_search(scene.tractrix, "trailer", scene, "objects", icon = 'OBJECT_DATA', text = "Trailer")
        col.prop_search(scene.tractrix, "trailerpath", scene, "objects", icon = 'CURVE_BEZCURVE', text = "Trailer path")
        
        col.operator("tractrix.setobj2curve", text="2. set 2 path")
        col.prop(scene.tractrix, "SolverMode", icon = 'CON_ROTLIKE', text = "Sover")
        col.operator("tractrix.calculate", text="calculate path")        
            
    writelog('Tractrix_PT_Panel done')
    writelog('_____________________________________________________________________________')


def ReadCurve(objPath):
    curObj = bpy.data.curves[objPath.data.name]
    int_Curve = len(bpy.data.curves[objPath.data.name].splines[0].points)
    datPath = createMatrix(int_Curve,3)
    
    for int_PCurve in range(0,int_Curve,1):       
        #objTraktor.location, objTraktor.rotation_euler = get_absolute(Vector(datTraktorCurve), (0,0,0), objTraktorPath)
        datPath[int_PCurve][0:3] = [curObj.splines[0].points[int_PCurve].co.x, curObj.splines[0].points[int_PCurve].co.y, curObj.splines[0].points[int_PCurve].co.z]
 
    return int_Curve, datPath
  
    
def WriteCurveTrailer(int_Curve, Trailer):
    
    #bpy.data.objects[Trailer].data.splines 
    objTrailerPath = bpy.data.objects[bpy.context.scene.tractrix.trailerpath]
    objTrailer = bpy.data.objects[bpy.context.scene.tractrix.trailer] 
    curTrailer = bpy.data.curves[objTrailerPath.data.name]    
    
    for int_PCurve in range(0,int_Curve-1,1):
        [curTrailer.splines[0].points[int_PCurve].co.x, curTrailer.splines[0].points[int_PCurve].co.y, curTrailer.splines[0].points[int_PCurve].co.z] = Trailer[int_PCurve][0]


def time_to_frame(time_value):
    fps = bpy.context.scene.render.fps
    frame_number = (time_value * fps) +1
    return int(round(frame_number, 0)) 

def SetKeyFrames(obj, cur, objPath, int_Curve, TIMEPTS):
    
    # objEmpty_A6 -> objTraktor
    # TargetObjList -> datTraktorCurve
    # TIMEPTS -> tbd
    
    original_type         = bpy.context.area.type
    bpy.context.area.type = "VIEW_3D"
    bpy.ops.object.select_all(action='DESELECT')
          
    #scene = bpy.context.scene
    #fps = scene.render.fps
    #fps_base = scene.render.fps_base
     
    raw_time=[]
    frame_number=[]
    
    bpy.context.view_layer.objects.active = obj
    
    obj.select_set(True)
    bpy.ops.anim.keyframe_clear_v3d() #Remove all keyframe animation for selected objects

    ob = bpy.context.active_object
    ob.rotation_mode = 'QUATERNION' #'XYZ'
    
    
    #QuaternionList = OptimizeRotationQuaternion(TargetObjList, TIMEPTSCount)
    for n in range(0,int_Curve-1,1):
        # Trailer[int_PCurve][0]
        #writelog(n)
        #290 bpy.context.scene.frame_set(time_to_frame(TIMEPTS[n]))  
        bpy.data.scenes['Scene'].frame_set(time_to_frame(TIMEPTS[n])) 
        
        # 04.09.2014 todo.....
        #c = Vector([cur.splines[0].points[n].co.x, cur.splines[0].points[n].co.y, cur.splines[0].points[n].co.z])
        #a, b = get_absolute(c, (0,0,0), objPath)
        
        ob.location = [cur.splines[0].points[n].co.x, cur.splines[0].points[n].co.y, cur.splines[0].points[n].co.z]
        
        #ob.location = bpy.data.objects[TargetObjList[n]].location
                
        # todo: ob.rotation_quaternion = bpy.data.objects[TargetObjList[n]].rotation_euler.to_quaternion()
           
        ob.keyframe_insert(data_path="location", index=-1)

        # file:///F:/EWa_WWW_Tutorials/Scripting/blender_python_reference_2_68_5/bpy.types.bpy_struct.html#bpy.types.bpy_struct.keyframe_insert
        
        # todo: ob.keyframe_insert(data_path="rotation_quaternion", index=-1)
        
        #ob.keyframe_insert(data_path="rotation_euler", index=-1)
    bpy.context.area.type = original_type 
    #writelog(n)
 
        
class Traktrix_OT_Main (bpy.types.Operator):    
    bl_idname = "tractrix.calculate"
    bl_label = "Tractrix_OT_Main (TB)" #Toolbar - Label
    bl_description = "Calculate Tractrix for Trailer Object from Tractor Object." 
    bl_options = {'REGISTER', 'UNDO'} 

    def execute(self, context):  
        
        objTraktorPath = bpy.data.objects[bpy.context.scene.tractrix.traktorpath] 
        objTraktor = bpy.data.objects[bpy.context.scene.tractrix.traktor] 
        objTrailerPath = bpy.data.objects[bpy.context.scene.tractrix.trailerpath]
        objTrailer = bpy.data.objects[bpy.context.scene.tractrix.trailer]
        curTraktor = bpy.data.curves[objTraktorPath.data.name]
        curTrailer = bpy.data.curves[objTrailerPath.data.name]     
            
        int_Curve, datTraktorCurve = ReadCurve(objTraktorPath)  
        
        datTrailerStart = [curTrailer.splines[0].points[0].co.x, curTrailer.splines[0].points[0].co.y, curTrailer.splines[0].points[0].co.z]
        # ToDo: datTraktorCurve muss noch mit getabsoulute umgerechnet werden...
        datTrailerCurve= Traktrix3D(datTraktorCurve, datTrailerStart)
        
        WriteCurveTrailer(int_Curve, datTrailerCurve)
        
        TIMEPTS = []
        for int_PCurve in range(0,int_Curve-1,1):
            TIMEPTS = TIMEPTS + [int_PCurve/12]
        
        # 04.09.2014 todo.....
        SetKeyFrames(objTraktor, curTraktor, objTraktorPath, int_Curve, TIMEPTS)
        SetKeyFrames(objTrailer, curTrailer, objTrailerPath, int_Curve, TIMEPTS)
    
        return {'FINISHED'} 
    writelog('- - Tractrix_OT_Main done- - - - - - -')

 
class setobj2curve_OT_Main (bpy.types.Operator):
    bl_idname = "tractrix.setobj2curve"
    bl_label = "set objects to path" 
    bl_description = "set traktor and trailer objects to cures" 
    bl_options = {'REGISTER', 'UNDO'} 
    
    def execute(self, context):
        bpy.data.scenes['Scene'].frame_current = bpy.data.scenes['Scene'].frame_start
        
        objTraktorPath = bpy.data.objects[bpy.context.scene.tractrix.traktorpath] 
        objTraktor = bpy.data.objects[bpy.context.scene.tractrix.traktor] 
        curTraktor = bpy.data.curves[objTraktorPath.data.name]
        
        datTraktorCurve = [curTraktor.splines[0].points[0].co.x, curTraktor.splines[0].points[0].co.y, curTraktor.splines[0].points[0].co.z]
        objTraktor.location, objTraktor.rotation_euler = get_absolute(Vector(datTraktorCurve), (0,0,0), objTraktorPath)
        
        
        objTrailerPath = bpy.data.objects[bpy.context.scene.tractrix.trailerpath]
        objTrailer = bpy.data.objects[bpy.context.scene.tractrix.trailer] 
        curTrailer = bpy.data.curves[objTrailerPath.data.name]    
        
        datTrailerCurve = [curTrailer.splines[0].points[0].co.x, curTrailer.splines[0].points[0].co.y, curTrailer.splines[0].points[0].co.z]
        objTrailer.location,objTrailer.rotation_euler = get_absolute(Vector(datTrailerCurve), (0,0,0), objTrailerPath)

        return {'FINISHED'} 
    writelog('- - setobj2curve_OT_Main done- - - - - - -') 
    
class clearanimation_OT_Main (bpy.types.Operator): 
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
          
        return {'FINISHED'} 
    writelog('- - parenttrailer_OT_Main done- - - - - - -') 

   
def Traktrix3D(datTraktor, datTrailerStart):
    
    # Variante 1
    
    # Ableitung aus Java-Script (link einfuegen...)
    # Status (Variante 1): OK (Zeigt geringeren Rechenfehler als Variante 2.
    # -> Rechenfehler optimieren indem Berechnungen in der Schleife reduziert werden. -> Variante 1a
    
    # Pruefen: 
    # a) die Wegpunkte vom Master/ Traktor muessen absolut aequidistant sein?... 
    # --> gegeben (vgl. Traktor Wegpunkte)
    # b) die Geschwindigkeit vom Slave/ Trailer darf nicht gegen Null gehen? (vgl. Formel)
    # Todo: 
    # - Rechenfehler (Abweichung von soll/ ist Distanz) --> ggf. mehr Wegpunkte notwendig;
    # - moeglich nicht alle Keyframes zu setzten? bzw. Verteilung ueber GUI steuern. 
    # --> Residuen zum minimieren des Fehlers...
          
    Mx = createMatrix(2,1)
    My = createMatrix(2,1)
    Mz = createMatrix(2,1)
    Sx = createMatrix(2,1)
    Sy = createMatrix(2,1) 
    Sz = createMatrix(2,1) 
    n  = [0,1,2,3]
    
    T1 = 0
    T2 = 1
    Term = float()
    
    Sx[T1][0] = datTrailerStart[0]
    Sy[T1][0] = datTrailerStart[1]
    Sz[T1][0] = datTrailerStart[2]
    
    int_Count = len(datTraktor[:][:])
    datTrailer = createMatrix(int_Count,1)
    datTrailer[0][0] = [Sx[T1][0], Sy[T1][0], Sz[T1][0]]
    
    for int_PCurve in range(0,int_Count-1,1):
        
        Mx[T1][0], My[T1][0], Mz[T1][0] = [datTraktor[int_PCurve][0], datTraktor[int_PCurve][1], datTraktor[int_PCurve][2]]
        Mx[T2][0], My[T2][0], Mz[T2][0] = [datTraktor[int_PCurve+1][0], datTraktor[int_PCurve+1][1], datTraktor[int_PCurve+1][2]]
        
        nn= math.sqrt(math.pow((Sx[T1][0] - Mx[T1][0]),2) + math.pow((Sy[T1][0] - My[T1][0]),2) + math.pow((Sz[T1][0] - Mz[T1][0]),2))
            
        n[1] = (Sx[T1][0] - Mx[T1][0])/nn
        n[2] = (Sy[T1][0] - My[T1][0])/nn
        n[3] = (Sz[T1][0] - Mz[T1][0])/nn
        
        Term = ((Mx[T2][0] -Mx[T1][0]) *n[1]+
                (My[T2][0] -My[T1][0]) *n[2]+
                (Mz[T2][0] -Mz[T1][0]) *n[3])
        
        #Gravity =  0* Sz[T1][0] - 0.1 * math.pow((T2-T1),2) 
        #Abstand = math.pow(math.pow((datTraktor[0][0]-Sx[T1][0]),2)+math.pow((datTraktor[0][1]-Sy[T1][0]),2)+math.pow((datTraktor[0][2]-Sz[T1][0]),2), 0.5)
        AbstandT1 = math.pow(math.pow((datTraktor[int_PCurve][0]-Sx[T1][0]),2)+math.pow((datTraktor[int_PCurve][1]-Sy[T1][0]),2)+math.pow((datTraktor[int_PCurve][2]-Sz[T1][0]),2), 0.5)
        
        Sx[T2][0] = Sx[T1][0] + Term * n[1]
        Sy[T2][0] = Sy[T1][0] + Term * n[2]
        Sz[T2][0] = Sz[T1][0] + Term * n[3]  #+ (Gravity)
        
        datTrailer[int_PCurve+1][0] = Sx[T2][0], Sy[T2][0], Sz[T2][0]
                
        Sx[T1][0] = deepcopy(Sx[T2][0])
        Sy[T1][0] = deepcopy(Sy[T2][0])
        Sz[T1][0] = deepcopy(Sz[T2][0])
    
    return datTrailer 
 


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
    #writelog('Vtrans_rel'+ str(Vtrans_rel))  # neuer Bezugspunkt
      
    MrotX = mathutils.Matrix.Rotation(BASEPos_Angle[0], 3, 'X') # C = -179 Global
    MrotY = mathutils.Matrix.Rotation(BASEPos_Angle[1], 3, 'Y') # B = -20
    MrotZ = mathutils.Matrix.Rotation(BASEPos_Angle[2], 3, 'Z') # A = -35
    Mrot = MrotZ @ MrotY @ MrotX
    #writelog('Mrot'+ str(Mrot))
    
    Mworld = Mtrans @ Mrot.to_4x4()
    
    Mrot_relX = mathutils.Matrix.Rotation(Obj_Angle[0], 3, 'X') # Local (bez. auf Base)
    Mrot_relY = mathutils.Matrix.Rotation(Obj_Angle[1], 3, 'Y') # 0,20,35 = X = -C, Y = -B, Z = -A
    Mrot_relZ = mathutils.Matrix.Rotation(Obj_Angle[2], 3, 'Z')
    Mrot_rel = Mrot_relZ @ Mrot_relY @ Mrot_relX # KUKA Erg.
    #writelog('Mrot_rel'+ str(Mrot_rel))

    Mrot_abs = Mrot_rel.transposed() @ Mrot.transposed()       
    Mrot_abs = Mrot_abs.transposed()
    rotEuler =Mrot_abs.to_euler('XYZ')
    
    #writelog('rotEuler'+ str(rotEuler))
    #writelog('rotEuler[0] :'+ str(rotEuler[0]*360/(2*math.pi)))
    #writelog('rotEuler[1] :'+ str(rotEuler[1]*360/(2*math.pi)))
    #writelog('rotEuler[2] :'+ str(rotEuler[2]*360/(2*math.pi)))
        
    Vtrans_abs = Mworld @Vtrans_rel
    #writelog('Vtrans_abs :'+ str(Vtrans_abs))
       
    return Vtrans_abs, rotEuler

   

# ________________________________________________________________________________________________________________________
class objectSettings(PropertyGroup):

    traktor: StringProperty(
        name="choose object",
        default="Traktor"        
        )
    trailer: StringProperty(
        name="choose object",
        default="Trailer"        
        )    
    traktorpath: StringProperty(
        name="choose nurbspath",
        default="TraktorPath"        
        )
    trailerpath: StringProperty(
        name="choose nurbspath",
        default="TrailerPath"        
        )
        
    intSolverItems = (
            ('distance'  , 'Distance'    , 'Calculate path with constant distance to traktor (Tractrix)'),
            ('velocity'  , 'Velocity'    , 'Calculate path with constant velocity (Hundekurve)'         ),
            ('squint'    , 'Squint angle', 'Squint angle curve'                                         )
            )
    SolverMode: EnumProperty(
            items      = intSolverItems,
            name       = "Solver Mode",
            description="Determines how to calculate the trailer path",
            default    ='distance'
            )


bpy.utils.register_class(objectSettings)
bpy.types.Scene.tractrix = bpy.props.PointerProperty(type=objectSettings) 
  
classes = [Tractrix_PT_Panel, Traktrix_OT_Main, setobj2curve_OT_Main, 
           clearanimation_OT_Main]

def register():
    for cls in classes:
        bpy.utils.register_class(cls) 
    register_module(__name__)
    
    
    # Handlers
    #bpy.app.handlers.load_post.append(foobar)
    
def unregister():       
    for cls in classes:
        bpy.unutils.register_class(cls)
    unregister_module(__name__)

    # Handlers
    #bpy.app.handlers.load_post.remove(foobar)

#--- ### Main code    
if __name__ == '__main__':
    register()

 
