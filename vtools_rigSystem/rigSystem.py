import bpy
import os
import sys
import math
import mathutils


from bpy.props import (StringProperty,BoolProperty,IntProperty,FloatProperty,FloatVectorProperty,EnumProperty,PointerProperty)
from bpy.types import (Menu, Panel,Operator,AddonPreferences, PropertyGroup)
from bpy_extras.io_utils import ImportHelper
#from rna_prop_ui import rna_idprop_ui_prop_get

#--- DEF GLOBAL --- #

def getFKChain():
    
    fkBones = None
    arm = bpy.context.active_object
    data = getChainSocketBone()
    
    if data != None:
        
        fkchainProperty = findCustomProperty(data, "fkchainBone")
        chainLenghtProperty = findCustomProperty(data, "ikchainLenght")
        
        fkLastBone = data[fkchainProperty]
        chainLenght = data[chainLenghtProperty]

        #-- COLLECT FK CHAIN BONES
        fkBones = []
        currentFKBone = arm.pose.bones[fkLastBone].name
        
        for i in range(0,chainLenght):
            fkBones.insert(0, currentFKBone)
            currentFKBone = arm.pose.bones[currentFKBone].parent.name
    
    return fkBones

def getFreeChain():
    
    freeBones = None
    arm = bpy.context.active_object

    fkChain = getFKChain()
    if fkChain != None:
        
        freeBones = []
        for b in fkChain:
            for c in  arm.pose.bones[b].children:
                if c.name.find("FreeChain") != -1:
                    freeBones.insert(0, c.name)
                    
    return freeBones

def getIKChain():
    ikBones = None
    arm = bpy.context.active_object
    data = getChainSocketBone()
    
    if data != None:
        
        ikChainProperty = findCustomProperty(data, "ikchainBone")
        chainLenghtProperty = findCustomProperty(data, "ikchainLenght")
        
        ikLastBone = data[ikChainProperty]
        chainLenght = data[chainLenghtProperty]

        #-- COLLECT IK CHAIN BONES
        if ikLastBone != "":
            currentIKBone = ikLastBone
            ikBones = []
            for i in range(0,chainLenght):
                ikBones.insert(0, currentIKBone)
                currentIKBone = arm.pose.bones[currentIKBone].parent.name
            
    return ikBones

def getIkTarget():
    
    arm = bpy.context.active_object
    data = getChainSocketBone()
    ikTargetName = None
    
    if data != None:
        ikTargetProperty = findCustomProperty(data, "iktargetid")
        ikTargetName = data[ikTargetProperty]
        if ikTargetName == "":
            ikTargetName = None
        
    return ikTargetName  
                    
def setRotationMode(pRotationMode):
    arm = bpy.context.active_object
    #socketBoneName = getChainSocketBone().name
    fkChain = getFKChain()
    ikChain = getIKChain()
    ikTarget = getIkTarget()
    freeChain = getFreeChain()
    
    """
    print(fkChain)
    print(ikChain)
    print(ikTarget)
    print(freeChain)
    """
    
    bpy.ops.object.mode_set(mode='POSE')
    
    if fkChain != None:
        for b in fkChain:
            arm.pose.bones[b].rotation_mode = pRotationMode #arm.pose.bones[socketBoneName].rotation_mode
        
    if ikChain != None:
        for b in ikChain: 
            arm.pose.bones[b].rotation_mode = pRotationMode
    
    if freeChain != None:
        for b in freeChain:
            print("ENTRA")
            arm.pose.bones[b].rotation_mode = pRotationMode
               
    if ikTarget != None:
        arm.pose.bones[ikTarget].rotation_mode = pRotationMode
           
    
    
def printChain (pChain):
    
    for obj in pChain:
        print(obj)
        
def setXYZRotation(pArm, pSelBoneName, pChainLenght):
    
    currentBone = pSelBoneName
    for i in range(0,pChainLenght):
        tmp_b = pArm.pose.bones[currentBone]
        tmp_b.rotation_mode = 'XYZ'
        currentBone = tmp_b.parent.name  
    


def hideBoneChain(pArm, pLastBone, pHide, pChainLenght):
    
    currentBone = pLastBone
    for i in range(0,pChainLenght):
        
        if (pArm.data.bones.find(currentBone) != -1):
            pArm.data.bones[currentBone].hide = pHide
            
            nextBone = pArm.data.bones[currentBone].parent
            if nextBone is not None:
                currentBone = nextBone.name
            else: 
                break

def getChainSocketBone():
    
    socketBone = None
    activeBone = bpy.context.active_pose_bone
    if activeBone != None:
        
        socketProperty = findCustomProperty(activeBone, "chainSocket")
        if socketProperty != "":
            chainSocketName = bpy.context.object.pose.bones[activeBone.name].get(socketProperty)
            if chainSocketName != "":
                socketBone = bpy.context.object.pose.bones[chainSocketName]
    
    return socketBone
                

def getIKConstraint(pIKControl):
    
    data = None
    obj = bpy.context.active_object
    
    if pIKControl is not None:
        ikProperty = findCustomProperty(pIKControl, "ikchainBone")
        ikLastBone = pIKControl[ikProperty]
        data = obj.pose.bones[ikLastBone].parent
    
    return data
 

def getBoneChainLength(pArm, pBoneChain, pnIkTargetName, pSocketBoneName):
    
    chainLength = len(pBoneChain)
    lastBone = pBoneChain[len(pBoneChain)-1]
    bSocket = pArm.data.bones[pSocketBoneName]
    bLast = pArm.data.bones[pnIkTargetName]
    distance = 0;
    
    
    for i in range(0,chainLength-1):
        pb = pArm.data.bones[pBoneChain[i]]
        distance += pb.length 
            
    
    return distance #+ pArm.data.bones[lastBone].head_radius
    

def moveBoneToLayer(pArm, pSelBoneBone, pLayerDest):
        
        bpy.ops.object.mode_set(mode='POSE')
        if pSelBoneBone in pArm.pose.bones != False:
            pArm.data.bones[pSelBoneBone].layers[pLayerDest] = True
            
            cont = 0
            for l in pArm.data.bones[pSelBoneBone].layers:
                if cont != pLayerDest:
                    pArm.data.bones[pSelBoneBone].layers[cont] = False
                cont += 1
            
                        
def getSelectedChain(pArm):
    
    
    bpy.ops.object.mode_set(mode='POSE')
    selBones = bpy.context.selected_pose_bones
    boneChainNames = [None]*len(selBones)
    
    #-- EXTRACT ORDERED BONE NAMES
    
    for b in selBones:
        tmp_b = b
        cont = 0
                   
        while tmp_b.parent != None:
            if tmp_b.parent in selBones:
                cont += 1
                tmp_b = tmp_b.parent
            else:
                break
            
        boneChainNames[cont] = b.name

    return boneChainNames

