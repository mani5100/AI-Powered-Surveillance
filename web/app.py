from flask import Flask, render_template, jsonify, request, send_from_directory, Response, stream_with_context
from flask_cors import CORS
from config import Config
from utils.event_manager import EventManager
from utils.notification_queue import notification_queue
from utils.system_controller import system_controller
from utils.config_manager import config_manager
from utils.stats_calculator import StatsCalculator
import json
import time
import uuid

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize EventManager
event_manager = EventManager(app.config['SUSPICIOUS_EVENTS_DIR'])

# API routes
@app.route('/api/events')
def api_events():
    """Get all events with optional filtering"""
    # Get query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    object_type = request.args.get('object_type')
    
    # Get all events
    events = event_manager.get_all_events()
    
    # Apply filters if provided
    if start_date or end_date or object_type:
        events = event_manager.filter_events(events, start_date, end_date, object_type)
    
    return jsonify({
        'success': True,
        'count': len(events),
        'events': events
    })

@app.route('/api/events/<event_id>')
def api_event_detail(event_id):
    """Get single event details"""
    event = event_manager.get_event_by_id(event_id)
    
    if event is None:
        return jsonify({
            'success': False,
            'error': 'Event not found'
        }), 404
    
    return jsonify({
        'success': True,
        'event': event
    })

@app.route('/api/status')
def api_status():
    """Get system status"""
    status = system_controller.get_status()
    
    return jsonify({
        'success': True,
        'status': 'running' if status['running'] else 'stopped',
        'message': status['message'],
        'pid': status.get('pid'),
        'uptime': status.get('uptime'),
        'uptime_seconds': status.get('uptime_seconds'),
        'memory_mb': status.get('memory_mb')
    })

@app.route('/api/stats')
def api_stats():
    """Get comprehensive statistics"""
    try:
        # Get all events
        events = event_manager.get_all_events()
        
        # Calculate statistics
        stats_calc = StatsCalculator(events)
        stats = stats_calc.calculate_all_statistics()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error calculating statistics: {str(e)}'
        }), 500

@app.route('/api/stream')
def api_stream():
    """Server-Sent Events endpoint for real-time notifications"""
    
    def event_stream():
        """Generator function that yields SSE messages"""
        # Generate unique listener ID
        listener_id = str(uuid.uuid4())
        notification_queue.add_listener(listener_id)
        
        # Start from current count - don't send old notifications
        last_notification_count = notification_queue.get_notification_count()
        
        try:
            # Send initial connection message
            yield f"data: {json.dumps({'type': 'connected', 'message': 'Connected to notification stream'})}\n\n"
            
            # Keep connection alive and send notifications
            while True:
                # Check for new notifications
                current_count = notification_queue.get_notification_count()
                
                if current_count > last_notification_count:
                    # Get new notifications
                    new_notifications = notification_queue.get_recent_notifications(
                        count=current_count - last_notification_count
                    )
                    
                    # Send each new notification
                    for notification in new_notifications:
                        event_data = json.dumps({
                            'type': 'notification',
                            'data': notification
                        })
                        yield f"data: {event_data}\n\n"
                    
                    last_notification_count = current_count
                
                # Send heartbeat every 30 seconds to keep connection alive
                yield f": heartbeat\n\n"
                
                # Sleep to prevent CPU spinning
                time.sleep(5)
                
        except GeneratorExit:
            # Client disconnected
            notification_queue.remove_listener(listener_id)
    
    return Response(
        stream_with_context(event_stream()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )

@app.route('/api/notifications')
def api_notifications():
    """Get recent notifications (for initial page load)"""
    notifications = notification_queue.get_recent_notifications(count=20)
    
    return jsonify({
        'success': True,
        'count': len(notifications),
        'notifications': notifications
    })

@app.route('/api/notifications/test', methods=['POST'])
def api_test_notification():
    """Test endpoint to manually trigger a notification (for development/testing)"""
    # Create a test notification
    test_event = {
        'id': f'test_{int(time.time())}',
        'object_types': ['test_object'],
        'confidence': 0.95,
        'timestamp_str': time.strftime('%Y-%m-%d %H:%M:%S'),
        'alert_message': 'This is a test notification'
    }
    
    notification = notification_queue.add_notification(test_event)
    
    return jsonify({
        'success': True,
        'message': 'Test notification sent',
        'notification': notification
    })

# System control API endpoints
@app.route('/api/control/start', methods=['POST'])
def api_control_start():
    """Start the detection system"""
    # Get webhook URL from config
    config = config_manager.get_config()
    webhook_url = config.get('webhook_url')
    
    # Start the system
    result = system_controller.start(webhook_url=webhook_url)
    
    return jsonify(result), 200 if result['success'] else 400

@app.route('/api/control/stop', methods=['POST'])
def api_control_stop():
    """Stop the detection system"""
    result = system_controller.stop()
    
    return jsonify(result), 200 if result['success'] else 400

# Configuration API endpoints
@app.route('/api/config', methods=['GET'])
def api_config_get():
    """Get current system configuration"""
    config = config_manager.get_config()
    
    return jsonify({
        'success': True,
        'config': config
    })

@app.route('/api/config', methods=['POST'])
def api_config_update():
    """Update system configuration"""
    try:
        # Get JSON data from request
        updates = request.get_json()
        
        if not updates:
            return jsonify({
                'success': False,
                'message': 'No configuration data provided'
            }), 400
        
        # Update configuration
        result = config_manager.update_config(updates)
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error processing request: {str(e)}'
        }), 400

