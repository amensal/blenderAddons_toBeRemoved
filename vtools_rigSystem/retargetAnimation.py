import bpy
import mathutils


    
def retargetByName(pArmName, pArmDestName, pNamePatterns, pRotationOnly):
    
    arm = bpy.data.objects[pArmName]
    armDest = bpy.data.objects[pArmDestName]
    
    np = pNamePatterns.split(",")
    
    bpy.ops.object.mode_set(mode='EDIT')
    selBones = bpy.context.selected_bones

    bpy.ops.object.mode_set(mode='POSE')

    for b in arm.pose.bones:
        found = False
        #CHECK IF IS A RETARGEABLE BONE
        for pattern in np: 
            if b.name.find(pattern) != -1: 
                found = True
                
                #print("Base Name: ", b.name)
                

                #FIND TARGET BONE
                targetBoneName = None
                for tb in armDest.pose.bones:
                    for p in np:
                        #print("BUSCANDO ", tb.name)
                        if b.name.find(tb.name) != -1 and b.name.find(p) != -1 and b.name.find("END") == -1:
                             #print("ENCONTRADO ", tb.name)
                             targetBoneName = tb.name
                             break
     
                #ADD CONSTRAINT
                if targetBoneName != None:
                    
                    if pRotationOnly == False:
                        """
                        pb = arm.pose.bones[b.name]
                        tCons = pb.constraints.new('COPY_TRANSFORMS')
                        tCons.name = "Retarget_transform"
                        tCons.target = armDest
                        tCons.subtarget = targetBoneName
                        tCons.target_space = 'LOCAL'
                        tCons.owner_space = 'LOCAL'
                        tCons.influence = 1
                        """ 
                        
                        
                        
                        #IF ROOT
                        
                        if targetBoneName == bpy.context.scene.vtoolRootBone:
                            
                            pb = arm.pose.bones[b.name]
                            tCons = pb.constraints.new('COPY_TRANSFORMS')
                            tCons.name = "Retarget_copyTransform"
                            tCons.target = armDest
                            tCons.subtarget = targetBoneName
                            tCons.target_space = 'WORLD'
                            tCons.owner_space = 'WORLD'
                            tCons.influence = 1
                        
                        else: 
                            
                            pb = arm.pose.bones[b.name] 
                            tCons = pb.constraints.new('DAMPED_TRACK')
                            tCons.name = "Retarget_dampedTrack"
                            tCons.head_tail = 1
                            tCons.track_axis = "TRACK_Y"
                            tCons.target = armDest
                            tCons.subtarget = targetBoneName
                            tCons.influence = 1
                            
                            
                    else:
                        
                        
                        pb = arm.pose.bones[b.name] 
                        tCons = pb.constraints.new('COPY_ROTATION')
                        tCons.name = "Retarget_rotation"
                        tCons.target = armDest
                        tCons.subtarget = targetBoneName
                        tCons.target_space = 'LOCAL_WITH_PARENT'
                        tCons.owner_space = 'LOCAL'
                        tCons.influence = 1
                    
                        pb = arm.pose.bones[b.name] 
                        tCons = pb.constraints.new('COPY_LOCATION')
                        tCons.name = "Retarget_location"
                        tCons.target = armDest
                        tCons.subtarget = targetBoneName
                        tCons.target_space = 'WORLD'
                        tCons.owner_space = 'WORLD'
                        tCons.influence = 1
                        
                        
                        
                  
                #END THE LOOP IF IT WAS A RETARGEABLE BONE    
                break

