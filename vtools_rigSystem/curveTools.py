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
    return boneName
    
class VTOOLS_OP_RS_deleteInvalidCurves(bpy.types.Operator):
    bl_idname = "vtoolsrigsystem.deleteinvalidcurves"
    bl_label = "Delete Invalid Animation Curves"
    bl_description = "Delete curve channels with errors"
    
    bySource : bpy.props.BoolProperty(name="Delete By Source", default = False)
    
    def deleteCurvesBySource(self,pAction, pSource):
        a = pAction
        for fc in a.fcurves:
            finder = fc.data_path.find(pSource)
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
    bl_description = "Substitute names within fcurves actions. All = rename also bones and vertex groups"
    
    renameBone : bpy.props.BoolProperty(name="Rename Bone and Vertex Group", default = False)
    
    def renameAnimationCurves(self, pAction):
        a = pAction
        oldString = bpy.context.scene.vt_curveOldstr
        newString = bpy.context.scene.vt_curveNewstr
        
        if self.renameBone == True:
            #RENAME BONE
            arm = bpy.context.object
            for b in arm.pose.bones:
                if b.name == oldString:
                    b.name = newString
            
            #RENAME VERTEX GROUPS
            for o in arm.children:
                if o.type == "MESH":
                    for vg in o.vertex_groups:
                        if vg.name == oldString:
                            vg.name = newString
                     
        #RENAME CURVES IN GROUPS
        for g in a.groups:
            targetBoneName = g.name.replace(oldString, newString)
            #if bpy.context.object.pose.bones.find(targetBoneName) != -1: 
                #if bpy.context.object.pose.bones[targetBoneName] in bpy.context.selected_pose_bones: 
            g.name = targetBoneName
            for c in g.channels:
                c.update()
                c.data_path = c.data_path.replace(bpy.context.scene.vt_curveOldstr, bpy.context.scene.vt_curveNewstr)
        
        #RENAME CURVES OUTSIDE GROUPS        
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

class VTOOLS_OP_RS_pasteKeyToAllActions(bpy.types.Operator):
    bl_idname = "vtoolsrigsystem.pastekeytoallactions"
    bl_label = "Paste Key to all actions"
    bl_description = "Paste key to all actions"
    
    def pasteKey(self, pOriginAction, pAction):
        o = bpy.data.actions[pOriginAction]
        a = pAction    
        for c in bpy.data.actions[o.name].fcurves:
            for k in c.keyframe_points:
                if k.select_control_point == True:
                    
                    destAction = bpy.data.actions[a.name]
                    
                    curveFound = False

                    for cd in destAction.fcurves:
                        if c.data_path == cd.data_path and c.array_index == cd.array_index:
                            if c.group != None and cd.group != None :
                                if c.group.name == cd.group.name:
                                    curveFound = True
                            else:
                                curveFound = True
                                
                    if curveFound == False:
                        newChannel = destAction.fcurves.new("vToolsNewActionChannel")
                        
                        #CREATE A GROUP IF NOT FOUND
                        groupFound = False
                        for group in destAction.groups:
                            if c.group != None:
                                if group.name == c.group.name:
                                    groupFound = True
                                    break
                        
                        if groupFound == False and c.group != None:
                            destAction.groups.new(c.group.name)
                        
                        if c.group != None:
                            newChannel.group = destAction.groups[c.group.name]  
                        newChannel.array_index = c.array_index  
                        newChannel.data_path = c.data_path
                          
        
        try:
            bpy.context.object.animation_data.action = bpy.data.actions[a.name]
            bpy.ops.action.paste()
        except:
            print("keys cannot be pasted")
        
        
    def execute(self, context):
        originalActionName = bpy.context.object.animation_data.action.name
        
        for a in bpy.data.actions:
            if a.name != originalActionName: 
                pattern = bpy.context.scene.vt_curveID
                
                if pattern == "" or a.name.find(pattern) != -1:
                    self.pasteKey(originalActionName, a)
        
        bpy.context.object.animation_data.action = bpy.data.actions[originalActionName]
        
        
        return {'FINISHED'}
                    
class VTOOLS_PT_animationCurveTools(bpy.types.Panel):
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
        
        box.operator(VTOOLS_OP_RS_renameAnimationCurves.bl_idname, text="Rename Curves")
        op = box.operator(VTOOLS_OP_RS_renameAnimationCurves.bl_idname, text="Rename All")
        op.renameBone = True
        deleteBySource = box.operator(VTOOLS_OP_RS_deleteInvalidCurves.bl_idname, text="Delete Curves By Source")
        deleteBySource.bySource = True
        
        box = layout.box()
        box.prop(bpy.context.scene,"vt_curveID", text="Action ID")
        box.operator(VTOOLS_OP_RS_pasteKeyToAllActions.bl_idname, text="Paste Key")
        

