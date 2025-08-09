GET_MAP_STATES_QUERY = """
    SELECT 
        location_id,
        STATE_NAME as name,
        state_iso,
        DATA_SOURCE_COUNT as source_count
    FROM
        PUBLIC.MAP_STATES
"""
