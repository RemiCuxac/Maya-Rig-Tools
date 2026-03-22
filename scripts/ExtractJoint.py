"""
This script duplicates the selected joints without the hierarchy and parent unparent it.
Usage:
    select one or more joints and execute the script.
"""
__author__ = "Rémi CUXAC"

from maya import cmds


def extract_joint(joint_list: list):
    for joint in joint_list:
        joint_name = joint.split("|")[-1] if "|" in joint else joint
        new_joint = cmds.duplicate(joint, parentOnly=True)[0]
        parent = cmds.listRelatives(joint, parent=True)
        if parent:
            cmds.parent(new_joint, world=True)
        radius = cmds.getAttr(f"{joint}.radius")
        cmds.setAttr(f"{new_joint}.radius", radius + 1)
        cmds.rename(new_joint, f"{joint_name}_to_rename")


sel = cmds.ls(sl=1, type="joint")
extract_joint(sel) if sel else cmds.warning("Please select a joint from your skeleton", n=True)
