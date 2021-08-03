bl_info = {
    "name": "vtools - Rig System",
    "author": "Antonio Mendoza - Campero Games",
    "version": (0, 0, 3),
    "blender": (2, 80, 3),
    "location": "View3D > Tool Panel > Tool Tab >  vTools Rig System",
    "warning": "",
    "description": "Simple Rig system to create IK/FK Chain Bones",
    "category": "Animation",
}

if "bpy" in locals():
    import importlib
    importlib.reload(rigSystem)
    importlib.reload(rigSystem_boneTools)
    importlib.reload(retargetAnimation)
    
    
    
else:
      
    from vtools_rigSystem import rigSystem
    from vtools_rigSystem import retargetAnimation
    from vtools_rigSystem import rigSystem_boneTools
    
    #remove when releasingp
    import importlib
    importlib.reload(rigSystem)
    importlib.reload(rigSystem_boneTools)
    importlib.reload(retargetAnimation)
    
    
import bpy 
 
"""                
class VTOOLS_PT_LayerProperties(bpy.types.Panel):
    bl_label = "Image Transform"
    bl_parent_id = "VTOOLS_PT_MultiLayerPainting"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
               
        layerNode = paintingLayers.getLayerNodeSelected()
        colorSpace = paintingLayers.getLayerColorSpace()
"""                  
        
class VTOOLS_PT_RigSystem(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Rig System"
    bl_category = 'Tool'
    bl_options = {'DEFAULT_CLOSED'}       
        
    @classmethod
    def poll(cls, context):
        
        return (context.object)
    
    def draw(self,context):
        layout = self.layout
        
        
# -- REGISTRATION -- #        

modules = (

    rigSystem,
    rigSystem_boneTools,
    retargetAnimation,
    

) 

classes = (VTOOLS_PT_RigSystem,)

def register():
    
    from bpy.utils import register_class
    
    #classes
    for cls in classes:
        register_class(cls)
    
    #submodules
    for mod in modules:
       mod.register()
    
    #createNodes.init()
    
def unregister():
    from bpy.utils import unregister_class
    
    #clases     
    bpy.utils.unregister_class(VTOOLS_PT_RigSystem)   
        
    #submodules
    for mod in modules:
        mod.unregister()
    
    
if __name__ == '__main__':
    register()
    unregister()
    register()
               
