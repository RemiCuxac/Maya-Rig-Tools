from maya import cmds


def group(pObjList: list):
    if not pObjList:
        cmds.group(n="grp_01", empty=True)
        return
    for obj in pObjList:
        objName = obj.split("|")[-1]
        parent = cmds.listRelatives(obj, parent=True, fullPath=True)
        group_obj = cmds.group(empty=True)
        cmds.matchTransform(group_obj, obj)
        cmds.parent(obj, group_obj)
        if parent:
            cmds.parent(group_obj, parent)
        cmds.rename(group_obj, f"grp_{objName}")


sel = cmds.ls(sl=1, long=True)
sel.sort(key=lambda x: x.count("|"), reverse=True)
group(sel)
