"""step 3 bootstrap revision

Revision ID: 0001_step3_bootstrap
Revises:
Create Date: 2026-03-27 00:00:00
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_step3_bootstrap"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """No-op bootstrap revision for Step 3."""
    pass


def downgrade() -> None:
    """No-op downgrade for Step 3."""
    pass