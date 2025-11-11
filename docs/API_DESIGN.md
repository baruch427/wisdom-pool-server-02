# 📋 Wisdom Pool Server - API Design Document

> **Version:** 2.0  
> **Date:** November 5, 2025  
> **Status:** Design Phase - Ready for Implementation

## 🎯 System Overview

### **Architecture Characteristics**
- **Read-heavy workload**: Stream reading >> stream writing
- **Sequential access**: Users scroll through drops in order
- **Eventual consistency**: New drops don't need immediate visibility
- **Linked list structure**: Drops connected via next/prev pointers

### **Data Hierarchy**
```
Pool (1) → Has Many → Streams (N)
Stream (1) → Has Many → Drops (N) [in linked order]
Drop (1) → Can be in → Multiple Streams (N)
```

### **Technology Stack**
- **Backend**: FastAPI + Python
- **Database**: Google Cloud Firestore
- **Deployment**: Google Cloud Run and GitHub Actions
- **Authentication**: TBD (Clerk/Auth0)

---

## 📊 Core Data Models

### **Pool**
```json
{
  "pool_id": "string",
  "creator_id": "string",
  "created_at": "timestamp",
  "content": {
    "title": "string",
    "description": "string (supports basic HTML + drop links)"
  }
}
```

### **Stream**
```json
{
  "stream_id": "string",
  "pool_id": "string",
  "creator_id": "string",
  "created_at": "timestamp",
  "first_drop_id": "string|null",
  "last_drop_id": "string|null",
  "stats": {
    "views": "number",
    "shares": "number"
  },
  "content": {
    "title": "string",
    "description": "string (supports basic HTML + drop links)",
    "ai_framing": "string",
    "category": "string",
    "image": "string"
  }
}
```

### **Drop**
```json
{
  "drop_id": "string",
  "creator_id": "string",
  "created_at": "timestamp",
  "content": {
    "title": "string",
    "text": "string",
    "images": ["url1", "url2"],
    "type": "text|image|mixed"
  }
}
```

### **Stream-Drop Association (Linked List)**
```json
{
  "placement_id": "string",
  "stream_id": "string",
  "drop_id": "string",
  "next_placement_id": "string|null",
  "prev_placement_id": "string|null",
  "added_at": "timestamp"
}
```



## 🚀 Complete API Specification

### **Read APIs (Frontend)**

#### **1. Get Stream Metadata**
```http
GET /api/v1/streams/{stream_id}
```
**Response:**
```json
{
  "stream_id": "string",
  "pool_id": "string",
  "creator_id": "string",
  "created_at": "2025-11-05T10:00:00Z",
  "first_drop_id": "string|null",
  "last_drop_id": "string|null",
  "stats": {
    "views": 0,
    "shares": 0
  },
  "content": {
    "title": "string",
    "description": "string",
    "ai_framing": "string",
    "category": "string",
    "image": "string"
  }
}
```

#### **2. Get Drops in Stream (Pagination)**
```http
GET /api/v1/streams/{stream_id}/drops?from_placement_id={id}&limit={num}
```
**Query Parameters:**
- `from_placement_id`: optional (if null, start from first drop)
- `limit`: number of drops to return (default: 10, max: 50)

**Response:**
```json
{
  "drops": [
    {
      "placement_id": "string",
      "drop_id": "string",
      "creator_id": "string",
      "created_at": "2025-11-05T10:00:00Z",
      "next_placement_id": "string|null",
      "prev_placement_id": "string|null",
      "content": {
        "title": "string",
        "text": "string",
        "images": ["url1", "url2"],
        "type": "text"
      }
    }
  ],
  "has_more": true,
  "total_count": 25
}
```

#### **3. Get Single Drop**
```http
GET /api/v1/drops/{drop_id}
```
**Response:**
```json
{
  "drop_id": "string",
  "creator_id": "string",
  "created_at": "2025-11-05T10:00:00Z",
  "content": {
    "title": "string",
    "text": "string",
    "images": ["url1", "url2"],
    "type": "text"
  }
}
```

#### **4. Search Streams (Future Phase)**
```http
GET /api/v1/streams/search?q={query}&limit={num}
```
**Query Parameters:**
- `q`: search query (searches stream descriptions)
- `limit`: number of results (default: 20, max: 100)

**Response:**
```json
{
  "streams": [
    {
      "stream_id": "string",
      "stats": {
        "views": 150,
        "shares": 12
      },
      "content": {
        "title": "string",
        "description": "string",
        "category": "string",
        "image": "string"
      }
    }
  ],
  "total_count": 5,
  "has_more": false
}
```

---

### **Write APIs (Wisdom Engine & Other Servers)**

#### **5. Create Pool**
```http
POST /api/v1/pools
Content-Type: application/json
```
**Request Body:**
```json
{
  "creator_id": "string",
  "content": {
    "title": "string",
    "description": "string"
  }
}
```
**Response:**
```json
{
  "pool_id": "generated_id",
  "creator_id": "string",
  "created_at": "2025-11-05T10:00:00Z",
  "content": {
    "title": "string",
    "description": "string"
  }
}
```

