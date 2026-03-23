"""
This script set any curve object as "template", so it makes the curve visible but non-selectable.
It's useful for controllers of face rig.
Usage:
    Select any curve transform and run the script.
"""

__author__ = "Rémi CUXAC"

from maya import cmds


def template_obj(pObjList: list):
    for obj in pObjList:
        objShape = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
        for shape in objShape:
            templateState = cmds.getAttr(shape + ".template")
            cmds.setAttr(shape + ".template", 1 - templateState)


sel = cmds.ls(sl=1)
template_obj(sel) if sel else cmds.error("Please select at least one nurbsCurve", n=True)
