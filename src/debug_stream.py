#verbose stream test for debugging!!
import network
import time
import st7789
from machine import Pin, SPI, WDT
import gc
import socket
import config
from stream import MJPEGStream
from camera import resolve_host

def init_display():
    spi = SPI(1, baudrate=62_500_000, sck=Pin(10), mosi=Pin(11))
    tft = st7789.ST7789(
        spi, 135, 240,
        reset=Pin(12, Pin.OUT), cs=Pin(9, Pin.OUT),
        dc=Pin(8, Pin.OUT), backlight=Pin(13, Pin.OUT),
        rotation=1,
    )
    tft.init()
    return tft

def main():
    print("[DEBUG] Booting...")
    tft = init_display()
    tft.fill(st7789.BLACK)
    
    print("[DEBUG] Connecting to WiFi...")
    import wifi
    wlan, ip = wifi.connect(tft)
    print("[DEBUG] WiFi connected:", ip)
        
    print("[DEBUG] Resolving camera...")
    cam_host, cam_port = resolve_host()
    print("[DEBUG] Camera resolved to:", cam_host, cam_port)
    
    print("[DEBUG] Initializing WDT...")
    wdt = WDT(timeout=8000)
    
    print("[DEBUG] Creating MJPEGStream object...")
    stream = MJPEGStream()
    
    print("[DEBUG] Calling _connect_stream...")
    while True:
        try:
            print("[DEBUG] Connecting to stream...")
            stream.connect(cam_host, cam_port, wdt=wdt)
            print("[DEBUG] Stream connected successfully!")
            break
        except OSError as e:
            wdt.feed()
            print("[DEBUG] Stream connect OSError:", e)
            time.sleep(2)
            wdt.feed()

    print("[DEBUG] Entering read_frame loop...")
    for i in range(10):
        print(f"[DEBUG] Attempting to read frame {i}...")
        try:
            frame = stream.read_frame(wdt=wdt)
            print(f"[DEBUG] Frame {i} read successfully! Size: {len(frame)} bytes")
            wdt.feed()
        except OSError as e:
            print(f"[DEBUG] OSError reading frame {i}: {e}")
            break
            
        print(f"[DEBUG] Decoding frame {i} on TFT...")
        try:
            tft.jpg(frame, 0, 0)
            print(f"[DEBUG] Frame {i} decoded on TFT successfully!")
        except Exception as e:
            print(f"[DEBUG] TFT decode exception: {e}")
            
        gc.collect()
        
    print("[DEBUG] Stream test completed without crashing!")

try:
    main()
except Exception as e:
    print("[FATAL ERROR]:", e)
