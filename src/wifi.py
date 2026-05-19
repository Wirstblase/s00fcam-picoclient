# Blocks until connected. Shows status on LCD if provided.

import network
import time
import st7789
import vga1_8x16 as font
import config


def connect(tft=None):

    try:
        ssid, password = config.load_wifi_creds()
    except (OSError, ValueError) as e:
        _show(tft, str(e), error=True)
        raise

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if wlan.isconnected():
        ip = wlan.ifconfig()[0]
        _show(tft, "Connected!\n{}".format(ip))
        return wlan, ip

    _show(tft, "Connecting...\n{}".format(ssid))

    attempt = 0
    backoff = 1  # seconds

    while True:
        attempt += 1
        wlan.connect(ssid, password)

        t0 = time.time()
        while not wlan.isconnected():
            if time.time() - t0 > config.WIFI_CONNECT_TIMEOUT:
                break
            time.sleep(0.5)

        if wlan.isconnected():
            ip = wlan.ifconfig()[0]
            _show(tft, "Connected!\n{}".format(ip))
            time.sleep(2)
            return wlan, ip

        _show(tft, "WiFi retry #{}\n{}".format(attempt, ssid))
        wlan.disconnect()
        time.sleep(backoff)
        backoff = min(backoff * 2, config.WIFI_RETRY_MAX)


def is_connected(wlan):
    try:
        return wlan.isconnected()
    except Exception:
        return False


def _show(tft, msg, error=False):
    
    if tft is None:
        return
    try:
        color = st7789.RED if error else st7789.WHITE
        bg = st7789.BLACK
        tft.fill(bg)
        lines = msg.split("\n")
        y = max(0, (tft.height() - len(lines) * font.HEIGHT) // 2)
        for line in lines:
            x = max(0, (tft.width() - len(line) * font.WIDTH) // 2)
            tft.text(font, line, x, y, color, bg)
            y += font.HEIGHT
    except Exception:
        pass  # display errors must never block WiFi
