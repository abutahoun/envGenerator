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
        self.setMinimumSize(400,700)


        self.createWidgets()
        self.createLayouts()
        self.createConnection()
        self.createWorkspaceControl()

        self.globalSettings = self.GlobalSettings(1,10,True,10,True)

        self.loadingItems = False
        self.isRunning = False



    def createWidgets(self):

        self.progressBar = QtWidgets.QProgressBar()
        self.generate_btn = QtWidgets.QPushButton("Generate")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")



        #TreeWidget
        
        self.genTree = TreeWidget(UI=self)
        self.genTree.setColumnCount(1)
        self.genTree.setHeaderHidden(True)
        self.genTree.setStyleSheet("QTreeWidget { background-color : #494949; }")
        self.genTree.setSelectionMode(self.genTree.ExtendedSelection)
        #self.genTree.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Maximum)


        #Global Settings
        self.gs_UseTexture = QtWidgets.QCheckBox("Create Areas from texture")
        self.gs_colorThreshold = QtWidgets.QDoubleSpinBox()
        self.gs_Accuracy = QtWidgets.QDoubleSpinBox()
        self.gs_sample = QtWidgets.QDoubleSpinBox()
        
        self.gs_Collision = QtWidgets.QCheckBox("Collision Detection")


        self.gs_UseTexture.setChecked(True)
        self.gs_Collision.setChecked(True)
        self.gs_colorThreshold.setValue(10)

        self.gs_Accuracy.setSingleStep(0.1)
        self.gs_Accuracy.setValue(1)
        self.gs_Accuracy.setMinimum(0.1)

        self.gs_sample.setMaximum(100)
        self.gs_sample.setMinimum(0.01)
        self.gs_sample.setValue(10)

        #Item Settings
        self.settings_Label = QtWidgets.QLabel("")
        self.settings_Mode = QtWidgets.QComboBox()
        self.settings_Accuracy = QtWidgets.QDoubleSpinBox()
        self.settings_Sample = QtWidgets.QDoubleSpinBox()

        self.settings_collision = QtWidgets.QCheckBox("Collision Detection")
        self.settings_collision.setChecked(True)

        self.settings_fastCollision = QtWidgets.QCheckBox("Fast Collision Detection")
        self.settings_fastCollision.setChecked(True)

        self.settings_Accuracy.setSingleStep(0.1)
        self.settings_Accuracy.setValue(1)
        self.settings_Accuracy.setMinimum(0.1)

        self.settings_Sample.setMaximum(100)
        self.settings_Sample.setMinimum(0.01)

        self.settings_Mode.addItem("Scatter",userData= 0)
        self.settings_Mode.addItem("Tiles",userData= 1)

        #Rotate SpinBoxs
        self.spinBox_R = []
        for i in range(6):
            spinBox = QtWidgets.QDoubleSpinBox()
            spinBox.valueChanged.connect(self.itemSettingsChanged)
            self.spinBox_R.append(spinBox)

        #scale SpinBoxes
        self.spinBox_S = []
        for i in range(6):
            spinBox = QtWidgets.QDoubleSpinBox()
            spinBox.setSingleStep(0.1)
            spinBox.valueChanged.connect(self.itemSettingsChanged)
            self.spinBox_S.append(spinBox)


        


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
        gFrom_layout.addRow(self.gs_Collision)
        gFrom_layout.addRow(QtWidgets.QSplitter())
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
        group_genTree.setMinimumHeight(600) #set GenTree Height

        #Item_Settings


        group_itemSettings_1 = QtWidgets.QGroupBox("")
        box_itemSettings_1 = QtWidgets.QHBoxLayout()
        box_itemSettings_1.addWidget(QtWidgets.QLabel("Accuracy: "))
        box_itemSettings_1.addWidget(self.settings_Accuracy)
        box_itemSettings_1.addWidget(QtWidgets.QLabel("Sample%: "))
        box_itemSettings_1.addWidget(self.settings_Sample)
        box_itemSettings_1.addStretch()
        box_itemSettings_1.addWidget(QtWidgets.QLabel("Mode: "))
        box_itemSettings_1.addWidget(self.settings_Mode)

        settingForm_layout = QtWidgets.QFormLayout()
        settingForm_layout.addRow("",box_itemSettings_1)
        settingForm_layout.addRow("",self.settings_collision)
        settingForm_layout.addRow("",self.settings_fastCollision)

        setting_Layout.addLayout(settingForm_layout)

        #Rotate 
        group_itemSettings_R = QtWidgets.QGroupBox("Random Rotation Range")
        group_itemSettings_R_X = QtWidgets.QGroupBox("X")
        group_itemSettings_R_Y = QtWidgets.QGroupBox("Y")
        group_itemSettings_R_Z = QtWidgets.QGroupBox("Z")
        box_itemSettings_R_X = QtWidgets.QVBoxLayout()
        box_itemSettings_R_Y = QtWidgets.QVBoxLayout()
        box_itemSettings_R_Z = QtWidgets.QVBoxLayout()
        box_itemSettings_R = QtWidgets.QHBoxLayout()

        group_itemSettings_R_X.setLayout(box_itemSettings_R_X)
        group_itemSettings_R_Y.setLayout(box_itemSettings_R_Y)
        group_itemSettings_R_Z.setLayout(box_itemSettings_R_Z)
        box_itemSettings_R.addWidget(group_itemSettings_R_X)
        box_itemSettings_R.addWidget(group_itemSettings_R_Y)
        box_itemSettings_R.addWidget(group_itemSettings_R_Z)
        box_itemSettings_R.addStretch()
        box_itemSettings_R_X.addWidget(QtWidgets.QLabel("+"))
        box_itemSettings_R_X.addWidget(self.spinBox_R[0])
        box_itemSettings_R_X.addWidget(QtWidgets.QLabel("-"))
        box_itemSettings_R_X.addWidget(self.spinBox_R[1] )
        box_itemSettings_R_Y.addWidget(QtWidgets.QLabel("+"))
        box_itemSettings_R_Y.addWidget(self.spinBox_R[2])
        box_itemSettings_R_Y.addWidget(QtWidgets.QLabel("-"))
        box_itemSettings_R_Y.addWidget(self.spinBox_R[3])
        box_itemSettings_R_Z.addWidget(QtWidgets.QLabel("+"))
        box_itemSettings_R_Z.addWidget(self.spinBox_R[4])
        box_itemSettings_R_Z.addWidget(QtWidgets.QLabel("-"))
        box_itemSettings_R_Z.addWidget(self.spinBox_R[5])

        #Scale
        group_itemSettings_S = QtWidgets.QGroupBox("Random Scale Range")
        group_itemSettings_S_X = QtWidgets.QGroupBox("X")
        group_itemSettings_S_Y = QtWidgets.QGroupBox("Y")
        group_itemSettings_S_Z = QtWidgets.QGroupBox("Z")
        box_itemSettings_S_X = QtWidgets.QVBoxLayout()
        box_itemSettings_S_Y = QtWidgets.QVBoxLayout()
        box_itemSettings_S_Z = QtWidgets.QVBoxLayout()
        box_itemSettings_S = QtWidgets.QHBoxLayout()

        group_itemSettings_S_X.setLayout(box_itemSettings_S_X)
        group_itemSettings_S_Y.setLayout(box_itemSettings_S_Y)
        group_itemSettings_S_Z.setLayout(box_itemSettings_S_Z)
        box_itemSettings_S.addWidget(group_itemSettings_S_X)
        box_itemSettings_S.addWidget(group_itemSettings_S_Y)
        box_itemSettings_S.addWidget(group_itemSettings_S_Z)
        box_itemSettings_S.addStretch()
        box_itemSettings_S_X.addWidget(QtWidgets.QLabel("+"))
        box_itemSettings_S_X.addWidget(self.spinBox_S[0])
        box_itemSettings_S_X.addWidget(QtWidgets.QLabel("-"))
        box_itemSettings_S_X.addWidget(self.spinBox_S[1] )
        box_itemSettings_S_Y.addWidget(QtWidgets.QLabel("+"))
        box_itemSettings_S_Y.addWidget(self.spinBox_S[2])
        box_itemSettings_S_Y.addWidget(QtWidgets.QLabel("-"))
        box_itemSettings_S_Y.addWidget(self.spinBox_S[3])
        box_itemSettings_S_Z.addWidget(QtWidgets.QLabel("+"))
        box_itemSettings_S_Z.addWidget(self.spinBox_S[4])
        box_itemSettings_S_Z.addWidget(QtWidgets.QLabel("-"))
        box_itemSettings_S_Z.addWidget(self.spinBox_S[5])

        
        




        group_itemSettings_R.setStyleSheet("QGroupBox{border:2px solid gray;border-radius:5px;margin-top: 1ex;} QGroupBox::title{subcontrol-origin: margin;subcontrol-position:top left;padding:0 3px;}")
        group_itemSettings_S.setStyleSheet("QGroupBox{border:2px solid gray;border-radius:5px;margin-top: 1ex;} QGroupBox::title{subcontrol-origin: margin;subcontrol-position:top left;padding:0 3px;}")


        group_itemSettings_1.setLayout(setting_Layout)
        group_itemSettings_R.setLayout(box_itemSettings_R)
        group_itemSettings_S.setLayout(box_itemSettings_S)

        settings_Layout = QtWidgets.QVBoxLayout()
        settings_Layout.addWidget(group_itemSettings_1)
        settings_Layout.addWidget(group_itemSettings_R)
        settings_Layout.addWidget(group_itemSettings_S)
        self.settings_group = QtWidgets.QGroupBox()
        self.settings_group.setLayout(settings_Layout)
        self.settings_group.setEnabled(False)

        #Main Tree Childs
        cnt.addTreeChild(main_tree,"Global Settings",global_group,expand=True)
        cnt.addTreeChild(main_tree,"GenTree",group_genTree,expand=True)
        cnt.addTreeChild(main_tree,"Settings",self.settings_group,expand=True)

        
        
        bottom_layout = QtWidgets.QVBoxLayout()
        bottom_layout.addWidget(self.progressBar)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.generate_btn)
        

        bottom_layout.addLayout(button_layout)


        #main_Layout.addLayout(form_layout)
        main_Layout.addWidget(main_tree)
        main_Layout.addLayout(bottom_layout)


    def createConnection(self):
        self.generate_btn.clicked.connect(self.generate)
        self.cancel_btn.clicked.connect(self.cancel)
        self.gs_UseTexture.toggled.connect(self.globalSettingsChanged)
        self.gs_Accuracy.valueChanged.connect(self.globalSettingsChanged)
        self.gs_sample.valueChanged.connect(self.globalSettingsChanged)
        self.gs_colorThreshold.valueChanged.connect(self.globalSettingsChanged)
        self.gs_Collision.toggled.connect(self.globalSettingsChanged)

        self.genTree.itemSelectionChanged.connect(self.genTree_selectionChanged)
        self.settings_Mode.currentIndexChanged.connect(self.itemSettingsChanged)
        self.settings_Accuracy.valueChanged.connect(self.itemSettingsChanged)
        self.settings_Sample.valueChanged.connect(self.itemSettingsChanged)
        self.settings_collision.toggled.connect(self.itemSettingsChanged)
        self.settings_fastCollision.toggled.connect(self.itemSettingsChanged)

    def createWorkspaceControl(self):
        self.workspaceControlInstance = controller(self.getWorksapceControlName())
        self.workspaceControlInstance.create(self.WINDOW_TITLE, self)





