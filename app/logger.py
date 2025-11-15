import logging
import io

# --- In-memory logging setup ---
# Create a thread-safe in-memory stream for logs
log_stream = io.StringIO()

# Configure a specific logger for the app to avoid capturing all of
# uvicorn's internal logs.
app_logger = logging.getLogger("api_logger")
app_logger.setLevel(logging.INFO)

# Clear existing handlers to avoid duplicate logs
if app_logger.hasHandlers():
    app_logger.handlers.clear()

# Add our custom stream handler
handler = logging.StreamHandler(log_stream)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
app_logger.addHandler(handler)
# --- End of logging setup ---
