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
            
    """       
    vx = math.pow((bSocket.head.x - bLast.tail.x),2)
    vy = math.pow((bSocket.head.y - bLast.tail.y),2)
    vz = math.pow((bSocket.head.z - bLast.tail.z),2)
    
    distance = math.sqrt(vx + vy + vz)
    """
    
    print("DISTANCE!! ", distance)
    
    
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
                cBone.use_connect = pConnected
                if cBone.parent != None:
                    if cBone.parent.name == b_tmp.name:
                        sortedDuplicatedBones.append(b)
                        b_tmp = pArm.data.edit_bones[b]
                
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
    
    print ("LAST BONE ", last, found)
    
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
            for bc in c: 
                arm.data.bones[bc].select = True
                arm.data.bones.active = arm.data.bones[bc]
                    
            #CREA LA CADENA    
            self.createIKFKChain()
            
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
        
    def createIKFKChain(self):
        ikTargetName = ""
        lastIKBoneName = ""
        ikChain = None
        sockectBoneName = None
        arm = bpy.data.objects[bpy.context.active_object.name]
        singleChain = False
        chainEndBoneName = None
        
        #IGNORE USED BONES
        self.ignoreUsedBones(arm)
        
        for i in range(0,len(arm.data.layers)):
            arm.data.layers[i] = True
         
        if len(bpy.context.selected_pose_bones) > 1:
            singleChain = True
            #DUPLCIATE LAST DEF BONE
            lastSelectedBoneName = findLastBoneInChain(bpy.context.selected_pose_bones)
            
        #GET SELECTED BONES
        bpy.ops.object.mode_set(mode='POSE')
        
        selBones = getSelectedChain(arm)
        
        oriBoneName = findLastBoneInChain(bpy.context.selected_pose_bones)
        firstBoneName = findFirstBoneInChain(bpy.context.selected_pose_bones)
        
        #SET CHAIN ID
        self.chainId = self.getNameId(firstBoneName)

        #CREATE CHAINS
        if oriBoneName != None and firstBoneName != None:
            
            chainLenght = len(bpy.context.selected_pose_bones)   
            bpy.context.object.data.use_mirror_x = False
            
            #CREATE CHAIN SOCKET
            
            bpy.ops.object.mode_set(mode='EDIT')
            firstBoneConnection = arm.data.edit_bones[selBones[0]].name
            sockectBoneName = ""
            
            #IF HUMANOID BREAK CONNECTION
            if bpy.context.scene.isHumanoidChain == True:
                for b in selBones:   
                    bpy.ops.object.mode_set(mode='EDIT')
                    editBone = arm.data.edit_bones[b]
                    editBone.use_connect = False 
                
            
            if firstBoneConnection != None:
                sockectBoneName = duplicateBone("SOCKETCHAIN-" + selBones[0] , arm, firstBoneConnection , bpy.context.scene.childChainSocket)
                
                bpy.ops.object.mode_set(mode='POSE')
                #REMOVE ALL CONSTRAINTS
                while len(arm.pose.bones[sockectBoneName].constraints) > 0:
                    removeC = arm.pose.bones[sockectBoneName].constraints[0]
                    arm.pose.bones[sockectBoneName].constraints.remove(removeC)
                    
                #PARENTING SOCKET BONE
                bpy.ops.object.mode_set(mode='EDIT')
                arm.data.edit_bones[sockectBoneName].use_connect = False
                arm.data.edit_bones[sockectBoneName].parent = arm.data.edit_bones[selBones[0]].parent
                if bpy.context.scene.childChainSocket == False:
                    arm.data.edit_bones[sockectBoneName].inherit_scale = "NONE"
                else: 
                    arm.data.edit_bones[sockectBoneName].inherit_scale = "FULL"
                
                #MOVE LAYER SOCKET BONE
                moveBoneToLayer(arm, sockectBoneName, 31)
                
                bpy.ops.object.mode_set(mode='POSE')
                
                tCons = arm.pose.bones[sockectBoneName].constraints.new('COPY_TRANSFORMS')
                tCons.name = "maintainVolumeC"
                tCons.influence = 1
            
            #bpy.ops.object.mode_set(mode='EDIT')
            #arm.data.edit_bones[sockectBoneName].parent = None

            bpy.ops.object.mode_set(mode='POSE')   
            
            #-- CREATE IK
            
            if bpy.context.scene.addIkChain == True:
                ikChain = self.createIKChain(chainLenght, sockectBoneName)
                lastIKBoneName = ikChain[len(ikChain)-1]
                ikTargetName = self.getTargetIK(arm,lastIKBoneName)
            
            #-- CREATE FK

            fkChain = self.createFKChain(chainLenght, sockectBoneName, ikTargetName)
            lastFkBoneName = fkChain[len(fkChain)-1]
            
            # -- CREATE FREE CONTROLS
            
            freeChain = self.createFreeChain(arm, chainLenght, sockectBoneName, fkChain, ikChain)
            
            #CREATE BENDY BONES
            bendyChain = []
            #bendyChain = self.createBendyBones()
                               
             #-- CREATE DRIVERS
            self.createCustomControlProperties(arm, sockectBoneName, lastFkBoneName, lastIKBoneName,chainLenght) 
            self.setTransformConstraints(selBones,ikChain, ikTargetName, fkChain, bendyChain, freeChain)
            
            if len(bendyChain) == 0:
                self.setSwitchDrivers(arm, selBones, ikTargetName, sockectBoneName)
            else:
                self.setSwitchDrivers(arm, bendyChain, ikTargetName, sockectBoneName)
            
            #-- MOVE BONES                
            self.moveChainToBoneLayer(arm, selBones, 0)

            #CREATE DEF CUSTOM VARIABLES
            bpy.ops.object.mode_set(mode='POSE')
            for o in selBones:
                cBone = arm.pose.bones[o]
                cBone["iktargetid"] = ikTargetName

            #--CREATE HIERARCHY CHAIN 
            if bpy.context.scene.isHumanoidChain == False:                   
                hrqChain = duplicateChainBone("hrq-", arm,16, bpy.context.scene.isHumanoidChain)
            
                #-- REPARENT DEF BONES
                bpy.ops.object.mode_set(mode='EDIT')
                
                arm.data.edit_bones[hrqChain[0]].parent = None
                if bpy.context.scene.fkikRoot != "":
                    arm.data.edit_bones[hrqChain[0]].parent = arm.data.edit_bones[bpy.context.scene.fkikRoot]

                cont = 0
                for b in selBones: 
                    arm.data.edit_bones[b].use_connect = False
                    arm.data.edit_bones[b].parent = arm.data.edit_bones[hrqChain[cont]]
                    cont += 1     
            
            #MOVE UTILS BONES
            if singleChain == True:
                bpy.ops.object.mode_set(mode='POSE')
                if chainEndBoneName != None:
                    moveBoneToLayer(arm, chainEndBoneName, 28)
            
            #-- RESET
            
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='POSE')
            
        for i in range(1,len(arm.data.layers)):
            arm.data.layers[i] = False
        
        #SET LAYER VISIBILITY / VISIBLE    
        arm.data.layers[0] = True
        arm.data.layers[1] = True
        arm.data.layers[2] = True
        arm.data.layers[3] = True
        
        
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='POSE')
                
        
    
    def setTransformConstraints(self, pDefBone, pIkChain, pIkTarget, pFkChain, pBendyChain, pFreeChain):
        
        arm = bpy.context.object
        bpy.ops.object.mode_set(mode='POSE')
        
        bcont = 0
        for b in pDefBone:
            
            pb = None
            if len(pBendyChain) == 0:
                pb = arm.pose.bones[b]
            else:
                pb = arm.pose.bones[pBendyChain[bcont]]
                
                pbs = arm.pose.bones[b]
                #TRANSFORM CONSTRAINT addtransformconstraint
                tCons = pbs.constraints.new('COPY_TRANSFORMS')
                tCons.name = "BENDY TRANSFORM"
                tCons.target = arm
                tCons.subtarget = pb.name
                tCons.target_space = 'WORLD'
                tCons.owner_space = 'WORLD'
                tCons.influence = 1
            
            #FREE  CONSTRAINT
            tCons = pb.constraints.new('COPY_TRANSFORMS')
            tCons.name = "FreeChain_transform"
            tCons.target = arm
            tCons.subtarget = arm.pose.bones[pFreeChain[bcont]].name
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
            
            if bpy.context.scene.isHumanoidChain == True:
                tCons.use_max_y = True
                tCons.max_y = 1
            
            tCons.owner_space = "LOCAL"
            
            
            #MAINTAIN VOLUME
            
            #tCons = pArm.pose.bones[pBone].constraints.new('MAINTAIN_VOLUME')
            tCons = pb.constraints.new('MAINTAIN_VOLUME')
            tCons.name = "DEF_MaintainVolume"
            tCons.free_axis = "SAMEVOL_Y"
            tCons.volume = 1
            tCons.owner_space = "LOCAL"

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
        
        
    def createCustomControlProperties(self, pArm, pSocketBoneName, pFkChainBoneName, pIkChainBoneName, pChainLen): 
        
        res = False
        bpy.ops.object.mode_set(mode='POSE')
        
        if (pArm.pose.bones.find(pSocketBoneName) != -1):
            
            ikControlBone = pArm.pose.bones[pSocketBoneName]
            
            ikControlBone[self.chainId + "_fkchainBone"] = pFkChainBoneName
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
            
            newIkTargetName = duplicateBone(("ikTarget-" + pLastBoneName), pArm, pLastBoneName, bpy.context.scene.isHumanoidChain)        
            
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
    
    def createIk(self,pArm, pIkLastBoneName, pIkTargetName, pChainLenght):
         
        
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
        newChain = duplicateChainBone("IKChain-", arm,30, bpy.context.scene.isHumanoidChain)
        
        firstChainBone = arm.data.bones[newChain[0]]
        lastIKBone = arm.data.bones[newChain[len(newChain)-1]]
        lastIKBoneName = lastIKBone.name
        
        
        ikTargetName = self.createIkTarget(arm, lastIKBoneName, newChain, pSockectBoneName)
        self.createIk(arm, lastIKBoneName, ikTargetName, cadLen) 
        
        bpy.ops.object.mode_set(mode='POSE')  
        
        #CREATE CONSTRAINT IK CONTROL IN SOCKET 
        tCons = arm.pose.bones[pSockectBoneName].constraints.new('COPY_TRANSFORMS')
        tCons.name = "IKControl"
        tCons.influence = 1
        
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
        freeChain = duplicateChainBone("FreeChain-", arm,3, False) 
        
        #CONECTAR AL SOCKET
        #bpy.ops.object.mode_set(mode='EDIT')
        #arm.data.edit_bones[freeChain[0]].parent = arm.data.edit_bones[pSockectBoneName]    
        
        print("FK ", pFKChain)
        print("IK ", pIKChain)
        
        
        #CHILDS CONTRAINTS
        if pFKChain != None:
            for i in range(0,len(freeChain)):
                
                bpy.ops.object.mode_set(mode='EDIT')
                arm.data.edit_bones[freeChain[i]].parent = arm.data.edit_bones[pFKChain[i]]
                         
                bpy.ops.object.mode_set(mode='POSE')
                
                #SET CUSTOM OBJECT
                if bpy.context.scene.fkFreeControlObjects != '':
                    arm.pose.bones[freeChain[i]].custom_shape = bpy.data.objects[bpy.context.scene.fkFreeControlObjects]
                    arm.pose.bones[freeChain[i]].use_custom_shape_bone_size = False
    
                
                #COPY IK ROTATION 
                if pIKChain != None:
                    
                    print("IK Bone ", pIKChain[i])
                    
                    #COPY LOCATION LOCAL WITHPARENT WITH OFFSET
                
                    tCons = arm.pose.bones[freeChain[i]].constraints.new('COPY_LOCATION')
                    tCons.name = "IK_LOCATION"
                    tCons.target = arm
                    tCons.subtarget = pIKChain[i]
                    tCons.use_offset = True
                    tCons.target_space = "LOCAL_WITH_PARENT"
                    tCons.owner_space = "LOCAL_WITH_PARENT"
                    tCons.influence = 1
                    
                    tCons = arm.pose.bones[freeChain[i]].constraints.new('COPY_ROTATION')
                    tCons.name = "IK_ROTATION"
                    tCons.target = arm
                    tCons.subtarget = pIKChain[i]
                    tCons.mix_mode = "BEFORE"
                    tCons.target_space = "LOCAL_WITH_PARENT"
                    tCons.owner_space = "LOCAL_WITH_PARENT"
                    tCons.influence = 1
        
                    #SET IK CONSTRAINT DRIVERS

                    for c in arm.pose.bones[freeChain[i]].constraints:
                        tmpD = c.driver_add("influence")
                        tmpD.driver.type = 'SCRIPTED'
                        tmpD.driver.expression = "ikControl"
                        
                        tmpV = tmpD.driver.variables.new()
                        tmpV.name = "ikControl"
                        tmpV.targets[0].id_type = 'OBJECT'
                        tmpV.targets[0].id = bpy.data.objects[arm.name]
                        tmpV.targets[0].data_path = "pose.bones[\""+pSockectBoneName+"\"].constraints[\"IKControl\"].influence"  
                    
                            
        return freeChain
     
    #CREATE FK CHAIN     
    def createFKChain(self, pChainLenght, pSockectBoneName, pIkTargetName):
        arm = bpy.context.active_object
        
        #SELECTED CHAIN
        
        selBones = getSelectedChain(arm)
        
        #DUPLICATE CHAINS
        
        #--FK BONES
        newChain = duplicateChainBone("FKChain-", arm,29, bpy.context.scene.isHumanoidChain) 
       
        if len(newChain) > 0:
            
            bpy.ops.object.mode_set(mode='EDIT')
            #GET LAST BONES
            lastFKBone = arm.data.bones[newChain[len(newChain)-1]]
            lastFKBoneName = lastFKBone.name        
            firstBoneName = arm.data.bones[newChain[0]].name
            
            #--FK CONTORL
            newStretchChain = duplicateChainBone("FKChainControls-", arm,2, False) 
            firstControlBoneName = arm.data.bones[newStretchChain[0]].name
    
            #--FREE FK BONES they will be created after fk controls
            freeFKChain = [] 
            
            
            #CREATE EXTRA FK CONTROL 
            if bpy.context.scene.addEndBone == True:
                bpy.ops.object.mode_set(mode='EDIT')
                
                lastFKControlBone = arm.data.bones[newStretchChain[len(newStretchChain)-1]]
                bExtraFKControlName = duplicateBone("END-" + lastFKControlBone.name , arm, lastFKControlBone.name , bpy.context.scene.isHumanoidChain)
                bExtraFKControl = arm.data.edit_bones[bExtraFKControlName]
                
                vmov = (bExtraFKControl.tail.copy() - bExtraFKControl.head.copy()) * 1
                  
                ot = bExtraFKControl.tail.copy()
                bExtraFKControl.tail += vmov
                bExtraFKControl.head = ot
                bExtraFKControl.parent = arm.data.edit_bones[lastFKControlBone.name]
                newStretchChain.append(bExtraFKControl.name)
                
                #MOVE EXTRA BONE
                moveBoneToLayer(arm, bExtraFKControl.name, 2)
            
            
            for o in newStretchChain:
                bpy.ops.object.mode_set(mode='EDIT')
                tmp_nsc = arm.data.edit_bones[o]
                tmp_nsc.use_connect = False
                
                #SET CUSTOM OBJECT
                bpy.ops.object.mode_set(mode='POSE')
                if bpy.context.scene.fkControlObjects != '': 
                    arm.pose.bones[o].custom_shape = bpy.data.objects[bpy.context.scene.fkControlObjects]
                    arm.pose.bones[o].use_custom_shape_bone_size = False
            
            #MOVE AND HIDE FIRST FK FREE CONTROL
            bpy.ops.object.mode_set(mode='EDIT')
            #moveBoneToLayer(arm, freeFKChain[0], 30)
            
            
            
            #CREATE STRETCH BONE
            nbName = ""
            nbcName = ""
            
            if len(selBones) > 1 and bpy.context.scene.fkStretchChain == True:    
                bpy.ops.object.mode_set(mode='EDIT')
                nbName = duplicateBone("FK_STRETCH-" + newChain[0] , arm, firstBoneName, False)
                nb = arm.data.edit_bones[nbName]
                nb.tail = arm.data.bones[lastFKBoneName].head_local
                arm.data.edit_bones[nbName].parent = arm.data.edit_bones[selBones[0]].parent
                
                #CREATE STRETCH CONTROL BONE
                
                nbcName = duplicateBone("FK_STRETCH_CONTROL-" + newChain[0] , arm, nbName, False)
                nbc = arm.data.edit_bones[nbcName]
                  
                nbc.head = arm.data.bones[lastFKBoneName].head_local
                nbc.tail = arm.data.bones[lastFKBoneName].tail_local
                nbc.bbone_x += 0.1
                nbc.bbone_z += 0.1
                
                #PARENT
                bpy.ops.object.mode_set(mode='EDIT')
                arm.data.edit_bones[firstControlBoneName].use_connect = False
                
                #CONECTAR AL STRETCH BONE
                arm.data.edit_bones[firstControlBoneName].parent = arm.data.edit_bones[nbName]
                
                arm.data.edit_bones[nbcName].parent =  arm.data.edit_bones[selBones[0]].parent    
                
                
                #MOVE BONE LAYERS
                moveBoneToLayer(arm, nbcName, 4)
                moveBoneToLayer(arm, nbName, 30)
            
            else:
                #CONECTAR AL SOCKET
                bpy.ops.object.mode_set(mode='EDIT')
                arm.data.edit_bones[firstControlBoneName].parent = arm.data.edit_bones[pSockectBoneName]    
           
            
            #STRETCH CUSTOM OBJECT    
            if bpy.context.scene.stretchControlObjects != '' and nbcName != "": 
                arm.pose.bones[nbcName].custom_shape = bpy.data.objects[bpy.context.scene.stretchControlObjects]
                arm.pose.bones[nbcName].use_custom_shape_bone_size = False
               
            
            
            #CREATE FK BONE CONSTRAINTS TO FK CONTROLS
            
            for i in range(0,len(newChain)):
                btmp = arm.pose.bones[newChain[i]]
                
                #PARENT FK DEF BONE TO FK CONTROL
                bpy.ops.object.mode_set(mode='EDIT')
                
                #arm.data.edit_bones[newChain[i]].parent = None
                arm.data.edit_bones[newChain[i]].use_connect = False
                arm.data.edit_bones[newChain[i]].parent = arm.data.edit_bones[newStretchChain[i]]
                
                #ADD CONSTRAINTS
                bpy.ops.object.mode_set(mode='POSE')
                
                
                #FK TRACK TO TO FREE CHAIN
                if i < len(newChain)-1:
                    tCons = btmp.constraints.new('TRACK_TO')
                    tCons.name = "FK_trackTo"
                    tCons.target = arm
                    tCons.subtarget = newChain[i+1]
                    tCons.up_axis = "UP_Z"
                    tCons.track_axis = "TRACK_Y"
                    tCons.use_target_z = True
                    tCons.influence = 1

            bpy.ops.object.mode_set(mode='POSE')            
            
            #ADD CUSTOM VARIABLES
            chains = [newStretchChain, freeFKChain]
            
            
            if pSockectBoneName != "":
                fkControlBone = arm.pose.bones[pSockectBoneName]
                
                fkControlBone[self.chainId + "_fkDriver"] = True
                fkControlBone[self.chainId + "_chainId"] = self.chainId
                fkControlBone[self.chainId + "_ikchainLenght"] = pChainLenght
                fkControlBone[self.chainId + "_fkStretchBone"] = nbName
                fkControlBone[self.chainId + "_iktargetid"] = pIkTargetName 
                
                if nbcName != "":
                    arm.pose.bones[nbcName][self.chainId + "_chainSocket"] = pSockectBoneName
                    arm.pose.bones[nbcName][self.chainId + "_chainId"] = self.chainId
                    
                    
                for c in chains:
                    i = 0
                    for i in range(0,len(c)):
                        o = c[i]
                        cBone = arm.pose.bones[o]
                        cBone[self.chainId + "_chainSocket"] = pSockectBoneName
                        cBone[self.chainId + "_chainId"] = self.chainId
                

                   
        return newChain
    
    def createBendyBones(self):
        
        arm = bpy.context.active_object
        selBones = getSelectedChain(arm)
        newChain = duplicateChainBone("BendyChain-", arm,30, bpy.context.scene.isHumanoidChain)
        
        print ("BENDY BONES ", newChain, " - ", selBones)
        
        #BENDY BONES 
        #CREATE HEAD AND TAIL CONTROLS
        numBones = len(selBones)
        bcont = 0    
        
        for b in selBones:    
            bpy.ops.object.mode_set(mode='EDIT')
            
            #print("SEL BONESSSSSSSSSSSSSSSS ", b)
            sb = arm.data.edit_bones[b]
            
            sbName = sb.name
            
            #TAIL CONTROL
            vmov_head = (sb.tail.copy() - sb.head.copy()) * 0.01
            bTailName = duplicateBone(sb.name + "_BENDYTAIL"  , arm, sb.name , False)
            bTail = arm.data.edit_bones[bTailName]
            ot = sb.tail.copy()
            bTail.tail += vmov_head
            bTail.head = ot
            
            #HEAD CONTROL
            vmov_tail = (sb.tail.copy() - sb.head.copy()) * 0.99
            bHeadName = duplicateBone(sb.name + "_BENDYHEAD"  , arm, sb.name , False)
            bHead = arm.data.edit_bones[bHeadName]
            ot = sb.head.copy()
            #bHead.head -= vmov
            bHead.tail -= vmov_tail
             
            
            #BENDY SEGMENTS
            sb.bbone_segments = 3
            sb.bbone_x /= 2 
            sb.bbone_z /= 2 
            
            #BENDY HANDLES
            sb.bbone_handle_type_start = "ABSOLUTE"
            sb.bbone_custom_handle_start = bHead
            sb.bbone_handle_type_end = "ABSOLUTE"
            sb.bbone_custom_handle_end = bTail
            
            #PARENTING
            sb.parent = bHead
            sb.use_connect = True    
            
            bHead.parent = arm.data.edit_bones[newChain[bcont]]
            bHead.use_connect = False
            bTail.parent = arm.data.edit_bones[newChain[bcont]]
            bTail.use_connect = False
            
            bpy.ops.object.mode_set(mode='POSE')
             
            #MOVE LAYER BENDY CONTROLS
            moveBoneToLayer(arm, bHeadName, 3)
            moveBoneToLayer(arm, bTailName, 3)
            
            bcont += 1
            
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
        
    def addMaintainVolumeConstraint(self, pArm, pChainBone):
        
        bpy.ops.object.mode_set(mode='POSE')
        
        for b in pChainBone:
            #tCons = pArm.pose.bones[pBone].constraints.new('MAINTAIN_VOLUME')
            tCons = b.constraints.new('MAINTAIN_VOLUME')
            tCons.name = "Maintain Volume"
            tCons.free_axis = "SAMEVOL_Y"
            tCons.volume = 1
            tCons.owner_space = "LOCAL"

        
            

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
        
        bpy.ops.object.mode_set(mode='POSE')
        
        arm = bpy.context.active_object
        data = getChainSocketBone()
        if data != None:
            
            ikChainProperty = findCustomProperty(data, "ikchainBone")
            fkchainProperty = findCustomProperty(data, "fkchainBone")
            chainLenghtProperty = findCustomProperty(data, "ikchainLenght")
            
            ikLastBone = data[ikChainProperty]
            fkLastBone = data[fkchainProperty]
            chainLenght = data[chainLenghtProperty]

            #-- sort chains
            
            currentFKBone = arm.pose.bones[fkLastBone].parent.name
            currentIKBone = ikLastBone
            fkBones = []
            ikBones = []
            for i in range(0,chainLenght):
                fkBones.insert(0, currentFKBone)
                ikBones.insert(0, currentIKBone)
                
                currentFKBone = arm.pose.bones[currentFKBone].parent.name
                currentIKBone = arm.pose.bones[currentIKBone].parent.name
        
            c = 0    
            for b in fkBones:
                bpy.ops.object.mode_set(mode='POSE')
                arm.pose.bones[b].matrix = arm.pose.bones[ikBones[c]].matrix
                #bpy.ops.object.mode_set(mode='OBJECT')
                c = c + 1
            
            bpy.ops.object.mode_set(mode='POSE')
            
        return {'FINISHED'}


