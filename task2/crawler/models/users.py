from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Numeric, Float, Date, Time, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, date, time
from decimal import Decimal
from typing import Optional, List
import uuid

from .base import Base


class Users(Base):
    """
    users 表模型
    
    自动生成时间: 2025-12-01 16:21:34
    """
    __tablename__ = "users"

    id = Column(String(32), primary_key=True, comment="用户ID,使用oauthID")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), comment="创建时间")
    deleted_at = Column(DateTime(timezone=True), comment="删除时间")
    name = Column(String(32), nullable=False, comment="用户名称")
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), comment="更新时间")

    def __repr__(self) -> str:
        return f"<Users({self.id})>"