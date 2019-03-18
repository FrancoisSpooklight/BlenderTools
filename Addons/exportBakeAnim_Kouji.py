######## A CLEANER ########

import bpy
from bpy import *

#### Class
class exportAnim(bpy.types.Operator):
    """ToolTip"""
    bl_idname = "wm.exportanim"
    bl_label = "SPOOKY - Export Anim"


    ### Variables
    source = bpy.props.EnumProperty(items= ())
    target = bpy.props.EnumProperty(items= ())
    exportObjects = bpy.props.EnumProperty(items= ())
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    #### Fonctions internes    
    
    def bakeAnim(self,target,source):
   
        # Stoquer les actions sources sélectionnées
        curActName = source.animation_data.action.name
        curActFrames = source.animation_data.action.frame_range #Vector2
        
        bpy.context.scene.frame_start = curActFrames[0]
        bpy.context.scene.frame_end = curActFrames[1]
        
#        # Selectionner uniquement le catcher !!!!
#        source.select = False # checker l'utilité
#        target.select = True # checker l'utilité

#        # copier la scene et la renommer
#        ops.scene.new(type='FULL_COPY')
#        context.scene.name = "BAKING"

#        # Cherche les armatures semblable à target et source dans la nouvelle scene et le Renomment selon l'originale
#        for obj in bpy.context.scene.objects: 
#            if target.name in obj.name:
#                obj.name = target.name

#        # Renommer l'action en __copy
#        for act in data.actions:
#            if curActName in act.name and not curActName == act.name:
#                act.name = curActName + "__COPY"

#        #Créer un nouvelle action pour le bake:
#        bakeAct = data.actions.new(curActName + "__BAKE" )
#        target.animation_data.action = bakeAct #Apply
#        
#        
#        ### Set Catcher as active object for BAKING !!!!
#        #bpy.context.scene.objects.active = target !!!!
#       
#        print ("::::::::::::::::::::::::::::::::::::::::::::",bpy.context.active_object) # !!!!
#         
#        ### BakeAction
#        ops.nla.bake(
#            frame_start = curActFrames[0],
#            frame_end = curActFrames[1] + 1,
#            only_selected = False,
#            visual_keying = True,
#            clear_constraints = True,
#            use_current_action = True,
#            bake_types = {'POSE'})
#            
#               
#        print("Bake DONE")
    
    #### Exporte l'animation dans le chemin spécifié
    ###  ARG: objets à exporter / filepath
    def exportAnim(self,selection,filepath,DAE):
        
        print ("export",selection,"at",filepath)

        #### MESH EXPORT DOESN'T WORK !!!        
        for obj in data.objects:
            if obj in selection:
                print ("exported",obj.name)
                obj.select = True

        if DAE == False:
            #export FBX
            bpy.ops.export_scene.fbx(
                filepath = filepath,
                check_existing = True,
                use_selection = True,
                use_mesh_modifiers = False,
                use_anim = True,
                use_anim_action_all = False,
                use_anim_optimize = True, ##!
                bake_anim_use_all_actions = False,
                bake_anim_use_nla_strips = False,
                global_scale = 1.0,
                axis_forward = '-Z',
                axis_up = 'Y',
                object_types = {'ARMATURE', 'MESH'})

        else:
            #Supprimmer les anims sur le root
            #tourner de 90°

            #export dae
            bpy.ops.wm.collada_export(
                filepath = filepath,
                check_existing=False,
                apply_modifiers = False,
                export_mesh_type = 0,
                export_mesh_type_selection = 'view',
                selected = True,
                include_children=False,
                include_armatures=False,
                include_shapekeys=False,
                deform_bones_only=False,
                active_uv_only=False,
                include_uv_textures=False,
                include_material_textures=False,
                use_texture_copies=False,
                triangulate=False,
                use_object_instantiation=True,
                use_blender_profile=True,
                sort_by_name=False,
                export_transformation_type=0,
                export_transformation_type_selection='matrix')


        print("export DONE")
    
    #### Nettoie la scène et la rétablie dans son été d'avant export
    def cleanScene(self,target):

        # Supprimer la scene
        bpy.ops.scene.delete()
                
              
        # Purge tous les orphelins
        for obj in data.objects:
            if obj.users == 0:
                data.objects.remove(obj)
        for act in data.actions:
            if act.users == 0:
                data.actions.remove(act)
        for arm in data.armatures:
            if arm.users == 0:
                data.armatures.remove(arm)
        for mesh in data.meshes:
            if mesh.users == 0:
                data.meshes.remove(mesh)
        for lamp in data.lamps:
            if lamp.users == 0:
                data.lamps.remove(lamp)
        for mat in data.materials:
            if mat.users == 0:
                data.materials.remove(mat)
        for tex in data.textures:
            if tex.users == 0:
                data.textures.remove(tex)
        for world in data.worlds:
            if world.users == 0:
                data.worlds.remove(world)
        for camera in data.cameras:
            if camera.users == 0:
                data.cameras.remove(camera)
        for linestyle in data.linestyles:
            if linestyle.users ==0:
                data.linestyles.remove(linestyle)

        # Renommer l'armature originale
        if "rig_catcher.001" in context.scene.objects:
            bpy.context.scene.objects["rig_catcher.001"].name = "rig_catcher"
            
        # Purge l'action du ou des catchers
        target.animation_data.action = None
        
        
        # Purge les actions résiduelles
        for act in data.actions:
            if "_BAKE" in act.name or "_COPY" in act.name:
                act.use_fake_user = False
                act.user_clear()
                bpy.data.actions.remove(act)
                
        
            
        print("Clean DONE")



#class exportAnimOp(exportAnim):
#    """ToolTip"""
#    bl_idname = "wm.exportanimop"
#    bl_label = "SPOOKY - Export Anim Operator"

#    ### Variables
#    source = [context.selected_objects[0]]
#    target = [context.object]
#    exportObjects = context.selected_objects
#    filepath = bpy.props.StringProperty(subtype="FILE_PATH")


#    @classmethod
#    def poll(cls, context):
#        return source.animation_data.actio is not None

#    def execute(self, context):
#        self.bakeAnim(self.target,self.source)
#        self.exportAnim(self.filepath)
#        self.cleanScene()
#        return {'FINISHED'}

#    def invoke(self, context, event):
#        context.window_manager.fileselect_add(self)
#        return {'RUNNING_MODAL'}



#### Registration
# Register and add to the file selector

def register():
    bpy.utils.register_class(exportAnim) 
    #bpy.utils.register_class(exportAnimOp)  
    
def unregister():
    bpy.utils.register_class(exportAnim) 
    #bpy.utils.unregister_class(exportAnimOp)  

if __name__ == "__main__":
    register()

# test call
#bpy.ops.wm.exportanim('INVOKE_DEFAULT')