def duplicateBone(pNewBoneName, pArm, pBoneName, pParenting):
    

    newBoneName = None    
    arm = pArm
    
    bpy.ops.object.mode_set(mode='EDIT')
    
    
    boneId = arm.data.edit_bones.find(pBoneName)
    newBoneName = None
    
    if boneId != -1:
        oldBone = arm.data.edit_bones[boneId]
        
        newBone = arm.data.edit_bones.new(pNewBoneName)
        newBone.name = pNewBoneName
        newBone.head = oldBone.head
        newBone.tail = oldBone.tail
        newBone.matrix = oldBone.matrix
        newBone.use_deform = False
        newBoneName = newBone.name
                
        if (pParenting == True) and (oldBone.parent != None):
            newBone.use_connect = oldBone.use_connect
            newBone.parent = oldBone.parent
    
        bpy.ops.object.mode_set(mode='EDIT')
             
    return newBoneName


    
def duplicateChainBone(pChainPrefix, pArm, pLayer, pConnected):
    #hola
    firstBone = None
    arm = pArm
    chainLen = 0
    duplicatedBones = []
    sortedDuplicatedBones = []
    
    bpy.ops.object.mode_set(mode='EDIT')
    
    selBones = bpy.context.selected_bones
    chainLen = len(selBones)
    
    #-- duplicate chain
    
    for b in selBones:
        newBoneName = pChainPrefix + b.name
        nbName = duplicateBone(newBoneName, arm, b.name, True)
        duplicatedBones.append(nbName)
        
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='EDIT')
    
    #-- Parenting 
    
    firstBone = None        
    for n in duplicatedBones:
        
        if pLayer != -1:
            moveBoneToLayer(arm,n,pLayer)
            
        bpy.ops.object.mode_set(mode='EDIT')
            
        nb = pArm.data.edit_bones[n]
        
        if nb.parent != None:
            newParentName = pChainPrefix + nb.parent.name
            tmp_nParent = arm.data.edit_bones.find(newParentName)
            if (tmp_nParent != -1):
                nb.use_connect = pConnected
                nb.parent = arm.data.edit_bones[tmp_nParent]
                
                #USE ORIGINAL USE CONNECT SO COMMENT THIS
                #nb.use_connect = True
            
            if findInChain(duplicatedBones, nb.parent.name) == -1:
                firstBone = nb.name
        else:
            firstBone = nb.name
                
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    if firstBone != None:
    
        bpy.ops.object.mode_set(mode='EDIT')
            
        #-- Order chain
        b_tmp = pArm.data.edit_bones[firstBone]
        sortedDuplicatedBones.append(b_tmp.name)
        
        while (len(sortedDuplicatedBones) < len(duplicatedBones)):
            for b in duplicatedBones:
                cBone = pArm.data.edit_bones[b]
                ##cBone.use_connect = pConnected
                if cBone.parent != None:
                    if cBone.parent.name == b_tmp.name:
                        sortedDuplicatedBones.append(b)
                        b_tmp = pArm.data.edit_bones[b]
                
        """
        #REMOVE FIRST BONE PARENT IT WILL BE PARENT LATER
        pArm.data.edit_bones[sortedDuplicatedBones[0]].parent = None
        """
        
        bpy.ops.object.mode_set(mode='OBJECT')            
        bpy.ops.object.mode_set(mode='POSE')
        
        
    return sortedDuplicatedBones    

def findInChain(pChain, pBoneName):
    
    foundId = -1    
    cont = 0
    for b in pChain:
        if b == pBoneName:
            foundId = cont
            break
        cont += 1
        
    return foundId
            

def findInBoneChain(pChain, pBoneName):
    
    found = None    
    for b in pChain:
        if b.name == pBoneName:
            found = b
            break
        
    return found
            
                            
def findPoseBone(pArm, pBoneName):
    
    bpy.ops.object.mode_set(mode='POSE')
    
    res = None
    found = pArm.data.bones.find(pBoneName)
    
    if found != -1:
        res = pArm.data.bones[found]
        
    return res

def findLastBoneInChain(pChain):
    
    last = None
    found = False
        
    for b in pChain:
        if len(b.children) > 0:
            found = True
            for c in b.children:
                if (c == None) or (c not in pChain):
                    found = True and found
                else: 
                    found = False
        else:
            found = True 
            
        if found == True:
            last = b.name
            break
    
    
    return last

def findFirstBoneInChain(pChain):
    
    first = None
    found = False

    for b in pChain:
        if (b.parent == None) or (b.parent not in pChain):
            first = b.name
    
    return first  

          

def findCustomProperty(pBone, pWildCat):
        
    id = ""
    
    for k in pBone.keys():
        if k.find(pWildCat) != -1:
            id = k
            break
    
    return id
            
    
#--- OPERATORS --- #

                
class VTOOLS_OP_RS_addArmature(bpy.types.Operator):
    bl_idname = "vtoolsrigsystem.addarmature"
    bl_label = "Test button"
    bl_description = "Add new armature"
           
    def execute(self, context):
        #self.addArmature()
        #duplicateBone("ikTarget",bpy.context.object, bpy.context.active_pose_bone)
        #duplicateChainBone("FK_", bpy.context.object)
        self.bendyBones()
        return {'FINISHED'}
    
    def bendyBones(self):
        
        #CREATE HEAD AND TAIL CONTROLS
        arm = bpy.context.object
        bpy.ops.object.mode_set(mode='EDIT')
        
        b = arm.data.edit_bones[0]
        v = mathutils.Vector((0,0,1))
        vmov = (b.tail.copy() - b.head.copy()) * 0.10
        ot = b.tail.copy()
        b.tail += vmov
        b.head = ot
 
        return True
    
    def addArmature(self):
        bpy.context.space_data.cursor_location = [0,0,0]
        bpy.ops.object.armature_add()
        newArm = bpy.context.active_object
        newArm.show_x_ray = True
        newArm.name = "NUEVO"
        bpy.context.object.data.use_mirror_x = True
    
        return True

