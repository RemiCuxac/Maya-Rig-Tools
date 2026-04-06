import maya.api.OpenMaya as om
from maya import cmds


def freeze_transform(obj_list: list):
    for obj in obj_list:
        if cmds.objectType(obj) == "joint":
            # rotation
            mat = cmds.xform(obj, q=True, m=True)
            m = om.MMatrix(mat)
            mt = om.MTransformationMatrix(m)
            rot = mt.rotation()
            rot_rad = (rot.x, rot.y, rot.z)
            rot_deg = [om.MAngle(angle).asDegrees() for angle in rot_rad]
            cmds.setAttr(f"{obj}.rotate", 0, 0, 0)
            cmds.setAttr(f"{obj}.jointOrient", *rot_deg)

            # scale
            skin = list(set(cmds.listConnections(obj, d=True, s=False, type="skinCluster") or []))
            if skin and cmds.getAttr(f"{obj}.scale") != [(1.0, 1.0, 1.0)]:
                cmds.warning(f"Bind Pose has been modified since the scale of {obj} has changed."
                             f"Please reset skin Bind Pose")
            list_children = {}
            for child in cmds.listRelatives(obj, fullPath=True, children=True) or []:
                mat = cmds.xform(child, q=True, m=True, ws=True)
                list_children[child] = mat
            cmds.setAttr(f"{obj}.scale", 1, 1, 1)
            for child in list_children:
                cmds.xform(child, m=list_children[child], ws=True)
        else:
            cmds.makeIdentity(obj, apply=True, t=True, r=True, s=True, n=False, pn=True)


sel = cmds.ls(selection=True)
freeze_transform(sel) if sel else cmds.error("Please select an object", n=True)
