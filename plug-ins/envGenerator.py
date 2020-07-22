import maya.api.OpenMaya as om
import maya.api.OpenMayaRender as omr
import maya.api.OpenMayaUI as omui
import maya.cmds as cmds

import envGen.segmants
reload (envGen.segmants)


maya_useNewAPI = True

class envGenerator(omui.MPxLocatorNode):
    TYPE_NAME = "segmantNode"
    TYPE_ID = om.MTypeId(0x0007f7f7)
    DRAW_CLASSIFICATION = "drawdb/geometry/helloworld"
    DRAW_REGISTRANT_ID = "envGenerator"

    

    def __init__(self):
        super(envGenerator, self).__init__()

    @classmethod
    def creator(cls):
        return envGenerator()

    @classmethod
    def intialize(cls):
        pass

class envGenratorCmd(om.MPxCommand):
    COMMAND_NAME ="drawSegmants"
    POLY = ""

    def __init__(self):
        super(envGenratorCmd, self).__init__()
    
    def doIt(self,args):
        
        envGenratorCmd.POLY = args.asString(0)
        segmantDraw.MODE = args.asInt(1)
        segmantDraw.segmants = envGen.segmants.getSegmants(envGenratorCmd.POLY,1)
        cmds.createNode("segmantNode")
        
    

    @classmethod
    def creator(cls):
        return envGenratorCmd()



def printHello():
    return "Hello"


class segmantDraw(omr.MPxDrawOverride):
    NAME = "segmantDraw"
    MODE = 0
    segmants = []
    parent = ""
    def __init__(self, obj):
        super(segmantDraw, self).__init__(obj, None, False)

    def prepareForDraw(self, obj_path, camera_path, frame_context, old_data):
        pass

    def supportedDrawAPIs(self):
        return omr.MRenderer.kAllDevices
    
    def hasUIDrawables(self):
        return True

    def addUIDrawables(self, obj_path, draw_manager, frame_context, data):
        path = obj_path.fullPathName()
        path = path.split("|")
        transform = path[len(path)-1]



        draw_manager.beginDrawable()
        
        if segmantDraw.MODE == 0:
            for s in segmantDraw.segmants:
                draw_manager.point(om.MPoint(s.location))
        else:
            for s in segmantDraw.segmants:
                endPoint = [s.location[0]+s.normal[0], s.location[1]+s.normal[1], s.location[2]+s.normal[2]]
                draw_manager.line(om.MPoint(s.location), om.MPoint(endPoint))

        draw_manager.endDrawable()

        # try:
        #     cmds.parent(transform,segmantDraw.parent)
        # except:
        #     pass

    @classmethod
    def creator(cls, obj):
        return segmantDraw(obj)




def initializePlugin(plugin):

    vendor = "Mohammad Abutahoun"
    version = "1.0.0"

    plugin_fn = om.MFnPlugin(plugin, vendor, version)

    #Initialize Plugin
    try:
        plugin_fn.registerNode(envGenerator.TYPE_NAME,envGenerator.TYPE_ID,envGenerator.creator,envGenerator.intialize,om.MPxNode.kLocatorNode, envGenerator.DRAW_CLASSIFICATION)
    except:
        om.MGlobal.displayError("Failed to register node: {0}".format(envGenerator))


    #Intialize DrawOverride
    try:
        omr.MDrawRegistry.registerDrawOverrideCreator(envGenerator.DRAW_CLASSIFICATION,
                                                      envGenerator.DRAW_REGISTRANT_ID,
                                                      segmantDraw.creator)
    except:
        om.MGlobal.displayError("Failed to register draw override: {0}".format(segmantDraw.NAME))

    #registerCommand
    try:
        plugin_fn.registerCommand(envGenratorCmd.COMMAND_NAME, envGenratorCmd.creator)
    except:
        om.MGlobal.displayError("Failed to register draw Command: {0}".format(envGenratorCmd.COMMAND_NAME))



def uninitializePlugin(plugin):
    plugin_fn = om.MFnPlugin(plugin)

    #Unintialize Command
    try:
        plugin_fn.deregisterCommand(envGenratorCmd.COMMAND_NAME)
    except:
        om.MGlobal.displayError("Failed to deregister draw Command: {0}".format(envGenratorCmd.COMMAND_NAME))

    #Unintialize DrawOverride
    try:
        omr.MDrawRegistry.deregisterDrawOverrideCreator(envGenerator.DRAW_CLASSIFICATION, envGenerator.DRAW_REGISTRANT_ID)
    except:
        om.MGlobal.displayError("Failed to deregister node: {0}".format(envGenerator))

    #Unintialize Plugin
    try:
        plugin_fn.deregisterNode(envGenerator.TYPE_ID)
    except:
        om.MGlobal.displayError("Failed to deregister node: {0}".format(envGenerator))



