"""
This script helps to replace a geo my a modified one. It's useful in cas you want to update the base shape of your skinned / rigged geo.
Both geos have to have the same vertex ID / count.
Usage:
    select the geom transform you want to be updated, then another geo that has the same vertex ID / count and run the script.
"""
__author__ = "Rémi CUXAC"

from maya import cmds


def get_shape_orig(transform: str):
    shapeOrig = cmds.deformableShape(transform, originalGeometry=True)
    if shapeOrig != [""]:
        shapeOrig = shapeOrig[0].split(".")[0]
    else:
        shapeOrig = cmds.listRelatives(transform, shapes=True)[0]
    return shapeOrig


def replace_geos(geo_list: list):
    target = geo_list[1]
    source = geo_list[0]
    targetShape = get_shape_orig(target)
    sourceShape = get_shape_orig(source)
    cmds.connectAttr(sourceShape + ".outMesh", targetShape + ".inMesh", force=True)


sel = cmds.ls(sl=1)
replace_geos(sel) if sel else cmds.warning("You have to select two objects : source then target.")
