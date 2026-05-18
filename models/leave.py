from datetime import date

from sqlalchemy import String, Date, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"), nullable=False
    )
    leave_type: Mapped[str] = mapped_column(
        Enum("annual", "sick", "personal", "others", name="leave_type_enum"),
        nullable=False,
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=True, default=None)
    status: Mapped[str] = mapped_column(
        Enum("pending", "approved", "rejected", name="leave_status"),
        nullable=False,
        default="pending",
    )
    approved_by: Mapped[int | None] = mapped_column(
        ForeignKey("employees.id"), nullable=True
    )

    # Relationships
    employee: Mapped["Employee"] = relationship(
        back_populates="leave_requests", foreign_keys=[employee_id]
    )
    approver: Mapped["Employee | None"] = relationship(
        foreign_keys=[approved_by]
    )
