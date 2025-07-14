import os
import duckdb
from sim import config as cfg
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "simulation.db")

def initialize_database():
    con = duckdb.connect(DB_PATH)
    
    # Create shifts table (if not exists)
    con.execute("""
        CREATE OR REPLACE TABLE shifts (
            shift_id INTEGER PRIMARY KEY,
            shift_name TEXT,
            start_time FLOAT,
            end_time FLOAT
        )
    """)

    df = pd.DataFrame(cfg.SHIFTS_DEFINITION)
    con.execute("INSERT INTO shifts SELECT * FROM df")
    con.close()
    print('Database initialized')

if __name__ == "__main__":
    initialize_database()

