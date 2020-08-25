import numpy
import math
import re
from maya import cmds
import maya.api.OpenMaya as om

import cnt
reload (cnt)



def getsegments(poly,segmentDensity = 1, useTexture = True, colorThreshold=100):
    # get edges segments

  
    tri = cmds.duplicate(poly)

    cmds.polyTriangulate(tri)
    
    segmentList =[]
    segmentsDict = {}

    ignoreEdge = []

    polyArea = cmds.polyEvaluate(poly,wa = 1) 
    segmentSize = math.sqrt(polyArea) / (50 * segmentDensity)
    

    #create segments for edges
    for i in range (cmds.polyEvaluate(tri,e=1)):
        edge = '%s.e[%s]'%(tri[0],i)
        edgeFace = cmds.polyListComponentConversion(edge,fe=True,tf=True)[0]
        
        faceid = edgeFace[ edgeFace.index('[')+1 : edgeFace.index(']')]
        faceIdArray = faceid.split(":")
        
        if len(faceIdArray) <= 1: #ignore border edges
            continue
        
        normals = []

        #get normals for edgeFaces
        for fId in faceIdArray:
            face = '%s.f[%s]'%(tri[0],fId)
            facefv = cmds.polyInfo(face,fv=1)
            normals.append(getNormalFromFace(face,tri))

        #normal average
        normal = [ (normals[0][0] + normals[1][0]) / 2 ,
                   (normals[0][1] + normals[1][1]) / 2 , 
                   (normals[0][2] + normals[1][2]) / 2]

        
        

        edgeV = cmds.polyInfo(edge,ev=1)
        verts = edgeV[0].split()[2:4]
        
        vertsList = getVerts(verts,tri) 
        
        
        line = Line(vertsList[0],vertsList[1])
        size = int(line.length/segmentSize)



        for s in getLinesegments(line,size):
            segmentList.append(Segment(s, normal))

    
    #crete segments for inner face without edges

    for i in range(cmds.polyEvaluate(tri,f=1)):
        face = '%s.f[%s]'%(tri[0],i)
        facefv = cmds.polyInfo(face,fv=1)
        verts = facefv[0].split()[2:]
        
        #create array for face verts
        vertsList = getVerts(verts,tri) 

        normal = getNormalFromVerts(vertsList)
        
        for s in getFacesegments(vertsList,segmentSize):
            segmentList.append(Segment(s, normal))
            

    # delete tringualted Poly


    
        
    cmds.delete(tri) 
    colorDict = {}
    sectionList = []
    # sample texures
    if useTexture:
        
        segmentList = cnt.getColor(segmentList,poly)
        for segment in segmentList:
            color = segment.getColor()
            if not color in colorDict:
                colorDict[color] = [segment]
            else:
                colorDict[color].append(segment)

    #Delete Color dictionaries with length lower than colorThreshold
        toDelete = []
        for key in colorDict:
            if len(colorDict[key]) < colorThreshold:
                toDelete.append(key)    #mark keys for deletion
    
        for key in toDelete:
            del colorDict[key]  #delete keys
        
        sectionList = dectToSectionList(colorDict)
    else:
        sectionList.append(Section(segmentList))


    
    return sectionList


def dectToSectionList(colorDict):
    sList = []
    for key in colorDict:
        sList.append(Section(colorDict[key],color=key,active=False))
    
    return sList


def getVerts(verts,poly):
    vertsList = []
    for v in verts:
        vert = '%s.vtx[%s]'%(poly[0],int(v))
        vertsList.append(cmds.pointPosition(vert,w=1))

    return vertsList


def getNormalFromFace(face,tri):
    #Return normal of a face
    # creates 2 vectors from verts and retrun cross product

    facefv = cmds.polyInfo(face,fv=1)
    verts = facefv[0].split()[2:]

    #create array for face verts
    vertsList = getVerts(verts,tri) 

    vert1=numpy.array(vertsList[0])
    vert2=numpy.array(vertsList[1])
    vert3=numpy.array(vertsList[2])
    v = vert2 - vert1
    w = vert3 - vert1
    
    cp = numpy.cross(v,w)
  


    n  = numpy.array(cp)

    norm = numpy.linalg.norm(n) #get normalize value
    normalized = n/norm
    x = normalized[0]
    y = normalized[1]
    z = normalized[2]


    return [x,y,z,0]


def getNormalFromVerts(vertsList):
    # Return Normal from face verts
    # creates 2 vectors from verts and retrun cross product



    #create array for face verts


    vert1=numpy.array(vertsList[0])
    vert2=numpy.array(vertsList[1])
    vert3=numpy.array(vertsList[2])
    v = vert2 - vert1
    w = vert3 - vert1
    
    cp = numpy.cross(v,w)


    n  = numpy.array(cp)

    norm = numpy.linalg.norm(n) #get normalize value
    normalized = n/norm
    x = normalized[0]
    y = normalized[1]
    z = normalized[2]


    return [x,y,z,0]
    

def getRotation(normal):
    vector = om.MVector(0,1,0)
    vNormal = om.MVector(normal[0],normal[1],normal[2])

    quat = om.MQuaternion(vector,vNormal)


    quat.normalizeIt() # to normalize
    rot = quat.asEulerRotation()
    return [ om.MAngle(rot.x).asDegrees(), om.MAngle(rot.y).asDegrees(), om.MAngle(rot.z).asDegrees() ]


    


