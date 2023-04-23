bl_info = {
    "name": "vtools Auto Incremental Save",
    "author": "Antonio Mendoza",
    "version": (0, 3, 5),
    "blender": (3, 0, 0),
    "location": "File Menu",
    "description": "Auto Incremental Current File. If your file is numbered at the end of the file, it will save incremental in the same file. If there is no number, it will create a new folder in order to storage incremental versions.",
    "category": "User Interface"
}

import bpy
import os 
import glob 
from bpy.props import *
from bpy_extras.io_utils import ExportHelper
import shutil
import textwrap
import bpy_extras

_globalVersionFolder = "BlenderVersions"

# --- DEF --- #

def getVersion(p_fileName):
    
    version = ""
    separator = False
    nameLeng = len(p_fileName)
    cont = nameLeng - 1
    isNumber = p_fileName[cont].isdigit()
    
    while cont >= 0 and isNumber:
        
        version = p_fileName[cont] + version
        cont = cont - 1
        if p_fileName[cont] == "_":
            separator = True
            break
        else:
            isNumber = p_fileName[cont].isdigit()
    
    if version == "" or separator == False:
        version = "NONE"
        
    return version

    
def incrementVersion(p_version):
    
    version = ""
    nameLeng = len(p_version)
    cont = nameLeng - 1
    sum = 0
    add = 0
    
    nVersion = int(p_version)
    nVersion += 1
    version = str(nVersion)
    
    while len(version) < len(p_version):
        version = "0" + version
        
    return version
    


def hasVersion(p_fileName):
    
    cont = len(p_fileName) - 1
    isNumber = p_fileName[cont].isdigit()
    
    return isNumber

def getVersionPosition(p_fileName):
    
    i = len(p_fileName) - 1
    while p_fileName[i] != "_":
        i = i - 1
    i += 1
    
    
    return i 
    
def getIncrementedFile(p_file="", p_inIncFolder = True):
    
    incrementedFile = ""
    file = p_file
    baseName= os.path.basename(file)
    folder = os.path.dirname(file)
    fileName = os.path.splitext(baseName)[0]
    versionFolderName =  "" #_globalVersionFolder
    type = os.path.splitext(baseName)[1]
    version = getVersion(fileName)
    newVersion = ""
    newFileName = ""
    
    #if there is not a first version file, create the new one
    if version == "NONE":
        versionFolderName = os.path.join(_globalVersionFolder, "versions_" + fileName)
        version = "000"
        fileName = fileName + "_000" 
        
    newVersion = incrementVersion(version) 
    numVersions = fileName.count(version)
    if numVersions >= 1:
        posVersion = getVersionPosition(fileName)
        fileName = fileName[:posVersion]
        newFileName = fileName + newVersion
        
    else:
        newFileName = fileName.replace(version,newVersion)
        
    newFullFileName = newFileName + type
    
    if p_inIncFolder:
        versionFolder = os.path.join(folder,versionFolderName)
        incrementedFile = os.path.join(versionFolder, newFullFileName)
    else:
        incrementedFile = os.path.join(folder, newFullFileName)
    
    return incrementedFile 

def getLastVersionFile(p_file = ""):
    
    #look into the version folder for the last one
    #if there is not anything, return an empty string
    
    lastFile = ""
    file = p_file
    baseName= os.path.basename(file)
    folder = os.path.dirname(file)
    folder = os.path.join(folder, _globalVersionFolder)
    fileName = os.path.splitext(baseName)[0]
    versionFolderName = "versions_" + fileName    
    versionFolder = os.path.join(folder,versionFolderName)

    if os.path.exists(versionFolder):
        filesToSearch = os.path.join(versionFolder, "*.blend")
        if len(filesToSearch) > 0:
            blendFiles = sorted(glob.glob(filesToSearch))
            if len(blendFiles) > 0:
                lastFile = blendFiles[len(blendFiles)-1]
    else:
        os.makedirs(versionFolder)
          
    return lastFile
    
