from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime


user_role = Table(
    'user_role',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), comment="用户ID"),
    Column('role_id', Integer, ForeignKey('roles.id'), comment="角色ID")
)


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"comment": "用户表"}

    id = Column(Integer, primary_key=True, index=True, comment="用户ID")
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    email = Column(String(100), unique=True, index=True, comment="邮箱")
    hashed_password = Column(String(255), nullable=False, comment="密码哈希")
    full_name = Column(String(100), comment="全名")
    is_active = Column(Boolean, default=True, comment="是否启用")
    is_superuser = Column(Boolean, default=False, comment="是否超级管理员")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    roles = relationship("Role", secondary=user_role, back_populates="users")


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = {"comment": "角色表"}

    id = Column(Integer, primary_key=True, index=True, comment="角色ID")
    name = Column(String(50), unique=True, nullable=False, comment="角色名称")
    description = Column(String(255), comment="角色描述")
    permissions = Column(String(1000), comment="权限列表")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    users = relationship("User", secondary=user_role, back_populates="roles")
