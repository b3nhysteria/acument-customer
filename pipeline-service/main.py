def get_db():

import os
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from models.customer import Customer
from database import SessionLocal
from services.ingestion import ingest_from_flask
import logging
from dotenv import load_dotenv

# --- Configuration Management ---
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/customer_db')
MAX_LIMIT = int(os.getenv('MAX_LIMIT', 50))

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database connection and DDL check at startup ---
def check_db_and_run_ddl():
    from sqlalchemy import create_engine, text
    engine = create_engine(DATABASE_URL)
    ddl = '''
    CREATE TABLE IF NOT EXISTS customers (
      customer_id VARCHAR(50) PRIMARY KEY,
      first_name VARCHAR(100) NOT NULL,
      last_name VARCHAR(100) NOT NULL,
      email VARCHAR(255) NOT NULL,
      phone VARCHAR(20),
      address TEXT,
      date_of_birth DATE,
      account_balance DECIMAL(15,2),
      created_at TIMESTAMP
    );
    '''
    try:
        with engine.connect() as conn:
            conn.execute(text(ddl))
            conn.commit()
        logging.info("Database connected and DDL executed.")
    except Exception as e:
        logging.error(f"Database connection or DDL failed: {e}")
        raise

@app.on_event("startup")
def startup_event():
    check_db_and_run_ddl()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/ingest")
def ingest():
    try:
        count = ingest_from_flask()
        return {"status": "success", "records_processed": count}
    except Exception as e:
        logging.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail="Ingestion failed")

# --- Filtering & Sorting ---
def filter_and_sort(query, last_name=None, sort_by=None, sort_order='asc'):
    if last_name:
        query = query.filter(Customer.last_name.ilike(last_name))
    if sort_by and hasattr(Customer, sort_by):
        col = getattr(Customer, sort_by)
        if sort_order == 'desc':
            col = col.desc()
        query = query.order_by(col)
    return query

@app.get("/api/customers")
def get_customers(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    last_name: str = Query(None),
    sort_by: str = Query(None),
    sort_order: str = Query('asc'),
    db: Session = Depends(get_db)
):
    if limit > MAX_LIMIT:
        raise HTTPException(status_code=400, detail=f"limit must be <= {MAX_LIMIT}")
    query = db.query(Customer)
    query = filter_and_sort(query, last_name, sort_by, sort_order)
    total = query.count()
    customers = query.offset((page-1)*limit).limit(limit).all()
    return {"data": [c.__dict__ for c in customers], "total": total, "page": page, "limit": limit}

@app.get("/api/customers/{customer_id}")
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer.__dict__
