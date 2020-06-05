# -*- coding: cp1252 -*-
from __future__ import division
from visual import *
from math import radians, degrees, sin, cos
import numpy as np
from ast import literal_eval
import functionfile as functions
import wx


# -*- coding: cp1252 -*-
#constants
dt = 0.1 #in solar days (JD units)
mindt = 0.001
maxdt = 5
tickRate = 300 #time passing per second is dt*tickRate
scale = 1000 #distance scale factor
starDistance = 500000 #AU
starCount = 500 #number of stars generated
starSize = 2 #pixels
elementnames = ['a','e','I','w','W','M0']
daysPerYear = 365.2422 #for conversion
dottedtex = materials.texture(data = materials.loadTGA("Dottedtexture"), mapping = "spherical", interpolate=False)
degreeSign= u'\N{DEGREE SIGN}'

#input file parsing
inp = open('Input/Object Input.txt')
epoch = [float(line[1:]) for line in inp if line[0] == '@'][0]
epochDMY = functions.J_to_DMY(epoch)
dayCounterText = " days past since {}/{}/{}.".format(*epochDMY) #not sure why addition of hello avoids glitch but it works
decimalYearOfEpoch = functions.DMY_to_decimalYear(*epochDMY)

inputlines = [line for line in inp if not line[0] in '#@']
orbiterlines = [line.split() for line in inputlines if line.split()[0] == 'orbiter']
orbiterinputs = [orbiterline[1:3] + [dict(zip(elementnames, map(float,orbiterline[3:5]) + map(radians,map(float,orbiterline[5:9]))))] + [radians(float(orbiterline[9]))] + map(float,orbiterline[10:13]) + [map(float,orbiterline[13:])] for orbiterline in orbiterlines]

G = 1.488E-34 #AU^3 Day^-2 kg^-1

scene.fullscreen = True
scene.up = (1,0,0)
scene.forward = (-0.1,1,0)
scene.title = 'Cosmic Neighborhood Simulator'
scene.width=800
scene.height=700
scene.x = 0
scene.y = 0

scene.range = 1e8 #barely inside star boundary,  WIP

class PointCloud():

    def __init__(self, name, primaryName, count, mina, maxa, size, restrictI):
        self.name = name
        self.primaryName = primaryName
        self.a = (mina+maxa)/2
        self.mass = 0.0
        
        randomNums = np.random.rand(6,count) #from which elements are determined
        randomNums[0] = (maxa-mina)*randomNums[0] + mina
        randomNums[1] *= 0.3
        if restrictI:
            randomNums[2] = 0.174533*2*randomNums[2] - 0.174533 #getting a value between -10 and 10 degrees
        self.obliquity = max(randomNums[2])
        randomNums[3:6] *= 2*pi
        asteroidElementslist = [dict(zip(elementnames, elements)) for elements in transpose(randomNums)]
        self.Elementslist = asteroidElementslist

        mu = G*Objects[primaryName].mass #asteroid mass is negligable
        self.nlist = [sqrt(mu/(elements['a']**3)) for elements in self.Elementslist]
        self.revolutionPeriod =2*pi/np.mean(self.nlist)
        self.f = frame()
        primary = Objects[primaryName]
        self.f.frame = primary.f
        self.viz = points(frame=self.f, size=size, color = (0.5,0.5,0.5))
        self.vizlabel = label(frame = self.f, text=name, pos = (0,0,scale*self.a), height=6)
        
        self.axis = arrow(frame = self.f)            
        self.size = maxa #setting greatest radius for camera

    def update(self, t):
        self.poses = [scale*functions.getpos(elements, t, n) for elements, n in zip(self.Elementslist, self.nlist)]
        self.viz.pos = self.poses
        angle = t*2*pi/self.revolutionPeriod
        self.vizlabel.pos = (0, scale*self.a*sin(angle), scale*self.a*cos(angle))

