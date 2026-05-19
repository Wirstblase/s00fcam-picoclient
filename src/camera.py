# camera.py — HTTP client for s00fcam API (non-stream calls)
# Uses raw sockets, no urequests dependency.

import socket
import json
import config


def resolve_host():
    #tries mdns, fallback ip
    try:
        addr_info = socket.getaddrinfo(config.CAMERA_HOST, config.CAMERA_PORT)
        if addr_info:
            return addr_info[0][-1][0], config.CAMERA_PORT
    except (OSError, IndexError):
        pass
    return config.CAMERA_IP_FALLBACK, config.CAMERA_PORT


def capture(host, port):
    #POST /api/capture
    body = '{"mode":"auto"}'
    try:
        status, resp = _post(host, port, config.CAPTURE_PATH, body)
        if status == 200 and resp.get("success"):
            fname = resp.get("filename", "photo")
            return True, fname
        return False, resp.get("error", "Capture failed (HTTP {})".format(status))
    except Exception as e:
        return False, str(e)


def heartbeat(host, port):
    #POST /api/heartbeat
    try:
        _post(host, port, config.HEARTBEAT_PATH, "")
    except Exception:
        pass


def ping(host, port):
    #GET /api/system/status. Returns True if camera is reachable
    try:
        status, _ = _get(host, port, config.SYSTEM_STATUS_PATH)
        return status == 200
    except Exception:
        return False


def _post(host, port, path, body):
    #raw HTTP POST returns (status_code, parsed_json_body)
    s = socket.socket()
    s.settimeout(config.SOCKET_TIMEOUT)
    try:
        s.connect((host, port))
        req = (
            "POST {} HTTP/1.0\r\n"
            "Host: {}:{}\r\n"
            "Content-Type: application/json\r\n"
            "Content-Length: {}\r\n"
            "\r\n"
            "{}"
        ).format(path, host, port, len(body), body)
        s.send(req.encode())
        return _read_response(s)
    finally:
        s.close()


def _get(host, port, path):
    #raw HTTP GET returns (status_code, parsed_json_body)
    s = socket.socket()
    s.settimeout(config.SOCKET_TIMEOUT)
    try:
        s.connect((host, port))
        req = (
            "GET {} HTTP/1.0\r\n"
            "Host: {}:{}\r\n"
            "\r\n"
        ).format(path, host, port)
        s.send(req.encode())
        return _read_response(s)
    finally:
        s.close()


def _read_response(s):
    buf = b""
    while True:
        try:
            chunk = s.recv(1024)
            if not chunk:
                break
            buf += chunk
        except OSError:
            break

    sep = buf.find(b"\r\n\r\n")
    if sep < 0:
        return 0, {}

    header_part = buf[:sep].decode("utf-8", "ignore")
    body_part = buf[sep + 4:]

    status = 0
    first_line = header_part.split("\r\n")[0]
    parts = first_line.split(" ", 2)
    if len(parts) >= 2:
        try:
            status = int(parts[1])
        except ValueError:
            pass

    resp = {}
    if body_part:
        try:
            resp = json.loads(body_part)
        except (ValueError, TypeError):
            pass

    return status, resp
