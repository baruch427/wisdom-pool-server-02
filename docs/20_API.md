# Wisdom Pool Server API

**Version:** 1.3
**Date:** November 19, 2025

This document outlines the API endpoints for the Wisdom Pool Server.

## Monitoring

- **Endpoint:** `GET /`
- **Description:** Returns a welcome message.
- **Arguments:** None
- **Return Value:** `JSON`
  ```json
  {
    "message": "Server is running"
  }
  ```

### Health Check

- **Endpoint:** `GET /health`
- **Description:** Returns the server's health status, including startup time and current server time.
- **Arguments:** None
- **Return Value:** `HealthStatus`
  ```json
  {
    "status": "ok",
    "start_time_utc": "2023-10-27T10:00:00.000Z",
    "server_time_utc": "2023-10-27T10:05:00.000Z",
    "commit_hash": "local-dev"
  }
  ```

### Get In-Memory Logs

- **Endpoint:** `GET /logs`
- **Description:** Returns all logs captured in memory since the last time they were cleared. This is intended for testing and debugging purposes.
- **Arguments:** None
- **Return Value:** `text/plain`
  ```
  2025-11-15 10:00:00,000 - api_logger - INFO - Log cleared.
  2025-11-15 10:01:00,000 - api_logger - INFO - Creating new stream...
  ...
  ```

### Clear In-Memory Logs

- **Endpoint:** `DELETE /logs/clear`
- **Description:** Clears all logs currently stored in memory.
- **Arguments:** None
- **Return Value:** `JSON`
  ```json
  {
    "message": "Log cleared."
  }
  ```

---

## Pools

### Create a new pool

- **Endpoint:** `POST /api/v1/pools`
- **Description:** Creates a new pool.
- **Arguments:**
  - **Request Body:**
    - `pool_content`: `PoolContent` object.
      ```json
      {
        "title": "The Nature of Consciousness",
        "description": "A curated collection of thoughts and resources exploring consciousness."
      }
      ```
    - `creator_id`: (string) The ID of the user creating the pool.
- **Return Value:** `Pool`
  ```json
  {
    "pool_id": "pool_123",
    "creator_id": "user_abc",
    "created_at": "2023-10-27T10:00:00.000Z",
    "content": {
      "title": "The Nature of Consciousness",
      "description": "A curated collection of thoughts and resources exploring consciousness."
    }
  }
  ```

### Get a pool by ID

- **Endpoint:** `GET /api/v1/pools/{pool_id}`
- **Description:** Retrieves a pool by its ID.
- **Arguments:**
  - **Path Parameters:**
    - `pool_id`: (string) The ID of the pool to retrieve.
- **Return Value:** `Pool`
  ```json
  {
    "pool_id": "pool_123",
    "creator_id": "user_abc",
    "created_at": "2023-10-27T10:00:00.000Z",
    "content": {
      "title": "The Nature of Consciousness",
      "description": "A curated collection of thoughts and resources exploring consciousness."
    }
  }
  ```

### List pools

- **Endpoint:** `GET /api/v1/pools`
- **Description:** Returns a paginated list of pools with optional creator filtering.
- **Arguments:**
  - **Query Parameters:**
    - `limit` (integer, optional, default: 20, min: 1, max: 100) — number of pools to return.
    - `offset` (integer, optional, default: 0, min: 0) — number of pools to skip.
    - `creator_id` (string, optional) — only return pools created by this user.
- **Return Value:** `PoolListResponse`
  ```json
  {
    "pools": [
      {
        "pool_id": "pool_123",
        "creator_id": "user_abc",
        "created_at": "2023-10-27T10:00:00.000Z",
        "content": {
          "title": "The Nature of Consciousness",
          "description": "A curated collection of thoughts and resources exploring consciousness."
        }
      }
    ],
    "total_count": 42,
    "has_more": true,
    "next_offset": 20
  }
  ```

---

## Streams

### Create a new stream

- **Endpoint:** `POST /api/v1/streams`
- **Description:** Creates a new stream within a specified pool.
- **Arguments:**
  - **Request Body:**
    - `stream_content`: `StreamContent` object.
      ```json
      {
        "title": "Exploring Quantum Mechanics",
        "description": "A stream of thoughts on quantum physics.",
        "ai_framing": "This stream is framed as a journey from classical to quantum physics.",
        "category": "Science",
        "image": "https://example.com/image.jpg"
      }
      ```
    - `pool_id`: (string) The ID of the pool this stream belongs to.
    - `creator_id`: (string) The ID of the user creating the stream.
- **Return Value:** `Stream`
  ```json
  {
    "stream_id": "stream_456",
    "pool_id": "pool_123",
    "creator_id": "user_abc",
    "created_at": "2023-10-27T10:00:00.000Z",
    "first_drop_placement_id": null,
    "last_drop_placement_id": null,
    "content": {
      "title": "Exploring Quantum Mechanics",
      "description": "A stream of thoughts on quantum physics.",
      "ai_framing": "This stream is framed as a journey from classical to quantum physics.",
      "category": "Science",
      "image": "https://example.com/image.jpg"
    }
  }
  ```

