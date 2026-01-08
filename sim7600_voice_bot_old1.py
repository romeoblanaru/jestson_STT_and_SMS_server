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
        self.sample_rate = 8000  # 8kHz for telephony
        self.channels = 1  # Mono
        self.chunk_size = 320  # 20ms chunks at 8kHz

        # Call state
        self.in_call = False
        self.call_id = None
        self.session_id = None

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
        # Typical SIM7600 creates multiple ttyUSB ports:
        # ttyUSB0 - Diagnostic
        # ttyUSB1 - GPS NMEA
        # ttyUSB2 - AT command
        # ttyUSB3 - PPP modem
        # ttyUSB4 - Audio/PCM (if available)

        ports = []
        for i in range(5):
            port = f"/dev/ttyUSB{i}"
            if os.path.exists(port):
                ports.append(port)
                logger.info(f"Found port: {port}")

        if len(ports) >= 3:
            # Assign ports based on typical SIM7600 layout
            self.at_port = ports[2] if len(ports) > 2 else ports[0]
            self.audio_port = ports[4] if len(ports) > 4 else ports[1]
            self.ppp_port = ports[3] if len(ports) > 3 else ports[-1]

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
        # They don't interfere - both can run simultaneously

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

            # Don't set ATS0 here - will be configured on RING based on fresh config
            # This allows dynamic answer_after_rings including -1 (don't answer)

            logger.info("SIM7600 initialized for voice calls (ATS0 will be set on RING)")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize modem: {e}")
            return False

    def send_at_command(self, command, timeout=1):
        """Send AT command and get response"""
        try:
            self.ser.write(f"{command}\r\n".encode())
            time.sleep(0.1)
            response = self.ser.read(self.ser.in_waiting or 1).decode('utf-8', errors='ignore')
            logger.debug(f"AT: {command} -> {response.strip()}")
            return response
        except Exception as e:
            logger.error(f"AT command error: {e}")
            return ""

    def handle_incoming_call(self, caller_id):
        """Handle incoming call"""
        logger.info(f"📞 RING detected from {caller_id}")

        # CRITICAL: Fetch fresh voice config from VPS IMMEDIATELY
        logger.info("Fetching fresh voice configuration from VPS...")
        if not self.fetch_voice_config_from_vps():
            logger.error("Failed to fetch voice config - using fallback")

        # Check answer_after_rings setting
        answer_after_rings = self.voice_config.get('answer_after_rings', 3)
        logger.info(f"Answer setting: {answer_after_rings} rings")

        if answer_after_rings == -1:
            logger.info("🚫 answer_after_rings = -1: NOT answering this call")
            # Send notification to VPS but don't answer
            self.notify_vps('call_rejected', {
                'caller': caller_id,
                'reason': 'answer_after_rings set to -1'
            })
            return  # Don't answer

        # Configure auto-answer based on fetched config
        logger.info(f"Configuring modem to answer after {answer_after_rings} rings...")
        self.send_at_command(f"ATS0={answer_after_rings}")

        # Wait for configured rings then answer
        logger.info(f"Waiting for {answer_after_rings} rings...")
        # Note: The modem will auto-answer due to ATS0 setting

        # Generate call and session IDs
        self.call_id = f"call_{int(time.time())}"
        self.session_id = f"session_{int(time.time())}"

        # Set call state
        self.in_call = True
        logger.info(f"✅ Call answered: {self.call_id}")

        # CRITICAL: Enable PCM audio after call connects
        logger.info("Enabling PCM audio...")
        self.send_at_command("AT+CPCMREG=1")
        time.sleep(0.5)  # Wait for PCM to initialize

        # VAD should already be loaded at startup (if not, skip it for this call)
        if self.vad is None:
            logger.warning("WebRTC VAD not loaded - will use fallback energy detection")

        # Reset conversation state
        # IMPORTANT: Start with caller_is_silent SET (assume silence when call connects)
        # This allows welcome message to play immediately
        # Flag will be cleared as soon as caller speaks
        self.caller_is_silent.set()
        self.bot_is_speaking = False
        self.last_speech_time = 0
        logger.info("Conversation state initialized: caller_is_silent=True (ready for welcome message)")

        # Open audio serial port (shared by capture and playback threads)
        if not self.audio_port:
            logger.error("Audio port not configured - cannot handle audio!")
            return

        try:
            self.audio_serial = serial.Serial(
                self.audio_port,  # /dev/ttyUSB4
                baudrate=115200,
                timeout=0.1
            )
            logger.info(f"✅ Audio serial port opened: {self.audio_port}")
        except Exception as e:
            logger.error(f"Failed to open audio port: {e}")
            self.in_call = False
            return

        # Start audio threads
        threading.Thread(target=self.audio_capture_thread, daemon=True).start()
        threading.Thread(target=self.audio_playback_thread, daemon=True).start()
        threading.Thread(target=self.transcription_thread, daemon=True).start()

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

            while self.in_call:
                try:
                    # Read one frame (20ms)
                    frame = audio_serial.read(frame_size)

                    if len(frame) < frame_size:
                        # Not enough data yet
                        time.sleep(0.01)
                        continue

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
                            # Queue audio chunks (in 640-byte chunks to match frame size)
                            chunk_size = 640  # 40ms at 8kHz
                            for i in range(0, len(audio_data), chunk_size):
                                self.audio_out_queue.put(audio_data[i:i+chunk_size])
                            logger.info(f"Queued TTS audio from {tts_file}: {len(audio_data)} bytes")
                            os.remove(tts_file)  # Delete after queuing
                        except Exception as e:
                            logger.error(f"Error loading TTS file {tts_file}: {e}")

                    if not self.audio_out_queue.empty():
                        # Check if this is start of a new message
                        is_new_message = queue_was_empty

                        if is_new_message:
                            # CRITICAL: Wait for caller to stop speaking before playing
                            # The silence flag is SET when 800ms silence detected
                            # The silence flag is CLEARED when caller starts speaking
                            # The silence flag STAYS SET during entire silence period
                            logger.info("📢 New message ready - checking if caller is silent...")

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

                        # Get and play audio chunk
                        audio_chunk = self.audio_out_queue.get(timeout=0.1)

                        # Write raw PCM bytes to serial port
                        # SIM7600 expects: 8kHz, 16-bit signed, mono, little-endian
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

                        queue_was_empty = True
                        time.sleep(0.01)

                except queue.Empty:
                    if not queue_was_empty:
                        with self.playback_lock:
                            self.bot_is_speaking = False
                        logger.info("✅ Bot finished speaking")
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
        """Request TTS from unified API"""
        try:
            payload = {
                'callId': self.call_id,
                'sessionId': self.session_id,
                'text': text,
                'action': 'speak',
                'priority': priority,
                'language': self.voice_config.get('language', 'en')
            }

            response = requests.post(
                self.local_tts_api,
                json=payload,
                timeout=5
            )

            if response.status_code == 200:
                logger.info(f"TTS requested: {text[:50]}...")
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
                            # Extract caller ID from CLIP
                            clip_line = self.ser.readline().decode('utf-8', errors='ignore')
                            caller_id = "Unknown"
                            if "+CLIP:" in clip_line:
                                parts = clip_line.split(',')
                                if len(parts) > 0:
                                    caller_id = parts[0].split(':')[1].strip('"')

                            # Answer call
                            self.send_at_command("ATA")
                            self.handle_incoming_call(caller_id)

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