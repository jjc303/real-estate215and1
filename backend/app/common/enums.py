from __future__ import annotations


class HouseStatus:
    DRAFT = "draft"
    LISTED = "listed"
    OFFLINE = "offline"


class AppointmentStatus:
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class ContractStatus:
    PENDING = "pending"
    ACTIVE = "active"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    TERMINATED = "terminated"


class BillType:
    RENT = "rent"
    DEPOSIT = "deposit"
    OTHER = "other"


class BillStatus:
    UNPAID = "unpaid"
    PAID = "paid"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"
