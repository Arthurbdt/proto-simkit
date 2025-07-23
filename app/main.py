import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import duckdb
import os

# Import simulation run function
from sim.core import run_simulation
from sim.logging import DB_PATH
from sim.config import SHIFTS_DEFINITION


st.title("Simulation App") # app title
run_button = st.sidebar.button("Run Simulation")

# Sidebar navigation
page = st.sidebar.radio("Navigation", ["Simulation", "How To"])


st.header("Assign Pickers to Shifts")

pickers = []
for shift in SHIFTS_DEFINITION:
    count = st.number_input(
        f"Number of pickers for {shift['shift_name']} ({shift['start_time']}–{shift['end_time']})",
        min_value=0,
        value=2,
        key=f"shift_{shift['shift_id']}"
    )
    for i in range(count):
        pickers.append({
            "picker_id": f"Picker-{shift['shift_id']}-{i+1}",
            "shift_id": shift["shift_id"]
        })

# --- User Input ---
if page == "Simulation":
# --- Run simulation ---
    if run_button:
        st.write("Running simulation...")
        run_simulation(pickers)
        st.success("Simulation complete!")

        # --- Query results ---
        try:
            con = duckdb.connect(DB_PATH)

            # Average cycle time
            avg_cycle_time = con.execute("""
                SELECT AVG(end_pick_time - arrival_time) AS avg_cycle_time
                FROM order_events
                WHERE end_pick_time IS NOT NULL
            """).fetchone()[0]

            # Picker workload
            picker_workload = con.execute("""
                SELECT picker_id, COUNT(order_id) AS orders_handled
                FROM order_events
                GROUP BY picker_id
                ORDER BY picker_id
            """).fetchdf()

            # --- Display results ---
            st.subheader("Results")
            st.metric("Average Order Cycle Time", f"{avg_cycle_time:.2f} time units")

            st.subheader("Picker Workload")
            st.dataframe(picker_workload)

            st.bar_chart(picker_workload.set_index("picker_id"))

        except Exception as e:
            st.error(f"Failed to load results: {e}")

elif page == "How To":
    st.header("How To Use This App")
    st.markdown("""
    ### Steps to run the simulation:
    1. Select the number of pickers.
    2. Click the **Run Simulation** button.
    3. Wait for the simulation to finish.
    4. View results on the Simulation page.

    ### About the simulation:
    - This app models order picking using discrete event simulation.
    - Each picker works individually.
    - Results include cycle times and workload.

    ### Contact:
    For questions, reach out at [email@example.com](mailto:email@example.com)
    """)