class VTOOLS_OP_RS_createSocket(bpy.types.Operator):
    bl_idname = "vtoolsrigsystem.createsocket"
    bl_label = "Create Socket"
    bl_description = "Create Connector Socket"
    
    def execute(self, context):
        arm = bpy.context.active_object
        
        selBones = bpy.context.selected_pose_bones
        for o in selBones:
            
            #selectedBone = context.active_pose_bone
            selectedBone = o
            selectedBoneName = selectedBone.name
            socketBoneName = arm.pose.bones[selectedBoneName].name
            
            conectorBoneName = duplicateBone("CHAIN_END_SOCKET-" + selectedBoneName , arm, socketBoneName, True)
            
            bpy.ops.object.mode_set(mode='POSE')
            
            tCons = arm.pose.bones[conectorBoneName].constraints.new('COPY_LOCATION')
            tCons.name = "Socket_loc"
            tCons.target = arm
            tCons.subtarget = arm.pose.bones[socketBoneName].name
            tCons.head_tail = 0
            tCons.influence = 1
            tCons.target_space = "WORLD"
            tCons.owner_space = "WORLD"
            
            tCons = arm.pose.bones[conectorBoneName].constraints.new('COPY_ROTATION')
            tCons.name = "Socket_rot"
            tCons.target = arm
            tCons.subtarget = arm.pose.bones[socketBoneName].name
            tCons.influence = 1
            tCons.target_space = "LOCAL_WITH_PARENT"
            tCons.owner_space = "LOCAL_WITH_PARENT"
            
            #REPARENTING
            bpy.ops.object.mode_set(mode='EDIT')
            arm.data.edit_bones[conectorBoneName].parent = None
            if bpy.context.scene.fkikRoot != "":
                arm.data.edit_bones[conectorBoneName].parent = arm.data.edit_bones[bpy.context.scene.fkikRoot]
          
            #MOVE SOCKET
            moveBoneToLayer(arm, conectorBoneName, 31)
            
        bpy.ops.object.mode_set(mode='POSE')
        
        
         
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

