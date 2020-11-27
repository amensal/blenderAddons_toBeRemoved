bl_info = {
    "name": "vtools - Rig System",
    "author": "Antonio Mendoza - Campero Games",
    "version": (0, 0, 3),
    "blender": (2, 80, 3),
    "location": "View3D > Tool Panel > Tool Tab >  vTools Rig System",
    "warning": "",
    "description": "Simple Rig system to create IK/FK Chain Bones",
    "category": "Animation",
}


import bpy
import os
import sys
import math
import mathutils


from bpy.props import (StringProperty,BoolProperty,IntProperty,FloatProperty,FloatVectorProperty,EnumProperty,PointerProperty)
from bpy.types import (Menu, Panel,Operator,AddonPreferences, PropertyGroup)
from bpy_extras.io_utils import ImportHelper
from rna_prop_ui import rna_idprop_ui_prop_get

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
            
def getIkControl():
    
        
    data = None
    
    obj = bpy.context.active_object
    if obj.type == 'ARMATURE':
        b = obj.pose.bones[obj.data.bones.active.name]
        if b.ikfksolver.ikDriver == True:
            data = b
        elif b.get("iktargetid") is not None:
            if b["iktargetid"] != "":
                data = obj.pose.bones[b["iktargetid"]]
    
    return data

def getChainSocketBone():
    
    socketBone = None
    activeBone = bpy.context.active_pose_bone
    if activeBone != None:
        chainSocketName = bpy.context.object.pose.bones[activeBone.name].ikfksolver.chainSocket
        if chainSocketName != "":
            socketBone = bpy.context.object.pose.bones[chainSocketName]
    
    return socketBone
                

def getIKConstraint(pIKControl):
    
    data = None
    obj = bpy.context.active_object
    
    if pIKControl is not None:
        ikLastBone = pIKControl.ikfksolver.ikchain
        data = obj.pose.bones[ikLastBone].parent
    
    return data

def getIKStretchControl(pBone):
    
    data = None
    obj = bpy.context.active_object
    
    if pBone is not None:
        ikLastBone = pIKControl.ikfksolver.ikchain
        data = obj.pose.bones[ikLastBone].parent
    
    return data  

def getBoneChainLength(pArm, pBoneChain):
    
    chainLength = len(pBoneChain)
    lastBone = pBoneChain[len(pBoneChain)-1]
    distance = 0;
    
    for i in range(0,chainLength-1):
        pb = pArm.data.bones[pBoneChain[i]]
        distance += pb.length 
            
    """        
    vx = math.pow((pBone.tail.x - pBone.head.x),2)
    vy = math.pow((pBone.tail.y - pBone.head.y),2)
    vz = math.pow((pBone.tail.z - pBone.head.z),2)
    
    distance = math.sqrt(vx + vy + vz)
    print("DISTANCE!! ", distance)
    """
    
    return distance + pArm.data.bones[lastBone].head_radius
    

def moveBoneToLayer(pArm, pSelBoneBone, pLayerDest):
        
        bpy.ops.object.mode_set(mode='POSE')
        if pSelBoneBone in pArm.data.bones != False:
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
        
        """
        boneChainNames.append(b.name)
        """
        
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
            newBone.parent = oldBone.parent
    
    return newBoneName


    
