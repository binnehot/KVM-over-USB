# import hid #换了硬件，改用串口,删除了所有hid相关代码
#
from serial import Serial
from serial import SerialException
from ch9329 import keyboard
from ch9329 import mouse
from ch9329.config import get_product
from ch9329.config import get_serial_number
from loguru import logger
from PySide6.QtWidgets import *
import os
import sys
import yaml  # type: ignore
import time
import random

product_id = 0x2107  # 换了硬件，dummy
vendor_id = 0x413D  # 换了硬件，dummy
usage_page = 0xFF00  # 换了硬件，dummy

DEBUG = False
VERBOSE = False
COM_PORT = ' '
SCREEN_SIZE = [0, 0]
KEYBOARD_CH9329CODE2KEY = {}
PATH = os.path.dirname(os.path.abspath(__file__))
ARGV_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))


def set_debug(debug):
    global DEBUG
    DEBUG = debug


def set_verbose(verbose):
    global VERBOSE
    VERBOSE = verbose


def set_com_port(com_port):
    global COM_PORT
    COM_PORT = com_port


def set_screen_size(screen_size):
    global SCREEN_SIZE
    SCREEN_SIZE = screen_size


def read_config_hid():
    default_config_hid = """COM_port: COM8
Screen size X: 1920
Screen size Y: 1080
"""
    # 默认设置 "COM_port: COM8, Screen size X: 1920, Screen size Y :1080"
    return_read_config_hid = ['COM0', 100, 100]
    if not os.path.exists(os.path.join(ARGV_PATH, "config_hid.yaml")):
        with open(os.path.join(ARGV_PATH, "config_hid.yaml"), "w") as f:
            f.write(default_config_hid)
    else:
        with open(os.path.join(ARGV_PATH, "config_hid.yaml"), "r") as load_f:
            config_hid_yaml = yaml.safe_load(load_f)
        #        print ("line 57 config_hid.yaml file: ",config_hid_yaml)
        return_read_config_hid = [config_hid_yaml.get("COM_port"), config_hid_yaml.get("Screen size X"),
                                  config_hid_yaml.get("Screen size Y")]
    return return_read_config_hid


# 建立COM口连接
hid_setting_cfg = read_config_hid()
set_com_port(hid_setting_cfg[0])
set_screen_size(hid_setting_cfg[1:3])
try:
    K_M = Serial(COM_PORT, 9600, timeout=0.05)
except SerialException:
    print(COM_PORT, ' is not in use, please edit the config_hid.yaml file')
    COM_PORT = COM_PORT + " fail"


# 初始化HID设备设置
def init_usb(vendor_id, usage_page):
    global KEYBOARD_CH9329CODE2KEY
    try:
        with open(os.path.join(PATH, "data", "KEYBOARD_CH9329CODE2KEY.yaml"), "r") as load_f:
            KEYBOARD_CH9329CODE2KEY = yaml.safe_load(load_f)
            print("line78, KEYBOARD_CH9329CODE2KEY.yaml:\n", KEYBOARD_CH9329CODE2KEY)
    except Exception as e:
        print(f"Import config error:\n {e}\n\n")
        print("Check the KEYBOARD_CH9329CODE2KEY.yaml and restart the program")
        sys.exit(1)
    if DEBUG:
        logger.debug(f"init_usb(vendor_id={vendor_id}, usage_page={usage_page})")  # 老代码，新硬件没有使用vendor_id

    if (COM_PORT[-3:] == "ail"):
        print("COM_PORT", COM_PORT)
        set_hid_dialog = HID_Setting_Dialog()
        set_hid_dialog.exec()
        return 1
    elif (len(get_product(K_M)) < 3):
        print("Key board and mouse connection error.")
        set_hid_dialog = HID_Setting_Dialog()
        set_hid_dialog.exec()
        return 1
    return 0


def check_connection() -> bool:
    reset_k_m()
    return True


# 读写HID设备
def hid_report(buffer=[], r_mode=False, report=0):
    if DEBUG:
        logger.debug(f"hid_report(buffer={buffer}, r_mode={r_mode}, report={report})")
        return 0
    buffer = buffer[-1:] + buffer[:-1]
    buffer[0] = 0
    if VERBOSE:
        logger.debug(f"hid < {buffer}")
    match buffer[1]:
        case 1:
            hid_report_key(buffer)
        case 2:
            hid_report_mouse(buffer)
        case 7:
            hid_report_mouse(buffer)
            pass
        case 3:
            buffer_indicator = [3, 0, 0]
            buffer_indicator[2] = hid_report_get_keyboard_light_status()
            print("line 122, Reporting the Keyboard indicator lights' status: ", buffer_indicator[2])
            return (buffer_indicator)
        case 4:
            print("line125,This hardware does not have MCU reset function.")
            msgBox = QMessageBox()
            msgBox.setText("更换了硬件,改用ch9329, 没有 重载MCU 功能.\n\n现在使用的硬件产品名是: " + get_product(
                K_M) + "\n\n产品序列号是:  " + get_serial_number(K_M))
            msgBox.exec()
            return 0
        case 5:
            if ((buffer[5] == 30) | (buffer[3] == 30)) & (buffer[4] == 30):
                set_hid_dialog = HID_Setting_Dialog()
                set_hid_dialog.exec()
                reset_k_m('all')
            else:
                print("line 136, Reset keyboard and mouse, code error.")
            return 0
        case _:
            print("line 139, This buffer number is not in the cases list:", buffer)
    return 0