def getFacesegments(verts,segmentSize,mode = 0):
    # Mode 1 creates segments on edges only
    # Mode 0 creates segments inside without edges

    line1 = Line(verts[0],verts[1])
    line1.id = "01"
    line2 = Line(verts[1],verts[2])
    line2.id = "12"
    line3 = Line(verts[2],verts[0])
    line3.id = "20"

    
    lineList = []
    lineList.append(line1)
    lineList.append(line2)
    lineList.append(line3)

    lineList.sort(key=lambda x: x.length)

    h = lineList[2]
    if h.id == "01":
        lineList[0] = line3
        lineList[1] = line2
    elif h.id == "12":
        lineList[0] = line1
        lineList[1] = line3
    else:
        lineList[0] = line2
        lineList[1] = line1

    

    # line0 = [p1,p2]

    segmentCount0 = int(lineList[0].length/segmentSize)
    segmentCount1 = int(lineList[1].length/segmentSize)
    segmentCount2 = segmentCount0 +segmentCount1
    
    segmentList = []
    segmentList.append(getLinesegments(lineList[0],segmentCount0))
    segmentList.append(getLinesegments(lineList[1],segmentCount1))
    segmentList.append(getLinesegments(lineList[2],segmentCount2))

    segmentList[0].reverse()
    segmentList[1].reverse()

    linesegments = segmentList[0] + segmentList[1]

   

    i = 0
    segmentsList = []
 
    for s in segmentList[2]:
        line = Line(s,linesegments[i])
        x = getLinesegments(line,int(line.length/segmentSize))
        ignore = 0
        for l in x:
            if(ignore != 0):
                segmentsList.append(l)
            ignore += 1
        i += 1


    return segmentsList

def getLinesegments(line,segmentCount):

    lst =[]

    p1 = line.p1
    p2 = line.p2

    lx = p2[0] - p1[0]
    ly = p2[1] - p1[1]
    lz = p2[2] - p1[2]

    for i in range(0,segmentCount):
        lst.append([p1[0]+lx * (float(i)/segmentCount),p1[1]+ly* (float(i)/segmentCount),p1[2]+lz* (float(i)/segmentCount)])
    
    return lst


class Line(object):
    def __init__(self,p1,p2):
        self.p1 = p1
        self.p2 = p2
        self.length = self.getLength()
        self.id = ""
    
    def getLength(self):
        sum = 0.0
        for i in range(3):
            sum+= pow(self.p1[i]- self.p2[i],2)
        distance = math.sqrt(sum)
        return distance

class Segment(object):
    def __init__(self,location,normal):
        self.x = location[0]
        self.z = location[1]
        self.y = location[2]
        self.id = id
        self.location = location
        self.rotation  = getRotation(normal)
        self.color =[]
        self.normal = normal

    def getColor(self, mergeThreshold = 40):
        if len(self.color) >= 3:
            #convert rgb to hex
            r = int(self.color[0]* 255/mergeThreshold) * mergeThreshold
            g = int(self.color[1]* 255/mergeThreshold) * mergeThreshold
            b = int(self.color[2]* 255/mergeThreshold) * mergeThreshold
            hex = '#%02x%02x%02x' % ( r , g , b)

            return hex
        else:
            return "0000"

class Section(object):
    def __init__(self,segments=[],active = True,poly =[], color=None,tree = None,isItem = True, pool = []):
        self.active = active
        self.segments = segments
        self.bbox = self.getBbox(segments)
        self.segmentsDict = {}
        self.segmentsDict, self.keyList = self.generateDict(segments)
        self.colliders = []
        self.poly = poly
        self.color  = color
        self.isItem = isItem
        self.tree = tree
        self.pool = []

    def removeKeys(self,bbox):
        
        #print len(self.keyList)
        self.keyList[:] = [x for x in self.keyList if not cnt.inBbox(bbox,self.segmentsDict[x].location,[0.1,0.1,0.1])]
        #print len(self.keyList)

    def getBbox(self,segments):
    #sort and save Min and Max

        listLength = self.getSize()
        if segments == []:
            return None

        segments.sort(key=lambda x: (x.z , x.y , x.x),reverse=1)
        zMax = segments[0].z
        zMin = segments[listLength-1].z

        segments.sort(key=lambda x: (x.y , x.x , x.z),reverse=1)
        yMax = segments[0].x
        yMin = segments[listLength-1].x

        segments.sort(key=lambda x: (x.x , x.y , x.z),reverse=1)
        xMax = segments[0].x
        xMin = segments[listLength-1].x

        #Create bounding box for segemnts
        bbox = [xMin,yMin,zMin,xMax,yMax,zMax]
        return bbox

    def generateDict(self,segments):
        segmentsDict = {}
        for i in range (self.getSize()):
            segmentsDict[i] = segments[i]
            segmentsDict[i].id = i

        keyList = list(segmentsDict.keys())

        return segmentsDict,keyList

    def addCollider(self,bbox):
        self.colliders.append(bbox)

    def getSafeArea(self,poly):
        MPoly = om.MGlobal.getSelectionListByName(poly)
        polyPath = MPoly.getDagPath(0)
        tranformation = om.MFnTransform(polyPath)

        scale = tranformation.scale()
        safeList = self.keyList[:]
        for collider in self.colliders:
            safeList[:] = [x for x in safeList if not cnt.inBbox(collider,self.segmentsDict[x].location,scale)]
        return safeList


            

    def getSize(self):
        return len(self.segments)







