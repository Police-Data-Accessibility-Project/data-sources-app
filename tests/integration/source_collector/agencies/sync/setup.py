def set_updated_at_dates(agency_ids, dbc):
    stmt = f"""
    WITH ranked AS (
      SELECT
        id,
        ROW_NUMBER() OVER (ORDER BY id) AS rn
      FROM agencies
      WHERE agencies.id in ({", ".join(map(str, agency_ids))})
      LIMIT 1000
    )
    UPDATE agencies
    SET updated_at = CURRENT_DATE - INTERVAL '1 day' * ranked.rn
    FROM ranked
    WHERE agencies.id = ranked.id;
    """
    dbc.execute_raw_sql(stmt)
