bl_info = {
    "name": "vtools - Create 3D Print Shell Object",
    "author": "Antonio Mendoza",
    "version": (0, 0, 1),
    "blender": (3, 00, 0),
    "location": "View3D > Tool Panel > 3D-Print Tab > Shell Object",
    "warning": "",
    "description": "SCreate a shell 3D printable object from selected object",
    "category": "3D-Print",
}


import bpy
import os 
from bpy.types import Panel


class Vtool3DPrintPanel:
    bl_category = "3D-Print"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == 'MESH' and obj.mode in {'OBJECT', 'EDIT'}

class VTOOLS_OP_3DPrint_createShellObject(bpy.types.Operator):
    bl_idname = "vtools3dprint.createshellobject"
    bl_label = "Create Shell Object"
    bl_description = "Create a shell 3D Object from all selected objects."
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        
        for o in bpy.context.selected_objects:
    
            found = False
            for mod in o.modifiers:
                if mod.type == "SUBSURF":
                    found = True
            
        if found == False:
            m = bpy.context.object.modifiers.new(name="mod", type="SUBSURF")
            m.levels = 0
            
        try: 
            bpy.ops.object.make_single_user(object=True, obdata=True, material=False, animation=False, obdata_animation=False)
        except: 
            print("cannot make unique")

        try: 
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        except: 
            print("cannot clear parent")
                    
        try:
            bpy.ops.object.convert(target="MESH")
        except:
            print("cannot convert to mesh")
            

        try:
            bpy.ops.object.join()
        except:
            print("cannot join mesh")
            
            
        try: 
            bpy.context.object.data.remesh_voxel_size = 0.04
            bpy.ops.object.voxel_remesh()
        except:
            print("cannot voxel remesh")

        dm = None    
        
        if bpy.context.scene.vtool3DPrntDecimateRatio != 1:
            try:
                dm = bpy.context.object.modifiers.new(name="Decimate", type="DECIMATE")
                dm.ratio = bpy.context.scene.vtool3DPrntDecimateRatio
            except:
                print("cannot decimate")
        
        """    
        try:
            bpy.ops.object.apply_all_modifiers()
        except:
            print("cannot apply decimate")
        """
        
        if bpy.context.scene.vtool3DPrintUseExport == True:      
            try: 
               bpy.ops.mesh.print3d_export()
            except:
                print("cannot export")
        
        return {'FINISHED'}
    
class VTOOL_PT_createShellObject(Vtool3DPrintPanel, Panel):
    bl_label = "Shell Object"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        #layout.use_property_split = True
        #layout.use_property_decorate = True
        layout.prop(bpy.context.scene, "vtool3DPrintUseExport", text="Use Export")
        layout.prop(bpy.context.scene, "vtool3DPrntDecimateRatio", text="Decimate Ratio")
        layout.operator(VTOOLS_OP_3DPrint_createShellObject.bl_idname, text="Shell", icon='META_DATA')

def register():
    from bpy.utils import register_class
    register_class(VTOOL_PT_createShellObject)
    register_class(VTOOLS_OP_3DPrint_createShellObject)
    
    bpy.types.Scene.vtool3DPrintUseExport = bpy.props.BoolProperty(default=True)
    bpy.types.Scene.vtool3DPrntDecimateRatio = bpy.props.FloatProperty(default=0.1, min=0, max=1)

    
    
def unregister():
    from bpy.utils import unregister_class
    unregister_class(VTOOL_PT_createShellObject)
    unregister_class(VTOOLS_OP_3DPrint_createShellObject)
    
    del bpy.types.Scene.vtool3DPrintUseExport


if __name__ == "__main__":
    register()