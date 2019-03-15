import bpy
from bpy.types import PropertyGroup, Panel, Operator

# Add-on Informations
bl_info = {
   "name": "Kouji Lock Selection",
   "author": "Spooklight Studio",
   "version": (1, 0, 0),
   "blender": (2, 79, 0),
   "location": "",
   "description": "Lock selection to current selection",
   "warning": "",
   "wiki_url": "",
   "tracker_url": "",
   "category": "Animation"}


# InFile Settings
class apLockSelSettings(PropertyGroup):
    '''
    every scene/pbject/bone will be constructed with apActSettings collection
    '''
    ap_wasLocked = bpy.props.BoolProperty(
        name="Was Selection Locked", default=False)


class apLockSel:
    @staticmethod
    def saveLockState(sel, target):
        '''
        target is an array with each Item
        Containing an .hide_select property.

        sel is an array with each Item
        Containing an .apLockSelection property Group

        Store if the object was locked.
        Lock it if it wasn't selected
        '''

        # Store Selected Items
        for item in target:
            item.apLockSelection.ap_wasLocked = item.hide_select

            # Lock unselected item
            if item not in sel:
                item.hide_select = True

    @staticmethod
    def loadLockState(target):
        '''
        target is an array with each Item
        Containing an .hide_select and .apLockSelection property.

        Reload previous lock state of
        each item in target
        '''

        for item in target:
            item.hide_select = item.apLockSelection.ap_wasLocked


# Operators
class apLockSelOp(Operator, apLockSel):
    '''
    Lock current selection
    '''

    bl_idname = "ap.locksel"
    bl_label = "Lock Selection"

    def execute(self, context):
        # Objects
        self.saveLockState(
            bpy.context.selected_objects, bpy.context.scene.objects)

        # Bones
        if bpy.context.active_object.type == 'ARMATURE':

            # Convert posebones array to bones array
            selBones = []
            for pbone in bpy.context.selected_pose_bones:
                selBones.append(pbone.bone)
            self.saveLockState(selBones, bpy.context.active_object.data.bones)

        # Switch Scene Lock State
        bpy.context.scene.apLockSelection.ap_wasLocked = True

        return {'FINISHED'}


class apUnlockSelOp(Operator, apLockSel):
    '''
    Unlock current selection
    '''

    bl_idname = "ap.unlocksel"
    bl_label = "Unock Selection"

    def execute(self, context):

        # Objects
        self.loadLockState(bpy.context.scene.objects)

        # Bones
        if bpy.context.active_object.type == 'ARMATURE':
            self.loadLockState(bpy.context.active_object.data.bones)

        # Switch Scene Lock State
        bpy.context.scene.apLockSelection.ap_wasLocked = False

        return {'FINISHED'}


# Interface graphique
class lockSelectionPanel(Panel):
    bl_label = "Selection Locker"
    bl_space_type = "VIEW_3D"
    bl_category = "Spooklight"
    bl_region_type = "TOOLS"

    def draw(self, context):
            scene = bpy.context.scene
            layout = self.layout
            row = layout.row()

            if bpy.context.scene.apLockSelection.ap_wasLocked:
                unlockButton = row.operator(
                    "ap.unlocksel", text="Unlock Selection")
            else:
                lockButton = row.operator(
                    "ap.locksel", text="Lock Selection")


def register():
    bpy.utils.register_class(apLockSelOp)
    bpy.utils.register_class(apUnlockSelOp)
    bpy.utils.register_class(lockSelectionPanel)
    bpy.utils.register_class(apLockSelSettings)

    # Properties Registration
    bpy.types.Object.apLockSelection = bpy.props.PointerProperty(
        name='Lock Selection', type=apLockSelSettings)
    bpy.types.Bone.apLockSelection = bpy.props.PointerProperty(
        name='Lock Selection', type=apLockSelSettings)
    bpy.types.Scene.apLockSelection = bpy.props.PointerProperty(
        name='Lock Selection', type=apLockSelSettings)


def unregister():
    bpy.utils.unregister_class(apLockSelOp)
    bpy.utils.unregister_class(apUnlockSelOp)
    bpy.utils.unregister_class(lockSelectionPanel)
    bpy.utils.unregister_class(apLockSelSettings)

if __name__ == "__main__":
    register()
