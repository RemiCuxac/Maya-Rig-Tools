from maya import cmds

sel= cmds.ls(sl=1, type="transform")

# 1. ----------------- CREATE
for ctrl in sel:
    loc = cmds.spaceLocator(name="piv_" + ctrl)[0]
    cmds.matchTransform(loc, ctrl)
    parent = cmds.listRelatives(ctrl, parent=True)
    if parent:
        cmds.parent(loc, parent[0])
    cmds.connectAttr(f"{loc}.translate", f"{ctrl}.rotatePivot", force=True)
    # cmds.setAttr(f"{loc}.translateX", 3)
    # cmds.setAttr(f"{ctrl}.rotateZ", 30)


# for ctrl in sel:
#     cmds.xform(ctrl, zeroTransformPivots=True)


# 2. ----------------- BAKE
for ctrl in sel:
    mat = cmds.xform(ctrl, m=True, ws=True, q=True)
    bake_loc = cmds.spaceLocator(name="bake" + ctrl)[0]
    cmds.xform(bake_loc, m=mat, ws=True)

    cmds.parentConstraint(ctrl, bake_loc, maintainOffset=True)

    cmds.bakeResults(bake_loc, t=(0, 50), sb=1)
    cmds.delete(bake_loc, constraints=True)
    cmds.disconnectAttr(f"{loc}.translate", f"{ctrl}.rotatePivot")
    
    cmds.xform(ctrl, m=mat, zeroTransformPivots=True)
    cmds.parentConstraint(bake_loc, ctrl, maintainOffset=False)
    cmds.bakeResults(ctrl, t=(0, 50), sb=1)
    cmds.delete(ctrl, constraints=True)
    cmds.delete(bake_loc, loc)
    