#### **6. Create Stream**
```http
POST /api/v1/streams
Content-Type: application/json
```
**Request Body:**
```json
{
  "pool_id": "string",
  "creator_id": "string",
  "content": {
    "title": "string",
    "description": "string",
    "ai_framing": "string",
    "category": "string",
    "image": "string"
  }
}
```
**Response:**
```json
{
  "stream_id": "generated_id",
  "pool_id": "string",
  "creator_id": "string",
  "created_at": "2025-11-05T10:00:00Z",
  "first_drop_id": null,
  "last_drop_id": null,
  "stats": {
    "views": 0,
    "shares": 0
  },
  "content": {
    "title": "string",
    "description": "string",
    "ai_framing": "string",
    "category": "string",
    "image": "string"
  }
}
```

#### **7. Add Drop to Stream (Create & Place)**
```http
POST /api/v1/streams/{stream_id}/drops
Content-Type: application/json
```
**Request Body (Insert at end):**
```json
{
  "creator_id": "string",
  "content": {
    "title": "string", 
    "text": "string",
    "images": ["url1", "url2"],
    "type": "text|image|mixed"
  }
}
```
**Request Body (Insert at specific position):**
```json
{
  "creator_id": "string",
  "content": {
    "title": "string",
    "text": "string", 
    "images": ["url1", "url2"],
    "type": "text|image|mixed"
  },
  "position": {
    "after": "existing_placement_id"
  }
}
```
**Response:**
```json
{
  "success": true,
  "placement_id": "string",
  "drop_id": "generated_id", 
  "stream_id": "string",
  "creator_id": "string",
  "created_at": "2025-11-05T10:00:00Z",
  "content": {
    "title": "string",
    "text": "string",
    "images": ["url1", "url2"],
    "type": "text"
  },
  "position_info": {
    "next_placement_id": "string|null",
    "prev_placement_id": "string|null"
  }
}
```

#### **8. Add Existing Drop to Stream**
```http
POST /api/v1/streams/{stream_id}/drops/existing
Content-Type: application/json
```
**Request Body:**
```json
{
  "drop_id": "string",
  "position": "end"
}
```
**Request Body (Insert at start):**
```json
{
  "drop_id": "string", 
  "position": "start"
}
```
**Request Body (Insert after specific placement):**
```json
{
  "drop_id": "string",
  "position": {
    "after": "existing_placement_id"
  }
}
```
**Response:**
```json
{
  "success": true,
  "placement_id": "string",
  "stream_id": "string",
  "drop_id": "string",
  "position_info": {
    "next_placement_id": "string|null",
    "prev_placement_id": "string|null"
  }
}
```

---

## 👥 Usage Patterns

### **Frontend Usage**

#### **Application Startup Flow**
1. FE has collection of `(stream_id, current_drop_id)` from user state engine
2. For each active stream:
   - `GET /streams/{stream_id}` → get stream metadata/header
   - `GET /streams/{stream_id}/drops?from_placement_id={current}&limit=10` → get drops from user's position

#### **User Scrolling Flow**
1. User scrolls through stream
2. When approaching end of loaded content:
   - `GET /streams/{stream_id}/drops?from_placement_id={last_seen}&limit=10`
3. Continue pagination using `next_placement_id` from the last drop in previous response

#### **Drop Sharing Flow**
1. User receives shared drop with `stream_id`
2. `GET /streams/{stream_id}` → get stream context
3. `GET /streams/{stream_id}/drops?from_drop_id={shared_drop}&limit=10` → show content around shared drop

---

### **Wisdom Engine Usage**

#### **Content Creation Flow**
1. `POST /pools` → Create thematic pool
2. `POST /streams` → Create curated stream within pool  
3. `POST /streams/{stream_id}/drops` → Create and place drops directly in stream

#### **Content Curation Flow**
1. `POST /streams/{stream_id}/drops` → Create new drop content and place in stream
2. `POST /streams/{stream_id}/drops/existing` with `position: {"after": "placement_123"}` → Reuse existing drop at specific position
3. Repeat to build narrative flow

#### **Content Updates (Rare)**
1. `PUT /streams/{stream_id}` → Update stream metadata
2. `POST /streams/{stream_id}/drops` → Insert new drops into existing streams

---

## 🗄️ Database Schema (Firestore)

### **Collections Structure**
```
/pools/{pool_id}                    // Pool documents
/streams/{stream_id}                // Stream documents  
/drops/{drop_id}                    // Drop documents (global)
/stream_drops/{stream_id}_{drop_id} // Linked list associations
```

### **Indexing Strategy**
- **Streams by pool**: `pool_id` index
- **Stream drops by stream**: `stream_id` index
- **Search**: Text index on stream `description` field
- **Trending**: Compound index on `stats.views` + `created_at`

### **Query Patterns**
```javascript
// Get stream metadata
db.collection('streams').doc(stream_id).get()

// Get next drops in stream
db.collection('stream_drops')
  .where('stream_id', '==', stream_id)
  .where('prev_placement_id', '==', from_placement_id)
  .limit(limit)
  .get()

// Search streams
db.collection('streams')
  .where('description', 'array-contains-any', search_terms)
  .limit(20)
  .get()
```

*Design finalized: November 5, 2025*