#!/bin/bash
# Define the path for the dump file
DUMP_FILE="prod_dump.sql"

echo "Dumping production database..."
pg_dump $PROD_DB_CONN_STRING > $DUMP_FILE

echo "Dropping all connections to the development database..."
psql -d $DEV_ADMIN_DB_CONN_STRING -c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = 'dev_dbname' AND pid <> pg_backend_pid();"

echo "Dropping the development database..."
psql -d $DEV_ADMIN_DB_CONN_STRING -c "DROP DATABASE IF EXISTS pdap_dev_db;"

echo "Creating development database..."
psql -d $DEV_ADMIN_DB_CONN_STRING -c "CREATE DATABASE pdap_dev_db;"

echo "Restoring dump to development database..."
psql $DEV_DB_CONN_STRING < $DUMP_FILE