#------- HEREDAR PARA OTROS PANELES

class VTOOLS_PT_animationCurveTools_VIEW3D(VTOOLS_PT_animationCurveTools):
    bl_space_type = 'VIEW_3D'
    
class VTOOLS_PT_animationCurveTools_DOPESHEET(VTOOLS_PT_animationCurveTools):
    bl_space_type = 'DOPESHEET_EDITOR'
    
class VTOOLS_PT_animationCurveTools_GRAPHEDITOR(VTOOLS_PT_animationCurveTools):
    bl_space_type = 'GRAPH_EDITOR'
    
#----------------------

    
    
    
class VTOOLS_OP_RS_bakeAllActions(bpy.types.Operator):
    bl_idname = "vtoolretargetsystem.bakeallactions"
    bl_label = "Bake All Actions"
    bl_description = "Bake and overwrite animation from selected bones"
    
    onlyClean : bpy.props.BoolProperty(name="Only Clean FCurves", default = False)
    
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
        
        
    
    def execute(self, context):
        arm = bpy.context.object.name
        
        if bpy.context.scene.vt_bakeOnlyActive == True:
            self.bakeAction(bpy.context.object.animation_data.action)
        else:
            for a in bpy.data.actions:
                self.bakeAction(a)
            
            bpy.ops.pose.constraints_clear()

        return {'FINISHED'}       

class VTOOLS_PT_BakingAnimation(bpy.types.Panel):
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
        opBake = col.operator(VTOOLS_OP_RS_bakeAllActions.bl_idname, text="Bake Actions")
        opBake.onlyClean = False
        opClean = col.operator(VTOOLS_OP_RS_bakeAllActions.bl_idname, text="Clean Curves")
        opClean.onlyClean = True
        


#---------- REGISTER ----------#
    
def register():  
    
    from bpy.utils import register_class
    #register_class(VTOOLS_PT_animationCurveTools)
    register_class(VTOOLS_PT_animationCurveTools_VIEW3D)
    register_class(VTOOLS_PT_animationCurveTools_DOPESHEET)
    register_class(VTOOLS_PT_animationCurveTools_GRAPHEDITOR)
    register_class(VTOOLS_OP_RS_renameAnimationCurves)
    register_class(VTOOLS_OP_RS_deleteInvalidCurves)
    register_class(VTOOLS_OP_RS_bakeAllActions)
    register_class(VTOOLS_PT_BakingAnimation)
    
    register_class(VTOOLS_OP_RS_pasteKeyToAllActions)

    bpy.types.Scene.vt_onlyActiveAction = bpy.props.BoolProperty(default = False)
    
    bpy.types.Scene.vt_curveOldstr = bpy.props.StringProperty(default="",description="String to be found and replaced")
    bpy.types.Scene.vt_curveNewstr = bpy.props.StringProperty(default="",description="String that will replace the old string")
    
    
    bpy.types.Scene.vt_curveID = bpy.props.StringProperty(default="",description="Curve String Identificator")

    
    bpy.types.Scene.vt_bakeOnlyActive = bpy.props.BoolProperty(default = False, description="Bake only active action")
    bpy.types.Scene.vt_clearLocation = bpy.props.BoolProperty(default = True)
    bpy.types.Scene.vt_clearScale = bpy.props.BoolProperty(default = True)
    bpy.types.Scene.vt_clearRotation = bpy.props.BoolProperty(default = False)
    
     
def unregister():
    
    from bpy.utils import unregister_class
    #unregister_class(VTOOLS_PT_animationCurveTools)
    unregister_class(VTOOLS_PT_animationCurveTools_VIEW3D)
    unregister_class(VTOOLS_PT_animationCurveTools_DOPESHEET)
    unregister_class(VTOOLS_PT_animationCurveTools_GRAPHEDITOR)
    unregister_class(VTOOLS_OP_RS_renameAnimationCurves)
    unregister_class(VTOOLS_OP_RS_deleteInvalidCurves)
    unregister_class(VTOOLS_OP_RS_bakeAllActions)
    unregister_class(VTOOLS_PT_BakingAnimation)
    
    
    unregister_class(VTOOLS_OP_RS_pasteKeyToAllActions)


    del bpy.types.Scene.vt_onlyActiveAction
    del bpy.types.Scene.vt_curveOldstr
    del bpy.types.Scene.vt_curveNewstr
    
    del bpy.types.Scene.vt_curveID
    
    del bpy.types.Scene.vt_clearLocation
    del bpy.types.Scene.vt_clearScale
    del bpy.types.Scene.vt_clearRotation

    
    
    

#---------- CLASES ----------#



if __name__ == "__main__":
    register() 