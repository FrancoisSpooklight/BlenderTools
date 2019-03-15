import bpy
import time
from utility import utilities

bl_info = {
   "name": "blendshapePropagation",
   "author": "Spooklight Studio",
   "version": (0, 0, 2),
   "blender": (2, 79, 0),
   "location": "",
   "description": "Apply the effect of a source's blenshape on a target",
   "warning": "",
   "wiki_url": "",
   "tracker_url": "",
   "category": "Rigging"}


# Methods Catalogs
class bsPropagation():
    '''
    Methods Library used by the Operator
    source: name of the object owning the shapes
    target: name of the object affected by the source
    '''

    # Input variables
    source = bpy.props.StringProperty()
    target = bpy.props.StringProperty()

    # Methods
    def meshToShape(self, sourceMesh, key):

        '''
        Transfer a mesh on a Shape Key.
        Working only with identical topology

        sourceMesh: mesh(data) to write
        key: shapekey on wich write to.
        '''

        # Pointers
        sourceObj = bpy.data.objects.get(self.source)
        targetObj = bpy.data.objects.get(self.target)

        targetKey = targetObj.data.shape_keys.key_blocks[key.name]

        # Copy the vertices coord from mesh to shape key.
        i = 0
        for vx in sourceMesh.vertices:

            targetKey.data[i].co = vx.co

            i += 1

    def propagate(self):
        '''
        Iterate among a source object's shape Keys.
        Activate them one by one.
        Generate a temporary mesh from the target and
        apply it as a new shape Key
        '''

        # Pointers
        sourceObj = bpy.data.objects.get(self.source)
        targetObj = bpy.data.objects.get(self.target)

        # Test Blendshapes
        # Doesn't do anything if source hasn't got shapes.
        sourceBS = sourceObj.data.shape_keys

        if sourceBS is not None:

            # Reset Blendshapes
            utilities.resetBS(sourceBS)

            # Iterate over Sources BS
            for key in sourceBS.key_blocks:

                key.value = 1

                # Activate or desactivate Fix Modifiers
                fixMods = []

                for mod in targetObj.modifiers:
                    if 'FIX' in mod.name:
                        if mod.name == 'FIX-' + key.name:
                            mod.show_viewport = True
                            fixMods.append(mod)
                        else:
                            mod.show_viewport = False

                # Update
                utilities.screenUpdate()

                # Store target result as a new mesh
                BStoMesh = targetObj.to_mesh(bpy.context.scene, True, ('PREVIEW'))

                # Create a shape and write it as a new target's shape.
                newKey = targetObj.shape_key_add(name=key.name, from_mix=False)
                # Except for Basis Shape Key
                if key.name != 'Basis':
                    self.meshToShape(BStoMesh, key)

                # Clean
                key.value = 0
                bpy.data.meshes.remove(BStoMesh)
                for mod in fixMods:
                    mod.show_viewport = False
                utilities.screenUpdate()

            # Remove target's modifiers
            utilities.resetMod(targetObj)

        else:
            print ("no BS in source object")


# Operator
class bsPropagationOp (bpy.types.Operator, bsPropagation):
    '''
    Called in context: source is the active object, target the last.
    Called with parameters bpy.ops.bs.propagation(target = "", source = "")
    '''

    bl_idname = "bs.propagation"
    bl_label = "blendshape propagation"
    bl_description = "Apply the effect of a source's blenshape on a target"

    def invoke(self, context, event):
        if len(bpy.context.selected_objects) > 1:
            self.source = bpy.context.active_object.name
            self.target = bpy.context.selected_objects[-1].name
            return self.execute(context)

    def execute(self, context):
        self.propagate()
        return {'FINISHED'}


# Registration
def register():
    bpy.utils.register_class(bsPropagationOp)


def unregister():
    bpy.utils.unregister_class(bsPropagationOp)


if __name__ == '__main__':
    register()
