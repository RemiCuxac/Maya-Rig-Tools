import traceback
from collections import namedtuple
from dataclasses import dataclass
from typing import Optional

try:
    from PySide6 import QtWidgets, QtCore
    from PySide6 import pyqtSignal as Signal
except ModuleNotFoundError:
    from PySide2 import QtWidgets, QtCore
    from PySide2.QtCore import Signal
import maya.cmds as cmds
import maya.api.OpenMaya as om

# -----------------------------------------------------------------------------
# Data Structures
# -----------------------------------------------------------------------------

StatusTheme = namedtuple("Style", ['background', 'color'])
SUCCESS = StatusTheme("SeaGreen", "white")
WARNING = StatusTheme("Chocolate", "white")
ERROR = StatusTheme("IndianRed", "white")


@dataclass
class OperationType:
    """Defines the type of weight transfer operation and its parameters."""
    copy: bool = False
    flip: bool = False
    mirror: bool = False
    invert: bool = False
    axis: str = ""
    axis_index: int = None


@dataclass
class Component:
    """Represents a source or target component (mesh) and its selected attributes."""
    object: str = ""
    object_shape: str = ""
    vertex_count: int = None
    component_type: str = ""  # "Source" or "Target"
    deformer_dict: dict[str, dict[str, str]] = None
    deformer_choice: str = ""
    attr_choice: str = ""


# -----------------------------------------------------------------------------
# UI Components (View)
# -----------------------------------------------------------------------------

class ComponentWidget(QtWidgets.QGroupBox):
    """
    Widget representing a single component (Source or Target).
    Allows selection of object, deformer, and attribute.
    """

    def __init__(self, component_type: str):
        super().__init__(component_type)
        self.comp = Component(component_type=component_type)
        self.create_layout()
        self.connect_signals()

    def create_layout(self):
        """Builds the UI layout for the component widget."""
        layout = QtWidgets.QVBoxLayout()
        sub_layout = QtWidgets.QHBoxLayout()
        self.qlabel = QtWidgets.QLabel("Select an object and set")
        self.qpb_set = QtWidgets.QPushButton("Set")
        self.qpb_set.setMaximumWidth(50)
        self.qcb_deformer = QtWidgets.QComboBox()
        self.qcb_attrs = QtWidgets.QComboBox()
        sub_layout.addWidget(self.qlabel)
        sub_layout.addWidget(self.qpb_set)
        layout.addLayout(sub_layout)
        layout.addWidget(self.qcb_deformer)
        layout.addWidget(self.qcb_attrs)
        layout.addStretch()
        self.setLayout(layout)
        if self.comp.component_type != "Source":
            self.setCheckable(True)
        self.setMinimumWidth(150)

    def connect_signals(self):
        """Connects UI signals to slots."""
        self.qpb_set.clicked.connect(self.fill_from_component)
        self.qcb_deformer.currentIndexChanged.connect(self.update_deform_combobox)
        self.qcb_attrs.currentIndexChanged.connect(self.update_attrs_combobox)
        self.toggled.connect(self.deleteLater)

    def fill_from_component(self, component: Component = None):
        """Populates the widget fields based on the provided Component data."""
        if not component:
            return
        self.comp = component
        self.qlabel.setText(self.comp.object)
        self.qcb_deformer.clear()
        self.qcb_deformer.addItems(list(self.comp.deformer_dict.keys()))
        self.update_deform_combobox()

    def update_deform_combobox(self):
        """Updates the attributes combobox based on the selected deformer."""
        current_deformer = self.qcb_deformer.currentText()
        if not current_deformer:
            self.qcb_attrs.clear()
            return
        self.qcb_attrs.clear()
        self.qcb_attrs.addItems(self.comp.deformer_dict[current_deformer].keys())
        self.comp.deformer_choice = self.qcb_deformer.currentText()

    def update_attrs_combobox(self):
        """Updates the component's attribute choice."""
        self.comp.attr_choice = self.qcb_attrs.currentText()


