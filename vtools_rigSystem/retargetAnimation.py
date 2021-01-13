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
                
                print("Base Name: ", b.name)
                
                #FIND TARGET BONE
                targetBoneName = None
                for tb in armDest.pose.bones:
                    for p in np:
                        print("BUSCANDO ", tb.name)
                        if b.name.find(tb.name) != -1 and b.name.find(p) != -1 and b.name.find("_END") == -1:
                             print("ENCONTRADO ", tb.name)
                             targetBoneName = tb.name
                             break
                
        
                #ADD CONSTRAINT
                if targetBoneName != None:
                    
                    if pRotationOnly == False:
                        pb = arm.pose.bones[b.name]
                        tCons = pb.constraints.new('COPY_TRANSFORMS')
                        tCons.name = "Retarget_transform"
                        tCons.target = armDest
                        tCons.subtarget = targetBoneName
                        tCons.target_space = 'WORLD'
                        tCons.owner_space = 'POSE'
                        tCons.influence = 1 
                    else:
                        pb = arm.pose.bones[b.name] 
                        tCons = pb.constraints.new('COPY_ROTATION')
                        tCons.name = "Retarget_transform"
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
    
    print("ARMATURES ", armatures)
    for a in armatures:
        
        #SELECT  ARMATURE
        bpy.ops.object.select_all(action="DESELECT")
        bpy.data.objects[a].select_set(True)
        bpy.context.view_layer.objects.active = bpy.data.objects[a]
        
        bpy.ops.object.mode_set(mode='EDIT')
    
        print("ENTRA")
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
    print("FIND NEAREST ")
    #Find nearest animated bone by position
    
    #SELECT  ARMATURE
    bpy.ops.object.select_all(action="DESELECT")
    bpy.data.objects[pRetargetArm].select_set(True)
    bpy.data.objects[pAnimatedArm].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[pRetargetArm]
       
       
    print("ARMATURE ACTIVO", bpy.context.view_layer.objects.active)
     
    bpy.ops.object.mode_set(mode='EDIT')
    for b in bpy.data.objects[pRetargetArm].data.edit_bones:
        tmp_nearestBones = []
        for pattern in np: 
            if b.name.find(pattern) != -1:        
                nearestBone = None
                currentDist = mathutils.Vector([100000,100000,100000])
                bpy.context.view_layer.objects.active = bpy.data.objects[pAnimatedArm]
                for ba in bpy.data.objects[pAnimatedArm].data.edit_bones:
                    dist = b.head - ba.head
                    if dist < tolerance:
                        tmp_nearestBones.append(ba.name)
                     
                    if (dist < currentDist):
                        nearestBone = ba.name
                        currentDist = dist
                
                print("NEAREST ", nearestBone)    
                if nearestBone != None:
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
    
    print(boneList)
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
    
    bpy.ops.object.mode_set(mode='POSE')    
    for bs in selBones: 
        for b in pRelationList:
            if bs == b[0]:
                if b[0].find("_END") == -1:
                    pb = arm.pose.bones[b[0]]
                    numDependencies = len(b[1])
                    for nearBone in b[1]:
                        if nearBone not in usedBones:   
                            if pRotationOnly == True:
                                tCons = pb.constraints.new('COPY_ROTATION')
                                tCons.name = "Retarget_transform"
                                tCons.target = armDest
                                tCons.subtarget = nearBone
                                tCons.target_space = 'WORLD'
                                tCons.owner_space = 'POSE'
                                tCons.influence = 1/numDependencies
                                
                            else:
                                
                                tCons = pb.constraints.new('COPY_TRANSFORMS')
                                tCons.name = "Retarget_transform"
                                tCons.target = armDest
                                tCons.subtarget = nearBone
                                tCons.target_space = 'WORLD'
                                tCons.owner_space = 'POSE'
                                tCons.influence = 1/numDependencies
                            
                            usedBones.append(nearBone)

                
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
        arm = bpy.context.object.name
        armDest = bpy.data.objects[bpy.context.scene.vtoolRetargetOrigin].name
        namePatterns = bpy.context.scene.vtoolsRetargetPattern

        retargetByName(arm, armDest, namePatterns, False)

        return {'FINISHED'}
    
class VTOOLS_OP_RS_retargetByPosition(bpy.types.Operator):
    bl_idname = "vtoolretargetsystem.retargetbyposition"
    bl_label = "Create Socket"
    bl_description = ""
    
    def execute(self, context):
        arm = bpy.context.object.name
        armDest = bpy.data.objects[bpy.context.scene.vtoolRetargetOrigin].name
        #namePatterns = "FKChainControls,ikTarget_IKChain"
        namePatterns = bpy.context.scene.vtoolsRetargetPattern
        selBoneNames = getSelBones()

        tmpArmatures = duplicateArmatures(arm, armDest)
        boneRelationList = findNearestBones(arm, namePatterns, bpy.context.scene.vtoolRetargetTolerance, tmpArmatures[0], tmpArmatures[1])
        retargetByPosition(arm, armDest, selBoneNames, boneRelationList, False)

        return {'FINISHED'}

# -- PANELS -- #      

class VTOOLS_PN_RetargetSystem(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Retarget System"
    bl_category = 'Tool'
    bl_parent_id = "VTOOLS_PT_RigSystem"
    #bl_options = {'DEFAULT_CLOSED'} 
    
        
    @classmethod
    def poll(cls, context):
        return (context.object)
    
    def draw(self,context):
        
        layout = self.layout
        
        layout.prop_search(bpy.context.scene, "vtoolRetargetOrigin", bpy.data, "objects", text="Origin")
        layout.prop(bpy.context.scene, "vtoolsRetargetPattern", text="Retarget Pattern")
        layout.prop(bpy.context.scene, "vtoolRetargetTolerance", text="Tolerance")
        layout.operator(VTOOLS_OP_RS_retargetByName.bl_idname, text="By Name")
        layout.operator(VTOOLS_OP_RS_retargetByPosition.bl_idname, text="By Position")
        

# -- REGISTER -- #       

def register():
    from bpy.utils import register_class
    register_class(VTOOLS_PN_RetargetSystem)
    register_class(VTOOLS_OP_RS_retargetByName)
    register_class(VTOOLS_OP_RS_retargetByPosition)
    
    bpy.types.Scene.vtoolsRetargetPattern = bpy.props.StringProperty()
    bpy.types.Scene.vtoolRetargetOrigin = bpy.props.StringProperty()
    bpy.types.Scene.vtoolRetargetTolerance = bpy.props.FloatProperty(default=0.1)
    
    
def unregister():
    from bpy.utils import unregister_class
    unregister_class(VTOOLS_PN_RetargetSystem)
    unregister_class(VTOOLS_OP_RS_retargetByName)
    unregister_class(VTOOLS_OP_RS_retargetByPosition)
    
    del bpy.types.Scene.vtoolsRetargetPattern
    del bpy.types.Scene.vtoolRetargetOrigin