def duplicateArmatures(pArmName, pArmDestName):
    
    arm = bpy.data.objects[pArmName]
    armDest = bpy.data.objects[pArmDestName]
    
    retargetArm = arm.copy()
    retargetArm.data = retargetArm.data.copy()
    animatedArm = armDest.copy()
    animatedArm.data = animatedArm.data.copy()
    armatures = [retargetArm.name, animatedArm.name]
    
    bpy.context.collection.objects.link(retargetArm)
    bpy.context.collection.objects.link(animatedArm)
    
    retargetArm.animation_data_clear()
    animatedArm.animation_data_clear()
    
    #--CLEAR TRANSFORM
    
    for obj in bpy.context.view_layer.objects: 
        bpy.data.objects[obj.name].select_set(False)
        
    
    bpy.data.objects[retargetArm.name].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[retargetArm.name]
    
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action="SELECT")
    bpy.ops.pose.transforms_clear()
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    bpy.data.objects[animatedArm.name].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[animatedArm.name]
    bpy.data.objects[retargetArm.name].select_set(False)
    
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action="SELECT")
    bpy.ops.pose.transforms_clear()
    
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.rotation_clear(clear_delta = False)
    bpy.ops.object.location_clear(clear_delta = False)
    
    
    
    #UNPARENT ALL BONES
    
    #print("ARMATURES ", armatures)
    for a in armatures:
        
        #SELECT  ARMATURE
        bpy.ops.object.select_all(action="DESELECT")
        bpy.data.objects[a].select_set(True)
        bpy.context.view_layer.objects.active = bpy.data.objects[a]
        
        bpy.ops.object.mode_set(mode='EDIT')
    
        #print("ENTRA")
        for b in bpy.data.objects[a].data.edit_bones:
            b.use_connect = False
            b.parent = None
        
        bpy.ops.object.mode_set(mode='OBJECT')
    
    #POSITION
    bpy.data.objects[retargetArm.name].location = bpy.data.objects[animatedArm.name].location
    
    return [animatedArm.name, retargetArm.name]
    
    
def findNearestBones(pArmName, pNamePatterns, pTolerance, pAnimatedArm, pRetargetArm):
    
    arm = bpy.data.objects[pArmName]
    
    tolerance = mathutils.Vector([pTolerance, pTolerance, pTolerance])
    boneList = []
    np = pNamePatterns.split(",")
    #print("FIND NEAREST ")
    #Find nearest animated bone by position
    
    #SELECT  ARMATURE
    bpy.ops.object.select_all(action="DESELECT")
    bpy.data.objects[pRetargetArm].select_set(True)
    bpy.data.objects[pAnimatedArm].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[pRetargetArm]
       
       
    #print("ARMATURE ACTIVO", bpy.context.view_layer.objects.active)
     
    bpy.ops.object.mode_set(mode='EDIT')
    for b in bpy.data.objects[pRetargetArm].data.edit_bones:
        tmp_nearestBones = []
        for pattern in np: 
            if b.name.find(pattern) != -1:        
                nearestBone = None
                currentDist = mathutils.Vector([100000,100000,100000])
                bpy.context.view_layer.objects.active = bpy.data.objects[pAnimatedArm]
                for ba in bpy.data.objects[pAnimatedArm].data.edit_bones:
                    dist = (b.head*bpy.data.objects[pRetargetArm].scale.x) - (ba.head*bpy.data.objects[pAnimatedArm].scale.x)
                    distTail = (b.tail*bpy.data.objects[pRetargetArm].scale.x) - (ba.tail*bpy.data.objects[pAnimatedArm].scale.x)
                    if dist < tolerance and distTail < tolerance:
                        tmp_nearestBones.append(ba.name)
                     
                    if dist < currentDist and distTail < currentDist:
                        nearestBone = ba.name
                        currentDist = dist
                
                #print(b.name, " NEAREST ", nearestBone)    
                if (nearestBone != None) and (nearestBone not in tmp_nearestBones):
                    tmp_nearestBones.append(nearestBone)        
            
                boneList.append([b.name, tmp_nearestBones])
                #boneList.append([b.name, nearestBone])
                bpy.context.view_layer.objects.active = bpy.data.objects[pRetargetArm]
                
                #STOP LOOP IF RETARGEABLE BONE
                break
    
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    #REMOVE TMP ARMATURES
    bpy.data.objects[pRetargetArm].select_set(False)
    bpy.data.objects[pAnimatedArm].select_set(False)
    bpy.data.objects.remove(bpy.data.objects[pAnimatedArm])    
    bpy.data.objects.remove(bpy.data.objects[pRetargetArm])    
    
    
    bpy.ops.object.select_all(action="DESELECT")
    bpy.data.objects[arm.name].select_set(True)
    bpy.context.view_layer.objects.active = arm
    
    #print(boneList)
    return boneList    