#----------- MAIN -----------------#

class VTOOLS_PN_ikfkSetup(bpy.types.Panel):
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
            
            layout.prop_search(bpy.context.scene, "fkikRoot", bpy.context.object.data, "bones", text="Root")
            layout.prop_search(bpy.context.scene, "fkControlObjects", bpy.data, "objects", text="FK Shape")
            layout.prop_search(bpy.context.scene, "fkFreeControlObjects", bpy.data, "objects", text="FK Free Shape")
            layout.prop_search(bpy.context.scene, "stretchControlObjects", bpy.data, "objects", text="Stretch Shape")
            layout.prop_search(bpy.context.scene, "ikControlObjects", bpy.data, "objects", text="IK Shape")
            
            layout.prop(bpy.context.scene,"isHumanoidChain", text="Humanoid")
            layout.prop(bpy.context.scene,"addIkChain", text="Add IK Chain")
            layout.prop(bpy.context.scene,"childChainSocket", text="Child Socket")
            layout.prop(bpy.context.scene,"fkStretchChain", text="Fk Stretch")
            layout.prop(bpy.context.scene,"addEndBone", text="Add End Bone")
            
            
            layout.operator(VTOOLS_OP_RS_createIK.bl_idname, text="Create Chain")
            layout.operator(VTOOLS_OP_RS_rebuildChain.bl_idname, text="Rebuild")
            #layout.operator(VTOOLS_OP_RS_createSocket.bl_idname, text="Create Socket") 
            
            data = getChainSocketBone()
            if data != None:
                ikDriverProperty = findCustomProperty(data, "ikDriver")
                if ikDriverProperty != "":
                    if data[ikDriverProperty] == True:
                        ikConstraintBone = getIKConstraint(data)
                        layout.prop(ikConstraintBone.constraints["IK"],"pole_target", text="Pole Target Bone", emboss=True);
                        layout.prop_search(ikConstraintBone.constraints["IK"], "pole_subtarget", bpy.context.object.data, "bones", text="Bone")
                        layout.prop(ikConstraintBone.constraints["IK"],"pole_angle", text="Pole angle", emboss=True);

