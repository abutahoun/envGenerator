#region imports

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance
from functools import partial
import maya.OpenMayaUI as omui
from maya import cmds

import envGen.segments
reload (envGen.segments)

import envGen.randomize
reload(envGen.randomize)

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
        self.treeWidget = self.TreeWidget()
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

    def setContextMenu(self, item):
        polyItem_label.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        polyItem_label.customContextMenuRequested.connect(partial(self.on_context_menu,item))
        

    def on_context_menu(self, pos):
        # show context menu
        self.popMenu.exec_(self.treeWidget.mapToGlobal(pos))

    

    def on_item_menu(self,pos):
        self.itemMenu.exec_(self.mapToGlobal(pos))
        

    
    def deleteItem(self):
        pass



    def generate(self):
 
        #loop through top level items
        for i in range (self.treeWidget.topLevelItemCount()):
            widgetItem = self.treeWidget.topLevelItem(i)
            treeLabel = self.treeWidget.itemWidget(widgetItem,0)
            print treeLabel.text
            self.getChildren(widgetItem)


            

    def getChildren(self,widgetItem):
        #Get all children recursively
        children = []
        for j in range (widgetItem.childCount()):
                child = widgetItem.child(j)
                treeLabel = self.treeWidget.itemWidget(child,0)
                if(child.active):children.append(treeLabel.text)
                self.getChildren(child)

        if len(children) > 0:
            envGen.randomize.randomize(widgetItem.segments,children)
        





    class TreeWidget(QtWidgets.QTreeWidget):
        def __init__(self, parent = None):
        
            QtWidgets.QTreeWidget.__init__(self, parent)
 

        def contextMenuEvent(self, event):
            contextMenu = QtWidgets.QMenu(self)
            newAction = QtWidgets.QAction('Add Base', self)
            contextMenu.addAction(newAction)
            newAction.triggered.connect(self.selectBasePoly)

            #create menue at mouse location
            action = contextMenu.exec_(self.viewport().mapToGlobal(event.pos()))
            
        def selectBasePoly(self):
            sel = cmds.ls(selection = True)
            
            if len(sel) > 0:
                basePoly = sel[0]
                row = self.TreeWidgetItem(active = False)
                polyItem_label = self.TreeLabel(sel[0],row)

                self.insertTopLevelItem(0,row)
                self.setItemWidget(row,0,polyItem_label)

                segmentsDict = envGen.segments.getsegments(basePoly,1,True)
                

                #Add colors as childs
                for key in segmentsDict:
                    colorRow = self.TreeWidgetItem(segmentsDict[key],active = False)
                    color = QtGui.QColor(key)
                    colorRow.setBackgroundColor(0,color)
                    colorLabel =self.TreeLabel(key,colorRow)
                    row.addChild(colorRow)
                    self.setItemWidget(colorRow,0,colorLabel)




                #cmds.drawsegments(basePoly,1)

                
            else:
                "Nothing Selected"
        

        class TreeWidgetItem(QtWidgets.QTreeWidgetItem):
            def __init__(self,segments=[],active = True,text ="test"):
                QtWidgets.QTreeWidgetItem.__init__(self)

                self.active = active
                self.text = text
                self.segments = segments

        class TreeLabel(QtWidgets.QLabel):
            def __init__(self, text, row):
                QtWidgets.QLabel.__init__(self, text)

                self.row = row
                self.text = text
                
            def contextMenuEvent(self, event):
                contextMenu = QtWidgets.QMenu(self)
                add_action = QtWidgets.QAction('Add Selected Item', self)
                contextMenu.addAction(add_action)
                add_action.triggered.connect(self.addItem)


                action = contextMenu.exec_(self.mapToGlobal(event.pos()))

            def addItem(self):
                sel = cmds.ls(selection = True)
                
                if len(sel) > 0:
                    poly = sel[0]
                    newRow = self.row.treeWidget().TreeWidgetItem()
                    polyItem_label = self.row.treeWidget().TreeLabel(poly,newRow)
                    self.row.addChild(newRow)
                    self.row.treeWidget().setItemWidget(newRow,0,polyItem_label)
                    
                    
                else:
                    "Nothing Selected"
            
            def getText(self):
                return self.text


            




#ToDo

#Create Areas using Texture
#Use models from folder
#Add option to depends on faces and vertex
#Create Randomization Tree
#Build Interface
#Tile Mode














