'''MJPEG stream parser for s00f camera
Opens a persistent HTTP connection to the MJPEG endpoint,
parses multipart boundaries by scanning for JPEG SOI/EOI markers
and yields raw JPEG frame bytes.'''

import socket
import gc
import config

# JPEG markers
_SOI = b'\xff\xd8'  # Start Of Image
_EOI = b'\xff\xd9'  # End Of Image


class MJPEGStream:
    """Persistent MJPEG stream reader over raw TCP socket.

    Uses a pre-allocated bytearray buffer to avoid heap fragmentation.
    Supports frame-skipping: if multiple complete frames accumulate in
    the buffer (Pico can't keep up), jumps to the latest one.
    """

    __slots__ = ('_host', '_port', '_path', '_sock', '_buf', '_blen',
                 '_mv', '_connected')

    def __init__(self):
        self._buf = bytearray(config.STREAM_BUF_SIZE)
        self._mv = memoryview(self._buf)
        self._blen = 0
        self._sock = None
        self._connected = False
        self._host = None
        self._port = None
        self._path = config.STREAM_PATH

    def connect(self, host, port, wdt=None):
        self.close()  
        self._host = host
        self._port = port
        self._blen = 0

        s = socket.socket()
        s.settimeout(config.SOCKET_TIMEOUT)
        s.connect((host, port))
        
        if wdt: wdt.feed()
        
        # now switch to 1s timeout so we can feed WDT during long recv() blocks
        # (The camera backend can take 5-6 seconds to start the picamera2 pipeline)
        s.settimeout(1.0)
        import time

        # send HTTP/1.0 GET — 1.0 avoids chunked transfer-encoding
        req = (
            "GET {} HTTP/1.0\r\n"
            "Host: {}:{}\r\n"
            "Connection: close\r\n"
            "\r\n"
        ).format(self._path, host, port)
        s.send(req.encode())

        hdr_buf = b""
        t0 = time.time()
        while b"\r\n\r\n" not in hdr_buf:
            try:
                chunk = s.recv(256)
                if wdt: wdt.feed()
                if not chunk:
                    s.close()
                    raise OSError("Stream closed during header read")
                hdr_buf += chunk
            except OSError as e:
                if wdt: wdt.feed()
                if time.time() - t0 > config.SOCKET_TIMEOUT:
                    s.close()
                    raise OSError("Header read timeout")

        body_start = hdr_buf.find(b"\r\n\r\n") + 4
        leftover = hdr_buf[body_start:]
        if leftover:
            n = len(leftover)
            self._buf[:n] = leftover
            self._blen = n

        self._sock = s
        self._connected = True

    def read_frame(self, wdt=None):
        """
        returns a bytes object containing the full JPEG data (SOI to EOI inclusive).
        Implements frame-skipping: returns the LATEST complete frame in the buffer.
        Raises OSError if the stream disconnects."""

        while True:
            frame = self._extract_latest_frame()
            if frame is not None:
                return frame

            space = len(self._buf) - self._blen
            if space < config.STREAM_RECV_SIZE:
                self._compact_buffer()
                space = len(self._buf) - self._blen

            if space <= 0:
                self._blen = 0
                space = len(self._buf)

            try:
                n = self._sock.readinto(self._mv[self._blen:self._blen + min(space, config.STREAM_RECV_SIZE)])
                if wdt: wdt.feed()
                if n is None or n == 0:
                    self._connected = False
                    raise OSError("Stream disconnected")
                self._blen += n
            except OSError as e:
                if e.args[0] == 110 or e.args[0] == 'ETIMEDOUT':
                    if wdt: wdt.feed()
                    continue
                self._connected = False
                raise OSError("Stream read error: {}".format(e))

    def _extract_latest_frame(self):

        last_boundary = self._buf.rfind(b'--frame', 0, self._blen)
        if last_boundary < 0:
            return None

        soi_pos = self._buf.rfind(b'\xff\xd8', 0, last_boundary)
        if soi_pos < 0:
            remaining = self._blen - last_boundary
            if remaining > 0:
                self._buf[:remaining] = self._buf[last_boundary:self._blen]
            self._blen = remaining
            return None

        frame_end = last_boundary
        eoi = self._buf.rfind(b'\xff\xd9', soi_pos, last_boundary)
        if eoi >= 0:
            frame_end = eoi + 2

        frame = bytes(self._buf[soi_pos:frame_end])

        remaining = self._blen - last_boundary
        if remaining > 0:
            self._buf[:remaining] = self._buf[last_boundary:self._blen]
        self._blen = remaining

        return frame

    def _compact_buffer(self):
        last_soi = -1
        pos = 0
        while True:
            idx = self._buf.find(b'\xff\xd8', pos, self._blen)
            if idx < 0:
                break
            last_soi = idx
            pos = idx + 2

        if last_soi > 0:
            remaining = self._blen - last_soi
            if remaining > 0:
                self._buf[:remaining] = self._buf[last_soi:self._blen]
            self._blen = remaining
        elif last_soi < 0:
            self._blen = 0

    def close(self):
        if self._sock is not None:
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None
        self._connected = False
        self._blen = 0

    @property
    def connected(self):
        return self._connected
