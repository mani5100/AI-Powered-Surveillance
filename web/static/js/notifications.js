/**
 * Real-time Notification Handler using Server-Sent Events (SSE)
 * Manages EventSource connection and displays notifications
 */

class NotificationManager {
    constructor() {
        this.eventSource = null;
        this.notifications = [];
        this.maxNotifications = 50;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000; // 3 seconds
    }

    /**
     * Initialize SSE connection to notification stream
     */
    connect() {
        if (this.eventSource) {
            console.log('Already connected to notification stream');
            return;
        }

        console.log('Connecting to notification stream...');
        this.eventSource = new EventSource('/api/stream');

        // Connection opened
        this.eventSource.onopen = () => {
            console.log('✓ Connected to notification stream');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.updateConnectionStatus('connected');
        };

        // Receive messages
        this.eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            } catch (error) {
                console.error('Error parsing notification:', error);
            }
        };

        // Connection error
        this.eventSource.onerror = (error) => {
            console.error('SSE connection error:', error);
            this.isConnected = false;
            this.updateConnectionStatus('disconnected');
            
            // Close the connection
            this.eventSource.close();
            this.eventSource = null;

            // Attempt to reconnect
            if (this.reconnectAttempts < this.maxReconnectAttempts) {
                this.reconnectAttempts++;
                console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
                setTimeout(() => this.connect(), this.reconnectDelay);
            } else {
                console.error('Max reconnection attempts reached');
                this.updateConnectionStatus('failed');
            }
        };
    }

    /**
     * Disconnect from SSE stream
     */
    disconnect() {
        if (this.eventSource) {
            console.log('Disconnecting from notification stream');
            this.eventSource.close();
            this.eventSource = null;
            this.isConnected = false;
            this.updateConnectionStatus('disconnected');
        }
    }

    /**
     * Handle incoming SSE messages
     */
    handleMessage(data) {
        if (data.type === 'connected') {
            console.log('Stream connected:', data.message);
        } else if (data.type === 'notification') {
            this.handleNotification(data.data);
        }
    }

    /**
     * Process a new notification
     */
    handleNotification(notification) {
        console.log('New notification received:', notification);

        // Add to notifications array
        this.notifications.unshift(notification);
        
        // Trim to max size
        if (this.notifications.length > this.maxNotifications) {
            this.notifications = this.notifications.slice(0, this.maxNotifications);
        }

        // Display notification
        this.displayNotification(notification);

        // Play sound
        this.playNotificationSound();

        // Trigger custom event for other parts of the page
        this.triggerNotificationEvent(notification);
    }

    /**
     * Display notification in UI
     */
    displayNotification(notification) {
        const container = document.getElementById('notification-container');
        if (!container) {
            console.warn('Notification container not found');
            return;
        }

        // Create notification element
        const notifEl = this.createNotificationElement(notification);
        
        // Add to container
        container.appendChild(notifEl);

        // Show clear all button
        this.updateClearButtonVisibility();

        // Animate in
        setTimeout(() => {
            notifEl.classList.remove('translate-x-full', 'opacity-0');
            notifEl.classList.add('translate-x-0', 'opacity-100');
        }, 10);

        // Auto-dismiss after 10 seconds
        setTimeout(() => {
            this.dismissNotification(notifEl);
        }, 10000);
    }

    /**
     * Create notification DOM element
     */
    createNotificationElement(notification) {
        const div = document.createElement('div');
        div.className = 'notification-toast transform translate-x-full opacity-0 transition-all duration-300 bg-white rounded-lg shadow-xl border-l-4 border-red-500 p-4 mb-3 max-w-md';
        div.dataset.notificationId = notification.id;

        const objectBadges = notification.object_types.map(obj => 
            `<span class="px-2 py-1 bg-red-100 text-red-700 text-xs rounded-full font-semibold mr-1">${obj}</span>`
        ).join('');

        div.innerHTML = `
            <div class="flex items-start">
                <div class="flex-shrink-0">
                    <i class="fas fa-exclamation-triangle text-2xl text-red-500"></i>
                </div>
                <div class="ml-3 flex-grow">
                    <h4 class="text-sm font-bold text-gray-900 mb-1">
                        Security Alert
                        <span class="ml-2 px-2 py-1 bg-orange-500 text-white text-xs rounded-full">${notification.confidence_pct}%</span>
                    </h4>
                    <div class="mb-2">
                        ${objectBadges}
                    </div>
                    <p class="text-sm text-gray-700 mb-2">${notification.message}</p>
                    <div class="flex items-center justify-between">
                        <p class="text-xs text-gray-500">
                            <i class="fas fa-clock mr-1"></i>${notification.timestamp}
                        </p>
                        <a href="/events/${notification.event_id}" class="text-xs text-blue-600 hover:text-blue-800 font-semibold">
                            View Details →
                        </a>
                    </div>
                </div>
                <button onclick="notificationManager.dismissNotificationById('${notification.id}')" 
                    class="ml-3 text-gray-400 hover:text-gray-600">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        return div;
    }

    /**
     * Dismiss notification with animation
     */
    dismissNotification(element) {
        if (!element) return;

        element.classList.remove('translate-x-0', 'opacity-100');
        element.classList.add('translate-x-full', 'opacity-0');

        setTimeout(() => {
            element.remove();
            this.updateClearButtonVisibility();
        }, 300);
    }

    /**
     * Dismiss notification by ID
     */
    dismissNotificationById(notificationId) {
        const element = document.querySelector(`[data-notification-id="${notificationId}"]`);
        this.dismissNotification(element);
    }

    /**
     * Play notification sound
     */
    playNotificationSound() {
        // Create a simple beep using Web Audio API
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);

            oscillator.frequency.value = 800; // Hz
            oscillator.type = 'sine';

            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.5);
        } catch (error) {
            console.warn('Could not play notification sound:', error);
        }
    }

    /**
     * Trigger custom event for notification
     */
    triggerNotificationEvent(notification) {
        const event = new CustomEvent('newNotification', {
            detail: notification
        });
        window.dispatchEvent(event);
    }

    /**
     * Update connection status indicator
     */
    updateConnectionStatus(status) {
        const indicator = document.getElementById('sse-status-indicator');
        if (!indicator) return;

        indicator.className = 'w-2 h-2 rounded-full';
        
        switch(status) {
            case 'connected':
                indicator.classList.add('bg-green-500');
                indicator.title = 'Connected to real-time notifications';
                break;
            case 'disconnected':
                indicator.classList.add('bg-yellow-500');
                indicator.title = 'Disconnected - attempting to reconnect';
                break;
            case 'failed':
                indicator.classList.add('bg-red-500');
                indicator.title = 'Connection failed';
                break;
            default:
                indicator.classList.add('bg-gray-400');
        }
    }

    /**
     * Get all notifications
     */
    getNotifications() {
        return this.notifications;
    }

    /**
     * Clear all notifications from UI
     */
    clearAllNotifications() {
        const container = document.getElementById('notification-container');
        if (container) {
            // Get all notification elements
            const notifications = container.querySelectorAll('.notification-toast');
            
            // Dismiss each one with animation
            notifications.forEach((notif, index) => {
                setTimeout(() => {
                    this.dismissNotification(notif);
                }, index * 50); // Stagger the animations
            });
        }
        this.notifications = [];
        this.updateClearButtonVisibility();
    }

    /**
     * Update visibility of clear all button
     */
    updateClearButtonVisibility() {
        const header = document.getElementById('notification-header');
        const container = document.getElementById('notification-container');
        
        if (header && container) {
            const hasNotifications = container.querySelectorAll('.notification-toast').length > 0;
            if (hasNotifications) {
                header.classList.remove('hidden');
            } else {
                header.classList.add('hidden');
            }
        }
    }

    /**
     * Load initial notifications from API
     */
    async loadInitialNotifications() {
        try {
            const response = await fetch('/api/notifications');
            const data = await response.json();
            
            if (data.success && data.notifications.length > 0) {
                this.notifications = data.notifications;
                console.log(`Loaded ${data.notifications.length} initial notifications`);
            }
        } catch (error) {
            console.error('Error loading initial notifications:', error);
        }
    }
}

// Create global notification manager instance
const notificationManager = new NotificationManager();

// Auto-connect when page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing notification system...');
    // Don't load initial notifications on page refresh - only show new ones from SSE
    notificationManager.connect();
});

// Disconnect when page unloads
window.addEventListener('beforeunload', () => {
    notificationManager.disconnect();
});
