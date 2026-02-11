import os
import psycopg2
from contextlib import contextmanager

DATABASE_URL = os.environ["DATABASE_URL"]

@contextmanager
def get_connection():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()
