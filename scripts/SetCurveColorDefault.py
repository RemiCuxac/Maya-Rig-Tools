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


def color_obj(obj_list: list, color: Color, color_outliner:bool=True):
    for obj in obj_list:
        obj_type = cmds.objectType(obj)
        if obj_type == "joint":
            sub_obj_list = [obj]
        else:
            sub_obj_list = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
        for sub_obj in sub_obj_list:
            cmds.setAttr(sub_obj + ".overrideEnabled", color[0])
            cmds.setAttr(sub_obj + ".overrideColor", color[1])
        if color_outliner:
            cmds.setAttr(obj + ".useOutlinerColor", False)


sel = cmds.ls(sl=True)
color_obj(sel, Color.DEFAULT) if sel else cmds.error("Please select a nurbsCurve or a joint.", n=True)