# Webhook endpoint for detection system integration
@app.route('/api/webhook/new-event', methods=['POST'])
def api_webhook_new_event():
    """Receive webhook notifications from detection system when new events are saved"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Extract event information
        event_id = data.get('event_id')
        timestamp = data.get('timestamp')
        analysis = data.get('analysis', {})
        
        if not event_id:
            return jsonify({
                'success': False,
                'message': 'Missing event_id'
            }), 400
        
        # Load the full event from filesystem to get complete data
        event_data = event_manager.get_event_by_id(event_id)
        
        if event_data:
            # Add notification to queue with complete event data
            notification = notification_queue.add_notification(event_data)
            
            print(f"🔔 Webhook received for event {event_id}, notification added to queue")
            
            return jsonify({
                'success': True,
                'message': 'Event notification received and queued',
                'notification_id': notification['id']
            }), 200
        else:
            # Event file might not be fully written yet, create basic notification
            # from webhook data
            basic_event = {
                'id': event_id,
                'timestamp_str': timestamp,
                'alert_message': analysis.get('alert_message', 'New suspicious event detected'),
                'confidence': analysis.get('confidence', 0.0),
                'is_legitimate': analysis.get('is_legitimate', True)
            }
            
            notification = notification_queue.add_notification(basic_event)
            
            print(f"🔔 Webhook received for event {event_id} (file pending), notification added")
            
            return jsonify({
                'success': True,
                'message': 'Event notification received and queued (pending file)',
                'notification_id': notification['id']
            }), 200
        
    except Exception as e:
        print(f"❌ Error processing webhook: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error processing webhook: {str(e)}'
        }), 500

# Page routes
@app.route('/')
def index():
    """Homepage/Dashboard"""
    return render_template('index.html')

@app.route('/events')
def events():
    """Event gallery page"""
    return render_template('events.html')

@app.route('/events/<event_id>')
def event_detail(event_id):
    """Individual event detail page"""
    return render_template('event_detail.html', event_id=event_id)

@app.route('/statistics')
def statistics():
    """Statistics page"""
    return render_template('statistics.html')

@app.route('/controls')
def controls():
    """System control panel page"""
    return render_template('controls.html')

# Serve event images from suspicious_events folder
@app.route('/event-images/<path:filename>')
def event_images(filename):
    """Serve event images"""
    return send_from_directory(app.config['SUSPICIOUS_EVENTS_DIR'], filename)

if __name__ == '__main__':
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
