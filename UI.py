#region imports

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance
from functools import partial
import maya.OpenMayaUI as omui
from maya import cmds

from workspace import controller

import envGen.cnt
import envGen.cnt as cnt
reload(envGen.cnt)

import envGen.CustomTreeWidget
reload(envGen.CustomTreeWidget)
from envGen.CustomTreeWidget import TreeWidget


import envGen.randomize
reload(envGen.randomize)

from envGen.randomize import randomizer

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

        self.globalSettings = GlobalSettings()
        self.globalSettings.useTexture=False

    def createWidgets(self):
        

        self.generate_btn = QtWidgets.QPushButton("Generate")

        

        #TreeWidget 
        self.genTree = TreeWidget()
        self.genTree.setColumnCount(1)
        self.genTree.setHeaderHidden(True)

        self.genTree.setStyleSheet("QTreeWidget { background-color : #494949; }")

        #Global Settings
        self.gs_UseTexture = QtWidgets.QCheckBox()
        self.gs_Density = QtWidgets.QLineEdit()

        #Item Settings
        self.itemSettings_Label = QtWidgets.QLabel("")
        self.itemSettings_Mode = QtWidgets.QComboBox()


        self.itemSettings_Mode.addItem("Scatter",userData= 0)
        self.itemSettings_Mode.addItem("Tiles",userData= 1)

        



    def createLayouts(self):
        '''
        main_Layout
        |_____main_tree
              |_____Global Settings
              |_____GenTree
              |_____Item Settings
        |_____buttonLayout


        '''

        main_Layout = QtWidgets.QVBoxLayout(self)

        gSetting_Layout = QtWidgets.QVBoxLayout(self)
        main_tree = QtWidgets.QTreeWidget()
        setting_Layout = QtWidgets.QVBoxLayout(self)

        #Main tree Properties
        main_tree.setHeaderHidden(True) 
        main_tree.setIndentation(0)
        main_tree.setRootIsDecorated(True)


        #Global_Settings 
        global_formLayout = QtWidgets.QFormLayout()
        global_formLayout.addRow("Use Textures: ", self.gs_UseTexture)
        global_formLayout.addRow("Density: ", self.gs_Density)
        global_group = QtWidgets.QGroupBox()
        global_group.setLayout(global_formLayout)


        #Item_Settings
        settings_formLayout = QtWidgets.QFormLayout()
        settings_formLayout.addRow("", self.itemSettings_Label)
        settings_formLayout.addRow("Mode: ", self.itemSettings_Mode)


        settings_group = QtWidgets.QGroupBox()
        settings_group.setLayout(settings_formLayout)

        
        #Main Tree Childs
        cnt.addTreeChild(main_tree,"Global Settings",global_group,expand=True)
        cnt.addTreeChild(main_tree,"GenTree",self.genTree,expand=True)
        cnt.addTreeChild(main_tree,"Settings",settings_group,expand=True)



        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.generate_btn)

        
        

        #main_Layout.addLayout(form_layout)
        main_Layout.addWidget(main_tree)
        main_Layout.addLayout(button_layout)
        

    def createConnection(self):
        self.generate_btn.clicked.connect(self.generate)
        self.gs_UseTexture.toggled.connect(self.useTextureToggled)
        self.genTree.itemSelectionChanged.connect(self.genTree_selectionChanged)
        self.itemSettings_Mode.currentIndexChanged.connect(self.itemSettingsChanged)

    def createWorkspaceControl(self):
        self.workspaceControlInstance = controller(self.getWorksapceControlName())
        self.workspaceControlInstance.create(self.WINDOW_TITLE, self)

    


        







#region Slots
    def generate(self):
 
        #loop through top level items
        for i in range (self.treeWidget.topLevelItemCount()):
            widgetItem = self.treeWidget.topLevelItem(i)
            treeLabel = self.treeWidget.itemWidget(widgetItem,0)

            
            #envGen.randomize.randomize(widgetItem, self.globalSettings)
            randomizer(widgetItem, self.globalSettings)
    
    def useTextureToggled(self):
        print self.gs_UseTexture.isChecked()
        self.globalSettings.useTexture = self.gs_UseTexture.isChecked()

    def genTree_selectionChanged(self):

        item = self.genTree.selectedItems()[0]
        self.itemSettings_Label.setText(item.poly)
        self.loadItemSettings(item)


    def itemSettingsChanged(self):

        item = self.genTree.selectedItems()[0]
        item.settings.mode = self.itemSettings_Mode.currentData()
        
    

                

#endregion

    def loadItemSettings(self, item):
        index = self.itemSettings_Mode.findData(item.settings.mode)
        self.itemSettings_Mode.setCurrentIndex(index)

    class GlobalSettings(object):
        def __init__(self):
            self.useTexture = False



    


            




#ToDo


#Use models from folder
#Add option to depends on faces and vertex
#Tile Mode














