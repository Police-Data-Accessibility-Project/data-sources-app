REFRESH_ALL_MATERIALIZED_VIEWS_QUERIES = """
        DO $$
        DECLARE
            rec RECORD;
        BEGIN
            FOR rec IN SELECT schemaname, matviewname FROM pg_matviews
            LOOP
                EXECUTE 'REFRESH MATERIALIZED VIEW ' || quote_ident(rec.schemaname) || '.' || quote_ident(rec.matviewname);
            END LOOP;
        END;
        $$;
        """
