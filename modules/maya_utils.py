try:
    from PySide2 import QtCore, QtWidgets
except ModuleNotFoundError:
    from PySide6 import QtCore, QtWidgets

from typing import Optional
from maya import cmds


def get_script_folder() -> str:
    return cmds.internalVar(userScriptDir=True)


def get_top_widget_by_name(maya_window, tool_class) -> Optional[QtWidgets.QWidget]:
    for widget in maya_window.children():
        if widget.__class__.__name__ == tool_class.__name__:
            return widget
    return None


def get_sorted_hierarchy(hierarchy):
    hierarchy = sorted(hierarchy, key=lambda t: t.count('|'))
    return hierarchy


def get_skin_cluster(obj):
    return cmds.ls(cmds.findDeformers(obj), type="skinCluster")


def hold_undo(undo_name):
    """Opens an undo chunk."""
    cmds.undoInfo(openChunk=True, chunkName=undo_name)


def close_undo():
    """Closes an undo chunk."""
    cmds.undoInfo(closeChunk=True)


def undo(undo_name):
    """Undo to the initial chunk"""
    last_undo = cmds.undoInfo(query=True, undoName=True)
    if last_undo == undo_name:
        cmds.undo()


def get_shape_orig(obj: str) -> str:
    """Finds the original geometry shape node for a transform."""
    shape_orig: list = cmds.deformableShape(obj, originalGeometry=True)
    if shape_orig != [""]:
        return str(shape_orig[0].split(".")[0])
    return str(cmds.listRelatives(obj, shapes=True)[0])


def get_vertex_count(component):
    """Gets the vertex count."""
    return cmds.polyEvaluate(component.object, vertex=True)
