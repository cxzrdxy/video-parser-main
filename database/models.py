from datetime import datetime
from typing import Optional

from sqlalchemy import Column, JSON
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    __tablename__ = "users"

    user_id: Optional[int] = Field(default=None, primary_key=True)
    open_id: str = Field(index=True, unique=True, max_length=100)
    nickname: Optional[str] = Field(default=None, max_length=50)
    avatar_url: Optional[str] = Field(default=None, max_length=255)
    gender: str = Field(default="unknown", max_length=20)
    country: Optional[str] = Field(default=None, max_length=50)
    province: Optional[str] = Field(default=None, max_length=50)
    city: Optional[str] = Field(default=None, max_length=50)
    wechat_id: Optional[str] = Field(default=None, max_length=50)
    permissions: Optional[dict] = Field(default=None, sa_column=Column(JSON, nullable=True))
    video_records: Optional[dict] = Field(default=None, sa_column=Column(JSON, nullable=True))
    status: str = Field(default="active", max_length=20)
    points: int = Field(default=0, ge=0)
    total_download_count: int = Field(default=0, ge=0)
    total_parse_count: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class UserPointLog(SQLModel, table=True):
    __tablename__ = "user_point_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    open_id: str = Field(index=True, max_length=100)
    delta: int
    reason: str = Field(max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class DownloadRecord(SQLModel, table=True):
    __tablename__ = "download_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    open_id: str = Field(index=True, max_length=100)
    video_id: str = Field(index=True, max_length=80)
    platform: Optional[str] = Field(default=None, max_length=50)
    title: Optional[str] = Field(default=None, max_length=255)
    source_url: Optional[str] = Field(default=None, max_length=1024)
    download_url: Optional[str] = Field(default=None, max_length=1024)
    points_cost: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
