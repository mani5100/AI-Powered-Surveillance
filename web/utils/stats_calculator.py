"""
Statistics Calculator for event analysis
Computes various statistics from suspicious event data
"""
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import List, Dict, Any


class StatsCalculator:
    """Calculate statistics from event data"""
    
    def __init__(self, events: List[Dict[str, Any]]):
        """
        Initialize with event data
        
        Args:
            events: List of event dictionaries from EventManager
        """
        self.events = events
    
    def calculate_total_events(self) -> int:
        """
        Calculate total number of events
        
        Returns:
            Total event count
        """
        return len(self.events)
    
    def calculate_events_by_type(self) -> Dict[str, Dict[str, Any]]:
        """
        Calculate event breakdown by object type
        
        Returns:
            Dictionary with object types as keys and stats as values
            {
                'cigarette': {'count': 10, 'percentage': 50.0, 'avg_confidence': 0.85},
                'knife': {'count': 5, 'percentage': 25.0, 'avg_confidence': 0.92},
                ...
            }
        """
        total = len(self.events)
        if total == 0:
            return {}
        
        # Count occurrences and collect confidences
        type_data = defaultdict(lambda: {'count': 0, 'confidences': []})
        
        for event in self.events:
            object_types = event.get('object_types', [])
            confidence = event.get('confidence', 0.0)
            
            for obj_type in object_types:
                type_data[obj_type]['count'] += 1
                type_data[obj_type]['confidences'].append(confidence)
        
        # Calculate percentages and average confidences
        result = {}
        for obj_type, data in type_data.items():
            count = data['count']
            confidences = data['confidences']
            
            result[obj_type] = {
                'count': count,
                'percentage': round((count / total) * 100, 1),
                'avg_confidence': round(sum(confidences) / len(confidences), 3) if confidences else 0.0
            }
        
        # Sort by count descending
        result = dict(sorted(result.items(), key=lambda x: x[1]['count'], reverse=True))
        
        return result
    
    def calculate_events_over_time(self, group_by: str = 'date') -> Dict[str, int]:
        """
        Calculate events grouped by time period
        
        Args:
            group_by: Time grouping - 'date', 'hour', 'day_of_week'
        
        Returns:
            Dictionary with time periods as keys and counts as values
        """
        time_counts = defaultdict(int)
        
        for event in self.events:
            # Try timestamp_str first, then timestamp
            timestamp = event.get('timestamp_str') or event.get('timestamp')
            if not timestamp:
                continue
            
            try:
                # Parse timestamp_str format: "2025-11-07 22:31:28"
                if ' ' in str(timestamp) and '-' in str(timestamp):
                    dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                else:
                    # Try ISO format
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                
                if group_by == 'date':
                    key = dt.strftime('%Y-%m-%d')
                elif group_by == 'hour':
                    key = f"{dt.hour:02d}:00"
                elif group_by == 'day_of_week':
                    key = dt.strftime('%A')
                else:
                    key = dt.strftime('%Y-%m-%d')
                
                time_counts[key] += 1
                
            except (ValueError, AttributeError):
                continue
        
        # Sort by key
        if group_by == 'date':
            time_counts = dict(sorted(time_counts.items()))
        elif group_by == 'hour':
            # Sort by hour numerically
            time_counts = dict(sorted(time_counts.items(), key=lambda x: int(x[0].split(':')[0])))
        
        return dict(time_counts)
    
    def calculate_average_confidence(self) -> float:
        """
        Calculate average confidence score across all events
        
        Returns:
            Average confidence (0.0-1.0)
        """
        if not self.events:
            return 0.0
        
        confidences = [event.get('confidence', 0.0) for event in self.events]
        valid_confidences = [c for c in confidences if c > 0]
        
        if not valid_confidences:
            return 0.0
        
        return round(sum(valid_confidences) / len(valid_confidences), 3)
    
    def identify_peak_detection_times(self) -> Dict[str, Any]:
        """
        Identify peak detection times (hours with most events)
        
        Returns:
            Dictionary with peak time analysis
            {
                'peak_hour': '14:00',
                'peak_count': 15,
                'hourly_distribution': {'00:00': 2, '01:00': 1, ...}
            }
        """
        hourly = self.calculate_events_over_time(group_by='hour')
        
        if not hourly:
            return {
                'peak_hour': None,
                'peak_count': 0,
                'hourly_distribution': {}
            }
        
        # Find peak hour
        peak_hour_str, peak_count = max(hourly.items(), key=lambda x: x[1])
        peak_hour_int = int(peak_hour_str.split(':')[0])
        
        return {
            'peak_hour': peak_hour_int,
            'peak_count': peak_count,
            'hourly_distribution': hourly
        }
    
    def calculate_today_events(self) -> int:
        """
        Calculate number of events from today
        
        Returns:
            Count of today's events
        """
        today = datetime.now().date()
        count = 0
        
        for event in self.events:
            # Try timestamp_str first, then timestamp
            timestamp = event.get('timestamp_str') or event.get('timestamp')
            if not timestamp:
                continue
            
            try:
                # Parse timestamp_str format: "2025-11-07 22:31:28"
                if ' ' in str(timestamp) and '-' in str(timestamp):
                    dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                else:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    
                if dt.date() == today:
                    count += 1
            except (ValueError, AttributeError):
                continue
        
        return count
    
    def calculate_this_week_events(self) -> int:
        """
        Calculate number of events from this week
        
        Returns:
            Count of this week's events
        """
        now = datetime.now()
        week_start = now - timedelta(days=now.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        count = 0
        for event in self.events:
            # Try timestamp_str first, then timestamp
            timestamp = event.get('timestamp_str') or event.get('timestamp')
            if not timestamp:
                continue
            
            try:
                # Parse timestamp_str format: "2025-11-07 22:31:28"
                if ' ' in str(timestamp) and '-' in str(timestamp):
                    dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                else:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    
                if dt >= week_start:
                    count += 1
            except (ValueError, AttributeError):
                continue
        
        return count
    
    def get_top_threat(self) -> Dict[str, Any]:
        """
        Get the most frequently detected threat type
        
        Returns:
            Dictionary with top threat info
            {'type': 'cigarette', 'count': 15, 'percentage': 45.5}
        """
        by_type = self.calculate_events_by_type()
        
        if not by_type:
            return {'type': 'None', 'count': 0, 'percentage': 0.0}
        
        # Already sorted by count, get first
        top_type = next(iter(by_type.items()))
        
        return {
            'type': top_type[0],
            'count': top_type[1]['count'],
            'percentage': top_type[1]['percentage']
        }
    
    def calculate_all_statistics(self) -> Dict[str, Any]:
        """
        Calculate all statistics in one call
        
        Returns:
            Comprehensive statistics dictionary
        """
        return {
            'total_events': self.calculate_total_events(),
            'today_events': self.calculate_today_events(),
            'this_week_events': self.calculate_this_week_events(),
            'average_confidence': self.calculate_average_confidence(),
            'events_by_type': self.calculate_events_by_type(),
            'events_by_date': self.calculate_events_over_time(group_by='date'),
            'events_by_hour': self.calculate_events_over_time(group_by='hour'),
            'peak_times': self.identify_peak_detection_times(),
            'top_threat': self.get_top_threat()
        }
