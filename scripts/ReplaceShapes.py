"""
This script is used to replace shapes. The first curve selected will replace the second one.
This script isn't compatible for constraints and other connections. It just parent things and rename.
"""
import maya.cmds as cmds

sel = cmds.ls(sl=1)
alert = lambda : cmds.confirmDialog(title='Error:', message="Please select two curves.", button=["Confirm"])
if len(sel) != 2:
    alert()
else:
    source = sel[0]
    target = sel[1]
    if any(cmds.listRelatives(obj, shapes=True) is None for obj in [source, target]):
        alert()
    else:
        sourceShapes = cmds.listRelatives(source, shapes=True, fullPath=True)
        targetShapes = cmds.listRelatives(target, shapes=True, fullPath=True)
        for shape in sourceShapes:
            cmds.parent(shape, target, r=True, s=True)
        for shape in targetShapes:
            cmds.delete(shape)
        if not cmds.listRelatives(source, allDescendents=True, type="transform"):
            cmds.delete(source)
        cmds.select(None)