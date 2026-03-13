from maya import cmds

def get_joints():
    sel = cmds.ls(sl=1)
    return cmds.listRelatives(sel, children=True, allDescendents=True, type="joint") + sel

def disable_constraints():
    jointList = get_joints()
    cmds.select(jointList)
    cmds.setKeyframe()
    for joint in jointList:
        if cmds.attributeQuery("blendParent1", n=joint, exists=True):
            cmds.setAttr(f"{joint}.blendParent1", 0)

def enable_constraints():
    jointList = get_joints()
    for joint in jointList:
        if cmds.attributeQuery("blendParent1", n=joint, exists=True):
            cmds.setAttr(f"{joint}.blendParent1", 1)

disable_constraints()
# enable_constraints()