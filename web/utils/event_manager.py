import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class EventManager:
    """Manages reading and parsing suspicious event data"""
    
    def __init__(self, events_dir: Path):
        self.events_dir = events_dir
        
    def get_all_events(self) -> List[Dict]:
        """
        Get all events from suspicious_events folder
        Returns list of event dictionaries sorted by timestamp (newest first)
        """
        events = []
        
        if not self.events_dir.exists():
            return events
        
        # Find all JSON files in the events directory
        json_files = list(self.events_dir.glob('event_*.json'))
        
        for json_file in json_files:
            try:
                # Extract event ID from filename (e.g., event_20251025_001450.json -> 20251025_001450)
                event_id = json_file.stem.replace('event_', '')
                
                # Read JSON data
                with open(json_file, 'r') as f:
                    event_data = json.load(f)
                
                # Look for corresponding image file
                image_file = json_file.with_suffix('.jpg')
                has_image = image_file.exists()
                
                # Parse timestamp from event_id
                timestamp = self._parse_timestamp(event_id)
                
                # Extract object types from alert message (if available)
                object_types = self._extract_object_types(event_data.get('alert_message', ''))
                
                # Build event object
                event = {
                    'id': event_id,
                    'timestamp': timestamp,
                    'timestamp_str': self._format_timestamp(timestamp),
                    'is_legitimate': event_data.get('is_legitimate', False),
                    'alert_message': event_data.get('alert_message', ''),
                    'confidence': event_data.get('confidence', 0.0),
                    'confidence_pct': int(event_data.get('confidence', 0.0) * 100),
                    'has_image': has_image,
                    'image_filename': image_file.name if has_image else None,
                    'object_types': object_types
                }
                
                events.append(event)
                
            except Exception as e:
                print(f"Error reading event file {json_file}: {e}")
                continue
        
        # Sort by timestamp, newest first
        events.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return events
    
    def get_event_by_id(self, event_id: str) -> Optional[Dict]:
        """Get a single event by its ID"""
        json_file = self.events_dir / f'event_{event_id}.json'
        
        if not json_file.exists():
            return None
        
        try:
            with open(json_file, 'r') as f:
                event_data = json.load(f)
            
            image_file = json_file.with_suffix('.jpg')
            has_image = image_file.exists()
            timestamp = self._parse_timestamp(event_id)
            object_types = self._extract_object_types(event_data.get('alert_message', ''))
            
            return {
                'id': event_id,
                'timestamp': timestamp,
                'timestamp_str': self._format_timestamp(timestamp),
                'is_legitimate': event_data.get('is_legitimate', False),
                'alert_message': event_data.get('alert_message', ''),
                'confidence': event_data.get('confidence', 0.0),
                'confidence_pct': int(event_data.get('confidence', 0.0) * 100),
                'has_image': has_image,
                'image_filename': image_file.name if has_image else None,
                'object_types': object_types
            }
        except Exception as e:
            print(f"Error reading event {event_id}: {e}")
            return None
    
    def filter_events(self, events: List[Dict], start_date: Optional[str] = None, 
                     end_date: Optional[str] = None, object_type: Optional[str] = None) -> List[Dict]:
        """
        Filter events by date range and/or object type
        
        Args:
            events: List of event dictionaries
            start_date: Start date string in YYYY-MM-DD format (inclusive)
            end_date: End date string in YYYY-MM-DD format (inclusive)
            object_type: Object type to filter (e.g., 'cigarette', 'fire', 'knife', etc.)
        
        Returns:
            Filtered list of events
        """
        filtered = events.copy()
        
        # Filter by date range
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                filtered = [e for e in filtered if e['timestamp'].date() >= start_dt.date()]
            except ValueError:
                pass
        
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                filtered = [e for e in filtered if e['timestamp'].date() <= end_dt.date()]
            except ValueError:
                pass
        
        # Filter by object type
        if object_type and object_type.lower() != 'all':
            filtered = [
                e for e in filtered 
                if any(obj.lower() == object_type.lower() for obj in e['object_types'])
            ]
        
        return filtered
    
    def _parse_timestamp(self, event_id: str) -> datetime:
        """Parse timestamp from event ID (format: YYYYMMDD_HHMMSS)"""
        try:
            return datetime.strptime(event_id, '%Y%m%d_%H%M%S')
        except ValueError:
            # Return current time if parsing fails
            return datetime.now()
    
    def _format_timestamp(self, dt: datetime) -> str:
        """Format timestamp for display"""
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    
    def _extract_object_types(self, alert_message: str) -> List[str]:
        """Extract detected object types from alert message"""
        # Common suspicious objects to look for
        suspicious_objects = ['fire', 'cigarette', 'knife', 'gun', 'vape', 'weapon']
        
        found_objects = []
        message_lower = alert_message.lower()
        
        for obj in suspicious_objects:
            if obj in message_lower:
                found_objects.append(obj.capitalize())
        
        return found_objects if found_objects else ['Unknown']
