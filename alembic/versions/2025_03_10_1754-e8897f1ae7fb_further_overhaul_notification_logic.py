"""Further overhaul notification logic

Revision ID: e8897f1ae7fb
Revises: e628c1173d56
Create Date: 2025-03-10 17:54:55.300192

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e8897f1ae7fb"
down_revision: Union[str, None] = "e628c1173d56"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

data_request_event_enum = sa.Enum(
    "Request Ready to Start", "Request Complete", name="event_type_data_request"
)
data_source_event_enum = sa.Enum("Data Source Approved", name="event_type_data_source")


def upgrade() -> None:

    op.drop_table("link_data_request_pending_event_notifications")
    op.drop_table("link_data_source_pending_event_notification")
    op.drop_table("user_notification_queue")
    op.drop_table("pending_event_notifications")
    op.execute("DROP FUNCTION IF EXISTS enforce_data_request_event_type()")
    op.execute(
        "DROP FUNCTION IF EXISTS enforce_unique_link_data_source_pending_event_notification()"
    )
    op.execute(
        "DROP FUNCTION IF EXISTS enforce_unique_link_data_request_pending_event_notifications()"
    )
    op.execute("DROP FUNCTION IF EXISTS enforce_data_source_event_type()")
    op.create_table(
        "data_request_pending_event_notification",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("data_request_id", sa.Integer(), nullable=False),
        sa.Column(
            "event_type",
            data_request_event_enum,
            nullable=False,
        ),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.ForeignKeyConstraint(
            ["data_request_id"],
            ["data_requests.id"],
            name="data_request_pending_event_notifications_dr_id_fkey",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "data_request_id", "event_type", name="unique_data_request_event_type"
        ),
    )
    op.create_table(
        "data_source_pending_event_notification",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("data_source_id", sa.Integer(), nullable=False),
        sa.Column(
            "event_type",
            data_source_event_enum,
            nullable=False,
        ),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.ForeignKeyConstraint(
            ["data_source_id"],
            ["data_sources.id"],
            name="data_source_pending_event_notification_ds_id_fkey",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "data_source_id", "event_type", name="unique_data_source_event_type"
        ),
    )
    op.create_table(
        "data_request_user_notification_queue",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "sent_at", sa.DateTime(), nullable=True, server_default=sa.func.now()
        ),
        sa.ForeignKeyConstraint(
            ["event_id"],
            ["data_request_pending_event_notification.id"],
            name="data_request_user_notification_queue_event_id_fkey",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="data_request_user_notification_queue_user_id_fkey",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "event_id", "user_id", name="unique_data_request_user_notification_queue"
        ),
    )
    op.create_table(
        "data_source_user_notification_queue",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "sent_at", sa.DateTime(), nullable=True, server_default=sa.func.now()
        ),
        sa.ForeignKeyConstraint(
            ["event_id"],
            ["data_source_pending_event_notification.id"],
            name="data_source_user_notification_queue_event_id_fkey",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="data_request_user_notification_queue_user_id_fkey",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "event_id", "user_id", name="unique_data_source_user_notification_queue"
        ),
    )

    op.execute(
        """
    CREATE OR REPLACE FUNCTION insert_pending_data_source_event_notification()
    RETURNS TRIGGER AS $$

    BEGIN
        IF (
            TG_OP = 'INSERT' AND NEW.approval_status = 'approved'::approval_status)
            OR (
                TG_OP = 'UPDATE' 
                AND NEW.approval_status != OLD.approval_status 
                AND NEW.approval_status = 'approved'::approval_status
        ) THEN
            INSERT INTO data_source_pending_event_notification (event_type, data_source_id)
            VALUES ('Data Source Approved'::event_type_data_source, NEW.id);
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    """
    )

    op.execute(
        """
    CREATE OR REPLACE FUNCTION insert_pending_data_request_event_notification()
    RETURNS TRIGGER AS $$

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
            INSERT INTO data_request_pending_event_notification (event_type, data_request_id)
            VALUES (
                CASE
                    WHEN NEW.request_status = 'Ready to start'::request_status THEN 'Request Ready to Start'::event_type_data_request
                    WHEN NEW.request_status = 'Complete'::request_status THEN 'Request Complete'::event_type_data_request
                END,
                NEW.id
            );

        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    """
    )


def downgrade() -> None:

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

    op.create_table(
        "user_notification_queue",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("pen_id", sa.Integer(), nullable=False),
        sa.Column(
            "sent_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_unique_constraint(
        "user_notification_queue_user_id_pen_id_key",
        "user_notification_queue",
        ["user_id", "pen_id"],
    )
    op.create_foreign_key(
        "user_notification_queue_pen_id_fkey",
        "user_notification_queue",
        "pending_event_notifications",
        ["pen_id"],
        ["id"],
    )

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

    op.drop_table("data_request_user_notification_queue")
    op.drop_table("data_source_user_notification_queue")

    op.drop_table("data_request_pending_event_notification")
    op.drop_table("data_source_pending_event_notification")

    data_request_event_enum.drop(op.get_bind())
    data_source_event_enum.drop(op.get_bind())

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
