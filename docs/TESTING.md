# Testing Guide

This document provides instructions on how to run the different testing environments for the Wisdom Pool Server.

## Prerequisites

**Docker Desktop:** All testing scripts rely on `docker-compose` to build and run the application containers. Please ensure **Docker Desktop is running** before executing any of the scripts.




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


---

## Convenience Script for Live DB

If you are frequently running the live database server, you can use the following PowerShell commands to quickly navigate and start it. You can save this as a `.ps1` file (e.g., `start_live_server.ps1`) in the root directory for easy access.

```powershell
C:\Users\Home\Dropbox\___WisdomPools\wisdom-pool-server-02
ztest/run_server_live_db.ps1
```
