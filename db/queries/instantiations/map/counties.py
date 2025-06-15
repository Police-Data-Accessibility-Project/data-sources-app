GET_MAP_COUNTIES_QUERY = """
SELECT 
    location_id,
    county_name as name,
    state_iso,
    fips,
    DATA_SOURCE_COUNT as source_count
FROM
    PUBLIC.MAP_COUNTIES
"""