def duplicateChainBone(pChainPrefix, pArm, pLayer):
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
                nb.use_connect = True
            
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
            for c in b.children:
                if (c == None) or (c not in pChain):
                    found = True
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
        """
        b.tail.x *= vmov.x
        b.tail.y *= vmov.y
        b.tail.z *= vmov.z
        """
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

    def execute(self, context):
        arm = bpy.data.objects[bpy.context.active_object.name]
        selBones = getSelectedChain(arm)
        
        ikTargetName = ""
        lastIKBoneName = ""
        ikChain = None
        
        bpy.ops.object.mode_set(mode='POSE')
        
        oriBoneName = findLastBoneInChain(bpy.context.selected_pose_bones)
        firstBoneName = findFirstBoneInChain(bpy.context.selected_pose_bones)
        sockectBoneName = None
        
        if oriBoneName != None:
            
            chainLenght = len(bpy.context.selected_pose_bones)   
            bpy.context.object.data.use_mirror_x = False
            
            #CREATE CHAIN SOCKET
            
            bpy.ops.object.mode_set(mode='EDIT')
            firstBoneConnection = arm.data.edit_bones[selBones[0]].name
            sockectBoneName = ""
            
            if firstBoneConnection != None:
                sockectBoneName = duplicateBone("SOCKETCHAIN_" + selBones[0] , arm, firstBoneConnection , bpy.context.scene.childChainSocket)
                
                #PARENTING SOCKET BONE
                bpy.ops.object.mode_set(mode='EDIT')
                arm.data.edit_bones[sockectBoneName].parent = arm.data.edit_bones[selBones[0]].parent
                if bpy.context.scene.childChainSocket == False:
                    arm.data.edit_bones[sockectBoneName].inherit_scale = "NONE"
                else: 
                    arm.data.edit_bones[sockectBoneName].inherit_scale = "FULL"
                
                #MOVE LAYER SOCKET BONE
                moveBoneToLayer(arm, sockectBoneName, 31)
                
                bpy.ops.object.mode_set(mode='POSE')
            """
            #SOCKET CONSTRAINT       
            if arm.pose.bones[selBones[0]].parent != None:
                    
                #LOC CONSTRAINT TO SOCKECT
                tCons = arm.pose.bones[sockectBoneName].constraints.new('COPY_LOCATION')
                tCons.name = "Socket_loc"
                tCons.target = arm
                tCons.subtarget = arm.pose.bones[selBones[0]].parent.name
                tCons.head_tail = 1
                tCons.influence = 1
                tCons.use_offset = False
                tCons.target_space = "POSE"
                tCons.owner_space = "POSE"
            """        
                
                
            #REPARENT FIRST BONE
            bpy.ops.object.mode_set(mode='EDIT')
            arm.data.edit_bones[firstBoneConnection].use_connect = False
            arm.data.edit_bones[firstBoneConnection].parent = arm.data.edit_bones[sockectBoneName] 
            
            #bpy.ops.object.mode_set(mode='EDIT')
            #arm.data.edit_bones[sockectBoneName].parent = None
                
            """
            if bpy.context.scene.fkikRoot != "":
                arm.data.edit_bones[sockectBoneName].parent = arm.data.edit_bones[bpy.context.scene.fkikRoot]
            """

            bpy.ops.object.mode_set(mode='POSE')   
            
            #-- CREATE IK
            
            if bpy.context.scene.addIkChain == True:
                ikChain = self.createIKChain(chainLenght, sockectBoneName)
                lastIKBoneName = ikChain[len(ikChain)-1]
                ikTargetName = self.getTargetIK(arm,lastIKBoneName)
            
            #-- CREATE FK

            fkChain = self.createFKChain(chainLenght, sockectBoneName, ikTargetName)
            lastFkBoneName = fkChain[len(fkChain)-1]
            
            #CREATE BENDY BONES
            bendyChain = []
            #bendyChain = self.createBendyBones()
                               
             #-- CREATE DRIVERS
            self.createCustomControlProperties(arm, sockectBoneName, lastFkBoneName, lastIKBoneName,chainLenght) 
            self.setTransformConstraints(selBones,ikChain, ikTargetName, fkChain, bendyChain)
            
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
            hrqChain = duplicateChainBone("hrq_", arm,16)
            
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
                
                """
                if sockectBoneName != None:
                    arm.data.edit_bones[b].parent = arm.data.edit_bones[sockectBoneName]   
                else:
                    arm.data.edit_bones[b].parent = None
                """
        
            #-- RESET
            
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='POSE')
                
        return {'FINISHED'}
    
    def setTransformConstraints(self, pDefBone, pIkChain, pIkTarget, pFkChain, pBendyChain):
        
        arm = bpy.context.object
        bpy.ops.object.mode_set(mode='POSE')
        
        bcont = 0
        for b in pDefBone:
            
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
            
            
            #IK CONSTRAINT
            
            if pIkTarget != "":
                    
                if bcont == (len(pDefBone)-1):
                    #IK CONSTRAINT LAST BONE POSITION AND ROTATION addtransformconstraint
                    
                    
                    tCons = pb.constraints.new('COPY_TRANSFORMS')
                    tCons.name = "IK_transform"
                    tCons.target = arm
                    tCons.subtarget = arm.pose.bones[pIkTarget].name
                    tCons.target_space = 'WORLD'
                    tCons.owner_space = 'WORLD'
                    tCons.influence = 1
                    
                    """
                    tCons = pb.constraints.new('COPY_LOCATION')
                    tCons.name = "IK_transform_loc"
                    tCons.target = arm
                    tCons.subtarget = arm.pose.bones[pIkChain[bcont]].name
                    tCons.target_space = 'WORLD'
                    tCons.owner_space = 'WORLD'
                    tCons.influence = 1
                    
                    tCons = pb.constraints.new('COPY_ROTATION')
                    tCons.name = "IK_transform_rot"
                    tCons.target = arm
                    tCons.subtarget = arm.pose.bones[pIkChain[bcont]].name
                    tCons.target_space = 'WORLD'
                    tCons.owner_space = 'WORLD'
                    tCons.influence = 1
                    """
                    
                else:
                    #IK CONSTRAINT addtransformconstraint
                    tCons = pb.constraints.new('COPY_TRANSFORMS')
                    tCons.name = "IK_transform"
                    tCons.target = arm
                    tCons.subtarget = arm.pose.bones[pIkChain[bcont]].name
                    tCons.target_space = 'WORLD'
                    tCons.owner_space = 'WORLD'
                    tCons.influence = 1
                
        
            #FK CONSTRAINT addtransformconstraint
            tCons = pb.constraints.new('COPY_TRANSFORMS')
            tCons.name = "FK_transform"
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
            
            #MAINTAIN VOLUME
            
            #tCons = pArm.pose.bones[pBone].constraints.new('MAINTAIN_VOLUME')
            tCons = pb.constraints.new('MAINTAIN_VOLUME')
            tCons.name = "DEF_MaintainVolume"
            tCons.free_axis = "SAMEVOL_Y"
            tCons.volume = 1
            tCons.owner_space = "LOCAL"
            
            
            """
            #BENDY CONSTRAINT TO DEF BONES (to swap between IK and FK)
            pb = arm.pose.bones[newChain[bcont]]
            tCons = pb.constraints.new('COPY_TRANSFORMS')
            tCons.name = "Bendy transform"
            tCons.target = arm
            tCons.subtarget = arm.pose.bones[selBones[bcont]].name
            tCons.target_space = 'WORLD'
            tCons.owner_space = 'WORLD'
            tCons.influence = 1
            """
            
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
            ikControlBone.ikfksolver.fkchain = pFkChainBoneName
            ikControlBone.ikfksolver.ikchain = pIkChainBoneName
            ikControlBone.ikfksolver.ikchainLenght = pChainLen
                
            res = True
            
        return res
        
        
    def setSwitchDrivers(self, pArm, pDefChain, pIkTargetName, pFKSocket):
        
        #if pIkTargetName != "":
        for i in range(0,len(pDefChain)):
            tmp_oriBone = pDefChain[i]
            if tmp_oriBone != None:
               
                for c in pArm.pose.bones[tmp_oriBone].constraints:
                    if pIkTargetName != "":
                        if "IK" in c.name:
                            tmpD = c.driver_add("influence")
                            tmpD.driver.type = 'SCRIPTED'
                            tmpD.driver.expression = "ikControl"
                            
                            tmpV = tmpD.driver.variables.new()
                            tmpV.name = "ikControl"
                            tmpV.targets[0].id_type = 'OBJECT'
                            tmpV.targets[0].id = bpy.data.objects[pArm.name]
                            tmpV.targets[0].data_path = "pose.bones[\""+pFKSocket+"\"].ikcontrol"  
                            #tmpV.targets[0].data_path = "pose.bones[\""+pIkTarget.name+"\"].constraints[\"IKControl\"].influence"
                            #tmpV.targets[0].data_path = "pose.bones[\""+pIkTargetName+"\"][\"ikcontrol\"]"     
                            
                        elif "FK" in c.name:
                            tmpD = c.driver_add("influence")
                            tmpD.driver.type = 'SCRIPTED'
                            tmpD.driver.expression = "1 - ikControl"
                            
                            tmpV = tmpD.driver.variables.new()
                            tmpV.name = "ikControl"
                            tmpV.targets[0].id_type = 'OBJECT'
                            tmpV.targets[0].id = bpy.data.objects[pArm.name]
                            tmpV.targets[0].data_path = "pose.bones[\""+pFKSocket+"\"].ikcontrol"  
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
                        tmpV.targets[0].data_path = "pose.bones[\""+pFKSocket+"\"].maintainVolumeC" 
            
                
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
               
    def createIkTarget(self, pArm, pLastBoneName, pChain):
        
        bpy.ops.object.mode_set(mode='POSE')
        newIkTargetName = None
        
        #self.selectBone(arm,"")
        #sBone = self.selectBone(pArm,pSelBone)    
        ikTarget = None
        
        if (pArm.pose.bones.find(pLastBoneName) != -1):
            
            newIkTargetName = duplicateBone(("ikTarget_" + pLastBoneName), pArm, pLastBoneName, False)        
            
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
                
                #constraint LIMIT DISTANCE for ik stretch
                tCons = pArm.pose.bones[pLastBoneName].constraints.new('LIMIT_DISTANCE')
                tCons.name = "IK_stretchLimit"
                tCons.target = pArm
                tCons.subtarget = pArm.pose.bones[pChain[0]].name #CAMBIO
                tCons.distance = getBoneChainLength(pArm,pChain)
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
        
        arm = bpy.context.active_object
        selBones = getSelectedChain(arm)
        cadLen = pChainLenght
        lastIKBoneName = None
        newChain = duplicateChainBone("IKChain_", arm,30)
        
        firstChainBone = arm.data.bones[newChain[0]]
        lastIKBone = arm.data.bones[newChain[len(newChain)-1]]
        lastIKBoneName = lastIKBone.name
        
        
        ikTargetName = self.createIkTarget(arm, lastIKBoneName, newChain)
        self.createIk(arm, lastIKBoneName, ikTargetName, cadLen) 
        
        bpy.ops.object.mode_set(mode='POSE')  
        
        #MOVE BONE
        moveBoneToLayer(arm, ikTargetName, 1)
        
        
        bcont = 0
        for b in newChain:
            arm.pose.bones[b].ik_stretch = 0.1
            
        #CREATE DEF CUSTOM PROPERTIES
        bpy.ops.object.mode_set(mode='POSE')
        
        if (pSockectBoneName != ""):
            
            ikControlBone = arm.pose.bones[pSockectBoneName]
            ikControlBone.ikfksolver.ikDriver = True
            ikControlBone.ikfksolver.ikchainLenght = pChainLenght
            ikControlBone.ikfksolver.ikTarget = ikTargetName
                
            for b in newChain:
                
                tmp_b = arm.pose.bones[b]
                #SET IK STRETCH
                tmp_b.ik_stretch = 0.1
                
                #CUSTOM PROP
                tmp_b.ikfksolver.chainSocket = pSockectBoneName
                
            
            arm.pose.bones[ikTargetName].ikfksolver.chainSocket = pSockectBoneName
    
        return newChain
    
    def createFKChain(self, pChainLenght, pSockectBoneName, pIkTargetName):
        arm = bpy.context.active_object
        
        #SELECTED CHAIN
        
        selBones = getSelectedChain(arm)
        
        #DUPLICATE CHAINS
        
        #--FK BONES
        newChain = duplicateChainBone("FKChain_", arm,29) 
       
        if len(newChain) > 0:
            
            bpy.ops.object.mode_set(mode='EDIT')
            #GET LAST BONES
            lastFKBone = arm.data.bones[newChain[len(newChain)-1]]
            lastFKBoneName = lastFKBone.name        
            firstBoneName = arm.data.bones[newChain[0]].name
            
            #--FK CONTORL
            newStretchChain = duplicateChainBone("FKChainControls_", arm,2) 
            firstControlBoneName = arm.data.bones[newStretchChain[0]].name
            
            
                
            #--FREE FK BONES they will be created after fk controls
            freeFKChain = [] 
            
            #CREATE EXTRA FK CONTROL 
            bpy.ops.object.mode_set(mode='EDIT')
            
            lastFKControlBone = arm.data.bones[newStretchChain[len(newStretchChain)-1]]
            bExtraFKControlName = duplicateBone(lastFKControlBone.name + "_END" , arm, lastFKControlBone.name , False)
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
                
                #CREATE FREE FK CONTROLS
              #  tmp_freeName = o.Copy()
                tmp_freeName = o.replace("FKChainControls_","FKFreeControl_")
                tmp_freeControlName = duplicateBone(tmp_freeName, arm, o , False)
                tmp_freeControlBone = arm.data.edit_bones[tmp_freeControlName]
                
                tmp_freeControlBone.parent = None
                tmp_freeControlBone.parent = tmp_nsc
                
                moveBoneToLayer(arm, tmp_freeControlName, 3)
                
                freeFKChain.append(tmp_freeControlName)
                
                #SET CUSTOM OBJECT
                bpy.ops.object.mode_set(mode='POSE')
                if bpy.context.scene.fkControlObjects != '': 
                    arm.pose.bones[o].custom_shape = bpy.data.objects[bpy.context.scene.fkControlObjects]
                    arm.pose.bones[o].use_custom_shape_bone_size = False
                    
                #SET CUSTOM OBJECT
                if bpy.context.scene.fkFreeControlObjects != '':
                    arm.pose.bones[tmp_freeControlName].custom_shape = bpy.data.objects[bpy.context.scene.fkFreeControlObjects]
                    arm.pose.bones[tmp_freeControlName].use_custom_shape_bone_size = False
                
            
            #MOVE AND HIDE FIRST FK FREE CONTROL
            bpy.ops.object.mode_set(mode='EDIT')
            moveBoneToLayer(arm, freeFKChain[0], 30)
            
            #CREATE STRETCH BONE
            nbName = ""
            nbcName = ""
            
            if len(selBones) > 1 and bpy.context.scene.fkStretchChain == True:    
                bpy.ops.object.mode_set(mode='EDIT')
                nbName = duplicateBone("FK_STRETCH_" + newChain[0] , arm, firstBoneName, False)
                nb = arm.data.edit_bones[nbName]
                nb.tail = arm.data.bones[lastFKBoneName].head_local
                arm.data.edit_bones[nbName].parent = arm.data.edit_bones[selBones[0]].parent
                
                #CREATE STRETCH CONTROL BONE
                
                nbcName = duplicateBone("FK_STRETCH_CONTROL_" + newChain[0] , arm, nbName, False)
                nbc = arm.data.edit_bones[nbcName]
                  
                nbc.head = arm.data.bones[lastFKBoneName].head_local
                nbc.tail = arm.data.bones[lastFKBoneName].tail_local
                nbc.bbone_x += 0.1
                nbc.bbone_z += 0.1
                
                #CREATE STRETCH BONE CONSTRAINTS 
                
                bpy.ops.object.mode_set(mode='POSE')
                tCons = arm.pose.bones[nbName].constraints.new('STRETCH_TO')
                tCons.name = "FK_Stretch_To"
                tCons.target = arm
                tCons.subtarget = nbcName
                tCons.influence = 1
                
                
                #PARENT
                bpy.ops.object.mode_set(mode='EDIT')
                arm.data.edit_bones[firstControlBoneName].use_connect = False
                
                #CONECTAR AL STRETCH BONE
                arm.data.edit_bones[firstControlBoneName].parent = arm.data.edit_bones[nbName]
                
                arm.data.edit_bones[nbcName].parent =  arm.data.edit_bones[selBones[0]].parent    
                
                #STRETCH CUSTOM VARIABLES    
                arm.pose.bones[nbcName]["iktargetid"] = pIkTargetName
                arm.pose.bones[nbcName].ikfksolver.fkDriver = True
                arm.pose.bones[nbcName].ikfksolver.fkStretchBone = nbName
                
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
                
                #FK LOCATION
                tCons = btmp.constraints.new('COPY_LOCATION')
                tCons.name = "FK_location"
                tCons.target = arm
                tCons.subtarget = freeFKChain[i]
                tCons.influence = 1
                tCons.target_space = 'LOCAL'
                tCons.owner_space = 'LOCAL'
                
                #FK STRETCH TO TO FREE CHAIN
                tCons = btmp.constraints.new('STRETCH_TO')
                tCons.name = "Stretch_To"
                tCons.target = arm
                tCons.subtarget = freeFKChain[i+1]
                tCons.influence = 1
                tCons.volume = "NO_VOLUME"
                
                
            bpy.ops.object.mode_set(mode='POSE')            
            
            #ADD CUSTOM VARIABLES
            chains = [newStretchChain, freeFKChain]
            
            
            if pSockectBoneName != "":
                fkControlBone = arm.pose.bones[pSockectBoneName]
                fkControlBone.ikfksolver.fkDriver = True
                fkControlBone.ikfksolver.ikchainLenght = pChainLenght
                fkControlBone.ikfksolver.fkStretchBone = nbName
                fkControlBone["iktargetid"] = pIkTargetName 
                
                if nbcName != "":
                    arm.pose.bones[nbcName].ikfksolver.chainSocket = pSockectBoneName
                    
                    
                for c in chains:
                    i = 0
                    for i in range(0,len(c)):
                        o = c[i]
                        cBone = arm.pose.bones[o]
                        
                        cBone.ikfksolver.fkLastBone = c[len(c)-1]
                        cBone.ikfksolver.fkchainLen = len(c)
                        cBone.ikfksolver.chainSocket = pSockectBoneName
                

                   
        return newChain
    
    def createBendyBones(self):
        
        arm = bpy.context.active_object
        selBones = getSelectedChain(arm)
        newChain = duplicateChainBone("BendyChain_", arm,30)
        
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
            
            """
            #BENDY STRETCH TO CONSTRAINT 
            tCons = arm.pose.bones[selBones[bcont]].constraints.new('STRETCH_TO')
            tCons.name = "Bendy_Stretch_To"
            tCons.target = arm
            tCons.subtarget = bTailName
            tCons.influence = 1
            """
                   
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
            arm.pose.bones[data.ikfksolver.ikTarget].matrix = arm.pose.bones[data.ikfksolver.fkchain].matrix
                
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
            
            ikLastBone = data.ikfksolver.ikchain
            fkLastBone = data.ikfksolver.fkchain
            chainLenght = data.ikfksolver.ikchainLenght

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
            
            conectorBoneName = duplicateBone("CHAIN_END_SOCKET_" + selectedBoneName , arm, socketBoneName, True)
            
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
            
            """
            arm.data.edit_bones[socketBoneName].parent = arm.data.edit_bones[conectorBoneName]
            arm.data.edit_bones[socketBoneName].use_connect = True
            
            
            arm.data.edit_bones[conectorBoneName].parent = None
            if bpy.context.scene.fkikRoot != "":
                arm.data.edit_bones[conectorBoneName].parent = arm.data.edit_bones[bpy.context.scene.fkikRoot]
            """
            
        bpy.ops.object.mode_set(mode='POSE')
        
        
         
        return {'FINISHED'}
            
