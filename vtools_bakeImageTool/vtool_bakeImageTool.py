import bpy
from bpy.types import Panel, Operator 
from bl_ui.utils import PresetPanel


bl_info = {
    "name": "vtools - Blender Bake Image Tools",
    "author": "Antonio Mendoza",
    "location": "Properties > Bake > Bake Texture",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "description": "",
    "category": "Bake"  
}

class CyclesButtonsPanel:
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    COMPAT_ENGINES = {'CYCLES'}

    @classmethod
    def poll(cls, context):
        return context.engine in cls.COMPAT_ENGINES

def selectNodeForBaking(pMat,pNodeName):
    
    bakeImageNode = pMat.node_tree.nodes[pNodeName]
    bakeImageNode.select = True
    pMat.node_tree.nodes.active = bakeImageNode
        
        
         
class VTOOL_OP_newBakeTextureNode(Operator):
    bl_idname = "vtool.newbaketexture"
    bl_label = "New Bake Node"
    bl_description = "Create a Bake Texture node in every material within selected objects"
    
    def execute(self,context):
        
        found = False
        obj = bpy.context.view_layer.objects.active
        mat = obj.data.materials[obj.active_material_index]
        
        if mat != None:
            for n in mat.node_tree.nodes:
                if n.name.find("vt_bakeTextureNode") != -1:
                    if found == True:
                        mat.node_tree.nodes.remove(n)
                    found = True
                    
            
            if found == False:        
                n = mat.node_tree.nodes.new(type="ShaderNodeTexImage")
                n.name = "vt_bakeTextureNode"
                n.location[0] = -300
                n.location[1] = 800
                
            
            selectNodeForBaking(mat,"vt_bakeTextureNode")
                
                
        return{'FINISHED'}
    

class VTOOL_OP_useBakeImage(Operator):
    bl_idname = "vtool.usebakeimage"
    bl_label = "Use for Bake"
    bl_description = "Use selected image for bake in every material within the selected objects"
    
  
    def execute(self,context):
        
        obj = bpy.context.view_layer.objects.active
        mainMat = obj.data.materials[obj.active_material_index]
        mainBakeImageNode = obj.data.materials[obj.active_material_index].node_tree.nodes["vt_bakeTextureNode"]
        
        for obj in bpy.context.view_layer.objects.selected:
            for m in obj.data.materials:
                if m != None:
                    if m != mainMat:
                        for n in m.node_tree.nodes:
                            if n.name.find("vt_bakeTextureNode") != -1:
                                m.node_tree.nodes.remove(n)
                          
                        n = m.node_tree.nodes.new(type="ShaderNodeTexImage")
                        n.name = "vt_bakeTextureNode"
                        n.image = mainBakeImageNode.image
                        n.location[0] = -300
                        n.location[1] = 800
                        
                        selectNodeForBaking(m,"vt_bakeTextureNode")
                    
                    else:
                        
                        selectNodeForBaking(m,"vt_bakeTextureNode")
                        
        return{'FINISHED'}
    
    
class VTOOL_OP_removeBakeImage(Operator):
    bl_idname = "vtool.removebakeimage"
    bl_label = "Remove Bake Image"
    bl_description = "Remove bake image in every material within every selected object"
    
    def execute(self,context):
        
        for obj in bpy.context.view_layer.objects.selected:
            for m in obj.data.materials:
                if m != None:
                    for n in m.node_tree.nodes:
                        if n.name.find("vt_bakeTextureNode") != -1:
                            if n.image != None:
                                bpy.data.images.remove(n.image)
                            m.node_tree.nodes.remove(n)
    
                if len(m.node_tree.nodes) > 0:
                    selectNodeForBaking(m,m.node_tree.nodes[0].name)              
                        
        return{'FINISHED'}
        
class VTOOL_PT_baketexture(CyclesButtonsPanel, Panel):
    bl_label = "Bake Texture"
    bl_context = "render"
    bl_parent_id = "CYCLES_RENDER_PT_bake"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'CYCLES'}
    
    @classmethod
    def poll(cls,context):
        scene = context.scene
        cscene = scene.cycles
        return True

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.
        

        row = layout.row(align=True)
        
        obj = bpy.context.view_layer.objects.active
        mainMat = obj.data.materials[obj.active_material_index]
        
        if mainMat != None:
            idBakeNode = mainMat.node_tree.nodes.find("vt_bakeTextureNode")
            
            if  idBakeNode == -1:
                row.operator(VTOOL_OP_newBakeTextureNode.bl_idname, text=VTOOL_OP_newBakeTextureNode.bl_label, icon="ADD")
            else:
                bakeNode = mainMat.node_tree.nodes[idBakeNode]
                row.operator(VTOOL_OP_useBakeImage.bl_idname, text=VTOOL_OP_useBakeImage.bl_label, icon="TRACKER")
                row.operator(VTOOL_OP_removeBakeImage.bl_idname, text=VTOOL_OP_removeBakeImage.bl_label,icon="REMOVE")
                layout.template_image(bakeNode, "image", bakeNode.image_user)
        else:
            layout.label(text="None material selected")


