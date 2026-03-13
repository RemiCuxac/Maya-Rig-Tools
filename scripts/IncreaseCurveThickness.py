from maya import cmds


def increase_line_width(pObjList: list):
    for obj in pObjList:
        shapeList = cmds.listRelatives(obj, shapes=True, fullPath=True)
        for shape in shapeList:
            if cmds.objectType(shape, isType="nurbsCurve"):
                width = cmds.getAttr(f"{shape}.lineWidth") + 1 or 2
                cmds.setAttr(f"{shape}.lineWidth", width)


sel = cmds.ls(sl=True, type="transform", long=True)
increase_line_width(sel) if sel else cmds.error("Please select at least one curve", n=True)
