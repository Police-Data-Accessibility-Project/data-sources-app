"""Initial creation

Revision ID: 34f45aad081a
Revises:
Create Date: 2025-01-20 12:44:42.378015

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import Table
from sqlalchemy.dialects.postgresql import ENUM

from database_client.models.core import Base
from relation_access_permissions.upload_relation_configurations_to_db import (
    upload_relation_configurations_to_db_alembic,
)

# revision identifiers, used by Alembic.
revision: str = "34f45aad081a"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Enums
access_permission_enum = ENUM(
    "READ", "WRITE", "NONE", name="access_permission", create_type=False
)
access_type_enum = ENUM(
    "Download", "Webpage", "API", name="access_type", create_type=False
)
account_type_enum = ENUM("github", name="account_type", create_type=False)
agency_aggregation_enum = ENUM(
    "county", "local", "state", "federal", name="agency_aggregation", create_type=False
)
approval_status_enum = ENUM(
    "approved",
    "rejected",
    "pending",
    "needs identification",
    name="approval_status",
    create_type=False,
)
detail_level_enum = ENUM(
    "Individual record",
    "Aggregated records",
    "Summarized totals",
    name="detail_level",
    create_type=False,
)
entity_type_enum = ENUM(
    "Data Request", "Data Source", name="entity_type", create_type=False
)
event_type_enum = ENUM(
    "Request Ready to Start",
    "Request Complete",
    "Data Source Approved",
    name="event_type",
    create_type=False,
)
jurisdiction_type_enum = ENUM(
    "school",
    "county",
    "local",
    "port",
    "tribal",
    "transit",
    "state",
    "federal",
    name="jurisdiction_type",
    create_type=False,
)
location_type_enum = ENUM(
    "State", "County", "Locality", name="location_type", create_type=False
)
record_type_enum = ENUM(
    "Dispatch Recordings",
    "Arrest Records",
    "Citations",
    "Incarceration Records",
    "Booking Reports",
    "Budgets & Finances",
    "Misc Police Activity",
    "Geographic",
    "Crime Maps & Reports",
    "Other",
    "Annual & Monthly Reports",
    "Resources",
    "Dispatch Logs",
    "Sex Offender Registry",
    "Officer Involved Shootings",
    "Daily Activity Logs",
    "Crime Statistics",
    "Records Request Info",
    "Policies & Contracts",
    "Stops",
    "Media Bulletins",
    "Training & Hiring Info",
    "Personnel Records",
    "Contact Info & Agency Meta",
    "Incident Reports",
    "Calls for Service",
    "Accident Reports",
    "Use of Force Reports",
    "Complaints & Misconduct",
    "Vehicle Pursuits",
    "Court Cases",
    "Surveys",
    "Field Contacts",
    "Wanted Persons",
    "List of Data Sources",
    "Car GPS",
    name="record_type",
    create_type=False,
)
relation_role_enum = ENUM(
    "STANDARD", "OWNER", "ADMIN", name="relation_role", create_type=False
)
request_status_enum = ENUM(
    "Intake",
    "Active",
    "Complete",
    "Request withdrawn",
    "Waiting for scraper",
    "Archived",
    "Ready to start",
    "Waiting for FOIA",
    "Waiting for requestor",
    name="request_status",
    create_type=False,
)
request_urgency_level_enum = ENUM(
    "urgent",
    "somewhat_urgent",
    "not_urgent",
    "long_term",
    "indefinite_unknown",
    name="request_urgency_level",
    create_type=False,
)
retention_schedule_enum = ENUM(
    "< 1 day",
    "1 day",
    "< 1 week",
    "1 week",
    "1 month",
    "< 1 year",
    "1-10 years",
    "> 10 years",
    "Future only",
    name="retention_schedule",
    create_type=False,
)
search_result_enum = ENUM(
    "found_results", "no_results_found", name="search_result", create_type=False
)
search_status_enum = ENUM(
    "pending",
    "completed",
    "error",
    "no_results",
    name="search_status",
    create_type=False,
)
update_method_enum = ENUM(
    "Insert", "No updates", "Overwrite", name="update_method", create_type=False
)
url_status_enum = ENUM(
    "ok", "none found", "broken", "available", name="url_status", create_type=False
)
enum_list = [
    access_permission_enum,
    access_type_enum,
    account_type_enum,
    agency_aggregation_enum,
    approval_status_enum,
    detail_level_enum,
    entity_type_enum,
    event_type_enum,
    jurisdiction_type_enum,
    location_type_enum,
    record_type_enum,
    relation_role_enum,
    request_status_enum,
    request_urgency_level_enum,
    retention_schedule_enum,
    search_result_enum,
    search_status_enum,
    update_method_enum,
    url_status_enum,
]


def upgrade() -> None:
    # Enums
    full_sql_upgrade()
    data_inserts()


def full_sql_upgrade():
    # Load sql file
    with open("alembic/misc/original_schema.sql", "r") as f:
        sql = f.read()

    # Execute sql
    op.execute(sql)


def data_inserts():
    meta = Base.metadata
    meta.reflect(bind=op.get_bind(), only=("permissions", "us_states", "counties"))

    op.bulk_insert(
        Table("permissions", meta),
        [
            {
                "permission_name": "db_write",
                "description": "Child apps and human maintainers can use this",
            },
            {
                "permission_name": "read_all_user_info",
                "description": "Enables viewing of user data; for admin use only",
            },
            {
                "permission_name": "notifications",
                "description": "Enables sending of notifications to users",
            },
            {
                "permission_name": "source_collector",
                "description": "Enables access to the Source Collector API",
            },
        ],
    )
    op.bulk_insert(
        Table("us_states", meta),
        [
            {"state_iso": "PA", "state_name": "Pennsylvania"},
            {"state_iso": "CA", "state_name": "California"},
            {"state_iso": "OH", "state_name": "Ohio"},
        ],
    )
    op.bulk_insert(
        Table("counties", meta),
        [
            {"name": "Allegheny", "state_iso": "PA", "fips": "42003", "state_id": 1},
            {"name": "Philadelphia", "state_iso": "PA", "fips": "42001", "state_id": 1},
            {
                "name": "Cuyahoga",
                "state_iso": "OH",
                "state_id": 3,
                "fips": "39003",
            },
            {
                "name": "Orange",
                "state_iso": "CA",
                "state_id": 2,
                "fips": "06003",
            },
        ],
    )
    op.execute(
        """
    BEGIN;

    -- Insert statements for categories and storing their IDs in variables
    DO $$
    DECLARE
        police_public_interactions_id INT;
        info_about_officers_id INT;
        info_about_agencies_id INT;
        agency_published_resources_id INT;
        jails_courts_specific_id INT;
        other_id INT;
    BEGIN

        INSERT INTO record_categories (name) VALUES ('Police & Public Interactions') RETURNING id INTO police_public_interactions_id;
    INSERT INTO record_categories (name) VALUES ('Info about Officers') RETURNING id INTO info_about_officers_id;
    INSERT INTO record_categories (name) VALUES ('Info about Agencies') RETURNING id INTO info_about_agencies_id;
    INSERT INTO record_categories (name) VALUES ('Agency-published Resources') RETURNING id INTO agency_published_resources_id;
    INSERT INTO record_categories (name) VALUES ('Jails & Courts') RETURNING id INTO jails_courts_specific_id;
    INSERT INTO RECORD_CATEGORIES (name, description)
    VALUES ('All', 'Pseudo-category representing all record categories');
    INSERT INTO record_categories (name) VALUES ('Other') RETURNING id INTO other_id;


    -- Insert statements for record_types using stored category IDs
    INSERT INTO record_types (name, category_id, description) VALUES
        ('Accident Reports', police_public_interactions_id, 'Records of vehicle accidents, sometimes published so that people involved in an accident can look up the police report.'),
        ('Arrest Records', police_public_interactions_id, 'Records of each arrest made in the agency''s jurisdiction.'),
        ('Calls for Service', police_public_interactions_id, 'Records of officers initiating activity or responding to requests for police response. Often called "Dispatch Logs" or "Incident Reports" when published.'),
        ('Car GPS', police_public_interactions_id, 'Records of police car location. Not generally posted online.'),
        ('Citations', police_public_interactions_id, 'Records of low-level criminal offenses where a police officer issued a citation instead of an arrest.'),
        ('Dispatch Logs', police_public_interactions_id, 'Records of calls or orders made by police dispatchers.'),
        ('Dispatch Recordings', police_public_interactions_id, 'Audio feeds and/or archives of municipal dispatch channels.'),
        ('Field Contacts', police_public_interactions_id, 'Reports of contact between police and civilians. May include uses of force, incidents, arrests, or contacts where nothing notable happened.'),
        ('Incident Reports', police_public_interactions_id, 'Reports made by police officers after responding to a call which may or may not be criminal in nature. Not generally posted online.'),
        ('Misc Police Activity', police_public_interactions_id, 'Records or descriptions of police activity not covered by other record types.'),
        ('Officer Involved Shootings', police_public_interactions_id, 'Case files of gun violence where a police officer was involved, typically as the shooter. Detailed, often containing references to records like Media Bulletins and Use of Force Reports.'),
        ('Stops', police_public_interactions_id, 'Records of pedestrian or traffic stops made by police.'),
        ('Surveys', police_public_interactions_id, 'Information captured from a sample of some population, like incarcerated people or magistrate judges. Often generated independently.'),
        ('Use of Force Reports', police_public_interactions_id, 'Records of use of force against civilians by police officers.'),
        ('Vehicle Pursuits', police_public_interactions_id, 'Records of cases where police pursued a person fleeing in a vehicle.'),
        ('Complaints & Misconduct', info_about_officers_id, 'Records, statistics, or summaries of complaints and misconduct investigations into law enforcement officers.'),
        ('Daily Activity Logs', info_about_officers_id, 'Officer-created reports or time sheets of what happened on a shift. Not generally posted online.'),
        ('Training & Hiring Info', info_about_officers_id, 'Records and descriptions of additional training for police officers.'),
        ('Personnel Records', info_about_officers_id, 'Records of hiring and firing, certification, discipline, and other officer-specific events. Not generally posted online.'),
        ('Annual & Monthly Reports', info_about_agencies_id, 'Often in PDF form, featuring summaries or high-level updates about the police force. Can contain versions of other record types, especially summaries.'),
        ('Budgets & Finances', info_about_agencies_id, 'Budgets, finances, grants, or other financial documents.'),
        ('Contact Info & Agency Meta', info_about_agencies_id, 'Information about organizational structure, including department structure and contact info.'),
        ('Geographic', info_about_agencies_id, 'Maps or geographic data about how land is divided up into municipal sectors, zones, and jurisdictions.'),
        ('List of Data Sources', info_about_agencies_id, 'Places on the internet, often data portal homepages, where many links to potential data sources can be found.'),
        ('Policies & Contracts', info_about_agencies_id, 'Policies or contracts related to agency procedure.'),
        ('Crime Maps & Reports', agency_published_resources_id, 'Records of individual crimes in map or table form for a given jurisdiction.'),
        ('Crime Statistics', agency_published_resources_id, 'Summarized information about crime in a given jurisdiction.'),
        ('Media Bulletins', agency_published_resources_id, 'Press releases, blotters, or blogs intended to broadly communicate alerts, requests, or other timely information.'),
        ('Records Request Info', agency_published_resources_id, 'Portals, forms, policies, or other resources for making public records requests.'),
        ('Resources', agency_published_resources_id, 'Agency-provided information or guidance about services, prices, best practices, etc.'),
        ('Sex Offender Registry', agency_published_resources_id, 'Index of people registered, usually by law, with the government as sex offenders.'),
        ('Wanted Persons', agency_published_resources_id, 'Names, descriptions, images, and associated information about people with outstanding arrest warrants.'),
        ('Booking Reports', jails_courts_specific_id, 'Records of booking or intake into corrections institutions.'),
        ('Court Cases', jails_courts_specific_id, 'Records such as dockets about individual court cases.'),
        ('Incarceration Records', jails_courts_specific_id, 'Records of current inmates, often with full names and features for notification upon inmate release.'),
        ('Other', other_id, 'Other record types not otherwise described.');


    END $$;

    -- Commit the transaction
    COMMIT;
    """
    )
    upload_relation_configurations_to_db_alembic()


def downgrade() -> None:
    # op.execute("""
    # DROP SCHEMA public CASCADE;
    # CREATE SCHEMA public;
    # """)
    # # Views
    views = [
        "data_requests_expanded",
        "agencies_expanded",
        "recent_searches_expanded" "locations_expanded",
        "data_sources_expanded",
        "dependent_locations",
        "locations_expanded",
        "num_agencies_per_data_source",
        "num_data_sources_per_agency",
        "qualifying_notifications",
        "record_types_expanded",
        "relation_column_permission_view",
        "user_external_accounts",
        "user_pending_notifications",
    ]
    for view in views:
        op.execute(f"DROP VIEW IF EXISTS public.{view} CASCADE;")

    materialized_views = [
        "distinct_source_urls",
        "typeahead_agencies",
        "typeahead_locations",
    ]
    for view in materialized_views:
        op.execute(f"DROP MATERIALIZED VIEW IF EXISTS public.{view} CASCADE;")

    procedures = [
        "refresh_distinct_source_urls",
        "refresh_typeahead_agencies",
        "refresh_typeahead_locations",
    ]
    for procedure in procedures:
        op.execute(f"DROP PROCEDURE IF EXISTS public.{procedure} CASCADE;")

    trigger_functions = [
        "insert_county_location",
        "insert_locality_location",
        "insert_new_archive_info",
        "insert_state_location",
        "maintain_recent_searches_row_limit",
        "set_agency_name",
        "set_source_name",
        "update_airtable_agency_last_modified_column",
        "update_approval_status_updated_at",
        "update_broken_source_url_as_of",
        "update_data_source_updated_at_column",
        "update_executed_datetime",
        "update_search_status",
        "update_status_change_date",
    ]
    for function in trigger_functions:
        op.execute(f"DROP FUNCTION IF EXISTS public.{function} CASCADE;")

    # Tables
    tables_to_drop = [
        "user_notification_queue",
        "search_links",
        "search_results",
        "search_queue",
        "search_batch_info",
        "pending_users",
        "link_user_followed_location",
        "link_recent_search_record_categories",
        "link_locations_data_requests",
        "link_data_sources_data_requests",
        "link_agencies_data_sources",
        "data_sources_archive_info",
        "data_sources",
        "record_types",
        "record_categories",
        "data_requests_github_issue_info",
        "agency_url_search_cache",
        "zip_codes",
        "agencies",
        "data_requests",
        "recent_searches",
        "locations",
        "localities",
        "counties",
        "us_states",
        "column_permission",
        "relation_column",
        "external_accounts",
        "user_permissions",
        "reset_tokens",
        "users",
        "permissions",
        "test_table",
    ]

    for table in tables_to_drop:
        op.drop_table(table)

    # Functions
    op.execute("DROP FUNCTION IF EXISTS public.generate_api_key();")

    # Enums
    for enum in enum_list:
        enum.drop(op.get_bind(), checkfirst=True)

    # Sequences
    op.execute(
        """
        DO $$
    DECLARE
        seq_record RECORD;
    BEGIN
        FOR seq_record IN 
            SELECT schemaname, sequencename 
            FROM pg_sequences
        LOOP
            EXECUTE FORMAT('DROP SEQUENCE IF EXISTS %I.%I CASCADE', seq_record.schemaname, seq_record.sequencename);
        END LOOP;
    END;
    $$;
    """
    )
