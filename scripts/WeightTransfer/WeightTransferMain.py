import dataclasses

try:
    from PySide6 import QtWidgets, QtCore
    from PySide6 import pyqtSignal as Signal
except:
    from PySide2 import QtWidgets, QtCore
    from PySide2.QtCore import Signal
import maya.cmds as cmds
import maya.api.OpenMaya as om


@dataclasses.dataclass
class Component:
    object: str = ""  # TODO : use uuid instead of name ? or full Path ?
    objectShape: str = ""
    componentType: str = ""  # "source" or "target"
    deformerList: tuple = ()
    attrsList: tuple = ()


class ComponentWidget(QtWidgets.QGroupBox):
    def __init__(self, component_type: str):
        super().__init__(component_type)
        self.comp = Component(componentType=component_type)
        self.create_layout()
        self.connect_signals()

    def create_layout(self):
        layout = QtWidgets.QVBoxLayout()
        subLayout = QtWidgets.QHBoxLayout()
        self.qlabel = QtWidgets.QLabel("Select an object and set")
        self.qpb_set = QtWidgets.QPushButton("Set")
        self.qcb_deformer = QtWidgets.QComboBox()
        self.qcb_attrs = QtWidgets.QComboBox()
        subLayout.addWidget(self.qlabel)
        subLayout.addWidget(self.qpb_set)
        layout.addLayout(subLayout)
        layout.addWidget(self.qcb_deformer)
        layout.addWidget(self.qcb_attrs)
        self.setLayout(layout)

    def connect_signals(self):
        self.qpb_set.clicked.connect(self.fill_from_component)

    def fill_from_component(self, component: Component = None):
        if not component:
            return
        self.comp = component
        self.qlabel.setText(self.comp.object)
        self.qcb_deformer.clear()
        self.qcb_deformer.addItems(self.comp.deformerList)
        self.qcb_attrs.clear()
        self.qcb_attrs.addItems(self.comp.attrsList)


class WeightTransferInterface(QtWidgets.QMainWindow):
    states: Signal = Signal(bool, bool, bool, str)
    geoData: Signal = Signal()
    component: Component = Component()
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
        self.qrb_flip = QtWidgets.QRadioButton("Flip")
        self.qrb_flip.setChecked(True)
        self.qrb_mirror = QtWidgets.QRadioButton("Mirror")
        self.qrb_invert = QtWidgets.QRadioButton("Invert")
        self.qpb_transfer = QtWidgets.QPushButton("Transfer")
        self.qcb_axis = QtWidgets.QComboBox()
        self.qcb_axis.addItems(["x", "y", "z"])
        self.qvl_layout.addWidget(self.qrb_flip)
        self.qvl_layout.addWidget(self.qrb_mirror)
        self.qvl_layout.addWidget(self.qrb_invert)
        self.qvl_layout.addWidget(self.qcb_axis)

        self.qpb_add_source = QtWidgets.QPushButton("+ source")
        self.qpb_add_target = QtWidgets.QPushButton("+ target")
        qhl_layout = QtWidgets.QHBoxLayout()
        self.qvl_layout_sources = QtWidgets.QVBoxLayout()
        self.qvl_layout_targets = QtWidgets.QVBoxLayout()
        self.qvl_layout_sources.addWidget(self.qpb_add_source)
        self.qvl_layout_targets.addWidget(self.qpb_add_target)
        qhl_layout.addLayout(self.qvl_layout_sources)
        qhl_layout.addLayout(self.qvl_layout_targets)
        self.qvl_layout.addLayout(qhl_layout)


        self.qvl_layout.addStretch()
        self.qvl_layout.addWidget(self.qpb_transfer)
        self.statusBar()
        self.centralWidget().setLayout(self.qvl_layout)

    def connect_signals(self):
        self.qpb_transfer.clicked.connect(self._on_transfer_clicked)
        self.qpb_add_source.clicked.connect(self.add_source)
        self.qpb_add_target.clicked.connect(self.add_target)

    def _on_transfer_clicked(self):
        self.states.emit(self.qrb_flip.isChecked(),
                         self.qrb_mirror.isChecked(),
                         self.qrb_invert.isChecked(),
                         self.qcb_axis.currentText())

    def add_source(self):
        widget = ComponentWidget("Source")
        self.qvl_layout_sources.addWidget(widget)
        widget.qpb_set.clicked.connect(self._on_set_clicked)

    def add_target(self):
        widget = ComponentWidget("Target")
        self.qvl_layout_targets.addWidget(widget)
        widget.qpb_set.clicked.connect(self._on_set_clicked)

    def _on_set_clicked(self):
        self._pending_widget: ComponentWidget = self.sender().parent()
        self.geoData.emit()

    def fill_component(self, component: Component):
        if self._pending_widget:
            self._pending_widget.fill_from_component(component)
            self._pending_widget = None