def retargetByPosition(pArmName, pArmDestName, pSelBones, pRelationList, pRotationOnly):
    
    arm = bpy.data.objects[pArmName]
    armDest = bpy.data.objects[pArmDestName]
    
    selBones = []
    usedBones = []
    bpy.ops.object.mode_set(mode='OBJECT')
    
    #SELECT  ARMATURE
    bpy.ops.object.select_all(action="DESELECT")
    bpy.data.objects[arm.name].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[arm.name]
    
    if len(pSelBones) ==0:
        bpy.ops.object.mode_set(mode='EDIT')
        for b in arm.data.edit_bones:
            selBones.append(b.name)
    else:
        selBones = pSelBones
    

    #ADD CONSTRAINTS
    bpy.ops.object.mode_set(mode='POSE')    
    for bs in selBones: 
        for b in pRelationList:
            if bs == b[0]:
                if b[0].find("_END") == -1:
                    pb = arm.pose.bones[b[0]]
                    numDependencies = len(b[1])
                    for nearBone in b[1]:
                        if nearBone not in usedBones:
                            
                            """
                            #CREATE EMPTY ROTAION HELPERS
                            bpy.ops.object.mode_set(mode='OBJECT')   
                            newEmpty = bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
                            newEmpty = bpy.context.object
                            newEmpty.name = "retarget-" + nearBone
                            newEmpty.empty_display_size = 0.05
                            
                            #TAIL HELPER
                            newEmptyTail = bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
                            newEmptyTail = bpy.context.object
                            newEmptyTail.name = "retargetTail-" + nearBone
                            newEmptyTail.empty_display_size = 0.05
                            
                            
                            #CREATE EMPTY CONSTRAINTS
                            print(pb.name + " "  + str(arm.data.bones[pb.name].use_connect))
                            if arm.data.bones[pb.name].use_connect == False:
                            
                                tCons = newEmpty.constraints.new('COPY_LOCATION')
                                tCons.name = "Retarget_location"
                                tCons.target = armDest
                                tCons.subtarget = nearBone
                                tCons.target_space = 'WORLD'
                                tCons.owner_space = 'WORLD'
                                tCons.influence = 1/numDependencies
                            
                            
                                tCons = newEmptyTail.constraints.new('COPY_LOCATION')
                                tCons.name = "Retarget_location"
                                tCons.target = armDest
                                tCons.subtarget = nearBone
                                tCons.target_space = 'WORLD'
                                tCons.owner_space = 'WORLD'
                                tCons.head_tail = 1
                                tCons.influence = 1/numDependencies
                            
                            #CREATE EMPTY DRIVER
                            rotationVars = []
                            
                            for i in range(0,3):
                                rotDriver = newEmpty.driver_add("rotation_euler",i)
                                rotDriver.driver.type = "AVERAGE" #'SCRIPTED'
                                rotDriver.driver.expression = "var"
                                rotVar = rotDriver.driver.variables.new()
                                rotVar.name = "var"
                                rotVar.type = "TRANSFORMS"
                                #rotVar.targets[0].id_type = 'OBJECT'
                                #print("ARMATURE ", arm.name, " ", armDest.name)
                                
                                rotVar.targets[0].id = bpy.data.objects[armDest.name]
                                
                                rotVar.targets[0].bone_target =  nearBone # bpy.data.objects[armDest.name].pose.bones[]
                                rotVar.targets[0].rotation_mode = "XYZ"
                                rotVar.targets[0].transform_space = "LOCAL_SPACE"
                                rotationVars.append(rotVar)
                            
                            rotationVars[0].targets[0].transform_type = "ROT_X"
                            rotationVars[1].targets[0].transform_type = "ROT_Y"
                            rotationVars[2].targets[0].transform_type = "ROT_Z"
                            
                            

                            #SELECT  ARMATURE
                            bpy.ops.object.select_all(action="DESELECT")
                            bpy.data.objects[arm.name].select_set(True)
                            bpy.context.view_layer.objects.active = bpy.data.objects[arm.name]
                            
                            """
                            
                            bpy.ops.object.mode_set(mode='POSE')   
                            #CREATE CONSTRAINTS ROTAION HELPERS   
                            if pRotationOnly == True:
                                tCons = pb.constraints.new('COPY_ROTATION')
                                tCons.name = "Retarget_rotation"
                                tCons.target =  armDest #newEmpty
                                tCons.subtarget = nearBone
                                tCons.target_space = 'LOCAL_WITH_PARENT'  #"LOCAL"
                                tCons.owner_space = 'LOCAL_WITH_PARENT' #"LOCAL" 
                                tCons.influence = 1/numDependencies
                                
                                tCons = pb.constraints.new('COPY_LOCATION')
                                tCons.name = "Retarget_location"
                                tCons.target = armDest
                                tCons.subtarget = nearBone
                                tCons.target_space = 'WORLD'
                                tCons.owner_space = 'WORLD'
                                tCons.influence = 1/numDependencies
                                
                                
                                tCons = pb.constraints.new('DAMPED_TRACK')
                                tCons.name = "Retarget_dampedTrack"
                                tCons.target = armDest #newEmptyTail
                                tCons.subtarget = nearBone
                                tCons.head_tail = 0
                                tCons.track_axis = "TRACK_Y"
                                tCons.influence = 1/numDependencies
                                
                                
                                """
                                tCons = pb.constraints.new('TRACK_TO')
                                tCons.name = "Retarget_trackTo"
                                tCons.target = armDest
                                tCons.subtarget = nearBone
                                tCons.head_tail = 1
                                tCons.track_axis = "TRACK_Y"
                                tCons.up_axis = "UP_X"
                                tCons.use_target_z = True
                                tCons.target_space = 'LOCAL'
                                tCons.owner_space = 'LOCAL'
                                tCons.influence = 1/numDependencies
                                """
                                
                                
                            else:
                                
                                tCons = pb.constraints.new('COPY_TRANSFORMS')
                                tCons.name = "Retarget_transform"
                                tCons.target = armDest
                                tCons.subtarget = nearBone
                                tCons.target_space = 'WORLD'
                                tCons.owner_space = 'POSE'
                                tCons.influence = 1/numDependencies
                            
                            usedBones.append(nearBone)


