import json

# ---------------------------------------------------------------------------
# Display — Waveshare Pico LCD 1.14" (ST7789, 135x240, SPI1)
# ---------------------------------------------------------------------------
DISP_WIDTH  = 135
DISP_HEIGHT = 240
DISP_SPI_ID = 1
DISP_BAUD   = 62_500_000   # 62.5 MHz — max stable for RP2350 SPI1
DISP_SCK    = 10
DISP_MOSI   = 11
DISP_CS     = 9
DISP_DC     = 8
DISP_RST    = 12
DISP_BL     = 13
DISP_ROTATION = 1           # landscape: 0°=portrait, 1°=landscape, 2°=inv portrait, 3°=inv landscape

# ---------------------------------------------------------------------------
# Buttons
# ---------------------------------------------------------------------------
BTN_A = 15   # KEY_A — capture photo (active LOW, internal pull-up)
BTN_B = 17   # KEY_B — reserved for future use

# ---------------------------------------------------------------------------
# Camera network
# ---------------------------------------------------------------------------
#todo: load these from a file maybe? instead of being hardcoded here, maybe package with wifi creds.
CAMERA_HOST        = "workshop-pi.local"
CAMERA_PORT        = 5000
CAMERA_IP_FALLBACK = "192.168.4.1"   # used if mDNS resolution fails
STREAM_PATH        = "/api/preview/stream/viewfinder"
SNAPSHOT_PATH      = "/api/preview/snapshot"
CAPTURE_PATH       = "/api/capture"
HEARTBEAT_PATH     = "/api/heartbeat"
SYSTEM_STATUS_PATH = "/api/system/status"

# ---------------------------------------------------------------------------
# Stream / memory tuning
# ---------------------------------------------------------------------------
STREAM_BUF_SIZE    = 50 * 1024   # 50 KB sliding buffer for MJPEG chunks
STREAM_RECV_SIZE   = 4096        # bytes per socket.recv() call
SOCKET_TIMEOUT     = 10          # seconds — connect + read timeout
HEARTBEAT_INTERVAL = 30          # seconds between heartbeat POSTs
GC_EVERY_N_FRAMES  = 10          # run gc.collect() every N frames
WATCHDOG_TIMEOUT   = 8000        # ms — WDT resets board if main loop hangs

# ---------------------------------------------------------------------------
# WiFi
# ---------------------------------------------------------------------------
WIFI_CREDS_FILE    = "wifi_creds.json"
WIFI_RETRY_MAX     = 15          # max seconds between retries (exponential backoff cap)
WIFI_CONNECT_TIMEOUT = 20        # seconds to wait for single connect attempt


def load_wifi_creds():
    try:
        with open(WIFI_CREDS_FILE, "r") as f:
            creds = json.load(f)
        ssid = creds.get("ssid", "").strip()
        password = creds.get("password", "").strip()
        if not ssid:
            raise ValueError("SSID is empty")
        return ssid, password
    except OSError:
        raise OSError("wifi_creds.json not found — run setup_wifi.sh and copy to Pico")
    except (ValueError, KeyError) as e:
        raise ValueError("Bad wifi_creds.json: {}".format(e))
