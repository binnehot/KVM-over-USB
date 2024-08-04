import logging
import os
import random
import re
import sys
import tempfile
import time
from typing import Tuple

import serial

import hid_def
import pythoncom
import pyWinhook as pyHook
import server_simple
import yaml
from default import default_config
from loguru import logger
from PySide6 import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtMultimedia import *
from PySide6.QtMultimediaWidgets import *
from PySide6.QtWidgets import *
from server import FPSCounter, KVM_Server, add_auth_user, count_auth_users
from ui import (
    device_setup_dialog_ui,
    indicator_ui,
    main_ui,
    numboard_ui,
    paste_board_ui,
    shortcut_key_ui,
    controller_setup_ui,
)

"""
qdarktheme import after QT
"""
# import qdarktheme

kb_buffer = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
mouse_buffer = [2, 0, 0, 0, 0, 0, 0, 0, 0]
mouse_buffer_rel = [7, 0, 0, 0, 0, 0, 0, 0, 0]
shift_symbol = [
    ")","!","@","#","$","%",
    "^","&","*","(","~","_",
    "+","{","}","|",":",'"',
    "<",">","?",
]  # fmt: skip
PATH = os.path.dirname(os.path.abspath(__file__))
ARGV_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))

if not os.path.exists(os.path.join(ARGV_PATH, "config.yaml")):
    with open(os.path.join(ARGV_PATH, "config.yaml"), "w") as f:
        f.write(default_config)

translation = True
try:
    with open(os.path.join(ARGV_PATH, "config.yaml"), "r") as load_f:
        config = yaml.safe_load(load_f)["config"]
        translation = config["translation"]
except Exception:
    pass


def str_bool(b) -> str:
    if not translation:
        return str(b)
    else:
        return "启用" if b else "禁用"


class Fake_StdWriter:
    def __init__(self, *args, **kwargs):
        self.buffer = ""
        self.callback = None

    def write(self, data):
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        self.buffer += data
        if self.callback is not None:
            self.callback(self.buffer)

    def flush(self):
        pass

    def clear(self):
        self.buffer = ""


fake_std = Fake_StdWriter()

# 屏蔽所有print
if sys.argv[-1] != "debug":

    def print(*args, **kwargs):
        pass

    sys.stdout = fake_std
    sys.stderr = fake_std

    logger.remove()
    logger.add(
        fake_std,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} - {level} - {name} - {message}",  #:{function}:{line}
        level="INFO",
    )
else:
    hid_def.set_verbose(True)


def strB2Q(uchar):
    inside_code = ord(uchar)
    if inside_code == 0x3000:
        inside_code = 0x0020
    else:
        inside_code -= 0xFEE0
    if inside_code < 0x0020 or inside_code > 0x7E:  # 转完之后不是半角字符返回原来的字符
        return uchar
    return chr(inside_code)


def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
    """
    Convert HSV color space to RGB color space.
    :param h: Hue, range in [0, 1)
    :param s: Saturation, range in [0, 1]
    :param v: Value, range in [0, 1]
    :return: RGB color space
    """
    if s == 0.0:
        return int(v * 255), int(v * 255), int(v * 255)
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6
    if i == 0:
        return int(v * 255), int(t * 255), int(p * 255)
    elif i == 1:
        return int(q * 255), int(v * 255), int(p * 255)
    elif i == 2:
        return int(p * 255), int(v * 255), int(t * 255)
    elif i == 3:
        return int(p * 255), int(q * 255), int(v * 255)
    elif i == 4:
        return int(t * 255), int(p * 255), int(v * 255)
    elif i == 5:
        return int(v * 255), int(p * 255), int(q * 255)
    return 0, 0, 0


def load_icon(name) -> QIcon:
    return QIcon(f"{PATH}/icons/24_light/{name}.png")


def load_pixmap(name, dark_override=None) -> QPixmap:
    return QPixmap(f"{PATH}/icons/24_light/{name}.png")


class MyPushButton(QPushButton):
    def __init__(self, parent=None):
        super(MyPushButton, self).__init__(parent)

    def setPixmap(self, pixmap):
        icon = QIcon(pixmap)
        self.setIcon(icon)
        self.setIconSize(QSize(18, 18))


