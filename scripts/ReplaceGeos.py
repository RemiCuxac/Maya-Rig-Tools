from maya import cmds

sel = cmds.ls(sl=1)
assert len(sel) == 2, "You have to select two objects : source then target."
target = sel[1]
source = sel[0]


def get_shape_orig(transform: str):
    shapeOrig = cmds.deformableShape(transform, originalGeometry=True)
    if shapeOrig != [""]:
        shapeOrig = shapeOrig[0].split(".")[0]
    else:
        shapeOrig = cmds.listRelatives(transform, shapes=True)[0]
    return shapeOrig


targetShape = get_shape_orig(target)
sourceShape = get_shape_orig(source)

cmds.connectAttr(sourceShape + ".outMesh", targetShape + ".inMesh", force=True)