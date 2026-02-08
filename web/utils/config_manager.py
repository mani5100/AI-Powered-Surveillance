"""
Configuration Manager for the surveillance system
Handles reading and writing system configuration to JSON file
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    """Manages system configuration persistence"""
    
    def __init__(self, config_file='/home/abdul/Project-yolo11/web/system_config.json'):
        """
        Initialize ConfigManager
        
        Args:
            config_file: Path to the configuration JSON file
        """
        self.config_file = Path(config_file)
        self.default_config = {
            'confidence_threshold': 0.2,
            'analysis_interval': 10,
            'resolution': '1640x1232',
            'enable_audio': True,
            'save_events': True,
            'webhook_url': 'http://localhost:5000/api/webhook/new-event',
            'model_path': '/home/abdul/Project-yolo11/best.pt',
            'object_classes': [
                'knife', 'gun', 'cigarette', 'vape', 'syringe',
                'pills', 'alcohol', 'phone', 'mask', 'person'
            ]
        }
        
        # Ensure config file exists with defaults
        if not self.config_file.exists():
            self._write_config(self.default_config)
    
    def get_config(self) -> Dict[str, Any]:
        """
        Read and return current configuration
        
        Returns:
            dict: Current system configuration
        """
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            # Merge with defaults to ensure all keys exist
            merged_config = self.default_config.copy()
            merged_config.update(config)
            
            return merged_config
            
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error reading config file: {e}")
            # Return defaults if file is corrupted
            return self.default_config.copy()
    
    def update_config(self, updates: Dict[str, Any]) -> Dict[str, str]:
        """
        Update configuration with new values
        
        Args:
            updates: Dictionary of configuration keys to update
        
        Returns:
            dict: Result with success status and message
        """
        try:
            # Get current config
            current_config = self.get_config()
            
            # Validate and update values
            validation_result = self._validate_updates(updates)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'message': validation_result['message']
                }
            
            # Apply updates
            for key, value in updates.items():
                if key in current_config:
                    current_config[key] = value
            
            # Write updated config
            self._write_config(current_config)
            
            return {
                'success': True,
                'message': 'Configuration updated successfully',
                'config': current_config
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error updating configuration: {str(e)}'
            }
    
    def _validate_updates(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate configuration updates
        
        Args:
            updates: Dictionary of updates to validate
        
        Returns:
            dict: Validation result with valid flag and message
        """
        # Validate confidence_threshold
        if 'confidence_threshold' in updates:
            value = updates['confidence_threshold']
            if not isinstance(value, (int, float)) or value < 0.1 or value > 0.9:
                return {
                    'valid': False,
                    'message': 'confidence_threshold must be between 0.1 and 0.9'
                }
        
        # Validate analysis_interval
        if 'analysis_interval' in updates:
            value = updates['analysis_interval']
            if not isinstance(value, int) or value < 1 or value > 300:
                return {
                    'valid': False,
                    'message': 'analysis_interval must be between 1 and 300 seconds'
                }
        
        # Validate resolution
        if 'resolution' in updates:
            value = updates['resolution']
            valid_resolutions = ['640x480', '1280x720', '1640x1232', '1920x1080']
            if value not in valid_resolutions:
                return {
                    'valid': False,
                    'message': f'resolution must be one of {valid_resolutions}'
                }
        
        # Validate boolean flags
        for key in ['enable_audio', 'save_events']:
            if key in updates:
                if not isinstance(updates[key], bool):
                    return {
                        'valid': False,
                        'message': f'{key} must be a boolean value'
                    }
        
        # Validate webhook_url
        if 'webhook_url' in updates:
            value = updates['webhook_url']
            if not isinstance(value, str) or (value and not value.startswith('http')):
                return {
                    'valid': False,
                    'message': 'webhook_url must be a valid HTTP URL or empty string'
                }
        
        return {'valid': True, 'message': 'Valid'}
    
    def _write_config(self, config: Dict[str, Any]) -> None:
        """
        Write configuration to file
        
        Args:
            config: Configuration dictionary to write
        """
        # Ensure directory exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write with pretty formatting
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def reset_to_defaults(self) -> Dict[str, str]:
        """
        Reset configuration to default values
        
        Returns:
            dict: Result with success status and message
        """
        try:
            self._write_config(self.default_config)
            return {
                'success': True,
                'message': 'Configuration reset to defaults',
                'config': self.default_config.copy()
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error resetting configuration: {str(e)}'
            }
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """
        Get a single configuration value
        
        Args:
            key: Configuration key to retrieve
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        config = self.get_config()
        return config.get(key, default)
    
    def set_value(self, key: str, value: Any) -> Dict[str, str]:
        """
        Set a single configuration value
        
        Args:
            key: Configuration key to set
            value: Value to set
        
        Returns:
            dict: Result with success status and message
        """
        return self.update_config({key: value})


# Global config manager instance
config_manager = ConfigManager()
