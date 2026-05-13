# Processing API

Endpoints for controlling the DNG processing pipeline — background LUT application, demosaic algorithm selection, worker lifecycle, and checkpoint management.

The processing worker runs in a **separate OS process** to isolate OOM crashes from the main camera app. It picks up `.mustedit` marker files and processes queued DNG→edited JPEG jobs.

---

## `POST /api/processing/toggle`

Toggle DNG processing on/off.

**Request Body:** None

**Response — `200 OK`:**

```json
{ "enabled": true }
```

---

## `GET /api/processing/status`

Return full processing pipeline status.

**Response — `200 OK`:**

```json
{
  "enabled": true,
  "queue_depth": 2,
  "current": "capture_20260514_120030_auto_4056x3040.dng",
  "worker_alive": true,
  "worker_pid": 12345,
  "worker_state": "running",
  "restart_count": 0,
  "jobs_completed": 5,
  "paused": false,
  "demosaic_algorithm": "PPG",
  "available_algorithms": ["LINEAR", "VNG", "PPG", "AHD", "DCB", "DHT"],
  "demosaic_descriptions": {
    "LINEAR": "Bilinear interpolation. Fastest and lightest on memory, but lowest quality.",
    "VNG": "Variable Number of Gradients. Good balance of quality and speed.",
    "PPG": "Patterned Pixel Grouping. Fast and memory-efficient. Recommended default.",
    "AHD": "Adaptive Homogeneity-Directed. High quality, uses more memory.",
    "DCB": "Directional Cubic interpolation. High quality for fine textures.",
    "DHT": "Directional Homogeneity Test. Best quality but heaviest on memory."
  },
  "luts_loaded": 2,
  "lut_names": ["Film Look", "Warm Tone"],
  "lut_settings": {
    "Film Look": { "enabled": true, "blend": 0.2, "order": 0 },
    "Warm Tone": { "enabled": false, "blend": 0.15, "order": 1 }
  },
  "skipped_jobs": ["capture_20260514_100000_auto_4056x3040.dng"],
  "color_noise_reduction": 0.5
}
```

| Field | Type | Description |
|---|---|---|
| `enabled` | `bool` | Whether processing is enabled globally |
| `queue_depth` | `int` | Number of jobs waiting in queue |
| `current` | `string\|null` | DNG currently being processed, or `null` |
| `worker_alive` | `bool` | Whether the worker process is running |
| `worker_pid` | `int\|null` | Worker process PID |
| `worker_state` | `string` | `"running"`, `"paused"`, `"killed"`, or `"crashed"` |
| `restart_count` | `int` | Number of times the worker has been restarted |
| `jobs_completed` | `int` | Total jobs completed in current session |
| `paused` | `bool` | Whether the worker is paused |
| `demosaic_algorithm` | `string` | Current demosaic algorithm name |
| `available_algorithms` | `string[]` | All supported algorithm names |
| `demosaic_descriptions` | `object` | Human-readable description for each algorithm |
| `luts_loaded` | `int` | Number of .cube LUT files loaded |
| `lut_names` | `string[]` | Names of loaded LUTs |
| `lut_settings` | `object` | Per-LUT settings (enabled, blend, order) |
| `skipped_jobs` | `string[]` | DNG filenames that exceeded max retry attempts |
| `color_noise_reduction` | `float` | Current chroma noise reduction strength (0.0–1.0) |

---

## `GET /api/debug/status`

Alias for `/api/processing/status`. Returns the same data.

---

## `POST /api/debug/demosaic`

Set the demosaic algorithm for DNG processing.

**Request Body (JSON):**

```json
{ "algorithm": "AHD" }
```

**Response — `200 OK`:**

```json
{ "success": true, "algorithm": "AHD" }
```

| Status | Condition |
|---|---|
| `400` | Missing `algorithm` field or unknown algorithm name |

**Available algorithms:** `LINEAR`, `VNG`, `PPG`, `AHD`, `DCB`, `DHT`

---

## `POST /api/debug/luts`

Update per-LUT settings (enable/disable individual LUTs, adjust blend strength).

**Request Body (JSON):**

```json
{
  "settings": {
    "Film Look": { "enabled": true, "blend": 0.3, "order": 0 },
    "Warm Tone": { "enabled": false, "blend": 0.15, "order": 1 }
  }
}
```

| Field | Type | Description |
|---|---|---|
| `settings.<name>.enabled` | `bool` | Whether to apply this LUT |
| `settings.<name>.blend` | `float` | Blend strength (0.0 = no effect, 1.0 = full) |
| `settings.<name>.order` | `int` | Application order (lower = applied first) |

**Response — `200 OK`:**

```json
{ "success": true, "settings": { ... } }
```

---

## `POST /api/debug/worker/pause`

Pause the processing worker. It stops picking up new jobs but stays alive.

**Response:** `{ "success": true, "worker_state": "paused" }`

---

## `POST /api/debug/worker/resume`

Resume the processing worker.

**Response:**

```json
{ "success": true, "worker_state": "running" }
```

If preview is currently running, the worker is kept paused:

```json
{
  "success": true,
  "worker_state": "paused",
  "note": "Worker paused while preview is running. Will resume when preview stops."
}
```

---

## `POST /api/debug/worker/restart`

Kill and restart the processing worker.

**Response:** `{ "success": true, "worker_state": "running" }`

If preview is running, worker starts paused (same pattern as resume).

---

## `POST /api/debug/worker/kill`

Kill the processing worker permanently (no auto-respawn).

**Response:** `{ "success": true, "worker_state": "killed" }`

---

## `POST /api/debug/checkpoints/clear`

Delete all `.decoded.npy` / `.denoised.npy` checkpoint files from the captures directory. These are intermediate files saved during DNG processing for crash recovery.

**Response — `200 OK`:**

```json
{ "success": true, "removed": 4 }
```

---

## `POST /api/debug/thumbnails/regenerate`

Regenerate all gallery thumbnails from source JPEGs.

**Response — `200 OK`:**

```json
{ "success": true, "count": 42 }
```

---

## `POST /api/debug/default_resolution`

Set the default capture resolution.

**Request Body (JSON):**

```json
{ "resolution": "2028x1520" }
```

Pass `null` or omit `resolution` to reset to the highest available.

**Response — `200 OK`:**

```json
{ "success": true, "default_resolution": "2028x1520" }
```

**Error — `400`:** Unknown resolution key.

---

*See also: [API Overview](api-overview.md) · [Capture](api-capture.md) · [Settings](api-settings.md)*
