from maya import cmds

axis = {13:(1,0,0), 14:(0,1,0), 15:(0,0,1)}
transform = cmds.group(n="lra_01", empty=True)
for color, endPoint in axis.items():
    crv = cmds.curve(d=1, p=[(0,0,0), endPoint])
    shape = cmds.listRelatives(crv, shapes=True)[0]
    cmds.setAttr(f"{shape}.lineWidth", 5)
    cmds.setAttr(f"{shape}.overrideEnabled", 1)
    cmds.setAttr(f"{shape}.overrideColor", color)
    cmds.parent(shape, transform, shape=True, r=True)
    cmds.delete(crv)