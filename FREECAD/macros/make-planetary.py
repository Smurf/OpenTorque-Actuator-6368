# -*- coding: utf-8 -*-

# Macro Begin: 
import FreeCAD
import InvoluteGearFeature
import PartDesignGui
import Part
import Part,PartGui
from math import *
from FreeCAD import Base
import Draft

def makeGear(name, teeth, pressureAngle=20, module=1, helixAngle=10,  height=10, bore=0, clearance=0.2, position = Base.Vector(0.00,0.00,0.00), rotation =0, extrude=False, chamfer=False, bearing=False, bearing_diameter=10, bearing_height=5):

    #Gui.activateWorkbench("PartDesignWorkbench")
    involute = InvoluteGearFeature.makeInvoluteGear(name+"_involute")
    involute.NumberOfTeeth = teeth
    involute.ExternalGear = True
    involute.HighPrecision = True
    involute.PressureAngle = pressureAngle
    involute.Modules = module - float(clearance)/float(teeth)
    
    involuteRadius = module * teeth /2.0

    doc = App.ActiveDocument
        
    if extrude:
        ext_name=name
        if chamfer: #rename gear body to end up with final name after chamfering
            ext_name=name+"_ext"
        else:
            if bore:
                ext_name = name+"_trimmed"

        if helixAngle!=0:
            helix = doc.addObject("Part::Helix",name+"_helix")
            helix.Pitch = pi * 2.0 * involuteRadius * tan(pi*(90-abs(helixAngle))/180.0)
            helix.Height = height
            helix.Radius=involuteRadius
            helix.Angle=0.00
            if helixAngle>0:
                helix.LocalCoord=0
            else:
                helix.LocalCoord=1
            helix.Style=1
            helix.Placement=Base.Placement(Base.Vector(0.00,0.00,0.00),Base.Rotation(0.00,0.00,0.00,1.00))
            helix.Label=name+'_helix'
            App.ActiveDocument.recompute()  
            sweep = doc.addObject('Part::Sweep',ext_name)
            sweep.Sections=doc.getObject(name+'_involute')
            sweep.Spine=(doc.getObject(name+'_helix'),[])
            sweep.Solid=True
            sweep.Frenet=True       
            #sweep.Placement=Base.Placement(position, Base.Rotation(Base.Vector(0.0,0.0,1.0),rotation))
        else:
            f = doc.addObject('Part::Extrusion', ext_name)
            f = doc.getObject(ext_name)
            f.Base = doc.getObject(name+'_involute')
            f.DirMode = "Normal"
            f.DirLink = None
            f.LengthFwd = height
            f.LengthRev = 0.000000000000000
            f.Solid = True
            f.Reversed = False
            f.Symmetric = False
            f.TaperAngle = 0.000000000000000
            f.TaperAngleRev = 0.000000000000000
        
        App.ActiveDocument.recompute()      
        Gui.ActiveDocument.getObject(name+'_involute').Visibility=False

        if chamfer:
            pl=FreeCAD.Placement()
            pl.Rotation.Q=(0,0,0,1)
            pl.Base=FreeCAD.Vector(0,0,0)
            circle1 = Draft.makeCircle(radius=involuteRadius-1.5*module,placement=pl,face=False,support=None)
            pl.Base=FreeCAD.Vector(0,0,1.5*module)
            circle2 = Draft.makeCircle(radius=involuteRadius+1.5*module,placement=pl,face=False,support=None)
            pl.Base=FreeCAD.Vector(0,0,height-1.5*module)
            circle3 = Draft.makeCircle(radius=involuteRadius+1.5*module,placement=pl,face=False,support=None)
            pl.Base=FreeCAD.Vector(0,0,height)
            circle4 = Draft.makeCircle(radius=involuteRadius-1.5*module,placement=pl,face=False,support=None)

            gear_body = doc.addObject('Part::Loft',name+'body')
            gear_body.Sections=[circle1, circle2, circle3, circle4 ]
            gear_body.Solid=True
            gear_body.Ruled=True
            gear_body.Closed=False
            body_name=name+'_trimmed'
            if bore==0:
                body_name=name
            intersect = doc.addObject("Part::Common",body_name)
            intersect.Base = doc.getObject(ext_name)
            intersect.Tool = doc.getObject(name+'body')
        if bore>0:
            cylinder = doc.addObject("Part::Cylinder",name+"_bore")
            cylinder.Label = name+"_bore"
            cylinder.Radius = (bore+clearance)/2.0
            cylinder.Height = height+0.1
            #cylinder.Placement=Base.Placement(position, Base.Rotation(Base.Vector(0.0,0.0,1.0),rotation))
            
            cut = doc.addObject("Part::Cut",name)
            cut.Base = doc.getObject(name+"_trimmed")
            cut.Tool = doc.getObject(name+"_bore")

        #create bearing
        if bearing:
            cylinder = doc.addObject("Part::Cylinder",name+"_bearing")
            cylinder.Label = name+"_bearing"
            cylinder.Radius = (bearing_diameter+clearance)/2.0
            cylinder.Height = bearing_height+0.1
            
            #Place up on z
            cylinder.Placement=Base.Placement(
                    Base.Vector(position.x,position.y,(height/2)-(bearing_height/2)), 
                    Base.Rotation(Base.Vector(0.0,0.0,1.0),
                    rotation))
            
            cut = doc.addObject("Part::Cut",name)
            cut.Base = doc.getObject(name)
            cut.Tool = doc.getObject(name+"_bearing")

 
        doc.getObject(name).Placement=Base.Placement(position, Base.Rotation(Base.Vector(0.0,0.0,1.0),rotation))
    else:
        involute.Placement=Base.Placement(position, Base.Rotation(Base.Vector(0.0,0.0,1.0),rotation))
    App.ActiveDocument.recompute()


