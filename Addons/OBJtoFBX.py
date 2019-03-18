import bpy
import os
import mathutils


bl_info = {
   "name": "OBJ to FBX",
   "author": "Spooklight Studio",
   "version": (0, 0, 1),
   "blender": (2, 79, 0),
   "location": "",
   "description": "Convert an OBJ folder to an usable FBX Folder",
   "warning": "",
   "wiki_url": "",
   "tracker_url": "",
   "category": "Import-Export"}


# Classes
class OBJtoFBXSettings(bpy.types.PropertyGroup):
    '''
    Definig the PropertyGroup used by the add-on.
    '''

    import_path = bpy.props.StringProperty(name="import path", subtype="FILE_PATH", default="C:/tmp/")
    export_path = bpy.props.StringProperty(name="export path", subtype="FILE_PATH", default="C:/tmp/FBX")
    scale = bpy.props.FloatProperty(name="scale", subtype="FACTOR", soft_min=0, soft_max=1, default=0.2)
    rig = bpy.props.StringProperty(name="rig", default="rig_catcher")
    bone = bpy.props.StringProperty(name="bone", default="CAT-head")


class OBJtoFBX():
    '''
    Methods Library
    '''

    # Class Variables
    IN_sourceFolder = bpy.props.StringProperty()
    IN_targetFolder = bpy.props.StringProperty()
    IN_scale = bpy.props.FloatProperty()
    IN_rig = bpy.props.StringProperty()
    IN_bone = bpy.props.StringProperty()

    def init(self):
        '''
        Attach the PropertyGroup to every Scene node
        '''
        bpy.types.Scene.OBJtoFBX = bpy.props.PointerProperty(name='OBJ to FBX', type=OBJtoFBXSettings)

    def screenUpdate(self):
        '''
        Update the viewport, applying the effect of shapes changes.
        '''

        for window in bpy.context.window_manager.windows:
            screen = window.screen

            for area in screen.areas:
                if area.type == 'VIEW_3D':
                    override = {'window': window, 'screen': screen, 'area': area}  # Inutile?
                    bpy.context.area.tag_redraw()
                    bpy.context.scene.update()
                    break

    def batchConvert(self):
        '''
        Main Method

        Iterate throught every file in a IN_source folder
        For every OBJ file, import it, treat it and
        export it in the IN_target folder as an fbx file.
        '''

        # Variables
        sourceFiles = []
        scale = [self.IN_scale, self.IN_scale, self.IN_scale]

        # For every file in the source folder:
        sourceFiles = os.listdir(os.path.normpath(self.IN_sourceFolder))

        for file in sourceFiles:

            # If the file is an .obj
            if file[-3:] == "obj":

                fullPath = self.IN_sourceFolder + file

                # import
                imported = bpy.ops.import_scene.obj(filepath=fullPath)
                obj = bpy.context.selected_objects[0]

                # scale
                obj.scale = scale

                # Put the object at the IN_bone position
                # bone position
                rig = bpy.data.objects.get(self.IN_rig)
                bone = rig.data.bones.get(self.IN_bone)
                poseBone = rig.pose.bones.get(self.IN_bone)

                # Determine bone Global World Position
                globalBoneLoc = rig.matrix_world * poseBone.matrix * poseBone.location

                bpy.context.scene.cursor_location = (globalBoneLoc)
                self.screenUpdate()
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

                # Apply scale and rotation
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

                # export fbx
                bpy.ops.export_scene.fbx(
                    filepath=self.IN_targetFolder + file[0:-7] + "FBX.fbx",
                    check_existing=False,
                    use_selection=True,
                    use_anim=False,
                    global_scale=1.0,
                    axis_forward='-Z',
                    axis_up='Y',
                    object_types={'MESH'})

                bpy.ops.object.delete()


# Operators
class initOp(bpy.types.Operator, OBJtoFBX):

    bl_idname = "obj2fbx.init"
    bl_label = "OBJ to FBX initialize"
    bl_description = "initialize the properties attached to the Scene node"

    def execute(self, context):
        self.init()
        return {'RUNNING_MODAL'}


class batchConvertOp(bpy.types.Operator, OBJtoFBX):

    bl_idname = "obj2fbx.batchconvert"
    bl_label = "OBJ to FBX converter"
    bl_description = "Convert the OBJ files at one location to FBX files saved in another one"

    def invoke(self, context, event):
        # Set class variables to scene variable
        self.IN_sourceFolder = bpy.context.scene.OBJtoFBX.import_path
        self.IN_targetFolder = bpy.context.scene.OBJtoFBX.export_path
        self.IN_scale = bpy.context.scene.OBJtoFBX.scale
        self.IN_rig = bpy.context.scene.OBJtoFBX.rig
        self.IN_bone = bpy.context.scene.OBJtoFBX.bone

        print ("import path", self.IN_sourceFolder)
        print ("export_path", self.IN_targetFolder)
        print ("rig", self.IN_rig)
        print ("bone", self.IN_bone)
        return self.execute(context)

    def execute(self, context):
        self.batchConvert()

        # Report
        message = "Export Done in" + self.IN_targetFolder
        self.report({'INFO'}, message)
        return {'FINISHED'}


# Panels
class OBJtoFBXPanel(bpy.types.Panel, OBJtoFBX):
    bl_label = "OBJ to FBX"
    bl_space_type = "VIEW_3D"
    bl_category = "Spooklight"
    bl_region_type = "TOOLS"

    @classmethod
    def poll(self, context):
        return True

    def draw(self, context):

        layout = self.layout
        row = layout.row()

        # If scene variables doesn't exist, display the "Init" button
        if bpy.context.scene.get("OBJtoFBX") is None:
            init_button = row.operator("obj2fbx.init", text="initialize")

        # Display the scene variables and "BATCH" butoon
        else:
            row.prop(bpy.context.scene.OBJtoFBX, "import_path")
            row = layout.row()
            row.prop(bpy.context.scene.OBJtoFBX, "export_path")
            row = layout.row()
            row.prop(bpy.context.scene.OBJtoFBX, "scale")
            row = layout.row()
            row.prop(bpy.context.scene.OBJtoFBX, "rig")
            row = layout.row()
            row.prop(bpy.context.scene.OBJtoFBX, "bone")
            row = layout.row()
            row.separator()
            row = layout.row()
            batch_button = row.operator("obj2fbx.batchconvert", text="BATCH CONVERT !")


# Registration
def register():
    bpy.utils.register_class(batchConvertOp)
    bpy.utils.register_class(initOp)
    bpy.utils.register_class(OBJtoFBXPanel)
    bpy.utils.register_class(OBJtoFBXSettings)

    bpy.types.Scene.OBJtoFBX = bpy.props.PointerProperty(name='OBJ to FBX',type=OBJtoFBXSettings)


def unregister():
    bpy.utils.unregister_class(batchConvertOp)
    bpy.utils.unregister_class(initOp)
    bpy.utils.unregister_class(OBJtoFBXPanel)
    bpy.utils.unregister_class(OBJtoFBXSettings)


if __name__ == '__main__':
    register()
