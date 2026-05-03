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


class PaymentMethod:
    MOCK = "mock"
    OFFLINE = "offline"


class PaymentStatus:
    SUCCESS = "success"


class RepairStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CLOSED = "closed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    REOPENED = "reopened"


class ComplaintStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REJECTED = "rejected"


class NotificationStatus:
    UNREAD = "unread"
    READ = "read"


class NewsStatus:
    DRAFT = "draft"
    PUBLISHED = "published"


class OperationLogModule:
    REPAIR = "repair"
    COMPLAINT = "complaint"
    CONTRACT = "contract"
    BILL = "bill"
    PAYMENT = "payment"
    NEWS = "news"
