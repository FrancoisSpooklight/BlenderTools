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
        print (targetKey)

        # Copy the vertices coord from mesh to shape key.
        i = 0
        for vx in BSMesh.vertices:

            targetKey.data[i].co = vx.co
            print(vx.co)

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

                # Update A virer?
                #targetObj.update_tag()
                #utilities.screenUpdate()

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
        if len(context.selected_objects) > 0:
            selected = context.selected_objects[0]
        else:
            return False

        active = context.active_object
        isSourceOk = False
        isTargetOk = False

        if active is not None:
            if active.type == 'MESH':
                    isSourceOk = True

        if selected.type == 'MESH':
            isTargetOk = True

        if isSourceOk and isTargetOk:
            return active is not selected
        else:
            return False

    def invoke(self, context, event):
        if len(bpy.context.selected_objects) > 1:
            self.source = bpy.context.active_object.name
            self.target = bpy.context.selected_objects[0].name

            if self.copyTarget:
                newTarget = bpy.context.selected_objects[0].copy()
                bpy.context.scene.collection.objects.link(newTarget)
                newTarget.name = newTarget.name[:-3] + "BAKE"
                self.target = newTarget.name
            else:
                self.target = bpy.context.selected_objects[0].name

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

    @classmethod
    def poll(self, context):
        return context.object.mode == 'OBJECT'

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
