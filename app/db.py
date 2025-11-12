import firebase_admin
from firebase_admin import credentials, firestore
import os

# Initialize Firebase Admin SDK
# This needs to be done only once. The `if not firebase_admin._apps:` check
# prevents re-initialization errors when using --reload with uvicorn.
if not firebase_admin._apps:
    # Check if running with Firestore emulator (for testing)
    if os.getenv('FIRESTORE_EMULATOR_HOST'):
        # For emulator, create a mock credential
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'local-dev')
        # Mock certificate dict (not validated by emulator)
        mock_key = (
            '-----BEGIN PRIVATE KEY-----\nMOCK\n-----END PRIVATE KEY-----\n'
        )
        mock_cred = credentials.Certificate({
            'type': 'service_account',
            'project_id': project_id,
            'private_key_id': 'mock',
            'private_key': mock_key,
            'client_email': f'mock@{project_id}.iam.gserviceaccount.com',
            'client_id': '1',
            'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
            'token_uri': 'https://oauth2.googleapis.com/token',
        })
        firebase_admin.initialize_app(
            mock_cred,
            options={'projectId': project_id}
        )
    # Check if credentials file is provided (production/development)
    elif os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    else:
        # Fallback to default credentials
        firebase_admin.initialize_app()

# Get a client to the Firestore service
db = firestore.client()

# Reference to the 'pools' collection
pools_collection = db.collection('pools')

# Reference to the 'streams' collection
streams_collection = db.collection('streams')

# Reference to the 'drops' collection
drops_collection = db.collection('drops')

# Reference to the 'stream_drops' collection
stream_drops_collection = db.collection('stream_drops')
