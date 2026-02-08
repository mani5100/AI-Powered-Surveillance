# Product Requirements Document: Surveillance Web Dashboard

## Introduction/Overview

This document outlines the requirements for developing a web-based dashboard for the YOLO-based security surveillance system. The dashboard will serve as the primary interface for the Final Year Project, allowing users to view the project overview, monitor suspicious events detected by the system, and access real-time alerts. The goal is to create a simple, professional web interface that demonstrates the project's capabilities during presentations while also providing practical real-world monitoring functionality.

## Goals

1. Provide a web-based interface to showcase the security surveillance system for FYP presentations
2. Display all detected suspicious events in an accessible, organized format
3. Enable real-time alert notifications when new suspicious events are detected
4. Allow users to control the detection system (start/stop, adjust settings)
5. Present a professional, modern UI that demonstrates technical competency

## User Stories

1. **As an FYP examiner**, I want to see a clear project overview on the homepage so that I can quickly understand what the system does and its capabilities.

2. **As a security monitor**, I want to view all suspicious events in a gallery format so that I can review past incidents at a glance.

3. **As a security monitor**, I want to see detailed information about each event (image, AI analysis, confidence score, timestamp) so that I can assess the legitimacy and severity of each incident.

4. **As a security monitor**, I want to receive real-time notifications when new suspicious events are detected so that I can respond quickly to potential threats.

5. **As a system administrator**, I want to start and stop the detection system from the web interface so that I don't need terminal access to the Raspberry Pi.

6. **As a system administrator**, I want to adjust detection settings (confidence threshold, analysis interval) so that I can optimize the system for different scenarios.

7. **As an FYP student**, I want statistics and charts displayed on the dashboard so that I can demonstrate the system's performance and detection patterns during my presentation.

## Functional Requirements

### Homepage/Dashboard
1. The system must display a homepage with project title, description, and key features
2. The system must show current system status (Running/Stopped/Error)
3. The system must display today's event count and total events count
4. The system must show a summary of recent events (last 5-10 events)
5. The system must include a statistics section showing:
   - Total events detected
   - Events by object type (Fire, cigarette, knife, gun, vape)
   - Events over time (simple chart/graph)

### Event Gallery
6. The system must display all suspicious events in a grid/card layout
7. Each event card must show:
   - Thumbnail image
   - Timestamp
   - Detected object type(s)
   - Confidence score
8. The system must allow users to click on an event to view full details
9. The event detail view must display:
   - Full-resolution image
   - Complete AI analysis message
   - Confidence percentage
   - Exact date and time
   - List of detected objects
10. The system must support filtering events by date range
11. The system must support filtering events by object type
12. The system must display events in reverse chronological order (newest first)

### Real-time Alerts
13. The system must push real-time notifications to the browser when new suspicious events are detected
14. Notifications must include:
    - Alert sound/visual indicator
    - Object type detected
    - Timestamp
    - Quick link to view event details
15. The system must maintain notification history for the current session
16. Users must be able to dismiss individual notifications

### System Controls
17. The system must provide a control panel to start the detection system
18. The system must provide a control panel to stop the detection system
19. The system must allow users to adjust the confidence threshold (slider: 0.1 - 0.9)
20. The system must allow users to adjust the analysis interval (input: 1-60 seconds)
21. The system must display the current configuration values
22. The system must apply configuration changes immediately when submitted
23. The system must show visual feedback when system status changes

### Statistics Page
24. The system must display total events count
25. The system must show breakdown of events by object type (pie/bar chart)
26. The system must show events over time (line/bar chart by day)
27. The system must calculate and display average confidence score
28. The system must show peak detection times (if sufficient data)

## Non-Goals (Out of Scope)

1. **User authentication/login system** - The dashboard will be accessible to anyone on the local network without login
2. **User management/roles** - No different permission levels or user accounts
3. **Multiple camera support** - System only handles single camera feed
4. **Mobile application** - Web interface only, though it should be responsive
5. **Email/SMS notifications** - Real-time browser notifications only
6. **Video playback** - Only still images from events, no video recordings
7. **Event editing/deletion** - Events are read-only once created
8. **External database** - Use existing file-based storage (suspicious_events/ folder)
9. **Cloud deployment** - Runs locally on Raspberry Pi only
10. **Advanced analytics** - Basic statistics only, no ML-based insights
11. **Export functionality** - No PDF reports or CSV exports in initial version
12. **Live camera feed** - No real-time video streaming, only event images

