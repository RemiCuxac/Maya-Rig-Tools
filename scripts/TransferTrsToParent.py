"""
This script transfer any translation / rotation / scale to the parent group if a parent group is found.
Usage:
    select the controller you want to reset transforms, and run the script.
"""
__author__ = "Rémi CUXAC"

from maya import cmds


def transfer_transforms_to_parent(pObjList: list):
    for obj in pObjList:
        parent = cmds.listRelatives(obj, parent=True)
        if parent:
            if cmds.objectType(parent) == "transform" and len(cmds.listRelatives(parent, shapes=True) or []) == 0:
                cmds.matchTransform(parent, obj)
                cmds.matchTransform(obj, parent)


sel = cmds.ls(sl=True, long=True, type="transform")
transfer_transforms_to_parent(sel) if sel else cmds.error("Please select an object", n=True)
