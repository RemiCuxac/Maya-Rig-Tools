from maya import cmds


def extract_joint(pObjList: list):
    for obj in pObjList:
        objName = obj.split("|")[-1] if "|" in obj else obj
        newObj = cmds.duplicate(obj, parentOnly=True)[0]
        parent = cmds.listRelatives(obj, parent=True)
        if parent:
            cmds.parent(newObj, world=True)
        radius = cmds.getAttr(f"{obj}.radius")
        cmds.setAttr(f"{newObj}.radius", radius + 1)
        cmds.rename(newObj, f"{objName}_to_rename")


sel = cmds.ls(sl=1, type="joint")
extract_joint(sel) if sel else cmds.warning("Please select a joint from your skeleton", n=True)
