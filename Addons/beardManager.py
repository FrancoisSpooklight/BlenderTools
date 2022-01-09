import bpy
import time
from blendshapePropagation import bsPropagation
from utility import utilities

bl_info = {
   "name": "BlendShape Baker",
   "author": "Spooklight Studio",
   "version": (2, 0, 0),
   "blender": (2, 80, 0),
   "location": "",
   "description": "Manage Blendshape Baking from a controller to a controlled object",
   "warning": "",
   "wiki_url": "https://drive.google.com/drive/u/0/folders/1iCiJOuvYUDW1UnV51MYD8gh0k5IAbFEq?ogsrc=32",
   "tracker_url": "",
   "category": "Rigging"}


#  InFile Settings
class beardManSettings(bpy.types.PropertyGroup):
    '''
    Variables initialized with the script for customization
    '''
    # Variables
    enabled : bpy.props.BoolProperty(name="Enabled", default=True)
    root : bpy.props.StringProperty(name="Root", default=".Empty")
    cage : bpy.props.StringProperty(name="Deformation Cage", default=".Cage")
    dynamic : bpy.props.StringProperty(name="Dynamic Object", default=".Dynamic")
    mustache : bpy.props.StringProperty(name="Mustache Object", default=".Moustache")
    mouth : bpy.props.StringProperty(name="Mouth Object", default="Kouji_Face.Mouth")
    # Originals Objects
    originalBeard : bpy.props.StringProperty(name="Beard Root", default="")
    originalMustache : bpy.props.StringProperty(name="Mustache Root", default="")
    originalBeardMustache : bpy.props.StringProperty(name="Beard/Mustache Root", default="")
    # Operator Properties
    isBeard : bpy.props.BoolProperty(name="Beard", default=False)
    isMustache : bpy.props.BoolProperty(name="Mustache", default=False)


class beardManager(bsPropagation):
    '''
    Automation Tools for beard and mustaches
    '''

    def createUpdateObject(self, target, source):
            '''
            Generic method creating a new object
            From a target object and
            According to his source new BS

            return the object (in .data, not in the scene)
            '''

            # Copy original Beard
            newTarget = target.copy()
            newTarget.data = newTarget.data.copy()

            # Update Variables
            self.source = source.name
            self.target = newTarget.name

            # Propagate
            self.propagate()

            return newTarget

    def updateBeardAndMustache(self):
        '''
        CHECK: active object is a root

        select root
        Check if it's a beard and a mustache
        Get it and Update it
        '''

        # Custom Wrangler (Custom String Terms)
        wrangler = bpy.context.scene.beardManager

        # Root
        root = bpy.context.active_object
        rootName = root.name[:-6]

        # Add Data wrangler
        # ChildObjects
        original = bpy.data.objects.get(rootName)
        #
        beardCage = bpy.data.objects.get(rootName + wrangler.cage)
        beardDynamic = bpy.data.objects.get(rootName + wrangler.dynamic)
        #
        mustacheDynamic = bpy.data.objects.get(rootName + wrangler.mustache + wrangler.dynamic)
        mouthMesh = bpy.data.objects.get(wrangler.mouth)
        #
        newBeard = None
        newMustache = None
        result = None

        # Processing updates
        # Beard (and mustache)...
        if beardDynamic is not None:
            print ("There is a beard : " + beardDynamic.name)

            newBeard = self.createUpdateObject(beardDynamic, beardCage)
            newBeard.data.name = original.data.name

            # ... And Mustache
            if mustacheDynamic is not None:
                print ("There is also a mustache : " + mustacheDynamic.name)

                # Update mustacheDynamic with new beard BS
                mustacheDynamic.data = newBeard.data
                newMustache = self.createUpdateObject(mustacheDynamic, mouthMesh)
                newMustache.data.name = mustacheDynamic.data.name

        # Mustache Only
        elif mustacheDynamic is not None:
            print ("There is a mustache : " + mustacheDynamic.name)

            newMustache = self.createUpdateObject(mustacheDynamic, mouthMesh)
            newMustache.data.name = original.data.name

        # Clean
        # Find out which object is the final result
        if newBeard is not None and newMustache is None:
            result = newBeard
        elif newMustache is not None:
            result = newMustache

        if result is not None:
            # result is new original object
            result.name = original.name
            print (result.name)
            # Append it in the scene and link it to the root
            bpy.context.scene.collection.objects.link(result)
            result.parent = root

            # Delete old original
            original.user_clear()
            bpy.data.objects.remove(original)

            # Clean left unused data
            for mesh in bpy.data.meshes:
                if mesh.users == 0:
                    print ("Cleaning ", mesh.name, " removed.")
                    bpy.data.meshes.remove(mesh)

    def createNew(self, mesh, dupli):
        '''
        Duplicate an original model of beard and mustache
        and apply the currently selected mesh to it
        '''
        wrangler = bpy.context.scene.beardManager

        # Reminder the output of this is a dic {old:new}
        objs = utilities.duplicateObj(dupli, True, True)

        # Find the original mesh name
        originalMesh = ""
        for oldObj in objs:

            if wrangler.root in oldObj:
                # Remove the root identifier
                originalMesh = oldObj[0:-len(wrangler.root)]
                break

        # print (originalMesh)

        # Mesh update and rename
        for oldObj in objs:
            newObj = bpy.data.objects.get(objs[oldObj])
            oldObj = bpy.data.objects.get(oldObj)

            # Exclude the cage from the mesh update
            if oldObj.type == 'MESH' and wrangler.cage not in oldObj.name:
                newObj.data = mesh

            # Reconstruct newObj name
            i = newObj.name.find(originalMesh)
            j = len(originalMesh)

            # If the mesh name is found
            if i >= 0:
                newObj.name = newObj.name[:i] + mesh.name + newObj.name[i+j:-4]

        ### This part is really dirty and contextual...
        # Clean old mesh (currently active)
        toClean = bpy.context.object
        toRename = bpy.data.objects.get(oldName + ".001")
        toClean.user_clear()
        bpy.data.objects.remove(toClean)

        # Rename ducplicate
        toRename.name = oldName


