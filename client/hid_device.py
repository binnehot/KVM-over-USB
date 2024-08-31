import os
import time
from enum import IntEnum, auto

from loguru import logger

from controller_ch9329 import Controller
from controller_ch9329 import Ch9329AttachFunction

if os.name == "nt":  # sys.platform == 'win32':
    from serial.tools.list_ports_windows import comports as list_comports
elif os.name == "posix":
    from serial.tools.list_ports_posix import comports as list_comports
else:
    raise ImportError("Sorry: no implementation for your platform {} available".format(os.name))


class DebugMode(IntEnum):
    FILTER_NONE = auto()
    FILTER_HID = auto()
    FILTER_MOUSE_DATA = auto()
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
        info = GLOBAL_CONTROLLER.product_info()
        if __DEBUG_MODE__ < DebugMode.FILTER_ALL:
            logger.debug(f"controller product info: {info}")
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
    reply: list = list()
    if __DEBUG_MODE__ < DebugMode.FILTER_HID:
        logger.debug(f"hid_report(buffer={buffer}, read_mode={read_mode})")
        # return status_code, replay
    if GLOBAL_CONTROLLER.check_connection() is False:
        status_code = 1
        if __DEBUG_MODE__ < DebugMode.FILTER_KEYBOARD:
            logger.debug(f"hid_event : check connection failed.")
        return status_code, reply
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
            status_code, reply = hid_keyboard_key_event(buffer)
        case 4:
            if __DEBUG_MODE__ <= DebugMode.FILTER_HID:
                logger.debug("hid_event: reload MCU")
            GLOBAL_CONTROLLER.reset_connection()
            # GLOBAL_CONTROLLER.reset_controller()
        case 5:
            if ((buffer[5] == 30) | (buffer[3] == 30)) & (buffer[4] == 30):
                GLOBAL_CONTROLLER.release('all')
            else:
                if __DEBUG_MODE__ <= DebugMode.FILTER_HID:
                    logger.debug("hid_event: reset keyboard and mouse code error")
                status_code = 1
        case _:
            if __DEBUG_MODE__ < DebugMode.FILTER_HID:
                logger.debug(f"hid_event: unknown buffer {buffer[1]}")
            status_code = 1
    return status_code, reply


# 按键事件
def hid_keyboard_key_event(buffer):
    status_code: int = 0
    replay: list = list()
    if buffer[1] == 1:
        hid_keyboard_key_button_event(buffer)
    elif buffer[1] == 3:
        replay = [3, 0, 0]
        status, replay[2] = GLOBAL_CONTROLLER.keyboard_light_status()
        if status is False:
            replay[0] = 1
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
            keys.append("")
        else:
            # 根据hid找keyname
            key_name = GLOBAL_CONTROLLER.convert_hid_key_code_to_ch9329_key_code(hid_key_code)
            keys.append(key_name)
            # logger.debug(f"key_name : {key_name}")
    GLOBAL_CONTROLLER.keyboard_keys_trigger(keys, function_keys)
    function_keys.clear()


def hid_mouse_event(buffer):
    if __DEBUG_MODE__ < DebugMode.FILTER_MOUSE_DATA:
        logger.debug(f"hid_mouse_event: {buffer}")
    # 绝对坐标模式
    if buffer[1] == 2:
        hid_mouse_send_absolute_data(buffer)
    # 相对坐标模式
    elif buffer[1] == 7:
        hid_mouse_send_relative_data(buffer)
    else:
        if __DEBUG_MODE__ < DebugMode.FILTER_MOUSE:
            logger.debug(f"hid_mouse_event: {buffer}")


def hid_mouse_send_absolute_data(buffer):
    wheel = buffer[8]

    x = ((buffer[5] & 0xFF) << 8) + buffer[4]
    xx = int(x / 0x7FFF * GLOBAL_CONTROLLER.screen_x)
    y = ((buffer[7] & 0xFF) << 8) + buffer[6]
    yy = int(y / 0x7FFF * GLOBAL_CONTROLLER.screen_y)

    assert xx <= 4096
    assert yy <= 4096

    if wheel == 255:
        # 滚轮向上
        wheel = -1
    elif wheel == 1:
        # 滚轮向下
        wheel = 1
    else:
        # 滚轮不动
        wheel = 0

    if buffer[3] == 0:
        GLOBAL_CONTROLLER.mouse_send_data('null', xx, yy, wheel, False)
    elif buffer[3] == 1:
        GLOBAL_CONTROLLER.mouse_send_data('left', xx, yy, wheel, False)
    elif buffer[3] == 2:
        GLOBAL_CONTROLLER.mouse_send_data('right', xx, yy, wheel, False)
    elif buffer[3] == 4:
        GLOBAL_CONTROLLER.mouse_send_data('center', xx, yy, wheel, False)
    else:
        if __DEBUG_MODE__ < DebugMode.FILTER_MOUSE_PRESS:
            logger.debug(f"hid_mouse_send_absolute_data: unknown mouse button {buffer[3]}")


def hid_mouse_send_relative_data(buffer):
    x = buffer[4]
    y = buffer[5]
    wheel = buffer[6]

    # 计算坐标
    x -= 0xFF if x > 127 else 0
    y -= 0xFF if y > 127 else 0

    # 加速移动鼠标需要放大坐标
    if -128 <= x * 2 <= 127:
        x = x * 2
    if -128 <= y * 2 <= 127:
        y = y * 2

    assert -128 <= x <= 127
    assert -128 <= y <= 127

    if wheel == 255:
        # 滚轮向上
        wheel = -1
    elif wheel == 1:
        # 滚轮向下
        wheel = 1
    else:
        # 滚轮不动
        wheel = 0

    if buffer[3] == 0:
        GLOBAL_CONTROLLER.mouse_send_data('null', x, y, wheel, True)
    elif buffer[3] == 1:
        GLOBAL_CONTROLLER.mouse_send_data('left', x, y, wheel, True)
    elif buffer[3] == 2:
        GLOBAL_CONTROLLER.mouse_send_data('right', x, y, wheel, True)
    elif buffer[3] == 4:
        GLOBAL_CONTROLLER.mouse_send_data('center', x, y, wheel, True)
    else:
        if __DEBUG_MODE__ < DebugMode.FILTER_MOUSE_PRESS:
            logger.debug(f"hid_mouse_send_relative_data: unknown mouse button {buffer[3]}")


if __name__ == "__main__":
    pass
