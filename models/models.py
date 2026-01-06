"""
Модели данных для системы бронирования столов в ресторане.
Используются dataclasses для простоты и типобезопасности.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal
from uuid import UUID, uuid4


@dataclass
class User:
    """Класс пользователя системы бронирования."""
    
    name: str
    phone: str
    email: str
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Table:
    """Класс стола в ресторане."""
    
    number: int
    capacity: int
    location: Literal["window", "corner", "center"]
    id: UUID = field(default_factory=uuid4)
    is_available: bool = True


@dataclass
class Booking:
    """Класс бронирования стола."""
    
    user_id: UUID
    table_id: UUID
    booking_date: datetime
    guest_count: int
    id: UUID = field(default_factory=uuid4)
    duration_minutes: int = 120
    status: Literal["pending", "confirmed", "cancelled"] = "pending"
    special_requests: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

