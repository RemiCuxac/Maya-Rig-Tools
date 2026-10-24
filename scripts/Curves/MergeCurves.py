"""
This script combine multiple curves into one.
Usage:
    select any amount of curve transform and run the script.
"""
__author__ = "Remi CUXAC"

from maya import cmds


def merge_curves(pObjList: list):
    dest = pObjList[-1]
    for obj in pObjList[:-1]:
        shapeList = cmds.listRelatives(obj, shapes=True, fullPath=True)
        for shape in shapeList:
            cmds.makeIdentity(obj, apply=True, t=True, r=True, s=True)
            cmds.parent(shape, dest, shape=True, r=True)
        cmds.delete(obj)
    cmds.select(dest)

sel = cmds.ls(sl=1, type="transform")
merge_curves(sel) if (sel and len(sel) >= 2) else cmds.error("Please select at least two curves", n=True)
