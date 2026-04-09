import os
from sqlalchemy import create_engine, text

def run_ddl():
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
    db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/customer_db')
    engine = create_engine(db_url)
    with engine.connect() as conn:
        conn.execute(text(ddl))
        conn.commit()

if __name__ == "__main__":
    run_ddl()