#------------------------------ BATCH BAKE -----------------------#
                
class VTOOL_OP_batchBake(Operator):
    bl_idname = "vtool.batchbake"
    bl_label = "Batch Bake"
    bl_description = "Bake several objects by collection setup"
    
    
    def findBakeCollection(self, pColList, pNamePattern):
        
        rCol = None
        
        for c in pColList.children:
            print(c.name)
            if c.name.find(pNamePattern) != -1:
                rCol = c
                break
        
        return rCol
        
    def showAllCollection(self, pCollection):
        

        pCollection.hide_viewport = False
        for c in pCollection.children:
            self.showAllCollection(c)
            
    def pairCollections(self,pHPNamePattern, pLPNamePattern):
        collections = []
        for colScene in bpy.context.scene.collection.children:
            if colScene.name == "BAKE":
                
                colScene.hide_viewport = False
                self.showAllCollection(bpy.context.view_layer.layer_collection.children[colScene.name])
                
                colHigh = self.findBakeCollection(colScene, pHPNamePattern)
                colLow = self.findBakeCollection(colScene, pLPNamePattern)
                
                print(colHigh, " ", colLow)
                if colHigh != None and colLow != None:
                    
                    colHigh.hide_viewport = False
                    colLow.hide_viewport = False
                    
                    
                    
                    #bpy.context.view_layer.layer_collection.children[colHigh.name].hide_viewpor = False
                    #bpy.context.view_layer.layer_collection.children[colLow.name].hide_viewpor = False
                    
                    for ch in colHigh.children:
                        
                        highId = ch.name.replace(pHPNamePattern + "_", "")
                        print(highId)
                        for cl in colLow.children:
                            lowId = cl.name.replace(pLPNamePattern + "_","")
                            if lowId == highId:
                                
                                ch.hide_render = True
                                cl.hide_render = True
                                
                                ch.hide_viewport = False
                                cl.hide_viewport = False
            
                                collections.append((cl, ch))
                                break
        return collections
            
    def bakePairedCollections(self,pPairedCol):
        
        vl = bpy.context.view_layer
        for c in pPairedCol:
            
            clp = c[0]
            chp = c[1]
            
    
            bpy.ops.object.select_all(action='DESELECT')            
            
            lpObj = clp.objects[0]
            lpObj.select_set(True)
            vl.objects.active = lpObj
            
            
            for o in chp.objects:
                o.select_set(True)
            
            clp.hide_render = False
            chp.hide_render = False
            
            bpy.ops.object.bake(type=bpy.context.scene.cycles.bake_type)
            
            clp.hide_render = True
            chp.hide_render = True
        
    
    def execute(self,context):           
        pairedCollections = self.pairCollections(bpy.context.scene.vtool_batchBake_hpId, bpy.context.scene.vtool_batchBake_lpId)
        self.bakePairedCollections(pairedCollections)
        
        return{'FINISHED'}


class VTOOL_PT_batchBake(CyclesButtonsPanel, Panel):
    bl_label = "Batch Bake"
    bl_context = "render"
    bl_parent_id = "CYCLES_RENDER_PT_bake"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'CYCLES'}
    
    @classmethod
    def poll(cls,context):
        scene = context.scene
        cscene = scene.cycles
        return True

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.
        

        row = layout.row(align=True)
        
        layout.prop(bpy.context.scene,"vtool_batchBake_lpId")
        layout.prop(bpy.context.scene,"vtool_batchBake_hpId")        
        layout.operator(VTOOL_OP_batchBake.bl_idname, text=VTOOL_OP_batchBake.bl_label, icon="RENDER_STILL")
        
            
def register():
    from bpy.utils import register_class
    register_class(VTOOL_OP_useBakeImage)
    register_class(VTOOL_OP_newBakeTextureNode)
    register_class(VTOOL_OP_removeBakeImage)
    register_class(VTOOL_PT_baketexture)
    register_class(VTOOL_OP_batchBake)
    register_class(VTOOL_PT_batchBake)
    
    bpy.types.Scene.vtool_batchBake_hpId = bpy.props.StringProperty(name="HP Collection", default='HP')
    bpy.types.Scene.vtool_batchBake_lpId = bpy.props.StringProperty(name="LP Collection", default='LP')

def unregister():
    from bpy.utils import unregister_class
    unregister_class(VTOOL_OP_useBakeImage)
    unregister_class(VTOOL_OP_newBakeTextureNode)
    unregister_class(VTOOL_OP_removeBakeImage)
    unregister_class(VTOOL_PT_baketexture)
    unregister_class(VTOOL_OP_batchBake)
    unregister_class(VTOOL_PT_batchBake)
    

if __name__ == '__main__':
    register()