#----------- MAIN -----------------#

class VTOOLS_PN_ikfkSetup(bpy.types.Panel):
    bl_label = "Setup"
    bl_parent_id = "VTOOLS_PN_RigSystem"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    #bl_options = {'DEFAULT_CLOSED'}
    

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
            
            layout.prop(bpy.context.scene,"addIkChain", text="Add IK Chain")
            layout.prop(bpy.context.scene,"childChainSocket", text="Child Socket")
            layout.prop(bpy.context.scene,"fkStretchChain", text="Fk Stretch")
            
            layout.operator(VTOOLS_OP_RS_createIK.bl_idname, text="Create Chain")
            layout.operator(VTOOLS_OP_RS_createSocket.bl_idname, text="Create Socket") 
            
            data = getChainSocketBone()
            if data != None:
                if data.ikfksolver.ikDriver == True:
                    ikConstraintBone = getIKConstraint(data)
                    layout.prop(ikConstraintBone.constraints["IK"],"pole_target", text="Pole Target Bone", emboss=True);
                    layout.prop_search(ikConstraintBone.constraints["IK"], "pole_subtarget", bpy.context.object.data, "bones", text="Bone")
                    layout.prop(ikConstraintBone.constraints["IK"],"pole_angle", text="Pole angle", emboss=True);