def retargetVertexGroupByPosition(pArm,pArmDestName, pSelBones, pRelationList):
    
    selBones = []
    usedBones = []
    bpy.ops.object.select_all(action="DESELECT")
    #bpy.ops.object.mode_set(mode='OBJECT')
    armDest = bpy.data.objects[pArmDestName]
    
    for o in armDest.children:
        for m in o.modifiers:
            if m.type == "ARMATURE":
                m.object = bpy.data.objects[pArm]
                break
            
        if o.type == "MESH":
            for r in pRelationList:
                vgId = o.vertex_groups.find(r[1][0])
                if vgId != -1:
                    o.vertex_groups[vgId].name = r[0]

def retargetVertexGroupByConstraints(arm, armDest):
    
    selBones = getSelBones()
    relationList = []
    #bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.object.mode_set(mode='POSE')
    
    armOrig = bpy.data.objects[arm]
    armDest = bpy.data.objects[armDest]
    
    for b in selBones:
        bon = bpy.context.object.pose.bones[b]
        for c in bon.constraints:
            if c.name.upper().find("RETARGET_LOCATION") != -1:
               # print(c.subtarget)
                
                boneDef = bon.name.replace(bpy.context.scene.vtoolsRetargetPattern, "")
                relationList.append([c.subtarget, boneDef])
                break
    
    if len(relationList) > 0:
        for o in armOrig.children:
            if o.type == "MESH":
                for r in relationList:
                    vgId = o.vertex_groups.find(r[0])
                    if vgId != -1:
                        o.vertex_groups[vgId].name = r[1]


    return True

                
def getSelBones():
    bpy.ops.object.mode_set(mode='EDIT')
    selBones = []
    for b in bpy.context.selected_bones:
        selBones.append(b.name)
    
    return selBones



    
