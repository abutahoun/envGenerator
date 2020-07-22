from maya.api import OpenMaya as om
import maya.OpenMaya as om1
import maya.OpenMayaRender as omr
import uuid

import maya.OpenMaya as om1  
import maya.OpenMayaFX as omfx  

import numpy
from maya import cmds
from array import array
import ctypes

def getColor(segmantDict,poly):


    MPoly = om.MGlobal.getSelectionListByName(poly)

    polyPath = MPoly.getDagPath(0)
    mesh = om.MFnMesh(polyPath)

    length = len(segmantDict)


    imgObj = om1.MObject()  
    sel = om1.MSelectionList()  
    om1.MGlobal.getSelectionListByName('lambert2', sel)  
    sel.getDependNode(0, imgObj)  
    fnThisNode = om1.MFnDependencyNode(imgObj)  
    attr = fnThisNode.attribute( "color" )  

    outColours = om1.MVectorArray()  
    outAlphas = om1.MDoubleArray() 

    uColArray = om1.MDoubleArray()  
    vColArray = om1.MDoubleArray() 
    uColArray.setLength(1)  
    vColArray.setLength(1)  



    for segmant in segmantDict:
        location = segmantDict[segmant].location
        vector = om.MVector(location[0],location[1],location[2])
        point = om.MPoint(vector)
        u,v,w = mesh.getUVAtPoint(point,4)
        uColArray.set(u, 0)  
        vColArray.set(v, 0) 
        omfx.MDynamicsUtil.evalDynamics2dTexture(imgObj, attr, uColArray, vColArray, outColours, outAlphas)  

        color = outColours[0]

        segmantDict[segmant].color = [color.x,color.y,color.z]


    return segmantDict



    

  

def CreatePoly(location,scale):
    sphere = cmds.polySphere(r=1)
    cmds.setAttr(sphere[0]+".translate",location[0],location[1],location[2])
    cmds.setAttr(sphere[0]+".scale",scale[0],scale[1],scale[2])
    return sphere




def inBbox(bbox,translate,scale):
    
    if translate[0] + scale[0] >= bbox[0]  and translate[0] - scale[0] <= bbox[3]  :
        if translate[1] + scale[1]  >= bbox[1]  and translate[1] - scale[1] <= bbox[4] :
            if translate[2] + scale[2]  >= bbox[2]  and translate[2] - scale[2] <= bbox[5] :
                return True
    else:
        return False



def getColorConnection(poly):
    print poly
    shape = cmds.listRelatives(poly, shapes=True)
    shadingGrps = cmds.listConnections(shape[0],type='shadingEngine')
    shaders = cmds.ls(cmds.listConnections(shadingGrps),materials=1)

    color = cmds.listConnections(shaders[0]+'.color')
    outColor = color[0]+'.outColor'
    print outColor
    return outColor



def getFiles(folder, fileTypes = ['obj','fbx']):
    files = []

    for fileType in fileTypes:
        files += (cmds.getFileList(folder=folder, filespec='*.%s' % fileType))
    
    for i in range(len(files)):
        files[i] = '%s\%s' % (folder,files[i])

    
    return files