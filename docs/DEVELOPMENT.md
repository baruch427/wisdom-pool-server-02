# Wisdom Pool Server - Development Guide

This document explains how to run the server on your local machine for development and manual testing. This setup is separate from the automated test environment and will not interfere with it.

## 1. 🎯 Purpose

This workflow is for:
-   Manually testing the API endpoints using the interactive Swagger UI.
-   Developing new features.
-   Debugging the application in a live environment.

The server uses a local **Firestore Emulator**, so your work will not affect any live production data. The database is reset every time you restart the development environment.

## 2. 🚀 How to Run the Development Server

### Prerequisites
-   Docker Desktop must be running.

### Steps

1.  **Open a PowerShell terminal** in the root directory of the project.

2.  **Run the development script:**
    ```powershell
    ./run_manual_tests.ps1
    ```

3.  **Wait for the services to start.** You will see logs from the application and the database in your terminal. Once you see a message like `Uvicorn running on http://0.0.0.0:8000`, the server is ready.

4.  **Access the API:**
    -   **Interactive Docs (Swagger UI):** Open your web browser and go to **[http://localhost:8000/docs](http://localhost:8000/docs)**. This is the recommended way to perform manual testing.
    -   **Server Health:** You can check if the server is running by visiting **[http://localhost:8000/health](http://localhost:8000/health)**.

### Hot Reloading

The development server is configured with **hot reloading**. This means any changes you save in the `.py` files inside the `app/` directory will automatically cause the server to restart with your changes applied.

## 3. 🛑 How to Stop the Server

-   Go to the terminal where the server is running and press **`CTRL+C`**.
-   Docker Compose will shut down the application and the database container. All data in the emulator will be cleared.
