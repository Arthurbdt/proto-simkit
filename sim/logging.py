import os
import duckdb
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "simulation.db")

class SimulationLogger:
    def __init__(self):
        # In-memory event store: key = order_id, value = dict with event data
        self.order_events = {}
        self.picker_states = []
    
    def log_pickers(self, pickers):
        """Store picker configuration for the current simulation."""
        df = pd.DataFrame(pickers)
        con = duckdb.connect(DB_PATH)
        con.execute("""
            CREATE OR REPLACE TABLE pickers (
                picker_id TEXT,
                shift_id INTEGER,
                skill_id INTEGER
            )
        """)
        con.execute("INSERT INTO pickers SELECT * FROM df")
        con.close()

    def log_order_arrival(self, order_id, arrival_time, due_date):
        """ Initialize order record upon arrival in the system"""
        self.order_events[order_id] = {
            "order_id": order_id,
            "arrival_time": arrival_time,
            "due_date": due_date,
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

    def log_picker_state(self, picker_id, state, timestamp):
        """ Record a change of state for a picker"""
        self.picker_states.append({
            "picker_id": picker_id,
            "state": state, 
            "timestamp": timestamp
            })

    def flush(self):
        """ Write all in-memory order events and picker states data to DuckDB.
        Clears the target table before inserting."""
        con = duckdb.connect(DB_PATH)

        # Ensure order events table exists
        con.execute("""
            CREATE OR REPLACE TABLE order_events (
                order_id TEXT,
                arrival_time FLOAT,
                due_date FLOAT,
                start_pick_time FLOAT,
                end_pick_time FLOAT,
                picker_id TEXT
            )
        """)

        # Ensure picker states table exists
        con.execute("""
            CREATE OR REPLACE TABLE picker_states (
                picker_id TEXT,
                state TEXT,
                timestamp FLOAT
            )
        """)

        # Write all events to the table
        df_order_events = pd.DataFrame(self.order_events.values())
        con.execute("INSERT INTO order_events SELECT * FROM df_order_events")

        # Write all picker states to the table
        df_picker_states = pd.DataFrame(self.picker_states)
        con.execute("INSERT INTO picker_states SELECT * FROM df_picker_states")

        con.close()