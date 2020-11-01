# -*- coding: utf-8 -*-    
#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# coding Angabe in Zeilen 1 und 2 fuer Eclipse Luna/ Pydev 3.9 notwendig
# cp1252

DEBUG_FLAG = 1 #A debug flag - just for the convinience (Set to 0 in the final version)

if DEBUG_FLAG == 1:                  # 1 = PyDev Debug 
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
    bl_idname      = "tractrix.setobj2curve"
    bl_label       = "set objects to path" 
    bl_description = "set traktor and trailer objects to cures" 
    bl_options     = {'REGISTER', 'UNDO'} 
    
    def execute(self, context):
        bpy.data.scenes['Scene'].frame_current = bpy.data.scenes['Scene'].frame_start
        
        objTraktorPath = bpy.context.scene.tractrix.traktorpath  
        objTraktor     = bpy.context.scene.tractrix.traktor        
        curTraktor     = bpy.data.curves[objTraktorPath.data.name]
        
        datTraktorCurve = curTraktor.splines[0].points[0].co.xyz
        objTraktor.location, objTraktor.rotation_euler = get_absolute(datTraktorCurve, (0,0,0), objTraktorPath.location, objTraktorPath.rotation_euler)
        
        objTrailerPath = bpy.context.scene.tractrix.trailerpath
        objTrailer     = bpy.context.scene.tractrix.trailer 
        curTrailer     = bpy.data.curves[objTrailerPath.data.name]    
        
        datTrailerCurve = curTrailer.splines[0].points[0].co.xyz
        objTrailer.location,objTrailer.rotation_euler = get_absolute(datTrailerCurve, (0,0,0), objTrailerPath.location,objTrailerPath.rotation_euler)
        
        writelog('- - TRACTRIX_OT_setobj2curve done- - - - - - -')
        return {'FINISHED'} 
     

class TRACTRIX_OT_clearanimation (Operator): 
    bl_idname      = "tractrix.clearanimation"
    bl_label       = "clear animations" 
    bl_description = "clear animations of traktor and trailer" 
    bl_options     = {'REGISTER', 'UNDO'} 
    
    def execute(self, context):

        objTraktor     = bpy.context.scene.tractrix.traktor 
        objTrailer = bpy.context.scene.tractrix.trailer 
        
        clear_keyframes(objTraktor)
        clear_keyframes(objTrailer)
        
        bpy.context.scene.tractrix.way_traktor = 0
        bpy.context.scene.tractrix.way_trailer = 0
        
        writelog('- - TRACTRIX_OT_clearanimation done- - - - - - -')  
        return {'FINISHED'} 
        

class TRACTRIX_OT_calculate (Operator):    
    bl_idname      = "tractrix.calculate"
    bl_label       = "TRACTRIX_OT_calculate (TB)" #Toolbar - Label
    bl_description = "Calculate Tractrix for Trailer Object from Tractor Object." 
    bl_options     = {'REGISTER', 'UNDO'} 

    def execute(self, context):  
        
        objTraktorPath = bpy.context.scene.tractrix.traktorpath 
        objTraktor     = bpy.context.scene.tractrix.traktor 
        
        objTrailerPath = bpy.context.scene.tractrix.trailerpath
        objTrailer     = bpy.context.scene.tractrix.trailer
        
        curTraktor     = bpy.data.curves[objTraktorPath.data.name]
        curTrailer     = bpy.data.curves[objTrailerPath.data.name]     
        
        solver_mode    = bpy.context.scene.tractrix.solver_mode
        velocity_fac    = bpy.context.scene.tractrix.velocity_factor
            
        int_curve, datTraktorCurve = read_global_splines(objTraktorPath)  
        
        datTrailerStart = get_absolute(
            Vector((curTrailer.splines[0].points[0].co.xyz)), 
                    (0,0,0),
                    objTrailerPath.location, 
                    objTrailerPath.rotation_euler
                    )
        if solver_mode == 'distance':
            datTrailerCurve = pursuit_curve_solver_distance(datTraktorCurve, datTrailerStart)
        elif solver_mode == 'velocity':
            datTrailerCurve = pursuit_curve_solver_velocity(datTraktorCurve, datTrailerStart, velocity_fac)
        elif solver_mode == 'squint':
            datTrailerCurve = pursuit_curve_solver_squint(datTraktorCurve, datTrailerStart)
        else:
            print('solve mode not found ..............................................')
            
        write_global_splines(int_curve, datTrailerCurve, objTrailerPath)
        
        TIMEPTS = []
        for int_PCurve in range(0,int_curve,1):
            TIMEPTS = TIMEPTS + [int_PCurve/12]
        
        set_keyframes(objTraktor, curTraktor, objTraktorPath, int_curve, TIMEPTS)
        set_keyframes(objTrailer, curTrailer, objTrailerPath, int_curve, TIMEPTS)
        bpy.data.scenes['Scene'].frame_set(1)
        
        writelog('- - TRACTRIX_OT_calculate done- - - - - - -')
        return {'FINISHED'} 
    
    
    