#region imports

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance
from functools import partial
import maya.OpenMayaUI as omui
from maya import cmds


import envGen.CustomTreeWidget
reload(envGen.CustomTreeWidget)
from envGen.CustomTreeWidget import TreeWidget

#endregion

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr),QtWidgets.QWidget)

class envGenWindow(QtWidgets.QWidget):

    dlg_instance = None

    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = envGenWindow()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()


    def __init__(self, parent=maya_main_window()):
        super(envGenWindow, self).__init__(parent)

        self.setWindowTitle("EnvGen")
        self.setMinimumWidth(600)
        self.setWindowFlags(QtCore.Qt.WindowType.Window)

        self.createWidgets()
        self.createLayouts()
        self.createConnection()


    def createWidgets(self):
        
        self.basePoly_label = QtWidgets.QLabel("test")
        self.addBase_btn = QtWidgets.QPushButton("Select Base Poly")
        self.generate_btn = QtWidgets.QPushButton("Generate")

        #TreeWidget
        self.treeWidget = TreeWidget()
        self.treeWidget.setColumnCount(3)
    





    def createLayouts(self):
        form_layout = QtWidgets.QFormLayout()

        basePoly_layout = QtWidgets.QHBoxLayout()
        basePoly_layout.addStretch()
        basePoly_layout.addWidget(self.addBase_btn)



        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.generate_btn)

        main_Layout = QtWidgets.QVBoxLayout(self)
        main_Layout.addLayout(form_layout)
        main_Layout.addWidget(self.treeWidget)
        main_Layout.addLayout(button_layout)
        




    def createConnection(self):
        self.generate_btn.clicked.connect(self.generate)


    



    def polyItemClicked(self):
        pass

        


    

    def on_item_menu(self,pos):
        self.itemMenu.exec_(self.mapToGlobal(pos))
        

    
    def deleteItem(self):
        pass



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





    


            




#ToDo

#Create Areas using Texture
#Use models from folder
#Add option to depends on faces and vertex
#Create Randomization Tree
#Build Interface
#Tile Mode














