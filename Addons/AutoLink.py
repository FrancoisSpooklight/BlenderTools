import bpy
import os

# INIT
print ('AUTOLINK launched in', __name__)


# CLASSES
class AutoLink:

    rigPath = bpy.props.StringProperty(subtype="FILE_PATH", default="//" + os.path.join("00_Rig", "00_KOUJI_Rig.blend"))
    animsPath = bpy.props.StringProperty(subtype="FILE_PATH", default="//01_Blend")
    propsPath = bpy.props.StringProperty(subtype="FILE_PATH", default="//04_Props")
    link = bpy.props.BoolProperty(default=True)
    exceptions = bpy.props.EnumProperty(items=())

    exceptions = ('WGT', 'PIK', 'UV')
    propsCompliant = ('Prop', 'PROP', 'VFX', 'Vfx', 'Set', 'SET')

    @staticmethod
    def storeParenting(object):
        '''
        return a dictionary as {object:parent}
        '''
        # Store every object in the hierachy
        toProcess = [object]
        oldProcess = []

        while toProcess != oldProcess:
            oldProcess = toProcess

            for obj in toProcess:
                for child in obj.children:
                    toProcess.append(child)

        # Create the dictionnary
        hierarchy = {}

        for item in toProcess:
            hierarchy[item] = item.parent

        return hierarchy

    @staticmethod
    def restoreParenting(hierarchy):
        '''
        recreate parenting accordind to the {object:parent} dic input.
        '''

        for obj in hierarchy:
            if hierarchy[obj] is not None:
                parent = bpy.data.objects.get(hierarchy[obj].name)
            else:
                parent = None
            child = bpy.data.objects.get(obj.name)
            child.parent = parent

            if parent is not None:
                child.matrix_parent_inverse = parent.matrix_world.inverted()

    @staticmethod
    def isExcept(input, excps):
        '''
        is a string input containing
        exceptions from a list?
        Raise True else False
        '''
        for excp in excps:
            if excp in input:
                return True
        return False

    def linkRig(self):
        '''
        Link items in the scene from the libraries
        found in the specified files
        '''

        # Path from the blend file
        path = bpy.path.abspath(self.rigPath)

        print ("Importing RIG from", path)

        # Import library's objects in two arrays
        with bpy.data.libraries.load(path) as (data_from, data_to):
            data_to.objects = [obj for obj in data_from.objects if not self.isExcept(obj, self.exceptions)]

        print (path + "\\Object\\")

        for obj in data_to.objects:
            bpy.context.scene.objects.link(obj)

    def linkProps(self):
        '''
        Link Props in the scene from the action files
        (!NOT from the PROP files, the prop needs to be in context)
        '''

        path = bpy.path.abspath(self.animsPath) + "\\"
        propsFiles = os.listdir(os.path.normpath(path))
        propsCount = {}  # nb of props per file for later warning

        print ("Importing PROPS from", path)

        for file in propsFiles:

            # Path or the anims blend files
            filePath = path + file
            props = []
            roots = []

            try:
                # Import library's objects in two arrays
                with bpy.data.libraries.load(filePath, link=self.link) as (data_from, data_to):

                    # Import process
                    data_to.objects = [obj for obj in data_from.objects if self.isExcept(obj, self.propsCompliant) and not self.isExcept(obj, self.exceptions)]

                    propsCount[file] = len(data_to.objects)

                # Link first all objects in the scene
                for obj in data_to.objects:
                    bpy.context.scene.objects.link(obj)

                    props.append(obj)

                # Process all the objects
                for obj in props:

                    # Add a namespace to the prop name (for duplicata)
                    obj.name = file + "::" + obj.name

                    # Hide object until it's called by the Anim Pipeline
                    obj.hide = True

                    # If the object has no parents, store as a root
                    if obj.parent is None:
                        roots.append(self.storeParenting(obj))

                    # Unlink the object node from the library
                    obj = obj.make_local()

                    # Relink constraints
                    for const in obj.constraints:
                        target = bpy.data.objects.get(const.target.name)
                        const.target = target

                    # Relink Skin:
                    for modifier in obj.modifiers:
                        if modifier.type == 'ARMATURE':
                            target = bpy.data.objects.get(modifier.object.name)
                            modifier.object = target

                # Restore Parenting
                for root in roots:
                        self.restoreParenting(root)

            except:
                # a -1 raise a warning message during the operator execution
                propsCount[file] = -1
                pass

        return propsCount

    def linkAction(self):
        '''
        Link Actions in the scene from the libraries
        found in the specified files
        '''

        path = bpy.path.abspath(self.animsPath) + "/"
        animFiles = os.listdir(os.path.normpath(path))
        actCount = {}  # nb of act per file for later warning

        for file in animFiles:
            # Path or the anims blend files
            filePath = path + file
            actions = []

            # Import library's actions in two arrays
            with bpy.data.libraries.load(filePath, link=self.link) as (data_from, data_to):

                actCount[file] = len(data_from.actions)

                # Import process
                data_to.actions = data_from.actions

            # Change Namespace in linked props list
            for act in data_from.actions:

                # Iterate throught list (if list exists)
                if act.animPipeline.get("ap_prop_1") is not None:
                    act.animPipeline.ap_prop_1 = file + "::" + act.animPipeline.ap_prop_1
                if act.animPipeline.get("ap_prop_2") is not None:
                    act.animPipeline.ap_prop_2 = file + "::" + act.animPipeline.ap_prop_2
                if act.animPipeline.get("ap_prop_3") is not None:
                    act.animPipeline.ap_prop_3 = file + "::" + act.animPipeline.ap_prop_3
                if act.animPipeline.get("ap_prop_4") is not None:
                    act.animPipeline.ap_prop_4 = file + "::" + act.animPipeline.ap_prop_4

        return actCount

    @staticmethod
    def fakeUserActions():
        '''
        each action will have single user enabled
        '''

        for act in bpy.data.actions:
            act.use_fake_user = True


class AutoLinkOp(bpy.types.Operator, AutoLink):
    bl_idname = 'ap.autolink'
    bl_label = 'AutoLink'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        # Exec
        self.report({'INFO'}, "Importing Rig from "+self.rigPath)
        self.linkRig()
        self.report({'INFO'}, "Importing Anims from"+self.animsPath)
        actCount = self.linkAction()
        self.fakeUserActions()
        self.report({'INFO'}, "Importing Props from"+self.animsPath)
        propsCount = self.linkProps()

        # Warning ACTIONS
        for act in actCount:
            if actCount[act] > 1:
                self.report({'WARNING'}, "%s contains %d actions!" % (act, actCount[act]))

        # Warning PROPS
        for prop in propsCount:
            if propsCount[prop] > 0:
                self.report({'INFO'}, "%d object(s) imported from %s" % (propsCount[prop], prop))
            elif propsCount[prop] == 0:
                self.report({'WARNING'}, "%s contains 0 valid object" % (prop))
            else:
                self.report({'WARNING'}, "%s has encoutered an error!" % (prop))

        self.report({'INFO'}, "DONE")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(AutoLinkOp)
    bpy.ops.ap.autolink()


def unregister():
    bpy.utils.unregister_class(AutoLinkOp)

if __name__ in ["AutoLink", "__main__"]:
    register()
