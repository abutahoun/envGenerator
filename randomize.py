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


        section = segments.Section(tree = widgetItem,poly= widgetItem.poly)

        
        self.processSection(section)

        
    

    def processSection(self, section):
        tree = section.tree
        if tree.childCount() == 0: return

        children = [] 
        for j in range (tree.childCount()):
            child = tree.child(j)
            if child.isItem:
                children.append(child)
            else:
                self.processSection(segments.Section(tree = child,segments=child.segments))

        if len(children) <= 0: return
        choice = numpy.random.choice(children)

        if section.segments == []:
            section = segments.getsegments(section.poly ,self.accuracy, self.sampleSize,self.useTexture,self.colorThreshold)[0]

            #section = segments.getsegments(section.poly,accuracy,sampleSize,useTexture,colorThreshold)[0]

        self.randomPoly(section,children)
        
        

    
    

    def randomPoly(self, section, children):

        
      
        #mode = child.parent().settings.mode
        #ToDo remove hardcode for Mode
        mode = 0 
        if mode == 1:
            section.sort()

        newPoly = None

        group = []
        #for i in range(10):
        Timer_Duplicate = 0.0
        Timer_collision = 0.0

        while len(section.keyList) > 0:
            child = numpy.random.choice(children)
            if child.isItem:
                poly = child.poly
                scale = child.settings.scale
                rotate = child.settings.rotate
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
                print rndRotate
                bbox = cmds.exactWorldBoundingBox(newPoly)


                #get keys that don't create collision
                
                #cmds.timer( s=True, n="c" )
                if mode == 0:
                    safeList = section.getSafeArea(newPoly)
                    #lap = cmds.timer(e=True , n="c")
                    #Timer_collision += lap
                    #print lap
                    if len(safeList) < 1: 
                        cmds.delete(newPoly)
                        break
                    rand = numpy.random.choice(safeList)        #Random segment key from safeList
                else:
                    safeList = section.getSafeArea(newPoly)
                    rand = safeList[0]
                section.keyList.remove(rand)                #Remove key from orginal keyList
                segment = section.segmentsDict.get(rand)    

                


                #cmds.move(bbox[3],bbox[1], bbox[5], '%s.scalePivot' % mesh,"%s.rotatePivot"% mesh, ws=True) #Move Pivot
                cmds.move(segment.location[0],segment.location[1],segment.location[2],newPoly,ws = 1,rpr=1)
                cmds.rotate(segment.rotation[0],segment.rotation[1],segment.rotation[2],newPoly,r=1)

                #recalculate Bounding Box
                bbox = cmds.exactWorldBoundingBox(newPoly)
                section.addCollider(bbox)
                group.append(newPoly)
                section.removeKeys(bbox)

            sectionList = []
            if child.childCount() > 0: #Create section and tree for new poly
                if child.useTexture:
                    sectionList = segments.getsegments(newPoly,self.accuracy,self.sampleSize,self.useTexture,self.colorThreshold)
                    for colorSection in sectionList:
                        for j in range (child.childCount()):
                            if colorSection.color == child.child(j).color: 
                                colorSection.tree = child.child(j)  #match Sction color to the tree child of the same color
                                processSection(colorSection) #Recursion
                else:
                    newSection = segments.Section(poly=newPoly,tree=child)
                    self.processSection(newSection) #Recursion
                
            cmds.refresh()
        if len(group) > 0:
            cmds.group(group)
            #print "duplicate Time:{0}".format(Timer_Duplicate)
            #print "collision Time:{0}".format(Timer_collision)
        
    


