"""
This script helps riggers to create a curve between two objects.
It's helpful in particular for IK's pole vector, to visualize from which limb the pole vector is attached.
It will also parent the curve under the first object selected.
Usage:
    Select two transforms or controllers and run the script.
"""
__author__ = "Rémi CUXAC"

from maya import cmds


def create_curve_link_from_controllers(obj_list: list = None, pName: str = None, suffix: str = "_crv_link"):
    if not obj_list or (len(obj_list) == 0 and isinstance(obj_list, list)):
        cmds.warning("Please select two objects first.")
        return
    ctrl1 = obj_list[0]
    ctrl2 = obj_list[1]
    curve1 = cmds.curve(degree=1, p=[(0, 0, 0), (0, 0, 0)])
    cmds.parent(curve1, ctrl1)
    for index, ctrl in enumerate([ctrl1, ctrl2]):
        decompM = cmds.createNode("decomposeMatrix")
        cmds.connectAttr(f"{ctrl}.worldMatrix", f"{decompM}.inputMatrix")
        cmds.connectAttr(f"{decompM}.outputTranslate", f"{curve1}.controlPoints[{index * 2}]")
    cmds.setAttr(f"{curve1}.overrideEnabled", True)
    cmds.setAttr(f"{curve1}.overrideDisplayType", 1)  # template
    cmds.setAttr(f"{curve1}.inheritsTransform", False, lock=True)

    # reset transforms of the curve
    cmds.makeIdentity(curve1)

    curve_name = f"{pName or ctrl2}{suffix or ''}"
    cmds.rename(curve1, curve_name)


sel = cmds.ls(sl=True)
create_curve_link_from_controllers(sel)