class VTOOLS_OP_RS_createIK(bpy.types.Operator):
    bl_idname = "vtoolsrigsystem.createik"
    bl_label = "Create IK/FK chain"
    bl_description = "Create a IK/FK Chain"
        
    oriLayer = 0
    oriLayerSaved = 31
    ikLayer = 31
    fkLayer = 30
    chainId = ""
    
    
    def findLastChild(self,pBone):
        last = None
        b = pBone
        if len(b.children) == 0:
            last = b
        elif b not in bpy.context.selected_pose_bones:
            if b.parent != None:
                last = b.parent
        else:
            for bc in b.children:
                if bc in bpy.context.selected_pose_bones:
                    last = self.findLastChild(bc)
                else:
                    last = b
       
        return last
                
    def getSelectedChains(self):
        
        arm = bpy.context.object
        chains = []
        usedBones = []
        
        for b in bpy.context.selected_pose_bones:

            if b.name not in usedBones:
                singleChain = []
                                
                #FIND LAST CHILD BONE
                lastChild = self.findLastChild(b)
                
                if lastChild != None:
                    #RUN THROUGH OUT THE WHOLE CHAIN
                    
                    singleChain.append(lastChild.name)
                    usedBones.append(lastChild.name) #if a bone is added to a chain is ignored in the future
                    
                    if lastChild.parent != None:
                        tmpB = lastChild.parent
                        while tmpB != None and tmpB in bpy.context.selected_pose_bones:
                            singleChain.append(tmpB.name)
                            usedBones.append(tmpB.name)
                            tmpB = tmpB.parent
                            
                    if len(singleChain) > 0:
                        chains.append(singleChain)  
                    
        return chains
        
    def execute(self, context):
        arm = bpy.context.object
        chains = self.getSelectedChains()
        
        #print("ENTRA -------------------- ", chains)
        
        for c in chains:
            bpy.ops.object.mode_set(mode='POSE')
            
            #DESELCCIONA TODO
            for b in bpy.context.object.data.bones:
                b.select = False
            
            #SELECCIONA LOS HUESOS DE UNA CADENA
            rotMode = None
            for bc in c: 
                arm.data.bones[bc].select = True
                arm.data.bones.active = arm.data.bones[bc]
                rotMode = arm.pose.bones[bc].rotation_mode
                    
            #CREA LA CADENA    
            self.createIKFKChain()
            
            #APLICA EL ROTATION MODE

            #bpy.ops.vtoolsrigsystem.setrotationmode(rotationMode=rotMode)
            
        return {'FINISHED'}
        
    def ignoreUsedBones(self, pArm):
        
        for b in bpy.context.selected_pose_bones:
            numSelectedBones = len(bpy.context.selected_pose_bones) 
            if len(b.constraints) > 0:
                #IGNORE
                dataBone = pArm.data.bones[b.name]
                dataBone.select = False
                dataBone.select_head = False
                dataBone.select_tail = False
                if numSelectedBones > 1:
                    pArm.data.bones.active = None
                else:
                    for bs in bpy.context.selected_pose_bone:
                        otherB = pArm.data.bones[bs.name]
                        if otherB.select == True:
                            pArm.data.bones.active = bs
                
    def getNameId(self, pName):
        
        id = ""
        
        for i in range(0,len(pName)):
            if pName[i] != ".":
                id += pName[i]
            else:
                break
            
        return id
    
    #CREATE SOCKET BONE
    def createSocketBone(self, pSelBones):
        arm = bpy.data.objects[bpy.context.active_object.name]
        sockectBoneName = None
        selBones = pSelBones
        
        bpy.ops.object.mode_set(mode='EDIT')
        firstBoneConnection = arm.data.edit_bones[selBones[0]].name
        sockectBoneName = ""
        
        
        #IF HUMANOID BREAK CONNECTION
        #if bpy.context.scene.isHumanoidChain == True:
        for b in selBones:   
            bpy.ops.object.mode_set(mode='EDIT')
            editBone = arm.data.edit_bones[b]
            editBone.use_connect = False
            editBone.inherit_scale = "NONE"
        
            
        #IF FIRST BONE EXISTS
        if firstBoneConnection != None:
            sockectBoneName = duplicateBone("SOCKETCHAIN-" + selBones[0] , arm, firstBoneConnection , bpy.context.scene.childChainSocket)
                
            bpy.ops.object.mode_set(mode='POSE')
            #REMOVE ALL CONSTRAINTS
            while len(arm.pose.bones[sockectBoneName].constraints) > 0:
                removeC = arm.pose.bones[sockectBoneName].constraints[0]
                arm.pose.bones[sockectBoneName].constraints.remove(removeC)
                
            #PARENT SOCKET BONE
            bpy.ops.object.mode_set(mode='EDIT')
            arm.data.edit_bones[sockectBoneName].use_connect = False
            arm.data.edit_bones[sockectBoneName].parent = arm.data.edit_bones[selBones[0]].parent 
            arm.data.edit_bones[sockectBoneName].inherit_scale = "NONE"
            """
            if bpy.context.scene.childChainSocket == False:
                arm.data.edit_bones[sockectBoneName].inherit_scale = "NONE"
            else: 
                arm.data.edit_bones[sockectBoneName].inherit_scale = "FULL"
            """
            
            #MOVE LAYER SOCKET BONE
            moveBoneToLayer(arm, sockectBoneName, 31)
            
            #CREATE SOCKET CONSTRAINTS
            bpy.ops.object.mode_set(mode='POSE')
            tCons = arm.pose.bones[sockectBoneName].constraints.new('COPY_TRANSFORMS')
            tCons.name = "maintainVolumeC"
            tCons.influence = 1
            tCons.enabled = False
            
            tCons = arm.pose.bones[sockectBoneName].constraints.new('COPY_TRANSFORMS')
            tCons.name = "limitScaleC"
            tCons.influence = 1
            tCons.enabled = False
            
            #CREATE CONSTRAINT IK CONTROL IN SOCKET 
            bpy.ops.object.mode_set(mode='POSE')  
            tCons = arm.pose.bones[sockectBoneName].constraints.new('COPY_TRANSFORMS')
            tCons.name = "IKControl"
            tCons.influence = 1
            tCons.enabled = False
            
            
        
        """
        #REMOVE PARENT
        bpy.ops.object.mode_set(mode='EDIT')
        arm.data.edit_bones[sockectBoneName].parent = None
        """
        
        bpy.ops.object.mode_set(mode='OBJECT')
        
        return sockectBoneName
            
    #PARENT TO SOCKET 
    def parentToSocket(self,pArm, pSockectBoneName, pChain, pUseConnect):
        arm = pArm
        bpy.ops.object.mode_set(mode='OBJECT')
        arm.data.update_tag()
        bpy.ops.object.mode_set(mode='EDIT')
        firstBone = arm.data.edit_bones[pChain[0]]
        try:
            arm.data.edit_bones[pChain[0]].use_connect = False
            firstBone.parent = arm.data.edit_bones[pSockectBoneName]
            bpy.ops.object.mode_set(mode='POSE')
        except:
            print("BONE BROKEN")
        
        print(arm.pose.bones[pChain[0]])    
        
        return True
    
    def rootInSelected(self,pSelBones):
        rootFind = False
        for b in pSelBones:
            if b.find(bpy.context.scene.fkikRoot) != -1:
                rootFind = True
        
        return rootFind         
        
    #CREATE IK FK FREE CHAINS
    def createIKFKChain(self):
        ikTargetName = ""
        lastIKBoneName = ""
        fkChain = None
        ikChain = None
        freeChain = None
        sockectBoneName = None
        arm = bpy.data.objects[bpy.context.active_object.name]
        singleChain = False
        chainEndBoneName = None
        lastFreeBoneName = None


        #IGNORE USED BONES
        self.ignoreUsedBones(arm)
        
        #SHOW ALL LAYERS
        for i in range(0,len(arm.data.layers)):
            arm.data.layers[i] = True
            
            
        #GET SELECTED BONES
        bpy.ops.object.mode_set(mode='POSE')
        selBones = getSelectedChain(arm)
        
        #CHECK IF IS A SINGLE CHAIN OR CAN HAVE IK
        lenSelBones = len(selBones)
        if lenSelBones == 1:
            singleChain = True
        
        if lenSelBones < 3 or self.rootInSelected(selBones) == True:
            bpy.context.scene.addIkChain = False
        
        #CANCEL INHERIT SCALE
        bpy.ops.object.mode_set(mode='EDIT')
        for b in selBones:
            arm.data.edit_bones[b].inherit_scale = "NONE"
        
        bpy.ops.object.mode_set(mode='POSE')    
        oriBoneName = findLastBoneInChain(bpy.context.selected_pose_bones)
        firstBoneName = findFirstBoneInChain(bpy.context.selected_pose_bones)
        
        #SET CHAIN ID
        self.chainId = self.getNameId(firstBoneName)

        #CREATE CHAINS
        if oriBoneName != None and firstBoneName != None:
            
            chainLenght = len(bpy.context.selected_pose_bones)   
            bpy.context.object.data.use_mirror_x = False
            
            #CREATE SOCKET
            sockectBoneName = self.createSocketBone(selBones)
            
            bpy.ops.object.mode_set(mode='POSE')   
            
            #-- CREATE IK
            if bpy.context.scene.addIkChain == True and singleChain == False:
                ikChain = self.createIKChain(chainLenght, sockectBoneName)
                lastIKBoneName = ikChain[len(ikChain)-1]
                ikTargetName = self.getTargetIK(arm,lastIKBoneName)
            
            #-- CREATE FK
            fkChain = self.createFKChain(chainLenght, sockectBoneName, ikTargetName, ikChain)
            lastFkBoneName = fkChain[len(fkChain)-1]
            
            # -- CREATE FREE CONTROLS
            if singleChain == False:
                freeChain = self.createFreeChain(arm, chainLenght, sockectBoneName, fkChain, ikChain)
                lastFreeBoneName = freeChain[len(freeChain)-1]
                               
             #-- CREATE DRIVERS
            self.createCustomControlProperties(arm, sockectBoneName, lastFkBoneName, lastFreeBoneName, lastIKBoneName,chainLenght) 
            self.setTransformConstraints(selBones,sockectBoneName, ikChain, ikTargetName, fkChain, freeChain)
            self.setSwitchDrivers(arm, selBones, ikTargetName, sockectBoneName)
            
            #-- MOVE BONES LAYER                
            self.moveChainToBoneLayer(arm, selBones, 0)

            #CREATE DEF CUSTOM VARIABLES
            bpy.ops.object.mode_set(mode='POSE')
            for o in selBones:
                cBone = arm.pose.bones[o]
                cBone["iktargetid"] = ikTargetName
            
            #MOVE UTILS BONES
            if singleChain == True:
                bpy.ops.object.mode_set(mode='POSE')
                if chainEndBoneName != None:
                    moveBoneToLayer(arm, chainEndBoneName, 28)
            
            #-- RESET
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='POSE')
            
            #PARENT TO SOCKET
            self.parentToSocket(arm, sockectBoneName, fkChain, True)
            if ikChain != None:
                self.parentToSocket(arm, sockectBoneName, ikChain, True)
            
            
        for i in range(1,len(arm.data.layers)):
            arm.data.layers[i] = False
        
        #SET LAYER VISIBILITY / VISIBLE    
        arm.data.layers[0] = True
        arm.data.layers[1] = True
        arm.data.layers[2] = True
        arm.data.layers[3] = True
        
        
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='POSE')
    
    def setTransformConstraints(self, pDefBone, pSocketBoneName, pIkChain, pIkTarget, pFkChain, pFreeChain):
        
        arm = bpy.context.object
        bpy.ops.object.mode_set(mode='POSE')
        
        bcont = 0
        for b in pDefBone:
            
            pb = None
            pb = arm.pose.bones[b]
            
            if pFreeChain != None:
                if bcont < len(pFreeChain)-1:
                    #FREE STRETCH
                    tCons = pb.constraints.new('COPY_LOCATION')
                    tCons.name = "FreeChain_Location"
                    tCons.target = arm
                    tCons.subtarget = arm.pose.bones[pFreeChain[bcont]].name
                    tCons.target_space = 'WORLD'
                    tCons.owner_space = 'WORLD'
                    tCons.influence = 1
                
                    tCons = pb.constraints.new('STRETCH_TO')
                    tCons.name = "FreeChain_stretchTo"
                    tCons.target = arm
                    tCons.subtarget = arm.pose.bones[pFreeChain[bcont+1]].name
                    tCons.volume = "NO_VOLUME"
                    tCons.influence = 1
                else: 
                    #FREE  COPY TRANSFORM
                    tCons = pb.constraints.new('COPY_TRANSFORMS')
                    tCons.name = "FreeChain_transform"
                    tCons.target = arm
                    tCons.subtarget = arm.pose.bones[pFreeChain[bcont]].name
                    tCons.target_space = 'WORLD'
                    tCons.owner_space = 'WORLD'
                    tCons.influence = 1
            else: 
                #IF NOT FREE CHAIN COPY TO FK
                tCons = pb.constraints.new('COPY_TRANSFORMS')
                tCons.name = "FKChain_transform"
                tCons.target = arm
                tCons.subtarget = arm.pose.bones[pFkChain[bcont]].name
                tCons.target_space = 'WORLD'
                tCons.owner_space = 'WORLD'
                tCons.influence = 1
                
            #LIMIT SCALE
            tCons = pb.constraints.new('LIMIT_SCALE')
            tCons.name = "DEF Limit Scale"
            tCons.use_max_x = True
            tCons.use_max_z = True
            tCons.max_x = 1
            tCons.max_z = 1
            tCons.owner_space = "LOCAL"
            #if bpy.context.scene.isHumanoidChain == True:
            tCons.use_max_y = True
            tCons.max_y = 1
            
            #ADD LIMIT SCALE DRIVER
            tmpD = tCons.driver_add("influence")
            tmpD.driver.type = 'SCRIPTED'
            tmpD.driver.expression = "limitScaleControl"
            
            tmpV = tmpD.driver.variables.new()
            tmpV.name = "limitScaleControl"
            tmpV.targets[0].id_type = 'OBJECT'
            tmpV.targets[0].id = bpy.data.objects[arm.name]
            
            tmpV.targets[0].data_path = "pose.bones[\""+pSocketBoneName+"\"].constraints[\"limitScaleC\"].influence"   
            #tmpV.targets[0].data_path = "pose.bones[\""+pFKSocket+"\"].maintainVolumeC"


            #MAINTAIN VOLUME
            #tCons = pArm.pose.bones[pBone].constraints.new('MAINTAIN_VOLUME')
            tCons = pb.constraints.new('MAINTAIN_VOLUME')
            tCons.name = "DEF_MaintainVolume"
            tCons.free_axis = "SAMEVOL_Y"
            tCons.volume = 1
            tCons.owner_space = "LOCAL"
            
            #ADD MAINTAIN VOLUME DRIVER
            tmpD = tCons.driver_add("influence")
            tmpD.driver.type = 'SCRIPTED'
            tmpD.driver.expression = "maintainVolumeControl"
            
            tmpV = tmpD.driver.variables.new()
            tmpV.name = "maintainVolumeControl"
            tmpV.targets[0].id_type = 'OBJECT'
            tmpV.targets[0].id = bpy.data.objects[arm.name]
            
            tmpV.targets[0].data_path = "pose.bones[\""+pSocketBoneName+"\"].constraints[\"maintainVolumeC\"].influence"   
            #tmpV.targets[0].data_path = "pose.bones[\""+pFKSocket+"\"].maintainVolumeC"

            bcont += 1 
                
                
        return True
    
    def moveChainToBoneLayer(self, pArm, pChain, pLayerDest):
        
        bpy.ops.object.mode_set(mode='POSE')
        
        for b in pChain:
            oriBoneName = pArm.pose.bones[b].name
            if oriBoneName != None: 
                pArm.data.bones[oriBoneName].layers[pLayerDest] = True
                
                cont = 0
                for l in pArm.data.bones[oriBoneName].layers:
                    if cont != pLayerDest:
                        pArm.data.bones[oriBoneName].layers[cont] = False
                    cont += 1
        
        
    def createCustomControlProperties(self, pArm, pSocketBoneName, pFkChainBoneName, pFreeChainBoneName, pIkChainBoneName, pChainLen): 
        
        res = False
        bpy.ops.object.mode_set(mode='POSE')
        
        if (pArm.pose.bones.find(pSocketBoneName) != -1):
            
            ikControlBone = pArm.pose.bones[pSocketBoneName]
            
            ikControlBone[self.chainId + "_fkchainBone"] = pFkChainBoneName
            ikControlBone[self.chainId + "_freechainBone"] = pFreeChainBoneName
            ikControlBone[self.chainId + "_ikchainBone"] = pIkChainBoneName
            ikControlBone[self.chainId + "_ikchainLenght"] = pChainLen
            ikControlBone[self.chainId + "_chainId"] = self.chainId
                
            res = True
            
        return res
        
        
    def setSwitchDrivers(self, pArm, pDefChain, pIkTargetName, pFKSocket):
        
        #if pIkTargetName != "":
        for i in range(0,len(pDefChain)):
            tmp_oriBone = pDefChain[i]
            if tmp_oriBone != None:
               
                for c in pArm.pose.bones[tmp_oriBone].constraints:
                    if pIkTargetName != "":
                        if "FK" in c.name:
                            tmpD = c.driver_add("influence")
                            tmpD.driver.type = 'SCRIPTED'
                            tmpD.driver.expression = "1 - ikControl"
                            
                            tmpV = tmpD.driver.variables.new()
                            tmpV.name = "ikControl"
                            tmpV.targets[0].id_type = 'OBJECT'
                            tmpV.targets[0].id = bpy.data.objects[pArm.name]
                            tmpV.targets[0].data_path = "pose.bones[\""+pFKSocket+"\"].constraints[\"IKControl\"].influence"  
                            #tmpV.targets[0].data_path = "pose.bones[\""+pFKSocket+"\"].ikcontrol"  
                            #tmpV.targets[0].data_path = "pose.bones[\""+pIkTarget.name+"\"].constraints[\"IKControl\"].influence" 
                            #tmpV.targets[0].data_path = "pose.bones[\""+pIkTargetName+"\"][\"ikcontrol\"]" 
                    
                    """        
                    #ADD MAINTAIN VOLUME
                    if "DEF_MaintainVolume" in c.name:
                        tmpD = c.driver_add("influence")
                        tmpD.driver.type = 'SCRIPTED'
                        tmpD.driver.expression = "maintainVolumeControl"
                        
                        tmpV = tmpD.driver.variables.new()
                        tmpV.name = "maintainVolumeControl"
                        tmpV.targets[0].id_type = 'OBJECT'
                        tmpV.targets[0].id = bpy.data.objects[pArm.name]
                        
                        tmpV.targets[0].data_path = "pose.bones[\""+pFKSocket+"\"].constraints[\"maintainVolumeC\"].influence"   
                        #tmpV.targets[0].data_path = "pose.bones[\""+pFKSocket+"\"].maintainVolumeC"
                    """
                
    def getSelectedBone(self, pArm):
        
        sBone = None
        
        for b in pArm.data.bones:
            if b.select == True:
                sBone = b    
                break
            
        return sBone
    
    def selectBone(self, pArm, pBoneName):
        
        bpy.ops.object.mode_set(mode='POSE')
        
        boneSelected = None
        pArm.data.bones.active = None
        
        for b in pArm.data.bones:
            if b.name != pBoneName:
                b.select = False
                b.select_head = False
                b.select_tail = False
            else:
                b.select = True
                b.select_head = True
                b.select_tail = True
                pArm.data.bones.active = b
                boneSelected = b
               
        return boneSelected
    
    def getTargetIK(self, pArm, pBoneName):
        
        bpy.ops.object.mode_set(mode='POSE')
        
        ikTarget = None
        if (pArm.pose.bones.find(pBoneName) != -1):
            sBone = pArm.pose.bones[pBoneName]

            if sBone.get("iktargetid") is not None:
                ikTarget = sBone["iktargetid"]
    
        return ikTarget
               
    def createIkTarget(self, pArm, pLastBoneName, pChain, pSockectBoneName):
        
        bpy.ops.object.mode_set(mode='POSE')
        newIkTargetName = None
        
        #self.selectBone(arm,"")
        #sBone = self.selectBone(pArm,pSelBone)    
        ikTarget = None
        
        if (pArm.pose.bones.find(pLastBoneName) != -1):
            
            newIkTargetName = duplicateBone(("ikTarget-" + pLastBoneName), pArm, pLastBoneName, True)        
            
            bpy.ops.object.mode_set(mode='EDIT')
            newIkTarget = pArm.data.edit_bones[newIkTargetName]
            
            if newIkTarget != None:
                
                newIkTarget.parent = None
                newIkTarget.use_connect = False
 
                bpy.ops.object.mode_set(mode='POSE')
            
                ikTarget = pArm.data.bones[newIkTargetName]    
                ikTarget.use_deform = False
                                
                pArm.pose.bones[ikTarget.name].bone.layers[self.ikLayer] = False
                pArm.pose.bones[ikTarget.name].bone.layers[self.oriLayer] = True
                
                bpy.ops.object.mode_set(mode='OBJECT')
                
                #constraint last bone to ikTarget
                tCons = pArm.pose.bones[pLastBoneName].constraints.new('COPY_TRANSFORMS')
                tCons.name = "IK_head"
                tCons.target = pArm
                tCons.subtarget = newIkTargetName
                tCons.target_space = 'WORLD'
                tCons.owner_space = 'WORLD'
                tCons.influence = 1
                
                #constraint IK TARGET LIMIT DISTANCE for ik stretch
                tCons = pArm.pose.bones[newIkTargetName].constraints.new('LIMIT_DISTANCE')
                tCons.name = "IK_stretchLimit"
                tCons.target = pArm
                tCons.subtarget = pArm.pose.bones[pSockectBoneName].name #CAMBIO
                tCons.distance = getBoneChainLength(pArm,pChain, newIkTargetName, pSockectBoneName)
                tCons.target_space = 'WORLD'
                tCons.owner_space = 'WORLD'
                tCons.influence = 1
        
                #hide last IK bone
                #pArm.data.bones[pLastBoneName].hide = True
                
                bpy.ops.object.mode_set(mode='POSE')
                
                #SET CUSTOM OBJECT
                if bpy.context.scene.ikControlObjects != '':
                    pArm.pose.bones[newIkTargetName].custom_shape = bpy.data.objects[bpy.context.scene.ikControlObjects]
                    pArm.pose.bones[newIkTargetName].use_custom_shape_bone_size = False

                
                
                bpy.ops.object.mode_set(mode='EDIT')
                #PARENT TO ROOT
                pArm.data.edit_bones[newIkTargetName].parent = None
                if bpy.context.scene.fkikRoot != "":
                    pArm.data.edit_bones[newIkTargetName].parent = pArm.data.edit_bones[bpy.context.scene.fkikRoot]
                    
        
        return newIkTargetName  
    
    def createIkConstraint(self,pArm, pIkLastBoneName, pIkTargetName, pChainLenght):
         
        
        bpy.ops.object.mode_set(mode='POSE')
        
        if (pArm.data.bones.find(pIkLastBoneName) != -1):
            
            lastIKPoseBone = pArm.data.bones[pIkLastBoneName] 
            
            if (pArm.data.bones.find(lastIKPoseBone.parent.name) != -1):
                
                ikBone = pArm.data.bones[lastIKPoseBone.parent.name]
                    
                ikConst = pArm.pose.bones[ikBone.name].constraints.new('IK')
                ikConst.target = pArm
                ikConst.subtarget = pIkLastBoneName #pIkTargetName CAMBIO!!!
                ikConst.chain_count = pChainLenght - 1
                
                currentBoneName = pIkLastBoneName
                for i in range(0, pChainLenght):
                    cBone = pArm.pose.bones[currentBoneName]
                    cBone["iktargetid"] = pIkTargetName
                    if cBone.parent != None: 
                        currentBoneName = cBone.parent.name
                    else: 
                        break

            #QUITA LA CONEXION PARA QUE FUNCIONE LA IK - STRETCH
            bpy.ops.object.mode_set(mode='EDIT')
            pArm.data.edit_bones[lastIKPoseBone.name].use_connect = False
            #pArm.data.edit_bones[lastIKPoseBone.name].parent = None
            
            
                         
    def createIKChain(self, pChainLenght, pSockectBoneName):

                
        #print("------------------ ENTRA IK ---------------------")
        
        arm = bpy.context.active_object
        selBones = getSelectedChain(arm)
        cadLen = pChainLenght
        lastIKBoneName = None
        newChain = duplicateChainBone("IKChain-", arm,30, True)
        lastIKBone = arm.data.bones[newChain[len(newChain)-1]]
        lastIKBoneName = lastIKBone.name
        
        #CREATE IK TARGET    
        ikTargetName = self.createIkTarget(arm, lastIKBoneName, newChain, pSockectBoneName)
        self.createIkConstraint(arm, lastIKBoneName, ikTargetName, cadLen) 
        
        #MOVE BONE
        moveBoneToLayer(arm, ikTargetName, 1)
        
        
        bcont = 0
        for b in newChain:
            arm.pose.bones[b].ik_stretch = 0.1
            
        #CREATE DEF CUSTOM PROPERTIES
        bpy.ops.object.mode_set(mode='POSE')
        
        if (pSockectBoneName != ""):
            
            ikControlBone = arm.pose.bones[pSockectBoneName]

            ikControlBone[self.chainId + "_ikDriver"] = True
            ikControlBone[self.chainId + "_chainId"] = self.chainId
            ikControlBone[self.chainId + "_ikchainLenght"] = pChainLenght
            ikControlBone[self.chainId + "_ikTarget"] = ikTargetName
            
            for b in newChain:
                
                tmp_b = arm.pose.bones[b]
                #SET IK STRETCH
                tmp_b.ik_stretch = 0.1
                
                #CUSTOM PROP
                tmp_b[self.chainId + "_chainSocket"] = pSockectBoneName
                tmp_b[self.chainId + "_chainId"] = self.chainId

            arm.pose.bones[ikTargetName][self.chainId + "_chainSocket"] = pSockectBoneName
            arm.pose.bones[ikTargetName][self.chainId + "_chainId"] = self.chainId
    
        return newChain
    
    #CREATE FREE CHAIN
    def createFreeChain(self, pArm, pChainLenght, pSockectBoneName, pFKChain, pIKChain):
        arm = pArm
        selBones = getSelectedChain(arm)
        freeChain = duplicateChainBone("FreeChain-", arm,1, False) 
        
        #SETTINGS
        for i in range(0,len(freeChain)):
            
            #PARENT TO FK CHAIN
            bpy.ops.object.mode_set(mode='EDIT')
            arm.data.edit_bones[freeChain[i]].parent = arm.data.edit_bones[pFKChain[i]]

            #SET CUSTOM OBJECT
            if bpy.context.scene.fkFreeControlObjects != '':
                bpy.ops.object.mode_set(mode='POSE')
                arm.pose.bones[freeChain[i]].custom_shape = bpy.data.objects[bpy.context.scene.fkFreeControlObjects]
                arm.pose.bones[freeChain[i]].use_custom_shape_bone_size = False
    
    
        #ADD CUSTOM PROPERTY
        for b in freeChain:
            cBone = arm.pose.bones[b]
            cBone[self.chainId + "_chainSocket"] = pSockectBoneName
            cBone[self.chainId + "_chainId"] = self.chainId
              
        return freeChain
    
        
    #CREATE FK CHAIN     
    def createFKChain(self, pChainLenght, pSockectBoneName, pIkTargetName, pIKChain):
        arm = bpy.context.active_object
        selBones = getSelectedChain(arm)
        
        #--FK BONES
        newChain = duplicateChainBone("FKChain-", arm,2, False) 
       
        if len(newChain) > 0:
 
            #SETTINGS
            for i in range(0,len(newChain)):
                o = newChain[i]
                #SET CUSTOM OBJECT
                bpy.ops.object.mode_set(mode='POSE')
                if bpy.context.scene.fkControlObjects != '': 
                    arm.pose.bones[o].custom_shape = bpy.data.objects[bpy.context.scene.fkControlObjects]
                    arm.pose.bones[o].use_custom_shape_bone_size = False
                    
                #CUSTOM PROPERTIES
                bpy.ops.object.mode_set(mode="POSE") 
                arm.pose.bones[o][self.chainId + "_chainSocket"] = pSockectBoneName
                arm.pose.bones[o][self.chainId + "_chainId"] = self.chainId
                
                #CONSTRAINT TO IK
                if pIKChain != None:
                    bpy.ops.object.mode_set(mode="POSE") 
                    tCons = arm.pose.bones[o].constraints.new('COPY_TRANSFORMS')
                    tCons.name = "IK_TRANSFORM"
                    tCons.target = arm
                    tCons.subtarget = pIKChain[i]
                    tCons.target_space = 'WORLD'
                    tCons.owner_space = 'WORLD'
                    tCons.influence = 0
                    
                    #SET IK DRIVER
                    tmpD = tCons.driver_add("influence")
                    tmpD.driver.type = 'SCRIPTED'
                    tmpD.driver.expression = "ikControl"
                    
                    tmpV = tmpD.driver.variables.new()
                    tmpV.name = "ikControl"
                    tmpV.targets[0].id_type = 'OBJECT'
                    tmpV.targets[0].id = bpy.data.objects[arm.name]
                    tmpV.targets[0].data_path = "pose.bones[\""+pSockectBoneName+"\"].constraints[\"IKControl\"].influence"
                    
                
            bpy.ops.object.mode_set(mode='POSE')            
            if pSockectBoneName != "":
                fkControlBone = arm.pose.bones[pSockectBoneName]
                
                fkControlBone[self.chainId + "_fkDriver"] = True
                fkControlBone[self.chainId + "_chainId"] = self.chainId
                fkControlBone[self.chainId + "_ikchainLenght"] = pChainLenght
                #fkControlBone[self.chainId + "_fkStretchBone"] = "" #nbName TO REMOVE
                fkControlBone[self.chainId + "_iktargetid"] = pIkTargetName 
                
         
        return newChain
                     
    def addTransformConstraint(self, pConsName, pArm, pBaseOri, pDriveOri, pChanLenght):
        
        bpy.ops.object.mode_set(mode='POSE')
        
        findObone = pArm.data.bones.find(pBaseOri)
        findDbone = pArm.data.bones.find(pDriveOri)
        
        if (findObone != -1) and (findDbone != -1):
            
            oBone = pArm.data.bones[pBaseOri]
            dBone = pArm.data.bones[pDriveOri]
            
            tmp_oBone = pBaseOri
            tmp_dBone = pDriveOri
            
            for i in range(0,pChanLenght):
                if (tmp_oBone != None) and (tmp_dBone != None):       
                    tCons = pArm.pose.bones[tmp_oBone].constraints.new('COPY_TRANSFORMS')
                    tCons.name = pConsName
                    tCons.target = pArm
                    tCons.subtarget = tmp_dBone
                    tCons.target_space = 'WORLD'
                    tCons.owner_space = 'WORLD'
                    tCons.influence = 0
                
                 
                    if (pArm.data.bones[tmp_oBone].parent != None):
                        tmp_oBone = pArm.data.bones[tmp_oBone].parent.name
                    else:
                        tmp_oBone = None
                            
                    if (pArm.data.bones[tmp_dBone].parent != None):
                        tmp_dBone = pArm.data.bones[tmp_dBone].parent.name
                    else:
                        tmp_dBone = None
        

