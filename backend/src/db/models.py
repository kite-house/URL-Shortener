from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import String
from datetime import datetime

class Base(AsyncAttrs, DeclarativeBase):
    pass

class Url(Base):
    __tablename__ = 'urls'

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True)
    long_url: Mapped[str] = mapped_column(String(700), unique=True)
    count_clicks: Mapped[int] = mapped_column(default=0)
    date_created: Mapped[datetime]
