import bpy
import sys
from os import path
from bpy.app.handlers import persistent
from bpy.types import PropertyGroup, Operator, Panel


# Modules Import
dir = path.dirname(path.realpath(__file__))
print ("Addon Launched at", dir)

if dir not in sys.path:
    sys.path.append(dir)

from animTools import exportAnim
from animTools import animPipeline
from animTools import apUtilities

# Add-on Informations
bl_info = {
   "name": "Kouji Animation Tools",
   "author": "Spooklight Studio",
   "version": (2, 4, 0),
   "blender": (2, 79, 0),
   "location": "",
   "description": "Tools to manage and export Kouji's animations",
   "warning": "",
   "wiki_url": "",
   "tracker_url": "",
   "category": "Animation"}


#  InFile Settings
class apActSettings(PropertyGroup):
    '''
    every action will be constructed with apActSettings collection

    Animation Pipeline Data Architecture:
    Action
    .animPipeline (Animation Pipeline //Property Group)
    ..ap_rig_version     (Float)
    ..ap_prop_n          (string)
    '''
    ap_rig_version = bpy.props.FloatProperty(name="rig version", default=0.0)
    ap_prop_1 = bpy.props.StringProperty(name="Prop 1", default="")
    ap_prop_2 = bpy.props.StringProperty(name="Prop 2", default="")
    ap_prop_3 = bpy.props.StringProperty(name="Prop 3", default="")
    ap_prop_4 = bpy.props.StringProperty(name="Prop 4", default="")


class apSettings(PropertyGroup):
    '''
    every object will be constructed with apSettings collection

    Animation Pipeline Data Architecture:
    Object
    .animPipeline (Animation Pipeline //Property Group)
    ..ap_seed     (seed // bool)
    ..ap_prop  (prop // bool)
    ..ap_leaf     (leaf // bool)
    ..ap_catcher  (catcher // bool)
    ..ap_export_path (export path //string / path)
    '''
    ap_seed = bpy.props.BoolProperty(name="seed", default=False)
    ap_prop = bpy.props.BoolProperty(name="prop", default=False)
    ap_leaf = bpy.props.BoolProperty(name="leaf", default=False)
    ap_catcher = bpy.props.BoolProperty(name="catcher", default=False)
    ap_export_path = bpy.props.StringProperty(name="export path", subtype="FILE_PATH", default="C:/tmp/")
    ap_rig_version = bpy.props.FloatProperty(name="rig version", default=0.0)


# Handlers
@persistent
def updateFramesHandler(dummy):
    '''
    If a seed is selected and its action is changed
    Update the scene frame range
    Update the visibility of the props
    '''

    # print ("handler active")
    global oldAct

    try:
        oldAct
    except:
        oldAct = None

    # Analyze context
    source = bpy.context.object
    if hasattr(source, "animPipeline"):
        isSeed = source.animPipeline.ap_seed
    else:
        isSeed = False

    # If active obj is a seed and its action has changed
    if isSeed:
        curAct = source.animation_data.action

        if curAct != oldAct:

            # Update frame range
            exportAnim.updateFrames(exportAnim, source)
            # Update Props visibility
            animPipeline.ap_prepare_props_for_action(animPipeline(), curAct)

            oldAct = curAct


# Operators
class ap_Init_Seed (Operator, animPipeline):
    '''
    initialize the object as a Seed
    '''

    bl_idname = "ap.initseed"
    bl_label = "ap initialize as seed"

    def execute(self, context):
        self.ap_init("seed")
        return {'FINISHED'}


class ap_Init_Prop (Operator, animPipeline):
    '''
    initialize the object as a Prop
    '''

    bl_idname = "ap.initprop"
    bl_label = "ap initialize as prop"

    @classmethod
    def poll(cls, context):
        return len(animPipeline.ap_collect_seed(animPipeline)) > 0

    def execute(self, context):
        self.ap_init("prop")
        self.ap_prop_ready_for_action()
        return {'FINISHED'}


class ap_Init_Leaf (Operator, animPipeline):
    '''
    initialize the object as a Leaf
    '''

    bl_idname = "ap.initleaf"
    bl_label = "ap initialize as leaf"

    def execute(self, context):
        self.ap_init("leaf")
        return {'FINISHED'}


class ap_Init_Catcher (Operator, animPipeline):
    '''
    initialize the object as a Catcher
    '''

    bl_idname = "ap.initcatcher"
    bl_label = "ap initialize as catcher"

    def execute(self, context):
        self.ap_init("catcher")
        return {'FINISHED'}