#ADD VERSION TO UI LIST
def addVersionToList(pSavedFilePath, pVersionInfo):
    
    savedFilePath = pSavedFilePath
    savedFileName = os.path.basename(pSavedFilePath)
    versionList = bpy.context.scene.vtFileVersionCollection
    
    #INSERT ITEM
    newVersionItem = versionList.add()
    newVersionItem.filePath = savedFilePath
    newVersionItem.fileName = savedFileName
    newVersionItem.info = pVersionInfo
    
    fileName = os.path.splitext(savedFileName)[0]
    newVersionItem. fileVersion = getVersion(fileName)
    
    #MOVE TO FIRST
    lastItem = len(versionList) - 1
    versionList.move(lastItem, 0)
      
def saveIncremental(pVersionInfo):
    
    # check if it has version, 
    # if it has a version in the name save in the same folder with a version up number,
    # if not, save a new version within the version folder.
    
    currentFile = bpy.data.filepath
    baseName= os.path.basename(currentFile)
    currentFileName= os.path.splitext(baseName)[0]
    newFile = ""
        
    hasVersion = getVersion(currentFileName)

    if hasVersion == "NONE":
        
        # save in the version folder
        lastFile = getLastVersionFile(p_file = currentFile)
        if lastFile == "":
            lastFile = currentFile
        
        newFile = getIncrementedFile(p_file = lastFile, p_inIncFolder = True)
        """
        bpy.ops.wm.save_as_mainfile(filepath=currentFile, copy=False)
        bpy.ops.wm.save_as_mainfile(filepath=newFile, copy=True)
        """

        #SAVE MASTER
        bpy.ops.wm.save_as_mainfile(filepath=currentFile, copy=True)
        
        #COPY MASTER FILE AND SAVE AS INCREMENTAL
        shutil.copyfile(currentFile, newFile)
        
    else:
        # save a new version in file current
        newFile = getIncrementedFile(p_file = currentFile, p_inIncFolder = False)
        bpy.ops.wm.save_as_mainfile(filepath=newFile)
    
    #ADD VERSION TO LIST
    addVersionToList(newFile, pVersionInfo)
        
    return newFile

def getSelectedVersion():
    
    versionItem = None
    scene = bpy.context.scene
    if bpy.context.scene.vtFileVersionCollection_ID != -1 and bpy.context.scene.vtFileVersionCollection_ID  < len(bpy.context.scene.vtFileVersionCollection):
        versionItem = scene.vtFileVersionCollection[scene.vtFileVersionCollection_ID]
        
    return versionItem

# --- OPERATORS --- #


class VTOOLS_OP_saveIncremental(bpy.types.Operator):
    bl_idname = "wm.saveincremental"
    bl_label = "Save incremental"
    
    versionInfo : bpy.props.StringProperty(default="")
    
    def draw(self, context):
        
        layout = self.layout
        layout.prop(self, "versionInfo", text="Version Info ")    
        
        
    def invoke (self, context, event):
        return context.window_manager.invoke_props_dialog(self)
        
    def execute(self,context):
        
        if bpy.data.is_saved == True:
             
            savedFilePath = saveIncremental(self.versionInfo)
            savedFileName = os.path.basename(savedFilePath)
            textReport = savedFileName + "version saved"
            self.report({'INFO'},textReport)
      
        else:
            bpy.ops.wm.save_as_mainfile('INVOKE_DEFAULT')
          
            
        return {'FINISHED'}   

class VTOOLS_OP_loadVersion(bpy.types.Operator):
    bl_idname = "vtools.loadversion"
    bl_label = "Load selected version"
    bl_description = "Load selected Version. Save as main file in order to overwrite it"
    
    def execute(self, context):
        
        vList =  bpy.context.scene.vtFileVersionCollection
        vListID =  bpy.context.scene.vtFileVersionCollection_ID
        
        if vListID != -1:
            vItem = vList[vListID]
            if os.path.isfile(vItem.filePath) == True:
                bpy.ops.wm.open_mainfile(filepath=vItem.filePath)
                #shutil.copyfile(currentFile, newFile)
            else:
                self.report({"ERROR"}, "Version not Found")
        
        return {'FINISHED'}

