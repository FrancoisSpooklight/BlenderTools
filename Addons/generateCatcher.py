import bpy
from mathutils import Vector

bl_info = {
    "name": "catcherGenerator",
    "author": "Spooklight Studio",
    "version": (2, 0, 0),
    "blender": (2, 91, 0),
    "location": "ADD OBJECT > Armature",
    "description": "Generate a rig catcher based on a rigify rig",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Rigging"}


class CatcherGenerator:

    def __init__(self):
        pass

    @staticmethod
    def collect_def_bones(rig):
        """
        Collects all the deformation bones.

        Return an array of objects with these information per elements:
            Bone Name, Head Position, Tail Position
            Bone Orientation Matrix, is Bone connected, Bone Parent.

        Input: rigObj: un objet Armature Rigify

        """

        # Context
        bpy.ops.object.mode_set(mode='EDIT')

        # Variables
        bones = rig.data.edit_bones
        def_bones = []

        # Iteration
        # bpy.context.view_layer.objects.active = rigObj

        for bone in bones:

            # print (bone.name) # DEBUG

            # Passer DEF et CAT en param !!!
            if "DEF" in bone.name:
                bone_infos = ['CAT' + bone.name[3:], bone.head, bone.tail, bone.matrix, bone.use_connect]

                # parenting
                parent = bone.parent

                # prevent non-parented bones
                if bone.parent is None:
                    print(bone.name, "Has no parent !!!")
                    bone_infos.append('')
                # Special Parent Bones
                elif 'DEF' not in parent.name:
                    # Try 3 Parent levels
                    for i in reversed(range(10)):  # Parameter !!!
                        # If no parent, break
                        if parent is None:
                            bone_infos.append('')
                            print(bone.name, "Has no primal parent !!!")
                            break

                        # If this parent is a DEF Bone
                        if bones.get('DEF' + parent.name[3:]) is not None:
                            # but has the same name than the child
                            if 'DEF' + parent.name[3:] == bone.name:
                                # Iterate
                                parent = parent.parent
                                continue
                            else:
                                # There we are! Register and break
                                bone_infos.append('CAT' + parent.name[3:])
                                break
                        elif i == 0:
                            # Nothing interesting. Stop trying.
                            print(bone.name, "no DEF parent found !!!")
                            bone_infos.append('')
                            break

                        else:
                            # iterate
                            parent = parent.parent

                # Regular Bone
                else:
                    bone_infos.append('CAT' + parent.name[3:])

                # Collapsing
                def_bones.append(bone_infos)

        return def_bones

    @staticmethod
    def create_cat_bones(def_bones):
        """
        Create a new armature and a corresponding object at (0,0,0)
        Create a bone for each one in the array
        Fits each bone to its heir
        Create a constraint for each new bone fiting its heir.
        """

        # Create new armature, checking if each component already exists
        if bpy.data.armatures.get('rig_catcher') is None:
            catcher_armature = bpy.data.armatures.new('rig_catcher')
        else:
            catcher_armature = bpy.data.armatures['rig_catcher']

        if bpy.data.objects.get('rig_catcher') is None:
            catcher_object = bpy.data.objects.new('rig_catcher', catcher_armature)
        else:
            catcher_object = bpy.data.objects['rig_catcher']

        if bpy.context.view_layer.objects.get('rig_catcher') is None:
            bpy.context.scene.collection.objects.link(catcher_object)

        catcher = bpy.context.view_layer.objects['rig_catcher']
        bpy.context.view_layer.objects.active = catcher

        # Iteration
        for bone in def_bones:
            # CreateBone
            bpy.ops.object.mode_set(mode='EDIT')  # ????????? pour la boucle????

            cat_bone = catcher.data.edit_bones.new(bone[0])  # replace "DEF" in name by "CAT"

            # repoint
            # cat_bone = catcher.data.edit_bones.get(bone[0])  # ????

            cat_bone.head = bone[1]
            cat_bone.tail = bone[2]
            cat_bone.matrix = bone[3]

        return catcher

    @staticmethod
    def constraint_rig(rig, catcher):
        """
        Create constraints to link Catcher moves to original rig
        """

        bpy.ops.object.mode_set(mode='POSE')
        drived_bones = catcher.pose.bones

        for drived in drived_bones:
            constraint = drived.constraints.new('COPY_TRANSFORMS')
            constraint.target = rig
            constraint.subtarget = 'DEF' + drived.name[3:]

    @staticmethod
    def consolidate_rig(catcher, def_bones):
        """
        reparente les bones
        """

        bpy.ops.object.mode_set(mode='EDIT')

        for bone in def_bones:
            print("parenting", bone[0], "to", bone[5])

            # Search child bone from defBones
            child = catcher.data.edit_bones.get(bone[0])
            # Search parent bone from defBones
            parent = catcher.data.edit_bones.get(bone[5])

            child.parent = parent
            child.use_connect = bone[4]


class GenerateCatcher(bpy.types.Operator, CatcherGenerator):
    bl_idname = 'ap.generate_catcher'
    bl_label = 'Generate Catcher from Rigify'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        return bpy.context.active_object.data.get("rig_id") is not None

    def execute(self, context):
        target = bpy.context.object
        def_bones = self.collect_def_bones(bpy.context.object)
        catcher = self.create_cat_bones(def_bones)
        self.consolidate_rig(catcher, def_bones)
        self.constraint_rig(target, catcher)
        return {'FINISHED'}


classes = (
    GenerateCatcher,
)


def menu_func(self, context):
    self.layout.operator(GenerateCatcher.bl_idname, icon='OUTLINER_OB_ARMATURE')


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_armature_add.append(menu_func)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_MT_armature_add.remove(menu_func)


if __name__ == "__main__":
    register()
