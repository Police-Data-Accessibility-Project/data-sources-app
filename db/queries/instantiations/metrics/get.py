GET_METRICS_QUERY = """
            SELECT
                COUNT(*),
                'source_count' "Count Type"
            FROM
                DATA_SOURCES
            UNION
            SELECT
                COUNT(DISTINCT (AGENCY_ID)),
                'agency_count' "Count Type"
            FROM
                link_agencies__data_sources
            UNION
            SELECT
                COUNT(DISTINCT L.ID),
                'state_count' "Count Type"
            FROM
                LINK_AGENCIES_DATA_SOURCES LINK
                INNER JOIN AGENCIES A ON A.ID = LINK.AGENCY_ID
                LEFT JOIN LINK_AGENCIES_LOCATIONS LAL on A.ID = LAL.AGENCY_ID
                JOIN DEPENDENT_LOCATIONS DL ON LAL.LOCATION_ID = DL.DEPENDENT_LOCATION_ID
                JOIN LOCATIONS L ON L.ID = LAL.LOCATION_ID
                OR L.ID = DL.PARENT_LOCATION_ID
            WHERE
                L.TYPE = 'State'
            UNION
            SELECT
                COUNT(DISTINCT L.ID),
                'county_count' "Count Type"
            FROM
                LINK_AGENCIES_DATA_SOURCES LINK
                INNER JOIN AGENCIES A ON A.ID = LINK.AGENCY_ID
                LEFT JOIN LINK_AGENCIES_LOCATIONS LAL on A.ID = LAL.AGENCY_ID
                JOIN DEPENDENT_LOCATIONS DL ON LAL.LOCATION_ID = DL.DEPENDENT_LOCATION_ID
                JOIN LOCATIONS L ON L.ID = LAL.LOCATION_ID
                OR L.ID = DL.PARENT_LOCATION_ID
            WHERE
                L.TYPE = 'County'
	"""
