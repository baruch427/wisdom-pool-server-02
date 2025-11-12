# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /code

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# We use --no-cache-dir to keep the image size small
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code
COPY ./app /code/app
COPY ./ztest /code/ztest

# Expose port 8000 to the outside world
EXPOSE 8000

# Define environment variable
ENV PORT 8000

# Run app.main:app when the container launches
# Use --host 0.0.0.0 to make it accessible from outside the container
# The PORT environment variable is automatically set by Cloud Run.
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
