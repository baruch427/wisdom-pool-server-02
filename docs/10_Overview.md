# Wisdom Pool – Requirements Specification

## Overview
The Wisdom Pool application is a cloud-based platform designed to present curated knowledge streams, each containing a sequence of individual content posts called "Drops". Users explore topics through a scrollable interface one drop at a time

Each Drop is globally unique, reusable across multiple Streams, and linked via placement metadata that defines navigation order. This ensures consistent identity, efficient reuse, and predictable synchronization between AI-generated and human-curated content.

## Key Concepts

### Pool
* A "Pool" is a collection of Streams grouped by theme or context.

### Stream
* Streams are rich content containers that define a curated narrative or topic.
* Each stream document includes identity, presentation, and system fields — not only metadata. They hold the information required for display, provenance, and UI rendering, while the ordering of Drops remains external in placement docs.
* Streams track both their "content boundaries" (`first_drop_id`, `last_drop_id`) and `drop_count` for efficient front-end pagination and navigation.
* They never embed Drops directly.
* Each Drop’s order and linkage are defined through per-stream placement documents located at `/streams/{stream_id}/drops/{drop_id}`.

### Drop
* A "Drop" is the fundamental, reusable unit of content in the Wisdom Pool ecosystem.
* Each Drop exists once globally under `/drops/{drop_id}` where `doc_id == drop_id`.
* A Drop may appear in multiple Streams or user-created collections without duplication.

## Pool Server
* **Technology:** FastAPI, Uvicorn, Python, Docker, Google Cloud Run.
* **Responsibilities:**
    * Serve content by joining placements + global Drops.
    * Manage user