/**
 * System Controls JavaScript
 * Handles system control panel interactions, AJAX calls, and UI updates
 */

// Configuration state
let currentConfig = {};

/**
 * Initialize controls page
 */
document.addEventListener('DOMContentLoaded', function() {
    refreshStatus();
    loadConfiguration();
    
    // Set up auto-refresh for status (every 5 seconds)
    setInterval(refreshStatus, 5000);
});

/**
 * Update confidence threshold display
 */
function updateConfidenceDisplay(value) {
    document.getElementById('confidence-display').textContent = parseFloat(value).toFixed(2);
}

/**
 * Fetch and display system status
 */
async function refreshStatus() {
    try {
        const response = await fetch('/api/status');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        const indicator = document.getElementById('status-indicator');
        const statusText = document.getElementById('status-text');
        const statusMessage = document.getElementById('status-message');
        const statusDisplay = document.getElementById('status-display');
        const startBtn = document.getElementById('start-btn');
        const stopBtn = document.getElementById('stop-btn');
        
        if (data.status === 'running') {
            // System is running
            indicator.className = 'w-6 h-6 rounded-full bg-green-500';
            statusText.textContent = 'Running';
            statusText.className = 'text-2xl font-bold text-green-600';
            
            // Add uptime and memory info if available
            let message = 'Detection system is active';
            if (data.uptime) {
                message += ` (Uptime: ${data.uptime})`;
            }
            if (data.memory_mb) {
                message += ` • Memory: ${data.memory_mb} MB`;
            }
            
            statusMessage.textContent = message;
            statusDisplay.className = 'mb-6 p-4 rounded-lg bg-green-50 border border-green-200';
            
            // Enable/disable buttons
            startBtn.disabled = true;
            stopBtn.disabled = false;
        } else {
            // System is stopped
            indicator.className = 'w-6 h-6 rounded-full bg-gray-400';
            statusText.textContent = 'Stopped';
            statusText.className = 'text-2xl font-bold text-gray-600';
            statusMessage.textContent = 'Detection system is stopped';
            statusDisplay.className = 'mb-6 p-4 rounded-lg bg-gray-50 border border-gray-200';
            
            // Enable/disable buttons
            startBtn.disabled = false;
            stopBtn.disabled = true;
        }
    } catch (error) {
        console.error('Error fetching status:', error);
        
        // Show error state
        const indicator = document.getElementById('status-indicator');
        const statusText = document.getElementById('status-text');
        const statusMessage = document.getElementById('status-message');
        
        indicator.className = 'w-6 h-6 rounded-full bg-red-400';
        statusText.textContent = 'Error';
        statusText.className = 'text-2xl font-bold text-red-600';
        statusMessage.textContent = 'Failed to fetch system status';
        
        showToast('Error', 'Failed to fetch system status', 'error');
    }
}

/**
 * Start detection system
 */
async function startSystem() {
    const startBtn = document.getElementById('start-btn');
    const originalHtml = startBtn.innerHTML;
    
    // Show loading state
    startBtn.disabled = true;
    startBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Starting...';
    
    try {
        const response = await fetch('/api/control/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Success', data.message || 'Detection system started successfully', 'success');
            
            // Refresh status after a short delay
            setTimeout(refreshStatus, 1000);
        } else {
            showToast('Error', data.message || 'Failed to start detection system', 'error');
            
            // Re-enable button
            startBtn.disabled = false;
            startBtn.innerHTML = originalHtml;
        }
    } catch (error) {
        console.error('Error starting system:', error);
        showToast('Error', 'Failed to communicate with server', 'error');
        
        // Re-enable button
        startBtn.disabled = false;
        startBtn.innerHTML = originalHtml;
    }
}

/**
 * Stop detection system
 */
async function stopSystem() {
    const stopBtn = document.getElementById('stop-btn');
    const originalHtml = stopBtn.innerHTML;
    
    // Show loading state
    stopBtn.disabled = true;
    stopBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Stopping...';
    
    try {
        const response = await fetch('/api/control/stop', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Success', data.message || 'Detection system stopped successfully', 'success');
            
            // Refresh status after a short delay
            setTimeout(refreshStatus, 1000);
        } else {
            showToast('Error', data.message || 'Failed to stop detection system', 'error');
            
            // Re-enable button
            stopBtn.disabled = false;
            stopBtn.innerHTML = originalHtml;
        }
    } catch (error) {
        console.error('Error stopping system:', error);
        showToast('Error', 'Failed to communicate with server', 'error');
        
        // Re-enable button
        stopBtn.disabled = false;
        stopBtn.innerHTML = originalHtml;
    }
}

/**
 * Load current configuration from server
 */
