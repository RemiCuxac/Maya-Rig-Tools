from maya import cmds

sel = cmds.ls(shapes=True)

for shape in sel:
    history = cmds.listHistory(shape, pruneDagObjects=True) or []
    skin_clusters = cmds.ls(history, type="skinCluster")
    if len(skin_clusters) > 1:
        for skin in skin_clusters:
            if cmds.getAttr(f"{skin}.envelope") != 1:
                cmds.delete(skin)
