# Avito Merch Shop Project

This README explains how to run and test the project (including load testing).

## 1. Prerequisites

- Docker and Docker Compose installed on your machine.
- Locust (if you want to run load tests) installed locally, or any other machine to run tests from.

## 2. Building and Running with Docker

1. Clone this repository (or place the files in a single folder):
   ```
   git clone https://example.com/your-project.git
   cd your-project
   ```
2. Build and run the containers:
   ```
   docker-compose up --build -d
   ```
3. The application will be accessible at:
   http://localhost:8000

## 3. Load Testing

1. Make sure your services are running (see above).
2. Install Locust globally or in a virtualenv:
   ```
   pip install locust
   ```
3. Run Locust:
   ```
   locust -f locustfile.py --host http://localhost:8000
   ```
4. Open the Locust web UI at:
   http://localhost:8089
5. Set the number of users (e.g., 50) and spawn rate (e.g., 5), then start swarming.  
   • You’ll see requests per second, response times, and error rates in real time.

## 4. Project Structure

- **Dockerfile**: Describes how to build the app container.  
- **docker-compose.yml**: Orchestrates the database and application services.  
- **locustfile.py**: Contains your load testing tasks for Locust.  
- **app/**: Contains the FastAPI code (main, models, database setup, etc.).  
- **tests/**: Contains unit, integration, and E2E test files.

## 5. Customization

- Modify environment variables (DATABASE_URL, SECRET_KEY) in "docker-compose.yml" as needed.  
- Adjust the "locustfile.py" to change load test scenarios (merch items, coin sending, concurrency, etc.).  
- Update Dockerfile to ensure the correct Python dependencies are installed.

## 6. Stopping the Services

When you’re done, stop the containers:
```
docker-compose down
```