"""
Example script showing how to interact with the real Firebase database.
You can run this while the dev server is running to inspect or manipulate data.

To run: python scripts/example_script.py
"""

import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase (only if not already initialized)
if not firebase_admin._apps:
    cred = credentials.Certificate('firebase-credentials.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()


def list_all_pools():
    """List all pools in the database."""
    pools_ref = db.collection('pools')
    pools = pools_ref.stream()
    
    print("\n=== All Pools ===")
    for pool in pools:
        pool_data = pool.to_dict()
        print(f"\nPool ID: {pool.id}")
        print(f"  Title: {pool_data.get('content', {}).get('title')}")
        print(f"  Creator: {pool_data.get('creator_id')}")
        print(f"  Created: {pool_data.get('created_at')}")


def list_all_streams():
    """List all streams in the database."""
    streams_ref = db.collection('streams')
    streams = streams_ref.stream()
    
    print("\n=== All Streams ===")
    for stream in streams:
        stream_data = stream.to_dict()
        print(f"\nStream ID: {stream.id}")
        print(f"  Title: {stream_data.get('content', {}).get('title')}")
        print(f"  Pool ID: {stream_data.get('pool_id')}")
        print(f"  First Drop: {stream_data.get('first_drop_placement_id')}")
        print(f"  Last Drop: {stream_data.get('last_drop_placement_id')}")


def list_all_drops():
    """List all drops in the database."""
    drops_ref = db.collection('drops')
    drops = drops_ref.stream()
    
    print("\n=== All Drops ===")
    for drop in drops:
        drop_data = drop.to_dict()
        print(f"\nDrop ID: {drop.id}")
        print(f"  Title: {drop_data.get('content', {}).get('title')}")
        print(f"  Creator: {drop_data.get('creator_id')}")


def count_documents():
    """Count documents in each collection."""
    print("\n=== Document Counts ===")
    
    pools_count = len(list(db.collection('pools').stream()))
    streams_count = len(list(db.collection('streams').stream()))
    drops_count = len(list(db.collection('drops').stream()))
    placements_count = len(
        list(db.collection('stream_drop_placements').stream())
    )
    
    print(f"Pools: {pools_count}")
    print(f"Streams: {streams_count}")
    print(f"Drops: {drops_count}")
    print(f"Placements: {placements_count}")


if __name__ == "__main__":
    print("=" * 50)
    print("Wisdom Pool Database Inspector")
    print("=" * 50)
    
    # Run all inspection functions
    count_documents()
    list_all_pools()
    list_all_streams()
    list_all_drops()
    
    print("\n" + "=" * 50)
    print("Inspection complete!")
    print("=" * 50)