class ap_Uninit (Operator, animPipeline):
    '''
    uninitialize the object
    '''

    bl_idname = "ap.uninit"
    bl_label = "ap uninitialize"

    def execute(self, context):
        self.ap_uninit()
        return {'FINISHED'}


class ap_Update_Rig_Version (Operator, animPipeline):
    '''
    Update rig version
    '''

    bl_idname = "ap.updaterigversion"
    bl_label = "ap update rig version"

    def execute(self, context):
        self.ap_update_rig_version()
        return {'FINISHED'}


class ap_Keep_One_Action (Operator, animPipeline):
    '''
    Delete all actions
    except the one currently selected
    '''

    bl_idname = "ap.keeponeaction"
    bl_label = "ap keep one action"

    def execute(self, context):
        self.ap_keep_one_action()
        return {'FINISHED'}


class ap_Link_Prop(Operator, animPipeline, apUtilities):
    '''
    Link the current prop to the current action
    '''

    bl_idname = "ap.linkprop"
    bl_label = "ap link prop to current action"

    @classmethod
    def poll(cls, context):
        # Enable only if the seed has an action
        try:
            seed = animPipeline.ap_collect_seed(animPipeline)
            if seed[0].animation_data.action is None:
                return False
            else:
                return True
        except:
            return False

    def execute(self, context):

        prop = bpy.context.active_object
        seed = self.ap_collect_seed()[0]
        curAct = seed.animation_data.action

        # Write the prop's name in the first free line
        # of the seed's properties
        for i in range(5):

            # No more empty field to write to
            if i == 4:
                self.report({'WARNING'}, "No more place for another prop!")
                return{'CANCELLED'}

            # set wich target property to write to for each loop
            lineProp = "ap_prop_" + str(i+1)

            # Check if prop name is already written
            if curAct.animPipeline.get(lineProp) == prop.name:
                self.report({'WARNING'}, "%s is already linked to %s" % (prop.name, curAct.name))
                return{'CANCELLED'}

            # If field empty, write on it
            if curAct.animPipeline.get(lineProp) == '' or curAct.animPipeline.get(lineProp) is None:
                curAct.animPipeline[lineProp] = prop.name
                return{'CANCELLED'}

        # Write children as props
        for child in self.getChildren(prop):
            self.ap_target = child.name
            self.ap_init("prop")

        return{'FINISHED'}


class ap_Unlink_Prop(Operator):
    '''
    Unlink the prop number #n from the current action
    Reorganize the prop list without empty spaces
    '''
    bl_idname = "ap.unlinkprop"
    bl_label = "ap unlink prop from current action"

    prop_target = bpy.props.FloatProperty(default=1)

    def execute(self, context):
        act = bpy.context.object.animation_data.action

        props = []

        for i in range(4):

            # Skip the target prop, it will be deleted
            if i == self.prop_target:
                continue

            lineIn = "ap_prop_" + str(i+1)
            inContent = act.animPipeline.get(lineIn)

            # Create a sorted array with only non empty data
            if inContent is not None or inContent != "":
                props.append(inContent)

        for i in range(4):
            lineOut = "ap_prop_" + str(i+1)

            # Avoid pointer error
            if i < len(props):
                act.animPipeline[lineOut] = props[i]
            else:
                act.animPipeline[lineOut] = None

        return{'FINISHED'}


class ap_Merge_Actions (Operator, animPipeline):
    '''
    Merge selected prop actions to seed's current action
    '''

    bl_idname = "ap.mergeactions"
    bl_label = "ap merge actions"

    @classmethod
    def poll(cls, context):
        # Enable only if the prop and the seed has both an action
        obj = bpy.context.object

        try:
            if obj.animation_data.action is None:
                return False
            else:
                seed = animPipeline.ap_collect_seed(animPipeline)
                if seed[0].animation_data.action is None:
                    return False
                else:
                    return True
        except:
            return False

    def execute(self, context):
        sourceAct = bpy.context.object.animation_data.action
        targetAct = self.ap_collect_seed()[0].animation_data.action

        if sourceAct != targetAct:
            self.ap_merge_actions(sourceAct, targetAct, True)
        else:
            self.report({'WARNING'}, "source and target actions are identical")
            return {'CANCELLED'}

        return {'FINISHED'}


