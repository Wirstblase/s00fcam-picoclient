# Settings & Config API

Endpoints for reading camera capabilities and updating runtime configuration.

---

## `GET /api/settings`

Return all camera settings, capabilities, and current state. This is the primary endpoint for client initialization.

**Response — `200 OK`:**

```json
{
  "camera_detected": true,
  "default_resolution": "4056x3040",
  "resolutions": {
    "4056x3040": {
      "width": 4056,
      "height": 3040,
      "label": "12.3MP (4056×3040)",
      "highlight": true,
      "color": null,
      "icon": "high_quality"
    },
    "2028x1520": {
      "width": 2028,
      "height": 1520,
      "label": "3.1MP (2028×1520)",
      "highlight": true,
      "color": null,
      "icon": "night_sight_max"
    },
    "1080p": {
      "width": 1920,
      "height": 1080,
      "label": "2.1MP (1920×1080) — 1080p",
      "highlight": false,
      "color": null,
      "icon": null
    }
  },
  "modes": [
    {
      "id": "auto",
      "label": "Auto",
      "description": "Continuous metering, fast capture via picamera2"
    },
    {
      "id": "manual",
      "label": "Manual",
      "description": "Control shutter speed, gain, and white balance"
    },
    {
      "id": "instant",
      "label": "Instant",
      "description": "Save preview frame as JPEG (720p, zero latency)"
    },
    {
      "id": "slow_auto",
      "label": "Legacy",
      "description": "Legacy rpicam-still capture (slower, full convergence)"
    }
  ],
  "awb_modes": [
    "auto", "incandescent", "tungsten", "fluorescent",
    "indoor", "daylight", "cloudy", "custom"
  ],
  "shutter_range": {
    "min": 100,
    "max": 200000000,
    "default": 10000
  },
  "gain_range": {
    "min": 1.0,
    "max": 16.0,
    "default": 1.0
  },
  "preview_running": true,
  "oled_focus_enabled": true,
  "oled_enabled": true,
  "processing_enabled": true,
  "picamera2_available": true,
  "metering": {},
  "sentry_mode": false,
  "config": {
    "save_raw": true,
    "inactivity_timeout": 120,
    "preview_auto_standby": true,
    "processing_enabled": true,
    "quality": 95,
    "color_noise_reduction": 0.5,
    "thumb_size": 400,
    "thumb_quality": 80,
    "default_resolution": null,
    "exposure_mode": "long",
    "long_exposure_mode": "predict",
    "sentry_mode": false,
    "gallery_rotate_target": "both"
  }
}
```

| Field | Type | Description |
|---|---|---|
| `camera_detected` | `bool` | Whether camera hardware was found |
| `default_resolution` | `string` | Current default resolution key |
| `resolutions` | `object` | Available resolutions (dynamically detected) |
| `modes` | `array` | Available capture modes with labels and descriptions |
| `awb_modes` | `string[]` | Available auto white balance modes |
| `shutter_range` | `object` | Shutter speed range in microseconds |
| `gain_range` | `object` | Analog gain range |
| `preview_running` | `bool` | Whether preview is currently active |
| `oled_focus_enabled` | `bool` | Whether OLED focus display is active |
| `oled_enabled` | `bool` | Whether OLED display is powered on |
| `processing_enabled` | `bool` | Whether DNG processing is enabled |
| `picamera2_available` | `bool` | Whether picamera2 backend loaded successfully |
| `metering` | `object` | Current metering data (empty if preview not running) |
| `sentry_mode` | `bool` | Whether sentry mode is active |
| `config` | `object` | Full configuration key-value map |

### Resolution Object

| Field | Type | Description |
|---|---|---|
| `width` | `int` | Width in pixels |
| `height` | `int` | Height in pixels |
| `label` | `string` | Human-readable label |
| `highlight` | `bool` | Whether this is a recommended/native resolution |
| `color` | `string\|null` | Optional UI color hint |
| `icon` | `string\|null` | Optional Material icon name (`"high_quality"`, `"night_sight_max"`) |

---

## `POST /api/config/update`

Update one or more global configuration values.

**Request Body (JSON):**

```json
{
  "save_raw": false,
  "quality": 90,
  "inactivity_timeout": 300
}
```

Pass any subset of [configuration keys](api-overview.md#configuration-keys). Unknown keys are ignored. Only keys that exist in the default config are persisted.

**Response — `200 OK`:**

```json
{
  "success": true,
  "config": { ... }
}
```

The response includes the full updated `config` object.

**Special Key Behaviors:**

| Key | Side Effect |
|---|---|
| `inactivity_timeout` | Updates the live inactivity timer value |
| `preview_auto_standby` | Updates the live auto-standby flag |
| `color_noise_reduction` | Updates the processing worker's noise reduction strength |
| `exposure_mode` | Updates the picamera2 AEC exposure mode dynamically |
| `default_resolution` | Updates the camera's default resolution. If empty/null, resets to highest available |
| `save_raw` | Updates the OLED idle info display |
| `sentry_mode` | Routes through `_activate_sentry()` / `_deactivate_sentry()` — config is only persisted on successful activation |

**Error Response (sentry activation failure) — `500`:**

```json
{
  "success": false,
  "error": "Failed to activate sentry mode",
  "config": { ... }
}
```

> **Note:** The `sentry_mode` key is special — its persistence is atomic with the actual activation to prevent config/state desync after failed activations.

---

*See also: [API Overview](api-overview.md) · [Processing](api-processing.md) · [Sentry Mode](api-sentry.md)*
