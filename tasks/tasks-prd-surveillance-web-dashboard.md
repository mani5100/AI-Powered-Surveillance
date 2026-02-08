# Task List: Surveillance Web Dashboard

## Relevant Files

### Backend Files
- `web/app.py` - Main Flask application with API routes and SSE endpoint
- `web/utils/event_manager.py` - Utility to read/parse events from suspicious_events/ folder
- `web/utils/system_controller.py` - Manages starting/stopping main.py detection process
- `web/utils/config_manager.py` - Handles reading/writing system configuration
- `web/utils/notification_queue.py` - Thread-safe notification queue for SSE
- `web/utils/stats_calculator.py` - Comprehensive statistics computation for events

### Frontend Files
- `web/templates/base.html` - Base template with navigation and common elements
- `web/templates/index.html` - Homepage/dashboard with stats and recent events
- `web/templates/events.html` - Event gallery page with filters
- `web/templates/event_detail.html` - Individual event detail view
- `web/templates/statistics.html` - Statistics page with charts
- `web/templates/controls.html` - System control panel
- `web/static/css/styles.css` - Custom CSS (if needed beyond Tailwind)
- `web/static/js/main.js` - Common JavaScript utilities and navigation
- `web/static/js/dashboard.js` - Dashboard-specific JavaScript
- `web/static/js/events.js` - Event gallery filtering and modal logic
- `web/static/js/statistics.js` - Chart rendering using Chart.js
- `web/static/js/controls.js` - System control panel interactions
- `web/static/js/notifications.js` - Real-time SSE notification handler

### Existing Files to Modify
- `main.py` - Add webhook/callback to notify web server of new events
- `src/vision_analyzer.py` - May need to trigger event notification after saving

### Configuration
- `web/requirements.txt` - Flask and additional web dependencies
- `web/config.py` - Flask configuration settings

### Notes
- Web application will be in a new `web/` directory to keep it organized
- Flask will serve static files and templates from within `web/` folder
- No unit tests required for this FYP project (focus on functionality)
- Use Tailwind CSS via CDN (no build process needed)
- Chart.js via CDN for statistics visualization

## Tasks

- [x] 1.0 Set up Flask web application structure and basic routing
  - [x] 1.1 Create `web/` directory and subdirectories (templates, static/css, static/js, utils)
  - [x] 1.2 Create `web/requirements.txt` with Flask, Flask-CORS dependencies
  - [x] 1.3 Create `web/config.py` with Flask configuration (debug mode, secret key, paths)
  - [x] 1.4 Create `web/app.py` with basic Flask app initialization
  - [x] 1.5 Add basic route handlers for all pages (/, /events, /statistics, /controls)
  - [x] 1.6 Configure static file serving for images from suspicious_events/ folder
  - [x] 1.7 Test Flask app runs successfully with blank pages

- [x] 2.0 Implement backend API endpoints for event data and system status
  - [x] 2.1 Create `web/utils/event_manager.py` to read and parse event JSON files
  - [x] 2.2 Implement function to list all events from suspicious_events/ folder
  - [x] 2.3 Implement function to get single event details by ID/filename
  - [x] 2.4 Implement function to filter events by date range and object type
  - [x] 2.5 Add API endpoint GET /api/events to return all events as JSON
  - [x] 2.6 Add API endpoint GET /api/events/<event_id> for single event details
  - [x] 2.7 Add API endpoint GET /api/status to return system running status
  - [x] 2.8 Test all API endpoints return correct data

- [x] 3.0 Create frontend templates and layouts with Tailwind CSS
  - [x] 3.1 Create `web/templates/base.html` with Tailwind CSS CDN, navigation, and footer
  - [x] 3.2 Add responsive navigation bar with links to all pages
  - [x] 3.3 Create `web/templates/index.html` for dashboard/homepage
  - [x] 3.4 Add project overview section with title, description, and key features
  - [x] 3.5 Add system status card showing Running/Stopped with color indicators
  - [x] 3.6 Add statistics cards for today's events and total events count
  - [x] 3.7 Add recent events section displaying last 5-10 events in cards
  - [x] 3.8 Create `web/templates/events.html` with event grid layout
  - [x] 3.9 Add event cards showing thumbnail, timestamp, object type, confidence
  - [x] 3.10 Add filter controls for date range and object type
  - [x] 3.11 Create `web/templates/event_detail.html` for full event view
  - [x] 3.12 Display full-resolution image, complete analysis, confidence, timestamp
  - [x] 3.13 Create `web/templates/statistics.html` with chart containers
  - [x] 3.14 Create `web/templates/controls.html` with system control panel
  - [x] 3.15 Add start/stop buttons with appropriate styling
  - [x] 3.16 Add configuration form with confidence threshold slider and analysis interval input
  - [x] 3.17 Test all pages render correctly and are responsive

