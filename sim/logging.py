import os
import duckdb
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "simulation.db")

class SimulationLogger:
    def __init__(self):
        # In-memory event store: key = order_id, value = dict with event data
        self.order_events = {}

    def log_order_arrival(self, order_id, timestamp):
        """ Initialize order record upon arrival in the system"""
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

        # Ensure table exists
        con.execute("""
            CREATE OR REPLACE TABLE order_events (
                order_id TEXT,
                arrival_time FLOAT,
                start_pick_time FLOAT,
                end_pick_time FLOAT,
                picker_id TEXT
            )
        """)

        # Write all events to the table
        df = pd.DataFrame(self.order_events.values())
        con.execute("INSERT INTO order_events SELECT * FROM df")

        con.close()