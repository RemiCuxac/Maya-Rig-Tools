"""
This script performs a "go to bind pose" from any kind of object.
So you can select a controller, a joint, a geo, and it will apply the right bind pose from the joint that is at end of chain.
Usage:
    Select a controller / joint / geo and execute the script.
"""
__author__ = "Rémi CUXAC"

import math

from maya import cmds
from maya.api import OpenMaya as om


def get_bind_mat(obj):
    if cmds.objectType(obj) == "joint":
        # TODO: use cmds.deformableShape() instead of cmds.listConnections) ?
        skin_list = list(set(cmds.ls(cmds.listConnections(f"{obj}.worldMatrix[0]", type="skinCluster", p=True))))
        if skin_list:
            bind_pre_mat = cmds.getAttr(skin_list[0].replace("matrix", "bindPreMatrix"))
            return om.MMatrix(bind_pre_mat).inverse()
    return None


def go_to_bind_pose(obj):
    if cmds.objectType(obj, isType="joint"):
        target_mat = get_bind_mat(obj)
        constraint_type = None
    else:
        # Controller case - find driven joint
        joint = cmds.ls(cmds.listHistory(obj, future=True, leaf=False), type="joint")[:1]
        if not joint:
            return
        bind_mat = get_bind_mat(joint)
        if not bind_mat:
            return

        constraints = cmds.listConnections(joint, type="constraint", source=True, destination=False) or []
        constraint_type = cmds.nodeType(constraints[0]) if constraints else None

        # Calculate offset and target
        joint_mat = om.MMatrix(cmds.xform(joint, q=True, ws=True, m=True))
        control_mat = om.MMatrix(cmds.xform(obj, q=True, ws=True, m=True))
        target_mat = (control_mat * joint_mat.inverse()) * bind_mat

    if not target_mat:
        return

    # Extract transforms
    mat = om.MTransformationMatrix(target_mat)
    trans = mat.translation(om.MSpace.kWorld)
    rot = mat.rotation().reorder(cmds.getAttr(f"{obj}.rotateOrder"))
    scale = mat.scale(om.MSpace.kWorld)

    # Apply based on constraint type
    if constraint_type == 'orientConstraint':
        cmds.xform(obj, ws=True, ro=[math.degrees(angle) for angle in rot])
    elif constraint_type == 'pointConstraint':
        cmds.xform(obj, ws=True, t=trans)
    else:
        cmds.xform(obj, ws=True, t=trans, ro=[math.degrees(angle) for angle in rot], s=scale)


def process_bind_pose(obj_list: list):
    for obj in obj_list:
        if cmds.objectType(obj, isType="joint"):
            # Process from parent to child
            hierarchy = [obj] + (cmds.listRelatives(obj, allDescendents=True, fullPath=True, type="joint") or [])
            hierarchy.sort(key=len)
            for jnt in hierarchy:
                go_to_bind_pose(jnt)
        elif cmds.objectType(obj, isType="transform"):
            shape = cmds.listRelatives(obj, shapes=True, noIntermediate=True)
            if cmds.objectType(shape) == "mesh":  # process for geos
                skin = cmds.listConnections(shape, type="skinCluster")
                dag_pose = cmds.listConnections(skin, type="dagPose")
                cmds.dagPose(obj, dag_pose, r=True, g=True)
            elif cmds.objectType(shape) == "nurbsCurve":  # process for controllers
                go_to_bind_pose(obj)


sel = cmds.ls(sl=1, long=True)
process_bind_pose(sel)
