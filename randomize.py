from maya import cmds
import numpy
import cnt
reload (cnt)
import segments
reload (segments)







def randomize(widgetItem):


    section = segments.section(tree = widgetItem,poly= widgetItem.poly)


    processSection(section)


    # listLength = len(widgetItem.segments)
    # treeWidget = widgetItem.treeWidget()
    # items = []

    # for j in range (widgetItem.childCount()):
    #         child = widgetItem.child(j)
    #         treeLabel = treeWidget.itemWidget(child,0)
    #         if(child.active):
    #             items.append(child)
    #             print child.poly
            
    #             if len(items) > 0:
    #                 section = segments.getsegments(widgetItem.poly,1,False)[0]
    #                 item = numpy.random.choice(items)
    #                 randomPoly(section,item)
            

    #         randomize(child)


    # if len(items) > 0:
    #     item = numpy.random.choice(items)

    #     randomPoly(widgetItem,item)
        # while(widgetItem.segments>0):
        #     result = randomPoly(widgetItem.segments,widgetItem.bboxes,children[0])
        #     widgetItem.segments = result.segments
        #     widgetItem.bboxes.append(result.bbox)


        


def processSection1(section):


    children = []
    widgetItem = section.tree
    if widgetItem.childCount() == 0: return

    for j in range (widgetItem.childCount()):
        child = widgetItem.child(j)
        if child.isItem: children.append(child)

    if section.segments == []:
            section = segments.getsegments(widgetItem.poly,1,False)[0]



    print children
    widgetItem = section.tree


        
    if len(children) > 0:
        item = numpy.random.choice(children)

        

        randomize(child)

    

def processSection(section):
    tree = section.tree
    if tree.childCount() == 0: return

    children = []
    for j in range (tree.childCount()):
        children.append(tree.child(j))
    
    child = numpy.random.choice(children)


    if section.segments == []:
        section = segments.getsegments(section.poly,1,False)[0]
        randomPoly(section,child)


    
    

def randomPoly(section,child):

    if child.isItem:
        poly = child.poly
        rand = numpy.random.choice(section.keyList)
        section.keyList.remove(rand)
        segment = section.segmentsDict.get(rand)
        
        mesh = cmds.duplicate(poly)

        bbox = cmds.exactWorldBoundingBox(mesh)

        #cmds.move(bbox[3],bbox[1], bbox[5], '%s.scalePivot' % mesh,"%s.rotatePivot"% mesh, ws=True)
        cmds.move(segment.location[0],segment.location[1],segment.location[2],mesh,ws = 1,rpr=1)
        cmds.rotate(segment.rotation[0],segment.rotation[1],segment.rotation[2],mesh)

        newSection = segments.Section(poly=mesh,tree=child)
        processSection(newSection)


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


