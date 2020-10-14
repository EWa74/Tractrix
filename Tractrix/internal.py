# -*- coding: utf-8 -*-    
#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# coding Angabe in Zeilen 1 und 2 fuer Eclipse Luna/ Pydev 3.9 notwendig
# cp1252

import bpy, os, sys
from bpy_extras.io_utils import ExportHelper
from bpy_extras.io_utils import ImportHelper
import time # um Zeitstempel im Logfile zu schreiben
from mathutils import Vector
from mathutils import *
import mathutils
import math
from copy import deepcopy # fuer OptimizeRotation   
    
def writelog(text=''):
    FilenameLog = bpy.data.filepath
    FilenameLog = FilenameLog.replace(".blend", '.log')
    fout = open(FilenameLog, 'a')
    localtime = time.asctime( time.localtime(time.time()) )
    fout.write(localtime + " : " + str(text) + '\n')
    fout.close();
    
    
def frame_to_time(frame_number):
    fps = bpy.context.scene.render.fps
    raw_time = (frame_number - 1) / fps
    return round(raw_time, 3)

def obj_distance(obj1, obj2):
    # Abstand zweier Objekte zum aktuellem Zeitpunkt
    
    A = obj1.location.x - obj2.location.x
    B = obj1.location.y - obj2.location.y
    C = obj1.location.z - obj2.location.z
        
    distance = math.sqrt(A*A+B*B+C*C)
    
    return distance

def obj_velocity(obj):
    # Akutelle Geschwindigkeit bezogen auf vorherriges frame.

    frame =  bpy.context.scene.frame_current
        
    current_xyz = obj.location
    fcurve = obj.animation_data.action.fcurves

    x = fcurve[0].evaluate(frame-1)
    y = fcurve[1].evaluate(frame-1)
    z = fcurve[2].evaluate(frame-1)

    delta_way  = (current_xyz - Vector((x, y, z))).length
    delta_time = frame_to_time(frame)-frame_to_time(frame-1)
    
    velocity = delta_way /delta_time
    
    return velocity    

def obj_way(obj, frm_stop, frm_start):
    # Addiere den Weg von frm_start bis frm_stop
    way = 0
    # Anfangswert:
    fcurve = obj.animation_data.action.fcurves
    x = fcurve[0].evaluate(frm_start)
    y = fcurve[1].evaluate(frm_start)
    z = fcurve[2].evaluate(frm_start)
    
    way_vec = Vector((x, y, z))
                
    # a) Zeit vorwaerts:    
    if (frm_stop-frm_start >0):
        
        for n in range(frm_start, frm_stop+1):
            x = fcurve[0].evaluate(n)
            y = fcurve[1].evaluate(n)
            z = fcurve[2].evaluate(n)

            way  = way + (way_vec - Vector((x, y, z))).length
            
            way_vec = Vector((x, y, z))
        
    # a) Zeit rueckwaerts:  
    if (frm_stop-frm_start <0):
          
        for n in range(frm_start, frm_stop-1,-1):
            x = fcurve[0].evaluate(n)
            y = fcurve[1].evaluate(n)
            z = fcurve[2].evaluate(n)

            way  = way - (way_vec - Vector((x, y, z))).length
            
            way_vec = Vector((x, y, z)) 
    
    return way 

def ReadCurve(objPath):
    curObj = bpy.data.curves[objPath.data.name]
    int_Curve = len(bpy.data.curves[objPath.data.name].splines[0].points)
    datPath = createMatrix(int_Curve,3)
    
    for int_PCurve in range(0,int_Curve,1):       
        
        # mit 'get_absolute' werden die GLOBALEN Punkte verwendet:
        datPath[int_PCurve][0:3] = get_absolute(curObj.splines[0].points[int_PCurve].co, (0,0,0), objPath.location, objPath.rotation_euler)
        # in der alten Version wurden nur die LOKALEN Punkte (d.h. bezogen auf den Origin) verwendet:
        #datPath[int_PCurve][0:3] = [curObj.splines[0].points[int_PCurve].co.x, curObj.splines[0].points[int_PCurve].co.y, curObj.splines[0].points[int_PCurve].co.z]
 
    return int_Curve, datPath

