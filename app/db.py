import firebase_admin
from firebase_admin import firestore

# Check if the app is already initialized to prevent errors during --reload
if not firebase_admin._apps:
    # In a Google Cloud environment, the SDK can automatically find the credentials.
    # For local development, it relies on the GOOGLE_APPLICATION_CREDENTIALS env var.
    firebase_admin.initialize_app()

# Get a client to the Firestore service
db = firestore.client()

# Reference to the 'pools' collection
pools_collection = db.collection('pools')