class WeightTransferModel:
    def __init__(self):
        self.weight: dict = {}
        self.bs_index_map: dict[str, str] = {}
        self.deform_node: str = None
        self.vertex_count: int = 0
        self.geo: str = None
        self.points: list[om.MPoint] = None
        self.axis: str = None
        self.axis_index: int = None

    @staticmethod
    def hold_undo():
        cmds.undoInfo(openChunk=True)

    @staticmethod
    def restore_undo():
        cmds.undoInfo(closeChunk=True)

    def check_data(self):
        vars = []
        for k, v in self.__dict__.items():
            if not k.startswith("__") and v != 0 and not callable(v):
                vars += [True] if v else [False]
        return True if all(vars) else False

    @staticmethod
    def get_orig_shape(transform: str) -> str:
        shape_orig: list[str] = cmds.deformableShape(transform, originalGeometry=True)
        if shape_orig != [""]:
            return str(shape_orig[0].split(".")[0])
        return str(cmds.listRelatives(transform, shapes=True)[0])

    @staticmethod
    def get_opposite_vtx_map(axis_index: int,
                             points: list[om.MPoint],
                             tolerance: float = 0.001) -> dict[int, int]:
        coords: list[tuple[float, float, float]] = [(float(p[0]), float(p[1]), float(p[2])) for p in points]

        vtx_map: dict[int, int] = {}
        for idx, src in enumerate(coords):
            fx: float = -src[0] if axis_index == 0 else src[0]
            fy: float = -src[1] if axis_index == 1 else src[1]
            fz: float = -src[2] if axis_index == 2 else src[2]

            best_idx: int = idx
            best_dist: float = tolerance

            for other_idx, pos in enumerate(coords):
                if other_idx == idx:
                    continue
                dx: float = pos[0] - fx
                if dx < -best_dist or dx > best_dist:
                    continue
                dy: float = pos[1] - fy
                if dy < -best_dist or dy > best_dist:
                    continue
                dz: float = pos[2] - fz
                if dz < -best_dist or dz > best_dist:
                    continue
                # Safe to compute full distance only when all axes pass
                dist: float = (dx * dx + dy * dy + dz * dz) ** 0.5
                if dist < best_dist:
                    best_dist = dist
                    best_idx = other_idx

            vtx_map[idx] = best_idx

        return vtx_map

    def get_data(self, axis: str = "x"):
        # Map blendshape target names to their weight attribute paths
        selected_attrs: list[str] = list(cmds.channelBox("mainChannelBox", query=True, sha=True) or [])
        if not selected_attrs:
            return
        self.deform_node = str(
            (cmds.channelBox("mainChannelBox", query=True, historyObjectList=True) or [None])[0])
        if not self.deform_node:
            return
        alias_list: list[str] = list(cmds.aliasAttr(self.deform_node, query=True) or [])
        if "en" in selected_attrs:
            default: list[str] = ["Envelope", ".inputTarget[0].baseWeights[*]"]
            alias_list = default if selected_attrs == ["en"] else alias_list + default

        for idx in range(0, len(alias_list), 2):
            alias: str = str(alias_list[idx])
            raw_path: str = str(alias_list[idx + 1])
            if alias == "Envelope":
                self.bs_index_map[alias] = raw_path
            else:
                mapped: str = f".inputTarget[0].{raw_path.replace('weight', 'inputTargetGroup')}.targetWeights[*]"
                self.bs_index_map[alias] = mapped

        self.geo: str = str(cmds.ls(sl=1, type="transform", noIntermediate=True)[0])
        shape_node: str = self.get_orig_shape(self.geo)
        sel: om.MSelectionList = om.MSelectionList()
        sel.add(shape_node)
        mesh_fn: om.MFnMesh = om.MFnMesh(sel.getDagPath(0))
        self.points = list(mesh_fn.getPoints(om.MSpace.kObject))
        self.vertex_count: int = int(len(self.points))
        self.axis = axis
        self.axis_index = int({"x": 0, "y": 1, "z": 2}[axis.lower()])

        # get weights
        self.weight = {}
        for bs, mapped in self.bs_index_map.items():
            self.weight[bs] = [cmds.getAttr(self.deform_node + mapped.replace("*", str(v))) for v in
                               range(self.vertex_count)]

    def flip_weights(self) -> None:
        # Build the full opposite-vertex map once
        vtx_map: dict[int, int] = self.get_opposite_vtx_map(self.axis_index, self.points)
        for bs, weights in self.weight.items():
            path: str = self.bs_index_map[bs]
            for v in range(self.vertex_count):
                cmds.setAttr(
                    f"{self.deform_node}{path.replace('*', str(v))}",
                    weights[vtx_map[v]])

    def invert_weights(self):
        for bs, weights in self.weight.items():
            for v in range(self.vertex_count):
                cmds.setAttr(self.deform_node + self.bs_index_map[bs].replace("*", str(v)), 1 - self.weight[bs][v])

    def mirror_weights(self):
        vtx_map: dict[int, int] = self.get_opposite_vtx_map(self.axis_index, self.points)
        for bs, weights in self.weight.items():
            for v in range(self.vertex_count):
                if self.points[v][self.axis_index] > 0:
                    cmds.setAttr(self.deform_node + self.bs_index_map[bs].replace("*", str(v)), self.weight[bs][v])
                else:
                    cmds.setAttr(self.deform_node + self.bs_index_map[bs].replace("*", str(v)), weights[vtx_map[v]])


class WeightTransferPresenter:
    message = Signal(list[str])

    def __init__(self, model: WeightTransferModel, view: WeightTransferInterface):
        self.model = model
        self.view = view
        self.view.states.connect(self._on_transfer_emit)
        self.view.geoData.connect(self._on_ask_component)

    def _on_transfer_emit(self, flip, mirror, invert, axis):
        self.model.get_data(axis)
        if not self.model.check_data():
            self.view.statusBar().showMessage("Select a property in the Channel Box", 5000)
            return

        self.model.hold_undo()
        result = []
        if flip:
            result.append(self.model.flip_weights())
        if mirror:
            result.append(self.model.mirror_weights())
        if invert:
            result.append(self.model.invert_weights())
        self.model.restore_undo()
        self.view.statusBar().showMessage("Done !", 2000)

    def _on_ask_component(self):
        self.view.fill_component(Component("MyCube1", "MyCubeShape1", "source", ("blendshape1",), ("myAttr1",)))


if __name__ == "__main__":
    # app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    model = WeightTransferModel()
    view = WeightTransferInterface()
    presenter = WeightTransferPresenter(model, view)
    view.show()
    # sys.exit(app.exec())

# TODO: add Source and Target widgets
