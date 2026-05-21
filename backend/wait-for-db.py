import time
import psycopg2
import os
import sys

def wait_for_db():
    database_url = os.getenv("DATABASE_URL")
    
    max_attempts = 30
    attempt = 0
    
    print(f"Waiting for database database_url...")
    
    while attempt < max_attempts:
        try:
            conn = psycopg2.connect(database_url,connect_timeout=1)
            conn.close()
            print("Database is ready!")
            return True
        except psycopg2.OperationalError as e:
            attempt += 1
            print(f"Attempt {attempt}/{max_attempts}: Database not ready yet...")
            time.sleep(2)
    
    print("Failed to connect to database after maximum attempts")
    return False

if __name__ == "__main__":
    if not wait_for_db():
        sys.exit(1)
    sys.exit(0)