import inspect
import json
import logging
import os
import re
import secrets
import threading as th
import time

from flask import (
    Flask,
    Response,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
from flask_sock import Sock
from loguru import logger
from PySide6 import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtMultimedia import *
from PySide6.QtMultimediaWidgets import *
from PySide6.QtWidgets import *
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.serving import make_server

PATH = os.path.dirname(os.path.abspath(__file__))


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1
        message = record.getMessage()
        # remove timestamp like [19/Sep/2023 14:08:16]
        message = re.sub(r"\[\d+/\w+/\d{4} \d{2}:\d{2}:\d{2}\] ", "", message)
        # remove terminal color code
        message = re.sub(r"\x1b\[\d+m", "", message)
        message = re.sub(r"\x1b\[\d+;\d+m", "", message)
        logger.opt(depth=depth, exception=record.exc_info).log(level, message)


logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

kvm_default_config = {
    "web_title": "KVM Remote Control Interface",
    "video": {
        "width": 1920,
        "height": 1080,
        "quality": 60,
        "format": "NV12",
        "show_fps": False,
        "avail_res": [],
        "avail_fmt": [],
    },
}


app = Flask(__name__, static_folder=os.path.join(PATH, "web"), static_url_path="")
sock = Sock(app)
cors = CORS(app, supports_credentials=True, allow_headers="*")
auth = HTTPBasicAuth()

app.template_folder = os.path.join(PATH, "web")

auth_users = {}
auth_secrets = {None: False}


def generate_secret():
    global auth_secrets
    secret = secrets.token_hex(16)
    while secret in auth_secrets:
        secret = secrets.token_hex(16)
    auth_secrets[secret] = False
    return secret


def add_auth_user(username, password):
    global auth_users
    auth_users[username] = generate_password_hash(password)


def count_auth_users():
    global auth_users
    return len(auth_users)


@auth.verify_password
def verify_password(username, password):
    if username in auth_users and check_password_hash(auth_users[username], password):
        return username


def get_browser_uuid():
    data = request.headers.get("User-Agent", "Unknown")
    return hash(data)


@app.route("/login")
@auth.login_required
def login():
    args = request.args.copy()
    red = args.pop("r", None)
    _ = args.pop("s", None)
    if red not in ["http_index", "http_stream", "http_snapshot", "http_info", "http_config"]:
        return Response(f"Invalid redirect: {red}", status=401)
    secret = generate_secret()
    broswer_id = get_browser_uuid()
    logger.info(f"Login: {auth.current_user()} - {secret} - {broswer_id}")
    auth_secrets[secret] = broswer_id
    return redirect(url_for(red, s=secret, **args))


def check_auth_secret():
    secret = request.args.get("s", None)
    if secret is None:
        return False
    if secret not in auth_secrets:
        return False
    if auth_secrets[secret] == get_browser_uuid():
        return True
    auth_secrets.pop(secret)
    logger.info(f"Logout: {secret}")
    return False


class FPSCounter:
    def __init__(self, max_sample=40) -> None:
        self.t = time.perf_counter()
        self.max_sample = max_sample
        self.t_list = []
        self.time_list = []

    def update(self) -> None:
        t = time.perf_counter()
        self.t_list.append(t - self.t)
        self.time_list.append(t)
        self.t = t
        if len(self.t_list) > self.max_sample:
            self.t_list.pop(0)
            self.time_list.pop(0)

    def get(self) -> float:
        now = time.perf_counter()
        if len(self.t_list) > 0:
            while len(self.time_list) > 0 and now - self.time_list[0] > 1:
                self.t_list.pop(0)
                self.time_list.pop(0)
            length = len(self.t_list)
            sum_t = sum(self.t_list)
            if sum_t == 0:
                return 0.0
            else:
                return length / sum_t
        return 0.0

    def reset(self):
        self.t_list = []
        self.t = time.perf_counter()


fpc = FPSCounter()


class KVM_Server(QObject):
    def __init__(self, parent=None):
        self.config = kvm_default_config.copy()
        self.running = False
        self.camera_opened = False
        self.command_callback = None
        self.auth_required = False

        app.route("/")(self.http_index)
        app.route("/<path:path>")(self.public_file)
        sock.route("/websocket")(self.websocket)
        app.route("/stream")(self.http_stream)
        app.route("/snapshot")(self.http_snapshot)
        app.route("/config")(self.http_config)
        super().__init__(parent=parent)

    def http_index(self):
        if self.auth_required:
            if not check_auth_secret():
                return redirect(url_for("login", r="http_index"))
        return render_template("index.html")

    def public_file(self, path):
        return send_from_directory("web", path)

    def websocket(self, sock):
        if self.auth_required:
            if not check_auth_secret():
                return redirect(url_for("login", r="websocket"))
        while True:
            data = sock.receive()
            if data:
                try:
                    jdata = json.loads(data)
                    data_type = jdata["type"]
                    data_payload = jdata["payload"]
                    if self.command_callback is not None:
                        self.command_callback(data_type, data_payload)
                    else:
                        logger.debug(f"Command: {data_type} {data_payload}")
                except Exception as e:
                    logger.error(f"Error Command: {e}")

    def register_command_callback(self, callback):
        self.command_callback = callback

    def camera_error_occurred(self, error, string):
        logger.error(f"Camera error: {error}")

    def open_camera(self, device_name):
        if self.camera_opened:
            return True, ""
        cameras = QMediaDevices.videoInputs()
        for camera in cameras:
            if camera.description() == device_name:
                self.camera_info = camera
                break
        else:
            return False, f"Camera {device_name} not found"
        self.config["video"]["avail_res"] = []
        self.config["video"]["avail_fmt"] = []
        fmt = None
        for i in self.camera_info.videoFormats():
            f = i.pixelFormat().name.split("_")[1]
            if (
                i.resolution().width() == self.config["video"]["width"]
                and i.resolution().height() == self.config["video"]["height"]
                and f == self.config["video"]["format"]
            ):
                fmt = i
            res = f"{i.resolution().width()}x{i.resolution().height()}"
            if res not in self.config["video"]["avail_res"]:
                self.config["video"]["avail_res"].append(res)
            if f not in self.config["video"]["avail_fmt"]:
                self.config["video"]["avail_fmt"].append(f)
        if fmt is None:
            return (
                False,
                f"Camera {device_name} does not support {self.config['video']['width']}x{self.config['video']['height']}",
            )
        self.camera = QCamera(self.camera_info)
        self.camera.setCameraFormat(fmt)
        self.camera.errorOccurred.connect(self.camera_error_occurred)

        self.capture_session = QMediaCaptureSession()
        self.capture_session.setCamera(self.camera)
        self.sink = QVideoSink()
        self.sink.videoFrameChanged.connect(self.frame_changed)
        self.capture_session.setVideoSink(self.sink)

        self.image_event = th.Event()
        self.ba1 = QByteArray()
        self.buffer1 = QBuffer(self.ba1)
        self.buffer1.open(QIODevice.WriteOnly)
        self.ba2 = QByteArray()
        self.buffer2 = QBuffer(self.ba2)
        self.buffer2.open(QIODevice.WriteOnly)
        self.camera.start()
        self.camera_opened = True
        return True, ""

    def close_camera(self):
        self.camera.stop()
        del self.camera
        del self.capture_session
        del self.sink
        self.buffer1.close()
        self.buffer2.close()
        self.camera_opened = False

    def frame_changed(self, frame: QVideoFrame):
        self.image = frame.toImage()
        self.image_event.set()

    def get_stream(self):
        while self.running:
            self.image_event.wait()
            self.image_event.clear()
            if self.config["video"]["show_fps"]:
                fpc.update()
                image = self.image.copy()
                painter = QPainter(image)
                painter.setPen(QPen(Qt.red))
                painter.setFont(QFont("Arial", 20))
                painter.drawText(10, 30, f"{fpc.get():.3f}")
                painter.end()
            else:
                image = self.image
            self.ba1.clear()
            self.buffer1.seek(0)
            if self.config["video"]["quality"] != 0:
                image.save(self.buffer1, "jpg", self.config["video"]["quality"])
                yield (b"Content-Type: data/jpeg\r\n\r\n" + bytes(self.buffer1.data()) + b"\r\n\r\n--frame\r\n")
            else:
                image.save(self.buffer1, "png")
                yield (b"Content-Type: data/png\r\n\r\n" + bytes(self.buffer1.data()) + b"\r\n\r\n--frame\r\n")

    def get_snapshot(self):
        self.image_event.wait()
        self.image_event.clear()
        self.ba2.clear()
        self.buffer2.seek(0)
        self.image.save(self.buffer2, "png")
        return bytes(self.buffer2.data())

    def http_stream(self):
        if self.auth_required:
            if not check_auth_secret():
                return redirect(url_for("login", r="http_stream"))
        return Response(self.get_stream(), mimetype="multipart/x-mixed-replace; boundary=frame")

    def http_snapshot(self):
        if self.auth_required:
            if not check_auth_secret():
                return redirect(url_for("login", r="http_snapshot"))
        return Response(self.get_snapshot(), mimetype="image/png")

    def http_config(self):
        if self.auth_required:
            if not check_auth_secret():
                return redirect(url_for("login", r="http_config", **request.args))
        res = request.args.get("res", None)
        fmt = request.args.get("fmt", None)
        show_fps = request.args.get("show_fps", None)
        quality = request.args.get("quality", None)
        if not any([res, show_fps, quality, fmt]):
            return jsonify(self.config)
        if (
            res is not None
            and fmt is not None
            and (
                res != f"{self.config['video']['width']}x{self.config['video']['height']}"
                or fmt != self.config["video"]["format"]
            )
        ):
            video_width = int(res.split("x")[0])
            video_height = int(res.split("x")[1])
            cfmt = None
            for i in self.camera_info.videoFormats():
                f = i.pixelFormat().name.split("_")[1]
                if i.resolution().width() == video_width and i.resolution().height() == video_height and f == fmt:
                    cfmt = i
            if cfmt is not None:
                self.camera.stop()
                self.camera.setCameraFormat(cfmt)
                self.camera.start()
                self.config["video"]["width"] = video_width
                self.config["video"]["height"] = video_height
                self.config["video"]["format"] = fmt
        if show_fps is not None:
            self.config["video"]["show_fps"] = (
                show_fps == "true" or show_fps == "1" or show_fps == "True" or show_fps is True
            )
        if quality is not None:
            video_quality = int(quality)
            video_quality = max(0, min(100, video_quality))
            self.config["video"]["quality"] = video_quality
        logger.info(
            f'New config set: {self.config["video"]["width"]}x{self.config["video"]["height"]}, quality={self.config["video"]["quality"]}, show_fps={self.config["video"]["show_fps"]}, format={self.config["video"]["format"]}'
        )
        return jsonify(self.config)

    def start_server(self, host, port, device):
        """
        Start the server non-blocking
        """
        assert not self.running, "Server already running"
        if not self.camera_opened:
            ret, msg = self.open_camera(device)
            if not ret:
                raise Exception(msg)
        self.running = True
        self.server = make_server(host, port, app, threaded=True, processes=1)
        self.server_thread = th.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()

    def stop_server(self):
        """
        Stop the server
        """
        assert self.running, "Server not running"
        self.running = False
        self.server.shutdown()
        self.server_thread.join()
        self.close_camera()


if __name__ == "__main__":
    qapp = QApplication()
    server = KVM_Server()
    add_auth_user("admin", "admin")
    server.auth_required = False
    server.start_server("0.0.0.0", 80, "USB Video")
    qapp.exec()
