"""add ttl

Revision ID: 395e76d13c41
Revises: fcd3e113c9c9
Create Date: 2026-04-03 19:47:47.702147

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import INTEGER

# revision identifiers, used by Alembic.
revision: str = '395e76d13c41'
down_revision: Union[str, Sequence[str], None] = 'fcd3e113c9c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Добавляем новую колонку с типом DateTime
    op.add_column('urls', sa.Column('ttl_new', sa.DateTime(timezone=True), nullable=True))
    
    # 2. Преобразуем данные: интерпретируем INTEGER как количество дней от текущей даты
    #    Или как Unix timestamp - выбирайте нужный вариант
    
    # Вариант А: Если INTEGER хранил количество дней (например, 7, 30)
    op.execute("""
        UPDATE urls 
        SET ttl_new = CURRENT_TIMESTAMP + (ttl * INTERVAL '1 day')
        WHERE ttl IS NOT NULL
    """)
    
    # Вариант Б: Если INTEGER хранил Unix timestamp (секунды)
    # op.execute("""
    #     UPDATE urls 
    #     SET ttl_new = to_timestamp(ttl)
    #     WHERE ttl IS NOT NULL
    # """)
    
    # 3. Удаляем старую колонку
    op.drop_column('urls', 'ttl')
    
    # 4. Переименовываем новую колонку
    op.alter_column('urls', 'ttl_new', new_column_name='ttl')
    
    # 5. Создаём индекс
    op.create_index('idx_urls_ttl', 'urls', ['ttl'])


def downgrade() -> None:
    """Downgrade schema."""
    # 1. Удаляем индекс
    op.drop_index('idx_urls_ttl', table_name='urls')
    
    # 2. Добавляем обратно INTEGER колонку
    op.add_column('urls', sa.Column('ttl_int', INTEGER(), nullable=True))
    
    # 3. Преобразуем даты обратно в INTEGER (например, в дни)
    op.execute("""
        UPDATE urls 
        SET ttl_int = EXTRACT(DAY FROM (ttl - CURRENT_TIMESTAMP))
        WHERE ttl IS NOT NULL
    """)
    
    # 4. Удаляем DateTime колонку
    op.drop_column('urls', 'ttl')
    
    # 5. Переименовываем INTEGER колонку
    op.alter_column('urls', 'ttl_int', new_column_name='ttl')