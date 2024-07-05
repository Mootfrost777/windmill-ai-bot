from __future__ import annotations
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Uuid, DateTime, String, ForeignKey, func
from typing import List
from datetime import datetime
from uuid import UUID


class Base(DeclarativeBase):
    pass


class Task(Base):
    __tablename__ = 'tasks'
    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(BigInteger())
    image_uuid: Mapped[UUID] = mapped_column(Uuid)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    results: Mapped[List['Result']] = relationship(back_populates='task')


class Result(Base):
    __tablename__ = 'results'
    id: Mapped[int] = mapped_column(primary_key=True)

    result: Mapped[str] = mapped_column(String())

    task_id: Mapped[int] = mapped_column(ForeignKey('tasks.id'))
    task: Mapped['Task'] = relationship(back_populates='results')