class MyControllerSetupDialog(QDialog, controller_setup_ui.Ui_ControllerSetupDialog):
    def __init__(self, parent=None):
        super(MyControllerSetupDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.line_edit_baud.setValidator(QIntValidator())
        self.line_edit_screen_x_size.setValidator(QIntValidator())
        self.line_edit_screen_y_size.setValidator(QIntValidator())


class MyDeviceSetupDialog(QDialog, device_setup_dialog_ui.Ui_Dialog):
    def __init__(self, parent=None):
        super(MyDeviceSetupDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)


class MyShortcutKeyDialog(QDialog, shortcut_key_ui.Ui_Dialog):
    def __init__(self, parent=None):
        super(MyShortcutKeyDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)


class MyPasteBoardDialog(QDialog, paste_board_ui.Ui_Dialog):
    def __init__(self, parent=None):
        super(MyPasteBoardDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)


class MyIndicatorDialog(QDialog, indicator_ui.Ui_Dialog):
    def __init__(self, parent=None):
        super(MyIndicatorDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)


class MyNumKeyboardDialog(QDialog, numboard_ui.Ui_Dialog):
    def __init__(self, parent=None):
        super(MyNumKeyboardDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setFixedWidth(self.width())


class HidThread(QThread):
    _hid_signal = Signal(list)
    _event_signal = Signal(str)

    def __init__(self, parent=None):
        super(HidThread, self).__init__(parent)
        self._hid_signal.connect(self.hid_report)

    def hid_report(self, buf):
        hidinfo = hid_def.hid_report(buf)
        if hidinfo == 1 or hidinfo == 4:
            self._event_signal.emit("hid_error")


class MyMainWindow(QMainWindow, main_ui.Ui_MainWindow):
    _log_signal = Signal(str)
    _wheel_signal = Signal()
    _hid_signal = Signal(list)

    def __init__(self, parent=None):
        self.ignore_event = False
        super(MyMainWindow, self).__init__(parent)
        self.setupUi(self)

        # MainWindow accept mouse events
        self.setMouseTracking(True)

        self.camera = None
        self.camera_opened = False
        self.camera_info = None
        self.audio_opened = False
        self.device_connected = False
        self.fpsc = FPSCounter()

        # 子窗口
        self.device_setup_dialog = MyDeviceSetupDialog()
        self.control_setup_dialog = MyControllerSetupDialog()
        self.shortcut_key_dialog = MyShortcutKeyDialog()
        self.paste_board_dialog = MyPasteBoardDialog()
        self.indicator_dialog = MyIndicatorDialog()
        self.numkeyboard_dialog = MyNumKeyboardDialog()

        self.shortcut_key_dialog.pushButtonSend.released.connect(
            lambda: self.shortcut_key_func(1)
        )
        self.shortcut_key_dialog.pushButtonSend.pressed.connect(
            lambda: self.shortcut_key_func(2)
        )
        self.shortcut_key_dialog.pushButtonSave.clicked.connect(
            lambda: self.shortcut_key_func(3)
        )

        self.shortcut_key_dialog.pushButton_ctrl.clicked.connect(
            lambda: self.shortcut_key_handle(1)
        )
        self.shortcut_key_dialog.pushButton_alt.clicked.connect(
            lambda: self.shortcut_key_handle(4)
        )
        self.shortcut_key_dialog.pushButton_shift.clicked.connect(
            lambda: self.shortcut_key_handle(2)
        )
        self.shortcut_key_dialog.pushButton_meta.clicked.connect(
            lambda: self.shortcut_key_handle(8)
        )
        self.shortcut_key_dialog.pushButton_tab.clicked.connect(
            lambda: self.shortcut_key_handle(0x2B)
        )
        self.shortcut_key_dialog.pushButton_prtsc.clicked.connect(
            lambda: self.shortcut_key_handle(0x46)
        )
        self.shortcut_key_dialog.keySequenceEdit.keySequenceChanged.connect(
            lambda: self.shortcut_key_handle(0xFF)
        )
        self.shortcut_key_dialog.pushButton_clear.clicked.connect(
            lambda: self.shortcut_key_handle(0xFE)
        )

        self.paste_board_dialog.pushButtonSend.clicked.connect(
            lambda: self.paste_board_send()
        )
        self.paste_board_dialog.pushButtonStop.clicked.connect(
            lambda: self.paste_board_stop()
        )

        self.indicator_dialog.pushButtonNum.clicked.connect(
            lambda: self.lock_key_func(2)
        )
        self.indicator_dialog.pushButtonCaps.clicked.connect(
            lambda: self.lock_key_func(1)
        )
        self.indicator_dialog.pushButtonScroll.clicked.connect(
            lambda: self.lock_key_func(3)
        )

        for i in range(1, 28):
            getattr(self.numkeyboard_dialog, f"pushButton_{i}").pressed.connect(
                lambda x=i: self.numboard_func(x, True)
            )
            getattr(self.numkeyboard_dialog, f"pushButton_{i}").released.connect(
                lambda x=i: self.numboard_func(x, False)
            )
        # 导入外部数据
        try:
            with open(
                os.path.join(PATH, "data", "keyboard_hid2code.yaml"), "r"
            ) as load_f:
                self.keyboard_hid2code = yaml.safe_load(load_f)
            with open(
                os.path.join(PATH, "data", "keyboard_scancode2hid.yml"), "r"
            ) as load_f:
                self.keyboard_scancode2hid = yaml.safe_load(load_f)
            with open(os.path.join(PATH, "data", "keyboard.yaml"), "r") as load_f:
                self.keyboard_code = yaml.safe_load(load_f)
            with open(os.path.join(ARGV_PATH, "config.yaml"), "r") as load_f:
                self.configfile = yaml.safe_load(load_f)
            self.config = self.configfile["config"]
            self.video_record_config = self.configfile["video_record_config"]
            self.video_config = self.configfile["video_config"]
            self.audio_config = self.configfile["audio_config"]
            self.controller_config = self.configfile["controller_config"]
            self.fullscreen_key = getattr(Qt, f'Key_{self.config["fullscreen_key"]}')
            self.relative_mouse_speed = self.config["relative_mouse_speed"]
            if self.config["mouse_report_freq"] != 0:
                self.mouse_report_interval = 1000 / self.config["mouse_report_freq"]
                self.dynamic_mouse_report_interval = False
            else:
                self.mouse_report_interval = 10
                self.dynamic_mouse_report_interval = True
        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("Error"),
                f"Import config error:\n {e}\n\n"
                + self.tr(
                    "Check the config.yaml and restart the program\nor delete the config.yaml to reset the config file."
                ),
            )
            sys.exit(1)
        # 加载配置文件
        self.status = {
            "fullscreen": False,
            "topmost": False,
            "mouse_capture": False,
            "hide_cursor": False,
            "init_ok": False,
            "screen_height": 0,
            "screen_width": 0,
            "RGB_mode": False,
            "quick_paste": True,
            "relative_mouse": False,
        }

        # 获取显示器分辨率大小
        self.desktop = QGuiApplication.primaryScreen()
        self.status["screen_height"] = self.desktop.availableGeometry().height()
        self.status["screen_width"] = self.desktop.availableGeometry().width()

        # 窗口图标
        self.setWindowIcon(QIcon(f"{PATH}/icons/icon.ico"))
        self.device_setup_dialog.setWindowIcon(load_icon("import"))
        self.control_setup_dialog.setWindowIcon(load_icon("import"))
        self.shortcut_key_dialog.setWindowIcon(load_icon("keyboard-settings-outline"))
        self.paste_board_dialog.setWindowIcon(load_icon("paste"))
        self.indicator_dialog.setWindowIcon(load_icon("capslock"))
        self.numkeyboard_dialog.setWindowIcon(load_icon("numkey"))

        # 状态栏图标
        self.statusbar_lable1 = QLabel()
        self.statusbar_lable2 = QLabel()
        self.statusbar_lable3 = QLabel()
        self.statusbar_lable4 = QLabel()
        font = QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setBold(True)
        self.statusbar_lable1.setFont(font)
        self.statusbar_lable2.setFont(font)
        self.statusbar_lable3.setFont(font)
        self.statusbar_lable4.setFont(font)
        self.statusbar_lable1.setText("CTRL")
        self.statusbar_lable2.setText("SHIFT")
        self.statusbar_lable3.setText("ALT")
        self.statusbar_lable4.setText("META")
        self.statusbar_lable1.setStyleSheet("color: grey")
        self.statusbar_lable2.setStyleSheet("color: grey")
        self.statusbar_lable3.setStyleSheet("color: grey")
        self.statusbar_lable4.setStyleSheet("color: grey")

        self.statusbar_btn1 = MyPushButton()
        self.statusbar_btn2 = MyPushButton()
        self.statusbar_btn3 = MyPushButton()
        self.statusbar_btn4 = MyPushButton()
        self.statusbar_btn5 = MyPushButton()
        self.statusbar_btn1.setPixmap(load_pixmap("keyboard-settings-outline"))
        self.statusbar_btn2.setPixmap(load_pixmap("paste"))
        self.statusbar_btn3.setPixmap(load_pixmap("capslock"))
        self.statusbar_btn4.setPixmap(load_pixmap("numkey"))
        self.statusbar_btn5.setPixmap(load_pixmap("hook-off"))

        self.statusbar_icon1 = MyPushButton()
        self.statusbar_icon2 = MyPushButton()
        self.statusbar_icon3 = MyPushButton()
        self.statusbar_icon1.setPixmap(load_pixmap("video-off"))
        self.statusbar_icon2.setPixmap(load_pixmap("keyboard-off"))
        self.statusbar_icon3.setPixmap(load_pixmap("mouse-off"))

        self.statusBar().setStyleSheet("padding: 0px;")
        self.statusBar().addPermanentWidget(self.statusbar_lable1)
        self.statusBar().addPermanentWidget(self.statusbar_lable2)
        self.statusBar().addPermanentWidget(self.statusbar_lable3)
        self.statusBar().addPermanentWidget(self.statusbar_lable4)
        self.statusBar().addPermanentWidget(self.statusbar_btn1)
        self.statusBar().addPermanentWidget(self.statusbar_btn2)
        self.statusBar().addPermanentWidget(self.statusbar_btn3)
        self.statusBar().addPermanentWidget(self.statusbar_btn4)
        self.statusBar().addPermanentWidget(self.statusbar_btn5)
        self.statusBar().addPermanentWidget(self.statusbar_icon1)
        self.statusBar().addPermanentWidget(self.statusbar_icon2)
        self.statusBar().addPermanentWidget(self.statusbar_icon3)

        self.statusbar_btn1.clicked.connect(lambda: self.statusbar_func(1))
        self.statusbar_btn2.clicked.connect(lambda: self.statusbar_func(2))
        self.statusbar_btn3.clicked.connect(lambda: self.statusbar_func(3))
        self.statusbar_btn4.clicked.connect(lambda: self.statusbar_func(4))
        self.statusbar_btn5.clicked.connect(lambda: self.statusbar_func(5))
        self.statusbar_icon1.clicked.connect(lambda: self.statusbar_func(6))
        self.statusbar_icon2.clicked.connect(lambda: self.statusbar_func(7))
        self.statusbar_icon3.clicked.connect(lambda: self.statusbar_func(8))

        # 菜单栏图标
        self.action_video_devices.setIcon(load_icon("import"))
        self.action_video_device_connect.setIcon(load_icon("video"))
        self.action_video_device_disconnect.setIcon(load_icon("video-off"))
        self.actionMinimize.setIcon(load_icon("window-minimize"))
        self.actionexit.setIcon(load_icon("window-close"))
        self.action_control_setup.setIcon(load_icon("import"))
        self.actionReload_MCU.setIcon(load_icon("reload"))
        self.actionReload_Key_Mouse.setIcon(load_icon("reload"))
        self.action_fullscreen.setIcon(load_icon("fullscreen"))
        self.action_Resize_window.setIcon(load_icon("resize"))
        self.actionKeep_ratio.setIcon(load_icon("ratio"))
        self.actionResetKeyboard.setIcon(load_icon("reload"))
        self.actionResetMouse.setIcon(load_icon("reload"))
        self.menuShortcut_key.setIcon(load_icon("keyboard-outline"))
        self.actionCustomKey.setIcon(load_icon("keyboard-settings-outline"))
        self.actionCapture_mouse.setIcon(load_icon("mouse"))
        self.actionRelease_mouse.setIcon(load_icon("mouse-off"))
        self.actionOn_screen_Keyboard.setIcon(load_icon("keyboard-variant"))
        self.actionCalculator.setIcon(load_icon("calculator"))
        self.actionSnippingTool.setIcon(load_icon("monitor-screenshot"))
        self.actionNotepad.setIcon(load_icon("notebook-edit"))
        self.actionIndicator_light.setIcon(load_icon("capslock"))
        self.actionKeep_on_top.setIcon(load_icon("topmost"))
        self.actionPaste_board.setIcon(load_icon("paste"))
        self.actionHide_cursor.setIcon(load_icon("cursor"))
        self.actionCapture_frame.setIcon(load_icon("capture"))
        self.actionRecord_video.setIcon(load_icon("record"))
        self.actionRGB.setIcon(load_icon("RGB"))
        self.actionQuick_paste.setIcon(load_icon("quick_paste"))
        self.actionWindows_Audio_Setting.setIcon(load_icon("audio"))
        self.actionWindows_Device_Manager.setIcon(load_icon("device"))
        self.actionNum_Keyboard.setIcon(load_icon("numkey"))
        self.actionOpen_Server_Manager.setIcon(load_icon("server"))
        self.actionSystem_hook.setIcon(load_icon("hook"))
        self.actionRefresh_device_list.setIcon(load_icon("reload"))
        self.actionWeb_client.setIcon(load_icon("web"))
        self.actionRelative_mouse.setIcon(load_icon("relative"))

        if self.video_config["keep_aspect_ratio"]:
            self.set_checked(self.actionKeep_ratio, True)
        self.set_checked(self.actionQuick_paste, True)

        # 初始化监视器
        self.setCentralWidget(self.serverFrame)
        self.serverFrame.setHidden(True)
        self.videoWidget = QVideoWidget()
        self.videoWidget.setAttribute(Qt.WA_OpaquePaintEvent)
        self.takeCentralWidget()
        self.setCentralWidget(self.videoWidget)
        self.videoWidget.setMouseTracking(True)
        self.videoWidget.children()[0].setMouseTracking(True)
        self.videoWidget.hide()


        s_format = QSurfaceFormat.defaultFormat()
        s_format.setSwapInterval(0)
        QSurfaceFormat.setDefaultFormat(s_format)

        self.disconnect_label = QLabel()
        self.disconnect_label.setPixmap(load_pixmap("disconnected"))
        self.disconnect_label.setAlignment(Qt.AlignCenter)
        self.disconnect_label.setMouseTracking(True)
        self.takeCentralWidget()
        self.setCentralWidget(self.disconnect_label)
        self.disconnect_label.show()

        # 快捷键菜单设置快捷键名称
        for i, name in enumerate(self.configfile["shortcut_key"]["shortcut_key_name"]):
            action = self.menuShortcut_key.addAction(name)
            action.triggered.connect(lambda checked, i=i: self.shortcut_key_action(i))

        # 按键绑定
        self.action_video_device_connect.triggered.connect(
            lambda: self.set_device(True)
        )
        self.action_video_device_disconnect.triggered.connect(
            lambda: self.set_device(False)
        )
        self.action_video_devices.triggered.connect(self.device_config)
        self.action_control_setup.triggered.connect(self.controller_setup)
        self.actionCustomKey.triggered.connect(self.shortcut_key_func)
        self.actionReload_Key_Mouse.triggered.connect(lambda: self.reset_keymouse(4))
        self.actionMinimize.triggered.connect(self.window_minimized)
        self.actionexit.triggered.connect(sys.exit)

        self.device_setup_dialog.comboBox.currentIndexChanged.connect(
            self.update_device_info
        )

        self.action_fullscreen.triggered.connect(self.fullscreen_func)
        self.action_Resize_window.triggered.connect(self.resize_window_func)
        self.actionKeep_ratio.triggered.connect(self.keep_ratio_func)
        self.actionKeep_on_top.triggered.connect(self.topmost_func)
        self.actionCapture_frame.triggered.connect(self.capture_to_file)
        self.actionRecord_video.triggered.connect(self.record_video)

        self.actionRelease_mouse.triggered.connect(self.release_mouse)
        self.actionCapture_mouse.triggered.connect(self.capture_mouse)
        self.actionResetKeyboard.triggered.connect(lambda: self.reset_keymouse(1))
        self.actionResetMouse.triggered.connect(lambda: self.reset_keymouse(3))
        self.actionIndicator_light.triggered.connect(self.indicatorLight_func)
        self.actionReload_MCU.triggered.connect(lambda: self.reset_keymouse(2))

        self.actionPaste_board.triggered.connect(self.paste_board_func)
        self.actionHide_cursor.triggered.connect(self.hide_cursor_func)
        self.actionQuick_paste.triggered.connect(self.quick_paste_func)
        self.actionNum_Keyboard.triggered.connect(self.num_keyboard_func)
        self.actionSystem_hook.triggered.connect(self.system_hook_func)
        self.actionRelative_mouse.triggered.connect(self.relative_mouse_func)

        self.actionOn_screen_Keyboard.triggered.connect(
            lambda: self.menu_tools_actions(0)
        )
        self.actionCalculator.triggered.connect(lambda: self.menu_tools_actions(1))
        self.actionSnippingTool.triggered.connect(lambda: self.menu_tools_actions(2))
        self.actionNotepad.triggered.connect(lambda: self.menu_tools_actions(3))
        self.actionWindows_Audio_Setting.triggered.connect(
            lambda: self.menu_tools_actions(4)
        )
        self.actionWindows_Device_Manager.triggered.connect(
            lambda: self.menu_tools_actions(5)
        )

        self.actionOpen_Server_Manager.triggered.connect(self.open_server_manager)
        self.actionRefresh_device_list.triggered.connect(
            self.refresh_server_device_list
        )
        self.actionWeb_client.triggered.connect(self.open_web_client)

        self.actionRGB.triggered.connect(self.RGB_func)
        self.paste_board_dialog.pushButtonFile.clicked.connect(
            self.paste_board_file_select
        )

        self.kvmSetDeviceCombo.currentTextChanged.connect(
            self.update_server_device_info
        )

        self.actionAuthor.triggered.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://github.com/ElluIFX"))
        )
        self.actionRaw_author.triggered.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://github.com/Jackadminx"))
        )

        self.device_setup_dialog.checkBoxAudio.setChecked(
            self.audio_config["audio_support"]
        )
        self.device_setup_dialog.checkBoxAudio.stateChanged.connect(
            self.audio_checkbox_switch
        )
        self.audio_checkbox_switch()

        self.paste_board_dialog.spinBox_ci.setValue(
            self.configfile["paste_board"]["click_interval"]
        )
        self.paste_board_dialog.spinBox_ps.setValue(
            self.configfile["paste_board"]["packet_size"]
        )
        self.paste_board_dialog.spinBox_pw.setValue(
            self.configfile["paste_board"]["packet_wait"]
        )

        # 设置聚焦方式
        self.statusbar_btn1.setFocusPolicy(Qt.NoFocus)
        self.statusbar_btn2.setFocusPolicy(Qt.NoFocus)
        self.statusbar_btn3.setFocusPolicy(Qt.NoFocus)
        self.statusbar_btn4.setFocusPolicy(Qt.NoFocus)
        self.statusbar_btn5.setFocusPolicy(Qt.NoFocus)
        self.statusbar_icon1.setFocusPolicy(Qt.NoFocus)
        self.statusbar_icon2.setFocusPolicy(Qt.NoFocus)
        self.statusbar_icon3.setFocusPolicy(Qt.NoFocus)

        # self.camerafinder.setFocusPolicy(Qt.NoFocus)
        # self.statusBar().setFocusPolicy(Qt.NoFocus)
        # self.statusBar().setFocusPolicy(Qt.NoFocus)
        # self.setFocusPolicy(Qt.StrongFocus)

        self.mouse_action_timer = QTimer()
        self.mouse_action_timer.timeout.connect(self.mouse_action_timeout)
        self.indicator_timer = QTimer()
        self.indicator_timer.timeout.connect(self.update_indicatorLight)
        self.check_device_timer = QTimer()
        self.check_device_timer.timeout.connect(self.check_device_status)
        self.check_device_timer.start(1000)

        # hid_def.current_screen_size.update_screen_size(self.video_config["resolution_X"],
        #                                               self.video_config["resolution_Y"])
        self.reset_keymouse(4)

        self.mouse_scroll_timer = QTimer()
        self.mouse_scroll_timer.timeout.connect(self.mouse_scroll_stop)

        self._log_signal.connect(self.set_log_text)
        fake_std.callback = self._log_signal.emit
        self.server = KVM_Server(parent=self)
        self.server_simple_started = False
        self._wheel_signal.connect(self.mouse_wheel_act)

        self._last_mouse_report = time.perf_counter()
        self._new_mouse_report = 0
        self.rel_x = 0
        self.rel_y = 0
        self._mouse_report_timer = QTimer()
        self._mouse_report_timer.timeout.connect(self.mouse_report_timeout)
        self._mouse_report_timer.start(self.mouse_report_interval)
        self._hid_thread = HidThread()
        self._hid_signal = self._hid_thread._hid_signal
        self._hid_thread._event_signal.connect(self.device_event_handle)
        self._hid_thread.start()

        self.hook_state = False
        self.hook_manager = pyHook.HookManager()
        self.hook_manager.KeyDown = self.hook_keyboard_down_event
        self.hook_manager.KeyUp = self.hook_keyboard_up_event
        self.pythoncom_timer = QTimer()
        self.pythoncom_timer.timeout.connect(lambda: pythoncom.PumpWaitingMessages())
        self.hook_pressed_keys = []

        self.status["init_ok"] = True

        self.crash_devices = []

        self.camera_list_inited = False
        if self.video_config["auto_connect"]:
            self.device_setup_dialog.checkBoxAutoConnect.setChecked(True)
            QTimer().singleShot(1000, lambda: self.set_device(True, center=True))

    code_remap = {
        "Rcontrol": 0x011D,
        "Lwin": 0x015B,
        "Rwin": 0x015C,
    }

    def hook_keyboard_down_event(self, event):
        logger.debug(f"Hook: {event.Key} {event.ScanCode}")
        if event.Key in self.code_remap:
            scan_code = self.code_remap[event.Key]
        else:
            scan_code = event.ScanCode
        if scan_code not in self.hook_pressed_keys:
            self.hook_pressed_keys.append(scan_code)
            self.keyPress(scan_code)
        return False

    def hook_keyboard_up_event(self, event):
        if event.Key in self.code_remap:
            scan_code = self.code_remap[event.Key]
        else:
            scan_code = event.ScanCode
        self.keyRelease(scan_code)
        try:
            self.hook_pressed_keys.remove(scan_code)
        except ValueError:
            pass
        return False

    def statusbar_func(self, act):
        if act == 1:
            if self.shortcut_key_dialog.isVisible():
                self.shortcut_key_dialog.close()
            else:
                self.shortcut_key_func(0)
        elif act == 2:
            if self.paste_board_dialog.isVisible():
                self.paste_board_dialog.close()
            else:
                self.paste_board_func()
        elif act == 3:
            if self.indicator_dialog.isVisible():
                self.indicator_dialog.close()
            else:
                self.indicatorLight_func()
        elif act == 4:
            if self.numkeyboard_dialog.isVisible():
                self.numkeyboard_dialog.close()
            else:
                self.num_keyboard_func()
        elif act == 5:
            self.system_hook_func()
        elif act == 6:
            self.device_config()
        elif act == 7:
            self.reset_keymouse(4)
        elif act == 8:
            if self.status["mouse_capture"]:
                self.release_mouse()
                self.statusBar().showMessage(self.tr("Mouse capture off"))
            else:
                self.capture_mouse()

    def set_checked(self, attr, state):
        font = attr.font()
        font.setBold(state)
        attr.setFont(font)
        if attr.isCheckable():
            # attr.setChecked(bold)
            text = attr.text().replace(" ·", "")
            if state:
                text += " ·"
            attr.setText(text)

    def save_config(self):
        # 保存配置文件
        with open(os.path.join(ARGV_PATH, "config.yaml"), "w", encoding="utf-8") as f:
            yaml.dump(self.configfile, f)

    def audio_checkbox_switch(self):
        if self.device_setup_dialog.checkBoxAudio.isChecked():
            self.device_setup_dialog.comboBox_4.show()
            self.device_setup_dialog.comboBox_5.show()
            self.device_setup_dialog.label_4.show()
            self.device_setup_dialog.label_5.show()
            self.device_setup_dialog.label_7.show()
            self.device_setup_dialog.setMaximumHeight(270)
            self.device_setup_dialog.setMinimumHeight(270)
            self.update_audio_devices()
        else:
            self.device_setup_dialog.comboBox_4.hide()
            self.device_setup_dialog.comboBox_5.hide()
            self.device_setup_dialog.label_4.hide()
            self.device_setup_dialog.label_5.hide()
            self.device_setup_dialog.label_7.hide()
            self.device_setup_dialog.setMaximumHeight(200)
            self.device_setup_dialog.setMinimumHeight(200)
        self.device_setup_dialog.adjustSize()

    def update_audio_devices(self):
        self.device_setup_dialog.comboBox_4.clear()
        self.device_setup_dialog.comboBox_5.clear()
        self.device_setup_dialog.comboBox_4.addItem("Default")
        self.device_setup_dialog.comboBox_5.addItem("Default")
        in_devices = QMediaDevices.audioInputs()
        out_devices = QMediaDevices.audioOutputs()
        devices = ["Default"]
        for i in in_devices:
            self.device_setup_dialog.comboBox_4.addItem(i.description())
            devices.append(i.description())
        if self.audio_config["audio_device_in"] in devices:
            self.device_setup_dialog.comboBox_4.setCurrentText(
                self.audio_config["audio_device_in"]
            )
        else:
            self.device_setup_dialog.comboBox_4.setCurrentIndex(0)
        devices = ["Default"]
        for i in out_devices:
            self.device_setup_dialog.comboBox_5.addItem(i.description())
            devices.append(i.description())
        if self.audio_config["audio_device_out"] in devices:
            self.device_setup_dialog.comboBox_5.setCurrentText(
                self.audio_config["audio_device_out"]
            )
        else:
            self.device_setup_dialog.comboBox_5.setCurrentIndex(0)

    # 弹出采集卡设备设置窗口，并打开采集卡设备
    def device_config(self):
        if self.serverFrame.isVisible():
            QMessageBox.critical(
                self,
                self.tr("Error"),
                self.tr("Close KVM Server before local connection"),
            )
            return False

        self.device_setup_dialog.comboBox.clear()
        cameras = QMediaDevices.videoInputs()
        remember_name = self.video_config["device_name"]
        # self.video_config["device_name"] = ""
        devices = []
        for camera in cameras:
            self.device_setup_dialog.comboBox.addItem(camera.description())
            devices.append(camera.description())
        self.camera_list_inited = True
        if remember_name in devices:
            self.device_setup_dialog.comboBox.setCurrentText(remember_name)
            self.update_device_info()
            resolution_str = (
                str(self.video_config["resolution_X"])
                + "x"
                + str(self.video_config["resolution_Y"])
            )
            self.device_setup_dialog.comboBox_2.setCurrentText(resolution_str)
            self.device_setup_dialog.comboBox_3.setCurrentText(
                self.video_config["format"]
            )
        else:
            self.device_setup_dialog.comboBox.setCurrentIndex(0)
            self.update_device_info()
            self.device_setup_dialog.comboBox_2.setCurrentIndex(0)
            self.device_setup_dialog.comboBox_3.setCurrentIndex(0)
            try:
                self.video_config["resolution_X"] = (
                    self.device_setup_dialog.comboBox_2.currentText().split("x")[0]
                )
                self.video_config["resolution_Y"] = (
                    self.device_setup_dialog.comboBox_2.currentText().split("x")[1]
                )
            except IndexError:
                self.video_config["resolution_X"] = 0
                self.video_config["resolution_Y"] = 0
            self.video_config["format"] = (
                self.device_setup_dialog.comboBox_3.currentText()
            )

        if self.device_setup_dialog.checkBoxAudio.isChecked():
            self.update_audio_devices()

        wm_pos = self.geometry()
        wm_size = self.size()
        self.device_setup_dialog.move(
            wm_pos.x() + wm_size.width() / 2 - self.device_setup_dialog.width() / 2,
            wm_pos.y() + wm_size.height() / 2 - self.device_setup_dialog.height() / 2,
        )
        # 如果选择设备
        ret = self.device_setup_dialog.exec()

        if not ret:
            return
        try:
            self.video_config["device_name"] = (
                self.device_setup_dialog.comboBox.currentText()
            )
            self.video_config["resolution_X"] = int(
                self.device_setup_dialog.comboBox_2.currentText().split("x")[0]
            )
            self.video_config["resolution_Y"] = int(
                self.device_setup_dialog.comboBox_2.currentText().split("x")[1]
            )
            self.video_config["format"] = (
                self.device_setup_dialog.comboBox_3.currentText()
            )

            if self.device_setup_dialog.checkBoxAudio.isChecked():
                self.audio_config["audio_device_in"] = (
                    self.device_setup_dialog.comboBox_4.currentText()
                )
                self.audio_config["audio_device_out"] = (
                    self.device_setup_dialog.comboBox_5.currentText()
                )
        except Exception:
            self.video_alert(self.tr("Selected invalid device"))
            return
        logger.debug(self.video_config)
        try:
            self.set_device(True, center=True)
            self.video_config["auto_connect"] = (
                self.device_setup_dialog.checkBoxAutoConnect.isChecked()
            )
            self.audio_config["audio_support"] = (
                self.device_setup_dialog.checkBoxAudio.isChecked()
            )
            self.save_config()
        except Exception as e:
            logger.error(e)

    # 控制器设置
    def controller_setup(self):
        if os.name == 'nt':  # sys.platform == 'win32':
            from serial.tools.list_ports_windows import comports as list_comports
        elif os.name == 'posix':
            from serial.tools.list_ports_posix import comports as list_comports
        else:
            raise ImportError("Sorry: no implementation for your platform ('{}') available".format(os.name))
        self.control_setup_dialog.combobox_com_port.clear()
        port_info_list: serial.tools.list_ports.ListPortInfo = list_comports(include_links=False)
        for port_info in port_info_list:
            self.control_setup_dialog.combobox_com_port.addItem(port_info.name)
        self.control_setup_dialog.label_screen_x = self.video_config["resolution_X"]
        self.control_setup_dialog.label_screen_y = self.video_config["resolution_Y"]
        dialog_return_code = self.control_setup_dialog.exec()
        if dialog_return_code == 1:
            # 用户按下确定
            self.controller_config["controller_port"] = self.control_setup_dialog.combobox_com_port.currentText()
            self.controller_config["controller_screen_x"] = self.control_setup_dialog.line_edit_screen_x_size.text()
            self.controller_config["controller_screen_y"] = self.control_setup_dialog.line_edit_screen_y_size.text()
            self.save_config()
            self.reset_keymouse(4)
            pass
        else:
            # 用户按下取消
            pass

    # 获取采集卡分辨率
    def update_device_info(self):
        self.device_setup_dialog.comboBox_2.clear()
        self.device_setup_dialog.comboBox_3.clear()
        cameras = QMediaDevices.videoInputs()
        if not self.camera_list_inited:
            for camera in cameras:
                if camera.description() == self.video_config["device_name"]:
                    self.camera_info = camera
                    break
            else:
                logger.error(self.tr("Target video device not found"))
                self.camera_info = None
                return
        else:
            try:
                self.camera_info = cameras[
                    self.device_setup_dialog.comboBox.currentIndex()
                ]
            except IndexError:
                self.camera_info = None
                return
        res_list = []
        fmt_list = []
        for i in self.camera_info.videoFormats():
            resolutions_str = f"{i.resolution().width()}x{i.resolution().height()}"
            if resolutions_str not in res_list:
                res_list.append(resolutions_str)
                self.device_setup_dialog.comboBox_2.addItem(resolutions_str)
            fmt_str = i.pixelFormat().name.split("_")[1]
            if fmt_str not in fmt_list:
                fmt_list.append(fmt_str)
                self.device_setup_dialog.comboBox_3.addItem(fmt_str)

    def camera_error_occurred(self, error, string):
        error_s = (
            f"Device: {self.camera_info.description()}\nReturned: {error}\n\n"
            + self.tr("Device disconnected")
        )
        self.crash_devices.append(
            (
                self.camera,
                self.capture_session,
                self.image_capture,
                self.video_record,
            )
        )
        if self.audio_opened:
            self.crash_devices.append(
                (
                    self.audio_input,
                    self.audio_output,
                    self.audio_in_device,
                    self.audio_out_device,
                )
            )
        self.statusbar_icon1.setPixmap(load_pixmap("video-off"))
        self.camera_opened = False
        self.camera_info = None
        self.takeCentralWidget()
        self.setCentralWidget(self.disconnect_label)
        self.videoWidget.hide()
        self.disconnect_label.show()
        self.setWindowTitle("USB KVM Client")
        self.check_device_status()
        QMessageBox.critical(self, self.tr("Device Error"), error_s)

    def frame_changed(self, frame: QVideoFrame):
        self.videoWidget.videoSink().setVideoFrame(frame)
        self.videoWidget.update()
        self.videoWidget.repaint()

    # 初始化指定配置视频设备
    def setup_device(self):
        if self.serverFrame.isVisible():
            QMessageBox.critical(
                self,
                self.tr("Error"),
                self.tr("Close KVM Server before local connection"),
            )
            return False
        if self.camera_info is None:
            self.update_device_info()
            if self.camera_info is None:
                self.video_alert(self.tr("Target video device not found"))
                return False
        self.camera = QCamera(self.camera_info)
        for i in self.camera_info.videoFormats():
            if (
                i.resolution().width() == self.video_config["resolution_X"]
                and i.resolution().height() == self.video_config["resolution_Y"]
                and i.pixelFormat().name.split("_")[1] == self.video_config["format"]
            ):
                self.camera.setCameraFormat(i)
                break
        else:
            self.video_alert(
                self.tr("Unsupported combination of resolution and format")
            )
            return False

        if self.device_setup_dialog.checkBoxAudio.isChecked():
            in_devices = QMediaDevices.audioInputs()
            out_devices = QMediaDevices.audioOutputs()
            in_device_name = self.audio_config["audio_device_in"]
            out_device_name = self.audio_config["audio_device_out"]
            if in_device_name == "Default":
                in_device = QMediaDevices.defaultAudioInput()
            else:
                for i in in_devices:
                    if i.description() == in_device_name:
                        in_device = i
                        break
                else:
                    in_device = None
            if out_device_name == "Default":
                out_device = QMediaDevices.defaultAudioOutput()
            else:
                for i in out_devices:
                    if i.description() == out_device_name:
                        out_device = i
                        break
                else:
                    out_device = None
            if in_device is None or out_device is None:
                self.video_alert(self.tr("Audio device not found"))
                return False
            self.audio_in_device = in_device
            self.audio_out_device = out_device

        self.camera.errorOccurred.connect(self.camera_error_occurred)
        self.camera.start()
        if not self.camera.isActive():
            self.video_alert(self.tr("Video device connect failed"))
            return False

        self.capture_session = QMediaCaptureSession()
        self.capture_session.setCamera(self.camera)
        self.video_sink = QVideoSink()
        self.capture_session.setVideoSink(self.video_sink)
        # self.capture_session.setVideoOutput(self.videoWidget)
        self.video_sink.videoFrameChanged.connect(self.frame_changed)

        self.image_capture = QImageCapture(self.camera)
        self.capture_session.setImageCapture(self.image_capture)
        self.image_capture.setQuality(QImageCapture.Quality.VeryHighQuality)
        self.image_capture.setFileFormat(QImageCapture.FileFormat.PNG)
        self.image_capture.connect(
            self.image_capture, SIGNAL("imageCaptured(int,QImage)"), self.image_captured
        )

        self.video_record = QMediaRecorder(self.camera)
        self.capture_session.setRecorder(self.video_record)
        self.video_record.setQuality(
            getattr(QMediaRecorder.Quality, self.video_record_config["quality"])
        )
        self.video_record.setMediaFormat(QMediaFormat.FileFormat.MPEG4)
        self.video_record.setEncodingMode(
            getattr(
                QMediaRecorder.EncodingMode, self.video_record_config["encoding_mode"]
            )
        )
        self.video_record.setVideoBitRate(self.video_record_config["encoding_bitrate"])
        self.video_record.setVideoFrameRate(self.video_record_config["framerate"])
        self.video_record.setVideoResolution(QSize())
        self.video_recording = False

        if self.device_setup_dialog.checkBoxAudio.isChecked():
            self.audio_input = QAudioInput(self.audio_in_device)
            self.audio_output = QAudioOutput(self.audio_out_device)
            self.audio_input.setVolume(1)
            self.audio_output.setVolume(1)
            self.audio_input.setMuted(False)
            self.audio_output.setMuted(False)
            self.capture_session.setAudioInput(self.audio_input)
            self.capture_session.setAudioOutput(self.audio_output)
            self.audio_opened = True
            # self.video_record.setAudioBitRate(16)
            # self.video_record.setAudioSampleRate(48000)
            # self.video_record.record()
            logger.debug("Audio device ok")
        return True

    # 保存当前帧到文件
    def capture_to_file(self):
        if not self.camera_opened:
            return
        self.image_capture.capture()
        logger.debug("capture_to_file ok")

    def record_video(self):
        if not self.camera_opened:
            return
        if (
            self.video_record.recorderState()
            == QMediaRecorder.RecorderState.RecordingState
        ):
            self.video_record.stop()
        if not self.video_recording:
            file_name = QFileDialog.getSaveFileName(
                self,
                self.tr("Video save location"),
                "output.mp4",
                "Video (*.mp4)",
            )[0]
            if file_name == "":
                return
            self.video_record.setOutputLocation(QUrl.fromLocalFile(file_name))
            self.video_record.record()
            self.video_recording = True
            self.actionRecord_video.setText(self.tr("Stop recording"))
            self.statusBar().showMessage(self.tr("Video recording started"))
        else:
            self.video_record.stop()
            self.video_recording = False
            self.actionRecord_video.setText(self.tr("Record video"))
            self.statusBar().showMessage(self.tr("Video recording stopped"))

    def image_captured(self, id, preview):
        logger.debug("image_captured", id)
        file_name = QFileDialog.getSaveFileName(
            self,
            self.tr("Save Frame"),
            "untitled.png",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)",
        )[0]
        if file_name != "":
            preview.save(file_name)
            self.statusBar().showMessage(self.tr("Image saved to") + f" {file_name}")

    # 视频设备错误提示
    def video_alert(self, s):
        QMessageBox.critical(self, self.tr("Video Error"), s)

    # 启用和禁用视频设备
    def set_device(self, state, center=False):
        if self.serverFrame.isVisible():
            QMessageBox.critical(
                self,
                self.tr("Error"),
                self.tr("Close KVM Server before local connection"),
            )
            return False
        if state:
            if not self.setup_device():
                return
            if not self.status["fullscreen"]:
                self.resize_window_func(center=center)
            fps = self.camera.cameraFormat().maxFrameRate()
            self.device_event_handle("video_ok")
            self.takeCentralWidget()
            self.setCentralWidget(self.videoWidget)
            self.disconnect_label.hide()
            self.videoWidget.show()
            self.setWindowTitle(
                f"USB KVM Client - {self.video_config['resolution_X']}x{self.video_config['resolution_Y']} @ {fps:.1f}"
            )
            if self.dynamic_mouse_report_interval:
                self.mouse_report_interval = 1000 / fps
                self._mouse_report_timer.setInterval(self.mouse_report_interval)
        else:
            if not self.camera_opened:
                return
            self.camera.setActive(False)
            self.camera.deleteLater()
            self.capture_session.deleteLater()
            self.camera.deleteLater()
            self.image_capture.deleteLater()
            self.video_record.deleteLater()
            if self.audio_opened:
                self.audio_input.deleteLater()
                self.audio_output.deleteLater()
                del self.audio_in_device
                del self.audio_out_device
                self.audio_opened = False
            self.device_event_handle("video_close")
            self.takeCentralWidget()
            self.setCentralWidget(self.disconnect_label)
            self.videoWidget.hide()
            self.disconnect_label.show()
            self.setWindowTitle("USB KVM Client")

    # 捕获鼠标功能
    def capture_mouse(self):
        self.status["mouse_capture"] = True
        self.statusbar_icon3.setPixmap(load_pixmap("mouse"))
        self.statusBar().showMessage(
            self.tr("Mouse capture on (Press Right-Ctrl to release)")
        )
        self.set_ws2812b(0, 30, 30)

    # 释放鼠标功能
    def release_mouse(self):
        self.status["mouse_capture"] = False
        self._hid_signal.emit([2, 0, 0, 0, 0, 0, 0, 0, 0])
        self.statusbar_icon3.setPixmap(load_pixmap("mouse-off"))
        self.qt_sleep(10)
        self.set_ws2812b(30, 30, 0)

    # 通过视频设备分辨率调整窗口大小
    def resize_window_func(self, center=True):
        if self.status["fullscreen"]:
            return
        if self.status["screen_height"] - self.video_config["resolution_Y"] < 100:
            self.showNormal()
            self.resize(
                int(
                    self.status["screen_height"]
                    * (2 / 3)
                    * self.video_config["resolution_X"]
                    / (self.video_config["resolution_Y"] + 66)
                ),
                int(self.status["screen_height"] * (2 / 3)),
            )
            self.showMaximized()
        else:
            self.showNormal()
            self.resize(
                self.video_config["resolution_X"],
                self.video_config["resolution_Y"] + 66,
            )
            if center:
                qr = self.frameGeometry()
                cp = QGuiApplication.primaryScreen().availableGeometry().center()
                qr.moveCenter(cp)
                self.move(qr.topLeft())
        if self.video_config["keep_aspect_ratio"]:
            self.videoWidget.setAspectRatioMode(Qt.KeepAspectRatio)
        else:
            self.videoWidget.setAspectRatioMode(Qt.IgnoreAspectRatio)

    def keep_ratio_func(self):
        self.video_config["keep_aspect_ratio"] = not self.video_config[
            "keep_aspect_ratio"
        ]
        if self.video_config["keep_aspect_ratio"]:
            self.videoWidget.setAspectRatioMode(Qt.KeepAspectRatio)
            self.set_checked(self.actionKeep_ratio, True)
        else:
            self.videoWidget.setAspectRatioMode(Qt.IgnoreAspectRatio)
            self.set_checked(self.actionKeep_ratio, False)
        if not self.status["fullscreen"]:
            self.resize(self.width(), self.height() + 1)
        self.statusBar().showMessage(
            self.tr("Keep aspect ratio: ")
            + str_bool(self.video_config["keep_aspect_ratio"])
        )
        self.save_config()

    # 最小化窗口
    def window_minimized(self):
        self.showMinimized()

    # 重置键盘鼠标
    def reset_keymouse(self, s):
        if s == 1:  # keyboard
            for i in range(2, len(kb_buffer)):
                kb_buffer[i] = 0
            hidinfo = hid_def.hid_report(kb_buffer)
            if hidinfo == 1 or hidinfo == 4:
                self.device_event_handle("hid_error")
            elif hidinfo == 0:
                self.device_event_handle("hid_ok")
            self.shortcut_status(kb_buffer)
        elif s == 2:  # MCU
            self.set_ws2812b(255, 0, 0)
            self.qt_sleep(100)
            hidinfo = hid_def.hid_report([4, 0])
            if hidinfo == 1 or hidinfo == 4:
                self.device_event_handle("hid_error")
            elif hidinfo == 0:
                self.device_event_handle("hid_ok")
            self.statusbar_icon2.setPixmap(load_pixmap("keyboard-off"))
            self.status["mouse_capture"] = False
            self.statusbar_icon3.setPixmap(load_pixmap("mouse-off"))
        elif s == 3:  # mouse
            for i in range(2, len(mouse_buffer)):
                mouse_buffer[i] = 0
            for i in range(2, len(mouse_buffer_rel)):
                mouse_buffer[i] = 0
            hidinfo = hid_def.hid_report(mouse_buffer)
            hidinfo = hid_def.hid_report(mouse_buffer_rel)
            if hidinfo == 1 or hidinfo == 4:
                self.device_event_handle("hid_error")
            elif hidinfo == 0:
                self.device_event_handle("hid_ok")
        elif s == 4:  # hid
            hid_code = hid_def.init_usb(
                self.controller_config["controller_port"],
                self.controller_config["controller_baud"],
                self.controller_config["controller_screen_x"],
                self.controller_config["controller_screen_y"]
            )

            if hid_code == 0:
                self.device_event_handle("hid_init_ok")
                if self.status["mouse_capture"]:
                    self.set_ws2812b(0, 30, 30)
                else:
                    self.set_ws2812b(30, 30, 0)
            else:
                self.device_event_handle("hid_init_error")

    # 自定义组合键窗口
    def shortcut_key_func(self, s):
        if s == 1:  # release
            self._hid_signal.emit([1, 0, 0, 0, 0, 0, 0, 0, 0])
            return
        elif s == 2:  # pressed
            self._hid_signal.emit(self.shortcut_buffer)
            return
        elif s == 3:  # save
            text, ok = QInputDialog.getText(
                self, self.tr("Save shortcut key"), self.tr("Shortcut name:")
            )
            if ok:
                idx = len(self.configfile["shortcut_key"]["shortcut_key_name"])
                self.configfile["shortcut_key"]["shortcut_key_name"].append(text)
                self.configfile["shortcut_key"]["shortcut_key_hidcode"].append(
                    [_ for _ in self.shortcut_buffer]
                )
                logger.debug(f"save {text}={self.shortcut_buffer}")
                action = self.menuShortcut_key.addAction(text)
                action.triggered.connect(lambda: self.shortcut_key_action(idx))
                self.save_config()
            return

        wm_pos = self.geometry()
        wm_size = self.size()
        addheight = 0
        if self.paste_board_dialog.isVisible():
            addheight += self.paste_board_dialog.height() + 30
        if self.indicator_dialog.isVisible():
            addheight += self.indicator_dialog.height() + 30
        if not self.status["fullscreen"]:
            addheight += 34
        self.shortcut_key_dialog.move(
            wm_pos.x() + (wm_size.width() - self.shortcut_key_dialog.width()),
            wm_pos.y()
            + (wm_size.height() - self.shortcut_key_dialog.height() - 30 - addheight),
        )
        self.shortcut_buffer = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        if self.shortcut_key_dialog.isVisible():
            self.shortcut_key_dialog.activateWindow()
            return
        self.shortcut_key_dialog.exec()
        for i in range(2, len(kb_buffer)):
            kb_buffer[i] = 0
        self.shortcut_key_handle(0xFE)

    # 自定义组合键窗口按钮对应功能
    def shortcut_key_handle(self, s):
        if s == 0xFE:
            self.shortcut_key_dialog.pushButton_ctrl.setChecked(False)
            self.shortcut_key_dialog.pushButton_alt.setChecked(False)
            self.shortcut_key_dialog.pushButton_shift.setChecked(False)
            self.shortcut_key_dialog.pushButton_meta.setChecked(False)
            self.shortcut_key_dialog.pushButton_tab.setChecked(False)
            self.shortcut_key_dialog.pushButton_prtsc.setChecked(False)
            self.shortcut_key_dialog.keySequenceEdit.setKeySequence("")
            for i in range(2, len(self.shortcut_buffer)):
                self.shortcut_buffer[i] = 0
        if s == 0xFF:  # keySequenceChanged
            if (
                self.shortcut_key_dialog.keySequenceEdit.keySequence().count() == 0
            ):  # 去除多个复合键
                keysequence = ""
                return
            elif self.shortcut_key_dialog.keySequenceEdit.keySequence().count() == 1:
                keysequence = (
                    self.shortcut_key_dialog.keySequenceEdit.keySequence().toString()
                )
            else:
                keysequence = (
                    self.shortcut_key_dialog.keySequenceEdit.keySequence()
                    .toString()
                    .split(",")
                )
                self.shortcut_key_dialog.keySequenceEdit.setKeySequence(keysequence[0])
                keysequence = keysequence[0]

            if [s for s in shift_symbol if keysequence in s]:
                keysequence = "Shift+" + keysequence

            if len(re.findall("\\+", keysequence)) == 0:  # 没有匹配到+号，不是组合键
                self.shortcut_key_dialog.keySequenceEdit.setKeySequence(keysequence)
            else:
                if keysequence != "+":
                    keysequence_list = keysequence.split(
                        "+"
                    ).copy()  # 将复合键转换为功能键
                    if [s for s in keysequence_list if "Ctrl" in s]:
                        self.shortcut_key_dialog.pushButton_ctrl.setChecked(True)
                        self.shortcut_buffer[2] = self.shortcut_buffer[2] | 1
                    else:
                        self.shortcut_key_dialog.pushButton_ctrl.setChecked(False)

                    if [s for s in keysequence_list if "Alt" in s]:
                        self.shortcut_key_dialog.pushButton_alt.setChecked(True)
                        self.shortcut_buffer[2] = self.shortcut_buffer[2] | 4
                    else:
                        self.shortcut_key_dialog.pushButton_alt.setChecked(False)

                    if [s for s in keysequence_list if "Shift" in s]:
                        self.shortcut_key_dialog.pushButton_shift.setChecked(True)
                        self.shortcut_buffer[2] = self.shortcut_buffer[2] | 2
                    else:
                        self.shortcut_key_dialog.pushButton_shift.setChecked(False)

                    if [s for s in keysequence_list if "Meta" in s]:
                        self.shortcut_key_dialog.pushButton_meta.setChecked(True)
                        self.shortcut_buffer[2] = self.shortcut_buffer[2] | 8

                    self.shortcut_key_dialog.keySequenceEdit.setKeySequence(
                        keysequence_list[-1]
                    )
                    keysequence = keysequence_list[-1]
            try:
                mapcode = self.keyboard_code[keysequence.upper()]
            except Exception:
                logger.error("Hid query error")
                return
            self.shortcut_buffer[4] = int(mapcode, 16)  # 功能位

        if self.shortcut_key_dialog.pushButton_ctrl.isChecked() and s == 1:
            self.shortcut_buffer[2] = self.shortcut_buffer[2] | 1
        elif (self.shortcut_key_dialog.pushButton_ctrl.isChecked() is False) and s == 1:
            self.shortcut_buffer[2] = (
                self.shortcut_buffer[2] & 1 and self.shortcut_buffer[2] ^ 1
            )

        if self.shortcut_key_dialog.pushButton_alt.isChecked() and s == 4:
            self.shortcut_buffer[2] = self.shortcut_buffer[2] | 4
        elif (self.shortcut_key_dialog.pushButton_alt.isChecked() is False) and s == 4:
            self.shortcut_buffer[2] = (
                self.shortcut_buffer[2] & 4 and self.shortcut_buffer[2] ^ 4
            )

        if self.shortcut_key_dialog.pushButton_shift.isChecked() and s == 2:
            self.shortcut_buffer[2] = self.shortcut_buffer[2] | 2
        elif (
            self.shortcut_key_dialog.pushButton_shift.isChecked() is False
        ) and s == 2:
            self.shortcut_buffer[2] = (
                self.shortcut_buffer[2] & 2 and self.shortcut_buffer[2] ^ 2
            )

        if self.shortcut_key_dialog.pushButton_meta.isChecked() and s == 8:
            self.shortcut_buffer[2] = self.shortcut_buffer[2] | 8
        elif (self.shortcut_key_dialog.pushButton_meta.isChecked() is False) and s == 8:
            self.shortcut_buffer[2] = (
                self.shortcut_buffer[2] & 8 and self.shortcut_buffer[2] ^ 8
            )

        if self.shortcut_key_dialog.pushButton_tab.isChecked() and s == 0x2B:
            self.shortcut_buffer[8] = 0x2B
        elif (
            self.shortcut_key_dialog.pushButton_tab.isChecked() is False
        ) and s == 0x2B:
            self.shortcut_buffer[8] = 0

        if self.shortcut_key_dialog.pushButton_prtsc.isChecked() and s == 0x46:
            self.shortcut_buffer[9] = 0x46
        elif (
            self.shortcut_key_dialog.pushButton_prtsc.isChecked() is False
        ) and s == 0x46:
            self.shortcut_buffer[9] = 0

    # 菜单快捷键发送hid报文
    def shortcut_key_action(self, s):
        try:
            get = self.configfile["shortcut_key"]["shortcut_key_hidcode"][s]
        except Exception:
            return
        self._hid_signal.emit(get)
        self.qt_sleep(10)
        self._hid_signal.emit([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    # 设备事件处理
    def device_event_handle(self, s):
        if s == "hid_error":
            self.statusBar().showMessage(
                self.tr("Keyboard Mouse connect error, try to <Reload Key/Mouse>")
            )
            self.statusbar_icon2.setPixmap(load_pixmap("keyboard-off"))
            self.status["mouse_capture"] = False
            self.statusbar_icon3.setPixmap(load_pixmap("mouse-off"))
            self.device_connected = False
            self.check_device_timer.stop()
        elif s == "video_error":
            self.statusBar().showMessage(self.tr("Video device error"))
            self.statusbar_icon1.setPixmap(load_pixmap("video-off"))
            self.camera_opened = False
            self.check_device_timer.start(1000)
        elif s == "video_close":
            self.statusBar().showMessage(self.tr("Video device close"))
            self.statusbar_icon1.setPixmap(load_pixmap("video-off"))
            self.camera_opened = False
            self.statusbar_icon3.setPixmap(load_pixmap("mouse-off"))
            self.status["mouse_capture"] = False
            self.set_ws2812b(30, 30, 0)
            self.check_device_timer.start(1000)
        elif s == "hid_init_error":
            self.statusBar().showMessage(self.tr("Keyboard Mouse initialization error"))
            self.statusbar_icon2.setPixmap(load_pixmap("keyboard-off"))
            self.device_connected = False
            self.check_device_timer.stop()
        elif s == "hid_init_ok":
            self.statusBar().showMessage(self.tr("Keyboard Mouse initialization done"))
            self.statusbar_icon2.setPixmap(load_pixmap("keyboard"))
            self.device_connected = True
            self.check_device_timer.start(1000)
        elif s == "hid_ok":
            self.statusbar_icon2.setPixmap(load_pixmap("keyboard"))
            self.device_connected = True
            self.check_device_timer.start(1000)
        elif s == "video_ok":
            self.statusBar().showMessage(self.tr("Video device connected"))
            self.statusbar_icon1.setPixmap(load_pixmap("video"))
            self.status["mouse_capture"] = True
            self.statusbar_icon3.setPixmap(load_pixmap("mouse"))
            self.camera_opened = True
            self.set_ws2812b(0, 30, 30)
            self.check_device_timer.stop()
        elif s == "device_disconnect":
            self.statusBar().showMessage(self.tr("Device disconnect"))
            self.statusbar_icon2.setPixmap(load_pixmap("keyboard-off"))
            self.statusbar_icon3.setPixmap(load_pixmap("mouse-off"))
            self.status["mouse_capture"] = False
            self.device_connected = False
            self.check_device_timer.stop()
        elif s == "video_disconnect":
            self.statusBar().showMessage(self.tr("Device disconnect"))
            self.statusbar_icon1.setPixmap(load_pixmap("video-off"))
            self.camera_opened = False
            self.check_device_timer.stop()

    # 检查连接状态
    def check_device_status(self):
        if self.device_connected:
            if not hid_def.check_connection():
                self.device_event_handle("device_disconnect")
        # if self.camera_opened:
        #     if self.camera.availability() != QMultimedia.Available:
        #         self.device_event_handle("video_disconnect")

    # 菜单小工具
    def menu_tools_actions(self, s):
        if s == 0:
            os.popen("osk")
        elif s == 1:
            os.popen("calc")
        elif s == 2:
            os.popen("SnippingTool")
        elif s == 3:
            os.popen("notepad")
        elif s == 4:
            os.popen("rundll32.exe shell32.dll, Control_RunDLL mmsys.cpl")
        elif s == 5:
            os.popen("devmgmt.msc")

    # 状态栏显示组合键状态
    def shortcut_status(self, s=[0, 0, 0]):
        highlight_color = "color: black"
        if (s[2] & 1) or (s[2] & 16):
            self.statusbar_lable1.setStyleSheet(highlight_color)
        else:
            self.statusbar_lable1.setStyleSheet("color: grey")
        if (s[2] & 2) or (s[2] & 32):
            self.statusbar_lable2.setStyleSheet(highlight_color)
        else:
            self.statusbar_lable2.setStyleSheet("color: grey")

        if (s[2] & 4) or (s[2] & 64):
            self.statusbar_lable3.setStyleSheet(highlight_color)
        else:
            self.statusbar_lable3.setStyleSheet("color: grey")

        if (s[2] & 8) or (s[2] & 128):
            self.statusbar_lable4.setStyleSheet(highlight_color)
        else:
            self.statusbar_lable4.setStyleSheet("color: grey")

    def update_indicatorLight(self) -> None:
        reply = hid_def.hid_report([3, 0], True)
        if reply == 1 or reply == 2 or reply == 3 or reply == 4:
            self.device_event_handle("hid_error")
            self.indicator_timer.stop()
            return
        if reply[0] != 3:
            self.statusBar().showMessage(self.tr("Indicator reply error"))
            self.indicator_timer.stop()
            return
        self.indicator_dialog.pushButtonNum.setText(
            "[" + ((reply[2] & (1 << 0)) and "*" or " ") + "] Num Lock"
        )
        self.indicator_dialog.pushButtonCaps.setText(
            "[" + ((reply[2] & (1 << 1)) and "*" or " ") + "] Caps Lock"
        )
        self.indicator_dialog.pushButtonScroll.setText(
            "[" + ((reply[2] & (1 << 2)) and "*" or " ") + "] Scroll Lock"
        )
        if reply[2] & (1 << 0):
            self.numkeyboard_dialog.pushButton_1.setText("*Num\nLock")
        else:
            self.numkeyboard_dialog.pushButton_1.setText("Num\nLock")

    def indicatorLight_func(self):
        self.update_indicatorLight()
        if self.indicator_dialog.isVisible():
            self.indicator_dialog.activateWindow()
            return
        addheight = 0
        if not self.status["fullscreen"]:
            addheight += 34
        wm_pos = self.geometry()
        wm_size = self.size()
        if self.paste_board_dialog.isVisible():
            addheight += self.paste_board_dialog.height() + 30
        if self.shortcut_key_dialog.isVisible():
            addheight += self.shortcut_key_dialog.height() + 30
        self.indicator_dialog.move(
            wm_pos.x() + (wm_size.width() - self.indicator_dialog.width()),
            wm_pos.y()
            + (wm_size.height() - self.indicator_dialog.height() - 30 - addheight),
        )
        self.indicator_timer.start(500)
        self.indicator_dialog.exec()
        if not self.numkeyboard_dialog.isVisible():
            self.indicator_timer.stop()

    def num_keyboard_func(self):
        if self.numkeyboard_dialog.isVisible():
            self.numkeyboard_dialog.activateWindow()
            return
        wm_pos = self.geometry()
        wm_size = self.size()
        addheight = 0
        if not self.status["fullscreen"]:
            addheight += 34
        self.numkeyboard_dialog.move(
            wm_pos.x() + (wm_size.width() - self.numkeyboard_dialog.width()),
            wm_pos.y()
            + (wm_size.height() - self.numkeyboard_dialog.height() - 30 - addheight),
        )
        self.indicator_timer.start(500)
        self.numkeyboard_dialog.exec()
        if not self.indicator_dialog.isVisible():
            self.indicator_timer.stop()

    num_hid_dict = {
        1: 0x53,2: 0x54,3: 0x55,
        4: 0x56,8: 0x57,17: 0x58,
        12: 0x59,13: 0x5A,14: 0x5B,
        9: 0x5C,10: 0x5D,11: 0x5E,
        5: 0x5F,6: 0x60,7: 0x61,
        15: 0x62,16: 0x63,
        18:0x4B,19:0x4A,20:0x4E,
        21:0x4D,22:0x46,23:0x48,
        24:0xE7,25:0x65,26:0x49,
        27:0x66
    }  # fmt:skip

    def numboard_func(self, x, state):
        self.update_kb_hid(self.num_hid_dict[x], state)

    def set_ws2812b(self, r: int, g: int, b: int):
        r = min(max(int(r), 0), 255)
        g = min(max(int(g), 0), 255)
        b = min(max(int(b), 0), 255)
        self._hid_signal.emit([5, 0, r, g, b, 0])

    def quick_paste_func(self):
        self.status["quick_paste"] = not self.status["quick_paste"]
        self.set_checked(self.actionQuick_paste, self.status["quick_paste"])
        self.statusBar().showMessage(
            self.tr("Quick paste: ") + str_bool(self.status["quick_paste"])
        )

    def system_hook_func(self):
        self.hook_state = not self.hook_state
        self.set_checked(self.actionSystem_hook, self.hook_state)
        self.statusBar().showMessage(
            self.tr("System hook: ") + str_bool(self.hook_state)
        )
        if self.hook_state:
            self.pythoncom_timer.start(5)
            self.hook_manager.HookKeyboard()
            self.statusbar_btn5.setPixmap(load_pixmap("hook"))
        else:
            self.hook_manager.UnhookKeyboard()
            self.pythoncom_timer.stop()
            self.statusbar_btn5.setPixmap(load_pixmap("hook-off"))

    def relative_mouse_func(self):
        self.status["relative_mouse"] = not self.status["relative_mouse"]
        self.set_checked(self.actionRelative_mouse, self.status["relative_mouse"])
        # self.reset_keymouse(3)
        self.statusBar().showMessage(
            self.tr("Relative mouse: ") + str_bool(self.status["relative_mouse"])
        )

    # 粘贴板
    def paste_board_func(self):
        addheight = 0
        if self.shortcut_key_dialog.isVisible():
            addheight += self.shortcut_key_dialog.height() + 30
        if self.indicator_dialog.isVisible():
            addheight += self.indicator_dialog.height() + 30
        if not self.status["fullscreen"]:
            addheight += 34
        wm_pos = self.geometry()
        wm_size = self.size()
        self.paste_board_dialog.move(
            wm_pos.x() + (wm_size.width() - self.paste_board_dialog.width()),
            wm_pos.y()
            + (wm_size.height() - self.paste_board_dialog.height() - 30 - addheight),
        )
        self.paste_board_file_path = None
        self.paste_board_dialog.labelFile.setText("N/A")
        self.paste_board_dialog.spinBox_ci.setValue(
            self.configfile["paste_board"]["click_interval"]
        )
        self.paste_board_dialog.spinBox_ps.setValue(
            self.configfile["paste_board"]["packet_size"]
        )
        self.paste_board_dialog.spinBox_pw.setValue(
            self.configfile["paste_board"]["packet_wait"]
        )
        if self.paste_board_dialog.isVisible():
            self.paste_board_dialog.activateWindow()
            return
        dialog_return = self.paste_board_dialog.exec()
        if dialog_return == 1:
            self.paste_board_send()
        self.configfile["paste_board"]["click_interval"] = (
            self.paste_board_dialog.spinBox_ci.value()
        )
        self.configfile["paste_board"]["packet_size"] = (
            self.paste_board_dialog.spinBox_ps.value()
        )
        self.configfile["paste_board"]["packet_wait"] = (
            self.paste_board_dialog.spinBox_pw.value()
        )
        self.save_config()

    def paste_board_file_select(self):
        self.paste_board_dialog.hide()
        file_path = QFileDialog.getOpenFileName(
            self, self.tr("Select file"), "", "All Files(*.*)"
        )[0]
        self.paste_board_dialog.show()
        if os.path.isfile(file_path):
            file_size_kb = os.path.getsize(file_path) / 1024
            self.paste_board_file_path = file_path
            self.paste_board_dialog.labelFile.setText(
                os.path.basename(file_path) + f" ({file_size_kb:.2f} KB)"
            )

    def qt_sleep(self, t):
        if (t := int(t)) > 0:
            loop = QEventLoop()
            QTimer.singleShot(t, loop.quit)
            loop.exec()

    last_char = None
    char_idx = 0

    def send_char(self, c):
        char_buffer = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        shift = False
        if c == "\n":
            mapcode = self.keyboard_code["ENTER"]
        elif c == "\t":
            mapcode = self.keyboard_code["TAB"]
        elif c == " ":
            mapcode = self.keyboard_code["SPACE"]
        else:
            try:
                cq = strB2Q(c)
                mapcode = self.keyboard_code[cq.upper()]
                if cq.isupper():
                    shift = True
            except KeyError:
                return 2
        mapcode = int(mapcode, 16)
        if self.last_char == c:
            self.char_idx = (self.char_idx + 1) % 5
        else:
            self.char_idx = 0
        self.last_char = c
        char_buffer[self.char_idx + 4] = mapcode
        if c in shift_symbol or shift:
            char_buffer[2] |= 2
        self._hid_signal.emit(char_buffer)
        self.qt_sleep(self.paste_board_dialog.spinBox_ci.value())
        self._hid_signal.emit([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.qt_sleep(self.paste_board_dialog.spinBox_ci.value())

    def paste_board_stop(self):
        self.paste_board_stop_flag = True

    def paste_board_send(self, text=None):
        if text is None:
            idx = self.paste_board_dialog.tabWidget.currentIndex() + 1
            if idx == 10:
                self.paste_board_file_send()
                return
            if idx > 9:
                return
            text = getattr(
                self.paste_board_dialog, f"plainTextEdit_{idx}"
            ).toPlainText()
        text = text.replace("\r\n", "\n")
        total = len(text)
        if total == 0:
            return
        self.paste_board_dialog.pushButtonSend.setEnabled(False)
        self.ignore_event = True
        self.paste_board_stop_flag = False
        kb_buffer[2] = 0
        for i, c in enumerate(text):
            self.paste_board_dialog.setWindowTitle(
                self.tr("Paste board - Sending") + f" {i/total:.0%}"
            )
            self.send_char(c)
            if not self.device_connected:
                self.paste_board_dialog.setWindowTitle(
                    self.tr("Paste board - Error occurred")
                )
                break
            if self.paste_board_stop_flag:
                self.paste_board_dialog.setWindowTitle(
                    self.tr("Paste board - Force stopped")
                )
                break
        else:
            self.paste_board_dialog.setWindowTitle(self.tr("Paste board - Finished"))
        self.paste_board_dialog.pushButtonSend.setEnabled(True)
        self.ignore_event = False

    def paste_board_file_send(self):
        if self.paste_board_file_path is None:
            return
        echo_only = self.paste_board_dialog.checkBoxEcho.isChecked()
        PACKGE_SIZE = self.paste_board_dialog.spinBox_ps.value()
        PACKGE_WAIT = self.paste_board_dialog.spinBox_pw.value()
        if not echo_only:
            CMD_HEAD = "echo "
            CMD_TAIL0 = (
                f" | xxd -r -p > ./{os.path.basename(self.paste_board_file_path)}\n"
            )
            CMD_TAIL1 = (
                f" | xxd -r -p >> ./{os.path.basename(self.paste_board_file_path)}\n"
            )
        else:
            CMD_HEAD = 'echo -e -n "'
            CMD_TAIL0 = f'" > ./{os.path.basename(self.paste_board_file_path)}\n'
            CMD_TAIL1 = f'" >> ./{os.path.basename(self.paste_board_file_path)}\n'
        with open(self.paste_board_file_path, "rb") as f:
            data = f.read()
        data = data.hex()
        if echo_only:
            data = "\\x".join([data[i : i + 2] for i in range(0, len(data), 2)])
            data = "\\x" + data
        total = len(data)
        if total == 0:
            return
        self.paste_board_dialog.setWindowTitle(self.tr("Paste board - Sending file"))
        self.paste_board_dialog.pushButtonSend.setEnabled(False)
        self.ignore_event = True
        kb_buffer[2] = 0
        self.paste_board_dialog.progressBar.setValue(0)
        error = False
        self.paste_board_stop_flag = False
        cnt = 0
        PACKGE_SIZE -= len(CMD_HEAD) + max(len(CMD_TAIL0), len(CMD_TAIL1))
        for i in range(0, total, PACKGE_SIZE):
            part = data[i : i + PACKGE_SIZE]
            if i == 0:
                cmd = CMD_HEAD + part + CMD_TAIL0
            else:
                cmd = CMD_HEAD + part + CMD_TAIL1
            cnt += len(part)
            print(f"\rSend: {i} {cnt} {total}         ", end="")
            now = int(i / total * 100)
            next = int((i + PACKGE_SIZE) / total * 100)
            next = min(next, 100)
            self.paste_board_dialog.progressBar.setValue(now)
            cmd_len = len(cmd)
            for j, c in enumerate(cmd):
                if self.send_char(c) == 1:
                    self.paste_board_dialog.setWindowTitle(
                        self.tr("Paste board - Error occurred")
                    )
                    error = True
                    break
                if self.paste_board_stop_flag:
                    self.paste_board_dialog.setWindowTitle(
                        self.tr("Paste board - Force stopped")
                    )
                    error = True
                    break
                self.paste_board_dialog.progressBar.setValue(
                    round(now + (next - now) * j / cmd_len)
                )
            if error:
                break
            self.qt_sleep(PACKGE_WAIT)
        else:
            self.paste_board_dialog.setWindowTitle(self.tr("Paste board - Finished"))
            self.paste_board_dialog.progressBar.setValue(100)
        self.paste_board_dialog.pushButtonSend.setEnabled(True)
        self.ignore_event = False

    # 三个Lock键
    def lock_key_func(self, key):
        if key == 1:  # Caps Lock
            key_code = self.keyboard_code["CAPSLOCK"]
        elif key == 2:  # Num Lock
            key_code = self.keyboard_code["NUMLOCK"]
        elif key == 3:  # Scroll Lock
            key_code = self.keyboard_code["SCROLLLOCK"]
        key_code = int(key_code, 16)
        self.update_kb_hid(key_code, True)
        self.qt_sleep(50)
        self.update_kb_hid(key_code, False)
        self.qt_sleep(50)
        self.update_indicatorLight()

    def RGB_func(self):
        self.status["RGB_mode"] = not self.status["RGB_mode"]
        self.set_checked(self.actionRGB, self.status["RGB_mode"])
        self.statusBar().showMessage(
            self.tr("RGB Indicator: ") + str_bool(self.status["RGB_mode"])
        )
        if not self.status["RGB_mode"]:
            if self.status["mouse_capture"]:
                self.set_ws2812b(0, 30, 30)
            else:
                self.set_ws2812b(30, 30, 0)

    # 全屏幕切换
    def fullscreen_func(self):
        self.status["fullscreen"] = not self.status["fullscreen"]
        if self.status["fullscreen"]:
            if not self.config["fullscreen_alert_showed"]:
                alert = QMessageBox(self)
                alert.setWindowTitle(self.tr("Fullscreen"))
                alert.setText(
                    self.tr("Press Ctrl+Alt+Shift+")
                    + f"{self.config['fullscreen_key']} "
                    + self.tr("to toggle fullscreen")
                    + self.tr("\n(Key ")
                    + f"{self.config['fullscreen_key']} "
                    + self.tr("can be changed in config.yaml)")
                    + self.tr("\nStay cursor at left top corner to show toolbar")
                )
                alert.Ok = alert.addButton(
                    self.tr("I know it, don't show again"), QMessageBox.AcceptRole
                )
                alert.exec()
                self.config["fullscreen_alert_showed"] = True
                self.save_config()
            self.showFullScreen()
            self.action_fullscreen.setChecked(True)
            self.action_Resize_window.setEnabled(False)
            self.statusBar().hide()
            self.menuBar().hide()
            self.set_checked(self.action_fullscreen, True)
        else:
            self.showNormal()
            self.action_fullscreen.setChecked(False)
            self.action_Resize_window.setEnabled(True)
            self.statusBar().show()
            self.menuBar().show()
            self.set_checked(self.action_fullscreen, False)

    # 隐藏指针
    def hide_cursor_func(self):
        self.status["hide_cursor"] = not self.status["hide_cursor"]
        if self.status["hide_cursor"]:
            self.set_checked(self.actionHide_cursor, True)
        else:
            self.set_checked(self.actionHide_cursor, False)
        self.statusBar().showMessage(
            self.tr("Hide cursor when capture mouse: ")
            + str_bool(self.status["hide_cursor"])
        )

    # 保持窗口在最前
    def topmost_func(self):
        self.status["topmost"] = not self.status["topmost"]
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint if self.status["topmost"] else Qt.Widget
        )
        self.show()
        self.statusBar().showMessage(
            self.tr("Window always on top: ") + str_bool(self.status["topmost"])
        )
        self.set_checked(self.actionKeep_on_top, self.status["topmost"])

    # 窗口失焦事件
    def changeEvent(self, event):
        try:  # 窗口未初始化完成时会触发一次事件
            if self.status is None:
                return
        except AttributeError:
            logger.debug("status Variable not initialized")
        except Exception as e:
            logger.error(e)
        else:
            if (
                not self.isActiveWindow() and self.status["init_ok"]
            ):  # 窗口失去焦点时重置键盘，防止卡键
                self.reset_keymouse(1)

    def mouseButton_to_int(self, s: Qt.MouseButton):
        if s == Qt.LeftButton:
            return 1
        elif s == Qt.RightButton:
            return 2
        elif s == Qt.MiddleButton:
            return 4
        elif s == Qt.XButton1:
            return 8
        elif s == Qt.XButton2:
            return 16
        else:
            return 0

    # 鼠标按下事件
    _last_click_time = 0

    def mousePressEvent(self, event):
        if self.ignore_event:
            return
        if (
            not self.status["mouse_capture"]
            and self.device_connected
            and event.button() == Qt.LeftButton
            and self.camera_opened
        ):
            if time.perf_counter() - self._last_click_time < 0.2:
                self.capture_mouse()
            else:
                self._last_click_time = time.perf_counter()
                self.statusBar().showMessage(self.tr("Double click to capture mouse"))
        if not self.status["mouse_capture"]:
            return
        if not self.status["relative_mouse"]:
            buffer = mouse_buffer
        else:
            buffer = mouse_buffer_rel
        buffer[2] = buffer[2] | self.mouseButton_to_int(event.button())
        self._hid_signal.emit(buffer)

    # 鼠标松开事件
    def mouseReleaseEvent(self, event):
        if self.ignore_event:
            return
        if not self.status["mouse_capture"]:
            return
        if not self.status["relative_mouse"]:
            buffer = mouse_buffer
        else:
            buffer = mouse_buffer_rel
        buffer[2] = buffer[2] ^ self.mouseButton_to_int(event.button())
        if buffer[2] < 0 or buffer[2] > 7:
            buffer[2] = 0
        self._hid_signal.emit(buffer)

    # 鼠标滚动事件
    def wheelEvent(self, event):
        if self.ignore_event:
            return
        if not self.status["mouse_capture"]:
            return
        if not self.status["relative_mouse"]:
            buffer = mouse_buffer
            bit = 7
        else:
            buffer = mouse_buffer_rel
            bit = 5
        if event.angleDelta().y() == 120:
            buffer[bit] = 0x01
        elif event.angleDelta().y() == -120:
            buffer[bit] = 0xFF
        else:
            buffer[bit] = 0
        self._hid_signal.emit(buffer)
        if self.mouse_scroll_timer.isActive():
            self.mouse_scroll_timer.stop()
        self.mouse_scroll_timer.start(100)

    def mouse_scroll_stop(self):
        self.mouse_scroll_timer.stop()
        if not self.status["relative_mouse"]:
            buffer = mouse_buffer
            bit = 7
        else:
            buffer = mouse_buffer_rel
            bit = 5
        buffer[bit] = 0
        self._hid_signal.emit(buffer)

    def mouse_action_timeout(self):
        if self.mouse_action_target == "menuBar":
            self.menuBar().show()
        elif self.mouse_action_target == "statusBar":
            self.statusBar().show()
        self.mouse_action_timer.stop()

    def hid_report(self, buf: list[int]):
        hidinfo = hid_def.hid_report(buf)
        if hidinfo == 1 or hidinfo == 4:
            self.device_event_handle("hid_error")

    # 鼠标移动事件
    _last_mouse_pos = None

    def mouseMoveEvent(self, event):
        super(QMainWindow, self).mouseMoveEvent(event)
        if self.ignore_event:
            return
        p = event.position().toPoint()
        x, y = p.x(), p.y()
        if self.status["fullscreen"]:
            if (y < 2 and x < 2) or (x > self.width() - 2 and y > self.height() - 2):
                if (
                    (y < 2 and x < 2)
                    and self.menuBar().isHidden()
                    and not self.mouse_action_timer.isActive()
                ):
                    self.mouse_action_target = "menuBar"
                    self.mouse_action_timer.start(500)
                elif (
                    (x > self.width() - 2 and y > self.height() - 2)
                    and self.statusBar().isHidden()
                    and not self.mouse_action_timer.isActive()
                ):
                    self.mouse_action_target = "statusBar"
                    self.mouse_action_timer.start(500)
            else:
                if not self.menuBar().isHidden():
                    self.menuBar().hide()
                if not self.statusBar().isHidden():
                    self.statusBar().hide()
                if self.mouse_action_timer.isActive():
                    self.mouse_action_timer.stop()
        if not (self.status["mouse_capture"]):
            self.setCursor(Qt.ArrowCursor)
            return
        if self.status["hide_cursor"] or self.status["relative_mouse"]:
            self.setCursor(Qt.BlankCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
        if not self.status["relative_mouse"]:
            self._last_mouse_pos = None
            if not self.camera_opened:
                x_res = self.disconnect_label.width()
                y_res = self.disconnect_label.height()
                width = self.disconnect_label.width()
                height = self.disconnect_label.height()
                # x_pos = self.disconnect_label.pos().x()
                y_pos = self.disconnect_label.pos().y()
            else:
                x_res = self.video_config["resolution_X"]
                y_res = self.video_config["resolution_Y"]
                width = self.videoWidget.width()
                height = self.videoWidget.height()
                # x_pos = self.videoWidget.pos().x()
                y_pos = self.videoWidget.pos().y()
            x_diff = 0
            y_diff = 0
            if self.video_config["keep_aspect_ratio"]:
                cam_scale = y_res / x_res
                finder_scale = height / width
                if finder_scale > cam_scale:
                    x_diff = 0
                    y_diff = height - width * cam_scale
                elif finder_scale < cam_scale:
                    x_diff = width - height / cam_scale
                    y_diff = 0
            x_hid = (x - x_diff / 2) / (width - x_diff)
            y_hid = (y - y_diff / 2 - y_pos) / (height - y_diff)
            x_hid = max(min(x_hid, 1), 0)
            y_hid = max(min(y_hid, 1), 0)
            if self.status["RGB_mode"]:
                self.set_ws2812b(
                    x_hid * 255, y_hid * 255, (1 - x_hid) * (1 - y_hid) * 255
                )
            self.statusBar().showMessage(f"X={x_hid*x_res:.0f}, Y={y_hid*y_res:.0f}")
            t = time.perf_counter()
            self._last_mouse_report = t
            x_hid = int(x_hid * 0x7FFF)
            y_hid = int(y_hid * 0x7FFF)
            mouse_buffer[3] = x_hid & 0xFF
            mouse_buffer[4] = x_hid >> 8
            mouse_buffer[5] = y_hid & 0xFF
            mouse_buffer[6] = y_hid >> 8
            self._new_mouse_report = 1
        else:
            middle_pos = self.mapToGlobal(QPoint(self.width() / 2, self.height() / 2))
            mouse_pos = QCursor.pos()
            if self._last_mouse_pos is not None:
                self.rel_x += (
                    mouse_pos.x() - self._last_mouse_pos.x()
                ) * self.relative_mouse_speed
                self.rel_y += (
                    mouse_pos.y() - self._last_mouse_pos.y()
                ) * self.relative_mouse_speed
                self._new_mouse_report = 2
                self._last_mouse_pos = mouse_pos
                if (
                    abs(mouse_pos.x() - middle_pos.x()) > 25
                    or abs(mouse_pos.y() - middle_pos.y()) > 25
                ):
                    QCursor.setPos(middle_pos)
                    self._last_mouse_pos = middle_pos
            else:
                self._last_mouse_pos = middle_pos
                QCursor.setPos(middle_pos)

    def mouse_report_timeout(self):
        if self._new_mouse_report == 1:
            self._hid_signal.emit(mouse_buffer)
        elif self._new_mouse_report == 2:
            x_hid = round(self.rel_x)
            y_hid = round(self.rel_y)
            self.rel_x -= x_hid
            self.rel_y -= y_hid
            x_hid = max(min(x_hid, 127), -127)
            y_hid = max(min(y_hid, 127), -127)
            x_hid += 0xFF if x_hid < 0 else 0
            y_hid += 0xFF if y_hid < 0 else 0
            mouse_buffer_rel[3] = x_hid & 0xFF
            mouse_buffer_rel[4] = y_hid & 0xFF
            self._hid_signal.emit(mouse_buffer_rel)
            mouse_buffer_rel[3] = 0
            mouse_buffer_rel[4] = 0
        self._new_mouse_report = 0

    scan_to_b2 = {
        0x001D: 1,  # Left Control
        0x002A: 2,  # Left Shift
        0x0038: 4,  # Left Alt
        0x015B: 8,  # Left GUI
        0x011D: 16,  # Right Control
        0x0036: 32,  # Right Shift
        0x0138: 64,  # Right Alt
        0x015C: 128,  # Right GUI
    }

    hid_to_b2 = {
        0xE0: 1,  # Left Control
        0xE1: 2,  # Left Shift
        0xE2: 4,  # Left Alt
        0xE3: 8,  # Left GUI
        0xE4: 16,  # Right Control
        0xE5: 32,  # Right Shift
        0xE6: 64,  # Right Alt
        0xE7: 128,  # Right GUI
    }

    def update_kb(self, scancode: int, state: bool):
        if state:
            if scancode in self.scan_to_b2:
                kb_buffer[2] |= self.scan_to_b2[scancode]
            else:
                scancode2hid = self.keyboard_scancode2hid.get(scancode, 0)
                if scancode2hid == 0:
                    if scancode != 256:
                        logger.warning(f"scancode2hid not found: {scancode}")
                    return
                for i in range(4, 10):
                    if kb_buffer[i] == scancode2hid:
                        return
                    if kb_buffer[i] == 0:
                        kb_buffer[i] = scancode2hid
                        break
                else:
                    logger.warning("Buffer overflow")
        else:
            if scancode in self.scan_to_b2:
                kb_buffer[2] &= ~self.scan_to_b2[scancode]
            else:
                scancode2hid = self.keyboard_scancode2hid.get(scancode, 0)
                if scancode2hid == 0:
                    if scancode != 256:
                        logger.warning(f"scancode2hid not found: {scancode}")
                    return
                for i in range(4, 10):
                    if kb_buffer[i] == scancode2hid:
                        kb_buffer[i] = 0
                        break
                else:
                    logger.warning("Key not found in buffer")
        if not self.device_connected:
            return 0
        self._hid_signal.emit(kb_buffer)
        return 0

    def update_kb_hid(self, hid: int, state: bool):
        if state:
            if hid in self.hid_to_b2:
                kb_buffer[2] |= self.hid_to_b2[hid]
            else:
                for i in range(4, 10):
                    if kb_buffer[i] == hid:
                        return
                    if kb_buffer[i] == 0:
                        kb_buffer[i] = hid
                        break
                else:
                    logger.warning("Buffer overflow")
        else:
            if hid in self.hid_to_b2:
                kb_buffer[2] &= ~self.hid_to_b2[hid]
            else:
                for i in range(4, 10):
                    if kb_buffer[i] == hid:
                        kb_buffer[i] = 0
                        break
                else:
                    logger.warning("Key not found in buffer")
        self._hid_signal.emit(kb_buffer)
        return 0

    # 键盘按下事件
    def keyPressEvent(self, event):
        if self.ignore_event:
            return
        if event.isAutoRepeat():
            return
        # Ctrl+Alt+Shift+F11 退出全屏
        if kb_buffer[2] == 7 and event.key() == self.fullscreen_key:
            self.fullscreen_func()
            return
        self.keyPress(event.nativeScanCode())

    def keyPress(self, scancode: int):
        # Ctrl+Alt+Shift+V quick paste
        if kb_buffer[2] == 7 and scancode == 0x002F and self.status["quick_paste"]:
            # 获取剪贴板内容
            clipboard = QApplication.clipboard()
            text = clipboard.text()
            if len(text) == 0:
                self.statusBar().showMessage(self.tr("Clipboard is empty"))
                return
            self.statusBar().showMessage(
                self.tr("Quick pasting") + f" {len(text)} " + self.tr("characters")
            )
            self.paste_board_send(text)
            return
        if scancode == 285:  # Right Ctrl
            self.release_mouse()
            self.statusBar().showMessage(self.tr("Mouse capture off"))
        if self.status["RGB_mode"]:
            self.set_ws2812b(
                *hsv_to_rgb(random.random(), random.randint(6, 10) / 10, 0.4)
            )
        self.update_kb(scancode, True)
        self.shortcut_status(kb_buffer)

    # 键盘松开事件
    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            return
        if self.ignore_event:
            return
        self.keyRelease(event.nativeScanCode())

    def keyRelease(self, scancode: int):
        self.update_kb(scancode, False)
        self.shortcut_status(kb_buffer)

    def closeEvent(self, event):
        # os._exit(0)
        pass

    @Slot()
    def on_btnServerSwitch_clicked(self):
        if self.server.running:
            self.server.stop_server()
            self.btnServerSwitch.setIcon(load_icon("Play"))
            logger.info("Server stopped")
            self.kvmSetPortSpin.setEnabled(True)
            self.kvmSetHostLine.setEnabled(True)
            self.kvmSetQualitySpin.setEnabled(True)
            self.kvmSetFormatCombo.setEnabled(True)
            self.kvmSetDeviceCombo.setEnabled(True)
            self.kvmSetResCombo.setEnabled(True)
        else:
            if (
                self.kvmSetDeviceCombo.currentText() == ""
                or self.kvmSetResCombo.currentText() == ""
            ):
                QMessageBox.warning(self, self.tr("Warning"), self.tr("Invalid device"))
                return
            self.server.config["video"]["quality"] = self.kvmSetQualitySpin.value()
            width, height = self.kvmSetResCombo.currentText().split("x")
            self.server.config["video"]["width"] = int(width)
            self.server.config["video"]["height"] = int(height)
            self.server.config["video"]["format"] = self.kvmSetFormatCombo.currentText()
            self.server.command_callback = self.server_command_callback
            try:
                host = self.kvmSetHostLine.text()
                port = self.kvmSetPortSpin.value()
                self.server.start_server(
                    host=host,
                    device=self.kvmSetDeviceCombo.currentText(),
                    port=port,
                )
            except Exception as e:
                self.server.running = False
                logger.error(f"Server start failed: {e}")
                QMessageBox.warning(
                    self, self.tr("Warning"), f"Server start failed: {e}"
                )
                return
            self.btnServerSwitch.setIcon(load_icon("Pause"))
            self.kvmSetPortSpin.setEnabled(False)
            self.kvmSetHostLine.setEnabled(False)
            self.kvmSetQualitySpin.setEnabled(False)
            self.kvmSetFormatCombo.setEnabled(False)
            self.kvmSetDeviceCombo.setEnabled(False)
            self.kvmSetResCombo.setEnabled(False)
            logger.info(f"Server hosting on {host}:{port}")

    @Slot()
    def on_btnServerSetAuth_clicked(self):
        # ask if auth is enabled
        box = QMessageBox(self)
        box.setWindowTitle(self.tr("HTTP Authentication"))
        if self.server.auth_required:
            box.setText(
                self.tr("Authentication is enabled") + f" ({count_auth_users()} users)"
            )
            box.b1 = box.addButton(self.tr("Disable"), QMessageBox.ActionRole)
        else:
            box.setText(self.tr("Authentication is disabled"))
            box.b1 = box.addButton(self.tr("Enable"), QMessageBox.ActionRole)
        box.b2 = box.addButton(self.tr("Add User"), QMessageBox.ActionRole)
        box.b3 = box.addButton(self.tr("Cancel"), QMessageBox.RejectRole)
        box.exec()
        if box.clickedButton() == box.b1:
            self.server.auth_required = not self.server.auth_required
            logger.info(
                self.tr("Authentication enabled")
                if self.server.auth_required
                else self.tr("Authentication disabled")
            )
            if self.server.auth_required and not count_auth_users():
                logger.warning(self.tr("No user found, remember to add one"))
        elif box.clickedButton() == box.b2:
            username, ret = QInputDialog.getText(
                self, self.tr("Add User"), self.tr("Username:"), QLineEdit.Normal, ""
            )
            if not ret:
                return
            password, ret = QInputDialog.getText(
                self, self.tr("Add User"), self.tr("Password:"), QLineEdit.Normal, ""
            )
            if not ret:
                return
            add_auth_user(username, password)
            logger.info(f"User {username} added")

    def refresh_server_device_list(self):
        self.kvmSetDeviceCombo.clear()
        cameras = QMediaDevices.videoInputs()
        devices = []
        rmbd = self.video_config["device_name"]
        for camera in cameras:
            self.kvmSetDeviceCombo.addItem(camera.description())
            devices.append(camera.description())
        if rmbd in devices:
            self.kvmSetDeviceCombo.setCurrentText(rmbd)
        else:
            self.kvmSetDeviceCombo.setCurrentIndex(0)
        self.update_server_device_info()

    def update_server_device_info(self):
        self.kvmSetResCombo.clear()
        self.kvmSetFormatCombo.clear()
        selected = self.kvmSetDeviceCombo.currentText()
        cameras = QMediaDevices.videoInputs()
        for camera in cameras:
            if camera.description() == selected:
                camera_info = camera
                break
        else:
            return
        res_list = []
        fmt_list = []
        for i in camera_info.videoFormats():
            resolutions_str = f"{i.resolution().width()}x{i.resolution().height()}"
            if resolutions_str not in res_list:
                res_list.append(resolutions_str)
                self.kvmSetResCombo.addItem(resolutions_str)
            fmt = i.pixelFormat().name.split("_")[1]
            if fmt not in fmt_list:
                fmt_list.append(fmt)
                self.kvmSetFormatCombo.addItem(fmt)
        if camera_info.description() == self.video_config["device_name"]:
            self.kvmSetResCombo.setCurrentText(
                f"{self.video_config['resolution_X']}x{self.video_config['resolution_Y']}"
            )
            self.kvmSetFormatCombo.setCurrentText(self.video_config["format"])

    def open_server_manager(self):
        if not self.serverFrame.isVisible():
            if self.camera_opened:
                ret = QMessageBox.warning(
                    self,
                    self.tr("Warning"),
                    self.tr("Video device is opened, close it?"),
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                if ret == QMessageBox.Yes:
                    self.set_device(False)
                else:
                    return
            self.takeCentralWidget()
            self.setCentralWidget(self.serverFrame)
            self.disconnect_label.hide()
            self.serverFrame.show()
            self.actionOpen_Server_Manager.setText(self.tr("Close Server Manager"))
            self.refresh_server_device_list()
            self.btnServerSwitch.setIcon(load_icon("Play"))
            self.btnServerOpenBrowser.setIcon(load_icon("Safari"))
            self.btnServerSetAuth.setIcon(load_icon("Lock"))
        else:
            if self.server.running:
                ret = QMessageBox.warning(
                    self,
                    self.tr("Warning"),
                    self.tr("Server is running, stop it?"),
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                if ret == QMessageBox.Yes:
                    self.on_btnServerSwitch_clicked()
                else:
                    return
            self.takeCentralWidget()
            self.setCentralWidget(self.disconnect_label)
            self.serverFrame.hide()
            self.disconnect_label.show()
            self.actionOpen_Server_Manager.setText(self.tr("Open Server Manager"))

    @Slot()
    def on_btnServerOpenBrowser_clicked(self):
        url = f"http://127.0.0.1:{self.kvmSetPortSpin.value()}"
        QDesktopServices.openUrl(QUrl(url))

    def open_web_client(self):
        if not self.serverFrame.isVisible():
            if self.camera_opened:
                ret = QMessageBox.warning(
                    self,
                    self.tr("Warning"),
                    self.tr("Video device is opened, close it first?"),
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                if ret == QMessageBox.Yes:
                    self.set_device(False)
        if self.server.running:
            ret = QMessageBox.warning(
                self,
                self.tr("Warning"),
                self.tr("Server is running, stop it?"),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if ret == QMessageBox.Yes:
                self.on_btnServerSwitch_clicked()
        if not self.server_simple_started:
            self.server_simple_port = server_simple.start_server()
            self.server_simple_started = True
        url = f"http://127.0.0.1:{self.server_simple_port}"
        QDesktopServices.openUrl(QUrl(url))

    def set_log_text(self, text):
        self.serverLogEdit.setText(text)
        self.serverLogEdit.moveCursor(QTextCursor.End)

    def mouse_wheel_act(self):
        if self.mouse_scroll_timer.isActive():
            self.mouse_scroll_timer.stop()
        self.mouse_scroll_timer.start(100)

    def server_command_callback(self, data_type, data_payload):
        global mouse_buffer, kb_buffer, mouse_buffer_rel
        if data_type == "reset_mcu":
            self.reset_keymouse(2)
        elif data_type == "reset_hid":
            self.reset_keymouse(4)
        if not self.device_connected:
            return
        if data_type == "mouse_wheel":
            if not self.status["relative_mouse"]:
                buffer = mouse_buffer
                bit = 7
            else:
                buffer = mouse_buffer_rel
                bit = 5
            if data_payload[0] > 0:
                buffer[bit] = 0x01
            elif data_payload[0] < 0:
                buffer[bit] = 0xFF
            else:
                buffer[bit] = 0
            self._hid_signal.emit(buffer)
            self._wheel_signal.emit()
        elif data_type == "mouse_btn":
            if not self.status["relative_mouse"]:
                buffer = mouse_buffer
            else:
                buffer = mouse_buffer_rel
            if data_payload[1] == 2:
                buffer[2] |= data_payload[0]
            elif data_payload[1] == 3:
                buffer[2] &= ~data_payload[0]
            else:
                mouse_buffer = [2, 0, 0, 0, 0, 0, 0, 0, 0]
                mouse_buffer_rel = [7, 0, 0, 0, 0, 0, 0, 0, 0]
                self._hid_signal.emit(mouse_buffer)
                self._hid_signal.emit(mouse_buffer_rel)
                return
            self._hid_signal.emit(buffer)
        elif data_type == "mouse_pos":
            self.status["relative_mouse"] = False
            x, y = int(data_payload[0]) & 0x7FFF, int(data_payload[1]) & 0x7FFF
            mouse_buffer[3] = x & 0xFF
            mouse_buffer[4] = x >> 8
            mouse_buffer[5] = y & 0xFF
            mouse_buffer[6] = y >> 8
            self._hid_signal.emit(mouse_buffer)
        elif data_type == "mouse_offset":
            self.status["relative_mouse"] = True
            x, y = int(data_payload[0]), int(data_payload[1])
            x = max(min(x, 127), -127)
            y = max(min(y, 127), -127)
            x += 0xFF if x < 0 else 0
            y += 0xFF if y < 0 else 0
            mouse_buffer_rel[3] = x & 0xFF
            mouse_buffer_rel[4] = y & 0xFF
            self._hid_signal.emit(mouse_buffer_rel)
        elif data_type == "keyboard":
            state = data_payload[1]
            key = data_payload[0]
            if state == 3:  # release all
                kb_buffer = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                self._hid_signal.emit(kb_buffer)
            else:
                self.update_kb_hid(key, state == 1)
        elif data_type == "paste":
            logger.debug(f"Received {len(data_payload)} bytes paste data")
            if not self.ignore_event:
                self.paste_board_send(data_payload)

    _restore_track = False

    def focusInEvent(self, event):
        if self._restore_track:
            self._restore_track = False
            self.status["mouse_capture"] = True
        if self.hook_state:
            self.pythoncom_timer.start(5)
            self.hook_manager.HookKeyboard()
            self.statusbar_btn5.setPixmap(load_pixmap("hook"))
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        if self.status["mouse_capture"]:
            self.status["mouse_capture"] = False
            self._restore_track = True
        if self.hook_state:
            self.hook_manager.UnhookKeyboard()
            self.pythoncom_timer.stop()
            self.statusbar_btn5.setPixmap(load_pixmap("hook-off"))
        super().focusOutEvent(event)


def clear_splash():
    if "NUITKA_ONEFILE_PARENT" in os.environ:
        splash_filename = os.path.join(
            tempfile.gettempdir(),
            "onefile_%d_splash_feedback.tmp" % int(os.environ["NUITKA_ONEFILE_PARENT"]),
        )
        if os.path.exists(splash_filename):
            os.unlink(splash_filename)


def main():
    argv = sys.argv
    app = QApplication(argv)
    translator = QTranslator(app)
    if translation:
        if translator.load(os.path.join(PATH, "translate", "trans_cn.qm")):
            app.installTranslator(translator)
    translator2 = QTranslator(app)
    if translation:
        if translator2.load(os.path.join(PATH, "translate", "qtbase_cn.qm")):
            app.installTranslator(translator2)
    myWin = MyMainWindow()
    myWin.show()
    QTimer.singleShot(100, myWin.shortcut_status)
    clear_splash()
    return app.exec()


if __name__ == "__main__":
    main()
