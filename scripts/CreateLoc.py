"""
This script creates a locator from the position and orientation of the gizmo.
It can work from any kind of selection (vertex, edge, face, transform...).
If nothing selected, it creates the locator at origin.
Usage:
    Select an object and execute the script.
"""
__author__ = "Rémi CUXAC"

from maya import cmds


def get_gizmo_pos():
    """
    Detects the active tool and queries its specific position.
    Works for Move, Rotate, and Scale.
    """
    ctx = cmds.currentCtx()
    ctx_type = cmds.contextInfo(ctx, c=True)
    ctx_name = ctx_type.split("manip")[-1]
    if ctx_type == 'manipMove':
        return cmds.manipMoveContext(ctx_name, q=True, p=True)
    elif ctx_type == 'manipRotate':
        return cmds.manipRotateContext(ctx_name, q=True, p=True)
    elif ctx_type == 'manipScale':
        return cmds.manipScaleContext(ctx_name, q=True, p=True)

    # Fallback if no manip tool is active (e.g., Select Tool)
    # Returns the pivot of the selection in world space
    return cmds.xform(q=True, ws=True, piv=True)[:3]


def create_loc_from_gizmo(obj_list: list):
    prev_obj_name = ""
    if not obj_list:
        cmds.spaceLocator(name="locator_01")
        return
    for obj in obj_list:
        obj_name = obj.split('|')[-1].split('.')[0]
        mat = cmds.xform(obj, q=True, ws=True, m=True)
        pos = get_gizmo_pos()

        if obj_name == prev_obj_name:
            continue
        prev_obj_name = obj_name
        obj = cmds.spaceLocator(name=f"locator_{obj_name}")
        # cmds.setToolTo("moveSuperContext")
        cmds.xform(obj, ws=True, m=mat)
        cmds.xform(obj, ws=True, translation=pos)


sel = cmds.ls(sl=1)
create_loc_from_gizmo(sel)
