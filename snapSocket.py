# DANS BLENDER ##### snapSocket
# Crée le menu qui permet de snapper le controller du socket à la main.

# A cleaner
# Corriger le bug quand desactivation du layer alors qu'un socket est activé.

import bpy
from bpy.types import Operator, Panel

# Add-on Informations
bl_info = {
   "name": "Kouji Props Socket",
   "author": "Spooklight Studio",
   "version": (2, 0, 0),
   "blender": (2, 79, 0),
   "location": "",
   "description": "Tools to manage Kouji's sockets for props",
   "warning": "",
   "wiki_url": "",
   "tracker_url": "",
   "category": "Animation"}


# Generic Class
class snapTo():
    '''
    Snap the source bone to his constraint object target
    The source bone must have one "Prop_Snap" Child Constraint
    '''

    source = bpy.props.StringProperty()

    def snap(self):

        # Recupère l'identitée de la target depuis la contrainte de la source.
        sourceBone = bpy.context.object.pose.bones[self.source]
        sourceConst = sourceBone.constraints.get("Prop_Snap")
        targetBone = sourceConst.target.pose.bones.get(sourceConst.subtarget)

        # Applique la position de la target sur la source.
        sourceBone.matrix = targetBone.matrix

        return{'FINISHED'}


# Operators
class snapToOperator(Operator, snapTo):
    bl_idname = "snapto.button"
    bl_label = "Snap Socket to Parent"

    source = bpy.props.StringProperty()

    def execute(self, context):
        self.snap()

        return{'FINISHED'}


# Interface
class propSocketInterface(Panel):

    bl_label = "Snap"
    bl_idname = "Stack_snap"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        isPoseMode = bpy.context.mode == 'POSE'
        isConst = bpy.context.active_pose_bone.constraints.get("Prop_Snap") is not None
        return isPoseMode and isConst

    def draw(self, context):

        layout = self.layout
        bone = context.object

        row = layout.row()
        row.operator("snapto.button").source = bpy.context.active_pose_bone.name
        row = layout.row()
        row.prop(bpy.context.active_pose_bone.constraints.get("Prop_Snap"), "influence")


def register():
    bpy.utils.register_class(propSocketInterface)
    bpy.utils.register_class(snapToOperator)


def unregister():
    bpy.utils.unregister_class(propSocketInterface)
    bpy.utils.register_class(snapToOperator)

if __name__ == "__main__":
    register()
