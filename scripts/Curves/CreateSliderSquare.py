"""
This script create a slider that will be useful for face rigging.
"""
__author__ = "Rémi CUXAC"

from enum import Enum, auto

from maya import cmds


class SliderType(Enum):
    square = auto()
    rectanglePositive = auto()
    rectanglePositiveNegative = auto()


def create_slider(slider_type: SliderType):
    d = 1 / 3
    ctrl = cmds.circle(nr=(0, 1, 0), r=0.2, constructionHistory=False)[0]
    if slider_type == slider_type.rectanglePositive:
        ui = cmds.curve(d=True, point=[(-d, 0, -d),
                                       (1 + d, 0, -d),
                                       (1 + d, 0, d),
                                       (-d, 0, d),
                                       (-d, 0, -d)],
                        k=[1, 2, 3, 4, 5])
        cmds.transformLimits(ctrl, tx=(0, 1), etx=(1, 1))
        cmds.setAttr(f"{ctrl}.tz", lock=True, keyable=False, channelBox=False)
    elif slider_type == slider_type.square:

        ui = cmds.curve(d=True, point=[(-1 - d, 0, -1 - d),
                                       (1 + d, 0, -1 - d),
                                       (1 + d, 0, 1 + d),
                                       (-1 - d, 0, 1 + d),
                                       (-1 - d, 0, -1 - d)],
                        k=[1, 2, 3, 4, 5])
        cmds.transformLimits(ctrl, tx=(-1, 1), tz=(-1, 1), etx=(1, 1), etz=(1, 1))
    elif slider_type == slider_type.rectanglePositiveNegative:
        ui = cmds.curve(d=True, point=[(-1 - d, 0, -d),
                                       (1 + d, 0, -d),
                                       (1 + d, 0, d),
                                       (-1 - d, 0, d),
                                       (-1 - d, 0, -d)],
                        k=[1, 2, 3, 4, 5])
        cmds.transformLimits(ctrl, tx=(-1, 1), etx=(1, 1))
        cmds.setAttr(f"{ctrl}.tz", lock=True, keyable=False, channelBox=False)

    else:
        # Default fallback or error handling if needed, though with Enum typing it's safer.
        return

    cmds.setAttr(f"{ctrl}.ty", lock=True, keyable=False, channelBox=False)
    cmds.setAttr(f"{ctrl}.rx", lock=True, keyable=False, channelBox=False)
    cmds.setAttr(f"{ctrl}.ry", lock=True, keyable=False, channelBox=False)
    cmds.setAttr(f"{ctrl}.rz", lock=True, keyable=False, channelBox=False)
    cmds.setAttr(f"{ctrl}.sx", lock=True, keyable=False, channelBox=False)
    cmds.setAttr(f"{ctrl}.sy", lock=True, keyable=False, channelBox=False)
    cmds.setAttr(f"{ctrl}.sz", lock=True, keyable=False, channelBox=False)
    cmds.parent(ctrl, ui)
    cmds.rotate(90, 0, 90, ui, os=True, fo=True)
    cmds.select(ui)
    cmds.rename(ctrl, "ctrl_ui_to_rename")
    cmds.rename(ui, "interface_ui_to_rename")


create_slider(SliderType.square)