class VTOOLS_PN_ikfkControls(bpy.types.Panel):
    bl_label = "Controls"
    bl_parent_id = "VTOOLS_PN_RigSystem"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    #bl_options = {'DEFAULT_CLOSED'}
    

    def draw(self, context):
        
        layout = self.layout
        activeBone = context.active_pose_bone
        if activeBone != None:
            
            chainSocketName = bpy.context.object.pose.bones[activeBone.name].ikfksolver.chainSocket
            
            if chainSocketName != "":
                socketBone = bpy.context.object.pose.bones[chainSocketName]
                
                layout.prop(socketBone, "maintainVolumeC", text="Maintain Volume", emboss = True)
                
                if socketBone.ikfksolver.ikDriver == True:
                    layout.prop(socketBone, "ikcontrol", text="FK/IK", emboss = True)
                    lastIkBone = socketBone.ikfksolver.ikchain
                    layout.prop(bpy.context.object.pose.bones[lastIkBone].constraints["IK_stretchLimit"], "influence" , text = "IK Stretch Limit", emboss = True)
                if socketBone.ikfksolver.fkDriver == True:
                    stretchBone = bpy.context.object.pose.bones[socketBone.ikfksolver.fkStretchBone]
                    if stretchBone != "":
                        layout.prop(stretchBone.constraints["FK_Stretch_To"],"influence", text="FK Stretch", emboss=True);
            
            layout.operator(VTOOLS_OP_RS_snapIKFK.bl_idname, text=VTOOLS_OP_RS_snapIKFK.bl_label)
            layout.operator(VTOOLS_OP_RS_snapFKIK.bl_idname, text=VTOOLS_OP_RS_snapFKIK.bl_label)
                
                      
