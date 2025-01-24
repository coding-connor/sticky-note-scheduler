"""update_event_and_recurrence_schema

Revision ID: fa4ee783ef4e
Revises:
Create Date: 2024-03-19

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fa4ee783ef4e"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SQLite doesn't support ALTER TABLE RENAME directly, so we need to:
    # 1. Create new table
    # 2. Copy data
    # 3. Drop old table

    # Create new recurrence_rule table
    op.create_table(
        "recurrence_rule",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("days_of_week", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Copy data from recurrence to recurrence_rule
    op.execute("INSERT INTO recurrence_rule SELECT * FROM recurrence")

    # Drop old recurrence table
    op.drop_table("recurrence")

    # Create new event table with updated schema
    op.create_table(
        "event_new",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("start_datetime", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_datetime", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "timezone", sa.String(50), nullable=False, server_default="America/New_York"
        ),
        sa.Column("recurrence_rule_id", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(["recurrence_rule_id"], ["recurrence_rule.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # Copy data from event to event_new, converting datetime columns
    op.execute(
        """
        INSERT INTO event_new (
            id, name, start_datetime, end_datetime,
            timezone, recurrence_rule_id
        )
        SELECT
            id, name, start_time, end_time,
            'America/New_York', recurrence_id
        FROM event
    """
    )

    # Drop old event table
    op.drop_table("event")

    # Rename event_new to event
    op.rename_table("event_new", "event")


def downgrade() -> None:
    # Create old recurrence table
    op.create_table(
        "recurrence",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("days_of_week", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Copy data from recurrence_rule to recurrence
    op.execute("INSERT INTO recurrence SELECT * FROM recurrence_rule")

    # Drop new recurrence_rule table
    op.drop_table("recurrence_rule")

    # Create old event table
    op.create_table(
        "event_old",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("start_time", sa.DateTime(), nullable=False),
        sa.Column("end_time", sa.DateTime(), nullable=False),
        sa.Column("recurrence_id", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(["recurrence_id"], ["recurrence.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # Copy data back, converting datetime columns
    op.execute(
        """
        INSERT INTO event_old (
            id, name, start_time, end_time, recurrence_id
        )
        SELECT
            id, name, start_datetime, end_datetime, recurrence_rule_id
        FROM event
    """
    )

    # Drop new event table
    op.drop_table("event")

    # Rename event_old to event
    op.rename_table("event_old", "event")
