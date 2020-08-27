from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from maya import cmds

from functools import partial

import envGen.randomize
reload(envGen.randomize)


import envGen.segments
reload (envGen.segments)



class TreeWidget(QtWidgets.QTreeWidget):
        def __init__(self, parent = None):
        
            QtWidgets.QTreeWidget.__init__(self, parent)
 

        def contextMenuEvent(self, event):
            contextMenu = QtWidgets.QMenu(self)
            newAction = QtWidgets.QAction('Add Base', self)
            contextMenu.addAction(newAction)
            newAction.triggered.connect(self.addItem)

            #create menue at mouse location
            action = contextMenu.exec_(self.viewport().mapToGlobal(event.pos()))
            
        def addItem(self, row = None):
            sel = cmds.ls(selection = True)
            if len(sel) > 0:
                poly = sel[0]
                sections = envGen.segments.getsegments(poly,1,True)
                newRow = self.TreeWidgetItem(poly=poly)

                if (not row):
                    self.insertTopLevelItem(0,newRow)
                    newRow.isItem = False
                else:
                    row.addChild(newRow)
                    if len(sections) > 1:newRow.useTexture = True

                polyItem_label = self.TreeLabel(sel[0],newRow)
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
                        #self.setItemWidget(colorRow,0,colorLabel)
                        




                #cmds.drawsegments(basePoly,1)

                
            else:
                "Nothing Selected"
        

        class TreeWidgetItem(QtWidgets.QTreeWidgetItem):
            def __init__(self,segments=[],isItem = True,poly =None,color = None,useTexture = False):
                QtWidgets.QTreeWidgetItem.__init__(self)

                
                self.segments = segments
                self.bbox = self.getBbox(segments)
                self.segmentsDict = {}
                self.segmentsDict, self.keyList = self.generateDict(segments)
                self.colliders = []
                self.poly = poly
                self.color = color
                self.isItem = isItem
                self.useTexture = useTexture
                

            def getBbox(self,segments):
                #sort and save Min and Max

                listLength = self.getSize()
                if segments == []:
                    return None

                segments.sort(key=lambda x: (x.z , x.y , x.x),reverse=1)
                zMax = segments[0].z
                zMin = segments[listLength-1].z

                segments.sort(key=lambda x: (x.y , x.x , x.z),reverse=1)
                yMax = segments[0].x
                yMin = segments[listLength-1].x

                segments.sort(key=lambda x: (x.x , x.y , x.z),reverse=1)
                xMax = segments[0].x
                xMin = segments[listLength-1].x

                #Create bounding box for segemnts
                bbox = [xMin,yMin,zMin,xMax,yMax,zMax]
                return bbox

            def generateDict(self,segments):
                segmentsDict = {}
                for i in range (self.getSize()):
                    segmentsDict[i] = segments[i]
                    segmentsDict[i].id = i

                keyList = list(segmentsDict.keys())

                return segmentsDict,keyList

            def addCollider(self,bbox):
                self.colliders.append(bbox)

            def getSafeArea(self,bbox):
                pass
            
            def getSize(self):
                return len(self.segments)
                

        class TreeLabel(QtWidgets.QLabel):
            def __init__(self, text, row):
                QtWidgets.QLabel.__init__(self, text)

                self.row = row
                self.text = text
  
                
            def contextMenuEvent(self, event):
                contextMenu = QtWidgets.QMenu(self)
                add_action = QtWidgets.QAction('Add Selected Item', self)
                contextMenu.addAction(add_action)
                add_action.triggered.connect(partial(self.row.treeWidget().addItem,self.row))


                action = contextMenu.exec_(self.mapToGlobal(event.pos()))

            def addItem(self):
                sel = cmds.ls(selection = True)
                
                if len(sel) > 0:


                    poly = sel[0]
                    segmentsDict = envGen.segments.getsegments(poly,1,False)

                    newRow = self.row.treeWidget().TreeWidgetItem(segmentsDict,poly = sel[0])
                    polyItem_label = self.row.treeWidget().TreeLabel(poly,newRow)
                    self.row.addChild(newRow)
                    self.row.treeWidget().setItemWidget(newRow,0,polyItem_label)
                    
                    
                else:
                    "Nothing Selected"
            
            def getText(self):
                return self.text