def hid_report_key(buffer_key):
    if buffer_key[1] == 1:
        if buffer_key[3] == 0:
            hid_report_key_presskey(buffer_key)
        else:
            function_keys = []
            if (buffer_key[3] & 1) or (buffer_key[3] & 16):
                function_keys.append('ctrl')
            if (buffer_key[3] & 2) or (buffer_key[3] & 32):
                function_keys.append('shift')
            if (buffer_key[3] & 4) or (buffer_key[3] & 64):
                function_keys.append('alt')
            if (buffer_key[3] & 8) or (buffer_key[3] & 128):
                function_keys.append('lwin')
            hid_report_key_presskey(buffer_key, function_keys)
            function_keys = []
        if len(buffer_key) > 10:
            if buffer_key[9] == 43:
                keyboard.press_and_release(K_M, 'tab')
            if buffer_key[10] == 70:
                keyboard.press_and_release(K_M, 'printscreen')
    else:
        print("line 165, buffer_key error:", buffer_key)
    return 0


def hid_report_key_presskey(buffer_key, function_keys=[]):
    #    for i in range(5,6):       # 避免按键连击的问题，尝试关闭for循环，没用。
    for i in range(5, min(10, len(buffer_key))):
        if buffer_key[i] == 0:
            break
        else:
            keyname = KEYBOARD_CH9329CODE2KEY.get(str(buffer_key[i]))  # 根据hid找keyname
            keyboard.press_and_release(K_M, keyname, function_keys)
    return 0


def hid_report_mouse(buffer_mouse):
    if buffer_mouse[1] == 2:
        if buffer_mouse[3] == 0:
            hid_report_mouse_move_to(buffer_mouse)
        elif ((buffer_mouse[4] == 0) & (buffer_mouse[5] == 0) & (buffer_mouse[6] == 0) & (buffer_mouse[7] == 0)):
            hid_report_mouse_click(buffer_mouse)
        else:
            hid_report_mouse_keyDown(buffer_mouse)
            hid_report_mouse_move_to(buffer_mouse)
            hid_report_mouse_keyUp(buffer_mouse)
            pass
        if buffer_mouse[8] != 0:
            hid_report_mouse_wheel(buffer_mouse[8])

    elif buffer_mouse[1] == 7:
        if buffer_mouse[3] == 0:
            hid_report_mouse_move_rel(buffer_mouse)
        elif ((buffer_mouse[4] == 0) & (buffer_mouse[5] == 0) & (buffer_mouse[6] == 0) & (buffer_mouse[7] == 0)):
            hid_report_mouse_click(buffer_mouse)
        else:
            hid_report_mouse_keyDown(buffer_mouse)
            hid_report_mouse_move_rel(buffer_mouse)
            hid_report_mouse_keyUp(buffer_mouse)
            pass
        if buffer_mouse[6] != 0:
            hid_report_mouse_wheel(buffer_mouse[6])
    else:
        print("line 205, buffer_mouse error:", buffer_mouse)
    return 0


def hid_report_mouse_move_to(buffer_mouse):
    x = ((buffer_mouse[5] & 0xFF) << 8) + buffer_mouse[4]
    xx = int(x / 0x7FFF * SCREEN_SIZE[0])
    y = ((buffer_mouse[7] & 0xFF) << 8) + buffer_mouse[6]
    yy = int(y / 0x7FFF * SCREEN_SIZE[1])
    mouse.move(K_M, xx, yy, False, SCREEN_SIZE[0], SCREEN_SIZE[1])
    print("line 214, mouse move to", xx, yy)
    return 0


def hid_report_mouse_click(buffer_mouse):
    if buffer_mouse[3] == 1:
        mouse.click(K_M, 'left')
    elif buffer_mouse[3] == 2:
        mouse.click(K_M, 'right')
    elif buffer_mouse[3] == 4:
        mouse.click(K_M, 'middle')
    else:
        print("line 225, hid_report_mouse_click, mouse XButton? ", buffer_mouse)
        return 0
    return 0


def hid_report_mouse_keyDown(buffer_mouse):
    if buffer_mouse[3] == 1:
        mouse.press(K_M, 'left')
    elif buffer_mouse[3] == 2:
        mouse.press(K_M, 'right')
    elif buffer_mouse[3] == 4:
        mouse.press(K_M, 'middle')
    else:
        print("line 237, hid_report_mouse_keyDown, mouse XButton? ", buffer_mouse)
        return 0
    return 0


