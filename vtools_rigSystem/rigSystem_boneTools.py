import bpy

# -- PANELS -- #      

class VTOOLS_PN_boneTools(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Bone Tools"
    bl_category = 'Rig vTools'
    #bl_parent_id = "VTOOLS_PT_RigSystem"
    bl_options = {'DEFAULT_CLOSED'} 
    
        
    @classmethod
    def poll(cls, context):
        return (context.object)
    
    def draw(self,context):
        
        layout = self.layout
        
        
        layout.label(text="Armature Layers")
        layout.prop(bpy.context.object.data, "layers", text="")
        
        
        bone = bpy.context.active_pose_bone
        if not bone:
            bone = bpy.context.active_bone
        
        if context.mode == "POSE":   
            row = layout.row()
            row.label(text="", icon='BONE_DATA')
            row.prop(bone, "name", text="")
            layout.prop(bone, "parent")
            layout.prop(bone, "custom_shape")
            col = layout.column()
            col.prop(bone, "custom_shape_scale_xyz")

# -- REGISTER -- #       

def register():
    from bpy.utils import register_class
    register_class(VTOOLS_PN_boneTools)
    

    
def unregister():
    from bpy.utils import unregister_class
    unregister_class(VTOOLS_PN_boneTools)
    
#---------- CLASES ----------#

if __name__ == "__main__":
    register()