import bpy
from mathutils import Vector


bl_info = {
   "name": "catcherGenerator",
   "author": "Spooklight Studio",
   "version": (1, 0, 0),
   "blender": (2, 78, 0),
   "location": "",
   "description": "Generate a rig catcher based on a rigify rig",
   "warning": "",
   "wiki_url": "",
   "tracker_url": "",
   "category": "Rigging"}


class catcherGenerator:

    def collectDefBones(self, rig):
        '''
        Collects all the deformation bose.
        #Assuming the given object is a rigify one
        (tested in the operator class)

        Return an array of objects with these information per elements:
            Bone Name, Head Position, Tail Position, Bone Roll

        '''

        # Variables
        bones = rig.data.edit_bones
        defBones = []

        # Iteration
        bpy.context.scene.objects.active = rig
        bpy.ops.object.mode_set(mode='EDIT')

        for bone in bones:
            if "DEF" in bone.name:
                defBones.append([bone.name, bone.head, bone.tail, bone.roll])

        bpy.ops.object.mode_set(mode='OBJECT')
        
        print ("OUT collect ", defBones)

        return defBones

    def createCatBones(self, rig, defBones):
        '''
        Create a new armature and a corresponding object at (0,0,0)
        Create a bone for each one in the array
        Fits each bone to its heir
        Create a constraint for each new bone fiting its heir.
        '''

        #print ("IN create ", defBones)
        # Create new armature, checking if each component already exists
        if bpy.data.armatures.get('rig_catcher') is None:
            catcherArmature = bpy.data.armatures.new('rig_catcher')
        else:
            catcherArmature = bpy.data.armatures['rig_catcher']

        if bpy.data.objects.get('rig_catcher') is None:
            catcherObject = bpy.data.objects.new('rig_catcher', catcherArmature)
        else:
            catcherObject = bpy.data.objects['rig_catcher']

        if bpy.context.scene.objects.get('rig_catcher') is None:
            bpy.context.scene.objects.link(catcherObject)

        catcher = bpy.context.scene.objects['rig_catcher']
        bpy.context.scene.objects.active = catcher
        bpy.ops.object.mode_set(mode='EDIT')

        # Iteration
        for bone in defBones:

            print (bone)

            # CreateBone
            bpy.ops.object.mode_set(mode='EDIT')
            
            catBone = catcher.data.edit_bones.new('CAT'+bone[0][3:])  # replace "DEF" in name by "CAT"
            catBone.head = bone[1]
            catBone.tail = bone[2]
            catBone.roll = bone[3]

            # Create Constraint
            bpy.ops.object.mode_set(mode='POSE')
            drived = catcher.pose.bones.get(catBone.name)

            constraint = drived.constraints.new('COPY_TRANSFORMS')
            constraint.target = rig
            constraint.subtarget = bone[0]


        return catcher

    def consolidateRig(self, catcher):
        '''
        Parente les bones ayant une tail et un head commun
        '''

        bpy.ops.object.mode_set(mode='EDIT')

        for bone in catcher.data.edit_bones:
            
            # Parente les bones de fin de chaine.
            if "CAT-palm" in bone.name or "CAT-thumb.01" in bone.name and bone.name[-1:] is not "2":
                if ".R" in bone.name:
                    bone.parent = catcher.data.edit_bones.get('CAT-hand.R')
                    continue
                else:
                    bone.parent = catcher.data.edit_bones.get('CAT-hand.L')
                    continue

            if "CAT-thigh.01" in bone.name:
                bone.parent = catcher.data.edit_bones.get('CAT-hips')
                continue

            if "CAT-upper_arm.01.L" in bone.name:
                bone.parent = catcher.data.edit_bones.get('CAT-shoulder.L')
                continue
            if "CAT-upper_arm.01.R" in bone.name:
                bone.parent = catcher.data.edit_bones.get('CAT-shoulder.R')
                continue
            
            if "CAT-shoulder" in bone.name:
                bone.parent = catcher.data.edit_bones.get('CAT-chest')
                continue

            #parente les bones ayant une tail et un head en commun
            for otherBone in catcher.data.edit_bones:
                if bone.head == otherBone.tail:
                    bone.parent = otherBone
                    bone.use_connect = True
                    break
                


class generateCatcherOp(bpy.types.Operator, catcherGenerator):
    bl_idname = 'catcher.generate'
    bl_label = 'Generate Catcher'

    @classmethod
    def poll(self, context):
        return bpy.context.active_object.data.get("rig_id") is not None and context.active_object.mode == 'EDIT'

    def execute(self, context):
        #for i in range(0,3):
        #    print (self.collectDefBones(bpy.context.object))
        
        target = bpy.context.object
        catcher = self.createCatBones(bpy.context.object, self.collectDefBones(bpy.context.object))
        self.consolidateRig(catcher)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(generateCatcherOp)


def unregister():
    bpy.utils.unregister_class(generateCatcherOp)


if __name__ == "__main__":
    register()