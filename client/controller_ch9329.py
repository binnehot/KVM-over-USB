# import hid #换了硬件，改用串口,删除了所有hid相关代码
#
import os
import random
import sys
import threading
import time
from typing import List

import yaml
from ch9329 import keyboard
from ch9329 import mouse
from ch9329.keyboard import Modifier
from loguru import logger
from serial import Serial
from serial import SerialException

__DEBUG__ = False
SELF_PATH = os.path.dirname(os.path.abspath(__file__))


class Ch9329KeyboardAttachFunction:

    @staticmethod
    def trigger_keys(ser: Serial, keys: list, modifiers: List[Modifier] = []) -> None:
        press_keys = keys.copy()
        press_modifiers = modifiers.copy()
        press_modifiers = list(set(press_modifiers))
        # Supports press to 6 normal buttons at the same time
        if len(press_keys) > 6:
            press_keys = press_keys[0:5]
        # len(keys) <= 6
        else:
            while len(press_keys) != 6:
                press_keys.append("")
        logger.debug(f'press_keys {press_keys}, {press_modifiers}')
        if press_keys[0] != '' and len(press_modifiers) > 0:
            pass
        keyboard.send(ser, (press_keys[0], press_keys[1], press_keys[2], press_keys[3], press_keys[4], press_keys[5]),
                      press_modifiers)


