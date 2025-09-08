""" Generate charts for application's KPIs """
import altair as alt
import pandas as pd

def plot_picker_states(data):
    """
    Create stacked bar chart plot of time spend in each state for all pcikers

    Inputs:
        - Data: pandas dataframe with columns picker_id, state and proportion
    """
    visual = (alt
        .Chart(data)
        .mark_bar()
        .encode(
            x=alt.X("picker_id:N", title="Picker"),
            y=alt.Y("proportion:Q", stack="normalize", axis=alt.Axis(format='%')),
            color=alt.Color("state:N", title="State"),
            tooltip=["picker_id", "state", "duration", alt.Tooltip("proportion:Q", format=".0%")]
        )
        .properties(width=600, height=400)
    )
    return visual

def plot_orders_in_system(data, shifts):
    """
    Create a line chart of active orders in system. Shifts are shaded to facilitate
    reading results

    Inputs:
        - Data: pandas dataframe with columns timestamp and count of orders
        - Shifts: array of dictionaries with shift start and end times
    """
    # create line chart
    line = (alt
        .Chart(data)
        .mark_line(color="steelblue")
        .encode(
            x=alt.X("t:Q", title="Time"),
            y=alt.Y("orders_in_system:Q", title="Orders in System")
        )
    )
    # alternate gray areas to model shifts
    shift_rects = []
    colors = ["#f5f5f5", "#e0e0e0"]  # alternate gray shades
    for i, shift in enumerate(shifts):
        rect = (alt
            .Chart(pd.DataFrame(
                {"start": [shift["start_time"]],
                 "end": [shift["end_time"]],
                 "shift": [shift["shift_name"]]
                }))
            .mark_rect(opacity=0.3, color=colors[i % len(colors)])
            .encode(x="start:Q", x2="end:Q")
        )
        shift_rects.append(rect)

    # generate visual
    visual = (alt
        .layer(*shift_rects, line)
        .resolve_scale(y='shared')
    )
    return visual

def expand_shifts(shifts, sim_duration, day_duration):
    """
    Replicates shift definitions across the full simulation horizon.
    """
    expanded = []
    n_days = int(sim_duration // day_duration)

    for d in range(n_days):
        offset = d * day_duration
        for shift in shifts:
            expanded.append({
                "shift_id": shift["shift_id"],
                "shift_name": shift["shift_name"],
                "start_time": shift["start_time"] + offset,
                "end_time": shift["end_time"] + offset,
            })
    return expanded