class VTOOLS_OP_removeVersion(bpy.types.Operator):
    bl_idname = "vtools.removeversion"
    bl_label = "Remove selected version"
    bl_description = "Remove the selected version from the list. NOTE: this does not remove the actual file"
    
    def execute(self, context):
        
        vList =  bpy.context.scene.vtFileVersionCollection
        vListID =  bpy.context.scene.vtFileVersionCollection_ID
        newID = vListID
        numElements = len(vList) - 1
        
        if vListID == numElements:
            newID = vListID - 1    
            
        vList.remove(vListID)
        bpy.context.scene.vtFileVersionCollection_ID = newID
        
        
        return {'FINISHED'}

class VTOOLS_OP_reloadVersions(bpy.types.Operator):
    bl_idname = "vtools.reloadversions"
    bl_label = "Reload Versions"
    bl_description = "Reload existings versions from versions folder"
    
    def execute(self, context):
        
        baseDir = os.path.dirname(bpy.data.filepath)
        baseName= os.path.basename(bpy.data.filepath)
        fileName = os.path.splitext(baseName)[0]
        versionFolderName =  "" #_globalVersionFolder
        version = getVersion(fileName)
        
        #IF NO VERSION SUBFIX, FIND THE VERSION FOLDER
        if version == "NONE":
            versionFolderName = os.path.join(_globalVersionFolder, "versions_" + fileName)
            versionFolderName = os.path.join(baseDir, versionFolderName)
            

        #GET ALL FILES IN BLENDER VERSION
        if os.path.exists(versionFolderName):
            filesToSearch = os.path.join(versionFolderName, "*.blend")
            if len(filesToSearch) > 0:
                blendFiles = sorted(glob.glob(filesToSearch))

                if len(blendFiles) > 0:
                    i = 0
                    for i in range(0,len(blendFiles)):
                        f = blendFiles[i]
                        version = getVersion(os.path.splitext(os.path.basename(f))[0])
                        position = int(version) - 1
                        
                        vList =  bpy.context.scene.vtFileVersionCollection
                        vListID =  bpy.context.scene.vtFileVersionCollection_ID
                        
                        #LOOK FOR AN EXISTING VERSION
                        found = False
                        foundCont = 0
                        for vItem in vList:
                            if vItem.fileVersion == version:
                                found = True
                                break
                            foundCont += 1
                        
                       #print("VERSION ", version, "int ", position, "Found ", found) 
                        
                        #IF NOT FOUND ADD TO LIST IN FIRST POSITION
                        if found == False:
                            addVersionToList(f, "")
                            #vList.move(i,0)
                        else:
                            #IF FOUND MOVE TO CORRECT POSITION
                            vList.move(foundCont,0)
                        i += 1
        return {'FINISHED'}
    

