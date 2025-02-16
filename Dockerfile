# Use a Python base image (e.g., python:3.9-slim)
FROM python:3.9-slim

# Set working directory
# Copy requirements.txt into the container
WORKDIR /app
# Install dependencies (make sure uvicorn is included in requirements.txt)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# Copy the rest of the app files
COPY . .

# Expose port 8000 for the application
EXPOSE 8000

# Run the FastAPI application with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]