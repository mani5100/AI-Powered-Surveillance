"""
Notification Queue Manager for real-time event notifications
Manages a queue of notifications to be sent via Server-Sent Events (SSE)
"""
import time
from collections import deque
from datetime import datetime
from threading import Lock

class NotificationQueue:
    """Manages a thread-safe queue of event notifications"""
    
    def __init__(self, max_size=100):
        """
        Initialize notification queue
        
        Args:
            max_size: Maximum number of notifications to keep in memory
        """
        self.notifications = deque(maxlen=max_size)
        self.lock = Lock()
        self._listeners = []
    
    def add_notification(self, event_data):
        """
        Add a new notification to the queue
        
        Args:
            event_data: Dictionary containing event information
                Expected keys: id, object_types, confidence, timestamp_str, alert_message
        
        Returns:
            dict: The notification object that was added
        """
        with self.lock:
            notification = {
                'id': event_data.get('id'),
                'event_id': event_data.get('id'),
                'object_types': event_data.get('object_types', []),
                'confidence': event_data.get('confidence', 0.0),
                'confidence_pct': int(event_data.get('confidence', 0.0) * 100),
                'timestamp': event_data.get('timestamp_str', ''),
                'message': event_data.get('alert_message', 'New suspicious event detected'),
                'notified_at': datetime.now().isoformat(),
                'type': 'new_event'
            }
            
            self.notifications.append(notification)
            return notification
    
    def get_all_notifications(self):
        """
        Get all notifications currently in the queue
        
        Returns:
            list: All notifications
        """
        with self.lock:
            return list(self.notifications)
    
    def get_recent_notifications(self, count=10):
        """
        Get the most recent notifications
        
        Args:
            count: Number of recent notifications to return
        
        Returns:
            list: Most recent notifications (newest first)
        """
        with self.lock:
            all_notifs = list(self.notifications)
            # Return in reverse order (newest first)
            return all_notifs[-count:][::-1] if all_notifs else []
    
    def clear_notifications(self):
        """Clear all notifications from the queue"""
        with self.lock:
            self.notifications.clear()
    
    def get_notification_count(self):
        """
        Get the total number of notifications in the queue
        
        Returns:
            int: Number of notifications
        """
        with self.lock:
            return len(self.notifications)
    
    def add_listener(self, listener_id):
        """
        Register a new SSE listener
        
        Args:
            listener_id: Unique identifier for the listener
        """
        with self.lock:
            if listener_id not in self._listeners:
                self._listeners.append(listener_id)
    
    def remove_listener(self, listener_id):
        """
        Remove an SSE listener
        
        Args:
            listener_id: Unique identifier for the listener
        """
        with self.lock:
            if listener_id in self._listeners:
                self._listeners.remove(listener_id)
    
    def get_listener_count(self):
        """
        Get the number of active SSE listeners
        
        Returns:
            int: Number of active listeners
        """
        with self.lock:
            return len(self._listeners)


# Global notification queue instance
notification_queue = NotificationQueue()
