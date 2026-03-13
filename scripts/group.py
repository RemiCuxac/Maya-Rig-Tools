from maya import cmds


def group(pObjList: list):
    if not pObjList:
        cmds.group(n="grp_01", empty=True)
        return
    for obj in pObjList:
        objName = obj.split("|")[-1]
        parent = cmds.listRelatives(obj, parent=True, fullPath=True)
        group = cmds.group(empty=True)
        cmds.matchTransform(group, obj)
        cmds.parent(obj, group)
        if parent:
            cmds.parent(group, parent)
        cmds.rename(group, f"grp_{objName}")


sel = cmds.ls(sl=1, long=True)
sel.sort(key=lambda x: x.count("|"), reverse=True)
group(sel)
