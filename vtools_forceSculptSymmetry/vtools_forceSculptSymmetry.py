bl_info = {
    "name": "vtools - Sculpt Force Symmetry",
    "author": "Antonio Mendoza Salado",
    "version": (0, 0, 1),
    "blender": (2, 80, 3),
    "location": "Sculpt Mode > View3D > Tool Panel > Tool Tab >  Symmetry Panel > Force Symmetry",
    "warning": "",
    "description": "You can force to any object to enable or disable symmetry in sculpt mode when selected",
    "category": "Sculpting",
}


import bpy
import os

from bpy.props import (StringProperty,BoolProperty,IntProperty,FloatProperty,FloatVectorProperty,EnumProperty,PointerProperty)
from bpy.types import (Menu, Panel,Operator,AddonPreferences, PropertyGroup)
from rna_prop_ui import rna_idprop_ui_prop_get

#---------- CALLBACKS  ----------#

def post_ob_data_updated(scene):
    ob = bpy.context.object
    if ob is not None:
        if bpy.context.mode == "SCULPT":
            bpy.context.scene.tool_settings.sculpt.use_symmetry_x = bpy.context.object.vt_forceSculptSymmetry_x
            bpy.context.scene.tool_settings.sculpt.use_symmetry_y = bpy.context.object.vt_forceSculptSymmetry_y
            bpy.context.scene.tool_settings.sculpt.use_symmetry_z = bpy.context.object.vt_forceSculptSymmetry_z
            
#---------- CLASES ----------#

class VTOOLS_PT_ForceSymmetry(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Force Symmetry"
    #bl_category = 'Tool'
    bl_parent_id = "VIEW3D_PT_sculpt_symmetry"
    #bl_options = {'DEFAULT_CLOSED'} 
    
        
    @classmethod
    def poll(cls, context):
        return (context.mode == "SCULPT")
    
    def draw(self,context):
        
        layout = self.layout
        
        if bpy.context.object:
            
            row = layout.row(align=True, heading="Force")
            row.prop(bpy.context.object,"vt_forceSculptSymmetry_x", text="X", toggle=True);
            row.prop(bpy.context.object,"vt_forceSculptSymmetry_y", text="Y", toggle=True);
            row.prop(bpy.context.object,"vt_forceSculptSymmetry_z", text="Z", toggle=True);
            

#---------- REGISTER  ----------#  

            
def register():  
    
    from bpy.utils import register_class
    
    register_class(VTOOLS_PT_ForceSymmetry)
    
    bpy.types.Object.vt_forceSculptSymmetry_x = bpy.props.BoolProperty(default = True)
    bpy.types.Object.vt_forceSculptSymmetry_y = bpy.props.BoolProperty(default = False)
    bpy.types.Object.vt_forceSculptSymmetry_z = bpy.props.BoolProperty(default = False)
    
    bpy.app.handlers.depsgraph_update_post.clear()
    bpy.app.handlers.depsgraph_update_post.append(post_ob_data_updated)

def unregister():
    
    from bpy.utils import unregister_class
    
    unregister_class(VTOOLS_PT_ForceSymmetry)
    
    del bpy.types.Object.vt_forceSculptSymmetry_x
    del bpy.types.Object.vt_forceSculptSymmetry_y
    del bpy.types.Object.vt_forceSculptSymmetry_z
    

if __name__ == "__main__":
    register()