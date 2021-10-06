import bpy 


def getFCurveTargetBone(pDataPath):
    
    boneName = ""
    copy = False
    
    for c in pDataPath:
        if copy == True and c != "]":
            boneName += c
            
        if c == "[":
            copy = True
        elif c == "]":
            copy = False
            break
    
    boneName = boneName.replace('"', '')
    print("BONENAME ----", boneName)
    return boneName
    
class VTOOLS_OP_RS_deleteInvalidCurves(bpy.types.Operator):
    bl_idname = "vtoolsrigsystem.deleteinvalidcurves"
    bl_label = "Delete Invalid Animation Curves"
    bl_description = "Delete curve channels with errors"
    
    bySource = bpy.props.BoolProperty(name="Delete By Source", default = False)
    
    def deleteCurvesBySource(self,pAction, pSource):
        a = pAction
        for fc in a.fcurves:
            finder = fc.data_path.find(pSource)
            print("Buscando---- ", pSource, " ", finder)
            if finder != -1:
                a.fcurves.remove(fc)
        
        for g in a.groups:
            finder = g.name.find(pSource)
            if finder != -1:
                a.groups.remove(g)                
    
    def deleteInvalidCurves(self, pAction):
        a = pAction
        
        for fc in a.fcurves:
            if fc.group == None:
                boneName = getFCurveTargetBone(fc.data_path)
                print(boneName)
                finder = bpy.context.object.pose.bones.find(boneName)
                if finder == -1:
                    a.fcurves.remove(fc)
        
                
        if bpy.context.object.type == "ARMATURE":        
            for g in a.groups:
                finder = bpy.context.object.pose.bones.find(g.name)
                if finder == -1:
                    for c in g.channels:
                        a.fcurves.remove(c)
                    a.groups.remove(g)
        
                        
    def execute(self, context):
        
        if self.bySource == False: #DELETE INVALID
            if bpy.context.scene.vt_onlyActiveAction == False:
                for a in bpy.data.actions:
                    self.deleteInvalidCurves(a)
            else:
                self.deleteInvalidCurves(bpy.context.object.animation_data.action)
        else: #DELETE BY SOURCE
            if bpy.context.scene.vt_onlyActiveAction == False:
                for a in bpy.data.actions:
                    self.deleteCurvesBySource(a, bpy.context.scene.vt_curveOldstr)
            else:
                self.deleteCurvesBySource(bpy.context.object.animation_data.action, bpy.context.scene.vt_curveOldstr)  
                  
                    
        return {'FINISHED'}
    
class VTOOLS_OP_RS_renameAnimationCurves(bpy.types.Operator):
    bl_idname = "vtoolsrigsystem.renameanimationcurves"
    bl_label = "Rename Animation Curves"
    bl_description = "Substitute names within fcurves actions"
    
    def renameAnimationCurves(self, pAction):
        a = pAction    
        for g in a.groups:
            targetBoneName = g.name.replace(bpy.context.scene.vt_curveOldstr, bpy.context.scene.vt_curveNewstr)
            #if bpy.context.object.pose.bones.find(targetBoneName) != -1: 
                #if bpy.context.object.pose.bones[targetBoneName] in bpy.context.selected_pose_bones: 
            g.name = targetBoneName
            for c in g.channels:
                c.update()
                c.data_path = c.data_path.replace(bpy.context.scene.vt_curveOldstr, bpy.context.scene.vt_curveNewstr)        
                
        for fc in a.fcurves:
            if fc.group == None:
                fc.data_path = fc.data_path.replace(bpy.context.scene.vt_curveOldstr, bpy.context.scene.vt_curveNewstr)
        
    def execute(self, context):
        
        
        if bpy.context.scene.vt_onlyActiveAction == False:
            for a in bpy.data.actions:
                self.renameAnimationCurves(a)
        else:
            self.renameAnimationCurves(bpy.context.object.animation_data.action)
        
        return {'FINISHED'}

                    
class VTOOLS_PN_retargetAnimation(bpy.types.Panel):
    bl_label = "Animation Curve Tools"
    #bl_parent_id = "VTOOLS_PN_RigSystem"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Rig vTools'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        
        layout.prop(bpy.context.scene,"vt_onlyActiveAction", text="Only Active Action")
        
        box = layout.box()
        col = box.column(align=True)
        col.prop(bpy.context.scene,"vt_curveOldstr", text="Source")
        col.prop(bpy.context.scene,"vt_curveNewstr", text="New")
        
        box.operator(VTOOLS_OP_RS_renameAnimationCurves.bl_idname, text="Rename Animation Curves")
        
        col = layout.column(align=True)
        col.operator(VTOOLS_OP_RS_deleteInvalidCurves.bl_idname, text="Delete Invalid Curves")
        deleteBySource = col.operator(VTOOLS_OP_RS_deleteInvalidCurves.bl_idname, text="Delete Curves By Source")
        deleteBySource.bySource = True
        
        

