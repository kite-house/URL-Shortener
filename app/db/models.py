from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import String
from datetime import datetime

class Base(AsyncAttrs, DeclarativeBase):
    pass

class Url(Base):
    __tablename__ = 'urls'

    id: Mapped[int] = mapped_column(primary_key=True)
    abbreviated_link: Mapped[str] = mapped_column(String(50), unique=True)
    address: Mapped[str] = mapped_column(String(300), unique=True)
    number_clicks: Mapped[int] = mapped_column(default=0)
    date_created: Mapped[datetime]