async function loadConfiguration() {
    try {
        const response = await fetch('/api/config');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success && data.config) {
            currentConfig = data.config;
            
            // Update form fields
            const confidenceSlider = document.getElementById('confidence-slider');
            const analysisInterval = document.getElementById('analysis-interval');
            const resolution = document.getElementById('resolution');
            const audioAlerts = document.getElementById('audio-alerts');
            const saveImages = document.getElementById('save-images');
            
            if (confidenceSlider) {
                confidenceSlider.value = currentConfig.confidence_threshold || 0.2;
                updateConfidenceDisplay(confidenceSlider.value);
            }
            
            if (analysisInterval) {
                analysisInterval.value = currentConfig.analysis_interval || 10;
            }
            
            if (resolution) {
                resolution.value = currentConfig.resolution || '1640x1232';
            }
            
            if (audioAlerts) {
                audioAlerts.checked = currentConfig.enable_audio !== false;
            }
            
            if (saveImages) {
                saveImages.checked = currentConfig.save_events !== false;
            }
            
            console.log('Configuration loaded:', currentConfig);
        }
    } catch (error) {
        console.error('Error loading configuration:', error);
        showToast('Warning', 'Failed to load configuration, using defaults', 'warning');
        
        // Set defaults on error
        setDefaultConfiguration();
    }
}

/**
 * Set default configuration values
 */
function setDefaultConfiguration() {
    const confidenceSlider = document.getElementById('confidence-slider');
    const analysisInterval = document.getElementById('analysis-interval');
    const resolution = document.getElementById('resolution');
    const audioAlerts = document.getElementById('audio-alerts');
    const saveImages = document.getElementById('save-images');
    
    if (confidenceSlider) {
        confidenceSlider.value = 0.2;
        updateConfidenceDisplay(0.2);
    }
    
    if (analysisInterval) analysisInterval.value = 10;
    if (resolution) resolution.value = '1640x1232';
    if (audioAlerts) audioAlerts.checked = true;
    if (saveImages) saveImages.checked = true;
}

/**
 * Save configuration to server
 */
async function saveConfiguration(event) {
    event.preventDefault();
    
    // Collect form data
    const confidenceThreshold = parseFloat(document.getElementById('confidence-slider').value);
    const analysisInterval = parseInt(document.getElementById('analysis-interval').value);
    const resolution = document.getElementById('resolution').value;
    const audioAlerts = document.getElementById('audio-alerts').checked;
    const saveImages = document.getElementById('save-images').checked;
    
    const configData = {
        confidence_threshold: confidenceThreshold,
        analysis_interval: analysisInterval,
        resolution: resolution,
        enable_audio: audioAlerts,
        save_events: saveImages
    };
    
    console.log('Saving configuration:', configData);
    
    // Show loading toast
    showToast('Saving', 'Saving configuration...', 'info');
    
    try {
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(configData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentConfig = data.config || configData;
            showToast('Success', data.message || 'Configuration saved successfully', 'success');
        } else {
            showToast('Error', data.message || 'Failed to save configuration', 'error');
        }
    } catch (error) {
        console.error('Error saving configuration:', error);
        showToast('Error', 'Failed to communicate with server', 'error');
    }
}

/**
 * Show toast notification
 */
function showToast(title, message, type = 'info') {
    const toast = document.getElementById('toast-notification');
    const icon = document.getElementById('toast-icon');
    const titleEl = document.getElementById('toast-title');
    const messageEl = document.getElementById('toast-message');
    
    if (!toast || !icon || !titleEl || !messageEl) {
        console.error('Toast elements not found');
        return;
    }
    
    // Set content
    titleEl.textContent = title;
    messageEl.textContent = message;
    
    // Set icon and color based on type
    const styles = {
        success: { icon: 'fas fa-check-circle text-green-500', border: 'border-green-500' },
        error: { icon: 'fas fa-exclamation-circle text-red-500', border: 'border-red-500' },
        warning: { icon: 'fas fa-exclamation-triangle text-yellow-500', border: 'border-yellow-500' },
        info: { icon: 'fas fa-info-circle text-blue-500', border: 'border-blue-500' }
    };
    
    const style = styles[type] || styles.info;
    icon.className = style.icon + ' text-2xl mr-3';
    
    // Update toast border color
    toast.className = 'fixed bottom-4 right-4 bg-white rounded-lg shadow-xl p-4 max-w-md z-50 transform transition-transform ' + style.border;
    
    // Show toast
    toast.classList.remove('hidden');
    
    // Auto-hide after 5 seconds
    setTimeout(hideToast, 5000);
}

/**
 * Hide toast notification
 */
function hideToast() {
    const toast = document.getElementById('toast-notification');
    if (toast) {
        toast.classList.add('hidden');
    }
}
