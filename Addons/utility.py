import bpy

bl_info = {
    "name": "Animation Pipeline Utilities",
    "author": "Spooklight Studio",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "",
    "description": "Common Methods Library",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Development"}


class utilities():

    @staticmethod
    def screenUpdate():

        '''
        Update the viewport, applying the effect of shapes changes.
        '''

        for window in bpy.context.window_manager.windows:
            screen = window.screen

            for area in screen.areas:
                if area.type == 'VIEW_3D':
                    override = {'window': window, 'screen': screen, 'area': area}  # Inutile?
                    bpy.context.area.tag_redraw()
                    bpy.context.view_layer.update()
                    break

    @staticmethod
    def resetBS(shapes):
        '''
        Set the values of all the Shape Keys to 0
        shapes: Shape Key set
        '''
        for BS in shapes.key_blocks:
            BS.value = 0

    @staticmethod
    def resetMod(object):
        '''
        Get Rid of all the modifiers of an object
        '''
        for mod in object.modifiers:
            object.modifiers.remove(mod)

    @staticmethod
    def updateScreen():
        '''
        Redraw all the 3D views
        '''

        for window in bpy.context.window_manager.windows:
            screen = window.screen

        for area in screen.areas:
            if area.type == 'VIEW_3D':
                bpy.context.area.tag_redraw()

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

    @staticmethod
    def duplicateObj(obj, withChildren=False, link=False):
        '''
        Duplicate given object
        withChildren (also duplicate the children of this object)
        link (link the results in the current scene)

        return an dict as oldobj:newobj
        '''

        objtoDuplicate = [obj]
        duplicatedObj = {}

        if withChildren:
            objtoDuplicate += utilities.getChildren(obj)

        # Duplicate all data blocks
        for o in objtoDuplicate:
            # Copy data and object
            if o.type in ['MESH', 'ARMATURE']:
                newData = o.data.copy()
            newObj = o.copy()

            # Store the result in a dic as oldobj:newobj
            duplicatedObj[o.name] = newObj.name

            if link:
                bpy.context.scene.collection.objects.link(newObj)

        # Reconstruct Hierarchy
        for o in duplicatedObj:

            newObject = bpy.data.objects.get(duplicatedObj[o])
            oldObject = bpy.data.objects.get(o)

            if oldObject.parent is not None:
                newParent = bpy.data.objects.get(duplicatedObj[oldObject.parent.name])
                newObject.parent = newParent
                newObject.matrix_parent_inverse = oldObject.matrix_parent_inverse

        return duplicatedObj


class UTILS_OT_help_desk(bpy.types.Operator):
    '''
    Call the context bl_info help url
    '''

    bl_idname = "help.desk"
    bl_label = "Spooklight HelpDesk"
    bl_description = "Open the current AddOn Help URL"

    helpURL : bpy.props.StringProperty()

    def execute(self, context):
        bpy.ops.wm.url_open(url=self.helpURL)
        return{'FINISHED'}


def register():
    bpy.utils.register_class(UTILS_OT_help_desk)


def unregister():
    bpy.utils.unregister_class(UTILS_OT_help_desk)
