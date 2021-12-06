# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8-80 compliant>

bl_info = {
    "name": "Shape Keys Tools",
    "author": "François Carrobourg",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "Object Data > Shape Keys Specials or Search",
    "description": "A set of tools for Shape Keys",
    "doc_url": "",
    "category": "Animation"
}


import bpy

 
class BSTools():
    '''
    Library of methods for shape keys edition    
    '''

    @staticmethod
    def BS_Mute_All(select,mute):
        '''
        mute or unmute shapes of selected objects.
        '''
                
        for obj in select:
            for shape in obj.data.shape_keys.key_blocks:
                if mute == "True":
                    shape.mute = True
                elif mute == "False":
                    shape.mute = False
                elif mute == "Swap":
                    shape.mute = not(shape.mute)
     
    @staticmethod
    def BS_Store_Visibility(obj):
        """
        Return a dictionary of an object's shapes visibility
        """
        
        mute_dict = {}
        for shape in obj.data.shape_keys.key_blocks:
            mute_dict[shape.name] = shape.mute
            
        return mute_dict
    
    @staticmethod
    def BS_Recall_Visibility(obj,dict):
        """
        Restore shapes visibility from a previously saved state.
        """
        
        for shape in obj.data.shape_keys.key_blocks:
            try:
                shape.mute = dict[shape.name]
            except:
                pass

    @staticmethod
    def BS_Mirror_All(select,use_topology):
        """
        Mirror unmute shapes.
        """
        
        for obj in select:
            i = 0
            for shape in obj.data.shape_keys.key_blocks:
                obj.active_shape_key_index = i
                if i > 0:
                    if not(shape.mute):
                        bpy.ops.object.shape_key_mirror(use_topology=use_topology)
                i += 1

    @staticmethod
    def BS_Mirror_Copy(obj,use_topology):
        """
        Create a mirror duplicate of the active shape
        """
        shape = obj.data.shape_keys.key_blocks[obj.active_shape_key_index]
        
        # Copy current shape
        obj.show_only_shape_key = True
        bpy.ops.object.shape_key_add(from_mix=True)
        
        # Rename it
        newName = shape.name
        if newName[-1] == "L":
            newName = newName[:-1] + "R"
        elif newName[-1] == "R":
            newName = newName[:-1] + "L"
        obj.data.shape_keys.key_blocks[-1].name = newName
        
        # Mirror it
        obj.active_shape_key_index = len(obj.data.shape_keys.key_blocks) -1
        print ("active shape :",obj.active_shape_key_index, obj.data.shape_keys.key_blocks[-1].name)
        bpy.ops.object.shape_key_mirror(use_topology=use_topology)

    @staticmethod
    def BS_Update_Drivers(select):
        """
        update shapes' drivers of the selection.
        """
    
        for obj in select:
            
            try:
                drivers = obj.data.shape_keys.animation_data.drivers
            except:
                continue
            
            for driver in drivers:
                driver.driver.expression += " "
                driver.driver.expression = driver.driver.expression[:-1]
                driver.update()

    def BS_Bake(self,select):
        """
        Bake non-muted shapes by mix duplication 
        """
        
        for obj in select:
            BS_Store = self.BS_Store_Visibility(obj)
            BSCount = len(obj.data.shape_keys.key_blocks)
            print ("Blendshapes blocks :",BSCount)
            
            obj.show_only_shape_key = True
            
            j = 1
            for i in range(1,BSCount):
                shape = obj.data.shape_keys.key_blocks[j]
                BSname = shape.name
                
                print (i,":",shape.name)
                
                if not(shape.mute):
                    
                    # Show only one shape and create a new one from it
                    self.BS_Mute_All([obj], "True")
                    shape.mute = False
                    obj.active_shape_key_index = j
                    bpy.ops.object.shape_key_add(from_mix=True)
                    
                    # Delete current Key
                    obj.active_shape_key_index = j
                    bpy.ops.object.shape_key_remove(all=False)
                    
                    # Rename BS
                    obj.data.shape_keys.key_blocks[-1].name = BSname
                    
                    # Reload and resave visibility
                    self.BS_Recall_Visibility(obj, BS_Store)
                    
                else:
                    #iterate j only if current BS is not deleted
                    print ("BS", BSname,"is ignored")
                    j+=1
          
            obj.show_only_shape_key = False
            self.BS_Update_Drivers([obj])


    def BS_Rebase(self,obj,rebase):
        """
        Rebase all shapes on the "rebase" one.
        """

        shapes = obj.data.shape_keys.key_blocks
        BSCount = len(shapes)
        
        try:
            drivers = obj.data.shape_keys.animation_data.drivers
                
            # Mute every driver
            for driver in drivers:
                driver.mute = True
        except:
            drivers = None       
        
        j=1
        for i in range (1,BSCount):
            
            name = shapes[j].name
            
            # Put every BS to 0 except the current one and the base
            if shapes[j].name == rebase:
                j += 1
                continue
            else:
                for shape in shapes:
                    if (shape.name == rebase) or shape.name == shapes[j].name:
                        shape.value = 1.
                    else:
                        shape.value = 0.
                    
            # Create a new shape from mix
            bpy.ops.object.shape_key_add(from_mix=True)
            
            # Delete current Key
            obj.active_shape_key_index = j
            bpy.ops.object.shape_key_remove(all=False)
            
            # Rename new shape
            shapes[-1].name = name
            
        # UnMute every driver
        if drivers is not None:
            for driver in obj.data.shape_keys.animation_data.drivers:
                driver.mute = False  
        
        self.BS_Update_Drivers([obj])
                
        # TODO: change shape dependancy
                
    @staticmethod
    def BS_Copy_Blank(source):
        """
        Create Empty Blendshapes named as thoses in source object
        """
        
        target = bpy.context.object
        
        for shape in source.data.shape_keys.key_blocks:
            bpy.ops.object.shape_key_add(from_mix=True)
            target.data.shape_keys.key_blocks[-1].name = shape.name
        
