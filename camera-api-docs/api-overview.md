# s00f Camera API — Overview

> **Base URL:** `http://<pi-ip>:5000`  
> **Transport:** HTTP/1.1 — JSON request/response unless noted otherwise  
> **Authentication:** None (local network only)

---

## Documentation Index

| Document | Endpoints |
|---|---|
| [Preview](api-preview.md) | Stream, snapshot, start, stop |
| [Capture](api-capture.md) | Capture photo, capture status, metering |
| [Gallery](api-gallery.md) | List, serve, thumbnails, EXIF, delete, rotate, edit, bulk ops, storage |
| [Settings & Config](api-settings.md) | Get settings, update config |
| [Sentry Mode](api-sentry.md) | Enable, disable, toggle, status, snap, ready |
| [Processing](api-processing.md) | Toggle, status, worker control, LUTs, demosaic, checkpoints |
| [System & Display](api-system.md) | System status, shutdown, reboot, display, heartbeat |

---

## Common Patterns

### Success Responses

Most mutating endpoints return:

```json
{ "success": true }
```

Some include additional data alongside `success`.

### Error Responses

All errors return an appropriate HTTP status code with a JSON body:

```json
{ "error": "Human-readable error description" }
```

| HTTP Code | Meaning |
|---|---|
| `400` | Bad request — invalid parameters, missing fields, path traversal |
| `404` | Resource not found |
| `409` | Conflict — action blocked by current state (e.g. sentry mode active) |
| `500` | Internal server error — hardware failure, subprocess error |
| `503` | Service unavailable — preview not running (snapshot endpoint) |

### Global Error Handlers

| Code | Response |
|---|---|
| `404` | `{ "error": "Not found" }` |
| `500` | `{ "error": "Internal server error" }` |

### Filename Conventions

Captured images follow this naming pattern:

```
capture_YYYYMMDD_HHMMSS_{mode}_{resolution}.jpg
capture_YYYYMMDD_HHMMSS_{mode}_{resolution}.dng       (if RAW enabled)
capture_YYYYMMDD_HHMMSS_{mode}_{resolution}_edited.jpg (if processing enabled)
```

Where:
- `mode` = `auto`, `manual`, `instant`, or `slow_auto`
- `resolution` = e.g. `4056x3040`, `2028x1520`, `1080p`, `720p`

### Filename Sanitization

All gallery endpoints that accept a `<filename>` path parameter reject requests containing `..` or `/` with a `400` status to prevent path traversal.

---

## Configuration Keys

These keys can be read via `GET /api/settings` (in the `config` field) and updated via `POST /api/config/update`.

| Key | Type | Default | Description |
|---|---|---|---|
| `save_raw` | `bool` | `true` | Save DNG alongside JPEG on capture |
| `inactivity_timeout` | `int` | `120` | Seconds before preview auto-stops (when `preview_auto_standby` is enabled) |
| `preview_auto_standby` | `bool` | `true` | Enable/disable the inactivity timeout |
| `processing_enabled` | `bool` | `true` | Enable DNG→edited JPEG processing with LUTs |
| `quality` | `int` | `95` | Default JPEG quality (1–100) |
| `color_noise_reduction` | `float` | `0.5` | Chroma noise reduction strength (0.0–1.0) |
| `thumb_size` | `int` | `400` | Thumbnail max dimension in pixels |
| `thumb_quality` | `int` | `80` | Thumbnail JPEG quality |
| `default_resolution` | `string\|null` | `null` | Default capture resolution key (e.g. `"4056x3040"`). `null` = highest available |
| `exposure_mode` | `string` | `"long"` | AEC exposure mode: `"normal"`, `"short"`, `"long"` |
| `long_exposure_mode` | `string` | `"predict"` | Long exposure strategy: `"predict"` or `"converge"` |
| `sentry_mode` | `bool` | `false` | Persisted sentry mode state (managed by sentry endpoints) |
| `gallery_rotate_target` | `string` | `"both"` | Which files gallery rotation applies to: `"both"`, `"original"`, `"edited"` |

---

## Capture Modes

| Mode ID | Label | Description |
|---|---|---|
| `auto` | Auto | Continuous AEC metering via picamera2, fast capture |
| `manual` | Manual | Full control: shutter speed, analog gain, white balance |
| `instant` | Instant | Save current preview frame as JPEG (720p, zero latency) |
| `slow_auto` | Legacy | Legacy `rpicam-still` subprocess with full AEC convergence (slower) |

---

## Resolution Keys

Resolutions are **dynamically detected** from the connected camera sensor. Standard entries for a typical IMX477 sensor:

| Key | Width | Height | Notes |
|---|---|---|---|
| `4056x3040` | 4056 | 3040 | Full 12MP (highlighted) |
| `2028x1520` | 2028 | 1520 | Half 3MP (highlighted) |
| `1080p` | 1920 | 1080 | Always available (ISP downscale) |
| `720p` | 1280 | 720 | Always available (ISP downscale) |

> **Note:** The actual resolution keys depend on the camera module attached. The `1080p` and `720p` fallbacks are always injected.

---

## AWB Modes

`auto`, `incandescent`, `tungsten`, `fluorescent`, `indoor`, `daylight`, `cloudy`, `custom`

When `awb` is `"custom"`, provide `awb_gains: [red_gain, blue_gain]`.

---

## Server Limits

| Limit | Value |
|---|---|
| Max upload size | 16 MB |
| Min free space for capture | 500 MB |
| Preview resolution | 1280×720 @ ~30fps (picamera2) or ~15fps (legacy) |
| Shutter range | 100 µs – 200,000,000 µs (200s) |
| Gain range | 1.0× – 16.0× |

---

*Last updated: May 2026*
