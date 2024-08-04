# import hid #换了硬件，改用串口,删除了所有hid相关代码
#
from serial import Serial
from serial import SerialException
from ch9329 import keyboard
from ch9329 import mouse
from ch9329.config import get_product
from ch9329.config import get_serial_number
from ch9329.config import get_manufacturer
from loguru import logger
import os
import sys
import yaml
import time
import random

__DEBUG__ = False
__VERBOSE__ = False
KEYBOARD_CH9329CODE2KEY = {}
PATH = os.path.dirname(os.path.abspath(__file__))
ARGV_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))
serial_connection: Serial | None = None
current_com_port: str = ""
current_com_baud_rate: int = 9600


class ScreenSize:
    def __init__(self, x: int = 1920, y: int = 1080):
        self.x = x
        self.y = y

    def update_screen_size(self, x: int, y: int):
        self.x = x
        self.y = y


current_screen_size = ScreenSize()


def set_debug(debug):
    global __DEBUG__
    __DEBUG__ = debug


def set_verbose(verbose):
    global __VERBOSE__
    __VERBOSE__ = verbose


def load_keyboard_code_key():
    global KEYBOARD_CH9329CODE2KEY
    try:
        with open(os.path.join(PATH, "data", "KEYBOARD_CH9329CODE2KEY.yaml"), "r") as load_f:
            KEYBOARD_CH9329CODE2KEY = yaml.safe_load(load_f)
            logger.debug(f"load KEYBOARD_CH9329CODE2KEY succeed")
    except FileNotFoundError:
        logger.debug(f"load KEYBOARD_CH9329CODE2KEY failed")
        sys.exit(1)


# 初始化HID设备设置
# 返回0为成功
# 返回非0为失败
def init_usb(controller_port: str, baud: int = 9600, screen_x: int = 1920, screen_y: int = 1080):
    global serial_connection
    load_keyboard_code_key()
    if __DEBUG__:
        logger.debug(f"init_usb({controller_port}, {baud}, {screen_x}, {screen_y})")
    if serial_connection:
        serial_connection.close()
        serial_connection = None
    try:
        serial_connection = Serial(controller_port, baud, timeout=0.05)
        current_screen_size.x = screen_x
        current_screen_size.y = screen_y
        logger.debug(f"serial port {controller_port} open succeed")
    except SerialException:
        logger.debug(f"serial port {controller_port} open failed")
        serial_connection = None

    if serial_connection is None:
        return 1
    else:
        return 0


def check_connection() -> bool:
    if serial_connection is None:
        return False
    if not serial_connection.is_open:
        return False
    # release_keyboard_or_mouse()
    return True


# 读写HID设备
def hid_report(buffer=[], r_mode=False, report=0):
    if __DEBUG__:
        logger.debug(f"hid_report(buffer={buffer}, r_mode={r_mode}, report={report})")
        return 0
    buffer = buffer[-1:] + buffer[:-1]
    buffer[0] = 0
    if __VERBOSE__:
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
            logger.debug("Reporting the Keyboard indicator lights status: ", buffer_indicator[2])
            return buffer_indicator
        case 4:
            logger.debug("Reset MCU(CH9329)")
            reset_mcu_ch9329()
            return 0
        case 5:
            if ((buffer[5] == 30) | (buffer[3] == 30)) & (buffer[4] == 30):
                release_keyboard_or_mouse("all")
            else:
                logger.debug("Reset keyboard and mouse, code error")
            return 0
        case _:
            logger.debug("Unknown buffer number %x:", buffer[1])
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
                keyboard.press_and_release(serial_connection, 'tab')
            if buffer_key[10] == 70:
                keyboard.press_and_release(serial_connection, 'printscreen')
    else:
        logger.debug("buffer_key error: %x", buffer_key[1])
    return 0


def hid_report_key_presskey(buffer_key, function_keys=[]):
    #    for i in range(5,6):       # 避免按键连击的问题，尝试关闭for循环，没用。
    for i in range(5, min(10, len(buffer_key))):
        if buffer_key[i] == 0:
            break
        else:
            keyname = KEYBOARD_CH9329CODE2KEY.get(str(buffer_key[i]))  # 根据hid找keyname
            keyboard.press_and_release(serial_connection, keyname, function_keys)
    return 0


