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

        self.globalSettings = self.GlobalSettings()
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

        #Item Settings
        self.settings_Label = QtWidgets.QLabel("")
        self.settings_Mode = QtWidgets.QComboBox()
        self.settings_Density = QtWidgets.QDoubleSpinBox()
        self.settings_Density.setSingleStep(0.1)


        self.settings_Mode.addItem("Scatter",userData= 0)
        self.settings_Mode.addItem("Tiles",userData= 1)

        #follow Normals
        #Rotation
        #Scale
        #transformation
        #Genration Density

        



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
        gFrom_layout = QtWidgets.QFormLayout()
        gFrom_layout.addRow("Use Texture: ",self.gs_UseTexture)
        gSetting_Layout.addLayout(gFrom_layout)

        global_group = QtWidgets.QGroupBox()
        global_group.setLayout(gSetting_Layout)


        #Item_Settings
        settingForm_layout = QtWidgets.QFormLayout()
        settingForm_layout.addRow("Accuracy: ",self.settings_Density)
        settingForm_layout.addRow("Mode: ",self.settings_Mode)
        setting_Layout.addLayout(settingForm_layout)


        settings_group = QtWidgets.QGroupBox()
        settings_group.setLayout(setting_Layout)

        
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
        self.settings_Mode.currentIndexChanged.connect(self.itemSettingsChanged)

    def createWorkspaceControl(self):
        self.workspaceControlInstance = controller(self.getWorksapceControlName())
        self.workspaceControlInstance.create(self.WINDOW_TITLE, self)

    


        







#region Slots
    def generate(self):

        #loop through top level items
        for i in range (self.genTree.topLevelItemCount()):
            widgetItem = self.genTree.topLevelItem(i)
            treeLabel = self.genTree.itemWidget(widgetItem,0)

            
            #envGen.randomize.randomize(widgetItem, self.globalSettings)
            randomizer(widgetItem, self.globalSettings)

    
    def useTextureToggled(self):
        print self.gs_UseTexture.isChecked()
        self.globalSettings.useTexture = self.gs_UseTexture.isChecked()

    def genTree_selectionChanged(self):

        item = self.genTree.selectedItems()[0]
        self.settings_Label.setText(item.poly)
        self.loadItemSettings(item)


    def itemSettingsChanged(self):

        item = self.genTree.selectedItems()[0]
        item.settings.mode = self.settings_Mode.currentData()
        
    

                

#endregion

    def loadItemSettings(self, item):
        index = self.settings_Mode.findData(item.settings.mode)
        self.settings_Mode.setCurrentIndex(index)

    class GlobalSettings(object):
        def __init__(self):
            self.useTexture = False



    


            




#ToDo


#Use models from folder
#Add option to depends on faces and vertex
#Tile Mode














