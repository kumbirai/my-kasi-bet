"""
Admin action log domain model.

This module defines the AdminActionLog model for tracking all administrative
actions for audit and compliance purposes.
"""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.admin import AdminUser


class AdminActionLog(Base):
    """
    Admin action log model for audit trail.

    This model tracks all administrative actions performed by admin users,
    providing a complete audit trail for compliance and security purposes.

    Attributes:
        id: Primary key identifier
        admin_id: Foreign key to AdminUser who performed the action
        action_type: Type of action (e.g., "approve_deposit", "block_user")
        entity_type: Type of entity affected (e.g., "deposit", "user", "bet")
        entity_id: ID of the affected entity
        details: Additional context/details about the action (JSON string)
        created_at: Timestamp when action was logged
        admin: Relationship to AdminUser
    """

    __tablename__ = "admin_action_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(
        Integer,
        ForeignKey("admin_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action_type = Column(String(50), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)
    details = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    # Relationships
    admin = relationship("AdminUser", backref="action_logs")

    def __repr__(self) -> str:
        """String representation of AdminActionLog instance."""
        return (
            f"<AdminActionLog(id={self.id}, admin_id={self.admin_id}, "
            f"action={self.action_type}, entity={self.entity_type}:{self.entity_id})>"
        )