class VTOOLS_OP_RS_snapIKFK(bpy.types.Operator):
    bl_idname = "vtoolsrigsystem.snapikfk"
    bl_label = "IK to FK"
    bl_description = "Snap IK to FK"
    
    def execute(self, context):
        arm = bpy.context.active_object
        data = getChainSocketBone()
        if data != None:
            ikTargetProperty = findCustomProperty(data, "ikTarget")
            fkchainProperty = findCustomProperty(data, "fkchainBone")
            
            arm.pose.bones[data[ikTargetProperty]].matrix = arm.pose.bones[data[fkchainProperty]].matrix
                
        return {'FINISHED'}
    
class VTOOLS_OP_RS_snapFKIK(bpy.types.Operator):
    bl_idname = "vtoolsrigsystem.snapfkik"
    bl_label = "FK to IK"
    bl_description = "Snap FK to IK"
    
    def execute(self, context):
        
        arm = bpy.context.active_object
        fkChain = getFKChain()
        ikChain = getIKChain()
        
        for i in range(0,len(fkChain)):
            bpy.ops.object.mode_set(mode='POSE')
            arm.pose.bones[fkChain[i]].matrix = arm.pose.bones[ikChain[i]].matrix
                  
        return {'FINISHED'}

            
class VTOOLS_OP_RS_rebuildChain(bpy.types.Operator):
    bl_idname = "vtoolsrigsystem.rebuildchain"
    bl_label = "Rebuild Chain"
    bl_description = "Adapt chain bones to a new structure bone"
    
    def execute(self, context):
        arm = bpy.context.active_object
        
        for b in arm.pose.bones:
            for c in b.constraints:
                if c.type == "STRETCH_TO":
                    c.rest_length = 0
                if c.type == "LIMIT_DISTANCE":
                    c.distance = 0
                    
        
        return {'FINISHED'}
    