class VTOOLS_PN_ikfkControls(bpy.types.Panel):
    bl_label = "Controls"
    #bl_parent_id = "VTOOLS_PN_RigSystem"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Rig vTools'
    #bl_options = {'DEFAULT_OPEN'}
    
        
        
    def draw(self, context):
        
        layout = self.layout
        activeBone = context.active_pose_bone
        if activeBone != None:
            
            socketProperty = findCustomProperty(activeBone, "chainSocket")
            chainSocketName = bpy.context.object.pose.bones[activeBone.name].get(socketProperty)
            
            #print("socket Name ", chainSocketName)
            if chainSocketName != None:
                if chainSocketName != "":
                    socketBone = bpy.context.object.pose.bones[chainSocketName]
                    
                    if socketBone.constraints.find("maintainVolumeC") != -1:
                        layout.prop(socketBone.constraints["maintainVolumeC"], "influence", text="Maintain Volume", emboss = True)
                        
                        ikDriverProperty = findCustomProperty(socketBone, "ikDriver")
                        if ikDriverProperty != "":
                            if socketBone[ikDriverProperty] == True:
                                
                                
                                layout.prop(socketBone.constraints["IKControl"], "influence", text="FK/IK", emboss = True)

                                ikTargetControl = findCustomProperty(socketBone, "ikTarget")
                                ikBoneProperty = findCustomProperty(socketBone, "ikchainBone")
                                lastIkBone = socketBone[ikBoneProperty]
                                ikTargetBone = socketBone[ikTargetControl]
                                layout.prop(bpy.context.object.pose.bones[ikTargetBone].constraints["IK_stretchLimit"], "influence" , text = "IK Stretch Limit", emboss = True)
                            
                            fkDriverProperty = findCustomProperty(socketBone, "fkDriver")
                            if socketBone[fkDriverProperty] == True:
                                stretchBoneProperty = findCustomProperty(socketBone, "fkStretchBone")
                                if socketBone[stretchBoneProperty] != "":
                                    stretchBone = bpy.context.object.pose.bones[socketBone[stretchBoneProperty]]
                                    if stretchBone != "":
                                        layout.prop(stretchBone.constraints["FK_Stretch_To"],"influence", text="FK Stretch", emboss=True);
                            
                            layout.operator(VTOOLS_OP_RS_snapIKFK.bl_idname, text=VTOOLS_OP_RS_snapIKFK.bl_label)
                            layout.operator(VTOOLS_OP_RS_snapFKIK.bl_idname, text=VTOOLS_OP_RS_snapFKIK.bl_label)
                

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
    register_class(VTOOLS_PN_ikfkSetup)
    register_class(VTOOLS_PN_ikfkControls)
    
    #register_class(VTOOLS_ikfksolver)
    
    
    register_class(VTOOLS_OP_RS_addArmature)
    register_class(VTOOLS_OP_RS_createIK)
    register_class(VTOOLS_OP_RS_snapIKFK)
    register_class(VTOOLS_OP_RS_snapFKIK)
    register_class(VTOOLS_OP_RS_createSocket)
    register_class(VTOOLS_OP_RS_rebuildChain)
    
    
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
    unregister_class(VTOOLS_PN_ikfkSetup)
    unregister_class(VTOOLS_PN_ikfkControls)
    
    #unregister_class(VTOOLS_ikfksolver)
    unregister_class(VTOOLS_OP_RS_addArmature)
    unregister_class(VTOOLS_OP_RS_createIK)
    unregister_class(VTOOLS_OP_RS_snapIKFK)
    unregister_class(VTOOLS_OP_RS_snapFKIK)
    unregister_class(VTOOLS_OP_RS_createSocket)
    unregister_class(VTOOLS_OP_RS_rebuildChain)
    
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