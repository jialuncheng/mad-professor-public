"""ORM models（Phase 0：建設用，核心模組尚未 import 此檔）。

SQLAlchemy 2.0 declarative。四表：User / Paper / Folder / Conversation。
檔案（PDF/MD/vectors/images）續留 output/ 檔案系統，DB 只存 metadata。
路徑不入庫，由 (owner_id, paper_uuid) 推導（見 db.paper_dir 註解）。
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import JSON


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user")
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    papers: Mapped[list["Paper"]] = relationship(
        back_populates="owner", passive_deletes=True
    )
    folders: Mapped[list["Folder"]] = relationship(
        back_populates="owner", passive_deletes=True
    )


class Folder(Base):
    __tablename__ = "folders"
    __table_args__ = (
        UniqueConstraint("owner_id", "parent_id", "name", name="uq_folder_sibling"),
        Index("ix_folders_owner_parent", "owner_id", "parent_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("folders.id", ondelete="CASCADE"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    owner: Mapped["User"] = relationship(back_populates="folders")
    parent: Mapped[Optional["Folder"]] = relationship(
        back_populates="children", remote_side="Folder.id"
    )
    children: Mapped[list["Folder"]] = relationship(
        back_populates="parent",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    papers: Mapped[list["Paper"]] = relationship(
        back_populates="folder", passive_deletes=True
    )


class Paper(Base):
    __tablename__ = "papers"
    __table_args__ = (
        UniqueConstraint("owner_id", "paper_uuid", name="uq_paper_owner_uuid"),
        Index("ix_papers_owner_status", "owner_id", "status"),
        Index("ix_papers_owner_folder", "owner_id", "folder_id"),
        Index("ix_papers_uuid", "paper_uuid"),
        Index("ix_papers_owner_last_opened", "owner_id", "last_opened_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    paper_uuid: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    translated_title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    domain: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    doc_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    folder_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("folders.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="processing"
    )
    progress_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    progress_stage: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    page_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
    ready_for_reading_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    ready_for_chat_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    last_opened_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    # Phase 4.5：metadata schema v2（JSON 字串；SQLite 用 Text + 應用層 json）
    # 屬性名不可叫 metadata（SQLAlchemy DeclarativeBase 保留字）
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Phase 4.7a：使用者上傳的原始檔名（中文/空格/特殊字元原樣保留）；
    # paper_uuid 經 sanitize 會損失資訊，此欄供下載真檔名 / 追溯 / debug。
    # nullable：4.7a 之前的舊資料無此欄。
    original_filename: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )

    owner: Mapped["User"] = relationship(back_populates="papers")
    folder: Mapped[Optional["Folder"]] = relationship(back_populates="papers")
    conversations: Mapped[list["Conversation"]] = relationship(
        back_populates="paper",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Conversation.id",
    )


class Conversation(Base):
    __tablename__ = "conversations"
    __table_args__ = (
        Index("ix_conversations_paper_id", "paper_id", "id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    paper_id: Mapped[int] = mapped_column(
        ForeignKey("papers.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    session_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # Web 來源（grounding）；舊 chat_history.json 遷入時為 NULL
    grounding_sources: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    paper: Mapped["Paper"] = relationship(back_populates="conversations")
    user: Mapped["User"] = relationship()