class VTOOLS_OP_RS_setRotationMode(bpy.types.Operator):
    bl_idname = "vtoolsrigsystem.setrotationmode"
    bl_label = "Set Rotation Mode"
    bl_description = "Set the rotation mode to all bones within the chain"
    
    rotationMode : StringProperty
    
    def execute(self, context):
        arm = bpy.context.active_object
        socketBone = getChainSocketBone()
        if socketBone != None:    
            setRotationMode(arm.pose.bones[socketBone.name].rotation_mode)     
            
        return {'FINISHED'}

#----------- MAIN -----------------#

class VTOOLS_PT_ikfkSetup(bpy.types.Panel):
    bl_label = "Bone chain Builder"
    #bl_parent_id = "VTOOLS_PN_RigSystem"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Rig vTools'
    bl_options = {'DEFAULT_CLOSED'}
    

    def draw(self, context):
        layout = self.layout 
        activeBone = context.active_pose_bone
        
        if activeBone != None:           
            #box.prop(activeBone.ikfksolver, "ikchainLenght" , text = "Chain lenght", emboss = True)
            
            box = layout.box()
            box.label(text="Controls Custom Shapes")
            box.prop_search(bpy.context.scene, "fkikRoot", bpy.context.object.data, "bones", text="Root")
            box.prop_search(bpy.context.scene, "fkControlObjects", bpy.data, "objects", text="FK Shape")
            box.prop_search(bpy.context.scene, "ikControlObjects", bpy.data, "objects", text="IK Shape")
            box.prop_search(bpy.context.scene, "fkFreeControlObjects", bpy.data, "objects", text="FK Free Shape")
            #box.prop_search(bpy.context.scene, "stretchControlObjects", bpy.data, "objects", text="Stretch Shape")
            
            box = layout.box()
            box.label(text="Build")
            
            box.prop(bpy.context.scene,"addIkChain", text="Add IK Chain")
            """
            box.prop(bpy.context.scene,"isHumanoidChain", text="Humanoid")
            box.prop(bpy.context.scene,"childChainSocket", text="Child Socket")
            box.prop(bpy.context.scene,"fkStretchChain", text="Fk Stretch")
            box.prop(bpy.context.scene,"addEndBone", text="Add End Bone")
            """
            
            box.operator(VTOOLS_OP_RS_createIK.bl_idname, text="Create Chain")
            box.operator(VTOOLS_OP_RS_rebuildChain.bl_idname, text="Rebuild")

            data = getChainSocketBone()
            if data != None:
                
                box = layout.box()
                box.label(text="Rotation Mode")
                box.label(text="Selected: " + activeBone.rotation_mode)
                row = box.row()
                row.prop(data, "rotation_mode", text="")
                row.operator(VTOOLS_OP_RS_setRotationMode.bl_idname, text="", icon="LINKED")


                ikDriverProperty = findCustomProperty(data, "ikDriver")
                if ikDriverProperty != "":
                    if data[ikDriverProperty] == True:
                        ikConstraintBone = getIKConstraint(data)
                        
                        box = layout.box()
                        box.label(text="IK Pole Control")
                        box.prop(ikConstraintBone.constraints["IK"],"pole_target", text="", emboss=True);
                        box.prop_search(ikConstraintBone.constraints["IK"], "pole_subtarget", bpy.context.object.data, "bones", text="")
                        box.prop(ikConstraintBone.constraints["IK"],"pole_angle", text="Pole angle", emboss=True);
                        
               
