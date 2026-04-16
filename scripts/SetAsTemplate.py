"""
This script set any object as "template", so it makes the object visible but non-selectable.
It's useful for controllers of face rig.
Usage:
    Select any transform (curve, geo, joint, whatever) and run the script.
"""

__author__ = "Rémi CUXAC"

from maya import cmds


def template_obj(obj_list: list):
    for obj in obj_list:
        obj_shape = cmds.listRelatives(obj, shapes=True, fullPath=True) or [obj]
        for shape in obj_shape:
            template_state = cmds.getAttr(shape + ".template")
            cmds.setAttr(shape + ".template", 1 - template_state)


sel = cmds.ls(sl=1)
template_obj(sel) if sel else cmds.error("Please select at least one nurbsCurve", n=True)