def WriteCurveTrailer(int_Curve, Trailer):
    
    #bpy.data.objects[Trailer].data.splines 
    objTrailerPath = bpy.data.objects[bpy.context.scene.tractrix.trailerpath]
    objTrailer = bpy.data.objects[bpy.context.scene.tractrix.trailer] 
    curTrailer = bpy.data.curves[objTrailerPath.data.name]    
    #int_Curve=len(curTrailer.splines[0].points)
    for int_PCurve in range(0,int_Curve,1):
        #[curTrailer.splines[0].points[int_PCurve].co.x, curTrailer.splines[0].points[int_PCurve].co.y, curTrailer.splines[0].points[int_PCurve].co.z] = Trailer[int_PCurve][0]
        ([curTrailer.splines[0].points[int_PCurve].co.x, 
          curTrailer.splines[0].points[int_PCurve].co.y, 
          curTrailer.splines[0].points[int_PCurve].co.z]), \
          rot_spline_element = get_relative(
              Trailer[int_PCurve][0], 
              (0,0,0), 
              objTrailerPath.location, 
              objTrailerPath.rotation_euler)
        
        # ToDo: rot_spline_element (findet bei bei Nurbspath keine Anwendung)      

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
          
    scene = bpy.context.scene
    #fps = scene.render.fps
    #fps_base = scene.render.fps_base
     
    raw_time=[]
    frame_number=[]
    
    bpy.context.view_layer.objects.active = obj
    
    obj.select_set(True)
    bpy.ops.anim.keyframe_clear_v3d() #Remove all keyframe animation for selected objects

    ob = bpy.context.active_object
    ob.rotation_mode = 'QUATERNION' #'XYZ'
    
    # Initialisierung um v zu berechnen:
    location_old = deepcopy(ob.location)
    T_old = deepcopy(time_to_frame(TIMEPTS[0]))
    
    #QuaternionList = OptimizeRotationQuaternion(TargetObjList, TIMEPTSCount)
    for n in range(0,int_Curve,1):
        
        # Trailer[int_PCurve][0]
        writelog(n)
        bpy.data.scenes['Scene'].frame_set(time_to_frame(TIMEPTS[n])) 

        ob.location, ob.rotation_euler = get_absolute(Vector((cur.splines[0].points[n].co.x,cur.splines[0].points[n].co.y,cur.splines[0].points[n].co.z)), (0,0,0),objPath.location, objPath.rotation_euler)
        
        #ob.location = [cur.splines[0].points[n].co.x, cur.splines[0].points[n].co.y, cur.splines[0].points[n].co.z]
        
        #ob.location = bpy.data.objects[TargetObjList[n]].location
                
        # todo: ob.rotation_quaternion = bpy.data.objects[TargetObjList[n]].rotation_euler.to_quaternion()
           
        ob.keyframe_insert(data_path="location", index=-1)

        # file:///F:/EWa_WWW_Tutorials/Scripting/blender_python_reference_2_68_5/bpy.types.bpy_struct.html#bpy.types.bpy_struct.keyframe_insert
        
        # todo: ob.keyframe_insert(data_path="rotation_quaternion", index=-1)
        
        #ob.keyframe_insert(data_path="rotation_euler", index=-1)
        
        #objTraktor_keyframes, objTraktor_keyframesCount =RfS_TIMEPTS(objTraktor)
        
       
    bpy.context.area.type = original_type 
    writelog(n)
    
