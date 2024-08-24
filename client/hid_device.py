import os
import time
from enum import IntEnum, auto

from loguru import logger

from controller_ch9329 import Controller

if os.name == "nt":  # sys.platform == 'win32':
    from serial.tools.list_ports_windows import comports as list_comports
elif os.name == "posix":
    from serial.tools.list_ports_posix import comports as list_comports
else:
    raise ImportError("Sorry: no implementation for your platform {} available".format(os.name))


class DebugMode(IntEnum):
    FILTER_NONE = auto()
    FILTER_HID = auto()
    FILTER_MOUSE_MOVE = auto()
    FILTER_MOUSE_PRESS = auto()
    FILTER_MOUSE = auto()
    FILTER_KEYBOARD = auto()
    FILTER_ALL = auto()


__DEBUG_MODE__: DebugMode = DebugMode.FILTER_ALL
GLOBAL_CONTROLLER: Controller = Controller()


def debug_mode(mode: DebugMode):
    global __DEBUG_MODE__
    __DEBUG_MODE__ = mode


def detect_serial_ports() -> list[str]:
    port_name_list: list[str] = []
    port_info_list: serial.tools.list_ports.ListPortInfo = list_comports(include_links=False)
    for port_info in port_info_list:
        port_name_list.append(port_info.name)
    port_info_list.sort()
    return port_name_list


# 初始化HID设备设置
# 返回0为成功
# 返回非0为失败
def init_usb(controller_port: str, baud: int = 9600, screen_x: int = 1920, screen_y: int = 1080):
    global GLOBAL_CONTROLLER
    if controller_port == 'auto':
        # 检测com端口
        ports: list[str] = detect_serial_ports()
        if len(ports) > 0:
            # 获取最后一个com端口
            controller_port = ports[-1]
        else:
            return 1
    GLOBAL_CONTROLLER.set_connection_params(controller_port, baud, screen_x, screen_y)
    status = GLOBAL_CONTROLLER.create_connection()
    if status is True:
        return 0
    else:
        return 1


def check_connection() -> bool:
    return GLOBAL_CONTROLLER.check_connection()


# 读写HID设备
# 返回0为成功
# 返回非0值为失败或特殊含义
def hid_event(buffer: list, read_mode: bool = False):
    status_code: int = 0
    replay: list = list()
    if __DEBUG_MODE__ < DebugMode.FILTER_HID:
        logger.debug(f"hid_report(buffer={buffer}, read_mode={read_mode})")
        # return status_code, replay
    if GLOBAL_CONTROLLER.check_connection() is False:
        status_code = 1
        if __DEBUG_MODE__ < DebugMode.FILTER_KEYBOARD:
            logger.debug(f"hid_event : check connection failed.")
        return status_code, replay
    buffer = buffer[-1:] + buffer[:-1]
    buffer[0] = 0
    # buffer[1] 为信息类型判断标志
    match buffer[1]:
        case 1:
            hid_keyboard_key_event(buffer)
        case 2:
            hid_mouse_event(buffer)
        case 7:
            hid_mouse_event(buffer)
        case 3:
            status_code, replay = hid_keyboard_key_event(buffer)
        case 4:
            if __DEBUG_MODE__ <= DebugMode.FILTER_HID:
                logger.debug("hid_event: reload MCU")
            GLOBAL_CONTROLLER.reset_connection()
            # GLOBAL_CONTROLLER.reset_controller()
        case 5:
            if ((buffer[5] == 30) | (buffer[3] == 30)) & (buffer[4] == 30):
                GLOBAL_CONTROLLER.release_devices_input('all')
            else:
                if __DEBUG_MODE__ <= DebugMode.FILTER_HID:
                    logger.debug("hid_event: reset keyboard and mouse code error")
                status_code = 1
        case _:
            if __DEBUG_MODE__ < DebugMode.FILTER_HID:
                logger.debug(f"hid_event: unknown buffer {buffer[1]}")
            status_code = 1
    return status_code, replay


# 按键事件
def hid_keyboard_key_event(buffer):
    status_code: int = 0
    replay: list = list()
    if buffer[1] == 1:
        hid_keyboard_key_button_event(buffer)
    elif buffer[1] == 3:
        replay = [3, 0, 0]
        replay[2] = GLOBAL_CONTROLLER.keyboard_light_status()
        if __DEBUG_MODE__ < DebugMode.FILTER_KEYBOARD:
            logger.debug(f"Reporting the Keyboard indicator lights status: {replay[2]}")
    else:
        if __DEBUG_MODE__ < DebugMode.FILTER_KEYBOARD:
            logger.debug(f"hid_keyboard_key_event : unknown buffer {buffer[1]}")
        status_code = 1
    return status_code, replay


def hid_keyboard_key_button_event(buffer):
    if __DEBUG_MODE__ < DebugMode.FILTER_KEYBOARD:
        byte_as_hex = [hex(x).split('x')[-1] for x in list(buffer)]
        logger.debug(f"hid_keyboard_key_button_event: buffer : {byte_as_hex}")
    function_keys = []
    if buffer[3] != 0:
        # 存在组合键
        if (buffer[3] & 1) or (buffer[3] & 16):
            function_keys.append('ctrl')
        if (buffer[3] & 2) or (buffer[3] & 32):
            function_keys.append('shift')
        if (buffer[3] & 4) or (buffer[3] & 64):
            function_keys.append('alt')
        if (buffer[3] & 8) or (buffer[3] & 128):
            function_keys.append('win')
    keys: list = list()
    for i in range(5, len(buffer)):
        hid_key_code = buffer[i]
        if hid_key_code == 0:
            # 按键弹起
            # GLOBAL_CONTROLLER.keyboard_key_release()
            keys.append("")
        else:
            # 根据hid找keyname
            key_name = GLOBAL_CONTROLLER.convert_hid_key_code_to_ch9329_key_code(hid_key_code)
            keys.append(key_name)
            # logger.debug(f"key_name : {key_name}")
    GLOBAL_CONTROLLER.keyboard_keys_trigger(keys, function_keys)
    function_keys.clear()