class ControllerCh9329:
    MOUSE_BUTTON_NAME: list[str] = ['left', 'right', 'middle']

    def __init__(self, controller_port: str = 'COM1', baud: int = 9600, screen_x: int = 1920, screen_y: int = 1080):
        self.connection_mutex: threading.Lock = threading.Lock()
        self.serial_connection: Serial | None = None
        self.code2key_path = os.path.join(SELF_PATH, "data", "keyboard_ch9329_code2key.yaml")
        self.ch9329_code2key: dict = {}
        self.press_key_map: dict = {}
        self.controller_port: str = controller_port
        self.baud: int = baud
        self.screen_x: int = screen_x
        self.screen_y: int = screen_y
        self.min_interval: float = 0.1
        self.max_interval: float = 0.5
        self.timeout: float = 0.1

        self.load_hid_code_key(self.code2key_path)

    def get_connection_params(self) -> tuple[str, int, int, int]:
        return self.controller_port, self.baud, self.screen_x, self.screen_y

    def set_connection_params(self, controller_port: str = 'COM1', baud: int = 9600, screen_x: int = 1920,
                              screen_y: int = 1080):
        self.controller_port: str = controller_port
        self.baud: int = baud
        self.screen_x: int = screen_x
        self.screen_y: int = screen_y

    def load_hid_code_key(self, file_path: str):
        try:
            with open(file_path, "r") as load_f:
                self.ch9329_code2key = yaml.safe_load(load_f)
                logger.debug(f"load ch9329_code2key succeed")
        except FileNotFoundError:
            logger.debug(f"load ch9329_code2key failed")
            sys.exit(1)

    def create_connection(self) -> bool:
        logger.debug(f"init_connection({self.controller_port}, {self.baud}, {self.screen_x}, {self.screen_y})")
        connection_created: bool = False
        if self.controller_port == "":
            return connection_created
        self.close_connection()
        with self.connection_mutex:
            try:
                self.serial_connection = Serial(self.controller_port, self.baud, timeout=self.timeout)
                connection_created = True
                logger.debug(f"init_connection succeed")
            except SerialException:
                logger.debug(f"init_connection failed")
                self.serial_connection = None
        return connection_created

    def check_connection(self) -> bool:
        with self.connection_mutex:
            if self.serial_connection is not None:
                if self.serial_connection.is_open is True:
                    return True
            return False

    def close_connection(self):
        with self.connection_mutex:
            if self.serial_connection is not None:
                self.serial_connection.close()
            self.serial_connection = None

    def reset_connection(self):
        logger.debug(f"reset_connection")
        self.press_key_map.clear()
        self.create_connection()

    def random_interval(self) -> float:
        return random.uniform(self.min_interval, self.max_interval)

    def reset_controller(self):
        cmd_reset_packet = b"\x57" + b"\xab" + b"\x00" + b"\x0f" + b"\x00" + b"\x11"
        with self.connection_mutex:
            if self.serial_connection is None:
                return False
            if self.serial_connection.is_open is False:
                return False
            self.serial_connection.write(cmd_reset_packet)
            controller_info = self.serial_connection.readline()
            if len(controller_info) >= 6:
                logger.debug(f'ch9329 reset command return: {keyboard_info[5]}', )
                if keyboard_info[5] == 0:
                    logger.debug('reset_controller succeed')

    def mouse_absolute_move_to(self, x: int, y: int):
        assert x <= 4096
        assert y <= 4096
        with self.connection_mutex:
            if self.serial_connection is None:
                return False
            if self.serial_connection.is_open is False:
                return False
            mouse.move(self.serial_connection, x, y, False, self.screen_x, self.screen_y)
            logger.debug(f"mouse absolute move to : {x} {y}")

    def mouse_relative_move_to(self, x: int, y: int):
        assert -128 <= x <= 127
        assert -128 <= y <= 127
        with self.connection_mutex:
            if self.serial_connection is None:
                return False
            if self.serial_connection.is_open is False:
                return False
            mouse.move(self.serial_connection, x, y, True, self.screen_x, self.screen_y)
            logger.debug(f"mouse relative move to : {x} {y}")

    def mouse_button_press(self, button_name: str) -> True:
        with self.connection_mutex:
            if self.serial_connection is None:
                return False
            if self.serial_connection.is_open is False:
                return False
            if button_name in self.MOUSE_BUTTON_NAME:
                mouse.press(self.serial_connection, button_name)
                logger.debug(f"mouse button press: {button_name}")
            else:
                logger.debug(f"unknown mouse button press: {button_name}")
        return True

    def mouse_button_release(self) -> bool:
        with self.connection_mutex:
            if self.serial_connection is None:
                return False
            if self.serial_connection.is_open is False:
                return False
            mouse.release(self.serial_connection)
        return True

    def mouse_button_click(self, button_name: str) -> bool:
        status: bool = self.mouse_button_press(button_name)
        if status is False:
            return status
        time.sleep(self.random_interval())
        status = self.mouse_button_release()
        return status

    def mouse_wheel(self, wheel: int) -> bool:
        with self.connection_mutex:
            if self.serial_connection is None:
                return False
            if self.serial_connection.is_open is False:
                return False
            if wheel == 1:
                mouse.wheel(self.serial_connection, 1)
            elif wheel == -1:
                mouse.wheel(self.serial_connection, -1)
            else:
                logger.debug(f"Incorrect wheel value {wheel}")
        return True

    def convert_hid_key_code_to_ch9329_key_code(self, code: int) -> str:
        string_key: str = '0x{:02x}'.format(code)
        ch9329_key: str | None = self.ch9329_code2key.get(string_key, None)
        if ch9329_key is None:
            ch9329_key = ''
        return ch9329_key

    def keyboard_key_press(self, key_name: str, function_keys: list):
        with self.connection_mutex:
            if self.serial_connection is None:
                return False
            if self.serial_connection.is_open is False:
                return False
            if self.press_key_map.get(key_name, None) is None:
                keyboard.press(self.serial_connection, key_name, function_keys)
                self.press_key_map[key_name] = True
                logger.debug(f"keyboard key press : {key_name}")
        return True

    def keyboard_key_release(self):
        with self.connection_mutex:
            if self.serial_connection is None:
                return False
            if self.serial_connection.is_open is False:
                return False
            keyboard.release(self.serial_connection)
            self.press_key_map.clear()
            logger.debug(f"keyboard key release")
        return True

    def keyboard_keys_trigger(self, keys: list, function_keys: list):
        with self.connection_mutex:
            if self.serial_connection is None:
                return False
            if self.serial_connection.is_open is False:
                return False
            Ch9329KeyboardAttachFunction.trigger_keys(self.serial_connection, keys, function_keys)
            logger.debug(f"keyboard keys press : {keys}")
        return True

    def keyboard_key_click(self, key_name: str, function_keys: list, min_interval: int = 0.1,
                           max_interval: int = 0.5) -> bool:
        status: bool = self.keyboard_key_press(key_name, function_keys)
        if status is False:
            return status
        time.sleep(self.random_interval())
        status = self.keyboard_key_release()
        return status

    def keyboard_light_status(self):
        cmd_get_info_packet = b"\x57" + b"\xab" + b"\x00" + b"\x01" + b"\x00" + b"\x03"
        __clear_buffer__: bytes = self.serial_connection.readall()
        g_serial_connection.write(cmd_get_info_packet)
        buffer: bytes = self.serial_connection.readline()
        keyboard_light_status: int = 0
        if len(buffer) == 14:
            keyboard_light_status = buffer[8]
        logger.debug(f"keyboard status 0x{keyboard_light_status:02x}")
        return keyboard_light_status

    def release_devices_input(self, device_type: str):
        if device_type == "mouse":
            self.mouse_button_release()
        elif device_type == "keyboard":
            self.keyboard_key_release()
        elif device_type == 'all':
            self.mouse_button_release()
            self.keyboard_key_release()
        else:
            logger.debug(f'unknown device type: {device_type}')


class Controller(ControllerCh9329):
    pass


if __name__ == "__main__":
    pass