### Operators ###################################################

def BS_Op_Poll():  
    try:
        obj = bpy.context.object
        shapes = obj.data.shape_keys.key_blocks
    except:
        return False
    return True


class BST_OT_shape_keys_mute(bpy.types.Operator, BSTools):

    bl_idname = "bst.mute_shape_keys"
    bl_label = "Mute/Unmute Shape Keys"
    
    mute : bpy.props.StringProperty() = "False"

    @classmethod
    def poll(cls, context): 
        return BS_Op_Poll()

    def execute(self, context):
        
        obj = bpy.context.object
        #    self.report({'ERROR'}, "Active object doesn't have shape keys !")
        self.BS_Mute_All([obj], self.mute)

        return {'FINISHED'}
    
class BST_OT_shape_keys_mirror_all(bpy.types.Operator, BSTools):

    bl_idname = "bst.mirror_all_shape_keys"
    bl_label = "Mirror all unmute Shape Keys"
    
    topology : bpy.props.BoolProperty() = True

    @classmethod
    def poll(cls, context):
        return BS_Op_Poll()

    def execute(self, context):
        
        obj = bpy.context.object
        self.BS_Mirror_All([obj], self.topology)

        return {'FINISHED'}
    
class BST_OT_shape_keys_mirror_duplicate(bpy.types.Operator, BSTools):

    bl_idname = "bst.shape_key_mirror_duplicate"
    bl_label = "Mirror duplicate active shape"
    
    topology : bpy.props.BoolProperty() = True

    @classmethod
    def poll(cls, context):
        return BS_Op_Poll()

    def execute(self, context):
        obj = bpy.context.object
        self.BS_Mirror_Copy(obj,self.topology)

        return {'FINISHED'}
    
class BST_OT_shape_keys_bake(bpy.types.Operator, BSTools):

    bl_idname = "bst.shape_keys_bake"
    bl_label = "Bake shape keys"
    
    @classmethod
    def poll(cls, context):
        return BS_Op_Poll()

    def execute(self, context):
        obj = bpy.context.object
        self.BS_Bake([obj])

        return {'FINISHED'}
    
class BST_OT_shape_keys_rebase(bpy.types.Operator, BSTools):

    bl_idname = "bst.shape_keys_rebase"
    bl_label = "Rebase shape keys"
    
    @classmethod
    def poll(cls, context):
        return BS_Op_Poll()

    def execute(self, context):
        obj = bpy.context.object
        self.BS_Rebase(obj, obj.active_shape_key.name)

        return {'FINISHED'}

  
class BST_OT_shape_keys_update_drivers(bpy.types.Operator, BSTools):

    bl_idname = "bst.shape_keys_update_drivers"
    bl_label = "Update drivers"
    
    @classmethod
    def poll(cls, context):
        if BS_Op_Poll:
            try:
                drivers = bpy.context.object.data.shape_keys.animation_data.drivers
            except:
                return False
        else:
            return False
        
        return True

    def execute(self, context):
        obj = bpy.context.object
        self.BS_Update_Drivers([obj])
        
        return {'FINISHED'}


