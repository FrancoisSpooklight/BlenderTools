import bpy
import time

# Check présence!!
from utility import utilities

bl_info = {
   "name": "Blendshape Propagation",
   "author": "Spooklight Studio",
   "version": (1, 0, 0),
   "blender": (2, 80, 0),
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
    source : bpy.props.StringProperty()
    target : bpy.props.StringProperty()

    # Methods
    @staticmethod
    def meshToShape(BSMesh, targetObj, key):

        '''
        Transfer a mesh on a Shape Key.
        Working only with identical topology

        sourceMesh: mesh(data) to write
        targetObj: target to write the BS into
        key: shape key name (string) on wich to write to.
        '''

        targetKey = targetObj.data.shape_keys.key_blocks[key.name]
        print ("Current Key : ", targetKey.name)

        # Copy the vertices coord from mesh to shape key.
        i = 0
        for vx in BSMesh.vertices:

            targetKey.data[i].co = vx.co
            #print(vx.co)

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
            #utilities.resetBS(sourceBS)

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

                # Store target result as a new mesh
                deps = bpy.context.evaluated_depsgraph_get()
                evalTarget = targetObj.evaluated_get(deps)
                BStoMesh = evalTarget.to_mesh()

                # Create a shape and write it as a new target's shape.
                newKey = targetObj.shape_key_add(name=key.name, from_mix=False)
                # Except for Basis Shape Key
                if key.name != 'Basis':
                    self.meshToShape(BStoMesh, targetObj, key)

                # Clean
                key.value = 0
                evalTarget.to_mesh_clear()
                for mod in fixMods:
                    mod.show_viewport = False
                utilities.screenUpdate()

            # Remove target's modifiers
            utilities.resetMod(targetObj)

        else:
            # Convert to raise warning
            print ("no BS in source object")


# Operator
class BSP_OT_bs_propagation (bpy.types.Operator, bsPropagation):
    '''
    Called in context: source is the active object, target the last.
    Called with parameters bpy.ops.bs.propagation(target = "", source = "")
    '''

    bl_idname = "bs.propagation"
    bl_label = "blendshape propagation"
    bl_description = "Apply the effect of a source's blenshape on a target"

    copyTarget : bpy.props.BoolProperty() = False

    @classmethod
    def poll(self, context):

        # Check if at least 2 objects are selected
        if len(context.selected_objects) > 1:
            source = context.active_object
            # The second object shouldn't be the active object
            selection = context.selected_objects
            selection.remove(source)
            target = selection[0]
        else:
            return False

        isSourceOk = False
        isTargetOk = False

        # Check that source is a mesh in object mode
        if source is not None:
            if source.type == 'MESH':
                if source.mode == 'OBJECT':
                    isSourceOk = True

        # Check that target is a mesh in object mode
        if target.type == 'MESH':
            if target.mode == 'OBJECT':
                isTargetOk = True

        return isSourceOk and isTargetOk

    def invoke(self, context, event):

        source = context.active_object
        self.source = source.name
        # The second object shouldn't be the active object
        selection = context.selected_objects
        selection.remove(source)
        target = selection[0]
        self.target = target.name

        # If copy: copy the original target object and change the target
        if self.copyTarget:
            newTarget = target.copy()
            bpy.context.scene.collection.objects.link(newTarget)
            newTarget.name = newTarget.name[:-3] + "BAKE"
            self.target = newTarget.name

        print("Source :",self.source)
        print("Target :", self.target)

        #check that both are not none and that target >< source
        return self.execute(context)

    def execute(self, context):
        self.propagate()
        return {'FINISHED'}

class BSP_PT_blendshape_propagation_panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Custom Tools"
    bl_label = 'Blendshape Baker'
    bl_options = {'HEADER_LAYOUT_EXPAND'}

    def draw(self, context):
        # UI
        layout = self.layout
        row = layout.row()
        bakeButton = row.operator("bs.propagation", text="BAKE", icon='RENDER_STILL').copyTarget = False
        row = layout.row()
        bakeButtonCopy = row.operator("bs.propagation", text="BAKE with Copy", icon='DUPLICATE').copyTarget = True


# Registration
def register():
    bpy.utils.register_class(BSP_OT_bs_propagation)
    bpy.utils.register_class(BSP_PT_blendshape_propagation_panel)


def unregister():
    bpy.utils.unregister_class(BSP_PT_blendshape_propagation_panel)
    bpy.utils.unregister_class(BSP_OT_bs_propagation)


if __name__ == '__main__':
    register()
