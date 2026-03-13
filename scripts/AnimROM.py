import maya.cmds as cmds


def key_rotate(pBone: str):
    cmds.setKeyframe(pBone, attribute='rotateX', t=cmds.currentTime(query=True))
    cmds.setKeyframe(pBone, attribute='rotateY', t=cmds.currentTime(query=True))
    cmds.setKeyframe(pBone, attribute='rotateZ', t=cmds.currentTime(query=True))


def get_rotations(axis):
    lRotationX = [(90, 0, 0), (-180, 0, 0), (90, 0, 0)]
    lRotationY = [(0, 90, 0), (0, -180, 0), (0, 90, 0)]
    lRotationZ = [(0, 0, 90), (0, 0, -180), (0, 0, 90)]

    if axis == "X":
        return lRotationX
    elif axis == "Y":
        return lRotationY
    elif axis == "Z":
        return lRotationZ
    return None


def process_all_bones(pBone: str):
    # Apply the keyframe and store the current rotation
    key_rotate(pBone)

    # Iterate through each axis and set the keyframes for the bone
    for axis in ['X', 'Y', 'Z']:
        rotations = get_rotations(axis)
        for rotation in rotations:
            cmds.currentTime(cmds.currentTime(query=True) + 1)
            cmds.rotate(rotation[0], rotation[1], rotation[2], pBone, relative=True, componentSpace=True)
            key_rotate(pBone)

    # Recursively process all child bones
    children = cmds.listRelatives(pBone, children=True, fullPath=True) or []
    for child in children:
        process_all_bones(child)


# Call the process_all_bones function for each root joint in the scene
root_joints = cmds.ls(sl=1, type="joint", l=True)
if len(root_joints) > 2:
    cmds.error("Maybe you have selected more than a root, please proceed one root at time to avoid long calculation", n=True)
elif not root_joints:
    cmds.error("Please select a joint of your skeleton.", n=True)
else:
    cmds.currentUnit(time="6fps")
    cmds.refresh(suspend=True)
    for joint in root_joints:
        process_all_bones(joint)
    current_frame = cmds.currentTime(query=True)
    cmds.playbackOptions(maxTime=current_frame, animationEndTime=current_frame)
    cmds.currentUnit(time="30fps")
    cmds.refresh(suspend=False)
