bl_info = {
    "name": "vtools - Random Transform",
    "author": "Antonio Mendoza",
    "location": "View3D > Panel Tools > Tool Tab",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "warning": "",
    "description": "Set random transform to selected objects",
    "category": "Object", 
}


import bpy
import math 
import random
from bpy.props import StringProperty, BoolProperty, IntProperty, CollectionProperty, FloatProperty, EnumProperty




class VTOOLS_OP_setTransform(bpy.types.Operator):
    bl_idname = "vtoolsrandomtransform.settransform"
    bl_label = "Set exact Transform"
        
    
    def setRandomScale(self,pObj):
        
        srX = 0
        srY = 0
        srZ = 0
        
        if bpy.context.scene.vt_rtransform_useTransform == "min":
            srX = bpy.context.scene.vt_rtransform_XminScale
            srY = bpy.context.scene.vt_rtransform_YminScale
            srZ = bpy.context.scene.vt_rtransform_ZminScale
        else:
            srX = bpy.context.scene.vt_rtransform_XmaxScale
            srY = bpy.context.scene.vt_rtransform_YmaxScale
            srZ = bpy.context.scene.vt_rtransform_ZmaxScale
            
        if bpy.context.scene.vt_rtransform_XsetScale == True:
            pObj.scale.x = srX
        
        if bpy.context.scene.vt_rtransform_YsetScale == True:    
            pObj.scale.y = srY
        
        if bpy.context.scene.vt_rtransform_ZsetScale == True:
            pObj.scale.z = srZ
        
    def setRandomRotation(self,pObj):
        
        rrX = 0
        rrY = 0
        rrZ = 0
        
        if bpy.context.scene.vt_rtransform_useTransform == "min":
            rrX = bpy.context.scene.vt_rtransform_XminRotation
            rrY = bpy.context.scene.vt_rtransform_YminRotation
            rrZ = bpy.context.scene.vt_rtransform_ZminRotation
        else:
            rrX = bpy.context.scene.vt_rtransform_XmaxRotation
            rrY = bpy.context.scene.vt_rtransform_YmaxRotation
            rrZ = bpy.context.scene.vt_rtransform_ZmaxRotation
            
        if bpy.context.scene.vt_rtransform_XsetRotation == True:
            pObj.rotation_euler.x = math.radians(rrX)
        
        if bpy.context.scene.vt_rtransform_YsetRotation == True:
            pObj.rotation_euler.y = math.radians(rrY)
        
        if bpy.context.scene.vt_rtransform_ZsetRotation == True:
            pObj.rotation_euler.z = math.radians(rrZ)
        
    def execute(self,context):

        for o in bpy.context.selected_objects:
            
                self.setRandomScale(o)
                self.setRandomRotation(o)
            
            
        return{'FINISHED'}
 

class VTOOLS_OP_setRandomTransform(bpy.types.Operator):
    bl_idname = "vtoolsrandomtransform.setrandtransform"
    bl_label = "Set Random Transform"
        
    
    def setRandomScale(self,pObj):
        
        srX = random.uniform(bpy.context.scene.vt_rtransform_XminScale, bpy.context.scene.vt_rtransform_XmaxScale)
        srY = random.uniform(bpy.context.scene.vt_rtransform_YminScale, bpy.context.scene.vt_rtransform_YmaxScale)
        srZ = random.uniform(bpy.context.scene.vt_rtransform_ZminScale, bpy.context.scene.vt_rtransform_ZmaxScale)
        
        if bpy.context.scene.vt_rtransform_XsetScale == True:
            pObj.scale.x = srX
        
        if bpy.context.scene.vt_rtransform_YsetScale == True:    
            pObj.scale.y = srY
        
        if bpy.context.scene.vt_rtransform_ZsetScale == True:
            pObj.scale.z = srZ
        
    def setRandomRotation(self,pObj):
        
        rrX = random.uniform(bpy.context.scene.vt_rtransform_XminRotation, bpy.context.scene.vt_rtransform_XmaxRotation)
        rrY = random.uniform(bpy.context.scene.vt_rtransform_YminRotation, bpy.context.scene.vt_rtransform_YmaxRotation)
        rrZ = random.uniform(bpy.context.scene.vt_rtransform_ZminRotation, bpy.context.scene.vt_rtransform_ZmaxRotation)


        
        if bpy.context.scene.vt_rtransform_XsetRotation == True:
            pObj.rotation_euler.x = math.radians(rrX)
        
        if bpy.context.scene.vt_rtransform_YsetRotation == True:
            pObj.rotation_euler.y = math.radians(rrY)
        
        if bpy.context.scene.vt_rtransform_ZsetRotation == True:
            pObj.rotation_euler.z = math.radians(rrZ)
        
    def execute(self,context):

        for o in bpy.context.selected_objects:
            
                self.setRandomScale(o)
                self.setRandomRotation(o)
            
            
        return{'FINISHED'}
    
