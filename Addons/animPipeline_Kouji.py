'''
Created on 19 sept. 2016

@author: Francois Spooklight

seed: armature originale
branch : armatures controlé par la seed (exemple: visage)
leaf: mesh liés aux differentes armatures
catcher : armature sur laquelle l'animation est backée

'''

import bpy
from exportBakeAnim import exportAnim



### Setup Animation Settings Property Group
### La collection apSettings est attribuée à tous les objects

### Animation Pipeline Data Architecture:
### Object
### .animPipeline (Animation Pipeline //Property Group)
### ..ap_seed     (seed // bool)
### ..ap_branch   (branch // bool)
### ..ap_leaf     (leaf // bool)
### ..ap_catcher  (catcher // bool)
### ..ap_export_path (export path //string / path)

class apSettings(bpy.types.PropertyGroup):
    ap_seed = bpy.props.BoolProperty(name="seed",default=False)
    ap_branch = bpy.props.BoolProperty(name="branch",default=False)
    ap_leaf = bpy.props.BoolProperty(name="leaf",default=False)
    ap_catcher = bpy.props.BoolProperty(name="catcher",default=False)
    ap_export_path = bpy.props.StringProperty(name="export path",subtype="FILE_PATH",default="C:/tmp/")


### Main Class
### Classe contenant les définitions des methodes de l'animation pipeline
class animPipeline:
    
    ap_target = bpy.props.StringProperty()


    # Initialisation d'un object en tant que seed/branch/leaf
    def ap_init(self,type):
        
        #print("ap_init",self.ap_target,"as",type)
        obj = bpy.data.objects[self.ap_target]
        
        #activation of the selected type
        if type == "seed":
            obj.animPipeline.ap_seed = True
        elif type == "branch":
            obj.animPipeline.ap_branch = True
        elif type == "leaf":
            obj.animPipeline.ap_leaf = True
        else:
            obj.animPipeline.ap_catcher = True
            
    # Desinscription et remise à zero d'un objet.
    def ap_uninit(self):
        
        #print("ap_init",self.ap_target,"as",type)
        obj = bpy.data.objects[self.ap_target]
        
        obj.animPipeline.ap_seed = False
        obj.animPipeline.ap_branch = False
        obj.animPipeline.ap_leaf = False
        obj.animPipeline.ap_catcher = False
    
    # renvoie un array des objets seed de la scène    
    def ap_collect_seed(self):
        
        seeds = []
        objs = bpy.context.scene.objects
        
        for obj in objs:
            if obj.animPipeline.ap_seed:
                seeds.append(obj)
                
        #print (seeds)
        return seeds
    
    # renvoie un array des objets branch de la scène    
    def ap_collect_branch(self):
        
        branches = []
        objs = bpy.context.scene.objects
        
        for obj in objs:
            if obj.animPipeline.ap_branch:
                branches.append(obj)
                
        #print (branches)
        return branches
    
    # renvoie un array des objets leaf de la scène    
    def ap_collect_leaf(self):
        
        leafs = []
        objs = bpy.context.scene.objects
        
        for obj in objs:
            if obj.animPipeline.ap_leaf:
                leafs.append(obj)
                
        #print (leafs)
        return leafs
    
    # renvoie un array des objets catcher de la scène    
    def ap_collect_catcher(self):
        
        catchers = []
        objs = bpy.context.scene.objects
        
        for obj in objs:
            if obj.animPipeline.ap_catcher:
                catchers.append(obj)
        
        return catchers
                
    # renvoie l'export path stoqué dans le catcher   
    def ap_get_export_path(self):
        
        catcher= (self.ap_collect_catcher())[0]
        export_path = catcher.animPipeline.ap_export_path
                
        return export_path
    
    # Répercute l'animation du seed sur toutes les branches
    def ap_update_action(self):
        
        seed = (self.ap_collect_seed())[0]
        branches = self.ap_collect_branch()
        
        for branch in branches:
            branch.animation_data.action = seed.animation_data.action


### Operators
### Operators dérivés de la main class

