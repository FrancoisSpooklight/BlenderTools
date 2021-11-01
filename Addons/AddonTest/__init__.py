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

bl_info = {
    "name": "Test",
    "author": "Gerard Le Normand d'Isere",
    "version": (2, 2, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Shift + Q key",
    "description": "This is a testitouille",
    "warning": "Beta",
    "doc_url": "",
   "category": "Animation"
}


if "bpy" in locals():
    import importlib
    if "tool" in locals():
        importlib.reload(tool)

else:
    from .tool import mathTools

# noinspection PyUnresolvedReferences
import bpy
from bpy.types import Operator

class TST_OT_Add (Operator, mathTools):
    '''
    TEST
    '''

    bl_idname = "test.add"
    bl_label = "Add"

    def execute(self, context):
        print (self.add(1,2))
        return {'FINISHED'}


#Registration
classes = (
    TST_OT_Add
)
def register():
    bpy.utils.register_class(TST_OT_Add)

def unregister():
    bpy.utils.unregister_class(TST_OT_Add)

if __name__ == "__main__":
    register()
