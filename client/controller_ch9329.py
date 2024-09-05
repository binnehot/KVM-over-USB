# import hid #换了硬件，改用串口,删除了所有hid相关代码
#
import os
import random
import sys
import threading
from typing import List

import yaml
from ch9329 import keyboard
from ch9329 import mouse
from ch9329.config import get_product
from ch9329.keyboard import Modifier
from loguru import logger
from serial import Serial
from serial import SerialException


SELF_PATH = os.path.dirname(os.path.abspath(__file__))


class Ch9329AttachFunction:

    @staticmethod
    def trigger_keys(
            ser: Serial, keys: list[str],
            modifiers: List[Modifier] = []
    ) -> None:
        press_keys = keys.copy()
        press_modifiers = modifiers.copy()
        press_keys = list(set(press_keys))
        press_modifiers = list(set(press_modifiers))
        # Supports press to 6 normal buttons at the same time
        if len(press_keys) > 6:
            press_keys = press_keys[0:6]
        # len(keys) <= 6
        else:
            while len(press_keys) != 6:
                press_keys.append("")
        logger.debug(f"press_keys {press_keys}, {press_modifiers}")
        keyboard.send(
            ser, (
                press_keys[0], press_keys[1], press_keys[2], press_keys[3],
                press_keys[4], press_keys[5]),
            press_modifiers
        )


class ControllerCh9329:

    def __init__(
            self, controller_port: str = "COM1",
            baud: int = 9600, screen_x: int = 1920,
            screen_y: int = 1080
    ):
        self.connection_mutex: threading.Lock = threading.Lock()
        self.serial_connection: Serial | None = None
        self.code2key_path = os.path.join(
            SELF_PATH, "data",
            "keyboard_ch9329_code2key.yaml"
        )
        self.ch9329_code2key: dict = {}
        self.press_key_map: dict = {}
        self.controller_port: str = controller_port
        self.baud: int = baud
        self.screen_x: int = screen_x
        self.screen_y: int = screen_y
        self.min_interval: float = 0.2
        self.max_interval: float = 0.5
        self.timeout: float = 0.1

        self.load_hid_code_key(self.code2key_path)

    def get_connection_params(self) -> tuple[str, int, int, int]:
        return self.controller_port, self.baud, self.screen_x, self.screen_y

    def set_connection_params(
            self, controller_port: str = "COM1",
            baud: int = 9600, screen_x: int = 1920,
            screen_y: int = 1080
    ):
        self.controller_port: str = controller_port
        self.baud: int = baud
        self.screen_x: int = screen_x
        self.screen_y: int = screen_y

    def load_hid_code_key(self, file_path: str):
        try:
            with open(file_path, "r", encoding="utf-8") as load_f:
                self.ch9329_code2key = yaml.safe_load(load_f)
                # logger.debug("load ch9329_code2key succeed")
        except FileNotFoundError:
            logger.debug("load ch9329_code2key failed")
            sys.exit(1)

    def create_connection(self) -> bool:
        logger.debug(
            f"init_connection({self.controller_port}, {self.baud}, "
            f"{self.screen_x}, {self.screen_y})"
        )
        connection_created: bool = False
        if self.controller_port == "":
            return connection_created
        self.close_connection()
        with self.connection_mutex:
            try:
                self.serial_connection = Serial(
                    self.controller_port,
                    self.baud,
                    timeout=self.timeout
                )
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
        self.close_connection()
        self.create_connection()

    def random_interval(self) -> float:
        return random.uniform(self.min_interval, self.max_interval)

    def product_info(self) -> str:
        info = ""
        with self.connection_mutex:
            if self.serial_connection is None:
                return info
            if self.serial_connection.is_open is False:
                return info
            info = get_product(self.serial_connection)
        return info

    # 恢复出厂设置
    def restore_factory_settings(self):
        cmd_restore_packet = b"\x57\xab\x00\x0c\x00\x0e"
        with self.connection_mutex:
            if self.serial_connection is None:
                return False
            if self.serial_connection.is_open is False:
                return False
            self.serial_connection.write(cmd_restore_packet)

    # 复位芯片
    def reset_controller(self):
        cmd_reset_packet = b"\x57\xab\x00\x0f\x00\x11"
        with self.connection_mutex:
            if self.serial_connection is None:
                return False
            if self.serial_connection.is_open is False:
                return False
            self.serial_connection.write(cmd_reset_packet)

    def mouse_send_data(self, button_name: str, x: int = 0,
                        y: int = 0,
                        wheel: int = 0,
                        relative: bool = False):
        with self.connection_mutex:
            if self.serial_connection is None:
                return False
            if self.serial_connection.is_open is False:
                return False
            if relative is False:
                mouse.send_data_absolute(self.serial_connection, x, y, button_name, self.screen_x, self.screen_y, wheel)
            else:
                mouse.send_data_relative(self.serial_connection, x, y, button_name, wheel)

    def convert_hid_key_code_to_ch9329_key_code(
            self,
            code: int
    ) -> str:
        string_key: str = "0x{:02x}".format(code)
        ch9329_key: str | None = self.ch9329_code2key.get(
            string_key,
            None
        )
        if ch9329_key is None:
            ch9329_key = ""
        return ch9329_key

    def keyboard_keys_trigger(self, keys: list, function_keys: list):
        with self.connection_mutex:
            if self.serial_connection is None:
                return False
            if self.serial_connection.is_open is False:
                return False
            Ch9329AttachFunction.trigger_keys(
                self.serial_connection,
                keys, function_keys
            )
            logger.debug(f"keyboard keys press : {keys}")
        return True

    def keyboard_light_status(self):
        status: bool = False
        keyboard_light_status: int = 0
        with self.connection_mutex:
            if self.serial_connection is None:
                return status, keyboard_light_status
            if self.serial_connection.is_open is False:
                return status, keyboard_light_status
            cmd_get_info_packet = b"\x57\xab\x00\x01\x00\x03"
            __clear_buffer__: bytes = self.serial_connection.readall()
            self.serial_connection.write(cmd_get_info_packet)
            buffer: bytes = self.serial_connection.readall()
            if len(buffer) == 14:
                keyboard_light_status = buffer[7]
                status = True
            logger.debug(f"keyboard status 0x{keyboard_light_status:02x}")
            return status, keyboard_light_status

    def release(self, device_type: str = "all"):
        if device_type == "mouse":
            mouse.release(self.serial_connection)
        elif device_type == "keyboard":
            keyboard.release(self.serial_connection)
        elif device_type == "all":
            mouse.release(self.serial_connection)
            keyboard.release(self.serial_connection)
        else:
            logger.debug(f"unknown device type: {device_type}")


class Controller(ControllerCh9329):
    pass


if __name__ == "__main__":
    pass
