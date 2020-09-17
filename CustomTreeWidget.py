from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from maya.api import OpenMaya as om
from maya import cmds
import pymel.core
from functools import partial

import cnt
reload(cnt)

import envGen.randomize
reload(envGen.randomize)

from envGen.randomize import randomizer


import envGen.segments
reload (envGen.segments)



class TreeWidget(QtWidgets.QTreeWidget):
        def __init__(self, parent = None, UI = None):
        
            QtWidgets.QTreeWidget.__init__(self, parent)
            self.UI = UI

        def contextMenuEvent(self, event):
            contextMenu = QtWidgets.QMenu(self)
            addAction = QtWidgets.QAction('Add Base', self)
            contextMenu.addAction(addAction)
            addAction.triggered.connect(self.addItem)


            #create menue at mouse location
            action = contextMenu.exec_(self.viewport().mapToGlobal(event.pos()))
            
        def addItem(self, row = None):
            rows = self.selectedItems()
            accuracy = self.UI.globalSettings.accuracy
            useTexture = self.UI.globalSettings.useTexture
            sampleSize = self.UI.globalSettings.sampleSize
            colorThreshold = self.UI.globalSettings.colorThreshold
            collision = self.UI.globalSettings.collision





            sel = pymel.core.ls(selection=True, transforms=True)


            sections = []
            if len(sel) > 0:
                for item in sel:
                    poly = str(item)
                    if cnt.isGroup(item):
                        newRow = self.TreeWidgetItem(poly=poly,isGroup =True,settings = self.Settings(accuracy,sampleSize,collision,useTexture,0,[0,0,0,0,0,0],[0,0,0,0,0,0],True))
                        if (row): row.addChild(newRow)
                    else:
                        if useTexture:
                            sections = envGen.segments.getsegments(poly,accuracy,sampleSize,useTexture,colorThreshold)
                        
                        newRow = self.TreeWidgetItem(poly=poly, settings = self.Settings(accuracy,sampleSize,collision,useTexture,0,[0,0,0,0,0,0],[0,0,0,0,0,0],True))
                        
                        if (not row):
                            self.insertTopLevelItem(0,newRow)
                            newRow.isItem = False
                        else:
                            for row in rows:
                                row.addChild(newRow)
                                if len(sections) > 1:
                                    newRow.settings.useTexture = True
                                else:
                                    newRow.settings.useTexture = False
                        
                    polyItem_label = self.TreeLabel(poly,newRow)
                    self.setItemWidget(newRow,0,polyItem_label)
                

                    if len(sections) > 1:
                    #Add colors as childs
                        for section in sections:
                            
                            color = QtGui.QColor(section.color)
                            colorRow = self.TreeWidgetItem(section.segments,isItem = False,color =color,settings = self.Settings(accuracy,sampleSize,collision,useTexture,0,[0,0,0,0,0,0],[0,0,0,0,0,0],True))
                            colorRow.setBackgroundColor(0,color)
                            colorLabel =self.TreeLabel("",colorRow)
                            colorLabel.setMargin(10)
                            newRow.addChild(colorRow)
                            self.setItemWidget(colorRow,0,colorLabel)
                            




                #cmds.drawsegments(basePoly,1)

                
            else:
                "Nothing Selected"
        

 

        class TreeWidgetItem(QtWidgets.QTreeWidgetItem):
            def __init__(self,segments=[],isItem = True,poly =None,color = None, isGroup = False,settings = None):
                QtWidgets.QTreeWidgetItem.__init__(self)

            
                self.poly = poly
                self.color = color
                self.isItem = isItem
                self.settings = settings
                self.segments = segments
                self.isGroup = isGroup
                


        class Settings(object):
            def __init__(self,accuracy,sampleSize,collision,useTexture,mode,rotate,scale,fast):
                self.accuracy = accuracy
                self.sampleSize = sampleSize
                self.mode = mode
                self.scale = scale
                self.rotate = rotate
                self.collision = collision
                self.useTexture = useTexture
                self.fast = fast
                

        class TreeLabel(QtWidgets.QLabel):
            def __init__(self, text, row):
                QtWidgets.QLabel.__init__(self, text)

                self.row = row
                self.text = text
                self.tree = self.row.treeWidget()


                # tree = QtWidgets.QTreeWidget()
                # item = QtWidgets.QTreeWidgetItem()
                # item.removeChild()
                # tree.indexOfTopLevelItem(row)
                # #tree.top
                
            def contextMenuEvent(self, event):
                
                contextMenu = QtWidgets.QMenu(self)

                if not self.row.isGroup:
                    add_action = QtWidgets.QAction('Add Selected Item', self)
                    contextMenu.addAction(add_action)
                    add_action.triggered.connect(partial(self.row.treeWidget().addItem,self.row))

                deleteAction = QtWidgets.QAction('Delete', self)
                contextMenu.addAction(deleteAction)
                deleteAction.triggered.connect(partial(self.deleteItem,self.row))

                action = contextMenu.exec_(self.mapToGlobal(event.pos()))
                
                

                
            
            def getText(self):
                return self.text

            def deleteItem(self, row):
                if row.parent() is None:
                    index = self.tree.indexOfTopLevelItem(row)
                    self.tree.takeTopLevelItem(index)
                else:
                    parent = row.parent()
                    parent.removeChild(row)

