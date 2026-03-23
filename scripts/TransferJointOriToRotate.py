"""
This script bakes any joint orient information to the rotation of the joint.
Useful to send an animation to a game engine that deosn't supports joint orients.
Usage:
    select the joint then run the script.
"""
__author__ = "Rémi CUXAC"

import maya.api.OpenMaya as om
from maya import cmds

sel = cmds.ls(sl=1, type="joint")

for jnt in sel:
    # Get parent
    parent = cmds.listRelatives(jnt, parent=True)
    if parent:
        parent_matrix = cmds.getAttr(parent[0] + ".worldMatrix[0]")
        parent_matrix = om.MMatrix(parent_matrix)
        parent_inverse = parent_matrix.inverse()
    else:
        parent_inverse = om.MMatrix()  # identity if no parent

    # Get joint world matrix
    world_matrix = cmds.getAttr(jnt + ".worldMatrix[0]")
    world_matrix = om.MMatrix(world_matrix)

    # Compute local matrix
    local_matrix = world_matrix * parent_inverse

    # Build transformation
    mTransform = om.MTransformationMatrix(local_matrix)

    # Respect joint rotate order
    rot_order = cmds.getAttr(jnt + ".rotateOrder")
    euler_rot = mTransform.rotation(asQuaternion=False)
    euler_rot.reorderIt(rot_order)

    # Convert to degrees
    new_rot = (
        om.MAngle(euler_rot.x).asDegrees(),
        om.MAngle(euler_rot.y).asDegrees(),
        om.MAngle(euler_rot.z).asDegrees()
    )

    # Reset jointOrient
    cmds.setAttr(jnt + ".jointOrient", 0, 0, 0)

    # Apply extracted rotation
    cmds.setAttr(jnt + ".rotate", *new_rot)

cmds.inViewMessage(amg='<hl>Joint orient transferred to rotate.</hl>', pos='botCenter', fade=True)