class WeightTransferInterface(QtWidgets.QMainWindow):
    """
    Main Window for the Weight Transfer tool.
    Manages the overall layout and user interactions.
    """
    transfer: Signal = Signal(Component, list, OperationType)  # source, targets, operation
    get_component: Signal = Signal(Component)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("WeightTransfer")
        self.resize(250, 100)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self._create_timer()
        self._create_layout()
        self._connect_signals()
        self._pending_widget: Optional[ComponentWidget] = None

    def _create_timer(self):
        """Adds a persistent timer for the status bar message."""
        self.status_timer = QtCore.QTimer(self)
        self.status_timer.setSingleShot(True)
        self.status_timer.timeout.connect(self.clear_message)

    def _create_layout(self):
        """Constructs the main window layout."""
        self.setCentralWidget(QtWidgets.QWidget())
        self.qvl_main_layout = QtWidgets.QVBoxLayout()

        # Operation Type Radio Buttons
        self.qrb_copy = QtWidgets.QRadioButton("Copy")
        self.qrb_flip = QtWidgets.QRadioButton("Flip")
        self.qrb_flip.setChecked(True)
        self.qrb_mirror = QtWidgets.QRadioButton("Mirror")
        self.qrb_invert = QtWidgets.QRadioButton("Invert")

        # Axis Selection
        self.qcb_axis = QtWidgets.QComboBox()
        self.qcb_axis.addItems(["x", "y", "z"])

        for widget in [self.qrb_copy, self.qrb_flip, self.qrb_mirror, self.qrb_invert, self.qcb_axis]:
            self.qvl_main_layout.addWidget(widget)

        # Source Section
        self.qw_sources = QtWidgets.QWidget()
        self.qvl_layout_sources = QtWidgets.QVBoxLayout(self.qw_sources)
        self.qvl_layout_sources.setContentsMargins(2, 2, 2, 2)
        self._add_source()

        # Target Section
        self.qw_targets = QtWidgets.QWidget()
        self.qvl_layout_targets = QtWidgets.QVBoxLayout(self.qw_targets)
        self.qvl_layout_targets.setContentsMargins(2, 2, 2, 2)
        self.qpb_add_target = QtWidgets.QPushButton("+ target")
        self.qvl_layout_targets.addWidget(self.qpb_add_target)

        # Set QSplitter
        self.qs_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.qs_splitter.addWidget(self.qw_sources)
        self.qs_splitter.addWidget(self.qw_targets)
        self.qvl_main_layout.addWidget(self.qs_splitter)
        self.qs_splitter.setCollapsible(0, False)
        self.qs_splitter.setCollapsible(1, False)

        # Finish Main Layout
        self.qvl_main_layout.addStretch()
        self.qpb_transfer = QtWidgets.QPushButton("Transfer")
        self.qvl_main_layout.addWidget(self.qpb_transfer)
        self.centralWidget().setLayout(self.qvl_main_layout)
        self.statusBar = self.statusBar()

    def _connect_signals(self):
        """Connects main window signals."""
        self.qpb_transfer.clicked.connect(self._on_transfer_clicked)
        self.qpb_add_target.clicked.connect(self._add_target)

    def _on_transfer_clicked(self):
        """Handles the transfer button click, gathering data and emitting the transfer signal."""
        source = self.qvl_layout_sources.itemAt(0).widget()  # we assume source is the first widget of the layout
        assert isinstance(source, ComponentWidget)
        targets = []
        for i in range(self.qvl_layout_targets.count()):
            widget = self.qvl_layout_targets.itemAt(i).widget()
            if not isinstance(widget, ComponentWidget):
                continue
            targets.append(widget.comp)
        if not targets:
            targets = [source.comp]
        self.transfer.emit(source.comp, targets, self._get_operation())

    def _get_operation(self):
        """Collects the selected operation parameters from the UI."""
        operation = OperationType()
        operation.copy = self.qrb_copy.isChecked()
        operation.flip = self.qrb_flip.isChecked()
        operation.mirror = self.qrb_mirror.isChecked()
        operation.invert = self.qrb_invert.isChecked()
        operation.axis = self.qcb_axis.currentText()
        return operation

    def _add_source(self):
        """Adds a source component widget."""
        widget = ComponentWidget("Source")
        self.qvl_layout_sources.addWidget(widget)
        widget.qpb_set.clicked.connect(self._on_set_clicked)

    def _add_target(self):
        """Adds a target component widget."""
        widget = ComponentWidget("Target")
        self.qvl_layout_targets.insertWidget(self.qvl_layout_targets.count() - 1, widget)
        widget.qpb_set.clicked.connect(self._on_set_clicked)

    def _on_set_clicked(self):
        """Handles the 'Set' button click on component widgets."""
        self._pending_widget = self.sender().parent()
        assert isinstance(self._pending_widget, ComponentWidget)
        component = self._pending_widget.comp
        self.get_component.emit(component)

    def fill_component(self, component: Component):
        """Updates the pending widget with the retrieved component data."""
        if self._pending_widget:
            self._pending_widget.fill_from_component(component)
            self._pending_widget = None

    def send_message(self, message: str, message_type: StatusTheme, delay: int = 3000):
        """Sends a message to the status bar with a specific theme."""
        self.status_timer.stop()
        self.statusBar.showMessage(message)
        self.statusBar.setStyleSheet(f"background-color: {message_type.background}; color: {message_type.color}")
        if delay:
            self.status_timer.start(delay)

    def clear_message(self):
        """Clears the status bar message."""
        self.statusBar.clearMessage()
        self.statusBar.setStyleSheet("")