class VTOOLS_PT_ikfkControls(bpy.types.Panel):
    bl_label = "Controls"
    #bl_parent_id = "VTOOLS_PN_RigSystem"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Rig vTools'
    bl_options = {'DEFAULT_CLOSED'}
    
        
        
    def draw(self, context):
        
        layout = self.layout
        activeBone = context.active_pose_bone
        if activeBone != None:
            
            socketProperty = findCustomProperty(activeBone, "chainSocket")
            chainSocketName = bpy.context.object.pose.bones[activeBone.name].get(socketProperty)
            
            if chainSocketName != None:
                if chainSocketName != "":
                    socketBone = bpy.context.object.pose.bones[chainSocketName]
                    
                    ikDriverProperty = findCustomProperty(socketBone, "ikDriver")
                    if ikDriverProperty != "":
                        if socketBone[ikDriverProperty] == True:

                            layout.prop(socketBone.constraints["IKControl"], "influence", text="FK/IK", emboss = True)

                            ikTargetControl = findCustomProperty(socketBone, "ikTarget")
                            ikBoneProperty = findCustomProperty(socketBone, "ikchainBone")
                            lastIkBone = socketBone[ikBoneProperty]
                            ikTargetBone = socketBone[ikTargetControl]
                            layout.prop(bpy.context.object.pose.bones[ikTargetBone].constraints["IK_stretchLimit"], "influence" , text = "Limit IK", emboss = True)
                        
                        row = layout.row()    
                        row.operator(VTOOLS_OP_RS_snapIKFK.bl_idname, text="IK-FK")
                        row.operator(VTOOLS_OP_RS_snapFKIK.bl_idname, text="FK-IK")
                    
                    if socketBone.constraints.find("limitScaleC") != -1:
                        layout.prop(socketBone.constraints["limitScaleC"], "influence", text="No Stretch", emboss = True)
                    
                    if socketBone.constraints.find("maintainVolumeC") != -1:
                        layout.prop(socketBone.constraints["maintainVolumeC"], "influence", text="Maintain Volume", emboss = True)
                    

                    
                    
            

