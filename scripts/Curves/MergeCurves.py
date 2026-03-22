from maya import cmds


def merge_curves(pObjList: list):
    group = cmds.group(n="mygroup1", empty=True)

    ## To set the pivot to the first selected object, uncomment the following line:
    # cmds.matchTransform(group, pObjList[0], pivots=True)

    for obj in pObjList:
        shapeList = cmds.listRelatives(obj, shapes=True, fullPath=True)
        for shape in shapeList:
            cmds.makeIdentity(obj, apply=True, t=True, r=True, s=True)
            cmds.parent(shape, group, shape=True, r=True)
        cmds.delete(obj)

    ## to move the new group to the center of the world, uncomment the following lines:
    # cmds.move(0, 0, 0,group, rpr=True)
    # cmds.makeIdentity(group, apply=True, t=True, r=True, s=True)

    cmds.delete(group, constructionHistory=True)
    cmds.select(group)
    cmds.rename(group, pObjList[0])


sel = cmds.ls(sl=1, type="transform")
merge_curves(sel) if (sel and len(sel) >= 2) else cmds.error("Please select at least two curves", n=True)
