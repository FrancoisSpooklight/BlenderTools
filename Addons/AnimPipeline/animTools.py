# noinspection PyUnresolvedReferences
import bpy
from mathutils import Quaternion
from mathutils import Vector


## A mettre dans un fichier à part
class apUtilities():
    '''
    Generic static methods

    '''

    @staticmethod
    def updateScreen():
        for window in bpy.context.window_manager.windows:
            screen = window.screen

            for area in screen.areas:
                if area.type == 'VIEW_3D':
                    bpy.context.area.tag_redraw()
                    break

    @staticmethod
    def resetArmature(armature):
        '''
        reset every bone of an armature
        '''
        for pbone in armature.pose.bones:
            pbone.rotation_quaternion = Quaternion((0, 0, 0), 0)
            pbone.scale = Vector((1, 1, 1))
            pbone.location = Vector((0, 0, 0))

    @staticmethod
    def muteConstraints(obj, mute):
        '''
        Mute or unmute all bones constraints of a given object
        '''

        for bone in obj.pose.bones:
            for const in bone.constraints:
                const.mute = mute

    @staticmethod
    def getChildren(obj):
        '''
        return an array containing obj's children recursively
        '''

        objIn = [obj]
        objOut = []

        for o in objIn:
            if len(o.children) > 0:
                for child in o.children:
                    objOut.append(child)
                    objIn.append(child)

        return objOut

    @staticmethod
    def remNameSpace(item, separator):
        '''
        Remove a namespace, if existing before the name of the designated item
        '''
        try:
            index = item.name.index(separator) + len(separator)

            item.name = item.name[:index]
        except:
            pass

## Mettre les utilities dans un autre fichier
class exportAnim(bpy.types.Operator, apUtilities):
    '''
    Library for baking and exportations.
    Variables:
        source: source rig
        target: catcher (baked rig)
        exportObjects: list of objects to be exported
        filepath: output path

    '''

    bl_idname = "wm.exportanim"
    bl_label = "SPOOKY - Export Anim"

    # Variables
    #source : bpy.props.EnumProperty(items=())
    #target : bpy.props.EnumProperty(items=())
    #exportObjects : bpy.props.EnumProperty(items=())
    filepath : bpy.props.StringProperty(subtype="FILE_PATH")

    def updateFrames(self, source):
        '''
        Fits the scene frame range to the source's action
        return the frames range
        '''

        curActFrames = source.animation_data.action.frame_range  # Vector2
        bpy.context.scene.frame_start = curActFrames[0] + 1
        bpy.context.scene.frame_end = curActFrames[1]

        print ("Frames range updated to", curActFrames[0], ":", curActFrames[1])

        return (curActFrames)

    @staticmethod
    def resetConstraints(armature):
        '''
        Set all controllers constraints to
        0.0
        exceps list contains Rigify special bones
        prefixes.
        '''

        exceps = ('MCH', 'DEF', 'VIS', 'ORG', 'CNT', 'prop')

        for pbone in armature.pose.bones:
            for ex in exceps:
                if ex in pbone.name:
                    break
            else:
                for const in pbone.constraints:
                    const.influence = 0

    def bakeAnim(self, target, source):
        '''
        Create a dummy scene,
        Bake the source's current action on a
        target's new action.
        '''

        print ("Baking...")

        #target = self.target[0]
        #source = self.source[0]

        # Store the source action
        curActName = source.animation_data.action.name
        curActFrames = self.updateFrames(source)

        # Create a new action for baking
        bakeAct = bpy.data.actions.new(curActName + "__BAKE")
        target.animation_data.action = bakeAct

        # BakeAction
        bpy.ops.nla.bake(
            frame_start=curActFrames[0],
            frame_end=curActFrames[1] + 1,
            only_selected=False,
            visual_keying=True,
            clear_constraints=False,
            use_current_action=True,
            bake_types={'POSE'})

        print("Baking DONE")

    def exportAnim(self, target, exportObjects):
        '''
        Export an fbx of the current selection to
        a specified filepath
        '''

        # print ("Exporting", self.exportObjects, "at", self.filepath)
        print ("Exporting at", self.filepath, "...")

        for obj in exportObjects:
            print ("Object tagged for export:", obj.name)
            # Select object if it is not select_hided
            obj.hide_viewport = False
            obj.hide_select = False
            obj.select_set(True)

        # Unactive target clear_constraints
        self.muteConstraints(target, True)

        #Updating depsgraph
        dg = bpy.context.evaluated_depsgraph_get()
        dg.update()


        # export FBX
        bpy.ops.export_scene.fbx(
            filepath=self.filepath,
            check_existing=False,
            use_selection=True,
            use_mesh_modifiers=False,
            bake_anim=True,
            bake_anim_use_all_bones=True,
            bake_anim_use_nla_strips=False,
            bake_anim_use_all_actions=False,
            bake_anim_force_startend_keying=False,
            bake_anim_step = 1.00,
            bake_anim_simplify_factor = 0.50,
            global_scale=1.0,
            axis_forward='-Z',
            axis_up='Y',
            object_types={'ARMATURE', 'MESH'}
        )

        print("Export DONE")

    def cleanScene(self, target, exportObjects):
        '''
        Clean scene to restore scene's state
        before baking and export
        Clean all remaining orphans data
        '''

        print("Cleaning...")

        # Purge orphans
        for obj in bpy.data.objects:
            if obj.users == 0:
                bpy.data.objects.remove(obj)
        for act in bpy.data.actions:
            if act.users == 0:
                bpy.data.actions.remove(act)
        for arm in bpy.data.armatures:
            if arm.users == 0:
                bpy.data.armatures.remove(arm)
        for mesh in bpy.data.meshes:
            if mesh.users == 0:
                bpy.data.meshes.remove(mesh)
        for lamp in bpy.data.lights:
            if lamp.users == 0:
                bpy.data.lamps.remove(lamp)
        for mat in bpy.data.materials:
            if mat.users == 0:
                bpy.data.materials.remove(mat)
        for tex in bpy.data.textures:
            if tex.users == 0:
                bpy.data.textures.remove(tex)
        for world in bpy.data.worlds:
            if world.users == 0:
                bpy.data.worlds.remove(world)
        for camera in bpy.data.cameras:
            if camera.users == 0:
                bpy.data.cameras.remove(camera)
        for linestyle in bpy.data.linestyles:
            if linestyle.users == 0:
                bpy.data.linestyles.remove(linestyle)

        # Reactivate muted target constraints
        #target = self.target[0]
        self.muteConstraints(target, False)
        self.resetArmature(target)

        # Reset Selectability of meshes
        # for obj in exportObjects:
        #     # print (obj.hide_select, '--->', not obj.hide_select)
        #     obj.select_set(False)
        #     obj.hide_select = not obj.hide_select

        # Empty catcher's action
        target.animation_data.action = None

        # Empty remaining actions // Check utility
        for act in bpy.data.actions:
            if "_BAKE" in act.name or "_COPY" in act.name:

                act.use_fake_user = False
                act.user_clear()
                bpy.data.actions.remove(act)

        print("Clean DONE")


