from enum import Enum

from maya import cmds


class Color(tuple, Enum):
    red=(True, 13)
    white=(True, 16)
    yellow=(True, 17)
    blue=(True, 18)
    pink=(True, 20)
    green=(True, 27)
    default=(False, 0)


def color_obj(pObjList: list, pColor: Color):
    for obj in pObjList:
        objType = cmds.objectType(obj)
        if objType == "joint":
            cmds.setAttr(obj + ".overrideEnabled", pColor[0])
            cmds.setAttr(obj + ".overrideColor", pColor[1])
        else:
            objShape = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
            for shape in objShape:
                cmds.setAttr(shape + ".overrideEnabled", pColor[0])
                cmds.setAttr(shape + ".overrideColor", pColor[1])

sel = cmds.ls(sl=True)
color_obj(sel, Color.red) if sel else cmds.error("Please select a nurbsCurve or a joint.", n=True)
