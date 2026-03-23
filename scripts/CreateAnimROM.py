"""
This script allows user to create a range of motion on a selected joint and its hierarchy.
Usage:
    Select one joint and run the script.
"""
__author__ = "Rémi CUXAC"

import maya.cmds as cmds


def key_rotate(obj: str):
    cmds.setKeyframe(obj, attribute='rotateX', t=cmds.currentTime(query=True))
    cmds.setKeyframe(obj, attribute='rotateY', t=cmds.currentTime(query=True))
    cmds.setKeyframe(obj, attribute='rotateZ', t=cmds.currentTime(query=True))


def get_rotations(axis):
    rot_x = [(90, 0, 0), (-180, 0, 0), (90, 0, 0)]
    rot_y = [(0, 90, 0), (0, -180, 0), (0, 90, 0)]
    rot_z = [(0, 0, 90), (0, 0, -180), (0, 0, 90)]
    if axis == "X":
        return rot_x
    elif axis == "Y":
        return rot_y
    elif axis == "Z":
        return rot_z
    return None


def create_range_of_motion(joint_list: list, step: int = 5):
    cmds.refresh(suspend=True)
    try:
        cmds.undoInfo(openChunk=True, chunkName="ROM")
        for joint in joint_list:
            # Apply the keyframe and store the current rotation
            key_rotate(joint)
            # Iterate through each axis and set the keyframes for the bone
            for axis in ['X', 'Y', 'Z']:
                rotations = get_rotations(axis)
                for rotation in rotations:
                    cmds.currentTime(cmds.currentTime(query=True) + step)
                    cmds.rotate(rotation[0], rotation[1], rotation[2], joint, relative=True, componentSpace=True)
                    key_rotate(joint)
        cmds.undoInfo(closeChunk=True)
    except Exception as e:
        last_undo = cmds.undoInfo(query=True, undoName=True)
        if last_undo == "ROM":
            cmds.undo()
        cmds.warning(str(e))
    cmds.refresh(suspend=False)
    cmds.currentTime(cmds.currentTime(query=True))


sel = cmds.ls(sl=1, type="joint", l=True)
create_range_of_motion(sel) if sel else cmds.warning("Please select at least one joint of your skeleton.")