class BST_OT_shape_keys_update_drivers(bpy.types.Operator, BSTools):

    bl_idname = "bst.shape_keys_update_drivers"
    bl_label = "Update drivers"
    
    @classmethod
    def poll(cls, context):
        if BS_Op_Poll:
            try:
                drivers = bpy.context.object.data.shape_keys.animation_data.drivers
            except:
                return False
        else:
            return False
        
        return True

    def execute(self, context):
        obj = bpy.context.object
        self.BS_Update_Drivers([obj])
        
        return {'FINISHED'}
    
class BST_OT_shape_keys_copy_blanks(bpy.types.Operator, BSTools):

    bl_idname = "bst.shape_keys_copy_shapes_blanks"
    bl_label = "Copy shapes as blanks"
    
    @classmethod
    def poll(cls, context):
        selection = bpy.context.selected_objects
        if len(selection) == 2:
            for obj in selection:
                if obj.type == 'MESH':
                    return True
        return False

    def execute(self, context):
        selection = bpy.context.selected_objects
        selection.remove(bpy.context.object)
        source = selection[0]
        try:
            shapes = source.data.shape_keys.key_blocks
        except:
            self.report({'ERROR'}, "Source has no shape keys")
            return {'CANCELLED'}

        self.BS_Copy_Blank(source)
        
        return {'FINISHED'}


### UI ###################################################

class BST_mute_SubMenu(bpy.types.Menu):
    bl_idname = "OBJECT_MT_mute_submenu"
    bl_label = "Mute/Unmute"

    def draw(self, context):
        layout = self.layout
        
        layout.operator("bst.mute_shape_keys",
                    text='Mute all',
                    icon='HIDE_ON').mute = "True"
        layout.operator("bst.mute_shape_keys",
                    text='Unmute all',
                    icon='HIDE_OFF').mute = "False"
        layout.operator("bst.mute_shape_keys",
                    text='Swap Mute',
                    icon='FILE_REFRESH').mute = "Swap"

class BST_mirror_SubMenu(bpy.types.Menu):
    bl_idname = "OBJECT_MT_mirror_submenu"
    bl_label = "Mute/Unmute"

    def draw(self, context):
        layout = self.layout
        
        layout.operator("bst.mirror_all_shape_keys",
                    text='Mirror all unmuted shape keys',
                    icon='ARROW_LEFTRIGHT').topology = False
        layout.operator("bst.mirror_all_shape_keys",
                    text='Mirror all unmuted shape keys (topology)',
                    icon='ARROW_LEFTRIGHT').topology = True
        layout.operator("bst.shape_key_mirror_duplicate",
                    text='Duplicate and mirror active shape',
                    icon='CENTER_ONLY').topology = False
        layout.operator("bst.shape_key_mirror_duplicate",
                    text='Duplicate and mirror active shape (topology)',
                    icon='IMPORT').topology = True
                    
class BST_bake_SubMenu(bpy.types.Menu):
    bl_idname = "OBJECT_MT_bake_submenu"
    bl_label = "Bake"

    def draw(self, context):
        layout = self.layout
        
        layout.operator("bst.shape_keys_bake",
                    text='Bake shape keys',
                    icon='SHADERFX')
        layout.operator("bst.shape_keys_rebase",
                    text='Rebase all shape keys',
                    icon='IMPORT')
        layout.operator("bst.shape_keys_update_drivers",
                    text='Update shapes drivers',
                    icon='DRIVER')


def BST_draw(self, context):
    layout = self.layout
    
    layout.menu(BST_mute_SubMenu.bl_idname, text='Mute/Unmute', icon='HIDE_OFF')
    layout.menu(BST_mirror_SubMenu.bl_idname, text='Mirror', icon='ARROW_LEFTRIGHT')
    layout.menu(BST_bake_SubMenu.bl_idname, text='Baking and Rebase', icon='SHADERFX')
    
    layout.operator("bst.shape_keys_copy_shapes_blanks",
    text='Copy shapes as Blanks',
    icon='COPYDOWN')


# Registration
classes = (
    BST_OT_shape_keys_mute,
    BST_OT_shape_keys_mirror_all,
    BST_OT_shape_keys_mirror_duplicate,
    BST_OT_shape_keys_bake,
    BST_OT_shape_keys_rebase,
    BST_OT_shape_keys_update_drivers,
    BST_OT_shape_keys_copy_blanks,
    BST_mute_SubMenu,
    BST_mirror_SubMenu,
    BST_bake_SubMenu
    )

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.MESH_MT_shape_key_context_menu.append(BST_draw)

def unregister():
    bpy.types.MESH_MT_shape_key_context_menu.remove(BST_draw)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == '__main__':
    try:
        bpy.types.MESH_MT_shape_key_context_menu.remove(BST_draw)
    except:
        pass
    register()