import bpy


def getCollectionByName(pCollName):
    
    res = None
    
    if bpy.data.collections.find(pCollName) != -1:
        res = bpy.data.collections[pCollName]

    return res


# ----- Field Area Collection -------#
class VTOOLS_UL_fieldAreaUI(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
            layout.prop(item, "name", text="", emboss=False, translate=False)
         
class VTOOLS_CC_fieldAreaType(bpy.types.PropertyGroup):
       
    name = bpy.props.StringProperty(default='')
    fieldAreaID = bpy.props.IntProperty()
    fieldAreaObject = bpy.props.PointerProperty(name="", type=bpy.types.Object)
        
        
class VTOOLS_PT_GolfRoyaleTools(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Golf Royale"
    bl_category = 'Campero Tools '
    bl_options = {'DEFAULT_CLOSED'}       
        
    @classmethod
    def poll(cls, context):
        
        return (context.mode == 'OBJECT')
        #return (context.object)
    
    def draw(self,context):
        enabled = True
        layout = self.layout
        
        layout.prop(bpy.context.scene, "ct_fieldBaseHP")
        bm = bpy.context.scene.ct_fieldBaseHP
        
        if bm == None:    
            enabled = False
            
        col = layout.column()
        col.enabled = enabled
        
        col.label(text="Field Areas:")
        col.template_list('VTOOLS_UL_fieldAreaUI', "fieldAreaID", context.scene, "ct_fieldAreaCollection", context.scene, "ct_fieldAreaCollection_ID", rows=8)
            
        
# -- REGISTRATION -- #        

modules = () 

    
def register():
    
    from bpy.utils import register_class
    
    bpy.utils.register_class(VTOOLS_PT_GolfRoyaleTools)
    bpy.utils.register_class(VTOOLS_UL_fieldAreaUI)
    bpy.utils.register_class(VTOOLS_CC_fieldAreaType)
    
    #submodules
    for mod in modules:
        mod.register()
    
    bpy.types.Scene.ct_fieldBaseHP = bpy.props.PointerProperty(name="Base Mesh", type=bpy.types.Object)
    
    bpy.types.Scene.ct_fieldAreaCollection_ID = bpy.props.IntProperty(default = -1)
    bpy.types.Scene.ct_fieldAreaCollection = bpy.props.CollectionProperty(type=VTOOLS_CC_fieldAreaType)
    
    
def unregister():
    from bpy.utils import unregister_class
    
    bpy.utils.unregister_class(VTOOLS_PT_GolfRoyaleTools)
    bpy.utils.unregister_class(VTOOLS_UL_fieldAreaUI)
    bpy.utils.unregister_class(VTOOLS_CC_fieldAreaType)
        
    #submodules
    for mod in modules:
        mod.unregister()
    
    del bpy.types.Scene.ct_fieldBaseHP
    
if __name__ == '__main__':
    register()
    