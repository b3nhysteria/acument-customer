import requests
from sqlalchemy.orm import Session
from models.customer import Customer
from database import SessionLocal
from sqlalchemy.dialects.postgresql import insert
import os

def fetch_all_customers(flask_url):
    customers = []
    page = 1
    limit = 10
    while True:
        resp = requests.get(f"{flask_url}/api/customers", params={"page": page, "limit": limit})
        data = resp.json()
        customers.extend(data["data"])
        if len(data["data"]) < limit:
            break
        page += 1
    return customers

def upsert_customers(customers):
    session = SessionLocal()
    count = 0
    for c in customers:
        stmt = insert(Customer).values(**c).on_conflict_do_update(
            index_elements=['customer_id'],
            set_={k: c[k] for k in c if k != 'customer_id'}
        )
        session.execute(stmt)
        count += 1
    session.commit()
    session.close()
    return count

def ingest_from_flask():
    flask_url = os.getenv('MOCK_SERVER_URL', 'http://mock-server:5000')
    customers = fetch_all_customers(flask_url)
    count = upsert_customers(customers)
    return count
