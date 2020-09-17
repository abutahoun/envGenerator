from maya import cmds
import maya.api.OpenMaya as om
import maya.utils
import threading
import numpy
import cnt
reload (cnt)
import segments
reload (segments)




class randomizer(object):
    def __init__(self, widgetItem, globalSettings):
        self.widgetItem = widgetItem
        self.globalSettings = globalSettings

        self.accuracy = widgetItem.settings.accuracy
        self.sampleSize = widgetItem.settings.sampleSize

        self.useTexture = globalSettings.useTexture
        self.colorThreshold = globalSettings.colorThreshold
        self.group = []

        section = segments.Section(tree = widgetItem,poly= widgetItem.poly)

        
        self.processSection(section)

        
        
    

    def processSection(self, section):
        tree = section.tree
        if tree.childCount() == 0:return

        children = [] 
        for j in range (tree.childCount()):
            child = tree.child(j)
            if child.isItem:
                children.append(child)
            else:
                self.processSection(segments.Section(tree = child,segments=child.segments))

        if len(children) <= 0: return
        choice = numpy.random.choice(children)

        if not section.poly == []:
            section = segments.getsegments(section.poly ,self.accuracy, self.sampleSize,self.useTexture,self.colorThreshold)[0]


        self.randomPoly(section,children)
        
        

    
    

    def randomPoly(self, section, children):

        
      
        mode = children[0].parent().settings.mode
        #ToDo remove hardcode for Mode
 
        if mode == 1:
            section.sort()

        newPoly = None


        #for i in range(10):
        Timer_Duplicate = 0.0
        Timer_collision = 0.0

        while len(section.keyList) > 0:
            child = numpy.random.choice(children)
            if child.isItem:
                poly = child.poly
                scale = child.parent().settings.scale
                rotate = child.parent().settings.rotate
                collision = child.parent().settings.collision
                fast = child.parent().settings.fast
                #cmds.timer( s=True, n="d" )

                newPoly = cmds.duplicate(poly)[0]
                cmds.makeIdentity(newPoly, apply = True, t=1, r=1, s=1)
                #Timer_collision += cmds.timer( e=True, n="d" )



                #genrate random scale and rotation values based on item settings
                rndScale = []
                rndRotate = []
                for i in range(0,6,2):
                    valueS = ((numpy.random.uniform(scale[i+1]*-1,scale[i]))+1)
                    valueR = ((numpy.random.uniform(rotate[i+1]*-1,rotate[i])))
                    if valueS < 0.1 and valueS > -0.1: valueS = 0.1
                    rndScale.append(valueS)
                    rndRotate.append(valueR)

                cmds.scale(rndScale[0],rndScale[1],rndScale[2],newPoly,r=1)
                cmds.rotate(rndRotate[0],rndRotate[1],rndRotate[2],newPoly,r=1)
                bbox = cmds.exactWorldBoundingBox(newPoly)


                
                rand = None
                #cmds.timer( s=True, n="c" )
                if collision:
                    if mode == 0:
                        if not fast:
                            safeList = section.getSafeArea(newPoly) #get keys that don't create collision

                            if len(safeList) < 1: 
                                cmds.delete(newPoly)
                                self.groupItems()
                                break
                            rand = numpy.random.choice(safeList)        #Random segment key from safeList
                        else:
                            rand = numpy.random.choice(section.keyList)
                    else: #mode == 1
                        if not fast: 
                            safeList = section.getSafeArea(newPoly)
                            rand = safeList[0]
                        else: 
                            rand = section.keyList[0]

                else: 
                    # No collision detection
                    if mode == 0:
                        rand = numpy.random.choice(section.keyList)
                    else:
                        rand = section.keyList[0]

                section.keyList.remove(rand)                #Remove key from orginal keyList
                segment = section.segmentsDict.get(rand)    

                


                #cmds.move(bbox[3],bbox[1], bbox[5], '%s.scalePivot' % mesh,"%s.rotatePivot"% mesh, ws=True) #Move Pivot
                cmds.move(segment.location[0],segment.location[1],segment.location[2],newPoly,ws = 1,rpr=1)
                cmds.rotate(segment.rotation[0],segment.rotation[1],segment.rotation[2],newPoly,r=1)

                #recalculate Bounding Box
                bbox = cmds.exactWorldBoundingBox(newPoly)
                section.addCollider(bbox)
                if collision: section.removeKeys(bbox)
                self.group.append(newPoly)
                

            sectionList = []
            if child.childCount() > 0: #Create section and tree for new poly
                if child.settings.useTexture:
                    sectionList = segments.getsegments(newPoly,self.accuracy,self.sampleSize,self.useTexture,self.colorThreshold)
                    for colorSection in sectionList:
                        for j in range (child.childCount()):
                            if colorSection.color == child.child(j).color: 
                                colorSection.tree = child.child(j)  #match Section color to the tree child of the same color
                                self.processSection(colorSection) #Recursion
                else:
                    newSection = segments.Section(poly=newPoly,tree=child)
                    self.processSection(newSection) #Recursion
                
            cmds.refresh()
        
        self.groupItems()
        

            #print "duplicate Time:{0}".format(Timer_Duplicate)
            #print "collision Time:{0}".format(Timer_collision)
        #return newPoly
    

    def groupItems(self):
        if len(self.group) > 0:cmds.group(self.group)
        self.group = []





