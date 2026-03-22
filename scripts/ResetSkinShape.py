from maya import cmds

def reset_skin_pose():
    skinList = []
    for obj in sel:
        history = cmds.listHistory(obj, future=True) if cmds.objectType(obj, isType="joint") else cmds.listHistory(obj)
        skinList = cmds.ls(history, type="skinCluster")
        for skin in skinList:
            plugs = cmds.listAttr(f"{skin}.matrix", multi=True) or []
            indices = [int(p.split('[')[-1][:-1]) for p in plugs]
            for i in indices:
                bindedJoint = cmds.listConnections(skin + '.matrix[' + str(i) + ']', destination=False)[0]
                wInvMtx = cmds.getAttr(bindedJoint + '.worldInverseMatrix')
                cmds.setAttr(skin + '.bindPreMatrix[' + str(i) + ']', wInvMtx, type='matrix')
    if skinList:
        cmds.inViewMessage( amg='<hl>Done !</hl>.', pos='botCenter', fade=True)

def reset_bind_pose():
    dagPoses = cmds.ls(type="dagPose")
    cmds.delete(dagPoses)
    cmds.dagPose(cmds.ls(type="joint"), s=True, bp=True)

sel = cmds.ls(sl=True, type="transform")
if sel:
    reset_skin_pose()
    reset_bind_pose()
else:
    cmds.error("Please selet at least one skinned object.", n=True)
