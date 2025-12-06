import json
from datetime import datetime
from typing import List, Dict, Any
from models import Event
from database import Database
import os


class FileHandler:
    @staticmethod
    def export_to_json(events: List[Event], filename: str) -> bool:
        try:
            # Create directory if it doesn't exist
            directory = os.path.dirname(filename)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # Prepare data for export
            data = {
                "export_date": datetime.now().isoformat(),
                "event_count": len(events),
                "events": [event.to_json_dict() for event in events]
            }
            
            # Write to file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Export error: {e}")
            return False
    
    @staticmethod
    def import_from_json(filename: str, db: Database) -> tuple:
        success_count = 0
        total_count = 0
        errors = []
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            events_data = data.get("events", [])
            total_count = len(events_data)
            
            for idx, event_data in enumerate(events_data):
                try:
                    # Create Event object from JSON data
                    event = Event.from_dict(event_data)
                    
                    # Add to database (this will generate new ID)
                    db.add_event(event)
                    success_count += 1
                    
                except Exception as e:
                    errors.append(f"Sự kiện {idx + 1}: {str(e)}")
            
            return success_count, total_count, errors
            
        except Exception as e:
            return 0, 0, [f"Lỗi file: {str(e)}"]