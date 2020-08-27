#region imports

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance
from functools import partial
import maya.OpenMayaUI as omui
from maya import cmds

from workspace import controller

import envGen.CustomTreeWidget
reload(envGen.CustomTreeWidget)
from envGen.CustomTreeWidget import TreeWidget

#endregion


class envGenUI(QtWidgets.QWidget):

    WINDOW_TITLE = "Environment Genrator"
    UI_NAME = "envGenUI"

    @classmethod
    def getWorksapceControlName(cls):
        return "{0}WorkSpaceControl".format(cls.UI_NAME)

    def __init__(self):
        super(envGenUI,self).__init__()

        self.setObjectName(self.__class__.UI_NAME)
        self.setMinimumSize(400,100)


        self.createWidgets()
        self.createLayouts()
        self.createConnection()
        self.createWorkspaceControl()


    def createWidgets(self):
        

        self.generate_btn = QtWidgets.QPushButton("Generate")

        

        #TreeWidget
        self.treeWidget = TreeWidget()
        self.treeWidget.setColumnCount(1)
        self.treeWidget.setHeaderHidden(True)



    def createLayouts(self):
        tree_Main = QtWidgets.QTreeWidget()


        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.generate_btn)

        main_Layout = QtWidgets.QVBoxLayout(self)
        #main_Layout.addLayout(form_layout)
        main_Layout.addWidget(self.treeWidget)
        main_Layout.addLayout(button_layout)
        

    def createConnection(self):
        self.generate_btn.clicked.connect(self.generate)

    def createWorkspaceControl(self):
        self.workspaceControlInstance = controller(self.getWorksapceControlName())
        self.workspaceControlInstance.create(self.WINDOW_TITLE, self)




#region Slots
    def generate(self):
 
        #loop through top level items
        for i in range (self.treeWidget.topLevelItemCount()):
            widgetItem = self.treeWidget.topLevelItem(i)
            treeLabel = self.treeWidget.itemWidget(widgetItem,0)
            #self.getChildren(widgetItem)
            
            envGen.randomize.randomize(widgetItem)


    def getChildren(self,widgetItem):
        #Get all children recursively
        children = []
        for j in range (widgetItem.childCount()):
                child = widgetItem.child(j)
                treeLabel = self.treeWidget.itemWidget(child,0)
                if(child.active):children.append(treeLabel.text)
                self.getChildren(child)

        if len(children) > 0:
            while(widgetItem.segment>0):
                result = envGen.randomize.randomize(widgetItem.segments,widgetItem.bboxes,children[0])
                widgetItem.segments = result.segments
                widgetItem.bboxes.append(result.bbox)

#endregion




    


            




#ToDo

#Create Areas using Texture
#Use models from folder
#Add option to depends on faces and vertex
#Create Randomization Tree
#Build Interface
#Tile Mode














