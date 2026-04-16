"""
This script updates any constraint after moving the constrained object.
Usage:
    move any constrained object, then run the script.
"""
__author__ = "Rémi CUXAC"

from maya import cmds


def update_offset_constraint(obj_list):
    if not obj_list: cmds.warning("Please select an constrained object or the constraint you want to update.");return
    constraint = list(set(cmds.ls(cmds.listConnections(obj_list, destination=False), type="constraint")))
    if not constraint: cmds.warning(
        "No constraint applied to the object. Please select a another constrained objet or constraint.");return
    for const in constraint:
        const_type = cmds.nodeType(const)
        function = getattr(cmds, const_type)
        driver_list = function(const, q=True, targetList=True)
        if not driver_list: cmds.warning("The constraint is driven by nothing.");return
        weight_list = function(driver_list, obj_list, q=True, w=True)
        weight_list = weight_list if isinstance(weight_list, list) else [weight_list]
        for driver, weight in zip(driver_list, weight_list):
            function(driver, obj_list, e=True, maintainOffset=True, w=weight)


sel = cmds.ls(sl=1)
update_offset_constraint(sel)
