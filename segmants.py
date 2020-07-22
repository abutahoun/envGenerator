import numpy
import math
import re
from maya import cmds
import maya.api.OpenMaya as om

import cnt



def getSegmants(poly,segmantSize):
    # get edges segmants

    print "getSegmants"
    
    print poly
    tri = cmds.duplicate(poly)

    cmds.polyTriangulate(tri)
    
    segmantList =[]
    segmantsDict = {}

    ignoreEdge = []

    

    #create segmants for edges
    for i in range (cmds.polyEvaluate(tri,e=1)):
        edge = '%s.e[%s]'%(tri[0],i)
        edgeFace = cmds.polyListComponentConversion(edge,fe=True,tf=True)[0]
        
        faceid = edgeFace[ edgeFace.index('[')+1 : edgeFace.index(']')]
        faceIdArray = faceid.split(":")
        
        if len(faceIdArray) <= 1: #ignore border edges
            continue
        
        normals = []

        #get normals for edgeFaces
        for i in range(2):
            face = '%s.f[%s]'%(tri[0],i)
            facefv = cmds.polyInfo(face,fv=1)
            normals.append(getNormal(face,tri))

        #normal average
        normal = [ (normals[0][0] + normals[1][0]) / 2 ,
                   (normals[0][1] + normals[1][1]) / 2 , 
                   (normals[0][2] + normals[1][2]) / 2]

        
        

        edgeV = cmds.polyInfo(edge,ev=1)
        verts = edgeV[0].split()[2:4]
        
        vertsList = getVerts(verts,tri) 
        
        print vertsList

        
        line = Line(vertsList[0],vertsList[1])
        size = int(line.length/segmantSize)



        for s in getLineSegmants(line,size):
            segmantList.append(Segmant(s, normal))

    
    #crete segmants for inner face without edges

    for i in range(cmds.polyEvaluate(tri,f=1)):
        face = '%s.f[%s]'%(tri[0],i)
        facefv = cmds.polyInfo(face,fv=1)
        verts = facefv[0].split()[2:]
        
        #create array for face verts
        vertsList = getVerts(verts,tri) 

        normal = getNormal2(vertsList)
        
        for s in getFaceSegmants(vertsList,segmantSize):
            segmantList.append(Segmant(s, normal))

    
    #numpy.random.shuffle(segmantList)
            

    # delete tringualted Poly


    
        
    cmds.delete(tri) 
    
    # for segmant in segmantList:
    #     mesh = cmds.duplicate('pCylinder1')[0]
    #     cmds.move(segmant.location[0],segmant.location[1],segmant.location[2],mesh,ws = 1,rpr=1)


    return segmantList


def getVerts(verts,poly):
    vertsList = []
    for v in verts:
        vert = '%s.vtx[%s]'%(poly[0],int(v))
        vertsList.append(cmds.pointPosition(vert,w=1))

    return vertsList


def getNormal(face,tri):
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
    #cp = numpy.cross(cp,[0,1,0])


    n  = numpy.array(cp)

    norm = numpy.linalg.norm(n) #get normalize value
    normalized = n/norm
    x = normalized[0]
    y = normalized[1]
    z = normalized[2]


    return [x,y,z,0]


def getNormal2(vertsList):
    # creates 2 vectors from verts and retrun cross product



    #create array for face verts


    vert1=numpy.array(vertsList[0])
    vert2=numpy.array(vertsList[1])
    vert3=numpy.array(vertsList[2])
    v = vert2 - vert1
    w = vert3 - vert1
    
    cp = numpy.cross(v,w)
    #cp = numpy.cross(cp,[0,1,0])


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


    


def getFaceSegmants(verts,segmantSize,mode = 0):
    # Mode 1 creates segmants on edges only
    # Mode 0 creates segmants inside without edges

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

    segmantCount0 = int(lineList[0].length/segmantSize)
    segmantCount1 = int(lineList[1].length/segmantSize)
    segmantCount2 = segmantCount0 +segmantCount1
    
    segmantList = []
    segmantList.append(getLineSegmants(lineList[0],segmantCount0))
    segmantList.append(getLineSegmants(lineList[1],segmantCount1))
    segmantList.append(getLineSegmants(lineList[2],segmantCount2))

    segmantList[0].reverse()
    segmantList[1].reverse()

    lineSegmants = segmantList[0] + segmantList[1]

   

    i = 0
    segmantsList = []
 
    for s in segmantList[2]:
        line = Line(s,lineSegmants[i])
        x = getLineSegmants(line,int(line.length/segmantSize))
        ignore = 0
        for l in x:
            if(ignore != 0):
                segmantsList.append(l)
            ignore += 1
        i += 1


    return segmantsList

def getLineSegmants(line,segmantCount):

    lst =[]

    p1 = line.p1
    p2 = line.p2

    lx = p2[0] - p1[0]
    ly = p2[1] - p1[1]
    lz = p2[2] - p1[2]

    for i in range(0,segmantCount):
        lst.append([p1[0]+lx * (float(i)/segmantCount),p1[1]+ly* (float(i)/segmantCount),p1[2]+lz* (float(i)/segmantCount)])
    
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

class Segmant(object):
    def __init__(self,location,normal):
        self.x = location[0]
        self.z = location[1]
        self.y = location[2]
        self.id = id
        self.location = location
        self.rotation  = getRotation(normal)
        self.color =[]
        self.normal = normal
        






