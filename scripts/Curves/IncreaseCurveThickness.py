"""
This script increases the thickness of a selected curve.
Usage:
    Select the curve transform and run the script.
"""
__author__ = "Rémi CUXAC"

from maya import cmds


def change_curve_thickness(curve_list: list, increase: bool = True):
    for crv in curve_list:
        shapeList = cmds.listRelatives(crv, shapes=True, fullPath=True)
        for shape in shapeList:
            if cmds.objectType(shape, isType="nurbsCurve"):
                width = cmds.getAttr(f"{shape}.lineWidth")
                if increase:
                    width += 3 if width < 1 else 1
                else:
                    width -= 1
                cmds.setAttr(f"{shape}.lineWidth", width)


sel = cmds.ls(sl=True, type="transform", long=True)
change_curve_thickness(sel, True) if sel else cmds.error("Please select at least one curve", n=True)