# -----------------------------------------------------------------------------
# Business Logic (Model)
# -----------------------------------------------------------------------------

class WeightTransferModel:
    """
    Contains the logic for Maya operations:
    - Retrieving geometry and deformer data.
    - Calculating weight transfers (Copy, Flip, Mirror, Invert).
    """

    @staticmethod
    def hold_undo():
        """Opens an undo chunk."""
        cmds.undoInfo(openChunk=True, chunkName="WeightTransfer")

    @staticmethod
    def close_undo():
        """Closes an undo chunk."""
        cmds.undoInfo(closeChunk=True)

    @staticmethod
    def undo():
        """Undo to the initial chunk"""
        last_undo = cmds.undoInfo(query=True, undoName=True)
        if last_undo == "WeightTransfer":
            cmds.undo()

    @staticmethod
    def get_orig_shape(component: Component) -> str:
        """Finds the original geometry shape node for a transform."""
        shape_orig: list[str] = cmds.deformableShape(component.object, originalGeometry=True)
        if shape_orig != [""]:
            return str(shape_orig[0].split(".")[0])
        return str(cmds.listRelatives(component.object, shapes=True)[0])

    @staticmethod
    def get_axis_index(axis: str):
        """Converts axis string ('x', 'y', 'z') to index (0, 1, 2)."""
        return int({"x": 0, "y": 1, "z": 2}[axis.lower()])

    @staticmethod
    def get_deformer_dict(component: Component):
        """Retrieves all supported deformers and their attributes for the component's object."""
        deformers = cmds.findDeformers(component.object) or []
        deform_list = {}
        for d in deformers:
            if cmds.objectType(d, isType="skinCluster"):
                continue
            deform_list[d] = {}
            aliases = cmds.aliasAttr(d, query=True) or ["weights", "weight[0]"]
            for i in range(0, len(aliases), 2):
                attr_name = aliases[i]
                attr_index = aliases[i + 1].rstrip(']').split('[')[-1]
                if cmds.objectType(d, isType="blendShape"):
                    deform_list[d]["envelope"] = f"{d}.inputTarget[0].baseWeights[*]"  # manually add envelope weight
                    path = f"{d}.inputTarget[0].inputTargetGroup[{attr_index}].targetWeights[*]"
                else:
                    path = f"{d}.weightList[{attr_index}].weights[*]"
                deform_list[d][attr_name] = path
        return deform_list

    @staticmethod
    def get_points(component: Component):
        """Gets the vertex positions of the component's mesh."""
        sel: om.MSelectionList = om.MSelectionList()
        sel.add(component.object_shape)
        mesh_fn: om.MFnMesh = om.MFnMesh(sel.getDagPath(0))
        return om.MPointArray(mesh_fn.getPoints(om.MSpace.kObject))

    @staticmethod
    def get_weights(component: Component):
        """Robust function to reads the weights from the selected deformer attribute."""
        return [cmds.getAttr(component.deformer_dict[component.deformer_choice][component.attr_choice].replace(
            "*", str(v))) for v in range(component.vertex_count)]

    @staticmethod
    def get_opposite_vtx_map(axis_index: int,
                             points: om.MPointArray,
                             tolerance: float = 0.001) -> dict[int, int]:
        """
        Calculates a mapping between vertices and their mirrored counterparts.
        Uses a spatial grid for optimization.
        """
        grid = {}
        inv_tol = 1.0 / tolerance
        sq_tolerance = tolerance * tolerance
        for idx, p in enumerate(points):
            key = (int(p[0] * inv_tol), int(p[1] * inv_tol), int(p[2] * inv_tol))
            if key not in grid:
                grid[key] = []
            grid[key].append(idx)

        vtx_map = {}
        for idx, p in enumerate(points):
            tx, ty, tz = p[0], p[1], p[2]
            if axis_index == 0:
                tx = -tx
            elif axis_index == 1:
                ty = -ty
            elif axis_index == 2:
                tz = -tz

            best_idx = idx
            min_sq_dist = sq_tolerance
            cx, cy, cz = int(tx * inv_tol), int(ty * inv_tol), int(tz * inv_tol)
            for i in range(cx - 1, cx + 2):
                for j in range(cy - 1, cy + 2):
                    for k in range(cz - 1, cz + 2):
                        neighbor_key = (i, j, k)
                        if neighbor_key in grid:
                            for other_idx in grid[neighbor_key]:
                                orig = points[other_idx]
                                dx = tx - orig[0]
                                dy = ty - orig[1]
                                dz = tz - orig[2]
                                sq_dist = dx * dx + dy * dy + dz * dz
                                if sq_dist < min_sq_dist:
                                    if other_idx == idx:
                                        continue
                                    min_sq_dist = sq_dist
                                    best_idx = other_idx
            vtx_map[idx] = best_idx
        return vtx_map

    @staticmethod
    def get_vertex_count(component):
        """Gets the vertex count."""
        return cmds.polyEvaluate(component.object, vertex=True)

    def get_data(self, component: Component) -> Optional[Component]:
        """Populates the Component object with data from the current Maya selection."""
        selection = cmds.ls(selection=True, type="transform", noIntermediate=True)
        component.object = selection[0] if selection else None
        if not component.object:
            return None
        # component.object_short = component.object.split("|")[-1]
        component.object_shape = self.get_orig_shape(component)
        component.vertex_count = self.get_vertex_count(component)
        component.deformer_dict = self.get_deformer_dict(component)
        return component

    def check_data(self, *components) -> bool:
        """Ensures that all components given weren't altered and are valid."""
        last = " Please set again."
        for comp in components:
            comp: Component
            assert comp.object, "Please make sure all widgets are filled."
            assert cmds.objExists(comp.object), "Object not found." + last
            assert cmds.objExists(comp.deformer_choice), "Deformer not found."
            assert cmds.objExists(f"{comp.deformer_choice}.{comp.attr_choice}"), "Attribute not found." + last
            assert comp.vertex_count == components[0].vertex_count, "Vertex count mismatch between source and targets."
            assert comp.vertex_count == self.get_vertex_count(comp), "Vertex count has changed." + last
        return True

    def transfer_weights(self, source: Component, *targets):
        """Direct copy of weights from source to target."""
        src_weights = self.get_weights(source)[1:-2]
        for target in targets:
            path: str = target.deformer_dict[target.deformer_choice][target.attr_choice]
            for v in range(source.vertex_count):
                cmds.setAttr(path.replace('*', str(v)), src_weights[v])

    def flip_weights(self, source: Component, *targets, operation_type: OperationType) -> None:
        """Flips weights across the specified axis."""
        points = self.get_points(source)
        vtx_map = self.get_opposite_vtx_map(self.get_axis_index(operation_type.axis), points)
        src_weights = self.get_weights(source)
        for target in targets:
            path: str = target.deformer_dict[target.deformer_choice][target.attr_choice]
            for v in range(source.vertex_count):
                cmds.setAttr(path.replace('*', str(v)), src_weights[vtx_map[v]])

    def invert_weights(self, source: Component, *targets):
        """Inverts weights (1 - weight)."""
        src_weights = self.get_weights(source)
        for target in targets:
            path: str = target.deformer_dict[target.deformer_choice][target.attr_choice]
            for v in range(source.vertex_count):
                cmds.setAttr(path.replace('*', str(v)), 1 - src_weights[v])

    def mirror_weights(self, source: Component, *targets, operation_type: OperationType):
        """Mirrors weights from positive to negative side (or vice versa) across axis."""
        points = self.get_points(source)
        vtx_map = self.get_opposite_vtx_map(self.get_axis_index(operation_type.axis), points)
        src_weights = self.get_weights(source)
        for target in targets:
            path: str = target.deformer_dict[target.deformer_choice][target.attr_choice]
            for v in range(source.vertex_count):
                if points[v][self.get_axis_index(operation_type.axis)] > 0:  # checks if x, y or z is positive
                    cmds.setAttr(path.replace('*', str(v)), src_weights[v])
                else:
                    cmds.setAttr(path.replace('*', str(v)), src_weights[vtx_map[v]])