## Design Considerations

### UI/UX Requirements
- **Modern and Professional**: Use Tailwind CSS for styling to achieve a clean, contemporary look
- **Responsive Design**: Interface should work on desktop, tablet, and mobile browsers
- **Color Scheme**: 
  - Use professional colors (e.g., dark navy/slate for headers, white/light gray backgrounds)
  - Red/orange for alerts and high-confidence detections
  - Green for system running status
  - Gray for system stopped status
- **Typography**: Clean, readable fonts (e.g., Inter, Roboto, or system fonts)
- **Icons**: Use icon library (e.g., Heroicons, Font Awesome) for consistent visuals
- **Cards/Containers**: Use card-based layouts for events and statistics
- **Loading States**: Show loading spinners when fetching data
- **Empty States**: Display friendly messages when no events exist

### Layout Structure
- **Navigation**: Top navigation bar or sidebar with links to:
  - Dashboard/Home
  - Event Gallery
  - Statistics
  - System Controls
- **Footer**: Include project information, technologies used, student name/year

## Technical Considerations

### Backend
- **Framework**: Flask (Python) - Simple, integrates well with existing Python codebase
- **API Endpoints**: RESTful API for:
  - GET /api/events - List all events
  - GET /api/events/:id - Get specific event details
  - GET /api/stats - Get statistics
  - GET /api/status - Get system status
  - POST /api/control/start - Start detection
  - POST /api/control/stop - Stop detection
  - POST /api/config - Update configuration
- **Real-time Updates**: Server-Sent Events (SSE) or WebSockets for live notifications
- **Data Source**: Read from existing `suspicious_events/` directory (JSON files + images)
- **Process Management**: Use subprocess/multiprocessing to control main.py execution

### Frontend
- **HTML/CSS/JavaScript**: Modern vanilla JS or simple framework
- **Styling**: Tailwind CSS via CDN or build process
- **Charts**: Chart.js or similar lightweight library for visualizations
- **AJAX/Fetch**: For API calls without page reloads
- **EventSource**: For real-time notifications (SSE)

### Integration
- The web server must run alongside the detection system on the same Raspberry Pi
- The detection system (main.py) must be modifiable to trigger webhooks/notifications when events occur
- Shared access to suspicious_events/ folder for reading event data

### Deployment
- Runs on Raspberry Pi on local network only
- Flask development server acceptable for FYP demo
- Accessible via Pi's local IP address (e.g., http://192.168.1.X:5000)

## Success Metrics

1. **Functional Completeness**: All pages (Home, Events, Statistics, Controls) are accessible and functional
2. **Data Display**: All existing events in suspicious_events/ folder are correctly displayed
3. **Real-time Alerts**: New events trigger browser notifications within 5 seconds of detection
4. **System Control**: Start/stop functionality works reliably without errors
5. **Professional Appearance**: Dashboard looks polished and modern, suitable for FYP presentation
6. **Live Demo Success**: Can successfully demonstrate all features during FYP presentation without technical issues
7. **Performance**: Page loads within 2 seconds on local network
8. **Responsiveness**: Interface is usable on desktop, tablet, and mobile screens

## Open Questions

1. Should the system display a warning when detection is stopped to prevent users from thinking it's still monitoring?
2. What should happen to in-browser notifications when the user navigates away from the dashboard? (Keep in notification history?)
3. Should there be a confirmation dialog before starting/stopping the system?
4. What is the maximum number of events to display on the homepage recent events section? (5, 10, or configurable?)
5. Should statistics page include time-based filtering (e.g., last 7 days, last 30 days)?
6. Should there be a "clear all notifications" button in the notification panel?
7. What should the default chart time period be? (Last 7 days, 30 days, all time?)
