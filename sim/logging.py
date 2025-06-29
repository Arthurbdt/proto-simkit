import os
import duckdb
import pandas as pd
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "simulation.db")

class SimulationLogger:
    def __init__(self):
        # In-memory event store: key = order_id, value = dict with event data
        self.order_events = {}

    def log_order_arrival(self, order_id, timestamp):
        """ Record orders data"""
        self.order_events[order_id] = {
            "order_id": order_id,
            "arrival_time": timestamp,
            "start_pick_time": None,
            "end_pick_time": None,
            "picker_id": None,
        }

    def log_pick_start(self, order_id, picker_id, timestamp):
        """ Update order record with pick start time and assigned picker."""
        if order_id in self.order_events:
            self.order_events[order_id]["start_pick_time"] = timestamp
            self.order_events[order_id]["picker_id"] = picker_id

    def log_pick_end(self, order_id, timestamp):
        """ Update order record with pick end time."""
        if order_id in self.order_events:
            self.order_events[order_id]["end_pick_time"] = timestamp

    def flush(self):
        """ Write all in-memory order event data to DuckDB.
        Clears the target table before inserting."""
        con = duckdb.connect(DB_PATH)
        con.execute("DELETE FROM order_events")

        # Ensure table exists
        con.execute("""
            CREATE TABLE IF NOT EXISTS order_events (
                order_id TEXT,
                arrival_time FLOAT,
                start_pick_time FLOAT,
                end_pick_time FLOAT,
                picker_id TEXT
            )
        """)

        # Clear existing rows for clean testing/development


        # Write all events to the table
        self.order_events.reset_index(drop=True).to_sql(
        "order_events",
        self.con,
        if_exists="append",
        index=False
)

        df = pd.DataFrame(self.order_events.values())
        con.execute("INSERT INTO order_events SELECT * FROM df")

        con.close()