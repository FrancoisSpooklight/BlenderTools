##### Spooklight Rigging Pipeline
##### Bones Buffer
## from: Spooklight Studio
## Create bones between bones of a chain to prevent fbx export inheritance issues.

import bpy
from mathutils import Vector
from animTools import apUtilities

bl_info = {
   "name": "Armature Stretcher",
   "author": "Spooklight Studio",
   "version": (1, 0, 0),
   "blender": (2, 78, 0),
   "location": "",
   "description": "Allow Edit of Corpulence",
   "warning": "",
   "wiki_url": "",
   "tracker_url": "",
   "category": "Rigging"}


class rp_Bones_Stretcher:

    def cleanArmature(self, object):

        bpy.ops.object.mode_set(mode = 'POSE')
        for pbone in object.pose.bones:
            for const in pbone.constraints:
                pbone.constraints.remove(const)

        for bone in object.data.bones:
            bone.use_inherit_rotation = False
            bone.use_inherit_scale = False
        bpy.ops.object.mode_set(mode = 'EDIT')


    def rp_createOrthBone(self,bone,child,front,suffix):
        ''' Creation d'un bone orthogonal aux deux bones (bone et child) selon le vecteur front axis'''

        # Création du nouveau bone
        armature = bone.id_data

        # Nouveau nom du buffer : Bone name + _buf + Side
        if bone.name[-2:] == ".R" or bone.name[-2:] == ".L":
            newBoneName = bone.name[:-2] + suffix + bone.name[-2:]
        else:
            newBoneName = bone.name + suffix

        newBone = armature.edit_bones.new(newBoneName)
        
        #Nouvelles coordonées du bones:
        #Le nouveau bone doit être à mi-chemin angulairement entre le bone bone parent et le bone enfant.
        #Il doit donc être orthogonal au vecteur reliant le head du parent et le tail du child.
        #Ce vecteur est la base du triangle dont les deux autres côtés sont le parent et l'enfant. #
        #Notre nouveau vecteur en est la mediatrice de cette base.
        #Pour l'obtenir: childTail- boneHead. On obtient donc un vecteur partant de l'origine.
        #On fait ensuite un produit vectoriel entre ce vecteur et le vecteur de direction pointant en Y (face)
        #On rajoute ensuite un offset pusique la base de ce bone est le head de l'enfant

        boneHead = Vector((bone.head))
        childHead = Vector((child.head))
        childTail = Vector((child.tail))
        bonesComp = childTail - boneHead
  
        newBone.head = childHead
        newBone.tail = bonesComp.cross(front) + childHead
        
        #Fix roll
        newBone.select = True
        bpy.context.object.data.bones.active = bpy.context.object.data.bones[bone.name]
        bpy.ops.armature.calculate_roll(type='ACTIVE')

        return newBone

    def rp_addStretchTarget(self, object, pbones):
        '''
        pbones inpuit is an array made of
        couple of target/stretchable bones
        '''

        bpy.ops.object.mode_set(mode = 'POSE')

        for pbone in pbones:

            tostretch = object.pose.bones.get(pbone[0].name)
    
            const = tostretch.constraints.new('STRETCH_TO')
            const.subtarget = pbone[1].name
            const.target = object

            tostretch.constraints.update()


    def rp_create_Buffers(self,selBones):

        # TODO: A déclarer en tant que variables de classe.
        rp_selBones = selBones
        rp_bonesFamily = []
        rp_frontAxis = Vector((0,0.25,0))

        # couple buffer, child
        out = []

        #Depuis une liste de bones, Créer la liste suivante: [[bone,[enfant,enfant...]],[...])
        for bone in rp_selBones:
            rp_bonesFamily.append([bone,bone.children])
            #Clear Selection:
            bone.select = False


        print (rp_bonesFamily)

        #Crée un bone perpendiculaire par bone
        for bone in rp_bonesFamily:
            # Prendre uniquement le premier child pour ne pas créer
            # plusieurs fois le même buffer.

            #Bone en cours, dont le buffer heritera du nom
            parent = bone[0]

            #Skip bones with no children
            if len(bone[-1]) == 0:
                continue
            else:
                child = bone[-1][0]

            buffer = self.rp_createOrthBone(parent,child,rp_frontAxis,"_buf")

            #child.hide_select = True
            #parent.hide_select = True

            #Prepare return
            out.append((parent, buffer))


        return out

    def getSymetryRef(self, object):
        '''
        get transform unitary vector
        '''

        boneRef = object.pose.bones.get('HLP-Symetry_Ref')

        if boneRef is None:
            return None

        return boneRef.location

    def symetrizePBone(self, pbone, side):
        '''
        found if there is any bone symetrical to pbone and symetrize its location
        '''

        target = pbone

        # Inverse le side
        if side == '.R':
            sym = '.L'
        else:
            sym= '.R'

        # Tente de retrouver le bone source
        source = bpy.context.active_object.pose.bones.get(pbone.name[:-2] + sym)

        # Remap les coordonnées
        #symVec = self.getSymetryRef(bpy.context.object)

        if source is not None:

            newMat = target.matrix.copy()

            newMat[0][3] = source.matrix[0][3] * -1
            newMat[1][3] = source.matrix[1][3]
            newMat[2][3] = source.matrix[2][3]

            target.matrix = newMat
        else:
            print ('No mirror bone')


class rp_Bones_Buffer_Operator(bpy.types.Operator, rp_Bones_Stretcher):
    bl_idname = "rp.bonesbuffer"
    bl_label = "Spooklight Bones Buffer"

    ### Variables 
    rp_bones = []
    
    @classmethod
    def poll(self,context):
        return bpy.context.active_object.mode == 'EDIT'
    
    def execute(self,context):
        
        self.cleanArmature(bpy.context.active_object)
        self.rp_addStretchTarget(bpy.context.object, self.rp_create_Buffers(bpy.context.selected_bones))
        apUtilities.updateScreen()
        return {'FINISHED'}


class symetrizeController(bpy.types.Operator, rp_Bones_Stretcher):
    '''
    symetrize stretch controller on the XZ plane
    '''

    bl_idname = "rp.symetrizecontroller"
    bl_label = "Spooklight Symetrize Controller"


    def execute(self, context):

        pbones = bpy.context.selected_pose_bones

        for pbone in pbones:

            # Si fini par .L ou .R, alors le bone a surement un symetrique
            side = pbone.name[-2:]

            if side == '.L' or side == '.R':
                self.symetrizePBone(pbone, side)
            else:
                print ('Not a Symetric Bone!')

        return {'FINISHED'}


### Operators Registration

def register():
    bpy.utils.register_class(rp_Bones_Buffer_Operator)
    bpy.utils.register_class(symetrizeController)

def unregister():
    bpy.utils.unregister_class(rp_Bones_Buffer_Operator)
    bpy.utils.unregister_class(symetrizeController)


if __name__ == "__main__":
    register()