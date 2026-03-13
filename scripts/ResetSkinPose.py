from maya import cmds

def reset_skin_pose():
    skinList = []
    for obj in sel:
        history = cmds.listHistory(obj, future=True) if cmds.objectType(obj, isType="joint") else cmds.listHistory(obj)
        skinList = cmds.ls(history, type="skinCluster")
        for skin in skinList:
            nbInfl = len(cmds.listConnections(skin + '.matrix', destination=False))
            offset = 0
            for i in range(nbInfl):
                while not cmds.getAttr(f"{skin}.matrix[{i+offset}]"):
                    offset+=1
                    if offset > 1000:
                        raise Exception("Infinite loop detected, please warn the author of this script")
                i += offset
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
