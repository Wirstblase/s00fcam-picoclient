# Preview API

Endpoints for controlling the live camera preview stream.

The preview uses **picamera2** as the primary backend (MJPEG @ ~30fps). If picamera2 is unavailable, it falls back to a **rpicam-vid → ffmpeg** pipeline (MJPEG @ ~15fps). Both backends stream at **1280×720**.

> **Important:** The camera is an exclusive-access resource. Preview is automatically paused during capture and while the processing worker is active.

---

## `GET /api/preview/stream`

MJPEG stream endpoint. Connect an `<img>` tag or video player to this URL.

**Usage:**
```html
<img src="http://<pi-ip>:5000/api/preview/stream" />
```

**Response:**
- `200 OK` — `Content-Type: multipart/x-mixed-replace; boundary=frame`
- Continuous stream of JPEG frames, each prefixed with multipart boundary headers
- Stream ends when the preview is stopped or the client disconnects

**Behavior:**
- If preview is not running, it is **auto-started** on first request
- Multiple clients can connect simultaneously (picamera2 backend); legacy backend serializes reads
- The stream keeps running until explicitly stopped via `/api/preview/stop`

---

## `GET /api/preview/snapshot`

Return a single JPEG frame from the current preview. Useful for timelapse, OctoPrint integration, or polling-based clients.

**Response:**
- `200 OK` — `Content-Type: image/jpeg` — raw JPEG binary data
- `503 Service Unavailable` — no frame available yet

**Behavior:**
- If preview is not running, it is **auto-started**
- Returns the most recent frame captured by the preview pipeline

---

## `POST /api/preview/start`

Explicitly start the preview stream.

**Request Body:** None

**Response:**
```json
{ "success": true }
```

| Status | Condition |
|---|---|
| `200` | Preview started (or was already running) |
| `400` | `{ "success": false, "error": "No camera detected" }` — no camera hardware found |

**Side Effects:**
- Pauses the processing worker (camera is exclusive-access)
- Enables OLED focus display
- Resets focus peak score
- Resets the inactivity timer

---

## `POST /api/preview/stop`

Stop the preview stream and put camera into standby.

**Request Body:** None

**Response:**
```json
{ "success": true }
```

| Status | Condition |
|---|---|
| `200` | Preview stopped successfully |
| `409` | `{ "success": false, "error": "Cannot stop preview while Sentry Mode is active" }` — sentry mode blocks preview stop |

**Side Effects:**
- Disables OLED focus display
- Resumes the processing worker (if it was paused for preview, in autorun mode)

---

*See also: [API Overview](api-overview.md) · [Sentry Mode](api-sentry.md)*
