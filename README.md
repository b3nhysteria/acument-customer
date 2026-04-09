# Customer Data Pipeline

## Overview
This project demonstrates a data pipeline using Flask (mock server), FastAPI (ingestion and API), and PostgreSQL. Data flows from Flask (JSON) → FastAPI (Ingest) → PostgreSQL → API Response.

## Project Structure
```
project-root/
├── docker-compose.yml
├── README.md
├── mock-server/
│   ├── app.py
│   ├── data/customers.json
│   ├── Dockerfile
│   └── requirements.txt
└── pipeline-service/
    ├── main.py
    ├── models/customer.py
    ├── services/ingestion.py
    ├── database.py
    ├── Dockerfile
    └── requirements.txt
```

## Running the Project
1. **Start all services:**
   ```sh
   docker-compose up -d
   ```
2. **Test Flask API:**
   ```sh
   curl http://localhost:5000/api/customers?page=1&limit=5
   ```
3. **Ingest data:**
   ```sh
   curl -X POST http://localhost:8000/api/ingest
   ```
4. **Get customers from FastAPI:**
   ```sh
   curl http://localhost:8000/api/customers?page=1&limit=5
   ```

## Endpoints
### Flask Mock Server
- `GET /api/customers?page=1&limit=10` — Paginated customers
- `GET /api/customers/{id}` — Single customer
- `GET /api/health` — Health check

### FastAPI Pipeline Service
- `POST /api/ingest` — Ingest data from Flask to PostgreSQL
- `GET /api/customers?page=1&limit=10` — Paginated customers from DB
- `GET /api/customers/{id}` — Single customer from DB

## Notes
- All services are containerized and orchestrated with Docker Compose.
- The ingestion pipeline handles pagination and upserts data into PostgreSQL.
- Modify `data/customers.json` to change mock data.
# acument-customer
