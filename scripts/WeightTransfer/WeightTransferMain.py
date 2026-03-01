from dataclasses import dataclass
from typing import Optional

try:
    from PySide6 import QtWidgets, QtCore
    from PySide6 import pyqtSignal as Signal
except:
    from PySide2 import QtWidgets, QtCore
    from PySide2.QtCore import Signal
import maya.cmds as cmds
import maya.api.OpenMaya as om


@dataclass
class OperationType:
    copy: bool = False
    flip: bool = False
    mirror: bool = False
    invert: bool = False
    axis: str = ""
    axis_index: int = None


@dataclass
class Component:
    object: str = ""
    object_shape: str = ""
    vertex_count: int = None
    component_type: str = ""  # "Source" or "Target"
    deformer_dict: dict[str, dict[str, str]] = None
    deformer_choice: str = ""
    attr_choice: str = ""


class ComponentWidget(QtWidgets.QGroupBox):
    def __init__(self, component_type: str):
        super().__init__(component_type)
        self.comp = Component(component_type=component_type)
        self.create_layout()
        self.connect_signals()

    def create_layout(self):
        layout = QtWidgets.QVBoxLayout()
        sub_layout = QtWidgets.QHBoxLayout()
        self.qlabel = QtWidgets.QLabel("Select an object and set")
        self.qpb_set = QtWidgets.QPushButton("Set")
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

    def connect_signals(self):
        self.qpb_set.clicked.connect(self.fill_from_component)
        self.qcb_deformer.currentIndexChanged.connect(self.update_deform_combobox)
        self.qcb_attrs.currentIndexChanged.connect(self.update_attrs_combobox)
        self.toggled.connect(self.deleteLater)

    def fill_from_component(self, component: Component = None):
        if not component:
            return
        self.comp = component
        self.qlabel.setText(self.comp.object)
        self.qcb_deformer.clear()
        self.qcb_deformer.addItems(list(self.comp.deformer_dict.keys()))
        self.update_deform_combobox()

    def update_deform_combobox(self):
        current_deformer = self.qcb_deformer.currentText()
        if not current_deformer:
            self.qcb_attrs.clear()
            return
        self.qcb_attrs.clear()
        self.qcb_attrs.addItems(self.comp.deformer_dict[current_deformer].keys())
        self.comp.deformer_choice = self.qcb_deformer.currentText()

    def update_attrs_combobox(self):
        self.comp.attr_choice = self.qcb_attrs.currentText()