### Get a stream by ID

- **Endpoint:** `GET /api/v1/streams/{stream_id}`
- **Description:** Retrieves stream metadata by its ID.
- **Arguments:**
  - **Path Parameters:**
    - `stream_id`: (string) The ID of the stream to retrieve.
- **Return Value:** `Stream`
  ```json
  {
    "stream_id": "stream_456",
    "pool_id": "pool_123",
    "creator_id": "user_abc",
    "created_at": "2023-10-27T10:00:00.000Z",
    "first_drop_placement_id": "placement_789",
    "last_drop_placement_id": "placement_987",
    "content": {
        "title": "Exploring Quantum Mechanics",
        "description": "A stream of thoughts on quantum physics.",
        "ai_framing": "This stream is framed as a journey from classical to quantum physics.",
        "category": "Science",
        "image": "https://example.com/image.jpg"
    }
  }
  ```

### List streams in a pool

- **Endpoint:** `GET /api/v1/pools/{pool_id}/streams`
- **Description:** Returns a paginated list of streams that belong to the specified pool.
- **Arguments:**
  - **Path Parameters:**
    - `pool_id`: (string) The ID of the pool whose streams should be retrieved.
  - **Query Parameters:**
    - `limit` (integer, optional, default: 20, min: 1, max: 100) — number of streams to return.
    - `offset` (integer, optional, default: 0, min: 0) — number of streams to skip.
    - `creator_id` (string, optional) — only return streams created by this user.
- **Return Value:** `StreamListResponse`
  ```json
  {
    "streams": [
      {
        "stream_id": "stream_456",
        "pool_id": "pool_123",
        "creator_id": "user_abc",
        "created_at": "2023-10-27T10:00:00.000Z",
        "first_drop_placement_id": null,
        "last_drop_placement_id": null,
        "content": {
          "title": "Exploring Quantum Mechanics",
          "description": "A stream of thoughts on quantum physics.",
          "ai_framing": "This stream is framed as a journey from classical to quantum physics.",
          "category": "Science",
          "image": "https://example.com/image.jpg"
        }
      }
    ],
    "total_count": 10,
    "has_more": false,
    "next_offset": null
  }
  ```

### Add drop(s) to a stream

- **Endpoint:** `POST /api/v1/streams/{stream_id}/drops`
- **Description:** Adds one or more drops to a stream. This is a transactional operation that creates the drop, creates a placement record, and updates the stream's pointers. To add a single drop, the body should be a `DropContent` object. To add multiple drops, the body should be an array of `DropContent` objects.
- **Arguments:**
  - **Path Parameters:**
    - `stream_id`: (string) The ID of the stream to add the drop to.
  - **Request Body:** A JSON object with the following fields:
    - `drops`: A `DropContent` object for a single drop, or a `List[DropContent]` for multiple drops.
    - `creator_id`: (string) The ID of the user creating the drop(s).
      ```json
      // Single drop example
      {
        "drops": {
          "title": "What is superposition?",
          "text": "Superposition is a fundamental principle of quantum mechanics.",
          "images": ["https://example.com/superposition.jpg"],
          "type": "text"
        },
        "creator_id": "user_abc"
      }
      ```
      ```json
      // Multiple drops example
      {
        "drops": [
          {
            "title": "First Drop",
            "text": "This is the first drop."
          },
          {
            "title": "Second Drop",
            "text": "This is the second drop."
          }
        ],
        "creator_id": "user_abc"
      }
      ```
- **Return Value:** `AddDropResponse` (for single drop) or `AddDropsResponse` (for multiple drops)
  ```json
  // Single drop response
  {
    "drop_id": "drop_abc",
    "creator_id": "user_abc",
    "created_at": "2023-10-27T10:00:00.000Z",
    "content": {
      "title": "What is superposition?",
      "text": "Superposition is a fundamental principle of quantum mechanics.",
      "images": ["https://example.com/superposition.jpg"],
      "type": "text"
    },
    "placement_id": "placement_123",
    "stream_id": "stream_456",
    "position_info": {
      "next_placement_id": null,
      "prev_placement_id": "placement_987"
    }
  }
  ```
  ```json
  // Multiple drops response
  {
    "drops": [
      {
        "drop_id": "drop_1",
        "creator_id": "user_abc",
        "created_at": "2023-10-27T10:00:00.000Z",
        "content": { "title": "First Drop", "text": "This is the first drop." },
        "placement_id": "placement_1",
        "stream_id": "stream_456",
        "position_info": { "next_placement_id": "placement_2", "prev_placement_id": "placement_987" }
      },
      {
        "drop_id": "drop_2",
        "creator_id": "user_abc",
        "created_at": "2023-10-27T10:00:01.000Z",
        "content": { "title": "Second Drop", "text": "This is the second drop." },
        "placement_id": "placement_2",
        "stream_id": "stream_456",
        "position_info": { "next_placement_id": null, "prev_placement_id": "placement_1" }
      }
    ]
  }
  ```

