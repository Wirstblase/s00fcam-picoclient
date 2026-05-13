# Sentry Mode API

Sentry mode enforces **continuous preview streaming**, prevents the auto-standby timer from stopping the camera, and pauses background DNG processing to ensure exclusive camera access. Designed for external monitoring software (e.g. motion detection, security).

> **For external clients:** Use the idempotent `POST /api/sentry/enable` and `POST /api/sentry/disable` endpoints. Avoid `toggle` — it is non-idempotent and races between concurrent callers.

---

## `POST /api/sentry/enable`

Idempotently activate sentry mode.

**Request Body:** None

**Response — `200 OK`:**

```json
{
  "active": true,
  "already_active": false
}
```

| Field | Type | Description |
|---|---|---|
| `active` | `bool` | Always `true` on success |
| `already_active` | `bool` | `true` if sentry was already on (no-op) |

**Error — `500`:**

```json
{ "active": false, "error": "Failed to start preview" }
```

**Side Effects:**
- Starts preview if not running
- Pauses processing worker
- Shows sentry icon on OLED
- Persists `sentry_mode: true` to config (only on success)

---

## `POST /api/sentry/disable`

Idempotently deactivate sentry mode. Preview stays running — stop it separately via `POST /api/preview/stop` if needed.

**Request Body:** None

**Response — `200 OK`:**

```json
{
  "active": false,
  "already_inactive": false
}
```

| Field | Type | Description |
|---|---|---|
| `active` | `bool` | Always `false` |
| `already_inactive` | `bool` | `true` if sentry was already off (no-op) |

---

## `POST /api/sentry/toggle`

Flip sentry mode on↔off atomically.

> **Not recommended for external clients.** Two concurrent toggles cancel each other out.

**Response — `200 OK`:**

```json
{ "active": true }
```

**Error — `500`:** Same as `/enable`.

---

## `GET /api/sentry/status`

Return sentry mode status and uptime.

**Response — `200 OK`:**

```json
{
  "active": true,
  "uptime_s": 128.5,
  "stream_info": {
    "resolution": "1280x720",
    "framerate": "~30fps"
  }
}
```

When inactive: `uptime_s` = `0.0`, `stream_info` = `null`.

---

## `POST /api/sentry/snap`

Capture a photo while sentry mode is active. Returns the filename for later retrieval via `GET /api/gallery/<filename>`.

**Request Body (optional, JSON):**

```json
{
  "mode": "auto",
  "resolution": "1080p",
  "shutter": 10000,
  "gain": 1.0
}
```

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | `string` | `"auto"` | `"auto"`, `"instant"`, or `"manual"` |
| `resolution` | `string` | Config default | Target resolution |
| `shutter` | `int` | Auto | Shutter speed in µs (manual mode) |
| `gain` | `float` | Auto | Analog gain (manual mode) |

**Success — `200 OK`:**

```json
{
  "filename": "capture_20260514_153045_auto_4056x3040.jpg",
  "files": ["capture_20260514_153045_auto_4056x3040.jpg"]
}
```

**Error Responses:**

| Status | Condition |
|---|---|
| `409` | `{ "error": "Sentry mode is not active" }` |
| `500` | Capture failed (hardware/internal error) |

---

## `GET /api/sentry/ready`

Check if the camera is ready to capture (preview running and not currently capturing).

**Response — `200 OK`:**

```json
{ "ready": true }
```

---

### Typical External Client Workflow

```
1. POST /api/sentry/enable        → activate sentry mode
2. GET  /api/sentry/ready          → poll until ready=true
3. GET  /api/preview/snapshot      → grab a preview frame for analysis
4. POST /api/sentry/snap           → capture full-res image
5. GET  /api/gallery/<filename>    → download the captured image
6. POST /api/sentry/disable        → deactivate when done
```

---

*See also: [API Overview](api-overview.md) · [Preview](api-preview.md) · [Capture](api-capture.md)*
