#!/usr/bin/env python3
"""
SIM7600 Voice Bot - Primary Voice Call Handler
Handles phone calls with audio piping for SIM7600G-H modem
Integrates with Whisper STT and Azure TTS via unified API
"""

import serial
import time
import subprocess
import json
import requests
import threading
import queue
import logging
import os
import glob
import sys
from pathlib import Path
import wave
import struct
import numpy as np
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler
import hashlib
import re

# Import audio recorder and profiler
from audio_recorder import CallAudioRecorder
from call_profiler import CallProfiler

# WebRTC VAD (lightweight real-time VAD)
try:
    import webrtcvad
    WEBRTC_VAD_AVAILABLE = True
except ImportError:
    WEBRTC_VAD_AVAILABLE = False
    logging.warning("WebRTC VAD not available - VAD will be disabled")

# Load environment variables
load_dotenv('/home/rom/.env')

# Configure logging based on mode
LOG_MODE = os.getenv('LOG_MODE', 'production')
LOG_LEVEL = logging.DEBUG if LOG_MODE == 'development' else logging.INFO

# Setup logging with rotation
log_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    if LOG_MODE == 'development' else
    '%(asctime)s - %(levelname)s - %(message)s'
)

# File handler with rotation (writes to RAM disk)
log_file_path = '/var/log/voice_bot_ram/sim7600_voice_bot.log'
file_handler = RotatingFileHandler(
    log_file_path,
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(LOG_LEVEL)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(LOG_LEVEL)

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

class SIM7600VoiceBot:
    """Main voice bot for SIM7600G-H modem"""

    def __init__(self):
        # Load port mapping from detector
        self.load_port_mapping()

        # Serial ports (will be opened when modem connects)
        self.ser = None  # AT command serial port
        self.audio_serial = None  # Audio PCM serial port

        # Audio configuration
        self.sample_rate = 8000  # 8kHz for telephony (updated dynamically based on webhook)
        self.channels = 1  # Mono
        self.chunk_size = 320  # 20ms chunks at 8kHz
        self.cpcmfrm_mode = 0  # Modem PCM format: 0=8kHz, 1=16kHz (set during init)

        # Call state
        self.in_call = False
        self.call_id = None
        self.session_id = None

        # TTS cache tracking {tmp_filename: {'text': str, 'voice': str, 'format': str, 'from_cache': bool}}
        self.tts_metadata = {}

        # Audio recorder and profiler
        self.audio_recorder = None
        self.profiler = None

        # Modem initialization retry counter
        self.init_retry_count = 0
        self.max_init_retries = 3

        # Audio queues
        self.audio_in_queue = queue.Queue()  # From phone
        self.audio_out_queue = queue.Queue()  # To phone

        # Voice config (will be fetched on RING, not at startup)
        self.voice_config = None

        # Conversation flow control (prevents overlap)
        self.caller_is_silent = threading.Event()  # Set when 800ms silence detected
        self.bot_is_speaking = False  # True when bot is talking
        self.last_speech_time = 0  # Timestamp of last detected speech
        self.playback_lock = threading.Lock()  # Ensures atomic playback decisions

        # PCM audio path readiness flag
        self.pcm_audio_ready = threading.Event()  # Set when first data arrives from ttyUSB4

        # VAD model (WebRTC)
        self.vad = None
        self.vad_mode = 3  # Aggressiveness: 0-3 (3 = most aggressive filtering)

        # VPS endpoints
        self.vps_webhook = "http://10.100.0.1:8088/webhook/phone_call/receive"
        self.local_tts_api = "http://localhost:8088/phone_call"

        logger.info("="*60)
        logger.info("SIM7600 Voice Bot Initialized")
        logger.info(f"Mode: {LOG_MODE.upper()}")
        logger.info("="*60)

    def load_port_mapping(self):
        """Load port mapping from detector"""
        mapping_file = '/home/rom/sim7600_ports.json'
        try:
            if os.path.exists(mapping_file):
                with open(mapping_file, 'r') as f:
                    mapping = json.load(f)
                    self.at_port = mapping.get('at_command')
                    self.audio_port = mapping.get('audio')
                    self.ppp_port = mapping.get('ppp')
                    logger.info(f"Loaded port mapping from {mapping_file}")
                    logger.info(f"AT Port: {self.at_port}")
                    logger.info(f"Audio Port: {self.audio_port}")
            else:
                # Fallback to defaults if file not found
                self.at_port = None
                self.audio_port = None
                self.ppp_port = None
                logger.warning("Port mapping file not found, will detect ports")
        except Exception as e:
            logger.error(f"Failed to load port mapping: {e}")

    def fetch_voice_config_from_vps(self):
        """Fetch fresh voice configuration from VPS webhook"""
        try:
            # Get VPN IP
            import subprocess
            result = subprocess.run(
                ['ip', 'addr', 'show', 'wg0'],
                capture_output=True,
                text=True,
                timeout=2
            )

            vpn_ip = None
            for line in result.stdout.split('\n'):
                if 'inet ' in line:
                    vpn_ip = line.split()[1].split('/')[0]
                    break

            if not vpn_ip:
                logger.error("Cannot get VPN IP - using cached config")
                return self.load_voice_config_from_file()

            # Fetch from VPS
            url = f"http://my-bookings.co.uk/webhooks/get_voice_config.php?ip={vpn_ip}&include_key=1"
            logger.info(f"Fetching voice config from VPS: {url}")

            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.voice_config = data.get('data')

                    # Save to file for next time
                    with open('/home/rom/voice_config.json', 'w') as f:
                        json.dump(self.voice_config, f, indent=2)

                    logger.info(f"✅ Fresh voice config fetched from VPS")
                    logger.info(f"  Language: {self.voice_config.get('language')}")
                    logger.info(f"  Answer after: {self.voice_config.get('answer_after_rings')} rings")
                    logger.info(f"  Welcome message: {self.voice_config.get('welcome_message', 'None')[:50]}...")
                    return True
                else:
                    logger.error(f"VPS returned error: {data.get('message')}")
                    return self.load_voice_config_from_file()
            else:
                logger.error(f"HTTP {response.status_code} - using cached config")
                return self.load_voice_config_from_file()

        except Exception as e:
            logger.error(f"Failed to fetch config from VPS: {e}")
            return self.load_voice_config_from_file()

    def load_voice_config_from_file(self):
        """Load voice configuration from local file (fallback)"""
        try:
            config_file = '/home/rom/voice_config.json'
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    self.voice_config = json.load(f)
                    logger.info(f"Loaded cached voice config: {self.voice_config.get('language')}")
                    return True
            else:
                logger.error("No voice config file found!")
                self.voice_config = {
                    'language': 'en',
                    'answer_after_rings': 3,
                    'welcome_message': 'Hello, how can I help you?'
                }
                return False
        except Exception as e:
            logger.error(f"Failed to load voice config from file: {e}")
            self.voice_config = {
                'language': 'en',
                'answer_after_rings': 3,
                'welcome_message': 'Hello, how can I help you?'
            }
            return False

    def get_audio_format_fallback(self):
        """Get audio format string based on modem's CPCMFRM setting"""
        if self.cpcmfrm_mode == 1:
            return 'raw-16khz-16bit-mono-pcm'
        else:
            return 'raw-8khz-16bit-mono-pcm'

    def sanitize_filename(self, text):
        """
        Clean text to create safe filesystem filename
        - Remove all non-alphanumeric characters
        - Convert to lowercase
        - Limit length to 200 chars
        - Use hash for very long texts
        """
        # Remove non-alphanumeric characters (keep only a-z, A-Z, 0-9)
        cleaned = re.sub(r'[^a-zA-Z0-9]', '', text)
        cleaned = cleaned.lower()

        # If too long, use first 150 chars + hash of full text
        if len(cleaned) > 200:
            text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
            cleaned = cleaned[:150] + '_' + text_hash

        return cleaned

    def get_cache_path(self, text, audio_format, voice):
        """
        Generate cache file path for TTS audio
        Path: /home/rom/audio_library/{audio_format}/{voice}/{filename}.raw
        """
        base_dir = Path('/home/rom/audio_library')

        # Create directory structure: audio_library/format/voice/
        cache_dir = base_dir / audio_format / voice
        cache_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename from text
        filename = self.sanitize_filename(text) + '.raw'

        return cache_dir / filename

    def load_from_cache(self, cache_path):
        """Load cached audio file"""
        try:
            if cache_path.exists():
                with open(cache_path, 'rb') as f:
                    audio_data = f.read()
                return audio_data
        except Exception as e:
            logger.error(f"Cache load error: {e}")
        return None

    def save_to_cache(self, cache_path, audio_data):
        """Save audio to cache"""
        try:
            with open(cache_path, 'wb') as f:
                f.write(audio_data)
        except Exception as e:
            logger.error(f"Cache save error: {e}")

    def load_vad_model(self):
        """Load WebRTC VAD for speech detection"""
        if not WEBRTC_VAD_AVAILABLE:
            logger.warning("WebRTC VAD not available - VAD disabled")
            return False

        try:
            logger.info("Loading WebRTC VAD...")

            # Create WebRTC VAD instance
            self.vad = webrtcvad.Vad(self.vad_mode)

            logger.info(f"✅ WebRTC VAD loaded successfully (mode={self.vad_mode})")
            return True

        except Exception as e:
            logger.error(f"Failed to load WebRTC VAD: {e}")
            logger.warning("Continuing without VAD - conversation overlap may occur")
            return False

    def detect_sim7600_ports(self):
        """Detect SIM7600 USB ports when modem is connected"""
        # This will be called when modem is plugged in
        # SIM7600 port layout (USB composition 9001):
        # ttyUSB0 - Diagnostics (causes broken pipe, DO NOT USE!)
        # ttyUSB1 - GPS/NMEA
        # ttyUSB2 - AT Commands (SMSTools - locked during SMS operations)
        # ttyUSB3 - AT Commands (MAIN PORT - reliable for voice + configuration)
        # ttyUSB4 - PCM Audio (8kHz raw audio during calls)

        ports = []
        for i in range(5):
            port = f"/dev/ttyUSB{i}"
            if os.path.exists(port):
                ports.append(port)
                logger.info(f"Found port: {port}")

        if len(ports) >= 3:
            # Assign ports based on SIM7600 layout (USB composition 9001)
            # Use ttyUSB3 (ports[3]) as main AT port for voice
            self.at_port = ports[3] if len(ports) > 3 else ports[0]  # ttyUSB3
            self.audio_port = ports[4] if len(ports) > 4 else ports[1]  # ttyUSB4
            self.ppp_port = None  # Internet via wwan0 (QMI), not PPP

            logger.info(f"AT Port: {self.at_port}")
            logger.info(f"Audio Port: {self.audio_port}")
            logger.info(f"PPP Port: {self.ppp_port}")
            return True
        else:
            logger.warning(f"Only found {len(ports)} ports, SIM7600 may not be fully connected")
            return False

    def stop_smstools(self):
        """Stop smstools to take over serial port"""
        try:
            # Check if smstools is running first
            result = os.system('sudo systemctl is-active --quiet smstools')

            if result != 0:
                # smstools not running, no need to stop
                logger.info("smstools already stopped")
                return True

            logger.info("Stopping smstools to take over serial port...")
            result = os.system('sudo systemctl stop smstools')

            if result == 0:
                time.sleep(2)  # Wait for port to be released
                logger.info("✅ smstools stopped - voice bot taking over")
                return True
            else:
                logger.error(f"Failed to stop smstools: exit code {result}")
                return False
        except Exception as e:
            logger.error(f"Error stopping smstools: {e}")
            return False

    def restart_smstools(self):
        """Restart smstools when voice bot exits"""
        try:
            logger.info("Restarting smstools...")
            result = os.system('sudo systemctl start smstools')
            time.sleep(1)

            if result == 0:
                logger.info("✅ smstools restarted successfully")
            else:
                logger.error("⚠️ Failed to restart smstools")
        except Exception as e:
            logger.error(f"Error restarting smstools: {e}")

    def init_modem(self):
        """Initialize SIM7600 for voice calls"""
        if not self.at_port:
            logger.error("AT port not available")
            return False

        # NOTE: No longer stopping SMSTools!
        # Voice bot uses ttyUSB3 (AT commands for calls)
        # SMSTools uses ttyUSB2 (SMS handling)
        # No conflict - different ports, both can run simultaneously

        try:
            # Open AT command port
            logger.info(f"Opening serial port: {self.at_port}")
            self.ser = serial.Serial(
                port=self.at_port,
                baudrate=115200,
                timeout=1,
                rtscts=False,
                dsrdtr=False
            )

            # Basic initialization
            self.send_at_command("AT")
            self.send_at_command("ATE0")  # Disable echo

            # CRITICAL: Disable automatic sleep mode
            # AT+CSCLK=0 prevents modem from entering sleep after idle period
            # This prevents I/O errors and USB disconnects during monitoring
            self.send_at_command("AT+CSCLK=0")  # Disable auto sleep

            # Configure audio
            self.send_at_command("AT+CLVL=5")  # Volume level (speaker/earpiece)

            # Enable CLIP (caller ID)
            self.send_at_command("AT+CLIP=1")

            # Enable RING notifications (critical for call detection)
            self.send_at_command("AT+CRC=1")

            # CRITICAL: Enable VoLTE for 4G voice calls (2G/3G being deprecated)
            response = self.send_at_command("AT+CEVOLTE?")
            if "+CEVOLTE: 0" in response or "CEVOLTE" not in response:
                logger.info("Enabling VoLTE for 4G voice support...")
                volte_response = self.send_at_command("AT+CEVOLTE=1,1")
                if "OK" in volte_response:
                    logger.info("✅ VoLTE enabled - ready for 4G voice calls")
                else:
                    logger.warning("⚠️ VoLTE enable failed - calls may fail when 3G shuts down")
            else:
                logger.info("✅ VoLTE already enabled")

            # Don't set ATS0 here - will use timed ATA based on fresh config from VPS
            # This allows dynamic answer_after_rings including -1 (don't answer)

            # CRITICAL: Configure PCM audio format based on VPS webhook settings
            # Fetch config to determine if we should use 8kHz or 16kHz
            logger.info("Fetching voice config to configure audio format...")
            if self.fetch_voice_config_from_vps():
                audio_format = self.voice_config.get('audio_format', '')

                # Check if 16kHz format is requested
                if 'Raw16Khz16BitMonoPc' in audio_format:
                    logger.info("🎵 16kHz audio format detected - configuring modem for 16kHz PCM")
                    self.send_at_command("AT+CPCMFRM=1")  # 1 = 16kHz
                    self.sample_rate = 16000
                    self.cpcmfrm_mode = 1  # Store modem mode
                    logger.info("✅ Modem audio configured: 16kHz (AT+CPCMFRM=1)")
                else:
                    logger.info("🎵 8kHz audio format (default) - configuring modem for 8kHz PCM")
                    self.send_at_command("AT+CPCMFRM=0")  # 0 = 8kHz
                    self.sample_rate = 8000
                    self.cpcmfrm_mode = 0  # Store modem mode
                    logger.info("✅ Modem audio configured: 8kHz (AT+CPCMFRM=0)")
            else:
                logger.warning("⚠️ Could not fetch config - defaulting to 8kHz")
                self.send_at_command("AT+CPCMFRM=0")
                self.sample_rate = 8000
                self.cpcmfrm_mode = 0  # Store modem mode

            logger.info("SIM7600 initialized for voice calls (answer timing based on VPS config)")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize modem: {e}")
            return False

    def send_at_command(self, command, timeout=1, delay=1):
        """Send AT command and get response

        Args:
            command: AT command to send
            timeout: Serial port read timeout (max wait for modem response)
            delay: Time to wait after sending command before reading response
        """
        try:
            # Set serial timeout dynamically
            self.ser.timeout = timeout

            # Send command
            self.ser.write(f"{command}\r\n".encode())

            # Wait for modem to process (configurable delay)
            time.sleep(delay)

            # Read response (read as data arrives, don't request fixed byte count)
            response = ""
            start_time = time.time()
            first_data_time = None
            iterations = 0

            # Debug flag for timing-critical commands
            debug_timing = 'CPCMREG' in command

            # Suppress verbose debug logs for query commands (they return multiline responses)
            suppress_debug = any(cmd in command for cmd in ['CPCMFRM?', 'COPS?', 'CGDCONT?'])

            while (time.time() - start_time) < timeout:
                iterations += 1
                if self.ser.in_waiting > 0:
                    if first_data_time is None:
                        first_data_time = time.time()
                        if debug_timing:
                            logger.debug(f"[{command}] First data after {(first_data_time - start_time)*1000:.1f}ms, {iterations} iterations")

                    # Read only available bytes (don't request more than available)
                    chunk = self.ser.read(self.ser.in_waiting).decode('utf-8', errors='ignore')
                    response += chunk

                    # If we got OK or ERROR, response is complete
                    if 'OK' in response or 'ERROR' in response:
                        if debug_timing:
                            logger.debug(f"[{command}] Complete response in {(time.time() - start_time)*1000:.1f}ms")
                        break
                else:
                    # Small sleep to avoid busy waiting
                    time.sleep(0.01)

            # Only log debug for non-suppressed commands
            if not suppress_debug:
                logger.debug(f"AT: {command} -> {response.strip()}")
            return response
        except Exception as e:
            logger.error(f"AT command error: {e}")
            return ""

    def handle_incoming_call(self, caller_id, ring_time):
        """Handle incoming call"""
        logger.info(f"📞 RING detected from {caller_id}")

        # Generate call and session IDs (initialize profiler FIRST to track everything)
        temp_call_id = f"call_{int(time.time())}"
        self.call_id = temp_call_id
        self.session_id = f"session_{int(time.time())}"

        # Initialize profiler to track entire call flow
        self.profiler = CallProfiler(self.call_id)
        self.profiler.log_event('call_started')

        # CRITICAL: Trigger immediate internet check (call depends on internet!)
        logger.info("🚨 Triggering priority internet check (call requires VPS queries)...")
        self.profiler.start_timer('internet_check')
        try:
            subprocess.run(
                ['/home/rom/trigger_internet_check.sh', f'Incoming call from {caller_id}'],
                timeout=2,
                capture_output=True
            )
            self.profiler.stop_timer('internet_check', 'internet_check_triggered', {})
        except Exception as e:
            logger.warning(f"Failed to trigger internet check: {e}")
            self.profiler.stop_timer('internet_check', 'internet_check_failed', {'error': str(e)})

        # CRITICAL: Fetch fresh voice config from VPS IMMEDIATELY
        logger.info("Fetching fresh voice configuration from VPS...")
        self.profiler.start_timer('config_fetch')
        config_success = self.fetch_voice_config_from_vps()
        self.profiler.stop_timer('config_fetch', 'vps_config_fetch', {'success': config_success})
        if not config_success:
            logger.error("Failed to fetch voice config - using fallback")

        # Verify audio format configuration
        audio_format = self.voice_config.get('audio_format', 'Not specified')
        logger.info(f"🎵 Audio format from webhook: {audio_format}")

        # Query current CPCMFRM setting
        cpcmfrm_response = self.send_at_command("AT+CPCMFRM?", timeout=0.3, delay=0.1)
        if '+CPCMFRM:' in cpcmfrm_response:
            # Extract the number (0 or 1)
            cpcmfrm_value = cpcmfrm_response.split('+CPCMFRM:')[1].strip().split()[0]
            cpcmfrm_explanation = "8kHz" if cpcmfrm_value == "0" else "16kHz" if cpcmfrm_value == "1" else "Unknown"
            logger.info(f"🎵 Modem PCM format: AT+CPCMFRM={cpcmfrm_value} ({cpcmfrm_explanation})")
        else:
            logger.warning("⚠️ Could not query AT+CPCMFRM setting")

        # Check answer_after_rings setting
        answer_after_rings = self.voice_config.get('answer_after_rings', 3)
        logger.info(f"Answer setting: {answer_after_rings} rings")

        if answer_after_rings == -1:
            logger.info("🚫 answer_after_rings = -1: NOT answering this call (human operator may answer)")
            return  # Don't answer, no VPS notification

        # Calculate wait time: 2 seconds per ring
        wait_seconds = 2 * answer_after_rings
        logger.info(f"Waiting {wait_seconds} seconds ({answer_after_rings} rings × 2s) before answering...")

        # Wait for the required time
        self.profiler.start_timer('ring_wait')
        elapsed = 0
        while elapsed < wait_seconds:
            time.sleep(0.5)
            elapsed = time.time() - ring_time
            logger.debug(f"Waiting to answer: {elapsed:.1f}s / {wait_seconds}s")
        self.profiler.stop_timer('ring_wait', 'ring_wait_complete', {'wait_seconds': wait_seconds, 'rings': answer_after_rings})

        # Time elapsed - answer the call
        logger.info(f"⏰ {wait_seconds}s elapsed - answering call with ATA")
        self.profiler.start_timer('ata_command')
        response = self.send_at_command("ATA", timeout=0.3, delay=0.25)

        # Check if call was successfully answered
        if "BUSY" in response or "NO CARRIER" in response or "ERROR" in response:
            logger.warning(f"Failed to answer call - caller may have hung up: {response}")
            self.profiler.log_event('call_answer_failed', {'reason': response})
            self.profiler.save()
            return

        self.profiler.stop_timer('ata_command', 'AT:ATA', {'delay': '0.25s', 'timeout': '0.3s'})

        # Set call state
        self.in_call = True
        logger.info(f"✅ Call answered: {self.call_id}")
        self.profiler.log_event('call_answered', {'caller_id': caller_id})

        # Enable PCM audio after answering
        logger.info("Enabling PCM audio...")
        self.profiler.start_timer('pcm_enable')
        self.send_at_command("AT+CPCMREG=1", timeout=5, delay=0)
        self.profiler.stop_timer('pcm_enable', 'AT:AT+CPCMREG=1', {'delay': '0s', 'timeout': '5s'})

        # Start audio recorder
        self.profiler.start_timer('audio_recorder_init')
        self.audio_recorder = CallAudioRecorder(self.call_id, self.sample_rate)
        self.audio_recorder.start_all()
        self.profiler.stop_timer('audio_recorder_init', 'audio_recorder_started')

        # VAD should already be loaded at startup (if not, skip it for this call)
        if self.vad is None:
            logger.warning("WebRTC VAD not loaded - will use fallback energy detection")

        # Reset conversation state
        # IMPORTANT: Start with caller_is_silent SET (assume silence when call connects)
        # This allows welcome message to play immediately
        # Flag will be cleared as soon as caller speaks
        self.profiler.start_timer('conversation_state_init')
        self.caller_is_silent.set()
        self.pcm_audio_ready.clear()  # Will be set when first data arrives from ttyUSB4
        self.bot_is_speaking = False
        self.last_speech_time = 0
        self.profiler.stop_timer('conversation_state_init', 'conversation_state_initialized')
        logger.info("Conversation state initialized: caller_is_silent=True (ready for welcome message)")

        # Open audio serial port (shared by capture and playback threads)
        if not self.audio_port:
            logger.error("Audio port not configured - cannot handle audio!")
            return

        self.profiler.start_timer('audio_serial_open')
        try:
            self.audio_serial = serial.Serial(
                self.audio_port,  # /dev/ttyUSB4
                baudrate=115200,
                timeout=0.1
            )
            self.profiler.stop_timer('audio_serial_open', 'audio_serial_opened')
            logger.info(f"✅ Audio serial port opened: {self.audio_port}")
        except Exception as e:
            logger.error(f"Failed to open audio port: {e}")
            self.in_call = False
            return

        # Start audio threads
        self.profiler.start_timer('audio_threads_start')
        threading.Thread(target=self.audio_capture_thread, daemon=True).start()
        threading.Thread(target=self.audio_playback_thread, daemon=True).start()
        threading.Thread(target=self.transcription_thread, daemon=True).start()
        self.profiler.stop_timer('audio_threads_start', 'audio_threads_started')

        # Play welcome message from config
        welcome_message = self.voice_config.get('welcome_message',
                                                'Hello, how can I help you today?')
        logger.info(f"Playing welcome message: {welcome_message[:50]}...")
        self.request_tts(welcome_message, priority='high')

        # Notify VPS about call start
        self.notify_vps('call_started', {
            'caller': caller_id,
            'welcome_message': welcome_message
        })

    def audio_capture_thread(self):
        """Capture audio with progressive transcription and multi-tier silence detection"""
        logger.info("Audio capture thread started")

        try:
            # Use shared audio serial port
            audio_serial = self.audio_serial

            # Audio parameters
            sample_rate = 8000  # 8kHz
            bytes_per_sample = 2  # 16-bit = 2 bytes
            frame_duration_ms = 20  # 20ms chunks (WebRTC VAD supports 10/20/30ms)
            frame_size = int(sample_rate * frame_duration_ms / 1000) * bytes_per_sample  # 320 bytes

            # Multi-tier silence detection thresholds (from voice_config or defaults)
            normal_pause_ms = self.voice_config.get('silence_timeout', 800)  # Normal pause: 600-1200ms
            phrase_pause_ms = self.voice_config.get('phrase_pause_ms', 350)  # Short pause for phrase boundaries
            long_speech_threshold_ms = self.voice_config.get('long_speech_threshold_ms', 4500)  # Progressive transcription
            max_speech_duration_ms = self.voice_config.get('max_speech_duration_ms', 6500)  # Noise timeout

            # Calculate frame counts
            normal_pause_frames = normal_pause_ms // frame_duration_ms
            phrase_pause_frames = phrase_pause_ms // frame_duration_ms
            long_speech_frames = long_speech_threshold_ms // frame_duration_ms
            max_speech_frames = max_speech_duration_ms // frame_duration_ms

            # State tracking
            audio_buffer = []
            silence_frames = 0
            vad_chunk_count = 0  # Track detected speech segments
            speech_frames = 0
            in_speech = False
            speech_start_time = 0
            last_chunk_sent_time = 0

            logger.info(f"WebRTC VAD enabled: {self.vad is not None}")
            if self.vad:
                logger.info(f"WebRTC VAD mode: {self.vad_mode} (0=least aggressive, 3=most aggressive)")
            logger.info(f"Normal pause: {normal_pause_ms}ms ({normal_pause_frames} frames)")
            logger.info(f"Phrase pause: {phrase_pause_ms}ms ({phrase_pause_frames} frames)")
            logger.info(f"Long speech threshold: {long_speech_threshold_ms}ms")
            logger.info(f"Max speech duration: {max_speech_duration_ms}ms")

            first_data_received = False

            while self.in_call:
                try:
                    # Read one frame (20ms)
                    frame = audio_serial.read(frame_size)

                    if len(frame) < frame_size:
                        # Not enough data yet
                        time.sleep(0.01)
                        continue

                    # CRITICAL: Signal that PCM audio path is ready (first data received)
                    if not first_data_received:
                        first_data_received = True
                        self.pcm_audio_ready.set()
                        logger.info("🎧 PCM audio path ready - first data received from ttyUSB4")

                    # Record raw incoming audio
                    if self.audio_recorder:
                        self.audio_recorder.record_incoming_raw(frame)

                    # Detect speech using VAD
                    is_speech = False

                    if self.vad is not None:
                        try:
                            # WebRTC VAD expects raw PCM bytes (16-bit signed, little-endian)
                            # Frame must be exactly 10ms, 20ms, or 30ms at 8/16/32kHz
                            is_speech = self.vad.is_speech(frame, sample_rate)

                        except Exception as e:
                            logger.error(f"WebRTC VAD error: {e}")
                            is_speech = True  # Fallback: assume speech

                    else:
                        # No VAD - simple energy-based detection
                        audio_int16 = np.frombuffer(frame, dtype=np.int16)
                        energy = np.abs(audio_int16).mean()
                        is_speech = energy > 500  # Simple threshold

                    # Process based on speech detection
                    if is_speech:
                        # Speech detected
                        if not in_speech:
                            logger.info("🎤 Speech started - caller is speaking")
                            in_speech = True
                            speech_start_time = time.time()
                            speech_frames = 0
                            last_chunk_sent_time = speech_start_time

                        speech_frames += 1
                        silence_frames = 0

                        # CRITICAL: Clear silence flag - caller is speaking NOW
                        with self.playback_lock:
                            was_silent = self.caller_is_silent.is_set()
                            self.caller_is_silent.clear()
                            self.last_speech_time = time.time()
                            if was_silent:
                                logger.debug("🔴 Silence flag cleared - caller speaking (bot must wait)")

                        # Check speech duration
                        speech_duration_ms = (time.time() - speech_start_time) * 1000

                        # TIER 3: Maximum speech duration exceeded (6.5s) - probably noise
                        if speech_duration_ms > max_speech_duration_ms:
                            logger.warning(f"⚠️ Speech duration exceeded {max_speech_duration_ms}ms - probably background noise")
                            logger.warning("Setting flag and will play noise error message")

                            # Set flag (so bot can speak error message)
                            with self.playback_lock:
                                self.caller_is_silent.set()

                            # Queue special error message
                            self.request_tts(
                                "Sorry, it's too noisy and I can't understand what you're saying. Please call back from a quieter location.",
                                priority='high'
                            )

                            # Discard buffered audio (it's noise)
                            audio_buffer = []
                            in_speech = False
                            speech_frames = 0
                            silence_frames = 0
                            continue

                        # TIER 2: Long speech (>4.5s) - look for phrase pause (350ms)
                        elif speech_duration_ms > long_speech_threshold_ms:
                            # We're in long speech - check for short phrase pauses
                            # This allows progressive transcription without setting flag
                            time_since_last_chunk = time.time() - last_chunk_sent_time

                            if time_since_last_chunk * 1000 > long_speech_threshold_ms:
                                # Been 4.5s since last chunk - look for phrase pause
                                # (This check happens during silence detection below)
                                pass

                        # Collect audio
                        audio_buffer.append(frame)

                    else:
                        # Silence detected
                        silence_frames += 1

                        if in_speech:
                            # We're in speech, collect silence too (for natural audio)
                            audio_buffer.append(frame)

                            # Calculate current speech duration
                            speech_duration_ms = (time.time() - speech_start_time) * 1000

                            # TIER 2: Progressive transcription - short phrase pause (350ms)
                            if speech_duration_ms > long_speech_threshold_ms:
                                if silence_frames >= phrase_pause_frames:
                                    # Short pause detected during long speech
                                    time_since_last_chunk = time.time() - last_chunk_sent_time

                                    if time_since_last_chunk * 1000 >= long_speech_threshold_ms:
                                        logger.info(f"📝 Phrase pause ({phrase_pause_ms}ms) during long speech - sending progressive chunk")
                                        logger.debug(f"   Speech duration: {speech_duration_ms:.0f}ms, chunk interval: {time_since_last_chunk*1000:.0f}ms")

                                        # Send chunk WITHOUT setting flag (caller still speaking)
                                        if audio_buffer:
                                            audio_data = b''.join(audio_buffer)
                                            self.audio_in_queue.put(audio_data)
                                            logger.info(f"   Queued progressive chunk: {len(audio_buffer)} frames ({len(audio_data)} bytes)")

                                            # Clear buffer but continue collecting
                                            audio_buffer = []
                                            last_chunk_sent_time = time.time()
                                            silence_frames = 0  # Reset silence counter

                            # TIER 1: Normal pause detection (800ms configurable)
                            if silence_frames >= normal_pause_frames:
                                if speech_frames > 10:  # At least 200ms of speech
                                    # End of utterance detected
                                    logger.info(f"🔇 Normal pause ({normal_pause_ms}ms) detected - caller finished speaking")
                                    logger.info(f"   Total speech: {speech_frames} frames ({speech_duration_ms:.0f}ms)")

                                    # CRITICAL: Set silence flag - caller is silent NOW
                                    with self.playback_lock:
                                        self.caller_is_silent.set()
                                        logger.info("🟢 Silence flag SET - bot can speak now")

                                    # Send final chunk for transcription
                                    if audio_buffer:
                                        audio_data = b''.join(audio_buffer)
                                        self.audio_in_queue.put(audio_data)
                                        vad_chunk_count += 1
                                        logger.info(f"   Queued final utterance: {len(audio_buffer)} frames ({len(audio_data)} bytes)")
                                        audio_buffer = []

                                    # Reset state
                                    in_speech = False
                                    speech_frames = 0
                                    silence_frames = 0
                        else:
                            # Not in speech, just silence
                            if silence_frames == normal_pause_frames:
                                # Continuous silence - keep flag set
                                logger.debug(f"Continuous silence ({normal_pause_ms}ms) - flag remains SET")

                except Exception as e:
                    logger.error(f"Frame processing error: {e}")
                    time.sleep(0.1)

            # Save VAD chunk count to profiler
            if self.profiler:
                self.profiler.set_vad_chunks(vad_chunk_count)

            logger.info("Audio capture stopped")

        except Exception as e:
            logger.error(f"Audio capture error: {e}")

    def audio_playback_thread(self):
        """Play audio to phone line with conversation flow control"""
        logger.info("Audio playback thread started")

        try:
            # Use shared audio serial port
            audio_serial = self.audio_serial

            # Track if we're currently playing a message
            queue_was_empty = True

            while self.in_call:
                try:
                    # Check for new TTS files and queue them
                    tts_pattern = f"/tmp/tts_{self.call_id}_*.raw"
                    tts_files = sorted(glob.glob(tts_pattern))
                    for tts_file in tts_files:
                        try:
                            with open(tts_file, 'rb') as f:
                                audio_data = f.read()

                            # Validate audio data
                            if not audio_data or len(audio_data) == 0:
                                logger.warning(f"Empty TTS file: {tts_file} - skipping")
                                os.remove(tts_file)
                                continue

                            # Check for metadata (either direct or pending)
                            metadata = self.tts_metadata.get(tts_file)
                            if not metadata:
                                # Check for pending metadata (from TTS API call)
                                metadata = self.tts_metadata.get(f'pending_{self.call_id}')
                                if metadata:
                                    # Move from pending to file-specific
                                    self.tts_metadata[tts_file] = metadata
                                    del self.tts_metadata[f'pending_{self.call_id}']

                            # Log audio source and save to cache if needed
                            if metadata:
                                if metadata.get('from_cache', False):
                                    logger.info(f"🎵 Playing from CACHE: '{metadata['text'][:50]}...' ({len(audio_data)} bytes)")
                                else:
                                    logger.info(f"🎤 Playing from TTS ENGINE: '{metadata['text'][:50]}...' ({len(audio_data)} bytes)")
                                    # Save to cache for future use
                                    cache_path = self.get_cache_path(
                                        metadata['text'],
                                        metadata['format'],
                                        metadata['voice']
                                    )
                                    self.save_to_cache(cache_path, audio_data)
                            else:
                                logger.warning(f"⚠️ No metadata for TTS file: {tts_file} - playing anyway")

                            # Record outgoing TTS audio
                            if self.audio_recorder:
                                self.audio_recorder.record_outgoing_tts(audio_data)

                            # Queue audio chunks (dynamic size based on sample rate)
                            chunk_size = 1280 if self.sample_rate == 16000 else 640  # 40ms chunks (1280 for 16kHz, 640 for 8kHz)
                            for i in range(0, len(audio_data), chunk_size):
                                chunk = audio_data[i:i+chunk_size]
                                if chunk:  # Only queue non-empty chunks
                                    self.audio_out_queue.put(chunk)

                            # Track TTS generation timing (only for fresh TTS, not cache hits)
                            if self.profiler and metadata and not metadata.get('from_cache', False):
                                self.profiler.stop_timer('tts_generation', 'tts_audio_loaded')

                            # Clean up
                            os.remove(tts_file)  # Delete after queuing
                            if tts_file in self.tts_metadata:
                                del self.tts_metadata[tts_file]  # Clean up metadata
                        except Exception as e:
                            logger.error(f"Error loading TTS file {tts_file}: {e}")

                    if not self.audio_out_queue.empty():
                        # Check if this is start of a new message
                        is_new_message = queue_was_empty

                        if is_new_message:
                            # CRITICAL: Wait for PCM audio path to be ready (first data from ttyUSB4)
                            # This ensures the modem is actually ready to play audio
                            logger.info("📢 New message ready - waiting for PCM audio path...")
                            if not self.pcm_audio_ready.wait(timeout=3.0):
                                logger.error("❌ Timeout waiting for PCM audio - modem may not be ready!")
                                # Continue anyway, but audio might not work
                            else:
                                logger.info("✅ PCM audio path confirmed ready")

                            # CRITICAL: Wait for caller to stop speaking before playing
                            # The silence flag is SET when 800ms silence detected
                            # The silence flag is CLEARED when caller starts speaking
                            # The silence flag STAYS SET during entire silence period
                            logger.info("📢 Checking if caller is silent...")

                            # Check if caller is already silent (flag set)
                            if self.caller_is_silent.is_set():
                                logger.info("✅ Caller already silent - proceeding immediately")
                            else:
                                logger.info("⏳ Caller speaking - waiting for silence...")
                                # Wait up to 6 seconds for caller to stop speaking (short conversations)
                                if not self.caller_is_silent.wait(timeout=6.0):
                                    logger.warning("⚠️ Timeout waiting for silence - checking if caller still speaking...")

                                    # Double-check if caller is STILL speaking
                                    time_since_last_speech = time.time() - self.last_speech_time
                                    if time_since_last_speech < 2.0:
                                        logger.warning("Caller still speaking - waiting 2 more seconds...")
                                        time.sleep(2.0)
                                    else:
                                        logger.info("No recent speech detected - proceeding with playback")
                                else:
                                    logger.info("✅ Caller became silent - proceeding with playback")

                            # Check one more time if we should play
                            with self.playback_lock:
                                # If bot already speaking, don't interrupt ourselves
                                if self.bot_is_speaking:
                                    logger.debug("Bot already speaking - continuing")
                                else:
                                    # Mark that bot is now speaking
                                    self.bot_is_speaking = True
                                    logger.info("🔊 Bot started speaking - silence flag will be cleared if caller interrupts")

                                    # Start playback timing
                                    if self.profiler:
                                        self.profiler.start_timer('tts_playback')

                        # Get and play audio chunk
                        audio_chunk = self.audio_out_queue.get(timeout=0.1)

                        # Validate audio chunk
                        if audio_chunk is None or not isinstance(audio_chunk, bytes):
                            logger.warning(f"Invalid audio chunk type: {type(audio_chunk)}")
                            continue

                        if len(audio_chunk) == 0:
                            logger.debug("Empty audio chunk - skipping")
                            continue

                        # Write raw PCM bytes to serial port
                        # SIM7600 expects: 8kHz or 16kHz, 16-bit signed, mono, little-endian
                        # NOTE: TTS plays to completion regardless of caller interruption
                        audio_serial.write(audio_chunk)
                        logger.debug(f"Played {len(audio_chunk)} bytes to caller")

                        queue_was_empty = False

                    else:
                        # Queue is empty
                        if not queue_was_empty:
                            # Just finished playing a message
                            with self.playback_lock:
                                self.bot_is_speaking = False
                            logger.info("✅ Bot finished speaking")

                            # Stop playback timing
                            if self.profiler:
                                self.profiler.stop_timer('tts_playback', 'tts_playback_complete')

                        queue_was_empty = True
                        time.sleep(0.01)

                except queue.Empty:
                    if not queue_was_empty:
                        with self.playback_lock:
                            self.bot_is_speaking = False
                        logger.info("✅ Bot finished speaking")

                        # Stop playback timing
                        if self.profiler:
                            self.profiler.stop_timer('tts_playback', 'tts_playback_complete')

                    queue_was_empty = True
                    time.sleep(0.01)

                except Exception as e:
                    logger.error(f"Playback error: {e}")
                    with self.playback_lock:
                        self.bot_is_speaking = False
                    time.sleep(0.1)

            logger.info("Audio playback stopped")

        except Exception as e:
            logger.error(f"Audio playback error: {e}")
            with self.playback_lock:
                self.bot_is_speaking = False

    def transcription_thread(self):
        """Transcribe audio using Whisper"""
        logger.info("Transcription thread started")

        audio_buffer = []

        while self.in_call:
            try:
                # Collect audio chunks until we have enough for transcription
                # Run through Whisper
                # Send to VPS

                time.sleep(0.1)

            except Exception as e:
                logger.error(f"Transcription error: {e}")

    def request_tts(self, text, priority='normal'):
        """Request TTS from unified API with cache support"""
        try:
            # Get audio format and voice for cache lookup
            audio_format = self.voice_config.get('audio_format', self.get_audio_format_fallback())
            voice = self.voice_config.get('voice_settings', {}).get('voice', 'default')

            # Check cache first
            cache_path = self.get_cache_path(text, audio_format, voice)
            cached_audio = self.load_from_cache(cache_path)

            if cached_audio:
                # Cache hit! Write directly to /tmp file for playback thread
                timestamp = int(time.time() * 1000)
                tmp_file = f"/tmp/tts_{self.call_id}_{timestamp}.raw"

                with open(tmp_file, 'wb') as f:
                    f.write(cached_audio)

                logger.info(f"🚀 Cache hit! '{text[:50]}...' - instant playback ready")

                # Store metadata (mark as from_cache so playback thread doesn't re-cache)
                self.tts_metadata[tmp_file] = {
                    'text': text,
                    'voice': voice,
                    'format': audio_format,
                    'from_cache': True
                }

                # Still track timing for profiling
                if self.profiler:
                    self.profiler.log_event('tts_request_sent', {
                        'text_length': len(text),
                        'priority': priority,
                        'cache_hit': True
                    })
                return

            # Cache miss - call TTS API as normal

            # Store metadata with call_id as key (TTS API will create file with this call_id)
            # Playback thread will pick this up when it finds the file
            self.tts_metadata[f'pending_{self.call_id}'] = {
                'text': text,
                'voice': voice,
                'format': audio_format,
                'from_cache': False
            }

            payload = {
                'callId': self.call_id,
                'sessionId': self.session_id,
                'text': text,
                'action': 'speak',
                'priority': priority,
                'language': self.voice_config.get('language', 'en'),
                'audio_format': audio_format
            }

            response = requests.post(
                self.local_tts_api,
                json=payload,
                timeout=5
            )

            if response.status_code == 200:
                logger.info(f"TTS requested: {text[:50]}...")
                if self.profiler:
                    self.profiler.start_timer('tts_generation')
                    self.profiler.log_event('tts_request_sent', {
                        'text_length': len(text),
                        'priority': priority,
                        'cache_hit': False
                    })
            else:
                logger.error(f"TTS request failed: {response.status_code}")

        except Exception as e:
            logger.error(f"TTS request error: {e}")

    def cleanup_call(self):
        """Clean up resources after call ends"""
        logger.info("Cleaning up call resources...")

        # Stop audio threads
        self.in_call = False
        time.sleep(0.2)  # Give threads time to stop

        # Clear TTS metadata
        self.tts_metadata.clear()

        # Close audio serial port
        if hasattr(self, 'audio_serial') and self.audio_serial:
            try:
                self.audio_serial.close()
                logger.info("✅ Audio serial port closed")
            except Exception as e:
                logger.error(f"Error closing audio port: {e}")
            self.audio_serial = None

        # Clear queues
        while not self.audio_in_queue.empty():
            try:
                self.audio_in_queue.get_nowait()
            except:
                pass

        while not self.audio_out_queue.empty():
            try:
                self.audio_out_queue.get_nowait()
            except:
                pass

        # Stop audio recording
        if self.audio_recorder:
            self.audio_recorder.stop_all()
            logger.info("Audio recording stopped")

        # CRITICAL: Reset modem state for next call
        logger.info("Resetting modem for next call...")
        try:
            # Disable PCM
            self.send_at_command("AT+CPCMREG=0")
            time.sleep(0.1)

            # Hang up completely (in case line is still open)
            self.send_at_command("ATH")
            time.sleep(0.1)

            # Re-enable caller ID
            self.send_at_command("AT+CLIP=1")

            logger.info("✅ Modem reset complete - ready for next call")
        except Exception as e:
            logger.error(f"Error resetting modem: {e}")

        # Save profiler data
        if self.profiler:
            self.profiler.log_event('call_ending')
            output_file = self.profiler.save()
            logger.info(f"📊 Call profiling data saved to: {output_file}")

        logger.info("Call cleanup complete")

    def notify_vps(self, event_type, data):
        """Notify VPS about call events"""
        try:
            payload = {
                'event': event_type,
                'callId': self.call_id,
                'sessionId': self.session_id,
                'timestamp': time.time(),
                'data': data
            }

            response = requests.post(
                self.vps_webhook,
                json=payload,
                timeout=5
            )

            logger.info(f"VPS notified: {event_type}")

        except Exception as e:
            logger.error(f"VPS notification error: {e}")

    def monitor_modem(self):
        """Monitor for incoming calls and modem events"""
        logger.info("Starting modem monitor")

        while True:
            try:
                # Check if modem is initialized
                if self.ser is None:
                    # Check if port mapping exists
                    if not self.at_port:
                        # No port mapping - try to detect ports
                        if self.detect_sim7600_ports():
                            self.init_modem()
                        else:
                            time.sleep(5)
                            continue
                    else:
                        # Port mapping exists - initialize modem
                        logger.info("Port mapping loaded - initializing modem...")
                        if not self.init_modem():
                            self.init_retry_count += 1
                            logger.error(f"Failed to initialize modem (attempt {self.init_retry_count}/{self.max_init_retries})")

                            if self.init_retry_count >= self.max_init_retries:
                                logger.error(f"❌ Maximum initialization attempts ({self.max_init_retries}) reached")
                                logger.error("Modem initialization failed - stopping service")
                                sys.exit(1)

                            logger.info(f"Retrying in 5 seconds...")
                            time.sleep(5)
                            continue
                        else:
                            # Successful init - reset retry counter
                            self.init_retry_count = 0

                # Read unsolicited messages
                if self.ser and self.ser.in_waiting:
                    line = self.ser.readline().decode('utf-8', errors='ignore').strip()

                    if line:
                        logger.debug(f"Modem: {line}")

                        # Handle incoming call
                        if "RING" in line:
                            # Record ring time (for calculating when to answer)
                            ring_time = time.time()

                            # Extract caller ID from CLIP
                            clip_line = self.ser.readline().decode('utf-8', errors='ignore')
                            caller_id = "Unknown"
                            if "+CLIP:" in clip_line:
                                parts = clip_line.split(',')
                                if len(parts) > 0:
                                    caller_id = parts[0].split(':')[1].strip('"')

                            # Handle call (will answer based on answer_after_rings config)
                            self.handle_incoming_call(caller_id, ring_time)

                        # Handle call end
                        elif "NO CARRIER" in line or "BUSY" in line:
                            if self.in_call:
                                logger.info("Call ended")
                                self.cleanup_call()
                                self.notify_vps('call_ended', {})

                time.sleep(0.1)

            except Exception as e:
                logger.error(f"Monitor error: {e}")

                # If I/O error, close and reset serial port for reinitialization
                if "Input/output error" in str(e) or "Protocol error" in str(e):
                    logger.warning("Serial port error detected - closing and reinitializing...")
                    if self.ser:
                        try:
                            self.ser.close()
                        except:
                            pass
                        self.ser = None
                    time.sleep(3)
                else:
                    time.sleep(1)

def main():
    """Main entry point"""
    logger.info("="*60)
    logger.info("SIM7600 Voice Bot Starting")
    logger.info("="*60)
    logger.info("Waiting for SIM7600 modem connection...")

    bot = SIM7600VoiceBot()

    # CRITICAL: Pre-load VAD model at startup (instant with WebRTC VAD!)
    # This ensures VAD is ready for the first call
    logger.info("Loading WebRTC VAD at startup...")
    vad_loaded = bot.load_vad_model()
    if vad_loaded:
        logger.info("✅ WebRTC VAD loaded successfully")
    else:
        logger.warning("⚠️ WebRTC VAD not available - will use energy-based detection")

    try:
        bot.monitor_modem()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        # CRITICAL: Always restart smstools when exiting
        logger.info("Voice bot exiting - restoring SMS functionality...")
        try:
            bot.restart_smstools()
        except:
            # Last resort - try directly
            os.system('sudo systemctl start smstools')
        logger.info("Cleanup complete")
        sys.exit(0 if 'e' not in locals() else 1)

if __name__ == "__main__":
    main()