"""merge heads

Revision ID: 90badd5ebb25
Revises: 7847b15c4247, fa4ee783ef4e
Create Date: 2025-01-23 18:06:09.738308

"""
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "90badd5ebb25"
down_revision: Union[str, None] = ("7847b15c4247", "fa4ee783ef4e")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
