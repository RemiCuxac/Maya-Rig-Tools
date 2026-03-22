"""
This script converts any kind of selection to a curve. It works on full mesh, nurbsSurface and even on edge selection.
"""
__author__ = "Rémi CUXAC"

import maya.cmds as cmds


def get_all_nurbs_isoparms(n):
    u = [f"{n}.u[{i}]" for i in range(cmds.getAttr(n + ".spansU") + 1)]
    v = [f"{n}.v[{i}]" for i in range(cmds.getAttr(n + ".spansV") + 1)]
    return u + v


def edges_to_single_curve(sel_list: list):
    all_main_curves = []
    edges = []
    for elem in sel_list:
        if ".e" in elem:
            if ":" in elem:
                edges += cmds.ls(elem, flatten=True)
                continue
            edges += [elem]
            continue
        shape: list = cmds.listRelatives(elem, shapes=True)
        assert len(shape) == 1, f"Error for getting {elem}"
        if cmds.nodeType(shape) == "mesh":
            edges += cmds.ls(elem + ".e[*]", fl=True)
        elif cmds.nodeType(shape) == "nurbsSurface":
            edges = get_all_nurbs_isoparms(shape)

    main_curve = None
    for i, edge in enumerate(edges):
        try:
            if cmds.nodeType(edge) == "mesh":
                curves = cmds.polyToCurve(edge, form=2, degree=1, ch=False)
            else:
                curves = cmds.duplicateCurve(edge, ch=False, local=True)
            if i == 0:
                # first one becomes the main curve transform
                main_curve = curves[0]
            else:
                # parent shape node under main curve
                shape_nodes = cmds.listRelatives(curves[0], shapes=True, f=True) or []
                cmds.parent(shape_nodes, main_curve, shape=True, r=True)
                # delete the extra transform
                cmds.delete(curves[0])
        except Exception as e:
            cmds.warning("Failed to convert edge {}: {}".format(edge, e))
    if main_curve:
        if cmds.listRelatives(main_curve, parent=True):
            main_curve = cmds.parent(main_curve, world=True)
        main_curve = cmds.rename(main_curve, "curve_obj1")
        # cmds.matchTransform(main_curve, shape,pivots=True)
        all_main_curves.append(main_curve)
    cmds.select(all_main_curves)


sel = cmds.ls(sl=True)
edges_to_single_curve(sel) if sel else cmds.error("Please select an object.", n=True)
