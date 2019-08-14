import bpy

class VTOOLS_OP_SetMouseCursor(bpy.types.Operator):
    bl_idname = "vtoolpt.setmousecursor"
    bl_label = "Set Mouse cursor"
    bl_description = "Set Mouse cursor"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        
        if bpy.context.active_object.mode == "TEXTURE_PAINT":
            bpy.context.window.cursor_set("CROSSHAIR")
        else:
            bpy.context.window.cursor_set("DEFAUL")
              
        return {'FINISHED'}
           
class VTOOLS_PN_SetMouseCursorPanel(bpy.types.Panel):
    bl_label = "Set Mouse Cursor"
    bl_parent_id = "VIEW3D_PT_view3d_properties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}  
        
    @classmethod
    def poll(cls, context):
        
        return (context.mode == 'PAINT_TEXTURE')
        #return (context.object)
    
    def draw(self,context):
        layout = self.layout
        layout.label(text="HOLA")
        layout.operator(VTOOLS_OP_SetMouseCursor.bl_idname, text=VTOOLS_OP_SetMouseCursor.bl_label, icon='CURSOR')
        
def vt_setPaintingCursor(self, context):
    
    layout = self.layout
                    
def register():
    
    bpy.utils.register_class(VTOOLS_OP_SetMouseCursor)
    bpy.utils.register_class(VTOOLS_PN_SetMouseCursorPanel)
    
    #bpy.utils.register_class(VTOOLS_MOD_SetPaintingCursor)
    
    #bpy.types.VIEW3D_PT_view3d_properties.append(vt_addMaskImageTexture)


def unregister():
    bpy.utils.register_class(VTOOLS_OP_SetMouseCursor)
    bpy.utils.register_class(VTOOLS_PN_SetMouseCursorPanel)
    #bpy.utils.unregister_class(VTOOLS_MOD_SetPaintingCursor)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.object.modal_operator('INVOKE_DEFAULT')
