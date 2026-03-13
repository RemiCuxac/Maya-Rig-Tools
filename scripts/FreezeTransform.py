import maya.api.OpenMaya as om
from maya import cmds


def freeze_transform(pObjList: list):
    for obj in pObjList:
        if cmds.objectType(obj) == "joint":
            # rotation
            mat = cmds.xform(obj, q=True, m=True)
            m = om.MMatrix(mat)
            mt = om.MTransformationMatrix(m)
            rot = mt.rotation()
            rotRad = (rot.x, rot.y, rot.z)
            rotDeg = [om.MAngle(angle).asDegrees() for angle in rotRad]
            cmds.setAttr(f"{obj}.rotate", 0, 0, 0)
            cmds.setAttr(f"{obj}.jointOrient", *rotDeg)

            # scale
            skin = list(set(cmds.listConnections(obj, d=True, s=False, type="skinCluster")))
            if skin and cmds.getAttr(f"{obj}.scale") != [(1.0, 1.0, 1.0)]:
                cmds.warning(
                    f"Bind Pose has been modified since the scale of {obj} has changed. Please reset skin Bind Pose")
            listChildren = {}
            for child in cmds.listRelatives(obj, fullPath=True, children=True) or []:
                mat = cmds.xform(child, q=True, m=True, ws=True)
                listChildren[child] = mat
            cmds.setAttr(f"{obj}.scale", 1, 1, 1)
            for child in listChildren:
                cmds.xform(child, m=listChildren[child], ws=True)
        else:
            cmds.makeIdentity(obj, apply=True, t=True, r=True, s=True, n=False, pn=True)


sel = cmds.ls(sl=1)
freeze_transform(sel) if sel else cmds.error("Please select an object", n=True)