def makeRingGear(name, teeth, pressureAngle=20, module=1, helixAngle=10,  height=10, bore=0, clearance=0.2, external = True, position = Base.Vector(0.00,0.00,0.00), rotation =0, extrude=False, chamfer=False):

    #Gui.activateWorkbench("PartDesignWorkbench")
    involute = InvoluteGearFeature.makeInvoluteGear(name+"_involute")
    involute.NumberOfTeeth = teeth
    involute.ExternalGear = False
    involute.HighPrecision = True
    involute.PressureAngle = pressureAngle

    involute.Modules = module + float(clearance)/float(teeth)
    
    involuteRadius = module * teeth /2.0

    doc = App.ActiveDocument
    
    if extrude:
        ext_name=name+"_ext"

        if helixAngle!=0:
            helix = doc.addObject("Part::Helix",name+"_helix")
            helix.Pitch = pi * 2.0 * involuteRadius * tan(pi*(90-abs(helixAngle))/180.0)
            helix.Height = height
            helix.Radius=involuteRadius
            helix.Angle=0.00
            if helixAngle>0:
                helix.LocalCoord=0
            else:
                helix.LocalCoord=1
            helix.Style=1
            helix.Placement=Base.Placement(Base.Vector(0.00,0.00,0.00),Base.Rotation(0.00,0.00,0.00,1.00))
            helix.Label=name+'_helix'
            App.ActiveDocument.recompute()  
            sweep = doc.addObject('Part::Sweep',ext_name)
            sweep.Sections=doc.getObject(name+'_involute')
            sweep.Spine=(doc.getObject(name+'_helix'),[])
            sweep.Solid=True
            sweep.Frenet=True       
            #sweep.Placement=Base.Placement(position, Base.Rotation(Base.Vector(0.0,0.0,1.0),rotation))
        else:
            f = doc.addObject('Part::Extrusion', ext_name)
            f = doc.getObject(ext_name)
            f.Base = doc.getObject(name+'_involute')
            f.DirMode = "Normal"
            f.DirLink = None
            f.LengthFwd = height
            f.LengthRev = 0.000000000000000
            f.Solid = True
            f.Reversed = False
            f.Symmetric = False
            f.TaperAngle = 0.000000000000000
            f.TaperAngleRev = 0.000000000000000
            
        App.ActiveDocument.recompute()      
        Gui.ActiveDocument.getObject(name+'_involute').Visibility=False

        if chamfer:
            pl=FreeCAD.Placement()
            pl.Rotation.Q=(0,0,0,1)
            pl.Base=FreeCAD.Vector(0,0,0)
            circle1 = Draft.makeCircle(radius=involuteRadius+1.5*module,placement=pl,face=False,support=None)
            pl.Base=FreeCAD.Vector(0,0,1.5*module)
            circle2 = Draft.makeCircle(radius=involuteRadius-1.5*module,placement=pl,face=False,support=None)
            pl.Base=FreeCAD.Vector(0,0,height-1.5*module)
            circle3 = Draft.makeCircle(radius=involuteRadius-1.5*module,placement=pl,face=False,support=None)
            pl.Base=FreeCAD.Vector(0,0,height)
            circle4 = Draft.makeCircle(radius=involuteRadius+1.5*module,placement=pl,face=False,support=None)

            gear_body = doc.addObject('Part::Loft',name+'body')
            gear_body.Sections=[circle1, circle2, circle3, circle4 ]
            gear_body.Solid=True
            gear_body.Ruled=True
            gear_body.Closed=False

            cylinder = doc.addObject("Part::Cylinder",name+"_exthousing")
            cylinder.Label = name+"_exthousing"
            cylinder.Radius = involuteRadius+10
            cylinder.Height = height - 0.1
            
            body = doc.addObject("Part::Cut",name+'_trimmed')
            body.Base = doc.getObject(name+"_exthousing")
            body.Tool = doc.getObject(name+'body')
        else:
            cylinder = doc.addObject("Part::Cylinder",name+"_trimmed")
            cylinder.Label = name+"_exthousing"
            cylinder.Radius = involuteRadius+10
            cylinder.Height = height - 0.1


        cut = doc.addObject("Part::Cut",name)
        cut.Base = doc.getObject(name+"_trimmed")
        cut.Tool = doc.getObject(ext_name)
        
        doc.getObject(name).Placement=Base.Placement(position, Base.Rotation(Base.Vector(0.0,0.0,1.0),rotation))
    else:
        involute.Placement=Base.Placement(position, Base.Rotation(Base.Vector(0.0,0.0,1.0),rotation))
    App.ActiveDocument.recompute()