class WeightTransferInterface(QtWidgets.QMainWindow):
    transfer: Signal = Signal(Component, Component, OperationType)  # source component, target component, and operation
    get_data_component: Signal = Signal(Component)
    _pending_widget: QtWidgets.QWidget = None

    def __init__(self):
        super().__init__()
        self.setWindowTitle("WeightTransfer")
        self.resize(250, 100)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.create_layout()
        self.connect_signals()

    def create_layout(self):
        self.setCentralWidget(QtWidgets.QWidget())
        self.qvl_layout = QtWidgets.QVBoxLayout()
        self.qrb_copy = QtWidgets.QRadioButton("Copy")
        self.qrb_flip = QtWidgets.QRadioButton("Flip")
        self.qrb_flip.setChecked(True)
        self.qrb_mirror = QtWidgets.QRadioButton("Mirror")
        self.qrb_invert = QtWidgets.QRadioButton("Invert")
        self.qpb_transfer = QtWidgets.QPushButton("Transfer")
        self.qcb_axis = QtWidgets.QComboBox()
        self.qcb_axis.addItems(["x", "y", "z"])
        self.qvl_layout.addWidget(self.qrb_copy)
        self.qvl_layout.addWidget(self.qrb_flip)
        self.qvl_layout.addWidget(self.qrb_mirror)
        self.qvl_layout.addWidget(self.qrb_invert)
        self.qvl_layout.addWidget(self.qcb_axis)

        self.qpb_add_target = QtWidgets.QPushButton("+ target")
        qhl_layout = QtWidgets.QHBoxLayout()
        self.qvl_layout_sources = QtWidgets.QVBoxLayout()
        self.qvl_layout_targets = QtWidgets.QVBoxLayout()
        self.qvl_layout_targets.addWidget(self.qpb_add_target)
        qhl_layout.addLayout(self.qvl_layout_sources)
        qhl_layout.addLayout(self.qvl_layout_targets)
        self.qvl_layout.addLayout(qhl_layout)

        self.qvl_layout.addStretch()
        self.qvl_layout.addWidget(self.qpb_transfer)
        self.statusBar()
        self.centralWidget().setLayout(self.qvl_layout)

        self.add_source()

    def connect_signals(self):
        self.qpb_transfer.clicked.connect(self._on_transfer_clicked)
        self.qpb_add_target.clicked.connect(self.add_target)

    def _on_transfer_clicked(self):
        source = self.qvl_layout_sources.itemAt(0).widget()  # we assume source is the first widget of the layout
        assert isinstance(source, ComponentWidget)
        target_widgets = []
        for i in range(self.qvl_layout_targets.count()):
            widget = self.qvl_layout_targets.itemAt(i).widget()
            if not isinstance(widget, ComponentWidget):
                continue
            target_widgets.append(widget)
        if target_widgets:
            for target in target_widgets:
                self.transfer.emit(source.comp, target.comp, self._get_operation())
        else:
            self.transfer.emit(source.comp, source.comp, self._get_operation())

    def _get_operation(self):
        operation = OperationType()
        operation.copy = self.qrb_copy.isChecked()
        operation.flip = self.qrb_flip.isChecked()
        operation.mirror = self.qrb_mirror.isChecked()
        operation.invert = self.qrb_invert.isChecked()
        operation.axis = self.qcb_axis.currentText()
        return operation

    def add_source(self):
        widget = ComponentWidget("Source")
        self.qvl_layout_sources.addWidget(widget)
        widget.qpb_set.clicked.connect(self._on_set_clicked)

    def add_target(self):
        widget = ComponentWidget("Target")
        self.qvl_layout_targets.insertWidget(0, widget)
        widget.qpb_set.clicked.connect(self._on_set_clicked)

    def _on_set_clicked(self):
        self._pending_widget: ComponentWidget = self.sender().parent()
        component = self._pending_widget.comp
        self.get_data_component.emit(component)

    def fill_component(self, component: Component):
        if self._pending_widget:
            self._pending_widget.fill_from_component(component)
            self._pending_widget = None


