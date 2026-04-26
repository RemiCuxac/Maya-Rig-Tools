__author__ = "Rémi CUXAC"

try:
    from PySide2 import QtWidgets
except ModuleNotFoundError:
    from PySide6 import QtWidgets
from maya.api import OpenMaya as om
from maya import cmds

mat_dict = {"XY": [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, -1, 0, 0, 0, 0, 1],
            "YZ": [-1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            "XZ": [1, 0, 0, 0, 0, -1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]}


class MirrorJoints(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.create_layout()
        self.connect_buttons()
        self.setWindowTitle("Mirror joints")
        self.setMinimumSize(200, 100)
        self.show()

    def create_layout(self):
        # Main Layout
        qvbl_main_layout = QtWidgets.QVBoxLayout(self)
        qvbl_main_layout.setContentsMargins(10, 10, 10, 10)
        qvbl_main_layout.setSpacing(8)

        # Naming
        qgb_naming = QtWidgets.QGroupBox("Naming Convention")
        qgl_naming = QtWidgets.QGridLayout(qgb_naming)
        self.qle_source = QtWidgets.QLineEdit("left")
        self.qle_target = QtWidgets.QLineEdit("right")
        qgl_naming.addWidget(QtWidgets.QLabel("Search:"), 0, 0)
        qgl_naming.addWidget(self.qle_source, 0, 1)
        qgl_naming.addWidget(QtWidgets.QLabel("Replace:"), 1, 0)
        qgl_naming.addWidget(self.qle_target, 1, 1)
        qvbl_main_layout.addWidget(qgb_naming)

        # --- Settings
        qhbl_settings = QtWidgets.QHBoxLayout()

        # Mirror Plane
        qgb_mirror_plane = QtWidgets.QGroupBox("Mirror Plane")
        qvbl_mirror_plane = QtWidgets.QVBoxLayout(qgb_mirror_plane)
        self.qrb_yz = QtWidgets.QRadioButton("YZ")
        self.qrb_xz = QtWidgets.QRadioButton("XZ")
        self.qrb_xy = QtWidgets.QRadioButton("XY")
        self.qrb_yz.setChecked(True)
        qvbl_mirror_plane.addWidget(self.qrb_yz)
        qvbl_mirror_plane.addWidget(self.qrb_xz)
        qvbl_mirror_plane.addWidget(self.qrb_xy)

        # From
        qgb_from = QtWidgets.QGroupBox("From")
        qvbl_from = QtWidgets.QVBoxLayout(qgb_from)
        self.qrb_selected = QtWidgets.QRadioButton("Selected")
        self.qrb_hierarchy = QtWidgets.QRadioButton("Selected + Hierarchy")
        self.qrb_selected.setChecked(True)
        qvbl_from.addWidget(self.qrb_selected)
        qvbl_from.addWidget(self.qrb_hierarchy)

        # Mirror mode
        qgb_mirror_type = QtWidgets.QGroupBox("Mirror Mode")
        qvbl_mirror_type = QtWidgets.QVBoxLayout(qgb_mirror_type)
        self.qrb_behavior = QtWidgets.QRadioButton("Behavior")
        self.qrb_orientation = QtWidgets.QRadioButton("Orientation")
        self.qrb_behavior.setChecked(True)
        qvbl_mirror_type.addWidget(self.qrb_behavior)
        qvbl_mirror_type.addWidget(self.qrb_orientation)

        qhbl_settings.addWidget(qgb_from)
        qhbl_settings.addWidget(qgb_mirror_type)
        qhbl_settings.addWidget(qgb_mirror_plane)
        qvbl_main_layout.addLayout(qhbl_settings)

        # Extra
        qgb_extra = QtWidgets.QGroupBox("Extra")
        qgl_extra = QtWidgets.QGridLayout(qgb_extra)
        self.qcb_use_existing = QtWidgets.QCheckBox("Use Existing joints")
        self.qcb_use_existing.setChecked(True)
        qgl_extra.addWidget(self.qcb_use_existing, 0, 0)
        qvbl_main_layout.addWidget(qgb_extra)

        qvbl_main_layout.addStretch()
        self.qpb_mirror = QtWidgets.QPushButton("MIRROR")
        self.qpb_mirror.setMinimumHeight(40)
        qvbl_main_layout.addWidget(self.qpb_mirror)

    def connect_buttons(self):
        self.qpb_mirror.clicked.connect(self.mirror)

    def get_mirror_plane(self):
        if self.qrb_xy.isChecked():
            return "XY"
        if self.qrb_yz.isChecked():
            return "YZ"
        if self.qrb_xz.isChecked():
            return "XZ"

    def get_hierarchy(self, obj) -> list:
        return [obj] + list(cmds.listRelatives(obj, allDescendents=True) or [])

    def get_selection(self):
        return cmds.ls(sl=True)

    def get_naming_search_replace(self):
        return [self.qle_source.text(), self.qle_target.text()]

    def get_or_create_obj(self, source, target_name):
        # If target exists and 'use existing' is on, return it
        if self.qcb_use_existing.isChecked() and cmds.objExists(target_name):
            return target_name
        new_obj = cmds.duplicate(source, parentOnly=True, name=target_name)[0]

        return new_obj

    def get_mirrored_matrix(self, obj):
        mat = cmds.xform(obj, m=True, ws=True, q=True)
        mir_mat = mat_dict[self.get_mirror_plane()]
        om_mat = om.MMatrix(mat)
        om_mir_mat = om.MMatrix(mir_mat)
        om_new_mat = om_mat * om_mir_mat
        if self.qrb_behavior.isChecked():
            # flip each rotation axis
            for i in range(10):
                om_new_mat[i] *= -1
                # reset scale
        mt = om.MTransformationMatrix(om_new_mat)
        mt.setScale([1.0, 1.0, 1.0], om.MSpace.kWorld)
        om_new_mat = mt.asMatrix()
        return list(om_new_mat)

    def get_parent(self, obj):
        # Using fullPath=True is vital for the dictionary mapping to work
        parent = cmds.listRelatives(obj, parent=True, fullPath=True)
        return parent[0] if parent else None

    def get_target_name(self, source_name):
        search, replace = self.get_naming_search_replace()

        # If search string exists and isn't empty, try replacing
        if search and search in source_name:
            return source_name.replace(search, replace)

        # Fallback: If search fails, append suffix to avoid name collision
        return f"{source_name}_mirror"

    def mirror(self):
        sel = self.get_selection()
        if not sel:
            return
        cmds.undoInfo(openChunk=True)
        try:
            search, replace = self.get_naming_search_replace()

            # 1. Collect nodes TOP-DOWN
            if self.qrb_hierarchy.isChecked():
                all_nodes = cmds.listRelatives(sel[0], ad=True, f=True) or []
                nodes = [cmds.ls(sel[0], l=True)[0]] + list(reversed(all_nodes))
            else:
                nodes = cmds.ls(sel, l=True)

            # Map {OriginalFullPath : NewObjectActualName}
            # This is key for 'Use Existing' = False
            mirror_map = {}

            for obj_path in nodes:
                # Naming
                short_name = obj_path.split("|")[-1]
                target_name = self.get_target_name(short_name)

                # Create/Get - We capture the ACTUAL name returned by Maya
                mir_obj = self.get_or_create_obj(obj_path, target_name)
                mirror_map[obj_path] = mir_obj

                # Apply Matrix
                mat = self.get_mirrored_matrix(obj_path)
                cmds.xform(mir_obj, m=mat, ws=True)

                # 2. Advanced Parenting Logic
                parent_path = self.get_parent(obj_path)
                if parent_path:
                    # Priority 1: Parent to the object we JUST created/found in this loop
                    if parent_path in mirror_map:
                        new_parent = mirror_map[parent_path]

                        # FIX: Check if it's already parented before calling cmds.parent
                        current_p = cmds.listRelatives(mir_obj, parent=True, fullPath=True)
                        # Convert new_parent to full path for a reliable comparison
                        target_p_full = cmds.ls(new_parent, l=True)[0] if cmds.objExists(new_parent) else None

                        if current_p and target_p_full and current_p[0] == target_p_full:
                            pass
                        else:
                            cmds.parent(mir_obj, new_parent)
                    else:
                        # Use the helper function to ensure we look for the parent
                        # using the same logic (Search/Replace OR _mirror suffix)
                        parent_short_name = parent_path.split("|")[-1]
                        mir_parent_name = self.get_target_name(parent_short_name)  # FIX HERE

                        if cmds.objExists(mir_parent_name):
                            # Check if already parented to avoid redundant command warnings
                            current_p = cmds.listRelatives(mir_obj, parent=True)
                            if not current_p or current_p[0] != mir_parent_name:
                                # Avoid parenting an object to itself if names match
                                if mir_obj != mir_parent_name:
                                    cmds.parent(mir_obj, mir_parent_name)

        finally:
            cmds.undoInfo(closeChunk=True)


a = MirrorJoints()
