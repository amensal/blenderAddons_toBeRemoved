"""
NOTAS: 

Hay que ir cambiando la variable "ShapeKeyName" con el nombre del shapekey, 
eligiendo la accion donde se va a aplicar esa animacion de shapekey y lanzar el script


"""

import bpy

def transferShapeKeysToArmature(pShapeKeyName, pArmName, pAction):
    print(" ")
    print(" ")
    print(" ")
    print(" ")
    print(" ")
    print(" ")
    print(" ")
    print(" -- INICIO --")
    shapeKeyName = pShapeKeyName 
    arm = bpy.data.objects[pArmName]
    
    #SET ACTIVE ACTION
    arm.animation_data.action = bpy.data.actions[pAction]
    

    ActionOriginal = "" #bpy.context.object.animation_data.action.name
    ActionDestiny = ""

    o = bpy.data.objects[shapeKeyName]
    #o.data.shape_keys.animation_data.action.fcurves[1].evaluate(0)

    shapeKeys = bpy.data.shape_keys[o.data.shape_keys.name]

    for b in arm.data.bones: 
        b.select = False
         
    #Recorre los shape keys y busca un hueso que se llame igual para pegar la animacion
    for kb in shapeKeys.key_blocks:

        nameToSearch = kb.name
        print("Name to search ", nameToSearch)
        #busca el hueso
        for b in arm.pose.bones: 
            if b.name.find(nameToSearch) != -1:
                arm.data.bones[b.name].select = True
                print("Encontrado ", b.name)
                
                #Copiar animacion
                # bpy.context.object.data.shape_keys.animation_data.action.fcurves
                # bpy.context.object.animation_data.action.fcurves[2].array_index
                
                #busca en las curvas la que corresponda al shape key
                print("-- BUSCANDO FCURVES --")
                for fcurve in shapeKeys.animation_data.action.fcurves:
                    
                    """
                    #busca la accion
                    for fc in bpy.data.action[kb].fcurves:
                        if fc.dat_path.find(b) != -1:
                            curve = fc
                    """
                               
                    if fcurve.data_path.split('"')[1] == kb.name:
                        print(" ")
                        print(" -- ENCONTRADA --")
                        
                        #copia keyframes en el animation data del hueso
                        print("FCurve Shape Key ", kb.name, " ", fcurve.data_path) 
                        
                        armFCurve = None
                        #busca la curva del hueso
                        for fc in arm.animation_data.action.fcurves:
                            if fc.data_path.find(nameToSearch) != -1:
                                if fc.data_path.upper().find("LOCATION") and fc.array_index == 1:
                                    armFCurve = fc
                                    print("FCurve Hueso: ", armFCurve.data_path, " ", armFCurve.array_index)
                                    break
                        
                        #recorre los keyframes y los copia
                        print("------- KEYFRAMES ----------")
                        for k in fcurve.keyframe_points:
                            time = k.co[0]
                            fValue = k.co[1]#*100
                            
                            #bpy.context.object.keyframe_insert()
                            #bpy.ops.anim.keyframe_insert_by_name(type="Location"
                            
                            #bpy.context.scene.frame_current = int(time)
                            #b.location.y = value*100
                            
                            if armFCurve != None:
                                print("Insert Keyframe: ", armFCurve.data_path, " ", time , " ", fValue)
                                #armFCurve.keyframe_points.insert(frame=time, value=fValue)
                            
                                try: 
                                    armFCurve.keyframe_points.insert(frame=time, value=fValue)
                                    #bpy.ops.anim.keyframe_insert_by_name(type="Location")
                                    print("keyframe added")
                                except: 
                                    print("cannot add keyframe")
                                
     
                    try: 
                        arm.data.bones[b.name].select = False
                    except: 
                        print("cannot unselect")
                    


def configureShapeKeyDrivers(pArmName, pShapekeyObjectName):
    
    #ADD DRIVER TODO
    #añadir el driver del esqueleto a la cara

    if bpy.data.objects.find(pArmName) != -1:
        arm = bpy.data.objects[pArmName]
        targetObject = bpy.data.objects[pShapekeyObjectName]
        shapeKeys = targetObject.data.shape_keys
        
        #DELETE EXISTING DRIVERS
        for kb in shapeKeys.key_blocks:
            kb.driver_remove("value")
            
        #CREATE DRIVERS
        for kb in shapeKeys.key_blocks:
            if arm.data.bones.find(kb.name) != -1:
                kbDriver = kb.driver_add("value")
                kbDriver.driver.type = 'SCRIPTED'
                kbDriver.driver.expression = "var"
                rotVar = kbDriver.driver.variables.new()
                rotVar.name = "var"
                rotVar.type = "TRANSFORMS"
                #rotVar.targets[0].id_type = 'OBJECT'
                rotVar.targets[0].id = bpy.data.objects[pArmName]
                rotVar.targets[0].bone_target =  kb.name
                rotVar.targets[0].transform_type = "LOC_Y"
                rotVar.targets[0].transform_space = "LOCAL_SPACE"
                                        
                
