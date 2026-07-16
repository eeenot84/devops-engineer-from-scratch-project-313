import os
from datetime import datetime

from sqlalchemy import Column, DateTime, text
from sqlmodel import Field, SQLModel


class LinkBase(SQLModel):
    original_url: str
    short_name: str = Field(index=True, unique=True, max_length=255)


class Link(LinkBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        ),
    )


class LinkCreate(LinkBase):
    pass


class LinkUpdate(LinkBase):
    pass


class LinkRead(LinkBase):
    id: int
    short_url: str


def build_short_url(short_name: str) -> str:
    base = os.getenv("BASE_URL", "http://localhost:8080").rstrip("/")
    return f"{base}/r/{short_name}"


def link_to_read(link: Link) -> dict:
    return {
        "id": link.id,
        "original_url": link.original_url,
        "short_name": link.short_name,
        "short_url": build_short_url(link.short_name),
    }
