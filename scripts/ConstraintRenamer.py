import maya.cmds as cmds

sel = cmds.ls(sl=False, type="constraint")

for const in sel:
    # get all inputs of the constraint
    constInputs = cmds.listConnections(const)
    driven = constInputs[0]

    # get the drivers
    drivers = []
    for index, driver in enumerate(constInputs):
        if "Constraint" in driver:
            if "Constraint" not in constInputs[index - 1]:
                drivers.append(constInputs[index - 1])

    constraintType = const.split("_")[-1]

    # rename the attribute
    # find all custom attributes of the constraints
    constAttributes = cmds.listAttr(const)
    j = 0
    for index, attr in enumerate(constAttributes):
        if "W" in attr[-2]:
            # doesn't work if it exists an attr like "...W." with a "W" at the index [-2] in a constraint, quite impossible
            cmds.addAttr(f"{const}.{attr}", e=True, nn=f"{drivers[j]}W{attr[-1]}")
            try:
                cmds.renameAttr(f"{const}.{attr}", f"{drivers[j]}W{attr[-1]}")
            except:
                pass
            j += 1

    # rename the constraint
    newName = ""
    suffix = f"{driven}_{constraintType}"
    for k in range(len(drivers)):
        if not newName:
            newName = drivers[k]
        else:
            newName = f"{drivers[k]}__{newName}"
    fullName = f"{newName}__{suffix}"
    cmds.rename(const, fullName)