# -- OPERATORS -- #               
                            
class VTOOLS_OP_RS_transferShapeKeyToArmature(bpy.types.Operator):
    bl_idname = "vtoolshapekeytools.transfersptoarmature"
    bl_label = "Transfer Shape Keys to Armature"
    bl_description = "Transfer shape keys from a geometry to a set of bones"
    
    def execute(self, context):
        arm = bpy.context.object
        
        transferShapeKeysToArmature(bpy.context.scene.vtoolShapeKeyToTransfern, bpy.context.scene.vtoolTargetArmature, bpy.context.scene.vtoolTransfernToAction)
        
        return {'FINISHED'}
        
class VTOOLS_OP_RS_transferConfigureDrivers(bpy.types.Operator):
    bl_idname = "vtoolshapekeytools.configuredrivers"
    bl_label = "Transfer Shape Keys to Armature"
    bl_description = "Add shape key driver from a same name bone Y location"
    
    def execute(self, context):
        arm = bpy.context.object
        configureShapeKeyDrivers(bpy.context.scene.vtoolTargetArmature, bpy.context.scene.vtoolTargetShapeKey)
        return {'FINISHED'}
    
# -- PANELS -- #      

                    
class VTOOLS_PT_ShapeKeyTools(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Shape Key Tools"
    bl_category = 'Rig vTools'
    #bl_parent_id = "VTOOLS_PT_RigSystem"
    bl_options = {'DEFAULT_CLOSED'} 
    
        
    @classmethod
    def poll(cls, context):
        return (context.object)
    
    def draw(self,context):
        
        layout = self.layout
        
        layout.label(text="Setup")
        #layout.operator(VTOOLS_OP_RS_removeConstrains.bl_idname, text="Remove Retarget Constraints")
        layout.prop_search(bpy.context.scene, "vtoolTargetArmature", bpy.data, "objects", text="Armature")
        layout.prop_search(bpy.context.scene, "vtoolTargetShapeKey", bpy.data, "objects", text="Shape Key Target")
        
        layout.operator(VTOOLS_OP_RS_transferConfigureDrivers.bl_idname, text="Configure Drivers")
        
        layout.separator()
        layout.prop_search(bpy.context.scene, "vtoolShapeKeyToTransfern", bpy.data, "objects", text="Shape Key Origin")
        layout.prop_search(bpy.context.scene, "vtoolTransfernToAction", bpy.data, "actions", text="To Action")
        
        layout.operator(VTOOLS_OP_RS_transferShapeKeyToArmature.bl_idname, text="Transfer")


def register():
    from bpy.utils import register_class
    register_class(VTOOLS_OP_RS_transferShapeKeyToArmature)
    register_class(VTOOLS_OP_RS_transferConfigureDrivers)
    register_class(VTOOLS_PT_ShapeKeyTools)

    bpy.types.Scene.vtoolTargetArmature = bpy.props.StringProperty()
    bpy.types.Scene.vtoolTargetShapeKey = bpy.props.StringProperty()
    bpy.types.Scene.vtoolShapeKeyToTransfern = bpy.props.StringProperty()
    bpy.types.Scene.vtoolTransfernToAction = bpy.props.StringProperty()

    
    
def unregister():
    from bpy.utils import unregister_class
    unregister_class(VTOOLS_OP_RS_transferShapeKeyToArmature)
    unregister_class(VTOOLS_OP_RS_transferConfigureDrivers)
    unregister_class(VTOOLS_PT_ShapeKeyTools)
    
    del bpy.types.Scene.vtoolTargetArmature
    del bpy.types.Scene.vtoolTargetShapeKey
    del bpy.types.Scene.vtoolShapeKeyToTransfern
    del bpy.types.Scene.vtoolTransfernToAction


if __name__ == "__main__":
    register()          