class animPipeline(apUtilities):

    # Variables
    ap_target : bpy.props.StringProperty()

    def ap_init(self, type):
        '''
        Initialisation d'un object en tant que seed/prop/leaf
        '''

        obj = bpy.data.objects[self.ap_target]

        # activation of the selected type
        if type == "seed":
            obj.animPipeline.ap_seed = True
        elif type == "prop":
            obj.animPipeline.ap_prop = True
        elif type == "leaf":
            obj.animPipeline.ap_leaf = True
        else:
            obj.animPipeline.ap_catcher = True

    def ap_uninit(self):
        '''
        Unsubscribe and reset an object
        '''

        obj = bpy.data.objects[self.ap_target]

        # if prop, delete custom constraint
        if obj.animPipeline.ap_prop:
            const = obj.constraints.get('Prop_Link')
            obj.constraints.remove(const)

        obj.animPipeline.ap_seed = False
        obj.animPipeline.ap_prop = False
        obj.animPipeline.ap_leaf = False
        obj.animPipeline.ap_catcher = False

    def ap_collect_seed(self):
        '''
        return an array containing all seeds' objects in the scene
        '''

        print("collect seeds")

        seeds = []
        objs = bpy.context.scene.objects

        for obj in objs:
            if obj.animPipeline.ap_seed:
                seeds.append(obj)

        print("seeds",seeds)

        return seeds

    def ap_collect_prop(self):
        '''
        return an array containing all props objects in the scene
        '''

        props = []
        objs = bpy.context.scene.objects

        for obj in objs:
            if obj.animPipeline.ap_prop:
                props.append(obj)

        return props

    def ap_collect_leaf(self):
        '''
        return an array containing all leafs objects in the scene
        '''

        leafs = []
        objs = bpy.context.scene.objects

        for obj in objs:
            if obj.animPipeline.ap_leaf:
                leafs.append(obj)

        return leafs

    def ap_collect_catcher(self):
        '''
        return an array containing all catchers objects in the scene
        '''

        catchers = []
        objs = bpy.context.scene.objects

        for obj in objs:
            if obj.animPipeline.ap_catcher:
                catchers.append(obj)

        return catchers

    # NEW PROP PIPELINE
    def ap_collect_prop_for_action(self, action, withChildren=False):
        '''
        return an array containing all props linked to an action
        '''

        unsortProps = [None, None, None, None]
        actProps = []

        for i in range(4):
            propName = action.animPipeline.get("ap_prop_"+str(i+1))
            if propName is not None:
                unsortProps[i] = bpy.data.objects.get(propName)

        for prop in unsortProps:
            if prop is not None:
                actProps.append(prop)
                if withChildren:
                    for child in self.getChildren(prop):
                        actProps.append(child)

        return actProps

    def ap_prepare_props_for_action(self, action):
        '''
        hide all props except the ones in the seed's current action
        '''

        # Collect props and their children
        props = []
        propsRoot = self.ap_collect_prop()

        for prop in propsRoot:
            props += self.getChildren(prop)

        props += propsRoot

        for prop in props:
            # print (prop)
            if prop in self.ap_collect_prop_for_action(action, True):
                prop.hide = False
            else:
                prop.hide = True

    def ap_prop_ready_for_action(self):
        '''
        Create a specific action for the prop
        Create a ready to use copy transform constraint
        '''

        prop = bpy.data.objects.get(self.ap_target)
        seed = self.ap_collect_seed()[0]
        catcher = self.ap_collect_catcher()[0]
        act = seed.animation_data.action

        # Specific action
        if prop.type == 'ARMATURE':
            if not hasattr(prop.animation_data, "action"):
                propAct = bpy.data.actions.new("Prop" + act.name[4:])
                propAct.use_fake_user = True

                prop.animation_data_create()
                prop.animation_data.action = propAct

        # Specific contraint
        const = prop.constraints.new('COPY_TRANSFORMS')
        const.name = "Prop_Link"
        const.target = catcher

    @staticmethod
    def ap_merge_actions(sourceAct, targetAct, rem):
        '''
        Merge sourceAct tracks to targetAct
        output targetAct
        sourceAct is still conserved unless 'rem' is True
        '''

        for f in sourceAct.fcurves:

            # Avoid already existing track
            try:
                g = targetAct.fcurves.new(f.data_path, f.array_index)
            except RuntimeError as e:
                print (e)
                continue

            g.extrapolation = f.extrapolation
            g.color = f.color

            # Iterate througt each keyframe
            keysNb = len(f.keyframe_points)

            g.keyframe_points.add(keysNb)

            for i in range(keysNb):

                gKey = g.keyframe_points[i]
                fKey = f.keyframe_points[i]

                gKey.co = fKey.co
                gKey.handle_left_type = fKey.handle_left_type
                gKey.handle_right_type = fKey.handle_right_type
                gKey.interpolation = fKey.interpolation
                gKey.type = fKey.type
                gKey.easing = fKey.easing
                gKey.handle_left = fKey.handle_left
                gKey.handle_right = fKey.handle_right

        # Update action
        sourceAct.user_remap(targetAct)

        if rem:
            sourceAct.use_fake_user = False
            sourceAct.user_clear()
            bpy.data.actions.remove(sourceAct)

        return targetAct
    # END OF NEW PROP PIPELINE

    def ap_get_export_path(self):
        '''
        return export path stored in the catcher
        '''

        catcher = (self.ap_collect_catcher())[0]
        export_path = catcher.animPipeline.ap_export_path

        return export_path

    def ap_update_rig_version(self):
        '''
        propagate the seed version to the current action
        '''

        seed = (self.ap_collect_seed())[0]
        action = seed.animation_data.action
        ver = seed.animPipeline.get('ap_rig_version')

        if ver is not None:
            action.animPipeline.ap_rig_version = ver
        else:
            action.animPipeline.ap_rig_version = 0.0
            print ("Outdated Rig!!!")

    @staticmethod
    def ap_keep_one_action():
        '''
        Delete all actions
        except the one currently selected
        '''

        actToDel = []

        if bpy.context.object is not None:
            curAction = bpy.context.object.animation_data.action

        for act in bpy.data.actions:

            # Action is not the current one
            if act.name != curAction.name:
                actToDel.append(act.name)

        for act in actToDel:

                act = bpy.data.actions.get(act)
                act.use_fake_user = False
                act.user_clear()
                bpy.data.actions.remove(act)

    # LIBRARY METHODS
    @staticmethod
    def ap_remove_namespace(items, separator):
        '''
        remove namespace from a list of item
        Return 2 lists as [[oldnames][newnames]]
        '''

        oldNames = []
        newNames = []

        for item in items:
            oldNames.append(item.name)

            if separator in item.name:
                item.name = item.name[item.name.find(separator) + len(separator):]

            newNames.append(item.name)

        return [oldNames, newNames]

    @staticmethod
    def ap_restore_namespace(items):
        '''
        given an [[oldnames][newnames]] array
        restore the old namespace
        '''

        oldNames = items[0]
        newNames = items[1]

        for i in range(len(oldNames)):
            bpy.data.objects[newNames[i]].name = oldNames[i]