class WeightTransferModel:
    @staticmethod
    def hold_undo():
        cmds.undoInfo(openChunk=True)

    @staticmethod
    def restore_undo():
        cmds.undoInfo(closeChunk=True)

    @staticmethod
    def get_orig_shape(transform: str) -> str:
        shape_orig: list[str] = cmds.deformableShape(transform, originalGeometry=True)
        if shape_orig != [""]:
            return str(shape_orig[0].split(".")[0])
        return str(cmds.listRelatives(transform, shapes=True)[0])

    @staticmethod
    def get_axis_index(axis: str):
        return int({"x": 0, "y": 1, "z": 2}[axis.lower()])

    @staticmethod
    def get_deformer_dict(component: Component):
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
                    path = f"{d}.inputTarget[0].inputTargetGroup[{attr_index}].targetWeights[*]"
                else:
                    path = f"{d}.weightList[{attr_index}].weights[*]"
                deform_list[d][attr_name] = path
        return deform_list

    def get_data(self, component: Component) -> Optional[Component]:
        selection = cmds.ls(selection=True, type="transform", noIntermediate=True)
        component.object = selection[0] if selection else None
        if not component.object:
            return None
        component.object_shape = self.get_orig_shape(component.object)
        component.vertex_count = cmds.polyEvaluate(component.object, vertex=True)
        component.deformer_dict = self.get_deformer_dict(component)
        return component

    def get_points(self, component: Component):
        sel: om.MSelectionList = om.MSelectionList()
        sel.add(component.object_shape)
        mesh_fn: om.MFnMesh = om.MFnMesh(sel.getDagPath(0))
        return [(p.x, p.y, p.z, p.w) for p in mesh_fn.getPoints(om.MSpace.kObject)]

    def get_weights(self, component: Component):
        attr_path = component.deformer_dict[component.deformer_choice][component.attr_choice].replace("*", ":")
        return cmds.getAttr(attr_path) or []

    def get_opposite_vtx_map(self, axis_index: int,
                             points: list,
                             tolerance: float = 0.001) -> dict[int, int]:
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
            # Calcul de la position miroir (Target)
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

    def transfer_weights(self, source: Component, target: Component, *args):
        src_weights = self.get_weights(source)
        path: str = target.deformer_dict[target.deformer_choice][target.attr_choice]
        for v in range(source.vertex_count):
            cmds.setAttr(path.replace('*', str(v)), src_weights[v])

    def flip_weights(self, source: Component, target: Component, operationType: OperationType) -> None:
        points = self.get_points(source)
        vtx_map: dict[int, int] = self.get_opposite_vtx_map(self.get_axis_index(operationType.axis), points)
        src_weights = self.get_weights(source)
        path: str = target.deformer_dict[target.deformer_choice][target.attr_choice]
        for v in range(source.vertex_count):
            cmds.setAttr(path.replace('*', str(v)), src_weights[vtx_map[v]])

    def invert_weights(self, source: Component, target: Component, *args):
        src_weights = self.get_weights(source)
        path: str = target.deformer_dict[target.deformer_choice][target.attr_choice]
        for v in range(source.vertex_count):
            cmds.setAttr(path.replace('*', str(v)), 1 - src_weights[v])

    def mirror_weights(self, source: Component, target: Component, operationType: OperationType):
        points = self.get_points(source)
        vtx_map: dict[int, int] = self.get_opposite_vtx_map(self.get_axis_index(operationType.axis), points)
        src_weights = self.get_weights(source)
        path: str = target.deformer_dict[target.deformer_choice][target.attr_choice]
        for v in range(source.vertex_count):
            if points[v][self.get_axis_index(operationType.axis)] > 0:  # checks if x, y or z is positive
                cmds.setAttr(path.replace('*', str(v)), src_weights[v])
            else:
                cmds.setAttr(path.replace('*', str(v)), src_weights[vtx_map[v]])


class WeightTransferPresenter:
    message = Signal(list[str])

    def __init__(self, model: WeightTransferModel, view: WeightTransferInterface):
        self.model = model
        self.view = view
        self.view.transfer.connect(self._on_transfer_emit)
        self.view.get_data_component.connect(self._on_ask_component)

    def _on_transfer_emit(self, source: Component, target: Component, operationType: OperationType):
        self.model.hold_undo()
        if not source.object and not target.object:
            self.view.statusBar().showMessage("Please provide at least a source.", 5000)
        if source.vertex_count != target.vertex_count:
            self.view.statusBar().showMessage("Topology mismatch: Vertex counts /ID do not match.", 5000)
        if operationType.copy:
            self.model.transfer_weights(source, target, operationType)
        if operationType.flip:
            self.model.flip_weights(source, target, operationType)
        if operationType.mirror:
            self.model.mirror_weights(source, target, operationType)
        if operationType.invert:
            self.model.invert_weights(source, target, operationType)
        self.model.restore_undo()
        self.view.statusBar().showMessage("Done !", 2000)

    def _on_ask_component(self, component: Component):
        component = self.model.get_data(component)
        if not component:
            self.view.statusBar().showMessage("Please select a component.", 5000)
        self.view.fill_component(component)


if __name__ == "__main__":
    # app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    model = WeightTransferModel()
    view = WeightTransferInterface()
    presenter = WeightTransferPresenter(model, view)
    view.show()