# -----------------------------------------------------------------------------
# Presenter
# -----------------------------------------------------------------------------

class WeightTransferPresenter:
    """
    Presenter class connecting the View (Interface) and the Model (Logic).
    Handles events from the View and invokes Model operations.
    """

    def __init__(self, model: WeightTransferModel, view: WeightTransferInterface):
        self.model = model
        self.view = view
        self.view.transfer.connect(self._on_transfer_emit)
        self.view.get_component.connect(self._on_ask_component)

    def _on_transfer_emit(self, source: Component, targets: list[Component], operation_type: OperationType):
        """
        Slot called when transfer is requested.
        Validates inputs and executes the requested operation.
        """
        try:
            self.model.check_data(source, *targets)
        except Exception as e:
            self.view.send_message(str(e), WARNING)
            return
        try:
            self.model.hold_undo()
            if operation_type.copy:
                self.model.transfer_weights(source, *targets)
            if operation_type.flip:
                self.model.flip_weights(source, *targets, operation_type=operation_type)
            if operation_type.mirror:
                self.model.mirror_weights(source, *targets, operation_type=operation_type)
            if operation_type.invert:
                self.model.invert_weights(source, *targets)
            self.model.close_undo()
            self.view.send_message("Done !", SUCCESS)
        except Exception as e:
            traceback.print_exc()
            self.model.close_undo()
            self.model.undo()
            self.view.send_message(str(e), ERROR)

    def _on_ask_component(self, component: Component):
        """Slot called when a component needs to be populated from selection."""
        component = self.model.get_data(component)
        if not component:
            self.view.send_message("Please select a component.", WARNING)
        self.view.fill_component(component)


# -----------------------------------------------------------------------------
# Main Execution
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    # app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    wt_model = WeightTransferModel()
    wt_view = WeightTransferInterface()
    wt_presenter = WeightTransferPresenter(wt_model, wt_view)
    wt_view.show()
