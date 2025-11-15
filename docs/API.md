# Wisdom Pool Server API

This document outlines the API endpoints for the Wisdom Pool Server.

## Monitoring

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

### Add drop(s) to a stream

- **Endpoint:** `POST /api/v1/streams/{stream_id}/drops`
- **Description:** Adds one or more drops to a stream. This is a transactional operation that creates the drop, creates a placement record, and updates the stream's pointers. To add a single drop, the body should be a `DropContent` object. To add multiple drops, the body should be an array of `DropContent` objects.
- **Arguments:**
  - **Path Parameters:**
    - `stream_id`: (string) The ID of the stream to add the drop to.
  - **Request Body:**
    - `drops`: `DropContent` or `List[DropContent]`.
      ```json
      // Single drop
      {
        "title": "What is superposition?",
        "text": "Superposition is a fundamental principle of quantum mechanics.",
        "images": ["https://example.com/superposition.jpg"],
        "type": "text"
      }
      ```
      ```json
      // Multiple drops
      [
        {
          "title": "First Drop",
          "text": "This is the first drop."
        },
        {
          "title": "Second Drop",
          "text": "This is the second drop."
        }
      ]
      ```
    - `creator_id`: (string) The ID of the user creating the drop.
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
- **Description:** Get drops in a stream, with pagination.
- **Arguments:**
  - **Path Parameters:**
    - `stream_id`: (string) The ID of the stream.
  - **Query Parameters:**
    - `from_placement_id`: (string, optional) The placement ID to start retrieving drops from. If not provided, starts from the beginning of the stream.
    - `limit`: (integer, optional, default: 10) The maximum number of drops to return.
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
