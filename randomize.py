from maya import cmds
import numpy
import cnt
reload (cnt)
import segments
reload (segments)







def randomize(basePoly,poly=[],folder=[],buffer = [0,0,0],rSx=[1,1],rSy=[1,1],rSz=[1,1],
Normals = True,mode = 1):
    
    # rS Scale Range

    segmentList = segments.getsegments(basePoly,1)
    segmentsDict = {}

    if mode ==1:
        segmentList.sort(key=lambda x: x.z + x.y + x.x,reverse=1)
        #segmentList.sort(key=lambda x: (x.x , x.y , x.z),reverse=1)


    for i in range (len(segmentList)):
        segmentsDict[i] = segmentList[i]
        segmentsDict[i].id = i

    keyList = list(segmentsDict.keys())

    segmentsDict = cnt.getColor(segmentsDict,basePoly)
    

    polyList = []

    bboxes = []

    i = 1
    while len(keyList) > 0:
   # print len(keyList)
    #for itor in range(40):
        if mode == 0:
            rand = numpy.random.choice(keyList)
            keyList.remove(rand)
            segment = segmentsDict.get(rand)
    
        else:
            key = keyList[0] 
            keyList.remove(key)
            segment = segmentsDict[key]

        color = numpy.around(segment.color,decimals=4)

        if numpy.all(color == numpy.array([[ 1,1,1]])):
            continue

        rndScale = numpy.random.rand(1,3)[0] #genrate random offset

        # to do
        # check if the randmoized scale will make a collision with bboxes
        
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

        baseBbox = cmds.exactWorldBoundingBox(basePoly)
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
            #keyList[:] = [x for x in keyList if not cnt.inBbox(bboxZ,segmentsDict[x].location,[0,0,0])]

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


