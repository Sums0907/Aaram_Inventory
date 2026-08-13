from enum import Enum
from typing import Optional
from datetime import date
from src.foundation.validation.base import BaseSchema

class ShopDeckStatus(str, Enum):
    # Active Statuses
    PRINT = "PRINT"
    PACK = "PACK"
    IN_TRANSIT = "IN-TRANSIT"
    HANDOVER = "HANDOVER"
    RTO_ACKNOWLEDGED = "RTO_ACKNOWLEDGED"
    RTO_INITIATED = "RTO_INITIATED"
    DELIVERED = "DELIVERED"
    
    # Terminal Statuses
    RTO_DELIVERED = "RTO_DELIVERED"
    RETURNED = "RETURNED"
    CANCELLED_INITIATED = "CANCELLED INITIATED"
    EXPIRED_AWB = "EXPIRED AWB"
    LOST = "LOST"
    
    # Other Statuses
    PENDING = "PENDING"

class LifecycleState(str, Enum):
    ACTIVE = "ACTIVE"
    TERMINAL = "TERMINAL"
    UNKNOWN_STATUS = "UNKNOWN_STATUS"

class TransitionType(str, Enum):
    INITIAL_OBSERVATION = "INITIAL_OBSERVATION"
    STATE_TRANSITION = "STATE_TRANSITION"

class DynamicReportWindowResponse(BaseSchema):
    required_report_start_date: Optional[date]
    required_report_end_date: Optional[date]
    oldest_active_order_date: Optional[date]
    oldest_active_order_id: Optional[str]
    active_order_count: int
    reason: str
