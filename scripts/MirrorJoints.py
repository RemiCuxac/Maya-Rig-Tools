from maya import cmds

leftToRight = {"left": "right", "Left": "Right", "_l_": "_r_", "_L_": "_R_", "_l": "_r", "_L": "_R"}
full_mapping = {**leftToRight, **{v: k for k, v in leftToRight.items()}}


def mirror_joints(pJntList: list):
    for obj in pJntList:
        for key, value in full_mapping.items():
            if obj.count(key) > 1:  # for objets like jnt_leg_l
                # because there is no reverse replace, only replace the last occurrence if True :
                if obj.endswith(key) or obj.startswith(key):
                    if obj.endswith(key):
                        index = obj.count(key) - 1
                    else:
                        index = 1
                    obj = cmds.rename(obj, obj.replace(key, "TEMP", index))
                    mirrored = cmds.mirrorJoint(obj, mirrorYZ=True, mirrorBehavior=True, searchReplace=[key, value])
                    mirrored.reverse()
                    for e in mirrored + [obj]:
                        cmds.rename(e, e.split("|")[-1].replace("TEMP", key))
                else:
                    mirrored = cmds.mirrorJoint(obj, mirrorYZ=True, mirrorBehavior=True, searchReplace=[key, value])
                    cmds.warning(f"Please review naming of {obj} and {', '.join(mirrored)} and his hierarchy")
                break
            elif key in obj:
                cmds.mirrorJoint(obj, mirrorYZ=True, mirrorBehavior=True, searchReplace=[key, value])
                break
        else:
            mirrored = cmds.mirrorJoint(obj, mirrorYZ=True, mirrorBehavior=True, searchReplace=[key, value])
            cmds.warning(f"Please review naming of {obj} and {', '.join(mirrored)} and his hierarchy")


sel = cmds.ls(sl=1, type="joint")
mirror_joints(sel) if sel else cmds.error("Please select the root of the chain you want to mirror", n=True)