class Orbiter():

    """elements is a dictionary containing orbital elements"""
    def __init__(self, name, primaryName, elements, obliquity, size, mass, rotationPeriod, planetColor): #primaryName is name of object being orbited
        self.elements = elements
        
        self.primaryName = primaryName
        self.size = size
        self.name = name
        self.obliquity = obliquity
        self.mass = mass
        self.pos = (0,0,0) #in case Moon.update is called before its Planet.update

        self.f = frame(trail = curve(color=planetColor), axis = (1,0,0)) #init. axis set to sun's axis.
        planetMaterial = materials.texture(data = materials.loadTGA(name), mapping = 'spherical')

        ####frame to house texture pole glitch####
        self.rotationFrame = frame(frame = self.f)
        viz = sphere(frame= self.rotationFrame, radius=scale*size, color=(1,1,1), material=planetMaterial) #planet sphere, init pos
        viz.rotate(angle = pi/2, axis = (0,0,1)) #ensuring poles of texture match up
        self.color = planetColor
        ####end reference to rotationFrame and pole glitch####
        
        self.vizlabel = label(frame=self.f,
            text=name, xoffset=20,
            yoffset=12, space=size,
            height=10, border=6,
            font='sans')

        self.f.rotate(angle=obliquity, axis=(0,1,0)) #assigning proper axes
        self.rotationSpeed = 2*pi/rotationPeriod #in rad/Day

        self.axis = arrow(length=2*size*scale, frame = self.f)
        #scene.up = self.f.axis

        if '(' in primaryName: #if the primary is a coordinate, not an object
            self.worldFrame = frame(pos = literal_eval(primaryName))
            self.a = 1.897e9
            self.f.frame = self.worldFrame
            self.revolutionPeriod = 2.25e8
            self.primaryName = 'Sagittarius A* (Milk way supermassive black hole)'
        else:
            primary = Objects[primaryName]
            self.a = elements['a']
            self.f.frame = primary.f
            self.f.trail.frame = primary.f
            self.vizlabel.height = primary.vizlabel.height - 2

            mu = G*(mass + Objects[primaryName].mass)
            self.n = sqrt(mu/(self.a**3))
            self.revolutionPeriod = 2*pi/self.n #in JD
            print(name, self.n)
            
        
    def update(self, t):
        if self.name != "Sun":        
            self.pos = functions.getpos(self.elements, t, self.n)
            self.f.pos = self.pos*scale
            if t < self.revolutionPeriod: self.f.trail.append(pos = self.f.pos) #ensures the trail isnt overwritten
        self.rotationFrame.rotate(angle = dt*self.rotationSpeed) #in rad
    

class Rings():
    
    def __init__(self, name, primaryName, inner, outer, minthick, maxthick, maxgap):
        self.name = name
        self.primaryName = primaryName
        self.obliquity = 0.0
        primary = Objects[primaryName]
        self.a = primary.size + (inner+outer)/2
        self.f = primary.f
        self.size = outer #greatest radial distance for camera
        self.vizlabel = label(frame = self.f, text=name, pos = (0,0,self.a*scale), height=6)
        self.revolutionPeriod = 0.0
        self.mass = 0.0
        self.axis = arrow(frame = self.f)

        rands2 = np.random.rand(50,2)
        crs = []
        r = (outer + primary.size)*scale
        for n in range(20):
            if r < (inner + primary.size)*scale : break
            thick = (maxthick-minthick)*rands2[n][0]+minthick
            gap = rands2[n][1]*maxgap
            crs.append(shapes.circle(radius=r-gap, thickness=thick))
            r -= thick + gap
        
        rands = np.random.rand(50,3)
        rands[:,0] = 0.2*rands[:,0]+primary.color[0]-0.1
        rands[:,1] = 0.2*rands[:,1]+primary.color[1]-0.1
        rands[:,2] = 0.2*rands[:,2]+primary.color[2]-0.1

        straight = [(0,0,0),(0.00001,0,0)]

        for i in range(len(crs)):
            extrusion(frame=self.f,pos=straight, shape=crs[i], color=(rands[i]))

    def update(self, t): pass #rings don't visually move

class TextureCloud():

    def __init__(self, name, primaryName, shape, radius, halfthickness, pos):
        self.name = name
        self.a = radius
        self.primaryName = primaryName
        self.size = radius + halfthickness #greatest radial distance for camera
        self.obliquity = 0
        primary = Objects[primaryName]
        mu = G*primary.mass
        print(name, radius)
        n = sqrt(mu/(radius**3)) #assuming the average radius is approximately elements['a']
        print(name, n)
        self.revolutionPeriod = 2*pi/n #in JD
        self.angularSpeed = 2*pi/self.revolutionPeriod
        self.mass = 0.0

        
        self.f = frame(frame = primary.f)
        self.axis = arrow(frame = self.f)
        if shape == 'sphere':
            dottedtex.mapping = 'spherical'
            sphere(pos = pos, radius = scale*radius, material = dottedtex, frame = self.f)
            if halfthickness != 0:
                sphere(pos = pos, radius = scale*(radius - halfthickness), material = dottedtex, frame = self.f)
                sphere(pos = pos, radius = scale*(radius + halfthickness), material = dottedtex, frame = self.f)
        elif shape == 'ring':
            dottedtex.mapping = 'rectangular'
            ring(pos = pos, radius = scale*radius, material = dottedtex, thickness = scale*halfthickness,   frame = self.f)
            self.f.rotate(angle = 2*pi*np.random.rand(1)[0])
            ring(pos = pos, radius = scale*radius, material = dottedtex, thickness = scale*halfthickness/2, frame = self.f)

        self.vizlabel = label(frame = self.f, text = name, height = 14, pos = (0,0,self.a*scale))

    def update(self, t): pass#self.f.rotate(angle = self.angularSpeed*t) #presumably about self.f's axis

