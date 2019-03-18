import bpy
from bpy.app.handlers import persistent


bl_info = {
   "name": "Proxy Picker",
   "author": "Spooklight Studio",
   "version": (2, 0, 0),
   "blender": (2, 78, 0),
   "location": "",
   "description": "Manage The Bone picker for the Kouji Rig",
   "warning": "",
   "wiki_url": "",
   "tracker_url": "",
   "category": "Rigging"}


# Methods
def selectBones(target, bones):
    '''
    Select every bone  from a _bones_ list in the _target_ object
    Deselect the others.
    The active bone will be the last on the list.
    Don't handle wrong inputs.
    '''

    # print (target, "target")
    # print (bones, "bones")

    for bone in target.data.bones:
        if bone.name in bones:
            bone.select = True
        else:
            bone.select = False

    lastBone = target.data.bones.get(bones[-1])
    target.data.bones.active = lastBone


@persistent
def proxyPickerHandler(scene):
    '''
    Before every update, select bones regarding the current active object
    target stored in his own 'PICKER_TARGET*' constraints.
    '''

    #print ("Handler/ 1Frame")


    if bpy.context.scene.picker.edit_mode is False:

        #print ("Handler/ Edit Mode False")

        # Variables
        picked = None
        picker = None
        pickedBones = []

        # The potential picker is the first one selected
        sel = bpy.context.selected_objects
        if len(sel) > 0:
            picker = bpy.context.selected_objects[0]
        else:
            picker = None

        # For each constraint of the object
        for const in picker.constraints:

            # If the constraint is a 'PICKER_TARGET' one
            if 'PICKER_TARGET' in const.name and const.target is not None:
                picked = const.target

                # If the object is not an armature
                if picked.type != 'ARMATURE':
                    print ("Not an armature")

                # Else, you need to have a subtarget
                elif const.subtarget != "":
                    pickedBones.append(const.subtarget)

        if picked is not None:
            # Select the armature, deselect the picker
            bpy.context.scene.objects.active = picked
            picked.select = True
            picker.select = False

            # Select or deselect all the bones according to the picker
            selectBones(picked, pickedBones)


# Classes
class pickerSettings(bpy.types.PropertyGroup):
    '''
    Defining the PropertyGroup used by the add-on.
    '''

    edit_mode = bpy.props.BoolProperty(name="edit mode", default=True)


# Methodes library
class ProxyPicker:

    picker = bpy.props.StringProperty()

    def ppAddTarget(self):
        '''
        Add a 'PICKER_TARGET' constraint to the selected objet.
        Use the latest target if there is one/
        '''

        # Variables
        obj = bpy.data.objects.get(self.picker)
        pickerConstraints = []

        # For every constraint of the active object
        for constraint in obj.constraints:
            if "PICKER_TARGET" in constraint.name:
                pickerConstraints.append(constraint)

        # Create and configure the constraint
        const = obj.constraints.new('COPY_LOCATION')
        const.name = "PICKER_TARGET"
        const.use_x = False
        const.use_y = False
        const.use_z = False
        const.target = pickerConstraints[-1].target


# Target Add Operator
class ProxyPickerAddTarget(bpy.types.Operator, ProxyPicker):
    bl_idname = "pp.addtarget"
    bl_label = "add target"

    def execute(self, context):
        self.ppAddTarget()

        return {'FINISHED'}


# UI
class ProxyPickerPanel(bpy.types.Panel):

    bl_label = "Proxy Picker"
    bl_idname = "Proxy_Picker"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    # @classmethod
    # def poll(self, context):
    #     return bpy.context.object.mode == 'OBJECT'

    def draw(self, context):

        obj = bpy.context.object

        # Layout
        layout = self.layout
        row = layout.row()
        # Edit mode Check box
        row.prop(bpy.context.scene.picker, "edit_mode")

        # Targets and subtargets' choice
        for const in obj.constraints:

            row = layout.row()
            title = row.label(const.name)

            if "PICKER_TARGET" in const.name:
                row = layout.row()
                row.prop(const, "target")

                # If the target is an armature, bone's choice
                if const.target is not None:
                    if const.target.type == 'ARMATURE':
                        row = layout.row()
                        row.prop(const, "subtarget")

        # Add constraint Button
        row = layout.row()
        add_button = row.operator("pp.addtarget", text="Add").picker = obj.name


def register():
    bpy.utils.register_class(ProxyPickerPanel)
    bpy.utils.register_class(ProxyPickerAddTarget)
    bpy.utils.register_class(pickerSettings)
    bpy.types.Scene.picker = bpy.props.PointerProperty(name='Proxy Picker', type=pickerSettings)
    bpy.app.handlers.scene_update_pre.append(proxyPickerHandler)


def unregister():
    bpy.utils.unregister_class(ProxyPickerPanel)
    bpy.utils.unregister_class(ProxyPickerAddTarget)
    bpy.utils.unregister_class(pickerSettings)
    bpy.app.handlers.scene_update_pre.remove(proxyPickerHandler)

if __name__ == '__main__':
    register()