#---------- CLASES ----------#


class VTOOLS_ikfksolver(bpy.types.PropertyGroup):
    
            
    #---------- PARAMETERS ----------#  
    
    name = bpy.props.StringProperty(default="")
    ikcontrol = bpy.props.FloatProperty(default=1.0, min=0.0, max = 1.0)
    ikDriver = bpy.props.BoolProperty(default=False)
    fkchain = bpy.props.StringProperty(default="")
    ikchain = bpy.props.StringProperty(default="")
    ikTarget = bpy.props.StringProperty(default="")
    ikchainLenght = bpy.props.IntProperty(default=3, min=1, max = 10)
    
    fkDriver = bpy.props.BoolProperty(default=False)
    fkLastBone = bpy.props.StringProperty(default="")
    fkStretchBone = bpy.props.StringProperty(default="")
    fkchainLen = bpy.props.IntProperty(default=3, min=1, max = 10)
    chainSocket = bpy.props.StringProperty(default="")
    


#---------- REGISTER ----------#
    
def register():  
    
    from bpy.utils import register_class
    
    #register_class(VTOOLS_PN_RigSystem)
    register_class(VTOOLS_PT_ikfkSetup)
    register_class(VTOOLS_PT_ikfkControls)
    
    #register_class(VTOOLS_ikfksolver)
    
    
    register_class(VTOOLS_OP_RS_addArmature)
    register_class(VTOOLS_OP_RS_createIK)
    register_class(VTOOLS_OP_RS_snapIKFK)
    register_class(VTOOLS_OP_RS_snapFKIK)
    register_class(VTOOLS_OP_RS_rebuildChain)
    register_class(VTOOLS_OP_RS_setRotationMode)
    
    
    bpy.types.Scene.fkControlObjects = bpy.props.StringProperty()
    bpy.types.Scene.fkFreeControlObjects = bpy.props.StringProperty()
    bpy.types.Scene.ikControlObjects = bpy.props.StringProperty()
    bpy.types.Scene.stretchControlObjects = bpy.props.StringProperty()
    bpy.types.Scene.fkikRoot = bpy.props.StringProperty()
    
    bpy.types.Scene.isHumanoidChain = bpy.props.BoolProperty(default = True)
    bpy.types.Scene.addIkChain = bpy.props.BoolProperty(default = True)
    bpy.types.Scene.childChainSocket = bpy.props.BoolProperty(default = True)
    bpy.types.Scene.fkStretchChain = bpy.props.BoolProperty(default = True)
    bpy.types.Scene.addEndBone = bpy.props.BoolProperty(default = True)
     
