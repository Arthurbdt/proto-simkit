""" Store queries for application's KPIs """

def get_average_cycle_time(conn):
    """ """
    data = conn.execute("""
        SELECT
            AVG(end_pick_time - arrival_time) AS avg_cycle_time
        FROM order_events
        WHERE end_pick_time IS NOT NULL
        """).fetchone()[0]
    return data

def get_service_rate(conn):
    """ """
    data = conn.execute("""
        SELECT
            SUM(CASE WHEN end_pick_time <= due_date THEN 1 ELSE 0 END) * 1.0 / COUNT(order_id) AS prop_on_time
        FROM order_events
        WHERE end_pick_time IS NOT NULL
        """).df()
    return data

def get_picker_workload(conn):
    data = conn.execute("""
        SELECT 
            picker_id, 
            COUNT(order_id) AS orders_handled
        FROM order_events
        GROUP BY picker_id
        ORDER BY picker_id
        """).df()
    return data

def get_picker_states(conn):
    data = conn.execute("""
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
        """).df()
    return data

def get_orders_over_time(conn):
    data = conn.execute("""
        WITH events AS (
            SELECT arrival_time  AS t, +1 AS delta FROM order_events
            UNION ALL
            SELECT end_pick_time AS t, -1 AS delta FROM order_events
        )
        SELECT
            t,
            SUM(delta) OVER (ORDER BY t ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS orders_in_system
        FROM events
        WHERE t IS NOT NULL
        ORDER BY t
        """).df()
    return data