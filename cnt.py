from maya.api import OpenMaya as om
import maya.OpenMaya as om1
import maya.OpenMayaRender as omr
import uuid

from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.OpenMaya as om1  
import maya.OpenMayaFX as omfx  

import numpy
from maya import cmds
from array import array
import ctypes

import pymel

def getColor(segmantList,poly):

    MPoly = om.MGlobal.getSelectionListByName(poly)
    polyPath = MPoly.getDagPath(0)
    mesh = om.MFnMesh(polyPath)

    shape = mesh.name()
    shadingGrps = cmds.listConnections(shape,type='shadingEngine')
    #Get Connected shader name as string
    shader = cmds.ls(cmds.listConnections(shadingGrps),materials=1)[0]

    length = len(segmantList)


    imgObj = om1.MObject()  
    sel = om1.MSelectionList()  
    om1.MGlobal.getSelectionListByName(shader, sel)  
    sel.getDependNode(0, imgObj)  
    fnThisNode = om1.MFnDependencyNode(imgObj)  
    attr = fnThisNode.attribute( "color" )  

    outColours = om1.MVectorArray()  
    outAlphas = om1.MDoubleArray() 

    uColArray = om1.MDoubleArray()  
    vColArray = om1.MDoubleArray() 
    uColArray.setLength(1)  
    vColArray.setLength(1)  



    for segmant in segmantList:
        location = segmant.location
        vector = om.MVector(location[0],location[1],location[2])
        point = om.MPoint(vector)
        try:
            u,v,w = mesh.getUVAtPoint(point,4)
            uColArray.set(u, 0)  
            vColArray.set(v, 0) 
            omfx.MDynamicsUtil.evalDynamics2dTexture(imgObj, attr, uColArray, vColArray, outColours, outAlphas)  
        except:
            print "Unable to sample current Shading Node"
            return segmantList


        color = outColours[0]
        segmant.color = [color.x,color.y,color.z]


    return segmantList



    

  

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
    shape = cmds.listRelatives(poly, shapes=True)
    shadingGrps = cmds.listConnections(shape[0],type='shadingEngine')
    shaders = cmds.ls(cmds.listConnections(shadingGrps),materials=1)

    color = cmds.listConnections(shaders[0]+'.color')
    outColor = color[0]+'.outColor'
    return outColor



def getFiles(folder, fileTypes = ['obj','fbx']):
    files = []

    for fileType in fileTypes:
        files += (cmds.getFileList(folder=folder, filespec='*.%s' % fileType))
    
    for i in range(len(files)):
        files[i] = '%s\%s' % (folder,files[i])

    
    return files


def addTreeChild(tree, title, widget,expand=False):
    
    title_row = QtWidgets.QTreeWidgetItem()
    label = QtWidgets.QLabel(title)
    
    label.setStyleSheet("QLabel { background-color : #646464; }")


    widget_row = QtWidgets.QTreeWidgetItem()
    title_row = QtWidgets.QTreeWidgetItem(True)
    
    
    tree.addTopLevelItem(title_row)
    title_row.addChild(widget_row)
    
    tree.setItemWidget(title_row,0,label)
    tree.setItemWidget(widget_row,0,widget)
    


    if expand: tree.expandItem(title_row)

def isGroup(node):
    children = node.getChildren()
    for child in children:
        if type(child) is not pymel.core.nodetypes.Transform:
            return False
    return True