GET_MAP_LOCALITIES_QUERY = """
SELECT 
    location_id,
    LOCALITY_NAME as name,
    county_name,
    JSON_BUILD_OBJECT(
        'lat', lat,
        'lng', lng
    ) AS coordinates,
    county_fips,
    state_iso,
    DATA_SOURCE_COUNT as source_count
FROM
    PUBLIC.MAP_LOCALITIES
"""