# OPERATOR / Identifie l'objet comme une seed
class ap_Init_Seed (bpy.types.Operator,animPipeline):
    bl_idname = "ap.initseed"
    bl_label = "ap initialize as seed"
        
    def execute(self, context):
        self.ap_init("seed")
        return {'FINISHED'}
    
# OPERATOR / Identifie l'objet comme une branch
class ap_Init_Branch (bpy.types.Operator, animPipeline):
    bl_idname = "ap.initbranch"
    bl_label = "ap initialize as branch"
    
    
    def execute(self, context):
        self.ap_init("branch")
        return {'FINISHED'}
    
# OPERATOR / Identifie l'objet comme une leaf
class ap_Init_Leaf (bpy.types.Operator, animPipeline):
    bl_idname = "ap.initleaf"
    bl_label = "ap initialize as leaf"
     
    def execute(self, context):
        self.ap_init("leaf")
        return {'FINISHED'}
    
# OPERATOR / Identifie l'objet comme un catcher
class ap_Init_Catcher (bpy.types.Operator, animPipeline):
    bl_idname = "ap.initcatcher"
    bl_label = "ap initialize as catcher"
    
    def execute(self, context):
        self.ap_init("catcher")
        return {'FINISHED'}
    
# OPERATOR / Desinscrit l'objet
class ap_Uninit (bpy.types.Operator, animPipeline):
    bl_idname = "ap.uninit"
    bl_label = "ap uninitialize"
    
    def execute(self, context):
        self.ap_uninit()
        return {'FINISHED'}
    
# OPERATOR / Repercute l'action du seed sur ses branchs.
class ap_Update_Actions (bpy.types.Operator, animPipeline):
    bl_idname = "ap.updateaction"
    bl_label = "ap update action"
    
    def execute(self, context):
        self.ap_update_action()
        return {'FINISHED'}


# OPERATOR / Exporte l'action courante // passer en method d'anim pipeline?
class exportCurAction(exportAnim, animPipeline):
    bl_idname = "ap.exportaction"
    bl_label = "ap export action"
    
    def execute(self, context):
        
        # Update class variables        
        self.source = self.ap_collect_seed()
        self.target = self.ap_collect_catcher()
        exportObjects = self.ap_collect_catcher() + self.ap_collect_leaf()
        self.exportObjects = exportObjects
        
        # Get export path from seed #set a method for that)
        seed = self.source[0]
        action = seed.animation_data.action.name
        path = self.ap_get_export_path()
        self.filepath =  path + action + ".fbx"
        
        self.bakeAnim(self.target[0],self.source[0]) #Premier objet de chaque array !!! pas de doublons possibles pour le moment.
        self.exportAnim(self.exportObjects,self.filepath, False)
        self.cleanScene(self.target[0])
        return {'FINISHED'}

# OPERATOR / Exporte toutes les actions // passer en method d'anim pipeline?    
class exportAllActions(exportAnim, animPipeline):
    bl_idname = "ap.exportallactions"
    bl_label = "ap export all actions"
    
    def execute(self, context):
        
        #bpy.ops.wm.console_toggle() #debug Console
        
        # Update class variables      
        self.source = self.ap_collect_seed()
        self.target = self.ap_collect_catcher()
        exportObjects = self.ap_collect_catcher() + self.ap_collect_leaf()
        self.exportObjects = exportObjects

        # Prepare export path (without reccursive file name)
        seed = self.source[0]
        path = self.ap_get_export_path()
                
        #Stock every action in an array:
        actions = bpy.data.actions
        
        #Repète la boucle pour chaque action:
        for act in actions:
            #set current action
            seed.animation_data.action = act
            print("exporting", seed.animation_data.action) #!!!!
            
            # Get export path from catcher and file name from seed's action
            action = seed.animation_data.action.name
            self.filepath =  path + action + ".fbx"
            
            #propagate
            self.ap_update_action()
    
            #export
            self.bakeAnim(self.target[0],self.source[0]) #Premier objet de chaque array !!! pas de doublons possibles pour le moment.
            self.exportAnim(self.exportObjects,self.filepath, False)
            self.cleanScene(self.target[0])
        return {'FINISHED'}



