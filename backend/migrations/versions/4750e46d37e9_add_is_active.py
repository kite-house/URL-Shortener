"""add is_active

Revision ID: 4750e46d37e9
Revises: 6cb821e69763
Create Date: 2026-04-03 20:54:05.222824

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4750e46d37e9'
down_revision: Union[str, Sequence[str], None] = '6cb821e69763'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Добавляем колонку с возможностью NULL
    op.add_column('urls', sa.Column('is_active', sa.Boolean(), nullable=True))
    
    # 2. Для существующих записей ставим TRUE (активны)
    op.execute("UPDATE urls SET is_active = TRUE WHERE is_active IS NULL")
    
    # 3. Теперь делаем NOT NULL и DEFAULT
    op.alter_column('urls', 'is_active',
        existing_type=sa.Boolean(),
        nullable=False,
        server_default=sa.text('true')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('urls', 'is_active')