##class Object():
##
##    def __init__(self, inputline):
##        
##        if inputline[0] == "orbiter":
##            Orbiter.__init__(self, *(orbiterline[1:3] + [dict(zip(elementnames, map(float,orbiterline[3:5]) + map(radians,map(float,orbiterline[5:9]))))] + [radians(float(orbiterline[9]))] + map(float,orbiterline[10:13]) + [map(float,orbiterline[13:])]))
##            
inp = open('inp2.txt')
inputlines = [line for line in inp if line[0] != '#']
Objects = {}

orbiterlines = [functions.splitSpecial(line) for line in inputlines if line.split()[0] == 'orbiter']
orbiterinputs = [orbiterline[1:3] + [dict(zip(elementnames, map(float,orbiterline[3:5]) + map(radians,map(float,orbiterline[5:9]))))] + [radians(float(orbiterline[9]))] + map(float,orbiterline[10:13]) + [map(float,orbiterline[13:])] for orbiterline in orbiterlines]

orbiters = []
for orbiterinput in orbiterinputs:
    #print orbiterinput
    orbiters.append(Orbiter(*orbiterinput))
    Objects[orbiterinput[0]] = orbiters[-1]
    #print Objects

pointcloudlines = [functions.splitSpecial(line) for line in inputlines if line.split()[0] == 'pointcloud']
pointcloudinputs = [pointcloudline[1:3] + map(float,pointcloudline[3:7]) + [literal_eval(pointcloudline[7])] for pointcloudline in pointcloudlines]

pointclouds = []
for pointcloudinput in pointcloudinputs:
    pointclouds.append(PointCloud(*pointcloudinput))
    Objects[pointcloudinput[0]] = pointclouds[-1]

ringslines = [functions.splitSpecial(line) for line in inputlines if line.split()[0] == 'rings']
ringsinputs = [ringsline[1:3] + map(float,ringsline[3:]) for ringsline in ringslines]

ringss = []
for ringsinput in ringsinputs:
    ringss.append(Rings(*ringsinput))
    Objects[ringsinput[0]] = ringss[-1]

texturecloudlines = [functions.splitSpecial(line) for line in inputlines if line.split()[0] == 'texturecloud']
texturecloudinputs = [texturecloudline[1:4] + map(float,texturecloudline[4:6]) + [map(float,texturecloudline[6:])] for texturecloudline in texturecloudlines]
textureclouds = []
for texturecloudinput in texturecloudinputs:
    textureclouds.append(TextureCloud(*texturecloudinput))
    Objects[texturecloudinput[0]] = textureclouds[-1]

####making stars####
angles = 2*pi*np.random.rand(starCount) #generating random angular coordinates
heights = 2*np.random.rand(starCount) - 1 #generating random z coordinates
starxs = [starDistance*scale*cos(angle)*sqrt(1-height**2) for angle, height in zip(angles, heights)]
starys = [starDistance*scale*sin(angle)*sqrt(1-height**2) for angle, height in zip(angles, heights)]
starzs = starDistance*scale*heights
stars = points(pos=zip(starxs, starys, starzs), size=starSize)

focusingOn = Objects['Sun'] #init
#scene.fov = pi/5000

#######WX Controls#######

def slidedt(evt):
    global dt
    dt = dtSlider.GetValue()/1000
    simTime.SetLabel("Simulation time: " + str(dt*tickRate) + " Days/s")

def changefocus(evt):
    global focusingOn
    name = focusChooser.GetString(focusChooser.GetSelection())
    focusingOn = Objects[name]
    obl.SetLabel('Obliquity - {:.3f}°'.format(degrees(focusingOn.obliquity)))
    orb.SetLabel('Orbital Period - {:.6} days'.format(focusingOn.revolutionPeriod))
    siz.SetLabel('Size - {:.6} AU'.format(focusingOn.size))
    mas.SetLabel('Mass - {:.6} kg'.format(focusingOn.mass))
    peri.SetLabel('Semi-major Axis - {:.6} AU'.format(focusingOn.a))
    pri.SetLabel('Primary - ' + focusingOn.primaryName)
    pri.Wrap(L/2)
    
