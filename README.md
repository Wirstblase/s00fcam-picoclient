# s00fcam-picoclient

This project aims to build a super thin 'client' based on the Raspberry Pi Pico 2 W (paired with a ST7789 1.14" 240×135 Display HAT) for my [DIY camera project](https://github.com/Wirstblase/s00f-camera-test-backend).

The camera runs its own hotspot and exposes many endpoints and a video stream, allowing various addons & gizmos to interact with it such as remote controllers, phone apps, deep-learning vision models for object detection, etc.

## The problem

My camera does not have a screen (I mean it does, but one good enough to show a live preview) or even a viewfinder, so taking pictures with it like a 'normal camera' is a pretty bad experience:) It has a tiny 128x32 oled that shows just the most crucial information and a focus score to help you at least get (whatever you're shooting) in focus. 

This project attempts to solve that by bringing a viewfinder and some crude camera controls, maybe a simple photo viewer too to bridge the gap between this being just a gimmick and a (decently) usable camera.

I plan to give this client its own little battery back and to mount it to the back of the camera with some magnets and pogo pins, allowing it to act as a detachable remote control kind of device, inspired by the insta360 GO series but kinda in reverse:)


