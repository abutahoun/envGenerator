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
        self.setMinimumSize(400,600)


        self.createWidgets()
        self.createLayouts()
        self.createConnection()
        self.createWorkspaceControl()

        self.globalSettings = self.GlobalSettings(1,10,True,10)
        



    def createWidgets(self):


        self.generate_btn = QtWidgets.QPushButton("Generate")



        #TreeWidget
        
        self.genTree = TreeWidget(UI=self)
        self.genTree.setColumnCount(1)
        self.genTree.setHeaderHidden(True)
        self.genTree.setStyleSheet("QTreeWidget { background-color : #494949; }")
        #self.genTree.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Maximum)


        #Global Settings
        self.gs_UseTexture = QtWidgets.QCheckBox("Create Areas from texture")
        self.gs_colorThreshold = QtWidgets.QDoubleSpinBox()
        self.gs_Accuracy = QtWidgets.QDoubleSpinBox()
        self.gs_sample = QtWidgets.QDoubleSpinBox()

        #self.gs_UseTexture.setChecked(True)
        
        self.gs_colorThreshold.setValue(10)

        self.gs_Accuracy.setSingleStep(0.1)
        self.gs_Accuracy.setValue(1)
        self.gs_Accuracy.setMinimum(0.1)

        self.gs_sample.setMaximum(100)
        self.gs_sample.setMinimum(1)
        self.gs_sample.setValue(10)

        #Item Settings
        self.settings_Label = QtWidgets.QLabel("")
        self.settings_Mode = QtWidgets.QComboBox()
        self.settings_Accuracy = QtWidgets.QDoubleSpinBox()


        self.settings_Accuracy.setSingleStep(0.1)
        self.settings_Accuracy.setValue(1)
        self.settings_Accuracy.setMinimum(0.1)

        self.settings_Mode.addItem("Scatter",userData= 0)
        self.settings_Mode.addItem("Tiles",userData= 1)

        #follow Normals
        #Rotation
        #Scale
        #transformation
        #Genration Density





    def createLayouts(self):
        '''
        QVBoxLayout() main_Layout
        |_____QTreeWidget() main_tree
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

        group_accuracy = QtWidgets.QGroupBox("")
        box_accuracy = QtWidgets.QHBoxLayout()
        box_accuracy.addWidget(QtWidgets.QLabel("Accuracy"))
        box_accuracy.addWidget(self.gs_Accuracy)
        box_accuracy.addWidget(QtWidgets.QLabel("Sample%"))
        box_accuracy.addWidget(self.gs_sample)
        box_accuracy.addStretch()
        group_accuracy.setLayout(box_accuracy)


        group_areas = QtWidgets.QGroupBox("")
        gFrom_layout = QtWidgets.QFormLayout()
        gFrom_layout.addRow(self.gs_UseTexture)
        gFrom_layout.addRow("Color Threshold: ",self.gs_colorThreshold)
        group_areas.setLayout(gFrom_layout)
        


        global_VLayout = QtWidgets.QVBoxLayout()
        global_VLayout.addWidget(group_accuracy)
        global_VLayout.addWidget(group_areas)
        
        global_group = QtWidgets.QGroupBox()
        global_group.setLayout(global_VLayout)

        #genTree
        gnTreeBox = QtWidgets.QVBoxLayout()
        gnTreeBox.addWidget(self.genTree)
        group_genTree = QtWidgets.QGroupBox()
        group_genTree.setLayout(gnTreeBox)
        group_genTree.setMinimumHeight(900)

        #Item_Settings
        settingForm_layout = QtWidgets.QFormLayout()
        settingForm_layout.addRow("Accuracy: ",self.settings_Accuracy)
        settingForm_layout.addRow("Mode: ",self.settings_Mode)
        setting_Layout.addLayout(settingForm_layout)


        settings_group = QtWidgets.QGroupBox()
        settings_group.setLayout(setting_Layout)


        #Main Tree Childs
        cnt.addTreeChild(main_tree,"Global Settings",global_group,expand=True)
        cnt.addTreeChild(main_tree,"GenTree",group_genTree,expand=True)
        cnt.addTreeChild(main_tree,"Settings",settings_group,expand=True)

        
        

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.generate_btn)




        #main_Layout.addLayout(form_layout)
        main_Layout.addWidget(main_tree)
        main_Layout.addLayout(button_layout)


    def createConnection(self):
        self.generate_btn.clicked.connect(self.generate)
        self.gs_UseTexture.toggled.connect(self.globalSettingsChanged)
        self.gs_Accuracy.valueChanged.connect(self.globalSettingsChanged)
        self.gs_sample.valueChanged.connect(self.globalSettingsChanged)
        self.gs_colorThreshold.valueChanged.connect(self.globalSettingsChanged)


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


    def globalSettingsChanged(self):
        print "changed"
        self.globalSettings.useTexture = self.gs_UseTexture.isChecked()
        self.globalSettings.accuracy = self.gs_Accuracy.value()
        self.globalSettings.colorThreshold = self.gs_colorThreshold.value()
        self.globalSettings.sampleSize = self.gs_sample.value()

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
        def __init__(self, accuracy,sampleSize,useTexture,colorThreshold):
            self.accuracy = accuracy
            self.sampleSize = sampleSize
            self.useTexture = useTexture
            self.colorThreshold = colorThreshold










#ToDo


#Use models from folder
#Add option to depends on faces and vertex
#Tile Mode














