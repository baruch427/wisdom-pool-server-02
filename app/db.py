import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path

# Build an absolute path to the credentials file
# This makes the connection robust, regardless of where the script is run from
credentials_path = Path(__file__).parent.parent / "firebase-credentials.json"

# Check if the app is already initialized to prevent errors during --reload
if not firebase_admin._apps:
    # Use the credential file to initialize the SDK
    cred = credentials.Certificate(credentials_path)
    firebase_admin.initialize_app(cred)

# Get a client to the Firestore service
db = firestore.client()

# Reference to the 'pools' collection
pools_collection = db.collection('pools')
