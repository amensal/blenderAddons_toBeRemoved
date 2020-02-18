import bpy 
from bpy.types import Menu, Panel, Operator

bl_info = {
    "name": "vtools - Extra UV Layer Tools",
    "author": "Antonio Mendoza",
    "location": "Properties > Object Data > UV Layers Panel",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "description": "Extra tools to manage uv layers in multiple selected objects",
    "category": "Mesh"  
}


class VTOOL_OP_copyUVToSelected(Operator):
    bl_idname = "vtool.copyuvtoselected"
    bl_label = "Add to Selected"
    bl_description = "Add a new UV layer with the same name to every selected object"
    
    def execute(self,context):
        
        activeObject = bpy.context.view_layer.objects.active
        activeUVLayerName = activeObject.data.uv_layers[activeObject.data.uv_layers.active_index].name
        
        for o in bpy.context.selected_objects:
            id = o.data.uv_layers.find(activeUVLayerName)
            if id != -1:
                o.data.uv_layers.active_index = id 
            else:
                o.data.uv_layers.new(name = activeUVLayerName)
                o.data.uv_layers.active_index = len(o.data.uv_layers) - 1          
                        
        return{'FINISHED'}

class VTOOL_OP_removeUVAllObject(Operator):
    bl_idname = "vtool.removeuvallobjects"
    bl_label = "Remove from Selected"
    bl_description = "Remove selected UV layer with the same name from every selected object"
    
    def execute(self,context):
        
        activeObject = bpy.context.view_layer.objects.active
        activeUVLayerName = activeObject.data.uv_layers[activeObject.data.uv_layers.active_index].name
        
        for o in bpy.context.selected_objects:
            id = o.data.uv_layers.find(activeUVLayerName)
            if id != -1:
                o.data.uv_layers.remove(o.data.uv_layers[id])    
                        
        return{'FINISHED'}
    
class VTOOL_OP_selectUVAllObject(Operator):
    bl_idname = "vtool.selectuvallobjects"
    bl_label = "Active in Selected"
    bl_description = "Active selected UV layer with the same name in every selected object"
    
    def execute(self,context):
        
        activeObject = bpy.context.view_layer.objects.active
        activeUVLayerName = activeObject.data.uv_layers[activeObject.data.uv_layers.active_index].name
        
        for o in bpy.context.selected_objects:
            id = o.data.uv_layers.find(activeUVLayerName)
            if id != -1:
                o.data.uv_layers.active_index = id         
                        
        return{'FINISHED'}
    
class VTOOL_OP_copyNameUVAllObject(Operator):
    bl_idname = "vtool.copynameuvallobjects"
    bl_label = "Copy Name in Selected"
    bl_description = "Copy selected UV layer name in the same position uv layer of every selected object"
    
    def execute(self,context):
        
        activeObject = bpy.context.view_layer.objects.active
        selectedIndex = activeObject.data.uv_layers.active_index
        activeUVLayerName = activeObject.data.uv_layers[selectedIndex].name
        
        for o in bpy.context.selected_objects:
            if len(o.data.uv_layers) > selectedIndex:
                id = o.data.uv_layers.find(activeUVLayerName)
                if id != -1:
                    o.data.uv_layers[id].name += ".001"
                
                o.data.uv_layers[selectedIndex].name = activeUVLayerName;
                        
        return{'FINISHED'}


class VTOOL_MT_uvTools_menu(Menu):
    bl_label = "Extra UV Tools"
    
    def draw(self, _context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.
        layout.operator(VTOOL_OP_copyNameUVAllObject.bl_idname, text=VTOOL_OP_copyNameUVAllObject.bl_label, icon="CURSOR")
        layout.operator(VTOOL_OP_copyUVToSelected.bl_idname, text=VTOOL_OP_copyUVToSelected.bl_label, icon="ADD")
        layout.operator(VTOOL_OP_selectUVAllObject.bl_idname, text=VTOOL_OP_selectUVAllObject.bl_label, icon="EYEDROPPER")
        layout.operator(VTOOL_OP_removeUVAllObject.bl_idname, text=VTOOL_OP_removeUVAllObject.bl_label, icon="REMOVE")
        
        
def vt_addExtraUVTools(self, context):
    
    layout = self.layout
    
    row = layout.row(align = True)
    row.operator(VTOOL_OP_copyNameUVAllObject.bl_idname, text="", icon="CURSOR")
    row.operator(VTOOL_OP_copyUVToSelected.bl_idname, text="", icon="ADD")
    row.operator(VTOOL_OP_selectUVAllObject.bl_idname, text="", icon="EYEDROPPER")
    row.operator(VTOOL_OP_removeUVAllObject.bl_idname, text="", icon="REMOVE")
    
    
    #layout.menu("VTOOL_MT_uvTools_menu", icon='DOWNARROW_HLT', text="")
        
"""    
class VTOOL_PT_uvTools(Panel):
    bl_label = "Extra UV Layers Tools"
    bl_context = "data"
    bl_parent_id = "DATA_PT_uv_texture" 
    #bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    
    @classmethod
    def poll(cls,context):
        return context.object

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.
        row = layout.row(align=True)
        row.operator(VTOOL_OP_copyNameUVAllObject.bl_idname, text="", icon="CURSOR")
        row.operator(VTOOL_OP_copyUVToSelected.bl_idname, text="", icon="ADD")
        row.operator(VTOOL_OP_selectUVAllObject.bl_idname, text="", icon="EYEDROPPER")
        row.operator(VTOOL_OP_removeUVAllObject.bl_idname, text="", icon="REMOVE")
"""
        
def register():
    from bpy.utils import register_class
    register_class(VTOOL_OP_copyUVToSelected)
    register_class(VTOOL_OP_selectUVAllObject)
    register_class(VTOOL_OP_removeUVAllObject)
    register_class(VTOOL_OP_copyNameUVAllObject)
    #register_class(VTOOL_PT_uvTools)
    register_class(VTOOL_MT_uvTools_menu)
    
    bpy.types.DATA_PT_uv_texture.append(vt_addExtraUVTools)
    
    

def unregister():
    from bpy.utils import unregister_class
    unregister_class(VTOOL_OP_copyUVToSelected)
    unregister_class(VTOOL_OP_selectUVAllObject)
    unregister_class(VTOOL_OP_removeUVAllObject)
    unregister_class(VTOOL_OP_copyNameUVAllObject)
    #unregister_class(VTOOL_PT_uvTools)
    unregister_class(VTOOL_MT_uvTools_menu)
    
    bpy.types.DATA_PT_uv_texture.remove(vt_addExtraUVTools)
    

if __name__ == '__main__':
    register()
    
    