def hid_report_mouse_keyUp(buffer_mouse):
    if buffer_mouse[3] == 1 | buffer_mouse[3] == 2 | buffer_mouse[3] == 4:
        time.sleep(random.uniform(0.1, 0.45))
        mouse.release(K_M)
    else:
        print("line 246, hid_report_mouse_keyUp, mouse XButton? ", buffer_mouse)
    return 0


def hid_report_mouse_move_rel(buffer_mouse_rel):
    x_hid = buffer_mouse_rel[4]
    y_hid = buffer_mouse_rel[5]
    x_hid -= 0xFF if x_hid > 127 else 0
    y_hid -= 0xFF if y_hid > 127 else 0
    mouse.move(K_M, x_hid * 3, y_hid * 3, True, SCREEN_SIZE[0], SCREEN_SIZE[1])
    print("line 255, mouse move rel", x_hid, y_hid)
    return 0


def hid_report_mouse_wheel(buffer_wheel):
    if buffer_wheel == 1:
        mouse.wheel(K_M, 1)
    elif buffer_wheel == 255:
        mouse.wheel(K_M, -1)
    else:
        print("buffer wheel is incorrect", buffer_wheel)
    return 0


def hid_report_get_keyboard_light_status():
    keyboard_info = get_keyboard_info()
    print("line 269,keyboard_info", keyboard_info)
    frame_data_location = keyboard_info.find('57ab008108')
    keyboard_light_status = int(keyboard_info[frame_data_location + 15])
    return keyboard_light_status


def get_keyboard_info():
    CMD_GET_INFO_packet = b"\x57" + b"\xab" + b"\x00" + b"\x01" + b"\x00" + b"\x03"
    K_M.write(CMD_GET_INFO_packet)
    keyboard_info = K_M.readline()
    return keyboard_info.hex()


def reset_k_m(type='key'):
    if type == 'key':
        keyboard.release(K_M)
    elif type == 'mouse':
        mouse.release(K_M)
    elif type == 'all':
        keyboard.release(K_M)
        mouse.release(K_M)
    return 0


class HID_Setting_Dialog(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.dialog = QDialog()
        layout = QFormLayout()
        label0 = QLabel()
        layout.addRow(label0)
        label1 = QLabel('HID COM 端口： ')
        self.le1 = QLineEdit(COM_PORT)
        layout.addRow(label1, self.le1)
        label2 = QLabel('服务器（被控端）屏幕分辨率 宽度: ')
        self.le2 = QLineEdit(str(SCREEN_SIZE[0]))
        layout.addRow(label2, self.le2)
        label3 = QLabel('服务器（被控端）屏幕分辨率 高度: ')
        self.le3 = QLineEdit(str(SCREEN_SIZE[1]))
        layout.addRow(label3, self.le3)
        label0 = QLabel()
        layout.addRow(label0)
        QBbox = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        button_ok_cancel = QDialogButtonBox(QBbox)
        layout.addRow(button_ok_cancel)
        self.setting_text = [self.le1.text(), self.le2.text(), self.le3.text()]
        button_ok_cancel.accepted.connect(self.save_hid_setting)
        button_ok_cancel.rejected.connect(self.reject)
        self.setLayout(layout)
        self.setWindowTitle('HID setting')
        return 0

    def save_hid_setting(self):
        input_com_port = self.le1.text()
        input_screen_x = self.le2.text()
        input_screen_y = self.le3.text()
        if (input_com_port[0:3] == "COM") & (input_com_port[3].isdigit()):
            input_com_port = input_com_port[0:4]
            if COM_PORT != input_com_port:
                set_com_port(input_com_port)
                msgBox = QMessageBox()
                msgBox.setText("修改COM口,请关闭(或强制关闭)程序后 重新运行程序")
                msgBox.exec()
        else:
            msgBox = QMessageBox()
            msgBox.setText("COM口 格式是 大写COM和数字,例如:COM5")
            msgBox.exec()
        if (input_screen_x.isdigit()) & (input_screen_y.isdigit()):
            set_screen_size([int(input_screen_x), int(input_screen_y)])
        else:
            msgBox = QMessageBox()
            msgBox.setText("屏幕分辨率为数字,例如:1080")
            msgBox.exec()

        self.setting_text = [input_com_port, input_screen_x, input_screen_y]
        print("line 344 setting_text :", self.setting_text)

        new_config_hid = 'COM_port: ' + COM_PORT + '\n' + 'Screen size X: ' + str(
            SCREEN_SIZE[0]) + '\n' + 'Screen size Y: ' + str(SCREEN_SIZE[1]) + '\n'
        print('line 347 new config_hid:', new_config_hid)

        with open(os.path.join(ARGV_PATH, "config_hid.yaml"), "w", encoding="utf-8") as f:
            f.write(new_config_hid)
        self.close()
        return 0
