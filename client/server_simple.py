# write a simple web server with existing index.html file
import os
import socket
import threading as th
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from loguru import logger

path = os.path.dirname(os.path.abspath(__file__))


class handler(SimpleHTTPRequestHandler):
    def __init__(self, request, client_address, server, *, directory=...) -> None:
        super().__init__(request, client_address, server, directory=os.path.join(path, "web_s"))


def check_port_available(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) != 0


def start_server(port=None):
    global server, server_thread
    if port is None:
        port = 5020
        while not check_port_available(port):
            port += 1
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    server_thread = th.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    logger.info(f"Web client serving at http://127.0.0.1:{port}/")
    return port


def stop_server():
    server.shutdown()
    server_thread.join()


if __name__ == "__main__":
    import time

    start_server()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_server()
        print("Server stopped.")
