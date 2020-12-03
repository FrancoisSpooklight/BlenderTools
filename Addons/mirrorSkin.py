#### DANS BLENDER ##### mirrorSkin
#### Mirror les weight d'un skin


import bpy

### Amélioration à apporter:
### Rajouter les try/catch


### Mirror les Skin Weight de l'objet actif. L et R sont les identifiants de latéralité
### Dans les Vertex groups.
def mirrorSkin (_L,_R):

    # ActiveObject
    _selObj = bpy.context.active_object

    # Vertex groups
    _vxGroups = _selObj.vertex_groups
    _vxGroupsList = []
    _vxGroupsListL = []
    _vxGroupsListR = []

    ###################################

    ### Liste le noms des vertex Groups
    for group in _vxGroups :
        try:
            print (group.name)
            _vxGroupsList.append(group.name)
        except:
            pass

    print (_vxGroupsList)  ## Debug

    ### Trie Les vertex Groups de gauche
    for grpName in _vxGroupsList:
        if _L in grpName:
            
            _vxGroupsListL.append(grpName)
            
            #toDel = _vxGroups.get(grpName)
            #_vxGroups.delete(toDel)
         
    ### Trie Les vertex Groups de droite
    for grpName in _vxGroupsList:
        if _R in grpName:
            
            _vxGroupsListR.append(grpName)


    #print ("droite : "+str(_vxGroupsListR)) ## Debug
    #print ("gauche : "+str(_vxGroupsListL)) ## Debug



    ## Supprimme les gauche
    for grpNameL in _vxGroupsListL:
        toDel= _vxGroups.get(grpNameL)
        _vxGroups.remove(toDel)


    for grpNameR in _vxGroupsListR:

        grpNameRId= _vxGroups[grpNameR].index
        grpNameL= ""
        
        #duplicate Droite (R)
        _vxGroups.active_index = grpNameRId
        bpy.ops.object.vertex_group_copy()
        
        #Rename Droite (R) en Gauche (L)
        grpNameL = grpNameR.replace(_R,_L)
        _vxGroups[grpNameR+'_copy'].name = grpNameL
            
        #Mirror
        grpNameLId = _vxGroups[grpNameL].index
        _vxGroups.active_index= grpNameLId
        bpy.ops.object.vertex_group_mirror(flip_group_names=False,use_topology=True)

#to, from
mirrorSkin(".R",".L")
    
    

