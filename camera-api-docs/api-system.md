# System & Display API

Endpoints for OLED display control, system health monitoring, and power management.

---

## Display

### `POST /api/display/toggle`

Toggle the OLED focus score display on/off.

**Request Body:** None

**Response — `200 OK`:**

```json
{ "enabled": true }
```

**Side Effects:** When turning on, resets the focus peak score for a fresh session.

---

### `POST /api/display/power`

Toggle the OLED screen on/off (master power switch).

**Request Body:** None

**Response — `200 OK`:**

```json
{ "oled_enabled": true }
```

---

### `GET /api/display/status`

Return current OLED display state.

**Response — `200 OK`:**

```json
{
  "focus_enabled": true,
  "oled_enabled": true
}
```

| Field | Type | Description |
|---|---|---|
| `focus_enabled` | `bool` | Whether focus score display is active |
| `oled_enabled` | `bool` | Whether the OLED screen is powered on |

---

## System

### `GET /api/system/status`

Return Raspberry Pi system health: throttling flags, temperature, and storage.

**Response — `200 OK`:**

```json
{
  "under_voltage": false,
  "freq_capped": false,
  "throttled": false,
  "soft_temp_limit": false,
  "under_voltage_occurred": true,
  "freq_capped_occurred": false,
  "throttled_occurred": true,
  "soft_temp_limit_occurred": false,
  "has_issues": false,
  "has_past_issues": true,
  "raw_value": "0x50000",
  "error": null,
  "temperature": 42.8,
  "history": {
    "under_voltage": 1747224000.0,
    "freq_capped": null,
    "throttled": 1747224000.0,
    "soft_temp_limit": null
  },
  "storage": {
    "total_bytes": 31268536320,
    "used_bytes": 15634268160,
    "free_bytes": 15634268160,
    "error": null
  }
}
```

| Field | Type | Description |
|---|---|---|
| `under_voltage` | `bool` | Currently under-voltage |
| `freq_capped` | `bool` | CPU frequency currently capped |
| `throttled` | `bool` | Currently throttled |
| `soft_temp_limit` | `bool` | Soft temperature limit active |
| `*_occurred` | `bool` | Whether the condition has occurred since boot |
| `has_issues` | `bool` | Any current issue active |
| `has_past_issues` | `bool` | Any issue has occurred since boot |
| `raw_value` | `string` | Raw hex value from `vcgencmd get_throttled` |
| `error` | `string\|null` | Error message (e.g. `vcgencmd` not found on non-Pi) |
| `temperature` | `float\|null` | CPU temperature in °C |
| `history` | `object` | Unix timestamps of last occurrence for each warning type (`null` = never) |
| `storage` | `object` | Disk usage for the captures partition |

> **Note:** On non-Raspberry Pi systems, `error` will be set to `"vcgencmd not found"` and all flags will be `false`.

---

### `POST /api/system/shutdown`

Shut down the Raspberry Pi gracefully.

**Request Body:** None

**Response — `200 OK`:**

```json
{ "success": true }
```

**Side Effects:**
- Shows "OFF" animation on OLED
- Executes `sudo shutdown -h now`

> ⚠️ **Destructive:** The Pi will power off. The response may not reach the client.

---

### `POST /api/system/reboot`

Reboot the Raspberry Pi gracefully.

**Request Body:** None

**Response — `200 OK`:**

```json
{ "success": true }
```

**Side Effects:**
- Shows "OFF" animation on OLED
- Executes `sudo reboot`

> ⚠️ **Destructive:** The Pi will restart. The server will be unavailable during reboot (~30–60s).

---

## Heartbeat

### `POST /api/heartbeat`

Web client heartbeat. Keeps the OLED from showing "DISCONNECTED" status.

**Request Body:** None

**Response — `200 OK`:**

```json
{ "ok": true }
```

> **Usage:** The web UI sends this periodically. External clients should call this if they want the OLED to reflect that a client is connected.

---

*See also: [API Overview](api-overview.md) · [Settings](api-settings.md)*