#region Slots
    def generate(self):

        #loop through top level items
        for i in range (self.genTree.topLevelItemCount()):
            
            widgetItem = self.genTree.topLevelItem(i)
            treeLabel = self.genTree.itemWidget(widgetItem,0)
            randomizer(widgetItem, self.globalSettings)
    
    def cancel(self):
        self.isRunning = False


    def globalSettingsChanged(self):
        self.globalSettings.useTexture = self.gs_UseTexture.isChecked()
        self.globalSettings.accuracy = self.gs_Accuracy.value()
        self.globalSettings.colorThreshold = self.gs_colorThreshold.value()
        self.globalSettings.sampleSize = self.gs_sample.value()
        self.globalSettings.collision = self.gs_Collision.isChecked()
        


    def genTree_selectionChanged(self):
        if len(self.genTree.selectedItems()) == 0:
            self.settings_group.setEnabled(False)
        else:
            item = self.genTree.selectedItems()[0]
            self.settings_Label.setText(item.poly)
            self.loadItemSettings(item)
            self.settings_group.setEnabled(True)
        


    def itemSettingsChanged(self):
        if self.loadingItems: return
        if len(self.genTree.selectedItems()) <= 0: return
        
        for item in self.genTree.selectedItems():
            item.settings.mode = self.settings_Mode.currentData()
            item.settings.accuracy = self.settings_Accuracy.value()
            item.settings.sampleSize = self.settings_Sample.value()
            item.settings.collision = self.settings_collision.isChecked()
            item.settings.fast = self.settings_fastCollision.isChecked()
            
            rotate = []
            scale = []
            for i in range(6):
                rotate.append(self.spinBox_R[i].value())
                scale.append(self.spinBox_S[i].value())
            item.settings.rotate = rotate[:]
            item.settings.scale = scale[:]

            

#endregion

    def loadItemSettings(self, item):
        self.loadingItems = True
        index = self.settings_Mode.findData(item.settings.mode)
        self.settings_Mode.setCurrentIndex(index)

        self.settings_Accuracy.setValue(item.settings.accuracy)
        self.settings_Sample.setValue(item.settings.sampleSize)
        self.settings_collision.setChecked(item.settings.collision)
        self.settings_fastCollision.setChecked(item.settings.fast)

        for i in range(6):
            self.spinBox_R[i].setValue(item.settings.rotate[i])
            self.spinBox_S[i].setValue(item.settings.scale[i])

        self.loadingItems = False


    class GlobalSettings(object):
        def __init__(self, accuracy,sampleSize,useTexture,colorThreshold,collision):
            self.accuracy = accuracy
            self.sampleSize = sampleSize
            self.useTexture = useTexture
            self.colorThreshold = colorThreshold
            self.collision = collision










#ToDo


#Use models from folder
#Add option to depends on faces and vertex
#Tile Mode














