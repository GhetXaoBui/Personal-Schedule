"""
Database operations for Personal Schedule Assistant.
"""

import sqlite3
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from models import Event
import os


class Database:
    def __init__(self, db_path: str = "schedule.db"):
        """
        Initialize database connection.
        """
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Create tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_name TEXT NOT NULL,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME,
                    location TEXT,
                    reminder_minutes INTEGER DEFAULT 15,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def add_event(self, event: Event) -> int:
        """Add a new event to database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO events 
                (event_name, start_time, end_time, location, reminder_minutes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                event.event_name,
                event.start_time.isoformat(),
                event.end_time.isoformat() if event.end_time else None,
                event.location,
                event.reminder_minutes,
                event.created_at.isoformat(),
                event.updated_at.isoformat()
            ))
            
            event_id = cursor.lastrowid
            conn.commit()
            return event_id
    
    def update_event(self, event: Event) -> bool:
        """Update an existing event."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE events 
                SET event_name = ?, 
                    start_time = ?, 
                    end_time = ?, 
                    location = ?, 
                    reminder_minutes = ?,
                    updated_at = ?
                WHERE id = ?
            """, (
                event.event_name,
                event.start_time.isoformat(),
                event.end_time.isoformat() if event.end_time else None,
                event.location,
                event.reminder_minutes,
                datetime.now().isoformat(),
                event.id
            ))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_event(self, event_id: int) -> bool:
        """Delete an event by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def get_event(self, event_id: int) -> Optional[Event]:
        """Get a single event by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_event(row)
            return None
    
    def get_all_events(self) -> List[Event]:
        """Get all events sorted by start time."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM events ORDER BY start_time")
            rows = cursor.fetchall()
            
            return [self._row_to_event(row) for row in rows]
    
    def get_events_by_date(self, target_date: date) -> List[Event]:
        """Get events for a specific date."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            start_of_day = datetime.combine(target_date, datetime.min.time()).isoformat()
            end_of_day = datetime.combine(target_date, datetime.max.time()).isoformat()
            
            cursor.execute("""
                SELECT * FROM events 
                WHERE start_time >= ? AND start_time <= ?
                ORDER BY start_time
            """, (start_of_day, end_of_day))
            
            rows = cursor.fetchall()
            return [self._row_to_event(row) for row in rows]
    
    def get_events_by_week(self, target_date: date) -> List[Event]:
        """Get events for the week containing the target date."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Find Monday of the week
            monday = target_date - timedelta(days=target_date.weekday())
            sunday = monday + timedelta(days=6)
            
            start_of_week = datetime.combine(monday, datetime.min.time()).isoformat()
            end_of_week = datetime.combine(sunday, datetime.max.time()).isoformat()
            
            cursor.execute("""
                SELECT * FROM events 
                WHERE start_time >= ? AND start_time <= ?
                ORDER BY start_time
            """, (start_of_week, end_of_week))
            
            rows = cursor.fetchall()
            return [self._row_to_event(row) for row in rows]
    
    def get_events_by_month(self, year: int, month: int) -> List[Event]:
        """Get events for a specific month."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # First day of month
            start_date = date(year, month, 1)
            # Last day of month
            if month == 12:
                end_date = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(year, month + 1, 1) - timedelta(days=1)
            
            start_of_month = datetime.combine(start_date, datetime.min.time()).isoformat()
            end_of_month = datetime.combine(end_date, datetime.max.time()).isoformat()
            
            cursor.execute("""
                SELECT * FROM events 
                WHERE start_time >= ? AND start_time <= ?
                ORDER BY start_time
            """, (start_of_month, end_of_month))
            
            rows = cursor.fetchall()
            return [self._row_to_event(row) for row in rows]
    
    def search_events(self, keyword: str) -> List[Event]:
        """Search events by keyword in event_name or location."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            search_pattern = f"%{keyword}%"
            cursor.execute("""
                SELECT * FROM events 
                WHERE event_name LIKE ? OR location LIKE ?
                ORDER BY start_time
            """, (search_pattern, search_pattern))
            
            rows = cursor.fetchall()
            return [self._row_to_event(row) for row in rows]
    
    def _row_to_event(self, row) -> Event:
        """Convert database row to Event object."""
        return Event(
            id=row['id'],
            event_name=row['event_name'],
            start_time=datetime.fromisoformat(row['start_time']),
            end_time=datetime.fromisoformat(row['end_time']) if row['end_time'] else None,
            location=row['location'],
            reminder_minutes=row['reminder_minutes'],
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at'])
        )