class VTOOLS_OP_openVersionFolder(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    bl_idname = "vtools.openversionfolder" 
    bl_label = "Open Version Folder"
    bl_label = "Open File Version Folder"
    bl_description = "Open version folder"
    filename_ext = ""

    def execute(self, context):
        return {'FINISHED'}

# -- ui --------#




#-- DEF CALLBACKS ---#

"""    
def cb_selectPaintingLayer(self,value):
    
    return None

"""


# --- VERSIONS LAYER TREE --- #

class VTOOLS_UL_fileVersions(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        
        row = layout.row(align=True)
        row.label(text=item.fileVersion)
        row.label(text=item.info)
        
        
    def filter_items(self, context, data, propname):        
        collec = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list
        flt_flags = []
        flt_neworder = []
        if self.filter_name:
            flt_flags = helper_funcs.filter_items_by_name(self.filter_name, self.bitflag_filter_item, collec, "info",
                                                          reverse=self.use_filter_sort_reverse)
        return flt_flags, flt_neworder


        
class VTOOLS_CC_fileVersionsCollection(bpy.types.PropertyGroup):
       
    fileVersion : bpy.props.StringProperty(default='')
    fileName : bpy.props.StringProperty(default='')
    filePath : bpy.props.StringProperty(default='')
    info: bpy.props.StringProperty(default='')



# -------- PANEL ----------------#

class VTOOLS_PT_fileVersions(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Blender Versions"
    bl_category = 'View'
    #bl_options = {'HIDE_HEADER'} 
    
        
    @classmethod
    def poll(cls, context):
        return (context.object)
    
    def draw(self,context):
        layout = self.layout
        
        
        row = layout.row()
        row.template_list('VTOOLS_UL_fileVersions', "Versions ", context.scene, "vtFileVersionCollection", context.scene, "vtFileVersionCollection_ID", rows=4)
        
        col = row.column(align=True)
        col.operator(VTOOLS_OP_loadVersion.bl_idname, text="", icon="LOOP_BACK")
        col.operator(VTOOLS_OP_removeVersion.bl_idname, text="", icon="REMOVE")
        col.operator(VTOOLS_OP_reloadVersions.bl_idname, text="", icon="FILE_REFRESH")
        

        versionItem = getSelectedVersion()
        if versionItem != None:
            
            #box.label(text=versionItem.filePath)
            col.operator_context = "INVOKE_DEFAULT"
            op = col.operator(VTOOLS_OP_openVersionFolder.bl_idname, text="", icon="FILE_FOLDER")
            op.filepath = versionItem.filePath
                
            if versionItem.info != "":

                box = layout.box()
                
                #GET REGION WIDTH
                regionWidth = context.region.width / 7
                wrapper = textwrap.TextWrapper(width = regionWidth)
                wText = wrapper.wrap(text=versionItem.info)
            
                col = box.column(align=True)
                for line in wText:
                    col.label(text=line)
                    
            #EDIT VERSION INFO    
            col = layout.column(align=True)
            col.label(text="Edit Version Info")
            col.prop(versionItem, "info", text="")

# -- REGISTER --------#


def addShortcut():
    
    # replace ctrl+s to this save incremental
    # inactive
    
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.active
    km = kc.keymaps.find("Window")
    
    saveShortcut = km.keymap_items.find("wm.save_mainfile")
    
    cont = 0
    while cont < 10:
        saveShortcut = km.keymap_items.find("wm.save_mainfile")
        if saveShortcut != -1:
            shortCut = km.keymap_items[saveShortcut]
            if shortCut.type == "S":
                km.keymap_items.remove(km.keymap_items[saveShortcut])
                break
        cont = cont + 1
    
    kmi = km.keymap_items.new(VTOOLS_OP_saveIncremental.bl_idname,'S','PRESS', any=False, shift=False, ctrl=True, alt=False, oskey=False, key_modifier='NONE')
    


def menu_draw(self, context):
    self.layout.separator()
    self.layout.operator_context="INVOKE_DEFAULT"
    self.layout.operator(VTOOLS_OP_saveIncremental.bl_idname, text=VTOOLS_OP_saveIncremental.bl_label, icon='ADD')
    
def register():
    bpy.utils.register_class(VTOOLS_OP_saveIncremental)
    bpy.types.TOPBAR_MT_file.append(menu_draw)
    
    bpy.utils.register_class(VTOOLS_PT_fileVersions)
    bpy.utils.register_class(VTOOLS_UL_fileVersions)
    bpy.utils.register_class(VTOOLS_CC_fileVersionsCollection)
    bpy.utils.register_class(VTOOLS_OP_loadVersion)
    bpy.utils.register_class(VTOOLS_OP_removeVersion)
    bpy.utils.register_class(VTOOLS_OP_reloadVersions)
    bpy.utils.register_class(VTOOLS_OP_openVersionFolder)
    
    bpy.types.Scene.vtFileVersionCollection = bpy.props.CollectionProperty(type=VTOOLS_CC_fileVersionsCollection)
    bpy.types.Scene.vtFileVersionCollection_ID = bpy.props.IntProperty(default = -1)
 
    #addShortcut()
   
def unregister():
    bpy.utils.unregister_class(VTOOLS_OP_saveIncremental)
    bpy.types.TOPBAR_MT_file.remove(menu_draw)
    
    bpy.utils.unregister_class(VTOOLS_PT_fileVersions)
    bpy.utils.unregister_class(VTOOLS_UL_fileVersions)
    bpy.utils.unregister_class(VTOOLS_CC_fileVersionsCollection)
    bpy.utils.unregister_class(VTOOLS_OP_loadVersion)
    bpy.utils.unregister_class(VTOOLS_OP_removeVersion)
    bpy.utils.register_class(VTOOLS_OP_reloadVersions)
    bpy.utils.register_class(VTOOLS_OP_openVersionFolder)
    
    del bpy.types.Scene.vtFileVersionCollection
    del bpy.types.Scene.vtFileVersionCollection_ID

if __name__ == "__main__":
    register()