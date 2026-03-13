import maya.cmds as cmds


def tag_hierarchy_controllers():
    shapes = cmds.ls(type='nurbsCurve', long=True) or []
    nurbs_transforms = list(set(cmds.listRelatives(shapes, parent=True, fullPath=True) or []))

    if not nurbs_transforms:
        cmds.error("No nurbsCurve controllers found.", n=True)
        return

    for node in nurbs_transforms:
        # Tag the transform as a controller
        # Creating it if it doesn't exist
        cmds.controller(node)

        # Find the nearest ancestor that is also a controller
        # We climb the hierarchy to skip over groups like 'grp_body'
        curr_parent = cmds.listRelatives(node, parent=True, fullPath=True)

        while curr_parent:
            parent_node = curr_parent[0]

            if parent_node in nurbs_transforms:
                # Found a controller parent. Link it and stop climbing.
                cmds.controller(node, parent_node, p=True)
                print(f"Linked Controller: {node.split('|')[-1]} -> Parent: {parent_node.split('|')[-1]}")
                break

            # If current parent isn't a controller, keep going up
            curr_parent = cmds.listRelatives(parent_node, parent=True, fullPath=True)


tag_hierarchy_controllers()