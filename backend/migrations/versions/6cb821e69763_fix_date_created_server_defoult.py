"""fix date_created server_default

Revision ID: 6cb821e69763
Revises: bac2244d3f93
Create Date: 2026-04-03 20:05:29.272719

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6cb821e69763'
down_revision: Union[str, Sequence[str], None] = 'bac2244d3f93'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Добавляем DEFAULT для date_created
    op.execute("""
        ALTER TABLE urls 
        ALTER COLUMN date_created 
        SET DEFAULT now()
    """)
    
    # Обновляем существующие NULL записи
    op.execute("""
        UPDATE urls 
        SET date_created = now() 
        WHERE date_created IS NULL
    """)
    
    # Убеждаемся что колонка NOT NULL
    op.alter_column('urls', 'date_created',
        existing_type=sa.DateTime(timezone=True),
        nullable=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Убираем DEFAULT
    op.execute("""
        ALTER TABLE urls 
        ALTER COLUMN date_created 
        DROP DEFAULT
    """)
    
    # Делаем колонку nullable
    op.alter_column('urls', 'date_created',
        existing_type=sa.DateTime(timezone=True),
        nullable=True
    )