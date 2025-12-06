"""
Data models for the Personal Schedule Assistant application.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
import json


@dataclass
class Event:
    id: Optional[int] = None
    event_name: str = ""
    start_time: datetime = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    reminder_minutes: int = 15 #default
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        """Initialize timestamps if not provided."""
        now = datetime.now()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now
        if self.start_time is None:
            # Default to current time + 1 hour
            self.start_time = now.replace(minute=0, second=0, microsecond=0)
            self.start_time = self.start_time.replace(hour=self.start_time.hour + 1)
        if self.end_time is None:
            # Default to start_time + 1 hour
            self.end_time = self.start_time.replace(hour=self.start_time.hour + 1)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Event to dictionary for database storage.
        """
        return {
            "id": self.id,
            "event_name": self.event_name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "location": self.location,
            "reminder_minutes": self.reminder_minutes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    def to_json_dict(self) -> Dict[str, Any]:
        """
        Convert to JSON serializable dictionary.
        """
        return {
            "event_name": self.event_name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "location": self.location,
            "reminder_minutes": self.reminder_minutes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """
        Create Event instance from dictionary.
        """
        return cls(
            id=data.get("id"),
            event_name=data["event_name"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None,
            location=data.get("location"),
            reminder_minutes=data.get("reminder_minutes", 15),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
    
    def get_time_display(self) -> str:
        """Get formatted time display."""
        return self.start_time.strftime("%H:%M")
    
    def get_date_display(self) -> str:
        """Get formatted date display."""
        return self.start_time.strftime("%d/%m/%Y")