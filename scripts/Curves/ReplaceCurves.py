"""
This script helps to replace any curve by another one, without breaking connections on the source.
Usage:
    select the curve you want to be replaced, then the curve you want to replace from, and run the script.
"""
__author__ = "Rémi CUXAC"

import maya.cmds as cmds

alert = lambda: cmds.confirmDialog(title='Error:', message="Please select two curves.", button=["Confirm"])


def replace_curves(curve_list: list):
    if len(curve_list) != 2:
        alert()
        return
    source = curve_list[0]
    target = curve_list[1]
    if any(cmds.listRelatives(obj, shapes=True) is None for obj in [source, target]):
        alert()
        return
    sourceShapes = cmds.listRelatives(source, shapes=True, fullPath=True)
    targetShapes = cmds.listRelatives(target, shapes=True, fullPath=True)
    for shape in sourceShapes:
        cmds.parent(shape, target, r=True, s=True)
    for shape in targetShapes:
        cmds.delete(shape)
    if not cmds.listRelatives(source, allDescendents=True, type="transform"):
        cmds.delete(source)
    cmds.select(None)


sel = cmds.ls(sl=1)
replace_curves(sel)
