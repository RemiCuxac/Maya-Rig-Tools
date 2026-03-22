from maya import cmds


def template_obj(pObjList: list):
    for obj in pObjList:
        objShape = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
        for shape in objShape:
            templateState = cmds.getAttr(shape + ".template")
            cmds.setAttr(shape + ".template", 1-templateState)


sel = cmds.ls(sl=1)
template_obj(sel) if sel else cmds.error("Please select at least one nurbsCurve", n=True)