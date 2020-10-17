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
# Die Objekte werden unter Beruecksichtigung der Kurven im World-Space 
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
# - code cleaning !!!/ Variablen besser benennen (welche beziehen sich auf global bzw. lokal?)
# - Pruefung ob das Ergebnis des Trailers noch sinnvoll ist (Astand zum Traktor, delta Weg (-> proportional zu delta T)
# - Akutell arbeitet das Programm nur mit NURBSPATH. D.h. die Rotation des Splines wird nicht bruecksichtigt.
#   Traktor/ Trailer kann man über follow path constraint mit rotation animieren.
# - Laenge der Slave-Kurve automatisch anpassen
# - Import/ Export
# - Erbegnis "baken"
# - Abstand Abpruefen bei Berechnung und auf Fehler hinweisen
# - laesst sich mit 'writelog' noch nicht als AddOn starten, wegen initialisierungsproblem von filepath (ggf. writelog raus)
# - zurueckgelegte Strecke von Traktor und Trailer anzeigen
# - Fehler (Abtand soll/ist) anzeigen
'''

${workspace_loc:KUKA_OT_Export/src/curve_export.py}

Bevel add-on
bpy.data.curves[bpy.context.active_object.data.name].splines[0].bezier_points[0].co=(0,1,1)
'''  
#--- ### Header 
bl_info = { 
    "name": "Tractrix",
    "author": "Eric Wahl",
    "version": (1, 0, 1),
    "blender": (2, 90, 0),
    "api": 36147,
    "location": "View3D >Tools > Create",
    "category": "Add Curve",
    "description": "Calculate the path for Trailer Object following the Tractor Object.",
    "warning": "... under development.",
    "wiki_url": "http://...",
    "tracker_url": "http://..."
    }

#import pydevd 
#pydevd.settrace()  #<-- debugger stops at the next statement 
#import pydevd;pydevd.settrace() # notwendig weil breakpoints uebersprungen werden. warum auch immer


DEBUG = 1 #A debug flag - just for the convinience (Set to 0 in the final version)

#--- ### Import self coded functions and classes ----------------------------------------------------------------------------- 

if DEBUG == 1:                  # 1 = PyDev Debug
    from internal import*
    from operators import* 
else:                           # 0 = AddOn
    import bpy
    from .internal import*
    from .operators import* 
 
#--- ### Imports from blender python ------------------------------------------------------------------------------------------
# ExportHelper is a helper class, defines filename and
import bpy, os, sys
import bpy.utils
from bpy_extras.io_utils import ExportHelper
from bpy_extras.io_utils import ImportHelper
import time # um Zeitstempel im Logfile zu schreiben
     
#--- ### Imports python ------------------------------------------------------------------------------------------------------
from mathutils import Vector  
from mathutils import *
import mathutils
import math
import re  # zum sortieren de Objektliste
from symbol import except_clause
from copy import deepcopy # fuer OptimizeRotation

#--- ### Imports for custom properties and classes ------------------------------------------------------------------------------
from bpy.types import (
        Operator,
        Panel,
        PropertyGroup,
        )

from bpy.props import (
        #BoolProperty,
        #IntProperty,
        FloatProperty,
        EnumProperty,
        #CollectionProperty,
        StringProperty,
        PointerProperty
, IntProperty        #FloatVectorProperty, 
        )