def unregister():
    
    from bpy.utils import unregister_class
    #unregister_class(VTOOLS_PN_RigSystem)
    unregister_class(VTOOLS_PT_ikfkSetup)
    unregister_class(VTOOLS_PT_ikfkControls)
    
    #unregister_class(VTOOLS_ikfksolver)
    unregister_class(VTOOLS_OP_RS_addArmature)
    unregister_class(VTOOLS_OP_RS_createIK)
    unregister_class(VTOOLS_OP_RS_snapIKFK)
    unregister_class(VTOOLS_OP_RS_snapFKIK)
    unregister_class(VTOOLS_OP_RS_rebuildChain)
    unregister_class(VTOOLS_OP_RS_setRotationMode)
    
    del bpy.types.Scene.fkControlObjects
    del bpy.types.Scene.fkFreeControlObjects
    del bpy.types.Scene.ikControlObjects
    del bpy.types.Scene.stretchControlObjects
    del bpy.types.Scene.fkikRoot
    del bpy.types.Scene.addIkChain
    del bpy.types.Scene.childChainSocket
    del bpy.types.Scene.fkStretchChain
    del bpy.types.Scene.isHumanoidChain
    del bpy.types.Scene.addEndBone
    
    
    

#---------- CLASES ----------#



if __name__ == "__main__":
    register()