# main.py — s00fcam-picoclient entry point
# Boot sequence: display → WiFi → camera → MJPEG stream loop
# Button A (GP15) captures a photo. No UI, just the stream.

import gc
import time
from machine import Pin, SPI, WDT

import st7789
import vga1_8x16 as font
import config
import wifi
import camera
from stream import MJPEGStream

# ---------------------------------------------------------------------------
# Onboard LED — lights up to confirm code is running
# On Pico 2 W the LED is on the CYW43 chip, addressed as "LED"
# ---------------------------------------------------------------------------
def init_led():
    try:
        led = Pin("LED", Pin.OUT)
        led.on()
        return led
    except Exception:
        return None

# ---------------------------------------------------------------------------
# Display init
# ---------------------------------------------------------------------------
def init_display():
    spi = SPI(
        config.DISP_SPI_ID,
        baudrate=config.DISP_BAUD,
        sck=Pin(config.DISP_SCK),
        mosi=Pin(config.DISP_MOSI),
    )
    tft = st7789.ST7789(
        spi,
        config.DISP_WIDTH,
        config.DISP_HEIGHT,
        reset=Pin(config.DISP_RST, Pin.OUT),
        cs=Pin(config.DISP_CS, Pin.OUT),
        dc=Pin(config.DISP_DC, Pin.OUT),
        backlight=Pin(config.DISP_BL, Pin.OUT),
        rotation=config.DISP_ROTATION,
    )
    tft.init()
    return tft


def show_text(tft, text, fg=st7789.WHITE, bg=st7789.BLACK):
    #centered multi-line text on solid bg
    tft.fill(bg)
    lines = text.split("\n")
    total_h = len(lines) * font.HEIGHT
    y = max(0, (tft.height() - total_h) // 2)
    for line in lines:
        x = max(0, (tft.width() - len(line) * font.WIDTH) // 2)
        tft.text(font, line, x, y, fg, bg)
        y += font.HEIGHT

# ---------------------------------------------------------------------------
# Button setup
# ---------------------------------------------------------------------------
def init_buttons():
    """Initialize button A as input with pull-up. Returns Pin object."""
    btn_a = Pin(config.BTN_A, Pin.IN, Pin.PULL_UP)
    return btn_a

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    gc.collect()

    led = init_led()

    tft = init_display()
    show_text(tft, "s00fcam\npicoclient")
    time.sleep(1)

    wlan, ip = wifi.connect(tft)
    gc.collect()

    show_text(tft, "Finding camera...")
    cam_host, cam_port = camera.resolve_host()

    show_text(tft, "Ping camera...")
    retries = 0
    while not camera.ping(cam_host, cam_port):
        retries += 1
        show_text(tft, "Camera offline\nRetry #{}...".format(retries))
        time.sleep(2)
    gc.collect()

    btn_a = init_buttons()

    stream = MJPEGStream()
    show_text(tft, "Loading stream...")

    _run_stream_loop(tft, stream, btn_a, wlan, cam_host, cam_port)


def _run_stream_loop(tft, stream, btn_a, wlan, cam_host, cam_port):

    # watchdog
    wdt = WDT(timeout=config.WATCHDOG_TIMEOUT)

    frame_count = 0
    last_heartbeat = time.time()
    btn_was_pressed = False

    while True:
        # Ensure WiFi
        if not wifi.is_connected(wlan):
            show_text(tft, "WiFi lost!\nReconnecting...")
            stream.close()
            wlan, _ = wifi.connect(tft)
            gc.collect()

        # Ensure stream
        if not stream.connected:
            _connect_stream(tft, stream, cam_host, cam_port, wdt)
            frame_count = 0
            gc.collect()

        try:
            frame = stream.read_frame(wdt=wdt)
            wdt.feed()
        except OSError:
            stream.close()
            show_text(tft, "Stream lost\nReconnecting...")
            time.sleep(1)
            continue

        try:
            tft.jpg(frame, 0, 0)
        except Exception:
            pass

        frame_count += 1

        if frame_count % config.GC_EVERY_N_FRAMES == 0:
            gc.collect()

        now = time.time()
        if now - last_heartbeat >= config.HEARTBEAT_INTERVAL:
            camera.heartbeat(cam_host, cam_port)
            last_heartbeat = now

        btn_pressed = btn_a.value() == 0  # active LOW
        if btn_pressed and not btn_was_pressed:
            _handle_capture(tft, stream, cam_host, cam_port, wdt)
            gc.collect()
        btn_was_pressed = btn_pressed


def _connect_stream(tft, stream, cam_host, cam_port, wdt):
    while True:
        try:
            stream.connect(cam_host, cam_port, wdt=wdt)
            return
        except OSError as e:
            wdt.feed()
            show_text(tft, "Stream error\n{}".format(e))
            time.sleep(2)
            wdt.feed()
            show_text(tft, "(Re)loading stream...")


def _handle_capture(tft, stream, cam_host, cam_port, wdt):
    #camera is exclusive-access during capture
    stream.close()

    show_text(tft, "Capturing...")

    ok, msg = camera.capture(cam_host, cam_port)

    if ok:
        show_text(tft, "Captured!\n{}".format(msg[:28]), fg=st7789.GREEN)
    else:
        show_text(tft, "Failed!\n{}".format(msg[:28]), fg=st7789.RED)

    wdt.feed()
    time.sleep(2)
    wdt.feed()

    show_text(tft, "Resuming stream...")
    _connect_stream(tft, stream, cam_host, cam_port, wdt)


# ---------------------------------------------------------------------------
# Entry point w 2s delay so mpremote/Thonny can interrupt before we start
# ---------------------------------------------------------------------------
print("s00fcam-picoclient: booting in 2s... (Ctrl+C to cancel)")
time.sleep(2)
try:
    main()
except KeyboardInterrupt:
    print("Interrupted — dropping to REPL")
except Exception as e:
    print("FATAL:", e)
    try:
        tft = init_display()
        show_text(tft, "ERROR\n{}".format(str(e)[:20]), fg=st7789.RED)
    except Exception:
        pass
