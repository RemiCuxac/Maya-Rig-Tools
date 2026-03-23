"""
This script applies a color to the selected joint or curve.
Usage:
    select the joint or curve transform and run the script.
"""
__author__ = "Rémi CUXAC"

from enum import Enum

from maya import cmds


class Color(tuple, Enum):
    RED = (True, 13)
    WHITE = (True, 16)
    YELLOW = (True, 17)
    BLUE = (True, 18)
    PINK = (True, 20)
    GREEN = (True, 27)
    DEFAULT = (False, 0)


def color_obj(obj_list: list, color: Color):
    for obj in obj_list:
        objType = cmds.objectType(obj)
        if objType == "joint":
            cmds.setAttr(obj + ".overrideEnabled", color[0])
            cmds.setAttr(obj + ".overrideColor", color[1])
        else:
            objShape = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
            for shape in objShape:
                cmds.setAttr(shape + ".overrideEnabled", color[0])
                cmds.setAttr(shape + ".overrideColor", color[1])


sel = cmds.ls(sl=True)
color_obj(sel, Color.GREEN) if sel else cmds.error("Please select a nurbsCurve or a joint.", n=True)