class VTOOLS_PN_RandomTransform(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Random Transform"
    bl_context = "objectmode"
    bl_category = 'Item'
    bl_options = {'DEFAULT_CLOSED'}       
    
       
    def draw(self,context):
        
        layout = self.layout
        
        # ----------- CONFING  ------------------ #
        
        row = layout.row(align=True)
        row.label(text="Scale")
        
        col = layout.column(align = True)
        row = col.row(align=True)
        
        row.prop(context.scene,"vt_rtransform_XsetScale", text="")
        row.prop(context.scene,"vt_rtransform_XminScale")
        row.prop(context.scene,"vt_rtransform_XmaxScale")
       
        
        row = col.row(align=True)
        row.prop(context.scene,"vt_rtransform_YsetScale", text="")
        row.prop(context.scene,"vt_rtransform_YminScale")
        row.prop(context.scene,"vt_rtransform_YmaxScale")
        
        
        row = col.row(align=True)
        row.prop(context.scene,"vt_rtransform_ZsetScale", text="")
        row.prop(context.scene,"vt_rtransform_ZminScale")
        row.prop(context.scene,"vt_rtransform_ZmaxScale")
            
        
        row = layout.row(align=True)
        row.label(text="Rotation")
        
        col = layout.column(align = True)
        row = col.row(align=True)
        row.alignment = 'EXPAND'
        
        row.prop(context.scene,"vt_rtransform_XsetRotation", text="")
        row.prop(context.scene,"vt_rtransform_XminRotation")
        row.prop(context.scene,"vt_rtransform_XmaxRotation")
        
        
        row = col.row(align=True)
        row.prop(context.scene,"vt_rtransform_YsetRotation", text="")
        row.prop(context.scene,"vt_rtransform_YminRotation")
        row.prop(context.scene,"vt_rtransform_YmaxRotation")
        
        
        row = col.row(align=True)
        row.prop(context.scene,"vt_rtransform_ZsetRotation", text="")
        row.prop(context.scene,"vt_rtransform_ZminRotation")
        row.prop(context.scene,"vt_rtransform_ZmaxRotation")
            
        
        layout.separator()

        row = layout.row(align=True)
        row.operator(VTOOLS_OP_setRandomTransform.bl_idname, text=VTOOLS_OP_setRandomTransform.bl_label)
        
        col= layout.column(align=True)
        row = col.row(align=True)
        row.prop(bpy.context.scene,"vt_rtransform_useTransform", text=" ", toggle=True, expand=True)
        col.operator(VTOOLS_OP_setTransform.bl_idname, text=VTOOLS_OP_setTransform.bl_label)
        
        
        
def register():
    
    from bpy.utils import register_class
    
    register_class(VTOOLS_OP_setTransform)
    register_class(VTOOLS_OP_setRandomTransform)
    register_class(VTOOLS_PN_RandomTransform)
    

    bpy.types.Scene.vt_rtransform_useTransform = bpy.props.EnumProperty(
    items=(
        ("min", "Use min Value", 'min Value',  '', 1),
        ("max", "Use max Value", 'max Value',  '', 2),
    ),
    name="usevalue",
    default="min",
    )
    
    bpy.types.Scene.vt_rtransform_XsetScale = bpy.props.BoolProperty(name='X Scale', default=True)
    bpy.types.Scene.vt_rtransform_XminScale = bpy.props.FloatProperty(name='X min', default=0.5)
    bpy.types.Scene.vt_rtransform_XmaxScale = bpy.props.FloatProperty(name='X max', default=10)
    
    bpy.types.Scene.vt_rtransform_YsetScale = bpy.props.BoolProperty(name='Y Scale', default=True)
    bpy.types.Scene.vt_rtransform_YminScale = bpy.props.FloatProperty(name='Y min', default=0.5)
    bpy.types.Scene.vt_rtransform_YmaxScale = bpy.props.FloatProperty(name='Y max', default=10)
    
    bpy.types.Scene.vt_rtransform_ZsetScale = bpy.props.BoolProperty(name='Z Scale', default=True)
    bpy.types.Scene.vt_rtransform_ZminScale = bpy.props.FloatProperty(name='Z min', default=0.5)
    bpy.types.Scene.vt_rtransform_ZmaxScale = bpy.props.FloatProperty(name='Z max', default=10)
    
    
    bpy.types.Scene.vt_rtransform_XsetRotation = bpy.props.BoolProperty(name='X Rotation', default = False)
    bpy.types.Scene.vt_rtransform_XminRotation = bpy.props.IntProperty(name='X min', default=0)
    bpy.types.Scene.vt_rtransform_XmaxRotation = bpy.props.IntProperty(name='X max', default=0)
    
    bpy.types.Scene.vt_rtransform_YsetRotation = bpy.props.BoolProperty(name='Y Rotation', default = False)
    bpy.types.Scene.vt_rtransform_YminRotation = bpy.props.IntProperty(name='Y min', default=0)
    bpy.types.Scene.vt_rtransform_YmaxRotation = bpy.props.IntProperty(name='Y max', default=0)
    
    bpy.types.Scene.vt_rtransform_ZsetRotation = bpy.props.BoolProperty(name='Z Rotation', default = True)
    bpy.types.Scene.vt_rtransform_ZminRotation = bpy.props.IntProperty(name='Z min', default=0)
    bpy.types.Scene.vt_rtransform_ZmaxRotation = bpy.props.IntProperty(name='Z max', default=0)

          
def unregister():
    
    from bpy.utils import unregister_class
    
    unregister_class(VTOOLS_OP_setTransform)
    unregister_class(VTOOLS_OP_setRandomTransform)
    unregister_class(VTOOLS_PN_RandomTransform)

    del bpy.types.Scene.vt_rtransform_useTransform
    
    del bpy.types.Scene.vt_rtransform_XsetScale
    del bpy.types.Scene.vt_rtransform_XminScale
    del bpy.types.Scene.vt_rtransform_XmaxScale
    
    del bpy.types.Scene.vt_rtransform_YsetScale
    del bpy.types.Scene.vt_rtransform_YminScale
    del bpy.types.Scene.vt_rtransform_YmaxScale
    
    del bpy.types.Scene.vt_rtransform_ZsetScale
    del bpy.types.Scene.vt_rtransform_ZminScale
    del bpy.types.Scene.vt_rtransform_ZmaxScale
    
    
    
    del bpy.types.Scene.vt_rtransform_XsetRotation
    del bpy.types.Scene.vt_rtransform_XminRotation
    del bpy.types.Scene.vt_rtransform_XmaxRotation
    
    del bpy.types.Scene.vt_rtransform_YsetRotation
    del bpy.types.Scene.vt_rtransform_YminRotation
    del bpy.types.Scene.vt_rtransform_YmaxRotation
    
    del bpy.types.Scene.vt_rtransform_ZsetRotation
    del bpy.types.Scene.vt_rtransform_ZminRotation
    del bpy.types.Scene.vt_rtransform_ZmaxRotation
    
    
    
if __name__ == "__main__":
    register()
    