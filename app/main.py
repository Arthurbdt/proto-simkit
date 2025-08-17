import sys
import os
import streamlit as st
import duckdb
import pandas as pd
import altair as alt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# import simulation run function
from sim.core import run_simulation
from sim.logging import DB_PATH
from sim.config import SHIFTS_DEFINITION, SKILLS_DEFINITION, PICKERS_DEFAULT

# Create lookup dictionaries
SHIFT_ID_TO_NAME = {s["shift_id"]: s["shift_name"] for s in SHIFTS_DEFINITION}
SHIFT_NAME_TO_ID = {v: k for k, v in SHIFT_ID_TO_NAME.items()}

SKILL_ID_TO_NAME = {s["skill_id"]: s["skill_name"] for s in SKILLS_DEFINITION}
SKILL_NAME_TO_ID = {v: k for k, v in SKILL_ID_TO_NAME.items()}

# display initial picker
display_picker_df = pd.DataFrame([
    {
        "picker_id": p["picker_id"],
        "shift_name": SHIFT_ID_TO_NAME.get(p["shift_id"], ""),
        "skill_name": SKILL_ID_TO_NAME.get(p["skill_id"], "")
    }
    for p in PICKERS_DEFAULT
])


######### PAGE LAYOUT ######

st.title("Simulation App") # app title
run_button = st.sidebar.button("Run Simulation")

# Sidebar navigation
page = st.sidebar.radio("Navigation", ["Simulation", "How To"])

edited_df = st.data_editor(
    display_picker_df,
    num_rows="dynamic",
    use_container_width=True,
    key="picker_table",
    column_config={
        "shift_name": st.column_config.SelectboxColumn(
            label="Shift",
            options=list(SHIFT_NAME_TO_ID.keys())
        ),
        "skill_name": st.column_config.SelectboxColumn(
            label="Skill",
            options=list(SKILL_NAME_TO_ID.keys())
        )
    }
)

picker_input = []
for _, row in edited_df.iterrows():
    picker_input.append({
        "picker_id": row["picker_id"],
        "shift_id": SHIFT_NAME_TO_ID.get(row["shift_name"]),
        "skill_id": SKILL_NAME_TO_ID.get(row["skill_name"])
    })


# --- User Input ---
if page == "Simulation":
# --- Run simulation ---
    if run_button:
        st.write("Running simulation...")
        run_simulation(picker_input)
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

            # Picker states
            picker_states = con.execute("""
    WITH states AS (
        SELECT
            picker_id,
            state,
            timestamp AS start_time,
            LEAD(timestamp) OVER (PARTITION BY picker_id ORDER BY timestamp) AS end_time,
            LEAD(timestamp) OVER (PARTITION BY picker_id ORDER BY timestamp) - timestamp AS duration
        FROM picker_states
        ),
        state_duration AS (
        SELECT
            picker_id,
            state,
            SUM(duration) as duration
        FROM states
        GROUP BY picker_id, state
        )
        SELECT
            picker_id,
            state, 
            duration, 
            duration / SUM(duration) OVER (PARTITION BY picker_id) AS proportion
        FROM state_duration
""").fetch_df()
        
            # --- Display results ---
            st.subheader("Results")
            st.metric("Average Order Cycle Time", f"{avg_cycle_time:.2f} time units")

            st.subheader("Picker Workload")
            st.dataframe(picker_workload)

            st.bar_chart(picker_workload.set_index("picker_id"))

            chart = alt.Chart(picker_states).mark_bar().encode(
    x=alt.X("picker_id:N", title="Picker"),
    y=alt.Y("proportion:Q", stack="normalize", axis=alt.Axis(format='%')),
    color=alt.Color("state:N", title="State"),
    tooltip=["picker_id", "state", "duration", alt.Tooltip("proportion:Q", format=".0%")]
).properties(
    width=600,
    height=400
)
            st.altair_chart(chart, use_container_width=True)
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