# -- OPERATORS -- #  



class VTOOLS_OP_RS_retargetByName(bpy.types.Operator):
    bl_idname = "vtoolretargetsystem.retargetbyname"
    bl_label = "Create Socket"
    bl_description = ""
    
    def execute(self, context):
        #arm = bpy.context.object.name
        arm = bpy.data.objects[bpy.context.scene.vtoolRetargetDestiny].name
        armDest = bpy.data.objects[bpy.context.scene.vtoolRetargetOrigin].name
        namePatterns = bpy.context.scene.vtoolsRetargetPattern

        retargetByName(arm, armDest, namePatterns, bpy.context.scene.vtoolRetargetOnlyRotation)

        return {'FINISHED'}
    
class VTOOLS_OP_RS_retargetByPosition(bpy.types.Operator):
    bl_idname = "vtoolretargetsystem.retargetbyposition"
    bl_label = "Create Socket"
    bl_description = ""
    
    def execute(self, context):
        #arm = bpy.context.object.name
        arm = bpy.data.objects[bpy.context.scene.vtoolRetargetDestiny].name
        armDest = bpy.data.objects[bpy.context.scene.vtoolRetargetOrigin].name
        #namePatterns = "FKChainControls,ikTarget_IKChain"
        namePatterns = bpy.context.scene.vtoolsRetargetPattern
        

        tmpArmatures = duplicateArmatures(arm, armDest)
        boneRelationList = findNearestBones(arm, namePatterns, bpy.context.scene.vtoolRetargetTolerance, tmpArmatures[0], tmpArmatures[1])
        #print(boneRelationList)
        selBoneNames = getSelBones()
        retargetByPosition(arm, armDest, selBoneNames, boneRelationList, True)

        return {'FINISHED'}

class VTOOLS_OP_RS_retargetVertexGroupByPosition(bpy.types.Operator):
    bl_idname = "vtoolretargetsystem.retargetvertexgroupbyposition"
    bl_label = "Create Socket"
    bl_description = ""
    
    def execute(self, context):
        selBoneNames = []
        
        arm = bpy.data.objects[bpy.context.scene.vtoolRetargetDestiny].name
        armDest = bpy.data.objects[bpy.context.scene.vtoolRetargetOrigin].name
        #namePatterns = bpy.context.scene.vtoolsRetargetPattern
        
        #tmpArmatures = duplicateArmatures(arm, armDest)
        #boneRelationList = findNearestBones(arm, namePatterns, bpy.context.scene.vtoolRetargetTolerance, tmpArmatures[0], tmpArmatures[1])
        #retargetVertexGroupByPosition(arm, armDest, selBoneNames, boneRelationList)
        retargetVertexGroupByConstraints(arm, armDest)
        
        

        return {'FINISHED'}

class VTOOLS_OP_RS_removeConstrains(bpy.types.Operator):
    bl_idname = "vtoolretargetsystem.removeconstraints"
    bl_label = "Create Socket"
    bl_description = ""
    
    def execute(self, context):
        arm = bpy.context.object
        
        namePatterns = bpy.context.scene.vtoolsRetargetPattern
        np = namePatterns.split(",")
        
        bpy.ops.object.mode_set(mode='EDIT')
        selBones = bpy.context.selected_bones

        bpy.ops.object.mode_set(mode='POSE')

        for b in arm.pose.bones:
            found = False
            #CHECK IF IS A RETARGEABLE BONE
            for pattern in np: 
                if b.name.find(pattern) != -1: 
                    found = True
                    
                    #print("Base Name: ", b.name)
                    for cons in b.constraints:
                        if cons.name.find("Retarget") != -1:
                            b.constraints.remove(cons)
                

        

        return {'FINISHED'}
    
class VTOOLS_OP_RS_bakeAllActions(bpy.types.Operator):
    bl_idname = "vtoolretargetsystem.bakeallactions"
    bl_label = "Bake All Actions"
    bl_description = ""
    
    def execute(self, context):
        arm = bpy.context.object
        
        """
        
        opBake = layout.operator("nla.bake", text="Bake Action...")
        opBake.only_selected=True
        opBake.visual_keying=True
        opBake.clear_constraints=False
        opBake.clear_parents=False
        opBake.use_current_action=True
        opBake.clean_curves=False
        
        """
        
        return {'FINISHED'}
        