def hid_mouse_event(buffer):
    # 绝对坐标模式
    if buffer[1] == 2:
        if buffer[3] == 0:
            # 鼠标移动事件
            hid_mouse_absolute_move(buffer)
        else:
            # 包含鼠标点击事件
            hid_mouse_absolute_press(buffer)
            time.sleep(GLOBAL_CONTROLLER.random_interval())
            hid_mouse_release(buffer)
        if buffer[8] != 0:
            hid_mouse_wheel(buffer[8])
    # 相对坐标模式
    elif buffer[1] == 7:
        if buffer[3] == 0:
            hid_mouse_relative_move(buffer)
        else:
            hid_mouse_relative_press(buffer)
            time.sleep(GLOBAL_CONTROLLER.random_interval())
            hid_mouse_release(buffer)
        if buffer[6] != 0:
            hid_mouse_wheel(buffer[6])
    else:
        if __DEBUG_MODE__ < DebugMode.FILTER_MOUSE:
            logger.debug(f"hid_mouse_event: unknown buffer {buffer[1]}")


def hid_mouse_absolute_move(buffer):
    x = ((buffer[5] & 0xFF) << 8) + buffer[4]
    xx = int(x / 0x7FFF * GLOBAL_CONTROLLER.screen_x)
    y = ((buffer[7] & 0xFF) << 8) + buffer[6]
    yy = int(y / 0x7FFF * GLOBAL_CONTROLLER.screen_y)
    GLOBAL_CONTROLLER.mouse_absolute_move_to(xx, yy)
    if __DEBUG_MODE__ < DebugMode.FILTER_MOUSE_MOVE:
        logger.debug(f"mouse_absolute_move_to : {xx} {yy}")


def hid_mouse_relative_move(buffer):
    x_hid = buffer[4]
    y_hid = buffer[5]
    x_hid -= 0xFF if x_hid > 127 else 0
    y_hid -= 0xFF if y_hid > 127 else 0

    # 加速移动鼠标需要放大坐标
    if -128 <= x_hid * 2 <= 127:
        x_hid = x_hid * 2
    if -128 <= y_hid * 2 <= 127:
        y_hid = y_hid * 2

    GLOBAL_CONTROLLER.mouse_relative_move_to(x_hid, y_hid)
    if __DEBUG_MODE__ < DebugMode.FILTER_MOUSE_MOVE:
        logger.debug(f"mouse_relative_move_to : {x_hid} {y_hid}")


def hid_mouse_absolute_press(buffer):
    x = ((buffer[5] & 0xFF) << 8) + buffer[4]
    xx = int(x / 0x7FFF * GLOBAL_CONTROLLER.screen_x)
    y = ((buffer[7] & 0xFF) << 8) + buffer[6]
    yy = int(y / 0x7FFF * GLOBAL_CONTROLLER.screen_y)
    if buffer[3] == 1:
        GLOBAL_CONTROLLER.mouse_button_press('left', xx, yy)
    elif buffer[3] == 2:
        GLOBAL_CONTROLLER.mouse_button_press('right', xx, yy)
    elif buffer[3] == 4:
        GLOBAL_CONTROLLER.mouse_button_press('middle', xx, yy)
    else:
        if __DEBUG_MODE__ < DebugMode.FILTER_MOUSE_PRESS:
            logger.debug(f"hid_mouse_press: unknown mouse button {buffer[3]}")


def hid_mouse_relative_press(buffer):
    x = 0
    y = 0

    if buffer[3] == 1:
        GLOBAL_CONTROLLER.mouse_button_press('left', x, y, True)
    elif buffer[3] == 2:
        GLOBAL_CONTROLLER.mouse_button_press('right', x, y, True)
    elif buffer[3] == 4:
        GLOBAL_CONTROLLER.mouse_button_press('middle', x, y, True)
    else:
        if __DEBUG_MODE__ < DebugMode.FILTER_MOUSE_PRESS:
            logger.debug(f"hid_mouse_press: unknown mouse button {buffer[3]}")


def hid_mouse_release(buffer):
    if buffer[3] == 1 or buffer[3] == 2 or buffer[3] == 4:
        # time.sleep(random.uniform(0.1, 0.45))
        GLOBAL_CONTROLLER.mouse_button_release()
    else:
        if __DEBUG_MODE__ < DebugMode.FILTER_MOUSE_PRESS:
            logger.debug(f"hid_mouse_release: buffer error {buffer[3]}")


def hid_mouse_wheel(value):
    if value == 1:
        GLOBAL_CONTROLLER.mouse_wheel(1)
    elif value == 255:
        GLOBAL_CONTROLLER.mouse_wheel(-1)
    else:
        if __DEBUG_MODE__ < DebugMode.FILTER_MOUSE_PRESS:
            logger.debug(f"hid_mouse_wheel: incorrect value {value}")


if __name__ == "__main__":
    pass
