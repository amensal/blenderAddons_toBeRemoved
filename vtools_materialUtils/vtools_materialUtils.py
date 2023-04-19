bl_info = {
    "name": "vtools Material Utilities",
    "author": "Antonio Mendoza",
    "version": (0, 0, 3),
    "blender": (3, 0, 0),
    "location": "Material Slot Menu",
    "description": "Material operators for all selected objets",
    "category": "Material"
}



import bpy



class VTOOLS_OP_removeAllMaterials(bpy.types.Operator):
    bl_idname = "vtools.remveallmaterials"
    bl_label = "Remove All"
    bl_description = "Remove all materials from every object selected"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    
    def execute(self,context):
        
        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                if len(obj.data.materials) > 0:
                    obj.data.materials.clear()
    
        return {'FINISHED'}   

def menu_draw(self, context):
    self.layout.operator(VTOOLS_OP_removeAllMaterials.bl_idname, text=VTOOLS_OP_removeAllMaterials.bl_label, icon='REMOVE')
    
def register():
    bpy.utils.register_class(VTOOLS_OP_removeAllMaterials)
    bpy.types.MATERIAL_MT_context_menu.append(menu_draw)
    
    #addShortcut()
   
def unregister():
    bpy.utils.unregister_class(VTOOLS_OP_removeAllMaterials)
    bpy.types.TOPBAR_MT_file.remove(menu_draw)
    
    
if __name__ == "__main__":
    register()