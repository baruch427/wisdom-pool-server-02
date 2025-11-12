# Wisdom Pool API - Test Script Onboarding Guide

**Version:** 1.0  
**Date:** November 11, 2025

## 1. 🎯 Purpose of this Document

This document explains the purpose and logic behind the `test_api.py` script. It is intended for a new AI assistant or developer to quickly understand the testing strategy for the Wisdom Pool server without having to reverse-engineer the code.

The test script (`test_api.py`) is an **end-to-end integration test** designed to validate the core "happy path" functionality of the API. It simulates a typical client interaction from initial creation to final data retrieval.

## 2. 🧠 The Thinking Behind the Test Flow

The test steps are ordered logically to mimic a real-world usage pattern. Each step builds upon the previous one, using the data created earlier in the sequence. This ensures that the entire lifecycle of creating and consuming content is tested.

### The Test Sequence Rationale:

1.  **Health Check (`/health`)**
    *   **Why:** This is the most basic and essential first step. It answers the question: "Is the server running and responsive?" If this fails, there is no point in running any other tests.
    *   **What it Validates:** That the FastAPI application is up and can handle a simple GET request.

2.  **Create a Pool (`POST /pools`)**
    *   **Why:** Pools are the top-level containers in the data hierarchy. Before any content (streams or drops) can be created, a pool must exist.
    *   **What it Validates:** The `create_pool` endpoint, including JSON body parsing, interaction with the `pools_collection` in Firestore, and the successful return of a `201 Created` status with the new pool's data.

3.  **Create a Stream (`POST /streams`)**
    *   **Why:** Streams are the primary narrative structures that live inside a pool. This step tests the creation of a child resource linked to its parent pool.
    *   **What it Validates:** The `create_stream` endpoint, its ability to link to a `pool_id`, and the correct initialization of a stream with `null` values for `first_drop_placement_id` and `last_drop_placement_id`.

4.  **Add Multiple Drops (`POST /streams/{stream_id}/drops`)**
    *   **Why:** This is the most critical and complex part of the test. Adding drops to a stream involves a **transactional database operation** that modifies three different entities: the new `Drop`, the new `StreamDropPlacement`, and potentially the previous placement and the parent `Stream`.
    *   **What it Validates:**
        *   The transactional logic for adding a drop.
        *   The correct creation of `Drop` and `StreamDropPlacement` documents.
        *   The linked-list logic: ensuring the `prev_placement_id` of the new drop is set correctly and that the `Stream`'s `last_drop_placement_id` is updated.
        *   Running this in a loop (3 times) ensures the chain is built correctly beyond the first drop.

5.  **Retrieve a Single Drop (`GET /drops/{drop_id}`)**
    *   **Why:** This ensures that drops are globally accessible resources that can be retrieved directly by their unique ID, independent of any stream. This is important for features like sharing a direct link to a drop.
    *   **What it Validates:** The `get_drop` endpoint and direct document retrieval from the `drops_collection`.

6.  **Paginate Through the Stream's Drops (`GET /streams/{stream_id}/drops`)**
    *   **Why:** This final, crucial step validates that the linked list created in Step 4 can be correctly traversed. It confirms that the data is not just stored correctly but can be retrieved in the intended order.
    *   **What it Validates:**
        *   The `get_drops_in_stream` endpoint.
        *   The `limit` query parameter correctly restricts the number of results.
        *   The `from_placement_id` query parameter works for pagination, allowing a client to fetch the "next page" of drops.
        *   The `has_more` boolean in the response is accurately calculated, returning `true` when more drops are available and `false` on the final page.

## 3. 🚀 How to Run the Tests

This section outlines the process for running the automated test suite.

### Recommended Method: Use the Automation Script

The simplest and most reliable way to run the entire test suite is to use the provided PowerShell script. This script handles starting the environment, running the tests, and cleaning up afterward.

**From the project root, simply run:**
```powershell
./run_tests.ps1
```

The script will print its progress and exit with a success or failure code, making it ideal for both local development and CI/CD pipelines.

### Manual Method: Step-by-Step Guide

For developers who want to run the steps manually or debug the process, follow the guide below.

### Step 1: Start the Test Environment

The entire test environment is managed by Docker Compose. To build and start the services, run the following command from the project's root directory:

```bash
docker-compose -f docker-compose.test.yml up --build -d
```

*   `--build`: This flag tells Docker Compose to rebuild the application image if the source code (e.g., any Python files) has changed.
*   `-d` (detached mode): This runs the containers in the background, so your terminal is free for the next command.

This command will:
1.  Build a Docker image for the FastAPI application based on the `Dockerfile`.
2.  Pull the official Google Cloud SDK image to use for the Firestore emulator.
3.  Start both containers, linking them on a dedicated Docker network. The app will be accessible on `http://localhost:8000` and the emulator will be configured automatically.

