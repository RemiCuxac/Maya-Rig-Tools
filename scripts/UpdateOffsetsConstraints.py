from maya import cmds
sel = cmds.ls(sl=1)

def update_offset_constraint(sel):
    if not sel:cmds.warning("Please select an constrained object or the constraint you want to update.");return
    constraint = list(set(cmds.ls(cmds.listConnections(sel, destination=False), type="constraint")))
    if not constraint:cmds.warning("No constraint applied to the object. Please select a another constrained objet or constraint.");return
    for const in constraint:
        constType = cmds.nodeType(const)
        function = getattr(cmds, constType)
        driverList= function(const, q=True, targetList=True)
        if not driverList:cmds.warning("The constraint is driven by nothing.");return
        weightList = function(driverList, sel, q=True, w=True)
        weightList = weightList if isinstance(weightList, list) else [weightList]
        for driver, weight in zip(driverList, weightList):
            function(driver, sel, e=True, maintainOffset=True, w=weight)

update_offset_constraint(sel)