### Get drops in a stream

- **Endpoint:** `GET /api/v1/streams/{stream_id}/drops`
- **Description:** Get drops in a stream, with pagination. Supports both forward and backward traversal.
- **Arguments:**
  - **Path Parameters:**
    - `stream_id`: (string) The ID of the stream.
  - **Query Parameters:**
    - `from_placement_id`: (string, optional) The placement ID to start retrieving drops from (inclusive). If not provided, starts from the beginning of the stream (for positive limit) or end of the stream (for negative limit).
    - `limit`: (integer, optional, default: 10) The number of drops to return. **Positive values** (e.g., `limit=10`): include `from_placement_id` and retrieve forward (chronologically). **Negative values** (e.g., `limit=-10`): include `from_placement_id` and retrieve backward (reverse chronologically). Range: -50 to +50, excluding 0.
- **Return Value:** `GetDropsResponse`
  ```json
  {
    "drops": [
      {
        "drop_id": "drop_abc",
        "creator_id": "user_abc",
        "created_at": "2023-10-27T10:00:00.000Z",
        "content": {
          "title": "What is superposition?",
          "text": "Superposition is a fundamental principle of quantum mechanics.",
          "images": ["https://example.com/superposition.jpg"],
          "type": "text"
        },
        "placement_id": "placement_123",
        "next_placement_id": "placement_456",
        "prev_placement_id": "placement_789"
      }
    ],
    "has_more": true,
    "total_count": 25
  }
  ```

---

## Drops

### Get a drop by ID

- **Endpoint:** `GET /api/v1/drops/{drop_id}`
- **Description:** Retrieves a single drop by its ID.
- **Arguments:**
  - **Path Parameters:**
    - `drop_id`: (string) The ID of the drop to retrieve.
- **Return Value:** `Drop`
  ```json
  {
    "drop_id": "drop_abc",
    "creator_id": "user_abc",
    "created_at": "2023-10-27T10:00:00.000Z",
    "content": {
      "title": "What is superposition?",
      "text": "Superposition is a fundamental principle of quantum mechanics.",
      "images": ["https://example.com/superposition.jpg"],
      "type": "text"
    }
  }
  ```

---

## User State & Progress

### Update User Progress

- **Endpoint:** `POST /api/v1/user/progress`
- **Description:** Idempotent heartbeat to record where the user is currently looking. This updates both the global `last_active_context` and the specific `stream_history` entry for the given stream.
- **Auth:** Required (uses `get_current_user_id` dependency)
- **Request Body:**
  ```json
  {
    "pool_id": "string",
    "stream_id": "string",
    "placement_id": "string"
  }
  ```
- **Return Value:** `204 No Content`

### Get User River

- **Endpoint:** `GET /api/v1/user/river`
- **Description:** Returns the user's recent reading history ("river") ordered by the last time each stream was touched, newest first, capped at 30 records.
- **Auth:** Required (uses `get_current_user_id` dependency)
- **Query Parameters:**
  - `limit` (integer, optional, default: 30, min: 1, max: 30) — number of records to return.
- **Return Value:** `RiverResponse`
  ```json
  {
    "records": [
      {
        "stream_id": "stream_456",
        "last_read_placement_id": "placement_123",
        "updated_at": "2025-11-20T18:25:43.511Z"
      }
    ]
  }
  ```
- **Errors:** `422 Unprocessable Entity` if `limit` is outside the `[1, 30]` range.

---

## Data Models

### PoolContent

```json
{
  "title": "string",
  "description": "string"
}
```

### Pool

```json
{
  "pool_id": "string",
  "creator_id": "string",
  "created_at": "ISO 8601 datetime",
  "content": "PoolContent"
}
```

### StreamContent

```json
{
  "title": "string",
  "description": "string",
  "ai_framing": "string (optional)",
  "category": "string (optional)",
  "image": "string (optional, URL)"
}
```

### Stream

```json
{
  "stream_id": "string",
  "pool_id": "string",
  "creator_id": "string",
  "created_at": "ISO 8601 datetime",
  "first_drop_placement_id": "string or null",
  "last_drop_placement_id": "string or null",
  "content": "StreamContent"
}
```

### DropContent

```json
{
  "title": "string (optional)",
  "text": "string",
  "images": ["string (URL)"] (optional),
  "type": "string (optional, default: 'text')"
}
```

### Drop

```json
{
  "drop_id": "string",
  "creator_id": "string",
  "created_at": "ISO 8601 datetime",
  "content": "DropContent"
}
```

### UserProgress

```json
{
  "pool_id": "string",
  "stream_id": "string",
  "placement_id": "string"
}
```

### RiverRecord

```json
{
  "stream_id": "string",
  "last_read_placement_id": "string or null",
  "updated_at": "ISO 8601 datetime"
}
```

### RiverResponse

```json
{
  "records": ["RiverRecord"]
}
```