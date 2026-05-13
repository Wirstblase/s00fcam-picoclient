# Gallery API

Endpoints for browsing, serving, downloading, editing, rotating, and deleting captured images.

---

## `GET /api/gallery`

List all captured images, sorted newest first.

**Response — `200 OK`:**

```json
{
  "captures": [
    {
      "filename": "capture_20260514_120030_auto_4056x3040.jpg",
      "basename": "capture_20260514_120030_auto_4056x3040",
      "size": 4521984,
      "created": 1747224030.5,
      "has_dng": true,
      "dng_filename": "capture_20260514_120030_auto_4056x3040.dng",
      "dng_size": 23789568,
      "has_thumb": true,
      "has_edited": true,
      "edited_filename": "capture_20260514_120030_auto_4056x3040_edited.jpg",
      "to_be_edited": false,
      "edit_failed": false,
      "gallery_rotation": 0
    }
  ]
}
```

| Field | Type | Description |
|---|---|---|
| `filename` | `string` | JPEG filename |
| `basename` | `string` | Filename without extension |
| `size` | `int` | JPEG file size in bytes |
| `created` | `float` | Unix timestamp (mtime) |
| `has_dng` | `bool` | Whether a companion DNG exists |
| `dng_filename` | `string\|null` | DNG filename if it exists |
| `dng_size` | `int` | DNG file size in bytes (0 if none) |
| `has_thumb` | `bool` | Whether a thumbnail exists |
| `has_edited` | `bool` | Whether an `_edited.jpg` exists |
| `edited_filename` | `string\|null` | Edited JPEG filename if it exists |
| `to_be_edited` | `bool` | Whether a `.mustedit` marker exists (queued for processing) |
| `edit_failed` | `bool` | Whether editing exceeded max retry attempts (3) |
| `gallery_rotation` | `int` | Cumulative rotation applied in gallery (0, 90, 180, 270) |

> **Note:** `_edited.jpg` files are **not** listed as separate entries — they appear via their parent capture's `has_edited` / `edited_filename` fields.

---

## `GET /api/gallery/<filename>`

Serve a captured image at full resolution.

**Response:**
- `200 OK` — `Content-Type: image/jpeg` (or `image/x-adobe-dng` for DNG files)
- `400` — filename contains `..` or `/`
- `404` — file not found

**Headers:** `Cache-Control: no-store`

> **Tip:** Works for any file in the captures directory — JPEG, DNG, or edited JPEG.

---

## `GET /api/gallery/<filename>/thumb`

Serve the 400×400 LANCZOS thumbnail for a capture.

**Response:**
- `200 OK` — `Content-Type: image/jpeg`
- Falls back to the full-resolution image if thumbnail doesn't exist

**Headers:** `Cache-Control: no-store`

---

## `GET /api/gallery/<filename>/download`

Download a file with `Content-Disposition: attachment` header (triggers browser download).

**Response:**
- `200 OK` — file data with download headers
- `400` / `404` on invalid/missing filename

---

## `GET /api/gallery/<filename>/exif`

Extract and return EXIF metadata from a capture.

**Response — `200 OK`:**

```json
{
  "source": "dng",
  "make": "Raspberry Pi",
  "model": "RP_imx477",
  "software": "libcamera",
  "datetime": "2026:05:14 12:00:30",
  "datetime_original": "2026:05:14 12:00:30",
  "width": 4056,
  "height": 3040,
  "exposure": "1/500s",
  "iso": 100,
  "has_dng": true,
  "luts": "Film Look (20%), Color Denoise (50%), Total: 4.2s"
}
```

| Field | Type | Description |
|---|---|---|
| `source` | `string` | EXIF source: `"jpeg"` or `"dng"` (DNG values override JPEG when available) |
| `make` | `string` | Camera manufacturer |
| `model` | `string` | Camera model |
| `software` | `string` | Software used |
| `datetime` | `string` | Date/time from IFD0 |
| `datetime_original` | `string` | Original capture date/time |
| `width` | `int` | Image width in pixels |
| `height` | `int` | Image height in pixels |
| `exposure` | `string` | Formatted exposure time (e.g. `"1/500s"`, `"2.0s"`) |
| `iso` | `int` | ISO speed rating |
| `has_dng` | `bool` | Whether a DNG companion exists |
| `luts` | `string` | Applied LUT/editing info (from `ImageDescription` EXIF tag of edited JPEG) |

> **Note:** If a DNG exists, its EXIF values **override** the JPEG values for `exposure`, `iso`, `datetime_original`, `make`, `model`, and `software`. The `luts` field is pulled from the `_edited.jpg` companion if available.

---

## `DELETE /api/gallery/<filename>`

Delete a capture and all its associated files.

**Query Parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `raw_only` | `string` | `"false"` | If `"true"`, only delete the DNG file |

**Normal deletion removes:** JPEG, DNG, edited JPEG, thumbnails (original + edited), `.meta` sidecar.

**Response — `200 OK`:**

