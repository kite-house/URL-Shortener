from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import String, DateTime, func
from datetime import datetime

class Base(AsyncAttrs, DeclarativeBase):
    pass

class Url(Base):
    __tablename__ = 'urls'

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True)
    long_url: Mapped[str] = mapped_column(String(700), unique=True)
    count_clicks: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(default = True, nullable=False)
    ttl: Mapped[datetime | None] = mapped_column(DateTime(timezone = True), nullable=True)
    date_created: Mapped[datetime] = mapped_column(DateTime(timezone = True), server_default = func.now(), nullable = False)