class VTOOLS_PN_RigSystem(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "vTools Rig System"
    bl_category = 'Tool'
    #bl_options = {'DEFAULT_CLOSED'} 
    
        
    @classmethod
    def poll(cls, context):
        return (context.mode == "POSE" or context.mode == "EDIT_ARMATURE")
    
    def draw(self,context):
        
        layout = self.layout
        
        if bpy.context.object:    
            """ 
            row = layout.row()
            box = row.box()
            box.label("Sprite Tools")
            
            row = layout.row()
            box = row.box()
            box.label("Vector Tools")
            
            
            row = layout.row()
            box = row.box()
            box.label("Armature Tools")
            
            row = layout.row()
            box = row.box()
            box.label("Animation Tools") 
            """ 

    
#---------- CLASES ----------#


class VTOOLS_ikfksolver(bpy.types.PropertyGroup):
    
            
    #---------- PARAMETERS ----------#  
    
    name = bpy.props.StringProperty(default="")
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
    
    register_class(VTOOLS_PN_RigSystem)
    register_class(VTOOLS_PN_ikfkSetup)
    register_class(VTOOLS_PN_ikfkControls)
    
    register_class(VTOOLS_ikfksolver)
    
    
    register_class(VTOOLS_OP_RS_addArmature)
    register_class(VTOOLS_OP_RS_createIK)
    register_class(VTOOLS_OP_RS_snapIKFK)
    register_class(VTOOLS_OP_RS_snapFKIK)
    register_class(VTOOLS_OP_RS_createSocket)
    
    
    bpy.types.PoseBone.ikfksolver = bpy.props.PointerProperty(type=VTOOLS_ikfksolver)
    bpy.types.PoseBone.ikcontrol = bpy.props.FloatProperty(default=1.0, min=0.0, max = 1.0)
    bpy.types.PoseBone.maintainVolumeC = bpy.props.FloatProperty(default=1.0, min=0.0, max = 1.0)
    
    bpy.types.Scene.fkControlObjects = bpy.props.StringProperty()
    bpy.types.Scene.fkFreeControlObjects = bpy.props.StringProperty()
    bpy.types.Scene.ikControlObjects = bpy.props.StringProperty()
    bpy.types.Scene.stretchControlObjects = bpy.props.StringProperty()
    bpy.types.Scene.fkikRoot = bpy.props.StringProperty()
    
    bpy.types.Scene.addIkChain = bpy.props.BoolProperty(default = True)
    bpy.types.Scene.childChainSocket = bpy.props.BoolProperty(default = True)
    bpy.types.Scene.fkStretchChain = bpy.props.BoolProperty(default = True)
     
def unregister():
    
    from bpy.utils import unregister_class
    unregister_class(VTOOLS_PN_RigSystem)
    unregister_class(VTOOLS_PN_ikfkSetup)
    unregister_class(VTOOLS_PN_ikfkControls)
    
    unregister_class(VTOOLS_ikfksolver)
    unregister_class(VTOOLS_OP_RS_addArmature)
    unregister_class(VTOOLS_OP_RS_createIK)
    unregister_class(VTOOLS_OP_RS_snapIKFK)
    unregister_class(VTOOLS_OP_RS_snapFKIK)
    unregister_class(VTOOLS_OP_RS_createSocket)
    
    
    del bpy.types.PoseBone.ikfksolver
    del bpy.types.PoseBone.ikcontrol
    del bpy.types.Scene.fkControlObjects
    del bpy.types.Scene.fkFreeControlObjects
    del bpy.types.Scene.ikControlObjects
    del bpy.types.Scene.stretchControlObjects
    del bpy.types.Scene.fkikRoot
    del bpy.types.Scene.addIkChain
    del bpy.types.Scene.childChainSocket
    del bpy.types.Scene.fkStretchChain
    
    
    

#---------- CLASES ----------#



if __name__ == "__main__":
    register()