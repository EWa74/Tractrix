# -*- coding: utf-8 -*-    
#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# coding Angabe in Zeilen 1 und 2 fuer Eclipse Luna/ Pydev 3.9 notwendig
# cp1252

DEBUG = 1 #A debug flag - just for the convinience (Set to 0 in the final version)

if DEBUG == 1:                  # 1 = PyDev Debug 
    import bpy
    from internal import*
else:                           # 0 = AddOn
    from .internal import*
   

import bpy
from mathutils import Vector
from bpy.types import (
        Operator,
        #Panel,
        #PropertyGroup,
        )

import bpy.utils


    
class TRACTRIX_OT_setobj2curve (Operator):
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
    writelog('- - TRACTRIX_OT_setobj2curve done- - - - - - -') 

class TRACTRIX_OT_clearanimation (Operator): 
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
        
        

class TRACTRIX_OT_calculate (Operator):    
    bl_idname = "tractrix.calculate"
    bl_label = "TRACTRIX_OT_calculate (TB)" #Toolbar - Label
    bl_description = "Calculate Tractrix for Trailer Object from Tractor Object." 
    bl_options = {'REGISTER', 'UNDO'} 

    def execute(self, context):  
        
        objTraktorPath = bpy.data.objects[bpy.context.scene.tractrix.traktorpath] 
        objTraktor = bpy.data.objects[bpy.context.scene.tractrix.traktor] 
        objTrailerPath = bpy.data.objects[bpy.context.scene.tractrix.trailerpath]
        objTrailer = bpy.data.objects[bpy.context.scene.tractrix.trailer]
        curTraktor = bpy.data.curves[objTraktorPath.data.name]
        curTrailer = bpy.data.curves[objTrailerPath.data.name]     
            
        int_Curve, datTraktorCurve = read_curve(objTraktorPath)  
        
        #datTrailerStart = [curTrailer.splines[0].points[0].co.x, curTrailer.splines[0].points[0].co.y, curTrailer.splines[0].points[0].co.z]
        datTrailerStart, datTrailerStartRot = get_absolute(Vector((curTrailer.splines[0].points[0].co.x,curTrailer.splines[0].points[0].co.y,curTrailer.splines[0].points[0].co.z)), (0,0,0),objTrailerPath.location, objTrailerPath.rotation_euler)
        
        
        # ToDo: datTraktorCurve muss noch mit getabsoulute umgerechnet werden...
        datTrailerCurve= tractrix_distance(datTraktorCurve, datTrailerStart)
        
        write_curve(int_Curve, datTrailerCurve)
        
        TIMEPTS = []
        for int_PCurve in range(0,int_Curve,1):
            TIMEPTS = TIMEPTS + [int_PCurve/12]
        
        set_keyframes(objTraktor, curTraktor, objTraktorPath, int_Curve, TIMEPTS)
        set_keyframes(objTrailer, curTrailer, objTrailerPath, int_Curve, TIMEPTS)
        bpy.data.scenes['Scene'].frame_set(1)
        
        
        return {'FINISHED'} 
    writelog('- - TRACTRIX_OT_calculate done- - - - - - -')
    
    