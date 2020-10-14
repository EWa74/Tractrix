# -*- coding: utf-8 -*-    
#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# coding Angabe in Zeilen 1 und 2 fuer Eclipse Luna/ Pydev 3.9 notwendig
# cp1252

import bpy
from mathutils import Vector
from bpy.types import (
        Operator,
        #Panel,
        #PropertyGroup,
        )

import bpy.utils

from internal import*
    
class setobj2curve_OT_Main (Operator):
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
        objTraktor.location, objTraktor.rotation_euler = get_absolute(Vector(datTraktorCurve), (0,0,0), objTraktorPath.location, objTraktorPath.rotation_euler)
        
        
        objTrailerPath = bpy.data.objects[bpy.context.scene.tractrix.trailerpath]
        objTrailer = bpy.data.objects[bpy.context.scene.tractrix.trailer] 
        curTrailer = bpy.data.curves[objTrailerPath.data.name]    
        
        datTrailerCurve = [curTrailer.splines[0].points[0].co.x, curTrailer.splines[0].points[0].co.y, curTrailer.splines[0].points[0].co.z]
        objTrailer.location,objTrailer.rotation_euler = get_absolute(Vector(datTrailerCurve), (0,0,0), objTrailerPath.location,objTrailerPath.rotation_euler)

        return {'FINISHED'} 
    writelog('- - setobj2curve_OT_Main done- - - - - - -') 

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
        
        

class Traktrix_OT_Main (Operator):    
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
        
        #datTrailerStart = [curTrailer.splines[0].points[0].co.x, curTrailer.splines[0].points[0].co.y, curTrailer.splines[0].points[0].co.z]
        datTrailerStart, datTrailerStartRot = get_absolute(Vector((curTrailer.splines[0].points[0].co.x,curTrailer.splines[0].points[0].co.y,curTrailer.splines[0].points[0].co.z)), (0,0,0),objTrailerPath.location, objTrailerPath.rotation_euler)
        
        
        # ToDo: datTraktorCurve muss noch mit getabsoulute umgerechnet werden...
        datTrailerCurve= Traktrix3D(datTraktorCurve, datTrailerStart)
        
        WriteCurveTrailer(int_Curve, datTrailerCurve)
        
        TIMEPTS = []
        for int_PCurve in range(0,int_Curve,1):
            TIMEPTS = TIMEPTS + [int_PCurve/12]
        
        SetKeyFrames(objTraktor, curTraktor, objTraktorPath, int_Curve, TIMEPTS)
        SetKeyFrames(objTrailer, curTrailer, objTrailerPath, int_Curve, TIMEPTS)
        bpy.data.scenes['Scene'].frame_set(1)
        
        
        return {'FINISHED'} 
    writelog('- - Tractrix_OT_Main done- - - - - - -')
    
    
    
operators = [setobj2curve_OT_Main, clearanimation_OT_Main, Traktrix_OT_Main] #tractrix_math.operators 


def register():
    for cls in operators:
        bpy.utils.register_class(cls) 

    
def unregister():       
    for cls in operators:
        bpy.utils.unregister_class(cls)


      