##def autozoomfocus(evt):
##    dist = 10#20*scale*focusingOn.size
##    for ob in focusingOn.f.objects:
##        if not isinstance(ob.pos, np.ndarray):
##            if mag(ob.pos) > dist: dist = mag(ob.pos)
##    scene.range = dist
##    scene.up = focusingOn.f.axis

def pause(evt):
    global playing
    playing = not playing
    pauseButton.SetLabel("Pause") if playing else pauseButton.SetLabel("Resume")

def leave(evt): exit()

def toggleLabels(evt):
    global Objects
    for Object in Objects:
        Objects[Object].vizlabel.visible = not Objects[Object].vizlabel.visible

def toggleAxes(evt):
    global Objects
    for Object in Objects:
        Objects[Object].axis.visible = not Objects[Object].axis.visible


L = 500
w = window(width=L, height=400, title = 'Controls', x = 800,y=0)
p = w.panel

p.SetDoubleBuffered(True)

SliderWidth = 300
padding = 50

dayCounter = wx.StaticText(p, pos = (L/2-210, 10), size = (200,20), style=wx.ALIGN_RIGHT )#| wx.ST_NO_AUTORESIZE)

yearCounter = wx.StaticText(p, pos = (L/2+10,10))#, size=(200,20), style=wx.ALIGN_RIGHT)
lab = wx.StaticText(p, pos = (L/2,35), label = "Set step time (solar days):")
lab.SetPosition((lab.GetPosition().x-lab.GetSize().x/2, lab.GetPosition().y))

wx.StaticText(p, pos = (L/2-SliderWidth/2-25,50), label = str(mindt))
wx.StaticText(p, pos = (L/2+SliderWidth/2,   50), label = str(maxdt))
dtSlider = wx.Slider(p, pos = (L/2-SliderWidth/2,50), minValue = 1, maxValue = maxdt/mindt, size=(SliderWidth,20), value = dt/mindt)
dtSlider.Bind(wx.EVT_SCROLL, slidedt)
simTime = wx.StaticText(p, pos = (padding,80), label = "Simulation rate: " + str(dt*tickRate) + " Days/s")
pauseButton = wx.Button(p,pos=(padding,100),      size=(80,25), label="Pause")
pauseButton.Bind(wx.EVT_BUTTON, pause)
exitButton = wx.Button(p,pos=(L-padding-80,100), size=(80,25), label="Exit")
exitButton.Bind(wx.EVT_BUTTON, leave)

#--------------------------------------------
wx.StaticLine(p, pos = (padding+40, 150), size = (L - 2*(padding+40), 1))

wx.StaticText(p, pos = (padding,175), label = "Focusing Object:")
focusChooser = wx.Choice(p, pos = (padding,200), choices = [Objectname for Objectname in Objects], size=(80,30))
focusChooser.Bind(wx.EVT_CHOICE, changefocus)
focusChooser.SetSelection(focusChooser.FindString("Sun")) #init set to Sun

#wx.StaticText(p, pos = (padding+80+15,200), label = 'characteristics:')
obl = wx.StaticText(p, pos = (padding, 230))
orb = wx.StaticText(p, pos = (padding, 250))
siz = wx.StaticText(p, pos = (padding, 270))
mas = wx.StaticText(p, pos = (L/2, 230))
peri = wx.StaticText(p, pos = (L/2, 250))
pri = wx.StaticText(p, pos = (L/2, 270))


changefocus(None)


autoZoomer = wx.Button(p, pos = (padding,330), label = "Toggle Labels",size=(80,25))
autoZoomer.Bind(wx.EVT_BUTTON, toggleLabels)

autoZoomer2 = wx.Button(p, pos = (L-padding-80,330), label = "Toggle Axes",size=(80,25))
autoZoomer2.Bind(wx.EVT_BUTTON, toggleAxes)

toggleAxes(None)

def updateCounters(t):
    dayCounter.SetLabel(str(t) + dayCounterText)
    yearCounter.SetLabel("The year is "+ str(int(decimalYearOfEpoch+t/daysPerYear))+'.')

#######begin animation#######

t=0
playing = True
while True:
    rate(tickRate)
    if playing:
        for ObjectName in Objects:
            Objects[ObjectName].update(t)
        t += dt
    updateCounters(t)
    scene.center = focusingOn.f.frame.frame_to_world(focusingOn.f.pos)
