"""
This script updates any constraint after moving the constrained object.
Usage:
    move any constrained object, then run the script.
"""
__author__ = "Rémi CUXAC"
from maya import cmds

def update_offset_constraint(obj_list):
    if not obj_list:cmds.warning("Please select an constrained object or the constraint you want to update.");return
    constraint = list(set(cmds.ls(cmds.listConnections(obj_list, destination=False), type="constraint")))
    if not constraint:cmds.warning("No constraint applied to the object. Please select a another constrained objet or constraint.");return
    for const in constraint:
        constType = cmds.nodeType(const)
        function = getattr(cmds, constType)
        driverList= function(const, q=True, targetList=True)
        if not driverList:cmds.warning("The constraint is driven by nothing.");return
        weightList = function(driverList, obj_list, q=True, w=True)
        weightList = weightList if isinstance(weightList, list) else [weightList]
        for driver, weight in zip(driverList, weightList):
            function(driver, obj_list, e=True, maintainOffset=True, w=weight)

sel = cmds.ls(sl=1)
update_offset_constraint(sel)