class exportCurAction(animPipeline, exportAnim):
    '''
    Export the current action to an fbx file
    '''

    bl_idname = "ap.exportaction"
    bl_label = "ap export action"

    @classmethod
    def poll(cls, context):

        # Check if filepath is valid abd is there is a seed
        filepath = bpy.context.object.animPipeline.ap_export_path
        return path.exists(filepath) and len(animPipeline.ap_collect_seed(animPipeline)) > 0

    def execute(self, context):

        # Update Variables
        self.source = self.ap_collect_seed()
        self.target = self.ap_collect_catcher()
        self.exportObjects = self.ap_collect_catcher() + self.ap_collect_leaf()

        # Check if the current file is a library
        isLib = "AutoLink.py" in bpy.data.texts

        # Get export path from seed's action
        seed = self.source[0]
        action = seed.animation_data.action
        path = self.ap_get_export_path()
        self.filepath = path + action.name + ".fbx"

        # Add props to the export
        self.ap_prepare_props_for_action(action)
        props = self.ap_collect_prop_for_action(action, True)

        if isLib:
            propsNamespace = self.ap_remove_namespace(props, "::")

        self.exportObjects += props

        # Export Process
        self.bakeAnim()
        self.exportAnim()
        self.cleanScene()

        # Restore namespaces in props Names
        if isLib:
            self.ap_restore_namespace(propsNamespace)

        return {'FINISHED'}


class exportAllActions(exportAnim, animPipeline, Operator):
    '''
    Export the all the actions to their own fbx files
    '''

    bl_idname = "ap.exportallactions"
    bl_label = "ap export all actions"

    @classmethod
    def poll(cls, context):

        # Check if filepath is valid abd is there is a seed
        filepath = bpy.context.object.animPipeline.ap_export_path
        return path.exists(filepath) and len(animPipeline.ap_collect_seed(animPipeline)) > 0

    def execute(self, context):
        # Update class variables
        self.source = self.ap_collect_seed()
        self.target = self.ap_collect_catcher()

        # Check if the current file is a library
        isLib = "AutoLink.py" in bpy.data.texts

        # Prepare export path (without reccursive file name)
        seed = self.source[0]
        path = self.ap_get_export_path()

        # Stock every action in an array:
        actions = bpy.data.actions

        # Initialize counter
        i = 0

        # Repeat for each action:
        for action in actions:
            # Increment
            i += 1

            # set current action
            seed.animation_data.action = action
            print("Exporting Action", i, "/", len(actions), ":", seed.animation_data.action.name)

            # Get export path from catcher and file name from seed's action
            self.filepath = path + action.name + ".fbx"

            # Objects to export:
            self.exportObjects = self.ap_collect_catcher() + self.ap_collect_leaf()

            # Add props to the export
            self.ap_prepare_props_for_action(action)
            props = self.ap_collect_prop_for_action(action, True)
            self.exportObjects += props

            if isLib:
                propsNamespace = self.ap_remove_namespace(props, "::")

            # export
            self.bakeAnim()
            self.exportAnim()
            self.cleanScene()

            # Restore namespaces in props Names
            if isLib:
                self.ap_restore_namespace(propsNamespace)

            # Reset seed Constraints
            self.resetConstraints(seed)

        return {'FINISHED'}


