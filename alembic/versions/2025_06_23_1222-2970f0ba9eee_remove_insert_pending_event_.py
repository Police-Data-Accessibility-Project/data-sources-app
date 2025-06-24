"""Remove insert pending event notification triggers

Revision ID: 2970f0ba9eee
Revises: 4c60aece2682
Create Date: 2025-06-23 12:22:20.420656

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2970f0ba9eee"
down_revision: Union[str, None] = "4c60aece2682"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS insert_pending_data_source_event_notification ON data_sources"
    )
    op.execute(
        "DROP TRIGGER IF EXISTS insert_pending_data_request_event_notification ON data_requests"
    )
    op.execute(
        "DROP FUNCTION IF EXISTS insert_pending_data_source_event_notification()"
    )
    op.execute(
        "DROP FUNCTION IF EXISTS insert_pending_data_request_event_notification()"
    )


def downgrade() -> None:
    op.execute(
        """
        create function insert_pending_data_source_event_notification() returns trigger
    language plpgsql
    as
    $$
    
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
        $$;
    """
    )

    op.execute(
        """
    create trigger insert_pending_data_source_event_notification
        after insert or update
        on data_sources
        for each row
    execute procedure insert_pending_data_source_event_notification();
    """
    )

    op.execute(
        """
        create function insert_pending_data_request_event_notification() returns trigger
        language plpgsql
    as
    $$
    
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
        $$;
    """
    )

    op.execute(
        """
        create trigger insert_pending_data_request_event_notification
            after insert or update
            on data_requests
            for each row
        execute procedure insert_pending_data_request_event_notification();
    """
    )
