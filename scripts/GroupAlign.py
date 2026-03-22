"""
This script creates a parent group to each object in the selection.
Usage:
    select one or more object and run the script.
"""
__author__ = "Rémi CUXAC"

from maya import cmds


def group(obj_list: list):
    if not obj_list:
        cmds.group(name="grp_01", empty=True)
        return
    for obj in obj_list:
        obj_name = obj.split("|")[-1]
        parent = cmds.listRelatives(obj, parent=True, fullPath=True)
        group_obj = cmds.group(empty=True)
        cmds.matchTransform(group_obj, obj)
        cmds.parent(obj, group_obj)
        if parent:
            cmds.parent(group_obj, parent[0])
        cmds.rename(group_obj, f"grp_{obj_name}")


sel = cmds.ls(sl=1, long=True)
sel.sort(key=lambda x: x.count("|"), reverse=True)
group(sel)
