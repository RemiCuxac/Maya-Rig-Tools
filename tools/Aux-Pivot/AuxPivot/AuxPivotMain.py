try:
    from PySide6 import QtWidgets, QtCore
except ModuleNotFoundError:
    from PySide2 import QtWidgets, QtCore
from collections import namedtuple
from functools import wraps

from maya import cmds

StatusTheme = namedtuple("Style", ['background', 'color'])
SUCCESS = StatusTheme("SeaGreen", "white")
WARNING = StatusTheme("Chocolate", "white")
ERROR = StatusTheme("IndianRed", "white")
prefix = "pivot_"


def deco_suspend_and_undo(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        cmds.undoInfo(openChunk=True, chunkName=func.__name__)
        cmds.refresh(suspend=True)
        try:
            return func(*args, **kwargs)
        except Exception as e:
            cmds.warning(str(e))
            raise e
        finally:
            cmds.refresh(suspend=False)
            cmds.undoInfo(closeChunk=True)
            cmds.refresh()

    return wrapper


class FrameWidget(QtWidgets.QGroupBox):
    def __init__(self, name: str):
        super().__init__(name)
        self.create_layout()
        self.connect_signals()

    def create_layout(self):
        qhl_layout = QtWidgets.QHBoxLayout()
        self.qsb_frame = QtWidgets.QSpinBox()
        self.qsb_frame.setMinimum(-99999)
        self.qsb_frame.setMaximum(99999)
        self.qsb_frame.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        self.qpb_set = QtWidgets.QPushButton("<==")
        qhl_layout.addWidget(self.qsb_frame)
        qhl_layout.addWidget(self.qpb_set)
        self.setLayout(qhl_layout)

    def connect_signals(self):
        self.qpb_set.clicked.connect(self.set_frame)

    def get_frame(self):
        return self.qsb_frame.value()

    def set_frame(self, frame):
        self.qsb_frame.setValue(frame)


class AuxPivotMain(QtWidgets.QMainWindow):
    """
    Main Window for the Weight Transfer tool.
    Manages the overall layout and user interactions.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aux Pivot")
        self.resize(250, 100)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self._create_timer()
        self._create_layout()
        self._connect_signals()

    def _create_layout(self):
        """Constructs the main window layout."""
        self.setCentralWidget(QtWidgets.QWidget())
        qvl_main_layout = QtWidgets.QVBoxLayout()

        self.qpb_create = QtWidgets.QPushButton("Create Aux Pivot")
        self.qpb_bake = QtWidgets.QPushButton("Bake and Remove")

        qhl_layout = QtWidgets.QHBoxLayout()
        self.fw_start = FrameWidget("Start frame")
        self.fw_end = FrameWidget("End frame")
        qhl_layout.addWidget(self.fw_start)
        qhl_layout.addWidget(self.fw_end)

        qvl_main_layout.addWidget(self.qpb_create)
        qvl_main_layout.addWidget(self.qpb_bake)
        qvl_main_layout.addLayout(qhl_layout)

        # Finish Main Layout
        self.centralWidget().setLayout(qvl_main_layout)
        self.statusBar = self.statusBar()

    def _connect_signals(self):
        """Connects main window signals."""
        self.qpb_create.clicked.connect(self._on_create_clicked)
        self.qpb_bake.clicked.connect(lambda: self._on_bake_clicked(self.fw_start.get_frame(),
                                                                    self.fw_end.get_frame()))
        self.fw_start.qpb_set.clicked.connect(self._on_frame_set_clicked)
        self.fw_end.qpb_set.clicked.connect(self._on_frame_set_clicked)

    def _on_frame_set_clicked(self):
        """Handles the 'Set' button click on component widgets."""
        fw: FrameWidget = self.sender().parent()
        fw.set_frame(self._get_current_frame())

    @deco_suspend_and_undo
    def _on_create_clicked(self):
        sel = cmds.ls(sl=True, type="transform")
        cmds.select(clear=True)
        for ctrl in sel:
            loc = cmds.spaceLocator(name=prefix + ctrl)[0]
            cmds.matchTransform(loc, ctrl)
            cmds.parent(loc, ctrl)
            cmds.connectAttr(f"{loc}.translate", f"{ctrl}.rotatePivot", force=True)
            cmds.select(loc, add=True)
        self.send_message("Aux Pivot created and selected.", SUCCESS)

    @deco_suspend_and_undo
    def _on_bake_clicked(self, start: int, end: int):
        sel = cmds.ls(sl=True, type="transform")

        # get list of (loc, ctrl) for each element of selection.
        loc_ctrl = []
        for elem in sel:
            if prefix in elem:
                ctrl_list = cmds.listConnections(f"{elem}.translate", source=False, destination=True)
                loc_ctrl.append([elem, ctrl_list[0]])
            else:
                loc_list = cmds.listConnections(f"{elem}.rotatePivot", source=True, destination=False)
                if loc_list:
                    loc_ctrl.append([loc_list[0], elem])

        start_timeline = cmds.playbackOptions(q=True, min=True)
        end_timeline = cmds.playbackOptions(q=True, max=True)
        time = (start_timeline, end_timeline) if start == end else (start, end + 1)

        for (loc, ctrl) in loc_ctrl:
            bake_loc = cmds.spaceLocator(name="bake_" + ctrl)[0]

            # # previous method:
            # for t in range(int(time[0]), int(time[-1])):
            #     cmds.currentTime(t)
            #     mat = cmds.xform(ctrl, m=True, ws=True, q=True)
            #     cmds.xform(bake_loc, m=mat, ws=True)
            #     cmds.setKeyframe(bake_loc)

            # make bake_loc follows the initial pivot of ctrl
            mult_node = cmds.createNode("multMatrix")
            cmds.connectAttr(f"{ctrl}.worldMatrix[0]", f"{mult_node}.matrixIn[0]")
            cmds.connectAttr(f"{loc}.matrix", f"{mult_node}.matrixIn[1]")
            cmds.connectAttr(f"{loc}.inverseMatrix", f"{mult_node}.matrixIn[2]")
            decomp_node = cmds.createNode("decomposeMatrix")
            cmds.connectAttr(f"{mult_node}.matrixSum", f"{decomp_node}.inputMatrix")
            cmds.connectAttr(f"{decomp_node}.outputTranslate", f"{bake_loc}.translate")
            cmds.connectAttr(f"{decomp_node}.outputRotate", f"{bake_loc}.rotate")
            cmds.connectAttr(f"{decomp_node}.outputScale", f"{bake_loc}.scale")
            cmds.bakeResults(bake_loc, simulation=True, t=(start_timeline, end_timeline), sb=1)
            cmds.delete([mult_node, decomp_node])

            # make ctrl follows bake_loc
            # 1. first reset pivot and connections
            cmds.disconnectAttr(f"{loc}.translate", f"{ctrl}.rotatePivot")
            cmds.xform(ctrl, zeroTransformPivots=True)
            # 2. then constraint
            cmds.parentConstraint(bake_loc, ctrl, maintainOffset=True)
            # 3. key, and bake
            cmds.setKeyframe(ctrl, attribute="blendParent1", time=time[0] - 1, value=0)
            cmds.setKeyframe(ctrl, attribute="blendParent1", time=time[0], value=1)
            cmds.setKeyframe(ctrl, attribute="blendParent1", time=time[-1], value=1)
            cmds.setKeyframe(ctrl, attribute="blendParent1", time=time[-1] + 1, value=0)
            cmds.bakeResults(ctrl, t=time, sb=1, preserveOutsideKeys=True)
            # delete constraints, bake_loc and loc
            cmds.delete(ctrl, constraints=True)
            cmds.delete([bake_loc, loc])

        self.send_message("Anim baked, pivot removed.", SUCCESS)

    @staticmethod
    def _get_current_frame() -> int:
        return cmds.currentTime(q=True)

    def _create_timer(self):
        """Adds a persistent timer for the status bar message."""
        self.status_timer = QtCore.QTimer(self)
        self.status_timer.setSingleShot(True)
        self.status_timer.timeout.connect(self.clear_message)

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


if __name__ == "__main__":
    # app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    ap_view = AuxPivotMain()
    ap_view.show()
