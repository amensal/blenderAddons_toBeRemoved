bl_info = {
    "name": "vtools - Distribute Atlas",
    "author": "Antonio Mendoza",
    "location": "View3D > edit mode > UV Menu > Distribute Atlas",
    "version": (0, 1, 0),
    "blender": (2, 90, 0),
    "warning": "",
    "description": "Distribute and scale selected object's uv",
    "category": "Mesh", 
}

import bpy
import math


#get biggest object dpending volume
def getBigestObject():
    ob = [0,0,0]
    bigObject = None
    
    for o in bpy.context.selected_objects:
        
        ob_volume = ob[0]*ob[1]*ob[2]
        o_volume = o.dimensions.x * o.dimensions.y * o.dimensions.z
        
        if o_volume > ob_volume:
            bigObject = o
            ob[0] = o.dimensions.x
            ob[1] = o.dimensions.y
            ob[2] = o.dimensions.z
    
    return bigObject

#get scale ratio depending the biggest object
def getBiggerDimension(pDim):
    
    dim = pDim.x
    
    if pDim.x > pDim.y and pDim.x > pDim.z:
        dim = pDim.x
    elif pDim.y > pDim.x and pDim.y > pDim.x:
        dim = pDim.y
    elif pDim.z > pDim.x and pDim.z > pDim.y:
        dim = pDim.z
    
    return dim
    
def getScaleRatio(pDim1, pDim2):
    
    ratio = 1
    
    ratio = getBiggerDimension(pDim1) / getBiggerDimension(pDim2)
    
    
    """
    #depending on volume
    vol1 = pDim1.x * pDim1.y * pDim1.z
    vol2 = pDim2.x * pDim2.y * pDim2.z
    
    ratio = vol1 / vol2
    
    """
    return ratio

#move and scale objects uv
def transformAllUV(pObj, pXDesp, pYDesp, pBigestObject):
    
    for loop in pObj.data.loops:
        
        coord = pObj.data.uv_layers.active.data[loop.index].uv

        if pObj.name != pBigestObject.name:
            ratio = getScaleRatio (pBigestObject.dimensions, pObj.dimensions)
            coord /= ratio
        
        coord.x += pXDesp
        coord.y -= pYDesp
        
#get rows and columns to create the uv grid                
def getRowsAndColumns(pNumObjects):
    columns = math.sqrt(pNumObjects)
    mod = math.modf(columns)
    
    if mod[0] != 0:
        columns = mod[1] + 1
    else: 
        columns = mod[1]
    
    rows = math.modf(pNumObjects/columns)[1]
    
    if mod[0] != 0:
        rows += 1
        
        
    return (columns, rows)

#main function
def distributeAtlas(pBigestObjet): 
    
    bpy.ops.object.mode_set(mode='OBJECT')
     
    numObjects = len(bpy.context.selected_objects)
    biggestObject = getBigestObject()
 
    cells = getRowsAndColumns(numObjects)
   
    column = cells[0]
    row = 0
    cont = 0
    for o in bpy.context.selected_objects:
        transformAllUV(o, cont, row, biggestObject)
        cont += 1
        #if reach the max columns
        if cont == column:
            cont = 0
            row += 1
    
    bpy.ops.object.mode_set(mode='EDIT')

#menu panel            
def vtools_distributeAtlas(self, context):
    
    layout = self.layout
    layout.separator()
    layout.operator(VTOOLS_OP_distributeAtlas.bl_idname, text=VTOOLS_OP_distributeAtlas.bl_label)   
          

class VTOOLS_OP_distributeAtlas(bpy.types.Operator):
    bl_idname = "vtools.distributeatlas"
    bl_label = "Distribute Atlas"
    bl_description = "Distribute and scale selected object's UV"
    bl_options = {'REGISTER', 'UNDO'}
         
    def execute(self,context):
        distributeAtlas(bpy.context.object)        
        return {'FINISHED'}
            


#------ REGISTER ---#

def register():
    
    from bpy.utils import register_class
    
    register_class(VTOOLS_OP_distributeAtlas)
    bpy.types.VIEW3D_MT_uv_map.append(vtools_distributeAtlas)

          
def unregister():
    
    from bpy.utils import unregister_class
    
    unregister_class(VTOOLS_OP_distributeAtlas)    
    bpy.types.VIEW3D_MT_object_apply.remove(vtools_distributeAtlas)

    
if __name__ == "__main__":
    register()        
        