# Operators
class BSB_OT_init_beard_and_mustache(bpy.types.Operator):
    bl_idname = "beardmanager.init"
    bl_label = "Beard Manager Initialisation"
    bl_description = "Initialize beard Manager in the scene"

    def execute(self, context):
        bpy.types.Scene.beardManager = bpy.props.PointerProperty(name='Beard Manager', type=beardManSettings)
        return {'FINISHED'}


class BSB_OT_update_beard_and_mustache(bpy.types.Operator, beardManager):
    '''
    Update all the Blendshapes of a selected Beard/Mustache Structure
    '''

    bl_idname = "beardmanager.update"
    bl_label = "Beard Manager Update"
    bl_description = "Update a beard and/or mustache with the currents blendshapes"

    @classmethod
    def poll(cls, context):
        obj = bpy.context.active_object
        if obj is not None and obj.name[-6:] == bpy.context.scene.beardManager.root:
            return True
        else:
            return False

    def invoke(self, context, event):
        self.report({'INFO'}, "Updating Beard/Mustache...")
        return self.execute(context)

    def execute(self, context):
        self.updateBeardAndMustache()
        self.report({'INFO'}, "Done !")
        return {'FINISHED'}


class BSB_OT_create_beard_and_mustache(bpy.types.Operator, beardManager):
    '''
    Copy an original structure of Beard/ Mustache or both
    Apply the selected mesh to it
    '''

    bl_idname = "beardmanager.create"
    bl_label = "Beard Manager Create"
    bl_description = "Create a new beard and/or mustache with the currently selected mesh"

    @classmethod
    def poll(cls, context):
        obj = bpy.context.active_object
        '''
        poll is ok when there is a mesh selected
        and at least one option 'beard' or 'mustache' are True
        '''
        wrangler = bpy.context.scene.beardManager

        isMesh = obj is not None and obj.type == 'MESH'
        isOpt = wrangler.isBeard or wrangler.isMustache

        return isMesh and isOpt

    def invoke(self, context, event):
        self.report({'INFO'}, "Creating Beard/Mustache...")
        return self.execute(context)

    def execute(self, context):
        wrangler = bpy.context.scene.beardManager

        isBeard = wrangler.isBeard
        isMustache = wrangler.isMustache

        if isBeard and not isMustache:
            original = bpy.data.objects.get(wrangler.originalBeard)
        elif isMustache and not isBeard:
            original = bpy.data.objects.get(wrangler.originalMustache)
        elif isBeard and isMustache:
            original = bpy.data.objects.get(wrangler.originalBeardMustache)
        else:
            original = None
            print ('No parameters')

        if original is None:
            self.report({'ERROR'}, "Original Object cannot be found")

        self.createNew(bpy.context.active_object.data, original)
        self.report({'INFO'}, "Done !")

        return {'FINISHED'}


# UI
class BSB_PT_beard_manager_ui(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Custom Tools"
    bl_label = 'Blendshape Baker'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        if context.object is not None:
            return context.object.mode == 'OBJECT'

    def draw(self, context):

        obj = bpy.context.object
        try:
            wrangler = bpy.context.scene.beardManager
        except:
            wrangler = None

        # UI
        layout = self.layout

        # Variables and tools if scene is correctly configured
        if wrangler is not None and wrangler.enabled is True:

            label = layout.label(text='Tools')
            row = layout.row()
            updateButton = row.operator("beardmanager.update", text="update")
            row = layout.row()
            createButton = row.operator("beardmanager.create", text="create")
            row = layout.row()
            row.prop(wrangler, "isBeard")
            row.prop(wrangler, "isMustache")

            label = layout.label(text='Variables')
            box = layout.box()
            row = box.row()
            row.prop(wrangler, "root")
            row = box.row()
            row.prop(wrangler, "cage")
            row = box.row()
            row.prop(wrangler, "dynamic")
            row = box.row()
            row.prop(wrangler, "mustache")
            row = box.row()
            row.prop(wrangler, "mouth")

            label = layout.label(text='Original Objects')
            box = layout.box()
            row = box.row()
            row.prop(wrangler, "originalBeard")
            row = box.row()
            row.prop(wrangler, "originalMustache")
            row = box.row()
            row.prop(wrangler, "originalBeardMustache")

            
        # Init button if scene is not correctly configured
        else:
            row = layout.row()
            initButton = row.operator("beardmanager.init", text="Initialize")

        label = layout.label(text='Help')
        row = layout.row()
        helpButton = row.operator("help.desk", text="help desk", icon='QUESTION').helpURL = bl_info['wiki_url']



# Registration
classes = (
    beardManSettings,
    BSB_OT_init_beard_and_mustache,
    BSB_OT_update_beard_and_mustache,
    BSB_OT_create_beard_and_mustache,
    BSB_PT_beard_manager_ui
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == '__main__':
    register()