### Interface graphique
###
class AnimationPanel(bpy.types.Panel, animPipeline):
    bl_label = "Animation Pipeline"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    #bl_context = "object"
    
    #Poll Select is not none

    
    @classmethod
    def poll(self,context):
        if context.object.mode == 'OBJECT' and context.object.type in {'MESH','ARMATURE'}:
            return True
    
    def draw(self,context):

        obj = context.object
        anim = obj.animation_data
        
        ap_settings = bpy.context.active_object.animPipeline
        
        if not (ap_settings.ap_seed or ap_settings.ap_branch or ap_settings.ap_leaf or ap_settings.ap_catcher):
            layout = self.layout
            label = layout.label('Initialisation')
            row = layout.row()
            seed_button = row.operator("ap.initseed", text = "initialize as seed").ap_target = bpy.context.active_object.name
            row = self.layout.row()
            branch_button = row.operator("ap.initbranch", text = "initialize as branch").ap_target = bpy.context.object.name
            row = self.layout.row()
            leaf_button = row.operator("ap.initleaf", text = "initialize as leaf").ap_target = bpy.context.active_object.name
            row = self.layout.row()
            catcher_button = row.operator("ap.initcatcher", text = "initialize as catcher").ap_target = bpy.context.active_object.name
        else:
            layout = self.layout
            label = layout.label('Unsubscribe')
            row = layout.row()
            uninit_button = row.operator("ap.uninit", text = "uninitialize").ap_target = bpy.context.active_object.name
            
        if ap_settings.ap_seed:
            layout = self.layout
            label = layout.label("Initialized as a Seed")
            row = layout.row()
            row.prop(obj.animation_data ,"action")
            row.operator("ap.updateaction", text = "expand to branches")
            
                        
        elif ap_settings.ap_branch:
            layout = self.layout
            label = layout.label('Initialized as a Branch')
        elif ap_settings.ap_leaf:
            layout = self.layout
            label = layout.label('Initialized as a Leaf')
        elif ap_settings.ap_catcher:
            layout = self.layout
            label = layout.label('Initialized as a Catcher')
            
            layout.label('Export')
            row = layout.row()
            row.operator("ap.exportaction", text = "export current action")
            row.operator("ap.exportallactions", text = "export all actions")
            layout.prop(obj.animPipeline, "ap_export_path")
            
        

### Enregistrer les classes (a modifier)
def register():
    #bpy.utils.register_module(__name__)
    bpy.utils.register_class(apSettings)
    bpy.utils.register_class(ap_Init_Seed)
    bpy.utils.register_class(ap_Init_Branch)
    bpy.utils.register_class(ap_Init_Leaf)
    bpy.utils.register_class(ap_Init_Catcher)
    bpy.utils.register_class(ap_Uninit)
    bpy.utils.register_class(ap_Update_Actions)
    bpy.utils.register_class(exportCurAction)
    bpy.utils.register_class(exportAllActions)
    bpy.utils.register_class(AnimationPanel)
    
    # Enregistre les propriétés de la pipeline à l'enregistrement
    bpy.types.Object.animPipeline = bpy.props.PointerProperty(name='Animation Pipeline',type=apSettings)
    
def unregister():
    try:
        bpy.utils.unregister_class(apSettings)
        bpy.utils.unregister_class(ap_Init_Seed)
        bpy.utils.unregister_class(ap_Init_Branch)
        bpy.utils.unregister_class(ap_Init_Leaf)
        bpy.utils.unregister_class(ap_Init_Catcher)
        bpy.utils.unregister_class(ap_Uninit)
        bpy.utils.unregister_class(ap_Update_Actions)
        bpy.utils.unregister_class(exportCurAction)
        bpy.utils.unregister_class(exportAllActions)
        bpy.utils.unregister_class(AnimationPanel)
    except:
        pass
    
    
if __name__ == "__main__":
    register()
    