# UI
class AnimationPanel(Panel, animPipeline):
    bl_label = "Animation Pipeline"
    bl_space_type = "VIEW_3D"
    bl_category = "Spooklight"
    bl_region_type = "TOOLS"

    @classmethod
    def poll(self, context):
        if context.object is not None:
            if context.object.mode == 'OBJECT' and context.object.type in {'MESH', 'ARMATURE'}:
                return True

    def draw(self, context):

        obj = context.object
        anim = obj.animation_data
        ap_settings = bpy.context.active_object.animPipeline

        # SUBSCRIPTION
        if not (ap_settings.ap_seed or ap_settings.ap_prop or ap_settings.ap_leaf or ap_settings.ap_catcher):
            layout = self.layout
            label = layout.label('Initialisation')
            row = layout.row()
            seed_button = row.operator("ap.initseed", text="initialize as seed").ap_target = bpy.context.active_object.name
            row = self.layout.row()
            prop_button = row.operator("ap.initprop", text="initialize as prop").ap_target = bpy.context.object.name
            row = self.layout.row()
            leaf_button = row.operator("ap.initleaf", text="initialize as leaf").ap_target = bpy.context.active_object.name
            row = self.layout.row()
            catcher_button = row.operator("ap.initcatcher", text="initialize as catcher").ap_target = bpy.context.active_object.name
        else:
            layout = self.layout
            label = layout.label('Unsubscribe')
            row = layout.row()
            uninit_button = row.operator("ap.uninit", text="uninitialize").ap_target = bpy.context.active_object.name

        # SEED and animation management
        if ap_settings.ap_seed:
            layout = self.layout
            label = layout.label("Initialized as a Seed")

            # Animation
            box = layout.box()
            box.label("Animation :")
            row = box.row()
            row.prop(obj.animation_data, "action")
            row = box.row()
            row.operator("ap.keeponeaction", text="Keep this action only")

            # Props
            box = layout.box()
            box.label("Props Linked :")

            if anim.action is not None:
                for i in range(4):
                    row = box.row()
                    prop = bpy.context.object.animation_data.action.animPipeline.get("ap_prop_"+str(i+1))
                    if prop == "" or prop is None:
                        break
                    label = row.label(prop)
                    row.operator("ap.unlinkprop", text="", icon="ZOOMOUT", emboss=False).prop_target = i

            # Version
            box = layout.box()
            box.label("Version: " + str(round(ap_settings.ap_rig_version, 1)))
            if anim.action is not None:
                row = box.row()
                row.prop(anim.action.animPipeline, "ap_rig_version")
                version_button = row.operator("ap.updaterigversion", text="Update version")

        # PROP
        elif ap_settings.ap_prop:
            layout = self.layout
            label = layout.label('Initialized as a Prop')
            box = layout.box()

            # Constraint
            const = obj.constraints['Prop_Link']
            row = box.row()
            row.prop(const, "mute")
            row = box.row()
            row.prop_search(const, "subtarget", const.target.data, "bones", text="Bone")

            # Link to Action
            row = box.row()
            row.operator("ap.linkprop", text="Link to the Current action")

            # Merge Actions
            row = box.row()
            row.operator("ap.mergeactions", text="Merge action to seed")

        # LEAF
        elif ap_settings.ap_leaf:
            layout = self.layout
            label = layout.label('Initialized as a Leaf')

        # CATCHER and export
        elif ap_settings.ap_catcher:
            layout = self.layout
            label = layout.label('Initialized as a Catcher')
            box = layout.box()
            box.label('Export')
            row = box.row()
            row.operator("ap.exportaction", text="export current action")
            row.operator("ap.exportallactions", text="export all actions")
            box.prop(obj.animPipeline, "ap_export_path")


def register():
    bpy.utils.register_class(apSettings)
    bpy.utils.register_class(apActSettings)
    bpy.utils.register_class(ap_Init_Seed)
    bpy.utils.register_class(ap_Init_Prop)
    bpy.utils.register_class(ap_Init_Leaf)
    bpy.utils.register_class(ap_Init_Catcher)
    bpy.utils.register_class(ap_Uninit)
    bpy.utils.register_class(ap_Update_Rig_Version)
    bpy.utils.register_class(ap_Keep_One_Action)
    bpy.utils.register_class(ap_Link_Prop)
    bpy.utils.register_class(ap_Unlink_Prop)
    bpy.utils.register_class(ap_Merge_Actions)
    bpy.utils.register_class(exportCurAction)
    bpy.utils.register_class(exportAllActions)
    bpy.utils.register_class(AnimationPanel)

    # Register properties when addon registred
    bpy.types.Object.animPipeline = bpy.props.PointerProperty(name='Animation Pipeline', type=apSettings)
    bpy.types.Action.animPipeline = bpy.props.PointerProperty(name='Animation Pipeline', type=apActSettings)

    # Handler Registration
    bpy.app.handlers.frame_change_pre.clear()
    bpy.app.handlers.frame_change_pre.append(updateFramesHandler)


def unregister():
    bpy.utils.unregister_class(apSettings)
    bpy.utils.unregister_class(apActSettings)
    bpy.utils.unregister_class(ap_Init_Seed)
    bpy.utils.unregister_class(ap_Init_Prop)
    bpy.utils.unregister_class(ap_Init_Leaf)
    bpy.utils.unregister_class(ap_Init_Catcher)
    bpy.utils.unregister_class(ap_Uninit)
    bpy.utils.unregister_class(ap_Update_Rig_Version)
    bpy.utils.unregister_class(ap_Keep_One_Action)
    bpy.utils.unregister_class(ap_Link_Prop)
    bpy.utils.unregister_class(ap_Unlink_Prop)
    bpy.utils.unregister_class(ap_Merge_Actions)
    bpy.utils.unregister_class(exportCurAction)
    bpy.utils.unregister_class(exportAllActions)
    bpy.utils.unregister_class(AnimationPanel)

    # Handler Remove
    bpy.app.handlers.scene_update_pre.clear()

if __name__ == "__main__":
    register()
