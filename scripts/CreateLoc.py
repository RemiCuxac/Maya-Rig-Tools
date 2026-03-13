from maya import cmds


def create_loc_from_gizmo(pObjList: list):
    prevObjName = ""
    if not pObjList:
        obj = cmds.spaceLocator(name = "locator_01")
        return
    for obj in pObjList:
        objName = obj.split('|')[-1].split('.')[0]
        mat = cmds.xform(obj, q=True, ws=True, m=True)
        pos = cmds.manipMoveContext("Move", q=True, p=True)
        if objName == prevObjName:
            continue
        prevObjName = objName
        obj = cmds.spaceLocator(name=f"locator_{objName}")
        cmds.setToolTo("moveSuperContext")
        cmds.xform(obj, ws=True, m=mat)
        cmds.xform(obj, ws=True, translation=pos)


sel = cmds.ls(sl=1)
create_loc_from_gizmo(sel)
