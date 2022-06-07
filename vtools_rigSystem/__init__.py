bl_info = {
    "name": "vtools - Rig System",
    "author": "Antonio Mendoza - Campero Games",
    "version": (0, 1, 0),
    "blender": (2, 80, 3),
    "location": "View3D > Tool Panel > Tool Tab >  vTools Rig System",
    "warning": "",
    "description": "Simple Rig system to create IK/FK Chain Bones",
    "category": "Animation",
}

 
"""
if "bpy" in locals():
    import importlib
    importlib.reload(rigSystem)
    importlib.reload(rigSystem_boneTools)
    importlib.reload(retargetAnimation)
    importlib.reload(curveTools)
        
else:
    from vtools_rigSystem import rigSystem
    from vtools_rigSystem import retargetAnimation
    from vtools_rigSystem import rigSystem_boneTools
    from vtools_rigSystem import curveTools

"""

if "bpy" in locals():
    import rigSystem
    import rigSystem_boneTools
    import retargetAnimation
    import curveTools
else:
    from vtools_rigSystem import rigSystem
    from vtools_rigSystem import retargetAnimation
    from vtools_rigSystem import rigSystem_boneTools
    from vtools_rigSystem import curveTools

import bpy
    
# -- REGISTRATION -- #        


modules = (rigSystem,rigSystem_boneTools,retargetAnimation, curveTools,) 
classes = ()


def register():
    
    #submodules
    for mod in modules:
       mod.register()
       
    
def unregister():

    #submodules
    for mod in modules:
        mod.unregister()
    
if __name__ == '__main__':
    register()