```json
{
  "deleted": [
    "capture_20260514_120030_auto_4056x3040.jpg",
    "capture_20260514_120030_auto_4056x3040.dng",
    "capture_20260514_120030_auto_4056x3040_edited.jpg",
    "capture_20260514_120030_auto_4056x3040_thumb.jpg"
  ]
}
```

- `404` — no files found to delete

---

## `POST /api/gallery/<filename>/edit`

Enqueue an existing DNG for (re-)processing with current LUT settings.

**Request Body:** None

**Response:**
- `200 OK` — `{ "success": true }`
- `404` — DNG file not found

**Behavior:**
- Clears the image from the skipped list (if it failed previously)
- Creates a `.mustedit` marker file
- The processing worker will pick it up when running

---

## `DELETE /api/gallery/<filename>/edit`

Cancel a pending edit by removing the `.mustedit` marker file.

**Response:**
- `200 OK` — `{ "success": true }`

---

## `POST /api/gallery/<filename>/rotate`

Permanently rotate a gallery image (modifies the JPEG file on disk).

**Request Body (JSON):**

```json
{
  "degrees": 90,
  "target": "both"
}
```

| Field | Type | Default | Description |
|---|---|---|---|
| `degrees` | `int` | `90` | Rotation in degrees CW. **Must be** `90`, `180`, or `270` |
| `target` | `string` | Config `gallery_rotate_target` | Which files to rotate: `"both"`, `"original"`, `"edited"` |

**Success Response — `200 OK`:**

```json
{
  "success": true,
  "rotated": [
    "capture_20260514_120030_auto_4056x3040.jpg",
    "capture_20260514_120030_auto_4056x3040_edited.jpg"
  ],
  "gallery_rotation": 90
}
```

**Error Responses:**

| Status | Condition |
|---|---|
| `400` | Invalid `degrees` or `target` value |
| `404` | No files found to rotate |
| `500` | Pillow rotation failed |

**Behavior:**
- Preserves EXIF data during rotation
- Preserves original file timestamps (mtime/atime)
- Regenerates thumbnails after rotation
- Tracks cumulative rotation in `.meta` sidecar (`gallery_rotation` field)

---

## `POST /api/gallery/bulk` or `DELETE /api/gallery/bulk`

Delete multiple captures in a single request.

**Request Body (JSON):**

```json
{
  "filenames": [
    "capture_20260514_120030_auto_4056x3040.jpg",
    "capture_20260514_120045_manual_1080p.jpg"
  ],
  "rawOnly": false
}
```

| Field | Type | Default | Description |
|---|---|---|---|
| `filenames` | `string[]` | Required | List of filenames to delete |
| `rawOnly` | `bool` | `false` | If `true`, only delete DNG files |

**Response — `200 OK`:**

```json
{
  "deleted": 2,
  "total": 2
}
```

> **Note:** Invalid filenames (containing `..` or `/`) are silently skipped.

---

## `POST /api/gallery/download-bulk`

Download multiple captures as a single ZIP file.

**Request Body (JSON):**

```json
{
  "filenames": [
    "capture_20260514_120030_auto_4056x3040.jpg",
    "capture_20260514_120045_manual_1080p.jpg"
  ],
  "mode": "default"
}
```

| Field | Type | Default | Description |
|---|---|---|---|
| `filenames` | `string[]` | Required (non-empty) | List of capture filenames |
| `mode` | `string` | `"default"` | Download mode (see below) |

**Download Modes:**

| Mode | Includes |
|---|---|
| `default` | Edited JPEG if available, otherwise original JPEG |
| `all` | Original JPEG + DNG + edited JPEG + `.mustedit` marker |
| `raws` | DNG files only |
| `edited` | Edited JPEG files only |
| `originals` | Original JPEG files only |

**Response:**
- `200 OK` — `Content-Type: application/zip` — ZIP file download
  - Filename: `s00f_bulk_YYYYMMDD_HHMMSS.zip`
- `400` — empty or invalid filenames list, or invalid mode
- `404` — no files found

> **Note:** The ZIP file is created as a temporary file and automatically deleted after the response is sent.

---

## `GET /api/gallery/storage`

Return storage information and size breakdown for captures.

**Response — `200 OK`:**

```json
{
  "total_bytes": 31268536320,
  "used_bytes": 15634268160,
  "free_bytes": 15634268160,
  "error": null,
  "captures_total_size": 524288000,
  "jpeg_size": 150000000,
  "dng_size": 350000000,
  "thumbs_size": 24288000,
  "captures_size": 524288000
}
```

| Field | Type | Description |
|---|---|---|
| `total_bytes` | `int` | Total disk space |
| `used_bytes` | `int` | Used disk space |
| `free_bytes` | `int` | Free disk space |
| `error` | `string\|null` | Error message if storage check failed |
| `captures_total_size` | `int` | Total size: JPEGs + DNGs + thumbnails |
| `jpeg_size` | `int` | Total size of all JPEG files in captures |
| `dng_size` | `int` | Total size of all DNG files in captures |
| `thumbs_size` | `int` | Total size of thumbnail directory |

---

*See also: [API Overview](api-overview.md) · [Capture](api-capture.md) · [Processing](api-processing.md)*
