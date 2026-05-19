# s00fcam-picoclient

This project aims to build a super thin 'client' based on the Raspberry Pi Pico 2 W (paired with a ST7789 1.14" 240×135 Display HAT) for my [DIY camera project](https://github.com/Wirstblase/s00f-camera-test-backend).

The camera runs its own hotspot and exposes many endpoints and a video stream, allowing various addons & gizmos to interact with it such as remote controllers, phone apps, deep-learning vision models for object detection, etc.

## The problem

My camera does not have a screen (I mean it does, but one good enough to show a live preview) or even a viewfinder, so taking pictures with it like a 'normal camera' is a pretty bad experience:) It has a tiny 128x32 oled that shows just the most crucial information and a focus score to help you at least get (whatever you're shooting) in focus. 

This project attempts to solve that by bringing a viewfinder and some crude camera controls, maybe a simple photo viewer too to bridge the gap between this being just a gimmick and a (decently) usable camera.

I plan to give this client its own little battery back and to mount it to the back of the camera with some magnets and pogo pins, allowing it to act as a detachable remote control kind of device, inspired by the insta360 GO series but kinda in reverse.

## The hardware

[This Pi pico board](https://ro.farnell.com/raspberry-pi/sc1633/rpi-pico-2w-brd-32-bit-arm-cortex/dp/4568690)

[This Display](https://ro.farnell.com/seeed-studio/103030400/lcd-display-module-raspberry-pi/dp/4060364)

TODO: decide on battery pack, power module, design a case for it to fit on the camera, more shall be added

## How I pulled this off

Streaming live video to a $6 microcontroller isn't supposed to be easy:) but quite surprisingly, it is possible

 After burning a display (I soldered the pins on the pico the other way around) and then spent a night painstakingly debugging it and blaming it on my lack of experience with micropython, followed by a huge headache trying to debug it, almost giving up, then ordering another screen and another pico, here we are:

 ### Custom Firmware

Decided a more realistic approach was to bake the `st7789_mpy` C driver directly into the MicroPython firmware. 

The process involved:
1. **Setting up the build environment**: Cloned the official `micropython` repository and the `pico-sdk` to cross-compile for the RP2040 architecture.
2. **Injecting the C Module**: Cloned `russhughes/st7789_mpy` and linked it into the build process using the `USER_C_MODULES` flag. This allows Python code to call `tft.jpg()` and have it executed entirely in highly-optimized C code with direct memory access.
3. **Building for Pico W**: Compiled the `ports/rp2` port specifically for the `RPI_PICO_W` board definition so the CYW43 network stack (WiFi) was bundled alongside the display driver.


Configured the SPI bus to scream at **62.5 MHz** to push pixels to the LCD as fast as physically possible.

### Issues issues issues

The camera backend was sending beautiful `320x180` JPEGs, but the screen was just showing a tiny, glitchy rectangle. What gives?

It turns out the Pico's C display driver uses a library called `TJpgDec`, which is incredibly fast but very strictly bound to memory. It has absolutely **zero scaling capabilities**. When we fed it a 320-pixel wide image to display on a 240-pixel wide screen, it decoded exactly one 8x8 block of pixels, realized the image was too big, and **instantly aborted**. Weirdly, it was trying to display the image in some sort of text mode, it was exactly as big as and replacing the last char displayed on screen.

solution: had to update the camera backend to serve a dedicated stream at -exactly- the right resolution (`240x135`), memory usage dropped to just ~3KB per frame!

Once the resolution was fixed, the Pico started rendering exactly ONE frame... and then it would freeze forever. Turns out every three frames the stream would push out a thumbnail, which we didn't account for and it was just fed into the decoder which didn't understand the data and would just freeze.

Implemented an 8s Watchdog Timer. If the code ever gets stuck, the Pico reboots. Had to carefully place `wdt.feed()` calls throughout the MJPEG parser, the TCP handshake, and the garbage collector.

Next issue: I wanted _zero latency_, so I wrote a script to parse the stream and skip older frames if the network was sending data too fast. But the Pi got trapped in a timing loop: it would find a frame, see a newer one arriving, discard the old one, read more data, see an even newer one, discard the old one... **forever.** It was fetching as fast as it could but never actually stopping to draw the picture

the fix: `O(1)` backwards search using Python's `.rfind()` to search the buffer in reverse, we instantly locate the *absolute latest* HTTP boundary in the buffer, extract that single perfect frame, and dump the rest. 


---

### result
Can't believe it, I have achieved a (decently functional) low-latency wireless viewfinder. The Pico connects to WiFi, handshakes with the backend, parses chunked HTTP streams, rips out the JPEG payload, and displays it at ~15 FPS, with enough CPU time to listen for a physical button press to trigger the camera
