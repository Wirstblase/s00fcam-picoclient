# Capture API

Endpoints for capturing still images and reading metering data.

Capture routes to different backends based on mode:
- **`auto`**, **`manual`**, **`instant`** → picamera2 (does NOT stop preview)
- **`slow_auto`** → legacy `rpicam-still` subprocess (stops preview, restarts after)

---

## `POST /api/capture`

Take a photo with the given settings.

**Request Body (JSON):**

```json
{
  "mode": "auto",
  "resolution": "4056x3040",
  "shutter": 10000,
  "gain": 1.0,
  "awb": "auto",
  "awb_gains": [1.0, 1.0],
  "raw": false,
  "quality": 95,
  "rotation": {
    "flipH": false,
    "flipV": false,
    "rotateDeg": 0
  }
}
```

All fields are **optional**. Defaults are applied from global config.

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | `string` | `"auto"` | Capture mode: `"auto"`, `"manual"`, `"instant"`, `"slow_auto"` |
| `resolution` | `string` | Config default | Resolution key (e.g. `"4056x3040"`, `"1080p"`) |
| `shutter` | `int` | Auto | Shutter speed in **microseconds** (manual mode only). Range: 100–200,000,000 |
| `gain` | `float` | `1.0` | Analog gain (manual mode only). Range: 1.0–16.0 |
| `awb` | `string` | `"auto"` | White balance mode. See [AWB Modes](api-overview.md#awb-modes) |
| `awb_gains` | `[float, float]` | `[1.0, 1.0]` | Manual WB gains `[red, blue]` (only when `awb` = `"custom"`) |
| `raw` | `bool` | Config `save_raw` | Save DNG alongside JPEG |
| `quality` | `int` | `95` | JPEG quality (1–100) |
| `rotation.flipH` | `bool` | `false` | Horizontal flip |
| `rotation.flipV` | `bool` | `false` | Vertical flip |
| `rotation.rotateDeg` | `int` | `0` | Rotation in degrees CW: `0`, `90`, `180`, `270` |

**Success Response — `200 OK`:**

```json
{
  "success": true,
  "filename": "capture_20260514_120030_auto_4056x3040.jpg",
  "files": [
    "capture_20260514_120030_auto_4056x3040.jpg",
    "capture_20260514_120030_auto_4056x3040.dng",
    "capture_20260514_120030_auto_4056x3040_edited.jpg"
  ],
  "jpeg_size": 4521984,
  "dng_size": 23789568,
  "settings": {
    "mode": "auto",
    "resolution": "4056x3040"
  }
}
```

| Field | Type | Description |
|---|---|---|
| `filename` | `string` | Primary JPEG filename |
| `files` | `string[]` | All files created (JPEG, DNG, edited JPEG) |
| `jpeg_size` | `int` | JPEG file size in bytes |
| `dng_size` | `int` | DNG file size in bytes (0 if not saved) |
| `settings` | `object` | Echo of mode and resolution used |

**Error Responses:**

| Status | Condition | Error message |
|---|---|---|
| `400` | Capture already in progress | `"Capture already in progress"` |
| `500` | Storage full (< 500 MB free) | `"Not enough free space (less than 500MB left)."` |
| `500` | No camera detected | `"No camera detected"` |
| `500` | Subprocess failure | Varies |

**Side Effects:**
- Pauses the processing worker during capture
- Resets the inactivity timer
- If DNG processing is enabled, the DNG is queued for background LUT processing
- A 400×400 LANCZOS thumbnail is generated in `captures_thumbs/`

---

## `GET /api/capture/status`

Check if a capture is currently in progress.

**Response — `200 OK`:**

```json
{
  "is_capturing": false,
  "status": null,
  "progress": "",
  "preview_running": true
}
```

| Field | Type | Description |
|---|---|---|
| `is_capturing` | `bool` | Whether a capture is in progress |
| `status` | `string\|null` | `"capturing"`, `"processing"`, or `null` |
| `progress` | `string` | Human-readable progress message (e.g. `"Saving..."`, `"Generating thumbnail..."`) |
| `preview_running` | `bool` | Whether preview is currently active |

---

## `GET /api/metering`

Return current real-time metering data from the picamera2 backend.

**Response — `200 OK`:**

When preview is running (picamera2 backend):
```json
{
  "exposure_time": 33000,
  "analogue_gain": 1.5,
  "lux": 350.0,
  "colour_temperature": 5500,
  "iso_equivalent": 150
}
```

When preview is not running or picamera2 is unavailable:
```json
{}
```

| Field | Type | Description |
|---|---|---|
| `exposure_time` | `int` | Current exposure time in microseconds |
| `analogue_gain` | `float` | Current analog gain |
| `lux` | `float` | Estimated scene luminance |
| `colour_temperature` | `int` | Estimated colour temperature in Kelvin |
| `iso_equivalent` | `int` | ISO equivalent based on gain |

> **Note:** Metering data is only available when using the picamera2 backend. The legacy rpicam-apps backend does not provide live metering.

---

*See also: [API Overview](api-overview.md) · [Preview](api-preview.md) · [Gallery](api-gallery.md)*
