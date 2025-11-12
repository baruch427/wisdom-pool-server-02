# Custom Scripts Directory

This directory contains utility scripts for interacting with the Firebase database.

## Setup

Install dependencies if running scripts outside Docker:
```powershell
pip install -r requirements.txt
```

## Available Scripts

### `example_script.py`
Inspects the current state of the database, showing counts and details of all:
- Pools
- Streams  
- Drops
- Stream-Drop Placements

**Usage:**
```powershell
python scripts/example_script.py
```

## Creating Your Own Scripts

Use `example_script.py` as a template. Key points:

1. **Import Firebase:**
   ```python
   import firebase_admin
   from firebase_admin import credentials, firestore
   ```

2. **Initialize (only once):**
   ```python
   if not firebase_admin._apps:
       cred = credentials.Certificate('firebase-credentials.json')
       firebase_admin.initialize_app(cred)
   db = firestore.client()
   ```

3. **Access collections:**
   ```python
   pools = db.collection('pools').stream()
   ```

## Running Scripts While Server is Active

You can run these scripts while `run_dev_server.ps1` is running. Both the server and your scripts will access the same real Firebase database, allowing you to:
- Test API endpoints
- Run custom data operations
- Inspect database state
- Perform maintenance tasks

All changes will be visible in the Firebase Console.