def hid_report_mouse(buffer_mouse):
    if buffer_mouse[1] == 2:
        if buffer_mouse[3] == 0:
            hid_report_mouse_move_to(buffer_mouse)
        elif ((buffer_mouse[4] == 0) & (buffer_mouse[5] == 0) & (buffer_mouse[6] == 0) & (buffer_mouse[7] == 0)):
            hid_report_mouse_click(buffer_mouse)
        else:
            hid_report_mouse_key_down(buffer_mouse)
            hid_report_mouse_move_to(buffer_mouse)
            hid_report_mouse_key_up(buffer_mouse)
            pass
        if buffer_mouse[8] != 0:
            hid_report_mouse_wheel(buffer_mouse[8])

    elif buffer_mouse[1] == 7:
        if buffer_mouse[3] == 0:
            hid_report_mouse_move_rel(buffer_mouse)
        elif ((buffer_mouse[4] == 0) & (buffer_mouse[5] == 0) & (buffer_mouse[6] == 0) & (buffer_mouse[7] == 0)):
            hid_report_mouse_click(buffer_mouse)
        else:
            hid_report_mouse_key_down(buffer_mouse)
            hid_report_mouse_move_rel(buffer_mouse)
            hid_report_mouse_key_up(buffer_mouse)
            pass
        if buffer_mouse[6] != 0:
            hid_report_mouse_wheel(buffer_mouse[6])
    else:
        logger.debug("buffer_mouse error: %x", buffer_mouse[1])
    return 0


def hid_report_mouse_move_to(buffer_mouse):
    x = ((buffer_mouse[5] & 0xFF) << 8) + buffer_mouse[4]
    xx = int(x / 0x7FFF * current_screen_size.x)
    y = ((buffer_mouse[7] & 0xFF) << 8) + buffer_mouse[6]
    yy = int(y / 0x7FFF * current_screen_size.y)
    mouse.move(serial_connection, xx, yy, False, current_screen_size.x, current_screen_size.y)
    logger.debug("mouse move to : %d %d", xx, yy)
    return 0


def hid_report_mouse_click(buffer_mouse):
    if buffer_mouse[3] == 1:
        mouse.click(serial_connection, 'left')
    elif buffer_mouse[3] == 2:
        mouse.click(serial_connection, 'right')
    elif buffer_mouse[3] == 4:
        mouse.click(serial_connection, 'middle')
    else:
        logger.debug("unknown mouse button click: %x", buffer_mouse[3])
        return 0
    return 0


def hid_report_mouse_key_down(buffer_mouse):
    if buffer_mouse[3] == 1:
        mouse.press(serial_connection, 'left')
    elif buffer_mouse[3] == 2:
        mouse.press(serial_connection, 'right')
    elif buffer_mouse[3] == 4:
        mouse.press(serial_connection, 'middle')
    else:
        logger.debug("unknown mouse button press: %x", buffer_mouse[3])
        return 0
    return 0


def hid_report_mouse_key_up(buffer_mouse):
    if buffer_mouse[3] == 1 | buffer_mouse[3] == 2 | buffer_mouse[3] == 4:
        time.sleep(random.uniform(0.1, 0.45))
        mouse.release(serial_connection)
    else:
        logger.debug("unknown mouse button release: %x", buffer_mouse[3])
    return 0


def hid_report_mouse_move_rel(buffer_mouse_rel):
    x_hid = buffer_mouse_rel[4]
    y_hid = buffer_mouse_rel[5]
    x_hid -= 0xFF if x_hid > 127 else 0
    y_hid -= 0xFF if y_hid > 127 else 0
    mouse.move(serial_connection, x_hid * 3, y_hid * 3, True, current_screen_size.x, current_screen_size.y)
    logger.debug("mouse move rel %d %d", x_hid, y_hid)
    return 0


def hid_report_mouse_wheel(buffer_wheel):
    if buffer_wheel == 1:
        mouse.wheel(serial_connection, 1)
    elif buffer_wheel == 255:
        mouse.wheel(serial_connection, -1)
    else:
        logger.debug("Incorrect buffer wheel value %d", buffer_wheel)
    return 0


def hid_report_get_keyboard_light_status():
    keyboard_info = get_keyboard_info()
    print("line 269,keyboard_info", keyboard_info)
    frame_data_location = keyboard_info.find('57ab008108')
    keyboard_light_status = int(keyboard_info[frame_data_location + 15])
    return keyboard_light_status


def get_keyboard_info():
    cmd_get_info_packet = b"\x57" + b"\xab" + b"\x00" + b"\x01" + b"\x00" + b"\x03"
    serial_connection.write(cmd_get_info_packet)
    keyboard_info = serial_connection.readline()
    return keyboard_info.hex()


def release_keyboard_or_mouse(release_type='key'):
    if serial_connection is None:
        return 0
    logger.debug('release %s', release_type)
    if release_type == 'key':
        logger.debug('release key')
        keyboard.release(serial_connection)
    elif release_type == 'mouse':
        logger.debug('release mouse')
        mouse.release(serial_connection)
    elif release_type == 'all':
        logger.debug('release all')
        keyboard.release(serial_connection)
        mouse.release(serial_connection)
    return 0


def reset_mcu_ch9329():
    cmd_reset_packet = b"\x57" + b"\xab" + b"\x00" + b"\x0f" + b"\x00" + b"\x11"
    serial_connection.write(cmd_reset_packet)
    keyboard_info = serial_connection.readline()
    if len(keyboard_info) >= 6:
        logger.debug('ch9329 reset command return: %x', keyboard_info[5])
        if keyboard_info[5] == 0:
            logger.debug('ch9329 reset succeed')
    return keyboard_info.hex()


if __name__ == "__main__":
    pass
