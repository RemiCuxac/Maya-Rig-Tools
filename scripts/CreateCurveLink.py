from maya import cmds

def create_curve_link_from_controlers(pObjList: list = None, pParentOfCrv: str = None, pName: str = None,
                                      pSuffix: str = "_crv_link"):
    """
    This script create a link from two controlers with a curve
    """
    if not pObjList:
        pObjList = cmds.ls(sl=1)
    elif isinstance(pObjList, str):
        pObjList = [pObjList]

    if len(pObjList) == 2:
        ctrl1 = pObjList[0]
        ctrl2 = pObjList[1]
        if isinstance(ctrl1, list) and isinstance(ctrl2, list):
            ctrl1 = ctrl1[0]
            ctrl2 = ctrl2[0]
        curve1 = cmds.curve(degree=1, p=[(0, 0, 0), (0, 0, 0)])
        if not pParentOfCrv:
            pParentOfCrv = ctrl1
        cmds.parent(curve1, pParentOfCrv)
        for index, ctrl in enumerate([ctrl1, ctrl2]):
            decompM = cmds.createNode("decomposeMatrix")
            cmds.connectAttr(f"{ctrl}.worldMatrix", f"{decompM}.inputMatrix")
            cmds.connectAttr(f"{decompM}.outputTranslate", f"{curve1}.controlPoints[{index * 2}]")
        cmds.setAttr(f"{curve1}.overrideEnabled", True)
        cmds.setAttr(f"{curve1}.overrideDisplayType", 1)
        cmds.setAttr(f"{curve1}.inheritsTransform", False, lock=True)

        # reset transforms of the curve
        cmds.makeIdentity(curve1)

        curveName = f"{pName or ctrl2}{pSuffix or ''}"
        cmds.rename(curve1, curveName)
    else:
        raise Exception("Error, please select 2 controlers")

sel = cmds.ls(sl=True)
create_curve_link_from_controlers(sel)