def makePlanetary(name, 
                    module=1.0, 
                    sun_teeth = 20, 
                    planet_teeth = 20, 
                    z_off=0, 
                    helix=10, 
                    height=10, 
                    clearance = 0.0, 
                    extrude=True, 
                    bore=0, 
                    planets=1,
                    planet_bearings = False,
                    planet_bore = 0,
                    planet_bearing_diameter = 10,
                    planet_bearing_height = 5):

    ring_teeth = 2*planet_teeth+sun_teeth
    mesh_distance = (sun_teeth+planet_teeth)*module/2.0
    
    planet_rotation = (1-(planet_teeth % 2))*180.0/planet_teeth
    ring_rotation = 180.0/ring_teeth + planet_rotation*planet_teeth/ring_teeth
    
    makeGear(name+"_sun", teeth = sun_teeth, pressureAngle=20, module=module, helixAngle=helix, height=height, clearance = clearance, bore=bore, position = Base.Vector(0.00,0.00,z_off), rotation =0, extrude=extrude)
    for i in range(0,planets):
        a = i*360.0/planets
        planet_x = cos(pi/180.0*a)*mesh_distance
        planet_y = sin(pi/180.0*a)*mesh_distance
        planet_pos = Draft.makePoint(planet_x, planet_y, 0)
        planet_pos.Label = "planet_center_"+str(i)

        planet_add_rotation = -(a*float(sun_teeth+ring_teeth)/sun_teeth)*(0.5*sun_teeth/planet_teeth)

        makeGear(name+"_planet_%i"%i, 
            teeth = planet_teeth, 
            pressureAngle=20, 
            module=module, 
            helixAngle=-helix, 
            height=height, 
            clearance = clearance,  
            bore=planet_bore, 
            position = Base.Vector(planet_x,planet_y,z_off), 
            rotation =planet_rotation + planet_add_rotation, 
            extrude=extrude, 
            bearing=planet_bearings, 
            bearing_diameter=planet_bearing_diameter, 
            bearing_height=planet_bearing_height)
    makeRingGear(name+"_ring", 
        teeth = ring_teeth, 
        pressureAngle=20, 
        module=module, 
        helixAngle=-helix, 
        height=height, 
        clearance = clearance, 
        bore=bore, 
        position = Base.Vector(0.0,0.00,z_off), 
        rotation =ring_rotation, 
        external=False, 
        extrude=extrude)
    App.ActiveDocument.recompute()

helix = 15
planets = 3
makePlanetary("gearbox", 
                module=1.11,
                sun_teeth = 24, 
                planet_teeth =24, 
                z_off=0, helix = helix, 
                height=10, 
                bore=8, 
                clearance = 0.25, 
                planets = planets, 
                planet_bearings = True, 
                planet_bore = 5, 
                planet_bearing_diameter = 10, 
                planet_bearing_height = 5)

Gui.SendMsgToActiveView("ViewFit")


#