class VTOOLS_OP_RS_bakeAllActions(bpy.types.Operator):
    bl_idname = "vtoolretargetsystem.bakeallactions"
    bl_label = "Bake All Actions"
    bl_description = "Bake and overwrite animation from selected bones"
    
    onlyClean = bpy.props.BoolProperty(name="Only Clean FCurves", default = False)
    
    def cleanKeyFrames(self, pAction):
        
        for g in pAction.groups:
            if bpy.context.object.pose.bones.find(g.name) != -1: 
                if bpy.context.object.pose.bones[g.name] in bpy.context.selected_pose_bones:
                    for c in g.channels:
                        if bpy.context.scene.vt_clearLocation == True and c.data_path.upper().find("LOCATION") != -1:
                            pAction.fcurves.remove(c)
                        elif bpy.context.scene.vt_clearScale == True and c.data_path.upper().find("SCALE") != -1:
                            pAction.fcurves.remove(c)
                        elif bpy.context.scene.vt_clearRotation == True and c.data_path.upper().find("ROTATION") != -1:
                            pAction.fcurves.remove(c)    
                            
                        #while len(c.keyframe_points) > 0:
                        #    c.keyframe_points.remove(c.keyframe_points[0])

    
    def findLastFrame(self, pAction):
        
        lastKey = 0        
        for g in pAction.groups:
            for c in g.channels:
                for k in c.keyframe_points:
                    tmpLast = k.co[0]
                    if tmpLast >= lastKey:
                        lastKey = tmpLast

        return lastKey
                        
                        
    def bakeAction(self, pAction):
        
        bpy.ops.object.mode_set(mode='POSE')
        a = pAction
            
        if self.onlyClean == False:    
            bpy.context.object.animation_data.action = a
            lastFrame = self.findLastFrame(a)
            #print(a.name, " " , lastFrame)
            bpy.ops.nla.bake(frame_start=0, frame_end=lastFrame, only_selected=True, visual_keying=True, clear_constraints=False, use_current_action=True, clean_curves= False, clear_parents=False, bake_types={'POSE'})
        
        self.cleanKeyFrames(a)     
        bpy.ops.pose.constraints_clear()
        
    
    def execute(self, context):
        arm = bpy.context.object.name
        
        if bpy.context.scene.vt_bakeOnlyActive == True:
            self.bakeAction(bpy.context.object.animation_data.action)
        else:
            for a in bpy.data.actions:
                self.bakeAction(a)

        return {'FINISHED'}       

class VTOOLS_PN_BakingAnimation(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Baking"
    bl_category = 'Rig vTools'
    #bl_parent_id = "VTOOLS_PT_RigSystem"
    #bl_options = {'DEFAULT_CLOSED'} 
    
        
    @classmethod
    def poll(cls, context):
        return (context.object)
    
    def draw(self,context):
        
        layout = self.layout
        
        layout.prop(bpy.context.scene,"vt_bakeOnlyActive", text="Only Active Action")
        layout.label(text="Remove Curve") 
        row = layout.row(align=True)
        
        row.prop(bpy.context.scene,"vt_clearLocation", text="Location", toggle=True)
        row.prop(bpy.context.scene,"vt_clearScale", text="Scale", toggle=True)
        row.prop(bpy.context.scene,"vt_clearRotation", text="Rotation", toggle=True)
        
        col = layout.column(align=True)
        col.operator(VTOOLS_OP_RS_bakeAllActions.bl_idname, text="Bake Actions")
        opClean = col.operator(VTOOLS_OP_RS_bakeAllActions.bl_idname, text="Clean Curves")
        opClean.onlyClean = True
        


#---------- REGISTER ----------#
    
def register():  
    
    from bpy.utils import register_class
    register_class(VTOOLS_PN_retargetAnimation)
    register_class(VTOOLS_OP_RS_renameAnimationCurves)
    register_class(VTOOLS_OP_RS_deleteInvalidCurves)
    register_class(VTOOLS_OP_RS_bakeAllActions)
    register_class(VTOOLS_PN_BakingAnimation)

    bpy.types.Scene.vt_onlyActiveAction = bpy.props.BoolProperty(default = False)
    
    bpy.types.Scene.vt_curveOldstr = bpy.props.StringProperty(default="",description="String to be found and replaced")
    bpy.types.Scene.vt_curveNewstr = bpy.props.StringProperty(default="",description="String that will replace the old string")

    
    bpy.types.Scene.vt_bakeOnlyActive = bpy.props.BoolProperty(default = False, description="Bake only active action")
    bpy.types.Scene.vt_clearLocation = bpy.props.BoolProperty(default = True)
    bpy.types.Scene.vt_clearScale = bpy.props.BoolProperty(default = True)
    bpy.types.Scene.vt_clearRotation = bpy.props.BoolProperty(default = False)
    
     
def unregister():
    
    from bpy.utils import unregister_class
    unregister_class(VTOOLS_PN_retargetAnimation)
    unregister_class(VTOOLS_OP_RS_renameAnimationCurves)
    unregister_class(VTOOLS_OP_RS_deleteInvalidCurves)
    unregister_class(VTOOLS_OP_RS_bakeAllActions)
    unregister_class(VTOOLS_PN_BakingAnimation)


    del bpy.types.Scene.vt_onlyActiveAction
    del bpy.types.Scene.vt_curveOldstr
    del bpy.types.Scene.vt_curveNewstr
    
    del bpy.types.Scene.vt_clearLocation
    del bpy.types.Scene.vt_clearScale
    del bpy.types.Scene.vt_clearRotation

    
    
    

#---------- CLASES ----------#



if __name__ == "__main__":
    register() 