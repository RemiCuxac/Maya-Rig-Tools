import math

from maya import cmds
from maya.api import OpenMaya as om


def get_bind_mat(obj):
    if cmds.objectType(obj) == "joint":
        # TODO: use cmds.deformableShape() instead of cmds.listConnections) ?
        skinList = list(set(cmds.ls(cmds.listConnections(f"{obj}.worldMatrix[0]", type="skinCluster", p=True))))
        if skinList:
            bindPreMat = cmds.getAttr(skinList[0].replace("matrix", "bindPreMatrix"))
            return om.MMatrix(bindPreMat).inverse()
    return None


def go_to_bind_pose(obj):
    isJoint = cmds.objectType(obj, isType="joint")

    if isJoint:
        targetMat = get_bind_mat(obj)
        constraint_type = None
    else:
        # Controller case - find driven joint
        joint = cmds.ls(cmds.listHistory(obj, future=True, leaf=False), type="joint")[:1]
        if not joint:
            return
        bindMat = get_bind_mat(joint)
        if not bindMat:
            return

        constraints = cmds.listConnections(joint, type="constraint", source=True, destination=False) or []
        constraint_type = cmds.nodeType(constraints[0]) if constraints else None

        # Calculate offset and target
        jointMat = om.MMatrix(cmds.xform(joint, q=True, ws=True, m=True))
        controlMat = om.MMatrix(cmds.xform(obj, q=True, ws=True, m=True))
        targetMat = (controlMat * jointMat.inverse()) * bindMat

    if not targetMat:
        return

    # Extract transforms
    mat = om.MTransformationMatrix(targetMat)
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


def process_bind_pose(obj_list:list):
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
                dagPose1 = cmds.listConnections(skin, type="dagPose")
                cmds.dagPose(obj, dagPose1, r=True, g=True)
            elif cmds.objectType(shape) == "nurbsCurve":  # process for controllers
                go_to_bind_pose(obj)

sel = cmds.ls(sl=1, long=True)
process_bind_pose(sel)