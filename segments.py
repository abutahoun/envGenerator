import numpy
import math
import re
from maya import cmds
import maya.api.OpenMaya as om

import cnt



def getsegments(poly,segmentSize):
    # get edges segments

  
    tri = cmds.duplicate(poly)

    cmds.polyTriangulate(tri)
    
    segmentList =[]
    segmentsDict = {}

    ignoreEdge = []

    

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
            segmentList.append(segment(s, normal))

    
    #crete segments for inner face without edges

    for i in range(cmds.polyEvaluate(tri,f=1)):
        face = '%s.f[%s]'%(tri[0],i)
        facefv = cmds.polyInfo(face,fv=1)
        verts = facefv[0].split()[2:]
        
        #create array for face verts
        vertsList = getVerts(verts,tri) 

        normal = getNormalFromVerts(vertsList)
        
        for s in getFacesegments(vertsList,segmentSize):
            segmentList.append(segment(s, normal))
            

    # delete tringualted Poly


    
        
    cmds.delete(tri) 
    

    return segmentList


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

class segment(object):
    def __init__(self,location,normal):
        self.x = location[0]
        self.z = location[1]
        self.y = location[2]
        self.id = id
        self.location = location
        self.rotation  = getRotation(normal)
        self.color =[]
        self.normal = normal
        






