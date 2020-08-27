from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import getCppPointer
import maya.OpenMayaUI as omui
from maya import cmds




class controller(object):

    def __init__(self, name):
        self.name = name
        self.widget = None

    def create(self, label, widget, uiScript=None):
        cmds.workspaceControl(self.name, label=label)

        if uiScript:
            cmds.workspaceControl(self.name, e=True, uiScript=uiScript)
        
        self.addWidgetToLayout(widget)
        self.setVisible(True)

    def restore(self, widget):
        self.addWidgetToLayout(widget)

    def addWidgetToLayout(self,widget):
        if widget:
            self.widget = widget
            self.widget.setAttribute(QtCore.Qt.WA_DontCreateNativeAncestors)
            
            WorkspaceController_ptr = long(omui.MQtUtil.findControl(self.name))
            widget_ptr = long(getCppPointer(self.widget)[0])

            omui.MQtUtil.addWidgetToMayaLayout(widget_ptr, WorkspaceController_ptr)

    def exists(self):
        return cmds.workspaceControl(self.name, q=True, exists=True)
    

    def isVisible(self):
        return cmds.workspaceControl(self.name, q=True, visible=True)

    def setVisible(self, visible):
        if visible:
            cmds.workspaceControl(self.name, e=True, restore=True)
        else:
            cmds.workspaceControl(self.name, e=True, visible=True)
    
    def setLabel(self, label):
        cmds.workspaceControl(self.name, e=True, label=label)
    
    def isFloating(self):
        return cmds.workspaceControl(self.name, q=True, floating=True)
    
    def isCollapsed(self):
        return cmds.workspaceControl(self.name, q=True, collapse=True)
    