class TRACTRIX_PT_Panel(Panel):
    writelog('_____________________________________________________________________________')
    writelog('TRACTRIX_PT_Panel....')
    
    """Creates a Panel in the Tool-panel under the <creates> tab of the 3D-View"""
    bl_idname = "VIEW3D_PT_layout"
    bl_label = "Tractrix" # heading of panel
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "Create"
    bl_options = {'DEFAULT_CLOSED'}

    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'}
    
    
    def __init__(self):
        writelog('TRACTRIX_PT_Panel - __init__')
        try: 
            frame_before = bpy.context.scene.tractrix.frame_before
            frame_now    = bpy.context.scene.frame_current
    
            objTraktor = bpy.data.objects[bpy.context.scene.tractrix.traktor] 
            objTrailer = bpy.data.objects[bpy.context.scene.tractrix.trailer]
        except:
            #bpy.utils.register_class(tractrixProperty)
            bpy.types.Scene.tractrix = PointerProperty(type=tractrixProperty) 
            pass         
        try:
            # tractrix.distance - Berechnung anhand der Traktor/ Trailer Objekte:
            bpy.context.scene.tractrix.distance = obj_distance(objTraktor, objTrailer)
            
            # velocity_traktor - Berechnung:
            bpy.context.scene.tractrix.velocity_traktor = obj_velocity(objTraktor)
            
            #tractrix.way_traktor - Berechnung 
            if frame_before != frame_now:
                bpy.context.scene.tractrix.way_traktor = bpy.context.scene.tractrix.way_traktor + obj_way(objTraktor, frame_now, frame_before)
    
            # velocity_trailer - Berechnung 
            bpy.context.scene.tractrix.velocity_trailer = obj_velocity(objTrailer)
            
            #tractrix.way_trailer - Berechnung 
            if frame_before != frame_now:
                bpy.context.scene.tractrix.way_trailer = bpy.context.scene.tractrix.way_trailer + obj_way(objTrailer, frame_now, frame_before)
            
                   
            #ToDo: tractrix.squint_angle - Berechnung 
        
        except:

            pass
        
        
        #if frame_before != frame_now:
        bpy.context.scene.tractrix.frame_before = deepcopy(frame_now)
        
        return
        

    def draw(self, context):
        writelog('TRACTRIX_PT_Panel - draw')
        ob = context.object
        layout = self.layout
        scene = context.scene
        
        split = layout.split()
        col = split.column()
        col.label(text="Schleppkurven:")
        
        col.operator("tractrix.clearanimation", text="1. clear Animations")
        #col.operator("tractrix_math.tractrix.clearanimation", text="1. clear Animations")  #tractrix_math.
        
        col.prop_search(scene.tractrix, "traktor", scene, "objects", icon = 'OBJECT_DATA', text = "Traktor")
        col.prop_search(scene.tractrix, "traktorpath", scene, "objects", icon = 'CURVE_BEZCURVE', text = "Traktor path")
        col.prop_search(scene.tractrix, "trailer", scene, "objects", icon = 'OBJECT_DATA', text = "Trailer")
        col.prop_search(scene.tractrix, "trailerpath", scene, "objects", icon = 'CURVE_BEZCURVE', text = "Trailer path")
        
        col.operator("tractrix.setobj2curve", text="2. set 2 path")
        col.prop(scene.tractrix, "SolverMode", icon = 'CON_ROTLIKE', text = "Sover")
        
        col.operator("tractrix.calculate", text="calculate path")        

        col.label(text="Result at frame:")
        #distance()
        #print("Erg.:  %3.5f" %scene.tractrix.distance)
        col.label(icon='DRIVER_DISTANCE',  text="distance:    %3.3f"     %scene.tractrix.distance)
        col.label(icon='TRACKING',         text="way traktor: %3.3f"     %scene.tractrix.way_traktor)
        col.label(icon='TRACKING',         text="way trailer: %3.3f"     %scene.tractrix.way_trailer)
        # todo: Weg zum frame i ....
        
        col.label(icon='CON_OBJECTSOLVER', text="v traktor:   %3.3f" %scene.tractrix.velocity_traktor)        
        col.label(icon='TRACKER',          text="v trailer:   %3.3f" %scene.tractrix.velocity_trailer)
        col.label(icon='DRIVER_ROTATIONAL_DIFFERENCE', text="squint angle: %3.3f" %scene.tractrix.squint_angle)

            
    #writelog('TRACTRIX_PT_Panel done')
    #writelog('_____________________________________________________________________________')


# ________________________________________________________________________________________________________________________

class tractrixProperty(PropertyGroup):

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
    distance: FloatProperty(
        name="distance Traktor-Trailer",
        default= 0.0        
        )   
    way_traktor: FloatProperty(
        name="velocity Traktor",
        default= 0.0        
        )  
    way_trailer: FloatProperty(
        name="velocity Trailer",
        default= 0.0        
        )     
    velocity_traktor: FloatProperty(
        name="velocity Traktor",
        default= 0.0        
        )  
    velocity_trailer: FloatProperty(
        name="velocity Trailer",
        default= 0.0        
        )  
    squint_angle: FloatProperty(
        name="squint angle Traktor-Trailer",
        default= 0.0        
        ) 
    
    frame_before: IntProperty(
        name="frame before now",
        default= 1 #bpy.context.scene.frame_current        
        )
    
    
bpy.utils.register_class(tractrixProperty)
#bpy.types.Scene.tractrix = PointerProperty(type=tractrixProperty) 


classes = [TRACTRIX_PT_Panel, TRACTRIX_OT_calculate, TRACTRIX_OT_setobj2curve, TRACTRIX_OT_clearanimation]

def register():
    for cls in classes:
        bpy.utils.register_class(cls) 
        
def unregister():       
    for cls in classes:
        bpy.utils.unregister_class(cls)

        
#--- ### Main code    
if __name__ == '__main__':
    register()

 