def get_relative(dataPATHPTS_Loc, dataPATHPTS_Rot, BASEPos_Koord, BASEPos_Angle):
    # dataPATHPTS_Loc/Rot [rad]: absolute
    # BASEPos_Koord/Angle [rad]: absolute
    # Aufruf von: Diese Funktion wird nur bei Refresh und Import aufgerufen.
    # Wiedergabe von LOC/Rot bezogen auf Base
    
    # World2Local - OK (absolute -> relative)
    
    # Gegeben: Mtrans, Mrot = Base / Vtrans_abs, Mrot_abs
    # Ges:  Mrot_rel, Vtrans_rel
    #
    # Mworld  / Mworld_rel / Mworld_abs mit world = trans * rot
    # Mtrans  / Mtrans_rel / Mtrans_abs
    # Mrot    / Mrot_rel   / Mrot_abs
    #
    # dataPATHPTS_Loc = Global --> PATHPTS_Koord bezogen auf Base 
    # dataPATHPTS_Rot = Global --> PATHPTS_Angle bezogen auf Base
    
    writelog('_____________________________________________________________________________')
    writelog('Funktion: get_relativeX - lokale Koordinaten bezogen auf Base!')
            
    Mtrans     = mathutils.Matrix.Translation(BASEPos_Koord) 
    Vtrans_abs = dataPATHPTS_Loc                              #global 
    writelog('Vtrans_abs'+ str(Vtrans_abs))  # neuer Bezugspunkt
    
    #--------------------------------------------------------------------------
    MrotX = mathutils.Matrix.Rotation(BASEPos_Angle[0], 3, 'X') # Global
    MrotY = mathutils.Matrix.Rotation(BASEPos_Angle[1], 3, 'Y')
    MrotZ = mathutils.Matrix.Rotation(BASEPos_Angle[2], 3, 'Z')
    Mrot = MrotZ @ MrotY @ MrotX
    writelog('Mrot :'+ str(Mrot))
    
    Mworld_rel = Mtrans @ Mrot.to_4x4()
    
    Mrot_absX = mathutils.Matrix.Rotation(dataPATHPTS_Rot[0], 3, 'X') # Global
    Mrot_absY = mathutils.Matrix.Rotation(dataPATHPTS_Rot[1], 3, 'Y')
    Mrot_absZ = mathutils.Matrix.Rotation(dataPATHPTS_Rot[2], 3, 'Z')  
    Mrot_abs = Mrot_absZ @ Mrot_absY @ Mrot_absX
    writelog('Mrot_abs :'+ str(Mrot_abs))
    #--------------------------------------------------------------------------
     
    #PATHPTS_Koord = matrix_world.inverted() *point_local    # transpose fuehrt zu einem andren Ergebnis?!
    #Vtrans_rel   = Mworld_rel.inverted() *Vtrans_abs
    Vtrans_rel   = Mworld_rel.inverted() @Vector((Vtrans_abs))  
    PATHPTS_Koord = Vtrans_rel
    
    writelog('PATHPTS_Koord : '+ str(PATHPTS_Koord))           # neuer Bezugspunkt
    
    Mrot_rel = Mrot.inverted()  @ Mrot_abs 
    writelog('Mrot_rel'+ str(Mrot_rel))
    
    newR = Mrot_rel.to_euler('XYZ')
    
    writelog('newR'+ str(newR))    
    writelog('newR[0] :'+ str(newR[0]*360/(2*math.pi)))
    writelog('newR[1] :'+ str(newR[1]*360/(2*math.pi)))
    writelog('newR[2] :'+ str(newR[2]*360/(2*math.pi)))
    
            
    Vorz1 = +1#-1 # +C = X
    Vorz2 = +1#-1 # -B = Y
    Vorz3 = +1#-1 # -A = Z    
    PATHPTS_Angle = (Vorz1* newR[0], Vorz2*newR[1], Vorz3*newR[2]) # [rad]     
    
    writelog('PATHPTS_Koord : ' + str(PATHPTS_Koord))
    writelog('PATHPTS_Angle: '+'C X {0:.3f}'.format(PATHPTS_Angle[0])+' B Y {0:.3f}'.format(PATHPTS_Angle[1])+' A Z {0:.3f}'.format(PATHPTS_Angle[2]))
    
    writelog('get_relative done')
    writelog('_____________________________________________________________________________')
    return PATHPTS_Koord, PATHPTS_Angle 

