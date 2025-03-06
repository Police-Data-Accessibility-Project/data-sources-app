"""Overhaul notification architecture

Revision ID: e628c1173d56
Revises: 9d4bc460faba
Create Date: 2025-03-05 10:06:17.336913

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column

# revision identifiers, used by Alembic.
revision: str = "e628c1173d56"
down_revision: Union[str, None] = "9d4bc460faba"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # Remove `user_pending_notifications` view
    op.execute("DROP VIEW IF EXISTS user_pending_notifications")

    # Remove `qualifying_notifications` view
    op.execute("DROP VIEW IF EXISTS qualifying_notifications")

    # Create `pending_event_notifications` table
    # region pending_event_notifications
    op.create_table(
        "pending_event_notifications",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column(
            "event_type",
            sa.dialects.postgresql.ENUM(name="event_type", create_type=False),
            nullable=False,
        ),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
    )
    # endregion

    # Create link_data_request_pending_event_notifications table
    # region link_data_request_pending_event_notifications
    op.create_table(
        "link_data_request_pending_event_notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("data_request_id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["data_request_id"],
            ["data_requests.id"],
            name="link_data_request_pending_event_notifications_dr_id_fkey",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["event_id"],
            ["pending_event_notifications.id"],
            name="link_data_request_pending_event_notifications_event_id_fkey",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name="link_data_request_pending_event_notifications_pkey",
        ),
        sa.UniqueConstraint(
            "data_request_id",
            name="link_data_request_pending_event_notifications_unique",
        ),
    )
    # endregion

    # Create trigger that enforces constraint such that the event type
    # must be "Data Request Approved" or "Data Request Completed"
    # First, create function
    op.execute(
        """
        CREATE OR REPLACE FUNCTION enforce_data_request_event_type()
        RETURNS TRIGGER AS $$
        
        DECLARE actual_event_type TEXT;
        BEGIN
        
            -- Retrieve the actual event type
            SELECT event_type 
            INTO actual_event_type
            FROM pending_event_notifications
            WHERE id = NEW.event_id;
        
            -- Check if the event type is one of the allowed types
            IF actual_event_type IS NULL OR actual_event_type NOT IN 
                ('Request Ready to Start', 'Request Complete') THEN
                RAISE EXCEPTION 'Invalid event type: %. Event type must be "Request Ready to Start" or "Request Complete".', COALESCE(actual_event_type, 'NULL');
            END IF;
        
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

    """
    )

    op.execute(
        """
        CREATE OR REPLACE TRIGGER enforce_data_request_event_type
        BEFORE INSERT OR UPDATE
        ON public.link_data_request_pending_event_notifications
        FOR EACH ROW
        EXECUTE PROCEDURE enforce_data_request_event_type();
    """
    )

    # Create trigger that ensures that, if a row is inserted into the link
    # table which has the same data_request_id as another row, then the
    # then the old row, and the event_id it points to, is deleted
    # First, create function
    op.execute(
        """
        CREATE OR REPLACE FUNCTION enforce_unique_link_data_request_pending_event_notifications()
        RETURNS TRIGGER AS $$
        
        BEGIN
            IF EXISTS (
                SELECT 1 FROM link_data_request_pending_event_notifications 
                WHERE data_request_id = NEW.data_request_id
            ) THEN
                DELETE FROM link_data_request_pending_event_notifications 
                WHERE data_request_id = NEW.data_request_id AND event_id = OLD.event_id;
                DELETE FROM pending_event_notifications 
                WHERE id = OLD.event_id;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """
    )

    op.execute(
        """
        CREATE OR REPLACE TRIGGER enforce_unique_link_data_request_pending_event_notifications
        BEFORE INSERT OR UPDATE
        ON public.link_data_request_pending_event_notifications
        FOR EACH ROW
        EXECUTE PROCEDURE enforce_unique_link_data_request_pending_event_notifications();
    """
    )

    # Create `link_data_source_pending_event_notification` table
    # region link_data_source_pending_event_notification
    op.create_table(
        "link_data_source_pending_event_notification",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("data_source_id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["data_source_id"],
            ["data_sources.id"],
            name="link_data_source_pending_event_notification_ds_id_fkey",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["event_id"],
            ["pending_event_notifications.id"],
            name="link_data_source_pending_event_notification_event_id_fkey",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name="link_data_source_pending_event_notification_pkey",
        ),
        sa.UniqueConstraint(
            "data_source_id",
            name="link_data_source_pending_event_notification_unique",
        ),
    )
    # endregion

    # Create trigger that ensures that, if a row is inserted into the link
    # table which has the same data_request_id as another row, then the
    # then the old row, and the event_id it points to, is deleted
    # First, create function
    op.execute(
        """
        CREATE OR REPLACE FUNCTION enforce_unique_link_data_source_pending_event_notification()
        RETURNS TRIGGER AS $$

        BEGIN
            IF EXISTS (
                SELECT 1 FROM link_data_source_pending_event_notification 
                WHERE data_source_id = NEW.data_source_id
            ) THEN
                DELETE FROM link_data_source_pending_event_notification 
                WHERE data_source_id = NEW.data_source_id AND event_id = OLD.event_id;
                DELETE FROM pending_event_notifications 
                WHERE id = OLD.event_id;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """
    )

    op.execute(
        """
        CREATE OR REPLACE TRIGGER enforce_unique_link_data_source_pending_event_notification
        BEFORE INSERT OR UPDATE
        ON public.link_data_source_pending_event_notification
        FOR EACH ROW
        EXECUTE PROCEDURE enforce_unique_link_data_source_pending_event_notification();
    """
    )

    # Create trigger that enforces constraint such that the event type
    # must be "Data Source Approved" or "Data Source Completed"
    # First, create function
    op.execute(
        """
        CREATE OR REPLACE FUNCTION enforce_data_source_event_type()
        RETURNS TRIGGER AS $$
        
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pending_event_notifications 
                WHERE id = NEW.event_id AND event_type IN (
                    'Data Source Approved'
                )
            ) THEN
                RAISE EXCEPTION 'Event type must be "Data Source Approved".';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """
    )
    # Then, create trigger
    op.execute(
        """
        CREATE OR REPLACE TRIGGER enforce_data_source_event_type
        BEFORE INSERT OR UPDATE
        ON public.link_data_source_pending_event_notification
        FOR EACH ROW
        EXECUTE PROCEDURE enforce_data_source_event_type();
    """
    )

    # Create trigger so that, when a request is set as `Ready to start` or `Request Complete`, you insert into PEN
    # First, create function
    op.execute(
        """
    CREATE OR REPLACE FUNCTION insert_pending_data_request_event_notification()
    RETURNS TRIGGER AS $$
    
    DECLARE event_id INT;
    BEGIN
        IF NEW.request_status is null THEN
            RETURN NEW;
        END IF;
        
        IF (TG_OP = 'INSERT' AND NEW.request_status in ('Ready to start'::request_status, 'Complete'::request_status))
        OR 
            (
            TG_OP = 'UPDATE' AND 
            NEW.request_status != OLD.request_status 
            AND NEW.request_status IN ('Ready to start'::request_status, 'Complete'::request_status)
            ) 
        THEN
            INSERT INTO pending_event_notifications (event_type)
            VALUES (
                CASE
                    WHEN NEW.request_status = 'Ready to start'::request_status THEN 'Request Ready to Start'::event_type
                    WHEN NEW.request_status = 'Complete'::request_status THEN 'Request Complete'::event_type
                END
            )
            RETURNING id INTO event_id;
            INSERT INTO link_data_request_pending_event_notifications (data_request_id, event_id)
            VALUES (NEW.id, event_id);
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    """
    )
    # Then, create trigger
    op.execute(
        """
        CREATE OR REPLACE TRIGGER insert_pending_data_request_event_notification
        AFTER INSERT OR UPDATE
        ON public.data_requests
        FOR EACH ROW
        EXECUTE PROCEDURE insert_pending_data_request_event_notification();
    """
    )

    # Create trigger so that, when a data source is approved, you insert into PEN
    # First, create function
    op.execute(
        """
    CREATE OR REPLACE FUNCTION insert_pending_data_source_event_notification()
    RETURNS TRIGGER AS $$
    
    DECLARE event_id INT;
    BEGIN
        IF (
            TG_OP = 'INSERT' AND NEW.approval_status = 'approved'::approval_status)
            OR (
                TG_OP = 'UPDATE' 
                AND NEW.approval_status != OLD.approval_status 
                AND NEW.approval_status = 'approved'::approval_status
        ) THEN
            INSERT INTO pending_event_notifications (event_type)
            VALUES ('Data Source Approved'::event_type)
            RETURNING id INTO event_id;
            INSERT INTO link_data_source_pending_event_notification (data_source_id, event_id)
            VALUES (NEW.id, event_id);
            
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    """
    )
    # Then, create trigger

    op.execute(
        """
        CREATE OR REPLACE TRIGGER insert_pending_data_source_event_notification
        AFTER INSERT OR UPDATE
        ON public.data_sources
        FOR EACH ROW
        EXECUTE PROCEDURE insert_pending_data_source_event_notification();
    """
    )

    # Update `user_notification_queue` table

    # Remove the following columns
    columns = [
        "email",
        "entity_id",
        "entity_type",
        "entity_name",
        "event_type",
        "event_timestamp",
    ]
    for column in columns:
        op.drop_column("user_notification_queue", column)

    # Add the following columns
    # pen_id, a foreign key to the `pending_event_notifications` table
    op.add_column(
        "user_notification_queue",
        sa.Column("pen_id", sa.Integer(), nullable=True),
    )
    # Add unique constraint between user_id and pen_id
    op.create_unique_constraint(
        "user_notification_queue_user_id_pen_id_key",
        "user_notification_queue",
        ["user_id", "pen_id"],
    )

    # Add the following constraints
    op.create_foreign_key(
        "user_notification_queue_pen_id_fkey",
        "user_notification_queue",
        "pending_event_notifications",
        ["pen_id"],
        ["id"],
    )

    # created_at
    op.add_column(
        "user_notification_queue",
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
    )


def downgrade() -> None:

    # Drop unique constraint user_notification_queue_user_id_pen_id_key
    op.drop_constraint(
        "user_notification_queue_user_id_pen_id_key",
        "user_notification_queue",
        type_="unique",
    )

    # Drop columns
    op.drop_column(table_name="user_notification_queue", column_name="pen_id")
    op.drop_column(table_name="user_notification_queue", column_name="created_at")

    # Create `qualifying_notifications` view
    # region qualifying_notifications
    op.execute(
        """
        CREATE OR REPLACE VIEW public.qualifying_notifications
     AS
     WITH cutoff_point AS (
             SELECT date_trunc('month'::text, CURRENT_DATE::timestamp with time zone) - '1 mon'::interval AS date_range_min,
                date_trunc('month'::text, CURRENT_DATE::timestamp with time zone) AS date_range_max
            )
     SELECT
            CASE
                WHEN dr.request_status = 'Ready to start'::request_status THEN 'Request Ready to Start'::event_type
                WHEN dr.request_status = 'Complete'::request_status THEN 'Request Complete'::event_type
                ELSE NULL::event_type
            END AS event_type,
        dr.id AS entity_id,
        'Data Request'::entity_type AS entity_type,
        dr.title AS entity_name,
        lnk_dr.location_id,
        dr.date_status_last_changed AS event_timestamp
       FROM cutoff_point cp,
        data_requests dr
         JOIN link_locations_data_requests lnk_dr ON lnk_dr.data_request_id = dr.id
      WHERE dr.date_status_last_changed > cp.date_range_min AND dr.date_status_last_changed < cp.date_range_max AND (dr.request_status = 'Ready to start'::request_status OR dr.request_status = 'Complete'::request_status)
    UNION ALL
     SELECT 'Data Source Approved'::event_type AS event_type,
        ds.id AS entity_id,
        'Data Source'::entity_type AS entity_type,
        ds.name AS entity_name,
        lal.location_id,
        ds.approval_status_updated_at AS event_timestamp
       FROM cutoff_point cp,
        data_sources ds
         JOIN link_agencies_data_sources lnk ON lnk.data_source_id = ds.id
         JOIN agencies a ON lnk.agency_id = a.id
         LEFT JOIN link_agencies_locations lal ON lal.agency_id = a.id
      WHERE ds.approval_status_updated_at > cp.date_range_min AND ds.approval_status_updated_at < cp.date_range_max AND ds.approval_status = 'approved'::approval_status;

    """
    )
    # endregion

    # Create `user_pending_notifications` view
    op.execute(
        """
    CREATE OR REPLACE VIEW public.user_pending_notifications
 AS
 SELECT DISTINCT q.event_type,
    q.entity_id,
    q.entity_type,
    q.entity_name,
    q.location_id,
    q.event_timestamp,
    l.user_id,
    u.email
   FROM qualifying_notifications q
     JOIN dependent_locations d ON d.dependent_location_id = q.location_id
     JOIN link_user_followed_location l ON l.location_id = q.location_id OR l.location_id = d.parent_location_id
     JOIN users u ON u.id = l.user_id;
    """
    )

    # Drop `link_data_request_pending_event_notifications` table
    op.drop_table("link_data_request_pending_event_notifications")

    # Drop `link_data_source_pending_event_notification` table
    op.drop_table("link_data_source_pending_event_notification")

    # Drop `pending_event_notifications` table
    op.drop_table("pending_event_notifications")

    # Drop `enforce_data_request_event_type` trigger
    op.execute(
        "DROP TRIGGER IF EXISTS enforce_data_request_event_type ON public.link_data_request_pending_event_notifications"
    )

    # Drop `enforce_data_request_event_type` function
    op.execute("DROP FUNCTION IF EXISTS enforce_data_request_event_type()")

    # Drop `enforce_data_source_event_type` trigger
    op.execute(
        "DROP TRIGGER IF EXISTS enforce_data_source_event_type ON public.link_data_source_pending_event_notification"
    )

    # Drop `enforce_data_source_event_type` function
    op.execute("DROP FUNCTION IF EXISTS enforce_data_source_event_type()")

    # Drop `insert_pending_data_source_event_notification` trigger
    op.execute(
        "DROP TRIGGER IF EXISTS insert_pending_data_source_event_notification ON public.data_sources"
    )

    # Drop `insert_pending_data_source_event_notification` function
    op.execute(
        "DROP FUNCTION IF EXISTS insert_pending_data_source_event_notification()"
    )

    # Drop `insert_pending_data_request_event_notification` trigger
    op.execute(
        "DROP TRIGGER IF EXISTS insert_pending_data_request_event_notification ON public.data_requests"
    )

    # Drop `insert_pending_data_request_event_notification` function
    op.execute(
        "DROP FUNCTION IF EXISTS insert_pending_data_request_event_notification()"
    )

    # Drop 'enforce_unique_link_data_request_pending_event_notifications' trigger
    op.execute(
        "DROP TRIGGER IF EXISTS enforce_unique_link_data_request_pending_event_notifications ON public.link_data_request_pending_event_notifications"
    )

    # Drop 'enforce_unique_link_data_source_pending_event_notification' trigger
    op.execute(
        "DROP FUNCTION IF EXISTS enforce_unique_link_data_source_pending_event_notification()"
    )

    # Drop 'enforce_unique_link_data_source_pending_event_notification' trigger
    op.execute(
        "DROP TRIGGER IF EXISTS enforce_unique_link_data_source_pending_event_notification ON public.link_data_source_pending_event_notification"
    )

    # Drop 'enforce_unique_link_data_request_pending_event_notifications' function
    op.execute(
        "DROP FUNCTION IF EXISTS enforce_unique_link_data_request_pending_event_notifications()"
    )

    # Add columns to `user_notification_queue` table
    # region add_columns
    # email
    op.add_column(table_name="user_notification_queue", column=Column("email", sa.Text))
    # entity_id
    op.add_column(
        table_name="user_notification_queue", column=Column("entity_id", sa.Integer)
    )
    # entity_name
    op.add_column(
        table_name="user_notification_queue", column=Column("entity_name", sa.Text)
    )
    # entity_type
    op.add_column(
        table_name="user_notification_queue", column=Column("entity_type", sa.Text)
    )
    # event_timestamp
    op.add_column(
        table_name="user_notification_queue",
        column=Column("event_timestamp", sa.DateTime),
    )
    # endregion
