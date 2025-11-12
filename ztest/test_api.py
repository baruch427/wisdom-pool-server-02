import json

# The client and test_data fixtures are automatically injected by pytest from conftest.py.

# --- Constants ---
API_V1_PREFIX = "/api/v1"

# --- Helper Function ---
def print_response(message, res):
    """Prints a formatted message and the JSON response."""
    print(f"--- {message} ---")
    print(f"Status Code: {res.status_code}")
    try:
        print(json.dumps(res.json(), indent=2))
    except json.JSONDecodeError:
        print(f"Response Body: {res.text}")
    print("-" * (len(message) + 8) + "\n")

# --- Test Functions ---

def test_health_check(client):
    """STEP 1: Checking server health."""
    print("STEP 1: Checking server health...")
    res = client.get("/health")
    assert res.status_code == 200, "Health check failed!"
    print_response("Health Check OK", res)

def test_create_pool(client, test_data):
    """STEP 2: Creating a new Pool."""
    print("STEP 2: Creating a new Pool...")
    pool_payload = {
        "creator_id": "test_user_01",
        "content": {
            "title": "My Test Pool",
            "description": "A pool for testing the API."
        }
    }
    res = client.post(f"{API_V1_PREFIX}/pools", json=pool_payload)
    assert res.status_code == 201, "Failed to create pool!"
    response_json = res.json()
    assert 'pool_id' in response_json
    test_data['pool_id'] = response_json['pool_id']
    print_response(f"Pool created with ID: {test_data['pool_id']}", res)

def test_create_stream(client, test_data):
    """STEP 3: Creating a new Stream in the Pool."""
    print("STEP 3: Creating a new Stream in the Pool...")
    assert 'pool_id' in test_data, "Pool ID not found from previous test."
    
    # Note: The endpoint implementation expects `stream_content` and `creator_id`
    # at the top level, not nested under a single `content` object.
    # We adjust the payload to match the actual code.
    stream_payload = {
        "pool_id": test_data['pool_id'],
        "creator_id": "test_user_01",
        "stream_content": {
            "title": "My Test Stream",
            "description": "A stream for testing drop pagination."
        }
    }
    res = client.post(f"{API_V1_PREFIX}/streams", json=stream_payload)
    assert res.status_code == 201, "Failed to create stream!"
    response_json = res.json()
    assert 'stream_id' in response_json
    test_data['stream_id'] = response_json['stream_id']
    print_response(f"Stream created with ID: {test_data['stream_id']}", res)

def test_add_multiple_drops(client, test_data):
    """STEP 4: Adding 3 drops to the stream."""
    print("STEP 4: Adding 3 drops to the stream...")
    assert 'stream_id' in test_data, "Stream ID not found from previous test."
    test_data['drops'] = []
    for i in range(1, 4):
        # The endpoint expects a request body matching the `AddDropRequest` model
        drop_payload = {
            "creator_id": "test_user_01",
            "content": {
                "title": f"Drop Number {i}",
                "text": f"This is the content for drop #{i} in the sequence."
            }
        }
        res = client.post(f"{API_V1_PREFIX}/streams/{test_data['stream_id']}/drops", json=drop_payload)
        assert res.status_code == 201, f"Failed to add drop #{i}!"
        drop_info = res.json()
        test_data['drops'].append(drop_info)
        print_response(f"Added Drop #{i} with ID: {drop_info['drop_id']}", res)

def test_get_single_drop(client, test_data):
    """STEP 5: Retrieving the second drop directly."""
    print("STEP 5: Retrieving the second drop directly...")
    assert 'drops' in test_data and len(test_data['drops']) > 1, "Drops not found from previous test."
    drop_to_get_id = test_data['drops'][1]['drop_id']
    res = client.get(f"{API_V1_PREFIX}/drops/{drop_to_get_id}")
    assert res.status_code == 200, "Failed to get single drop!"
    assert res.json()['content']['title'] == "Drop Number 2"
    print_response(f"Successfully retrieved Drop ID: {drop_to_get_id}", res)

def test_paginate_drops(client, test_data):
    """STEP 6: Paginating through the stream's drops."""
    print("STEP 6: Paginating through the stream's drops (2 at a time)...")
    assert 'stream_id' in test_data, "Stream ID not found from previous test."
    
    # First page (limit=2)
    res_page1 = client.get(f"{API_V1_PREFIX}/streams/{test_data['stream_id']}/drops?limit=2")
    assert res_page1.status_code == 200
    page1_data = res_page1.json()
    assert len(page1_data['drops']) == 2
    assert page1_data['has_more'] is True, "has_more should be true after first page!"
    assert page1_data['total_count'] == 3
    assert page1_data['drops'][0]['content']['title'] == "Drop Number 1"
    assert page1_data['drops'][1]['content']['title'] == "Drop Number 2"
    print_response("Retrieved Page 1 (first 2 drops)", res_page1)

    # Get the placement ID of the last drop from page 1 to use for pagination
    last_placement_id_page1 = page1_data['drops'][-1]['placement_id']
    
    # Second page (from the last drop of page 1)
    res_page2 = client.get(f"{API_V1_PREFIX}/streams/{test_data['stream_id']}/drops?limit=2&from_placement_id={last_placement_id_page1}")
    assert res_page2.status_code == 200
    page2_data = res_page2.json()
    assert len(page2_data['drops']) == 1, "Page 2 should only have one drop!"
    assert page2_data['has_more'] is False, "has_more should be false on the last page!"
    assert page2_data['total_count'] == 3
    assert page2_data['drops'][0]['content']['title'] == "Drop Number 3"
    print_response("Retrieved Page 2 (last drop)", res_page2)
    print("\n✅ All API tests passed successfully! ✅")