def randomize1(segmentList,poly=[],folder=[],buffer = [0,0,0],rSx=[1,1],rSy=[1,1],rSz=[1,1],
Normals = True,mode = 1):
    
    # rS Scale Range


    segmentsDict = {}

    listLength = len(segmentList)

    #sort and save Min and Max
    segmentList.sort(key=lambda x: (x.z , x.y , x.x),reverse=1)
    zMax = segmentList[0].z
    zMin = segmentList[listLength-1].z

    segmentList.sort(key=lambda x: (x.y , x.x , x.z),reverse=1)
    yMax = segmentList[0].x
    yMin = segmentList[listLength-1].x

    segmentList.sort(key=lambda x: (x.x , x.y , x.z),reverse=1)
    xMax = segmentList[0].x
    xMin = segmentList[listLength-1].x

    #Create boinding box segemnts
    baseBbox = [xMin,yMin,zMin,xMax,yMax,zMax]




    for i in range (listLength):
        segmentsDict[i] = segmentList[i]
        segmentsDict[i].id = i

    keyList = list(segmentsDict.keys())

    

    polyList = []

    bboxes = []







    i = 1
    while len(keyList) > 0:
        if mode == 0:
            rand = numpy.random.choice(keyList)
            keyList.remove(rand)
            segment = segmentsDict.get(rand)
    
        else:
            key = keyList[0] 
            keyList.remove(key)
            segment = segmentsDict[key]

        

        rndScale = numpy.random.rand(1,3)[0] #genrate random offset

        
        
        if len(poly) > 0:
            mesh = cmds.duplicate(poly)[0]
        else:
            path = numpy.random.choice(folder)
            newNodes = cmds.file(path,i = 1, rnn=True)

            
            for item in newNodes:
                if item[0] == '|':
                    node = item[1:]
                    newName = node + '_' + str(key)
                    i +=1
                    mesh = cmds.rename(node,newName)
                    break

        
        
        bbox = cmds.exactWorldBoundingBox(mesh)
        cmds.move(bbox[3],bbox[1], bbox[5], '%s.scalePivot' % mesh,"%s.rotatePivot"% mesh, ws=True)
        cmds.move(segment.location[0],segment.location[1],segment.location[2],mesh,ws = 1,rpr=1)
        cmds.rotate(segment.rotation[0],segment.rotation[1],segment.rotation[2],mesh)

        scaleX = rndScale[0] * (rSx[1]-rSx[0]) + rSx[0]
        scaleY = rndScale[1] * (rSy[1]-rSy[0]) + rSy[0]
        scaleZ = rndScale[2] * (rSz[1]-rSz[0]) + rSz[0]


        # checks for collision
        # reduce size if there is collision

        # to do
        # reduction of size should't go bellow minimum 

        # if len(bboxes) > 0:
        #     colBboxes = isCollide(bboxes,segment,[scaleX,scaleY,scaleZ])
        #     while len(colBboxes) > 0:
        #         scaleX = scaleX * (0.9)
        #         scaleY = scaleY * (0.9)
        #         scaleZ = scaleZ * (0.9)
        #         colBboxes = isCollide(colBboxes,segment)

        cmds.scale(scaleX,scaleY,scaleZ,mesh,r=1)


        
         
        bbox = cmds.exactWorldBoundingBox(mesh)
     
        bboxX = [bbox[0],bbox[1],bbox[2],baseBbox[3],bbox[4],bbox[5]] 
        bboxY = [bbox[0],bbox[1],bbox[2],bbox[3],baseBbox[4],bbox[5]] 
        bboxZ = [bbox[0],bbox[1],bbox[2],bbox[3],bbox[4],baseBbox[5]] 
        #bboxX[3] = baseBbox[3] #bbox + area to basepoly edge in x
        # bboxY = bbox 
        # bboxY[4] = baseBbox[4] #bbox + area to basepoly edge in y
        # bboxZ = bbox 
        # bboxZ[5] = baseBbox[5] #bbox + area to basepoly edge in y

        
        for i in range (3):
            bbox[i]-=buffer[i]
            bbox[i+3] += buffer[i]

        bboxes.append(bbox)
        polyList.append(mesh)

        keyList[:] = [x for x in keyList if not cnt.inBbox(bbox,segmentsDict[x].location,[0,0,0])]
        
        if mode == 1:
            keyList[:] = [x for x in keyList if not cnt.inBbox(bboxX,segmentsDict[x].location,[0,0,0])]
            keyList[:] = [x for x in keyList if not cnt.inBbox(bboxY,segmentsDict[x].location,[0,0,0])]
            keyList[:] = [x for x in keyList if not cnt.inBbox(bboxZ,segmentsDict[x].location,[0,0,0])]

    #toDo

    # remove x between new and basepoly edge    within Z
    # remove y between new and basepoly edge    within Z
        

        
    
        


    if len(polyList) > 0:
        cmds.group(polyList)


def isCollide(bboxes,segment,scale):
    colBboxes = []
    for b in bboxes:
        if cnt.inBbox(b,segment.location):
            colBboxes.append(b)  
    
    return colBboxes


