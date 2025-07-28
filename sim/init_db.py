import os
import duckdb
from sim import config as cfg
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "simulation.db")

def initialize_database():
    con = duckdb.connect(DB_PATH)
    
    # Create and populate shifts table
    con.execute("""
        CREATE OR REPLACE TABLE shifts (
            shift_id INTEGER PRIMARY KEY,
            shift_name TEXT,
            start_time FLOAT,
            end_time FLOAT
        )
    """)
    df_shifts = pd.DataFrame(cfg.SHIFTS_DEFINITION)
    con.execute("INSERT INTO shifts SELECT * FROM df_shifts")

    # create and populate skills table
    con.execute("""
        CREATE OR REPLACE TABLE skills (
            skill_id INTEGER PRIMARY KEY,
            skill_name TEXT,
            speed_factor FLOAT
        )
    """)
    df_skills = pd.DataFrame(cfg.SKILLS_DEFINITION)
    con.execute("INSERT INTO skills SELECT * FROM df_skills")
    
    con.close()
    print('Database initialized')

if __name__ == "__main__":
    initialize_database()

