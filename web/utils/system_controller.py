"""
System Controller for managing the detection process (main.py)
Handles starting, stopping, and checking status of the surveillance system
"""
import subprocess
import os
import signal
import psutil
import time
from pathlib import Path

class SystemController:
    """Manages the detection system process lifecycle"""
    
    def __init__(self, project_root='/home/abdul/Project-yolo11'):
        """
        Initialize SystemController
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
        self.main_script = self.project_root / 'main.py'
        self.venv_python = self.project_root / 'venv' / 'bin' / 'python'
        self.process = None
        self.pid = None
        self.pid_file = self.project_root / 'web' / '.detection_pid'
        
        # Import config_manager here to avoid circular imports
        from .config_manager import config_manager
        self.config_manager = config_manager
    
    def is_running(self):
        """
        Check if the detection process is currently running
        
        Returns:
            bool: True if running, False otherwise
        """
        # First check if we have a stored PID
        if self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                # Check if process with this PID exists and is our script
                if psutil.pid_exists(pid):
                    try:
                        proc = psutil.Process(pid)
                        cmdline = ' '.join(proc.cmdline())
                        
                        # Verify it's actually running main.py
                        if 'main.py' in cmdline:
                            self.pid = pid
                            return True
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                # PID file exists but process is not running, clean up
                self.pid_file.unlink()
                self.pid = None
                return False
                
            except (ValueError, IOError):
                # Invalid PID file
                if self.pid_file.exists():
                    self.pid_file.unlink()
        
        # Alternative: Search for main.py in running processes
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if 'main.py' in cmdline and 'python' in cmdline.lower():
                    self.pid = proc.info['pid']
                    # Save PID for future reference
                    with open(self.pid_file, 'w') as f:
                        f.write(str(self.pid))
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return False
    
    def start(self, webhook_url=None):
        """
        Start the detection process
        
        Args:
            webhook_url: Optional webhook URL for event notifications
        
        Returns:
            dict: Result with success status and message
        """
        # Check if already running
        if self.is_running():
            return {
                'success': False,
                'message': 'Detection system is already running',
                'pid': self.pid
            }
        
        # Verify main.py exists
        if not self.main_script.exists():
            return {
                'success': False,
                'message': f'main.py not found at {self.main_script}'
            }
        
        # Load configuration from config file
        config = self.config_manager.get_config()
        
        # Prepare command - use NCNN model and config values
        model_path = self.project_root / 'best_ncnn_model'
        confidence_threshold = config.get('confidence_threshold', 0.2)
        resolution = config.get('resolution', '1640x1232')
        analysis_interval = config.get('analysis_interval', 3)
        
        cmd = [
            str(self.venv_python), 
            str(self.main_script),
            '--model', str(model_path),
            '--resolution', resolution,
            '--thresh', str(confidence_threshold),
            '--analyze-interval', str(analysis_interval)
        ]
        
        # Add webhook URL if provided, otherwise use from config
        if webhook_url:
            cmd.extend(['--webhook', webhook_url])
        elif config.get('webhook_url'):
            cmd.extend(['--webhook', config.get('webhook_url')])
        
        try:
            # Start process in background with DISPLAY environment variable
            env = os.environ.copy()
            env['DISPLAY'] = ':0'  # Ensure X11 display is available
            
            self.process = subprocess.Popen(
                cmd,
                cwd=str(self.project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                start_new_session=True  # Detach from parent
            )
            
            self.pid = self.process.pid
            
            # Save PID to file
            with open(self.pid_file, 'w') as f:
                f.write(str(self.pid))
            
            # Give it a moment to start
            time.sleep(2)
            
            # Verify it's still running (didn't crash immediately)
            if self.is_running():
                return {
                    'success': True,
                    'message': 'Detection system started successfully',
                    'pid': self.pid
                }
            else:
                return {
                    'success': False,
                    'message': 'Detection system failed to start (process exited)'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error starting detection system: {str(e)}'
            }
    
    def stop(self):
        """
        Stop the detection process gracefully
        
        Returns:
            dict: Result with success status and message
        """
        # Check if running
        if not self.is_running():
            # Clean up PID file if it exists
            if self.pid_file.exists():
                self.pid_file.unlink()
            return {
                'success': False,
                'message': 'Detection system is not running'
            }
        
        try:
            # Try graceful termination first (SIGTERM)
            proc = psutil.Process(self.pid)
            proc.terminate()
            
            # Wait up to 5 seconds for graceful shutdown
            try:
                proc.wait(timeout=5)
            except psutil.TimeoutExpired:
                # Force kill if it doesn't stop gracefully
                proc.kill()
                proc.wait(timeout=3)
            
            # Clean up PID file
            if self.pid_file.exists():
                self.pid_file.unlink()
            
            self.pid = None
            self.process = None
            
            return {
                'success': True,
                'message': 'Detection system stopped successfully'
            }
            
        except psutil.NoSuchProcess:
            # Process already dead, just clean up
            if self.pid_file.exists():
                self.pid_file.unlink()
            self.pid = None
            return {
                'success': True,
                'message': 'Detection system was not running'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error stopping detection system: {str(e)}'
            }
    
    def get_status(self):
        """
        Get current status of the detection system
        
        Returns:
            dict: Status information including running state, PID, uptime
        """
        is_running = self.is_running()
        
        status = {
            'running': is_running,
            'pid': self.pid if is_running else None,
            'message': 'Detection system is running' if is_running else 'Detection system is stopped'
        }
        
        # Add uptime if running
        if is_running and self.pid:
            try:
                proc = psutil.Process(self.pid)
                create_time = proc.create_time()
                uptime_seconds = time.time() - create_time
                
                # Format uptime
                hours = int(uptime_seconds // 3600)
                minutes = int((uptime_seconds % 3600) // 60)
                seconds = int(uptime_seconds % 60)
                
                status['uptime'] = f"{hours}h {minutes}m {seconds}s"
                status['uptime_seconds'] = int(uptime_seconds)
                
                # Add memory usage
                mem_info = proc.memory_info()
                status['memory_mb'] = round(mem_info.rss / 1024 / 1024, 1)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return status
    
    def restart(self, webhook_url=None):
        """
        Restart the detection process
        
        Args:
            webhook_url: Optional webhook URL for event notifications
        
        Returns:
            dict: Result with success status and message
        """
        # Stop if running
        if self.is_running():
            stop_result = self.stop()
            if not stop_result['success']:
                return stop_result
            
            # Wait a moment between stop and start
            time.sleep(2)
        
        # Start
        return self.start(webhook_url)


# Global system controller instance
system_controller = SystemController()