- [x] 4.0 Implement real-time notifications using Server-Sent Events (SSE)
  - [x] 4.1 Create `web/utils/notification_queue.py` to manage event notifications
  - [x] 4.2 Implement queue/list to store new event notifications
  - [x] 4.3 Add SSE endpoint GET /api/stream for real-time event updates
  - [x] 4.4 Create `web/static/js/notifications.js` for client-side SSE handling
  - [x] 4.5 Implement EventSource connection to /api/stream endpoint
  - [x] 4.6 Create notification UI component (toast/banner) in base.html
  - [x] 4.7 Display new event notifications with object type, timestamp, and link
  - [x] 4.8 Add browser notification sound/visual indicator
  - [x] 4.9 Implement notification history list for current session
  - [x] 4.10 Add dismiss functionality for individual notifications
  - [x] 4.11 Test notifications appear in real-time when events are added

- [x] 5.0 Build system control functionality (start/stop detection, configuration)
  - [x] 5.1 Create `web/utils/system_controller.py` for process management
  - [x] 5.2 Implement function to start main.py as subprocess with proper arguments
  - [x] 5.3 Implement function to stop running main.py process gracefully
  - [x] 5.4 Implement function to check if detection process is currently running
  - [x] 5.5 Create `web/utils/config_manager.py` for configuration management
  - [x] 5.6 Implement read/write functions for system configuration (JSON file)
  - [x] 5.7 Add API endpoint POST /api/control/start to start detection
  - [x] 5.8 Add API endpoint POST /api/control/stop to stop detection
  - [x] 5.9 Add API endpoint POST /api/config to update configuration
  - [x] 5.10 Add API endpoint GET /api/config to get current configuration
  - [x] 5.11 Create `web/static/js/controls.js` for control panel interactions
  - [x] 5.12 Implement AJAX calls to start/stop endpoints with error handling
  - [x] 5.13 Update UI to show loading state during start/stop operations
  - [x] 5.14 Display success/error messages after control actions
  - [x] 5.15 Test start/stop functionality works reliably

- [x] 6.0 Integrate web dashboard with existing detection system
  - [x] 6.1 Modify `main.py` to accept optional webhook URL parameter
  - [x] 6.2 Add function to send HTTP POST to webhook when new event is saved
  - [x] 6.3 Update `src/vision_analyzer.py` save_analysis to trigger webhook notification
  - [x] 6.4 Implement webhook receiver endpoint POST /api/webhook/new-event in Flask app
  - [x] 6.5 Add new event to notification queue when webhook is received
  - [x] 6.6 Test end-to-end: detection → event save → webhook → notification → browser
  - [x] 6.7 Handle edge cases (webhook failures, network issues)

- [x] 7.0 Add statistics and visualization features
  - [x] 7.1 Create `web/utils/stats_calculator.py` for statistics computation
  - [x] 7.2 Implement function to calculate total events count
  - [x] 7.3 Implement function to calculate events by object type (breakdown)
  - [x] 7.4 Implement function to calculate events over time (group by date)
  - [x] 7.5 Implement function to calculate average confidence score
  - [x] 7.6 Implement function to identify peak detection times/hours
  - [x] 7.7 Add API endpoint GET /api/stats to return all statistics
  - [x] 7.8 Create `web/static/js/statistics.js` for chart rendering
  - [x] 7.9 Include Chart.js library via CDN in statistics.html
  - [x] 7.10 Implement pie/bar chart for events by object type
  - [x] 7.11 Implement line/bar chart for events over time
  - [x] 7.12 Display total events, average confidence as stat cards
  - [x] 7.13 Add chart for peak detection times if sufficient data available
  - [x] 7.14 Create `web/static/js/dashboard.js` for homepage charts
  - [x] 7.15 Add mini chart/graph for events over time on dashboard
  - [x] 7.16 Test all charts render correctly with real data