### Step 2: Run the Tests

Once the containers are running, execute the test suite **inside the `app` container**. This ensures the tests run in the exact same environment as the application, without depending on your local machine's Python setup.

```bash
# Execute pytest inside the 'app' container
docker-compose -f docker-compose.test.yml exec app pytest -v ztest/
```

*   `docker-compose exec app`: This command tells Docker to run the following command (`pytest -v ztest/`) inside the container named `app`.
*   `pytest -v ztest/`: This runs the test suite located in the `ztest` directory with verbose output.

`pytest` will make live HTTP requests to the `app` service, which in turn communicates with the `firestore-emulator` container.

### Step 3: View Test Coverage (Optional)

To generate a report on which lines of application code were executed by the tests, run `pytest` with the `--cov` flag inside the container:

```bash
docker-compose -f docker-compose.test.yml exec app pytest --cov=app ztest/
```

This will provide a terminal report showing the percentage of code in the `app` directory that is covered by the test suite.

### Step 4: Shut Down the Test Environment

After you are finished testing, it is important to stop and remove the containers to free up system resources.

```bash
docker-compose -f docker-compose.test.yml down
```

This command stops and removes the containers, networks, and volumes created by `up`. The in-memory data in the Firestore emulator is completely wiped, ensuring a clean slate for the next test run.

---

## 4. 🏗️ Anatomy of the Test Environment

For a professional and scalable testing strategy, the manual test script has been evolved into an automated test suite running in an isolated, reproducible environment. This is built on four key principles.

### Principle 1: Isolation with the Firestore Emulator

Instead of testing against a live database, use the **Google Cloud Firestore Emulator**.

*   **Benefits:**
    *   **Zero Cost & No Quotas:** All operations are local and free.
    *   **Speed:** In-memory operations are significantly faster than network requests to the real Firestore.
    *   **Complete Isolation:** Each test run starts with a clean, empty database, preventing data contamination between tests.
    *   **Offline Development:** Enables running the full test suite without an internet connection.

### Principle 2: Reproducibility with Docker

Use Docker and Docker Compose to define the entire test environment in code. This guarantees that every developer and the CI/CD pipeline use the exact same setup.

**Example `docker-compose.test.yml`:**
```yaml
version: '3.8'
services:
  # Your FastAPI Application
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      # Tell the app to use the emulator
      - FIRESTORE_EMULATOR_HOST=firestore-emulator:8080
      - GOOGLE_CLOUD_PROJECT=local-dev # Project ID for the emulator
    depends_on:
      - firestore-emulator

  # Google Cloud Firestore Emulator
  firestore-emulator:
    image: gcr.io/google.com/cloudsdktool/cloud-sdk:latest
    command: >
      gcloud beta emulators firestore start --host-port=0.0.0.0:8080
    ports:
      - "8081:8080" # Port 8081 on host maps to 8080 in container
```

### Principle 3: Automation with a Test Runner (pytest)

Adopt a formal test framework like `pytest` to structure and run tests.

*   **Benefits:**
    *   **Fixtures:** Automatically manage setup and teardown, such as clearing the emulator database before each test run.
    *   **Test Discovery:** Automatically finds and runs test files and functions.
    *   **Rich Assertions:** Provides detailed and readable output when a test fails.
    *   **Extensible:** A vast plugin ecosystem for features like code coverage (`pytest-cov`).

### Principle 4: Configuration via Environment Variables

Modify the application to dynamically switch between the real Firestore and the emulator based on an environment variable. This avoids hardcoding and allows the same application code to run in development, testing, and production.

**Example `app/db.py` modification:**
```python
import firebase_admin
from firebase_admin import credentials, firestore
import os

# Check if running in an emulated environment
if os.getenv('FIRESTORE_EMULATOR_HOST'):
    # Use a dummy credential for the emulator
    cred = credentials.Anonymous()
    firebase_admin.initialize_app(options={'projectId': os.getenv('GOOGLE_CLOUD_PROJECT', 'local-dev')})
# Check if the app is already initialized to prevent errors during --reload
elif not firebase_admin._apps:
    # In a Google Cloud environment, the SDK can automatically find the credentials.
    firebase_admin.initialize_app()

# Get a client to the Firestore service
db = firestore.client()

# ... rest of the file
```

### The Ideal Workflow: A Summary

1.  **Start Docker Desktop.**
2.  Run `./run_automated_tests.ps1` and observe the output.

Alternatively, for manual control:
1.  Run `docker-compose -f docker-compose.test.yml up --build -d` to start the environment.
2.  Run `docker-compose -f docker-compose.test.yml exec app pytest -v ztest/` to execute the tests.
3.  Review the output for any failures.
4.  When finished, run `docker-compose -f docker-compose.test.yml down` to clean up.