# -- PANELS -- #      




class VTOOLS_PT_RetargetSystem(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Retargeting"
    bl_category = 'Rig vTools'
    #bl_parent_id = "VTOOLS_PT_RigSystem"
    bl_options = {'DEFAULT_CLOSED'}
    
        
    @classmethod
    def poll(cls, context):
        return (context.object)
    
    def draw(self,context):
        
        layout = self.layout
        
        layout.label(text="Setup")
        
        col = layout.column(align=True)
        
        col.prop_search(bpy.context.scene, "vtoolRetargetOrigin", bpy.data, "objects", text="Origin")
        col.prop_search(bpy.context.scene, "vtoolRetargetDestiny", bpy.data, "objects", text="Destiny")
        if bpy.context.object.type == "ARMATURE":
            col.prop_search(bpy.context.scene, "vtoolRootBone", bpy.context.object.data, "bones", text="Root")
        col.prop(bpy.context.scene, "vtoolsRetargetPattern", text="Retarget Pattern")
        
        layout.separator()
        layout.label(text="Retarget by Name")
        
        layout.operator(VTOOLS_OP_RS_retargetByName.bl_idname, text="Retarget")
         
        #layout.prop(bpy.context.scene, "vtoolRetargetOnlyRotation", text="Only Rot")
        layout.separator()
        layout.label(text="Retarget by Position")
        layout.prop(bpy.context.scene, "vtoolRetargetTolerance", text="Tolerance")
        layout.operator(VTOOLS_OP_RS_retargetByPosition.bl_idname, text="Retarget")
        layout.operator(VTOOLS_OP_RS_retargetVertexGroupByPosition.bl_idname, text="Vertex Group")
        
        layout.separator()
        layout.label(text="Tools")
        opBake = layout.operator("nla.bake", text="Bake Action...")
        opBake.frame_end = bpy.context.scene.frame_preview_end
        opBake.only_selected=True
        opBake.visual_keying=True
        opBake.clear_constraints=False
        opBake.clear_parents=False
        opBake.use_current_action=True
        opBake.clean_curves=False
        
        
        layout.operator(VTOOLS_OP_RS_removeConstrains.bl_idname, text="Remove Retarget Constraints")
         

# -- REGISTER -- #       

def register():
    from bpy.utils import register_class
    register_class(VTOOLS_PT_RetargetSystem)
    register_class(VTOOLS_OP_RS_retargetByName)
    register_class(VTOOLS_OP_RS_retargetByPosition)
    register_class(VTOOLS_OP_RS_retargetVertexGroupByPosition)
    register_class(VTOOLS_OP_RS_removeConstrains)

    
    bpy.types.Scene.vtoolsRetargetPattern = bpy.props.StringProperty()
    bpy.types.Scene.vtoolRetargetOrigin = bpy.props.StringProperty()
    bpy.types.Scene.vtoolRetargetDestiny = bpy.props.StringProperty()
    bpy.types.Scene.vtoolRootBone = bpy.props.StringProperty()
    bpy.types.Scene.vtoolRetargetTolerance = bpy.props.FloatProperty(default=0.1)
    bpy.types.Scene.vtoolRetargetOnlyRotation = bpy.props.BoolProperty(default=False)
    
    
def unregister():
    from bpy.utils import unregister_class
    unregister_class(VTOOLS_PT_RetargetSystem)
    unregister_class(VTOOLS_OP_RS_retargetByName)
    unregister_class(VTOOLS_OP_RS_retargetByPosition)
    unregister_class(VTOOLS_OP_RS_retargetVertexGroupByPosition)
    unregister_class(VTOOLS_OP_RS_removeConstrains)

    
    del bpy.types.Scene.vtoolsRetargetPattern
    del bpy.types.Scene.vtoolRetargetOrigin
    del bpy.types.Scene.vtoolRetargetOnlyRotation


if __name__ == "__main__":
    register()