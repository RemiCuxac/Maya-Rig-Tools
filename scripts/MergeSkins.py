import maya.cmds as cmds


def get_skin_cluster(pGeo) -> str:
    skin = cmds.ls(cmds.listHistory(pGeo), type='skinCluster')
    return skin


def get_weights(pGeo, pSkinCluster) -> dict:
    joints = cmds.skinCluster(pSkinCluster, query=True, influence=True)
    vertices = cmds.ls(f"{pGeo}.vtx[*]", flatten=True)
    weightsDict = {}
    for v in vertices:
        if v not in weightsDict:
            weightsDict[v] = {}

        weight = cmds.skinPercent(pSkinCluster, v, query=True, value=True)
        for i, jnt in enumerate(joints):
            if jnt in weightsDict[v]:
                weightsDict[v][jnt].append(weight[i])
            else:
                weightsDict[v][jnt] = [weight[i]]
    return weightsDict


def merge_skins(*args) -> dict:
    mergedDict = {}
    for skinDict in args:
        print(skinDict)
        for key, item in skinDict.items():
            if key not in mergedDict:
                mergedDict[key] = item
            else:
                for k, i in item.items():
                    if k not in mergedDict:
                        mergedDict[key][k] = i
                    else:
                        mergedDict[key][k] += i

    # Normalize the weights for each vertex
    for v, inf in mergedDict.items():
        total_weight = sum([sum(w) for w in inf.values()])
        if total_weight > 0:
            for jnt, weight in inf.items():
                mergedDict[v][jnt] = [w / total_weight for w in weight]
    print(mergedDict)
    return mergedDict


def apply_skin_weights(pGeo, pSkinDict):
    all_joints = set(jnt for vtx_data in pSkinDict.values() for jnt in vtx_data)
    skin_cluster = get_skin_cluster(pGeo)

    # Bind geometry with joints
    if not skin_cluster:
        skin_cluster = cmds.skinCluster(list(all_joints), pGeo, toSelectedBones=True)[0]
    else:
        skin_cluster = skin_cluster[0]

    for vtx, weights in pSkinDict.items():
        for jnt, weight in weights.items():
            vtx = pGeo + ".vtx" + vtx.split("vtx")[-1]
            cmds.skinPercent(skin_cluster, vtx, transformValue=(jnt, weight[0]))


def copy_merge_skin(*args):
    assert 1 <= len(args) <= 2, "Please select one or two geometry"
    source = args[0]
    target = args[1] if len(args) == 2 else source
    skinClusters = get_skin_cluster(source)
    if not skinClusters:
        return
    listSkins = []
    for skin in skinClusters:
        weightDict = get_weights(source, skin)
        listSkins.append(weightDict)
    outDict = merge_skins(*listSkins)

    apply_skin_weights(target, outDict)


sel = cmds.ls(sl=1)
copy_merge_skin(*sel)