def get_absolute(Obj_Koord, Obj_Angle, BASEPos_Koord, BASEPos_Angle): #objBase
    '''
    BASEPos_Koord = objBase.location
    BASEPos_Angle = objBase.rotation_euler
    '''
    
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
    
    #matrix_world =bpy.data.objects[objBase.name].matrix_world
    
    #mat_trans = mathutils.Matrix.Translation(BASEPos_Koord)
    #mat_rot = mathutils.Matrix.Rotation(radians(0), 4, 'X')
    #matrix_world = mat_trans @ mat_rot
    
    '''
    matrix_world[0] = Vector((1.0, 0.0, 0.0, BASEPos_Koord.x))
    matrix_world[1] = Vector((0.0, 1.0, 0.0, BASEPos_Koord.y))
    matrix_world[2] = Vector((0.0, 0.0, 1.0, BASEPos_Koord.z))
    matrix_world[3] = Vector((0.0, 0.0, 0.0, 1.0))
    '''
    
    #matrix_world =bpy.data.objects[objBase.name].matrix_world
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
    
    writelog('rotEuler'+ str(rotEuler))
    writelog('rotEuler[0] :'+ str(rotEuler[0]*360/(2*math.pi)))
    writelog('rotEuler[1] :'+ str(rotEuler[1]*360/(2*math.pi)))
    writelog('rotEuler[2] :'+ str(rotEuler[2]*360/(2*math.pi)))
        
    Vtrans_abs = Mworld @Vtrans_rel
    writelog('Vtrans_abs :'+ str(Vtrans_abs))
       
    return Vtrans_abs, rotEuler

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
        
        Mx[T1][0], My[T1][0], Mz[T1][0] = [datTraktor[int_PCurve][0][0], datTraktor[int_PCurve][0][1], datTraktor[int_PCurve][0][2]]
        #original: Mx[T1][0], My[T1][0], Mz[T1][0] = [datTraktor[int_PCurve][0], datTraktor[int_PCurve][1], datTraktor[int_PCurve][2]]
        
        Mx[T2][0], My[T2][0], Mz[T2][0] = [datTraktor[int_PCurve+1][0][0], datTraktor[int_PCurve+1][0][1], datTraktor[int_PCurve+1][0][2]]
        
        nn= math.sqrt(math.pow((Sx[T1][0] - Mx[T1][0]),2) + math.pow((Sy[T1][0] - My[T1][0]),2) + math.pow((Sz[T1][0] - Mz[T1][0]),2))
            
        n[1] = (Sx[T1][0] - Mx[T1][0])/nn
        n[2] = (Sy[T1][0] - My[T1][0])/nn
        n[3] = (Sz[T1][0] - Mz[T1][0])/nn
        
        Term = ((Mx[T2][0] -Mx[T1][0]) *n[1]+
                (My[T2][0] -My[T1][0]) *n[2]+
                (Mz[T2][0] -Mz[T1][0]) *n[3])
        
        #Gravity =  0* Sz[T1][0] - 0.1 * math.pow((T2-T1),2) 
        #Abstand = math.pow(math.pow((datTraktor[0][0]-Sx[T1][0]),2)+math.pow((datTraktor[0][1]-Sy[T1][0]),2)+math.pow((datTraktor[0][2]-Sz[T1][0]),2), 0.5)
        AbstandT1 = math.pow(math.pow((datTraktor[int_PCurve][0][0]-Sx[T1][0]),2)+math.pow((datTraktor[int_PCurve][0][1]-Sy[T1][0]),2)+math.pow((datTraktor[int_PCurve][0][2]-Sz[T1][0]),2), 0.5)
        
        Sx[T2][0] = Sx[T1][0] + Term * n[1]
        Sy[T2][0] = Sy[T1][0] + Term * n[2]
        Sz[T2][0] = Sz[T1][0] + Term * n[3]  #+ (Gravity)
        
        datTrailer[int_PCurve+1][0] = Sx[T2][0], Sy[T2][0], Sz[T2][0]
                
        Sx[T1][0] = deepcopy(Sx[T2][0])
        Sy[T1][0] = deepcopy(Sy[T2][0])
        Sz[T1][0] = deepcopy(Sz[T2][0])
        
            
    return datTrailer 

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
    