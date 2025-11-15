# Testing Guide

This document provides instructions on how to run the different testing environments for the Wisdom Pool Server.

## Prerequisites

**Docker Desktop:** All testing scripts rely on `docker-compose` to build and run the application containers. Please ensure **Docker Desktop is running** before executing any of the scripts.

**Java (for local emulator):** The local database emulator for Firestore requires a Java runtime (version 21 or higher). This is only needed for the `run_server_local_db.ps1` script.

## Running the Server for Manual Testing

The scripts for running the server are located in the `ztest/` directory. You should run them from the root of the project directory.

### 1. With a **Live** Firebase Database

This setup connects the server to the actual Firebase project database. It's useful for testing with real data and for running scripts that interact with the live database.

-   **Script:** `ztest/run_server_live_db.ps1`
-   **Command:**
    ```powershell
    .\ztest\run_server_live_db.ps1
    ```
-   **Server URL:** `http://localhost:8000`
-   **API Docs:** `http://localhost:8000/docs`
-   **Database:** Connects to the live Firebase Firestore.

### 2. With a **Local** Database Emulator

This setup runs a local instance of the Firestore emulator. This is ideal for development and testing without affecting live data.

-   **Script:** `ztest/run_server_local_db.ps1`
-   **Command:**
    ```powershell
    .\ztest\run_server_local_db.ps1
    ```
-   **Server URL:** `http://localhost:8000`
-   **API Docs:** `http://localhost:8000/docs`
-   **Database:** Uses a local Firestore emulator. Data is not persistent between runs.

## Automated Tests

To run the automated test suite:

-   **Script:** `ztest/run_automated_tests.ps1`
-   **Command:**
    ```powershell
    .\ztest\run_automated_tests.ps1
    ```
This will start the necessary containers and execute the tests defined in `ztest/test_api.py`.
