#!/usr/bin/env python3
"""
Voice Configuration Manager for Pi Gateway
Fetches configuration from VPS and manages voice models
"""

import json
import requests
import os
import sys
import subprocess
import logging
from pathlib import Path
from datetime import datetime
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/voice_config.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VoiceConfigManager:
    """Manages voice configuration and model loading"""

    def __init__(self):
        self.config_url = "http://my-bookings.co.uk/webhooks/get_voice_config.php"
        self.config_file = "/home/rom/voice_config.json"
        self.config = None

        # Whisper model paths
        self.whisper_models = {
            "WHISPER_TINY": "/home/rom/whisper.cpp/models/ggml-tiny-q5_0.bin",
            "WHISPER_BASE": "/home/rom/whisper.cpp/models/ggml-base-q5_0.bin",
            "WHISPER_TINY_FULL": "/home/rom/whisper.cpp/models/ggml-tiny.bin",
            "WHISPER_BASE_FULL": "/home/rom/whisper.cpp/models/ggml-base.bin"
        }

        # TTS provider modules (will be loaded dynamically)
        self.tts_providers = {}

    def get_vpn_ip(self):
        """Get current VPN IP address from WireGuard interface"""
        try:
            result = subprocess.run(
                ['ip', 'addr', 'show', 'wg0'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'inet ' in line:
                        ip = line.split()[1].split('/')[0]
                        logger.info(f"VPN IP detected: {ip}")
                        return ip

        except Exception as e:
            logger.error(f"Failed to get VPN IP: {e}")

        # Fallback to .env file
        try:
            env_file = '/home/rom/.env'
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    for line in f:
                        if line.startswith('WG_VPN_IP='):
                            ip = line.split('=')[1].strip()
                            logger.info(f"VPN IP from .env: {ip}")
                            return ip
        except Exception as e:
            logger.error(f"Failed to read .env: {e}")

        return None

    def wait_for_wireguard(self, max_wait=60):
        """Wait for WireGuard to establish connection"""
        logger.info("Waiting for WireGuard connection...")
        start_time = time.time()

        while time.time() - start_time < max_wait:
            # Check if WireGuard is up
            result = subprocess.run(
                ['sudo', 'wg', 'show', 'wg0'],
                capture_output=True,
                timeout=5
            )

            if result.returncode == 0:
                # Check for handshake
                if 'latest handshake' in result.stdout.decode():
                    logger.info("WireGuard connection established!")
                    time.sleep(2)  # Give it a moment to stabilize
                    return True

            time.sleep(2)

        logger.error("WireGuard connection timeout!")
        return False

    def fetch_configuration(self, retry_count=3):
        """Fetch configuration from VPS webhook"""
        vpn_ip = self.get_vpn_ip()
        if not vpn_ip:
            logger.error("Cannot determine VPN IP!")
            return None

        url = f"{self.config_url}?ip={vpn_ip}&include_key=1"
        logger.info(f"Fetching configuration from: {url}")

        for attempt in range(retry_count):
            try:
                response = requests.get(url, timeout=10)

                if response.status_code == 200:
                    data = response.json()

                    if data.get('success'):
                        logger.info(f"Configuration retrieved: {data.get('message')}")
                        self.config = data.get('data')

                        # Save to local file
                        with open(self.config_file, 'w') as f:
                            json.dump(self.config, f, indent=2)

                        return self.config
                    else:
                        logger.error(f"Configuration failed: {data.get('message')}")

                else:
                    logger.error(f"HTTP {response.status_code}: {response.text}")

            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed (attempt {attempt+1}/{retry_count}): {e}")

            if attempt < retry_count - 1:
                time.sleep(5)

        # Try to load cached config
        if os.path.exists(self.config_file):
            logger.warning("Using cached configuration")
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
                return self.config

        return None

    def validate_whisper_model(self):
        """Validate and return the whisper model path"""
        if not self.config:
            return None

        stt_model = self.config.get('stt_model', 'WHISPER_BASE')

        if stt_model == 'NULL':
            logger.info("STT disabled in configuration")
            return None

        model_path = self.whisper_models.get(stt_model)

        if model_path and os.path.exists(model_path):
            logger.info(f"Whisper model ready: {stt_model} at {model_path}")
            return model_path
        else:
            # Fallback to base model
            fallback = self.whisper_models.get('WHISPER_BASE')
            if os.path.exists(fallback):
                logger.warning(f"Using fallback model: {fallback}")
                return fallback

        logger.error("No valid whisper model found!")
        return None

    def get_tts_provider(self):
        """Get the TTS provider based on configuration"""
        if not self.config:
            return None

        tts_model = self.config.get('tts_model', 'azure').lower()

        # Import the appropriate TTS module
        if tts_model == 'azure':
            from TTS.tts_azure import AzureTTS
            return AzureTTS(self.config)
        elif tts_model == 'openai':
            from TTS.tts_openai import OpenAITTS
            return OpenAITTS(self.config)
        elif tts_model == 'liepa':
            from TTS.tts_liepa import LiepaTTS
            return LiepaTTS(self.config)
        elif tts_model == 'google':
            from TTS.tts_google import GoogleTTS
            return GoogleTTS(self.config)
        else:
            logger.error(f"Unknown TTS provider: {tts_model}")
            return None

    def apply_configuration(self):
        """Apply all configuration settings"""
        if not self.config:
            logger.error("No configuration to apply!")
            return False

        logger.info("="*60)
        logger.info("APPLYING VOICE CONFIGURATION")
        logger.info("="*60)

        # Display configuration
        logger.info(f"Workpoint: {self.config.get('workpoint_name')} (ID: {self.config.get('workpoint_id')})")
        logger.info(f"Phone: {self.config.get('phone_number')}")
        logger.info(f"Language: {self.config.get('language')}")
        logger.info(f"STT Model: {self.config.get('stt_model')}")
        logger.info(f"TTS Model: {self.config.get('tts_model')}")
        logger.info(f"Answer after: {self.config.get('answer_after_rings')} rings")
        logger.info(f"VAD Threshold: {self.config.get('vad_threshold')}")
        logger.info(f"Silence Timeout: {self.config.get('silence_timeout')}ms")

        # Validate models
        whisper_model = self.validate_whisper_model()
        if self.config.get('stt_model') != 'NULL' and not whisper_model:
            logger.error("Failed to validate Whisper model!")
            return False

        # Initialize TTS
        tts_provider = self.get_tts_provider()
        if not tts_provider:
            logger.error("Failed to initialize TTS provider!")
            return False

        # Save runtime configuration
        runtime_config = {
            'whisper_model': whisper_model,
            'tts_provider': self.config.get('tts_model'),
            'language': self.config.get('language'),
            'vad_threshold': self.config.get('vad_threshold'),
            'silence_timeout': self.config.get('silence_timeout'),
            'answer_after_rings': self.config.get('answer_after_rings'),
            'welcome_message': self.config.get('welcome_message'),
            'voice_settings': self.config.get('voice_settings'),
            'updated_at': datetime.now().isoformat()
        }

        with open('/home/rom/runtime_voice_config.json', 'w') as f:
            json.dump(runtime_config, f, indent=2)

        logger.info("✅ Configuration applied successfully!")
        return True

    def send_notification(self, message, severity="info"):
        """Send notification to monitoring system"""
        try:
            subprocess.run(
                ['/home/rom/pi_send_message.sh', message, severity],
                timeout=10
            )
        except:
            pass

def main():
    """Main initialization function"""
    manager = VoiceConfigManager()

    # Wait for WireGuard
    if not manager.wait_for_wireguard():
        manager.send_notification("Voice config: WireGuard timeout", "warning")
        sys.exit(1)

    # Fetch configuration
    config = manager.fetch_configuration()
    if not config:
        manager.send_notification("Voice config: Failed to fetch configuration", "error")
        sys.exit(1)

    # Apply configuration
    if manager.apply_configuration():
        manager.send_notification(
            f"Voice configured: {config.get('workpoint_name')} ({config.get('language')})",
            "info"
        )

        # Restart voice bot with new configuration
        # NOTE: Now using SIM7600 voice bot (EC25 deprecated)
        logger.info("Restarting voice bot service...")
        subprocess.run(['sudo', 'systemctl', 'restart', 'sim7600-voice-bot'], timeout=10)

    else:
        manager.send_notification("Voice config: Failed to apply configuration", "error")
        sys.exit(1)

if __name__ == "__main__":
    main()