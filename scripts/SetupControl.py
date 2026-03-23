"""
This script creates a controller, his parent group and the constraint to the selected joint.
Usage:
    Select the joint you want to constrain and setup, then run the script.
"""
__author__ = "Rémi CUXAC"

import maya.cmds as cmds


def create_control(pObjList: list):
    for bone in pObjList:
        parent = cmds.listRelatives(bone, parent=True, type="transform")
        # Create controls and groups
        controlName = bone.replace("jnt", "ctrl").replace("joint", "ctrl")
        controlName = "ctrl_" + controlName if "ctrl_" not in controlName else controlName
        newCtrl = cmds.circle(name=controlName, normal=(1, 0, 0), radius=5)
        newGrp = cmds.group(newCtrl, name=controlName.replace("ctrl", "grp"))
        cmds.matchTransform(newGrp, bone)

        # Create constraint
        cmds.parentConstraint(newCtrl, bone, maintainOffset=True)
        # if parent:
        #     cmds.parentConstraint(parent, newGrp, maintainOffset=True)
    cmds.inViewMessage(amg="<hl>Don't forget to parent newly created groups</hl>.", pos='midCenter', fade=True)


sel = cmds.ls(selection=True)
create_control(sel) if sel else cmds.error("Please select at least one object to control.", n=True)
