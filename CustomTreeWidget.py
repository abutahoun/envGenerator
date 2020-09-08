from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from maya import cmds

from functools import partial

import envGen.randomize
reload(envGen.randomize)

from envGen.randomize import randomizer


import envGen.segments
reload (envGen.segments)



class TreeWidget(QtWidgets.QTreeWidget):
        def __init__(self, parent = None):
        
            QtWidgets.QTreeWidget.__init__(self, parent)
            self.useTextue = False


        def contextMenuEvent(self, event):
            contextMenu = QtWidgets.QMenu(self)
            addAction = QtWidgets.QAction('Add Base', self)
            contextMenu.addAction(addAction)
            addAction.triggered.connect(self.addItem)


            #create menue at mouse location
            action = contextMenu.exec_(self.viewport().mapToGlobal(event.pos()))
            
        def addItem(self, row = None):
            sel = cmds.ls(selection = True)
            sections = []
            #if len(sel) > 0:
            for poly in sel:
                if self.useTextue:
                    sections = envGen.segments.getsegments(poly,1,True)
                
                newRow = self.TreeWidgetItem(poly=poly)
                
                if (not row):
                    self.insertTopLevelItem(0,newRow)
                    newRow.isItem = False
                else:
                    row.addChild(newRow)
                    if len(sections) > 1:newRow.useTexture = True

                polyItem_label = self.TreeLabel(poly,newRow)
                self.setItemWidget(newRow,0,polyItem_label)
        

                if len(sections) > 1:
                #Add colors as childs
                    for section in sections:
                        
                        color = QtGui.QColor(section.color)
                        colorRow = self.TreeWidgetItem(section.segments,isItem = False,color =color)
                        colorRow.setBackgroundColor(0,color)
                        colorLabel =self.TreeLabel("",colorRow)
                        colorLabel.setMargin(10)
                        newRow.addChild(colorRow)
                        self.setItemWidget(colorRow,0,colorLabel)
                        




                #cmds.drawsegments(basePoly,1)

                
            else:
                "Nothing Selected"
        

        def deleteItem(self,row):
            pass

        class TreeWidgetItem(QtWidgets.QTreeWidgetItem):
            def __init__(self,segments=[],isItem = True,poly =None,color = None,useTexture = False):
                QtWidgets.QTreeWidgetItem.__init__(self)

            
                self.poly = poly
                self.color = color
                self.isItem = isItem
                self.useTexture = useTexture
                self.settings = self.Settings()

                


            class Settings(object):
                def __init__(self):
                    self.mode = 0
                

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
                    self.tree.takeTopLevelItem(0)
                else:
                    parent = row.parent()
                    parent.removeChild(row)

