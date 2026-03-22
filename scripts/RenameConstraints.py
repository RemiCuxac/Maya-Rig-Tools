"""
This script renames all constraints from source, targets and type.
And update all attributes of the constraint to be up to date.
Usage:
    Execute the script. No selection needed.
"""
__author__ = "Rémi CUXAC"

import maya.cmds as cmds


def rename_constraints(const_list, rename_attrs: bool = True, rename_const: bool = True):
    for const in const_list:
        # get all inputs of the constraint
        const_inputs = cmds.listConnections(const)
        driven = const_inputs[0]

        # get the drivers
        drivers = []
        for index, driver in enumerate(const_inputs):
            if "Constraint" in driver:
                if "Constraint" not in const_inputs[index - 1]:
                    drivers.append(const_inputs[index - 1])

        const_type = const.split("_")[-1]

        # rename the attribute
        if rename_attrs:
            # find all custom attributes of the constraints
            const_attrs = cmds.listAttr(const)
            j = 0
            for index, attr in enumerate(const_attrs):
                if "W" in attr[-2]:
                    # doesn't work if it exists an attr like "...W." with a "W" at the index [-2] in a constraint, quite impossible
                    # TODO: find a way to work in any case
                    cmds.addAttr(f"{const}.{attr}", e=True, nn=f"{drivers[j]}W{attr[-1]}")
                    try:
                        cmds.renameAttr(f"{const}.{attr}", f"{drivers[j]}W{attr[-1]}")
                    except:
                        pass
                    j += 1

        if rename_const:
            # rename the constraint
            new_name = ""
            suffix = f"{driven}_{const_type}"
            for k in range(len(drivers)):
                if not new_name:
                    new_name = drivers[k]
                else:
                    new_name = f"{drivers[k]}__{new_name}"
            full_name = f"{new_name}__{suffix}"
            cmds.rename(const, full_name)


sel = cmds.ls(sl=False, type="constraint")
rename_constraints(sel) if sel else cmds.error("No constraint found.", n=True)
