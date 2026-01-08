#!/usr/bin/env python3
"""
SIM7600G-H Professional Voice Bot
Implements proper multi-port architecture and pre-configured answering
"""

import os
import sys
import time
import json
import serial
import logging
import threading
import subprocess
import requests
import wave
import struct
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import queue
import webrtcvad

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/voice_bot/sim7600_professional.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('sim7600_pro')

class SIM7600VoiceBot:
    """Professional SIM7600 Voice Bot with proper architecture"""

    def __init__(self):
        # Port configuration based on documentation
        self.at_port = '/dev/ttyUSB2'      # Primary AT port (for SMS/init)
        self.call_port = '/dev/ttyUSB3'    # Secondary AT port (for calls)
        self.audio_port = '/dev/ttyUSB4'   # PCM audio port

        # Serial connections
        self.at_serial = None
        self.call_serial = None
        self.audio_serial = None

        # Voice configuration
        self.voice_config = self.load_cached_config()
        self.vpn_ip = self.get_vpn_ip()

        # Call state
        self.in_call = False
        self.call_active = threading.Event()
        self.call_id = None
        self.caller_number = None

        # Audio management
        self.audio_queue = queue.Queue()
        self.recording_enabled = True
        self.recordings_dir = Path('/home/rom/Audio_wav/debug')
        self.recordings_dir.mkdir(parents=True, exist_ok=True)

        # VAD configuration
        self.vad = webrtcvad.Vad(2)  # Mode 2: balanced
        self.frame_duration_ms = 40  # 40ms frames for better VAD accuracy
        self.frame_size = int(8000 * self.frame_duration_ms / 1000) * 2  # 640 bytes

        # Threads
        self.ring_monitor_thread = None
        self.audio_capture_thread = None
        self.audio_playback_thread = None
        self.recording_thread = None

        logger.info("=" * 60)
        logger.info("SIM7600 Professional Voice Bot Initialized")
        logger.info(f"AT Port: {self.at_port}")
        logger.info(f"Call Port: {self.call_port}")
        logger.info(f"Audio Port: {self.audio_port}")
        logger.info("=" * 60)

    def get_vpn_ip(self) -> str:
        """Get VPN IP address"""
        try:
            result = subprocess.run(
                ['ip', '-4', 'addr', 'show', 'wg0'],
                capture_output=True, text=True, timeout=2
            )
            for line in result.stdout.split('\n'):
                if 'inet ' in line:
                    return line.split()[1].split('/')[0]
        except:
            pass
        return '10.100.0.11'

    def load_cached_config(self) -> Dict:
        """Load cached voice configuration"""
        try:
            with open('/home/rom/voice_config.json', 'r') as f:
                config = json.load(f)
                logger.info(f"Loaded cached config: {config.get('language')}, rings: {config.get('answer_after_rings')}")
                return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {
                'language': 'en',
                'answer_after_rings': 2,
                'welcome_message': 'Hello, how can I help you?'
            }

    def fetch_voice_config_from_vps(self) -> bool:
        """Fetch fresh voice configuration from VPS"""
        try:
            url = f"http://my-bookings.co.uk/webhooks/get_voice_config.php?ip={self.vpn_ip}&include_key=1"
            logger.info(f"Fetching voice config from: {url}")

            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                self.voice_config = response.json()
                # Save to cache
                with open('/home/rom/voice_config.json', 'w') as f:
                    json.dump(self.voice_config, f, indent=2)
                logger.info(f"✅ Fresh config fetched: rings={self.voice_config.get('answer_after_rings')}")
                return True
        except Exception as e:
            logger.error(f"Failed to fetch config from VPS: {e}")
        return False

    def send_at_command(self, port: serial.Serial, command: str, timeout: float = 1.0) -> str:
        """Send AT command and get response"""
        try:
            port.write(f"{command}\r\n".encode())
            port.flush()

            start_time = time.time()
            response = ""

            while time.time() - start_time < timeout:
                if port.in_waiting:
                    chunk = port.read(port.in_waiting).decode('utf-8', errors='ignore')
                    response += chunk
                    if 'OK' in response or 'ERROR' in response:
                        break
                time.sleep(0.01)

            clean_response = response.replace('\r\n', ' ').strip()
            logger.debug(f"AT: {command} -> {clean_response[:50]}")
            return response

        except Exception as e:
            logger.error(f"AT command error: {e}")
            return ""

    def initialize_modem(self) -> bool:
        """Initialize modem with professional configuration"""
        try:
            # Stop SMSTools temporarily for configuration
            logger.info("Stopping SMSTools for modem configuration...")
            subprocess.run(['sudo', 'systemctl', 'stop', 'smstools'], timeout=5)
            time.sleep(2)

            # Open AT port for initialization
            self.at_serial = serial.Serial(
                self.at_port, 115200, timeout=1,
                xonxoff=False, rtscts=False, dsrdtr=False
            )

            # Basic initialization
            self.send_at_command(self.at_serial, "AT")
            self.send_at_command(self.at_serial, "ATE0")  # Disable echo

            # Enable caller ID
            self.send_at_command(self.at_serial, "AT+CLIP=1")

            # Configure audio codec (8kHz PCM)
            self.send_at_command(self.at_serial, "AT+CSDVC=2")  # Speaker
            self.send_at_command(self.at_serial, "AT+CSDVC=1")  # Handset

            # PRE-CONFIGURE AUTO-ANSWER based on cached config
            answer_rings = self.voice_config.get('answer_after_rings', 2)
            if answer_rings > 0:
                logger.info(f"⚡ Pre-configuring auto-answer: ATS0={answer_rings}")
                self.send_at_command(self.at_serial, f"ATS0={answer_rings}")
            else:
                logger.info("Auto-answer disabled (ATS0=0)")
                self.send_at_command(self.at_serial, "ATS0=0")

            # Close AT port to allow SMSTools to use it
            self.at_serial.close()
            self.at_serial = None

            # Open call control port
            self.call_serial = serial.Serial(
                self.call_port, 115200, timeout=0.1,
                xonxoff=False, rtscts=False, dsrdtr=False
            )

            # Test call port
            response = self.send_at_command(self.call_serial, "AT")
            if "OK" not in response:
                logger.warning(f"Call port {self.call_port} may not support AT commands")

            # Restart SMSTools
            logger.info("Restarting SMSTools...")
            subprocess.run(['sudo', 'systemctl', 'start', 'smstools'], timeout=5)

            logger.info("✅ Modem initialized with pre-configured answering")
            return True

        except Exception as e:
            logger.error(f"Modem initialization failed: {e}")
            # Ensure SMSTools is restarted
            subprocess.run(['sudo', 'systemctl', 'start', 'smstools'], timeout=5)
            return False

    def monitor_incoming_calls(self):
        """Monitor for incoming calls on call port"""
        logger.info("📞 Monitoring for incoming calls...")

        buffer = ""
        while True:
            try:
                if self.call_serial and self.call_serial.in_waiting:
                    data = self.call_serial.read(self.call_serial.in_waiting)
                    buffer += data.decode('utf-8', errors='ignore')

                    # Check for RING
                    if 'RING' in buffer:
                        logger.info("🔔 RING detected!")

                        # Extract caller ID if present
                        if '+CLIP:' in buffer:
                            try:
                                clip_start = buffer.index('+CLIP:')
                                clip_line = buffer[clip_start:buffer.index('\r', clip_start)]
                                self.caller_number = clip_line.split('"')[1]
                                logger.info(f"📞 Incoming call from: {self.caller_number}")
                            except:
                                self.caller_number = "Unknown"

                        # Fetch fresh config on RING (but ATS0 already set!)
                        self.fetch_voice_config_from_vps()

                        # Check if we should reject (-1 means don't answer)
                        if self.voice_config.get('answer_after_rings') == -1:
                            logger.info("🚫 Rejecting call (answer_after_rings = -1)")
                            self.send_at_command(self.call_serial, "ATH")
                            buffer = ""
                            continue

                        # Handle the call (ATS0 will auto-answer based on pre-configuration!)
                        self.handle_incoming_call()
                        buffer = ""

                    # Clean buffer if too large
                    if len(buffer) > 1000:
                        buffer = buffer[-500:]

                time.sleep(0.1)

            except Exception as e:
                logger.error(f"Call monitoring error: {e}")
                time.sleep(1)

    def handle_incoming_call(self):
        """Handle incoming call with proper audio"""
        try:
            self.in_call = True
            self.call_active.set()
            self.call_id = f"call_{int(time.time())}"

            logger.info(f"✅ Call will auto-answer (pre-configured ATS0)")

            # Wait for VOICE CALL: BEGIN or connection
            time.sleep(2)

            # Enable PCM audio on audio port
            logger.info("Enabling PCM audio...")
            self.send_at_command(self.call_serial, "AT+CPCMREG=1")

            # Open audio port
            self.audio_serial = serial.Serial(
                self.audio_port, 115200, timeout=0.1,
                xonxoff=False, rtscts=False, dsrdtr=False
            )

            # Start audio threads
            self.start_audio_processing()

            # Play welcome message
            self.play_welcome_message()

            # Monitor call status
            self.monitor_call_status()

        except Exception as e:
            logger.error(f"Call handling error: {e}")
        finally:
            self.end_call()

    def start_audio_processing(self):
        """Start audio capture, playback, and recording threads"""
        # Audio capture thread
        self.audio_capture_thread = threading.Thread(
            target=self.audio_capture_worker,
            name="AudioCapture"
        )
        self.audio_capture_thread.daemon = True
        self.audio_capture_thread.start()

        # Audio playback thread
        self.audio_playback_thread = threading.Thread(
            target=self.audio_playback_worker,
            name="AudioPlayback"
        )
        self.audio_playback_thread.daemon = True
        self.audio_playback_thread.start()

        # Recording thread (saves to WAV)
        if self.recording_enabled:
            self.recording_thread = threading.Thread(
                target=self.audio_recording_worker,
                name="AudioRecording"
            )
            self.recording_thread.daemon = True
            self.recording_thread.start()

        logger.info("✅ Audio processing started")

    def audio_capture_worker(self):
        """Capture audio from caller and process with VAD"""
        logger.info("Starting audio capture...")

        audio_buffer = bytearray()
        silence_frames = 0

        try:
            while self.call_active.is_set():
                if self.audio_serial and self.audio_serial.in_waiting:
                    # Read available audio
                    chunk = self.audio_serial.read(self.audio_serial.in_waiting)
                    audio_buffer.extend(chunk)

                    # Process complete frames
                    while len(audio_buffer) >= self.frame_size:
                        frame = bytes(audio_buffer[:self.frame_size])
                        audio_buffer = audio_buffer[self.frame_size:]

                        # Save for recording
                        if self.recording_enabled:
                            self.audio_queue.put(('caller', frame))

                        # VAD processing
                        try:
                            is_speech = self.vad.is_speech(frame, 8000)
                            if is_speech:
                                silence_frames = 0
                            else:
                                silence_frames += 1
                                if silence_frames > 20:  # 800ms silence
                                    logger.debug("Caller silent for 800ms")
                        except:
                            pass

                time.sleep(0.01)

        except Exception as e:
            logger.error(f"Audio capture error: {e}")

    def audio_playback_worker(self):
        """Handle audio playback to caller"""
        logger.info("Starting audio playback...")

        try:
            while self.call_active.is_set():
                # Check for TTS files to play
                tts_files = sorted(Path('/tmp').glob(f'tts_{self.call_id}_*.raw'))

                for tts_file in tts_files:
                    try:
                        with open(tts_file, 'rb') as f:
                            audio_data = f.read()

                        # Play audio
                        if self.audio_serial:
                            self.audio_serial.write(audio_data)
                            self.audio_serial.flush()

                            # Save for recording
                            if self.recording_enabled:
                                self.audio_queue.put(('bot', audio_data))

                        # Delete played file
                        tts_file.unlink()
                        logger.info(f"Played TTS: {tts_file.name}")

                    except Exception as e:
                        logger.error(f"TTS playback error: {e}")

                time.sleep(0.1)

        except Exception as e:
            logger.error(f"Playback error: {e}")

    def audio_recording_worker(self):
        """Save audio to WAV files for debugging"""
        logger.info("Starting audio recording...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        caller_wav = self.recordings_dir / f"{self.call_id}_{timestamp}_caller.wav"
        bot_wav = self.recordings_dir / f"{self.call_id}_{timestamp}_bot.wav"

        caller_frames = []
        bot_frames = []

        try:
            while self.call_active.is_set() or not self.audio_queue.empty():
                try:
                    source, audio_data = self.audio_queue.get(timeout=0.5)

                    if source == 'caller':
                        caller_frames.append(audio_data)
                    elif source == 'bot':
                        bot_frames.append(audio_data)

                except queue.Empty:
                    continue

            # Save caller audio
            if caller_frames:
                with wave.open(str(caller_wav), 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(8000)
                    wf.writeframes(b''.join(caller_frames))
                logger.info(f"✅ Saved caller audio: {caller_wav}")

            # Save bot audio
            if bot_frames:
                with wave.open(str(bot_wav), 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(8000)
                    wf.writeframes(b''.join(bot_frames))
                logger.info(f"✅ Saved bot audio: {bot_wav}")

        except Exception as e:
            logger.error(f"Recording error: {e}")

    def play_welcome_message(self):
        """Generate and queue welcome message"""
        try:
            message = self.voice_config.get('welcome_message', 'Hello')
            logger.info(f"Generating welcome: {message}")

            # Call TTS API
            tts_url = "http://10.100.0.11:8070/tts"
            response = requests.post(
                tts_url,
                json={
                    'text': message,
                    'language': self.voice_config.get('language', 'en'),
                    'voice_config': self.voice_config
                },
                timeout=5
            )

            if response.status_code == 200:
                # Save TTS audio
                timestamp = int(time.time() * 1000)
                tts_file = f'/tmp/tts_{self.call_id}_{timestamp}.raw'

                with open(tts_file, 'wb') as f:
                    f.write(response.content)

                logger.info(f"✅ Welcome message ready: {tts_file}")

        except Exception as e:
            logger.error(f"Welcome message error: {e}")

    def monitor_call_status(self):
        """Monitor call until hangup"""
        try:
            while self.call_active.is_set():
                # Check for hangup
                response = self.send_at_command(self.call_serial, "AT+CLCC")
                if "OK" in response and "+CLCC:" not in response:
                    logger.info("Call ended")
                    break

                time.sleep(2)

        except Exception as e:
            logger.error(f"Call monitoring error: {e}")

    def end_call(self):
        """Clean up after call ends"""
        try:
            logger.info("Ending call...")

            # Disable PCM audio
            if self.call_serial:
                self.send_at_command(self.call_serial, "AT+CPCMREG=0")
                self.send_at_command(self.call_serial, "ATH")

            # Stop threads
            self.call_active.clear()

            # Close audio port
            if self.audio_serial:
                self.audio_serial.close()
                self.audio_serial = None

            # Reset state
            self.in_call = False
            self.call_id = None
            self.caller_number = None

            # Notify VPS
            self.notify_vps_call_ended()

            logger.info("✅ Call cleanup complete")

        except Exception as e:
            logger.error(f"Call cleanup error: {e}")

    def notify_vps_call_ended(self):
        """Notify VPS that call ended"""
        try:
            url = "http://10.100.0.1:8088/webhook/phone_call/receive"
            data = {
                'event': 'call_ended',
                'caller': self.caller_number,
                'call_id': self.call_id,
                'gateway_ip': self.vpn_ip
            }
            requests.post(url, json=data, timeout=2)
        except:
            pass

    def run(self):
        """Main run loop"""
        try:
            # Initialize modem
            if not self.initialize_modem():
                logger.error("Failed to initialize modem")
                return

            # Start call monitoring
            self.ring_monitor_thread = threading.Thread(
                target=self.monitor_incoming_calls,
                name="RingMonitor"
            )
            self.ring_monitor_thread.daemon = False
            self.ring_monitor_thread.start()

            logger.info("🚀 Voice bot running...")

            # Keep running
            self.ring_monitor_thread.join()

        except KeyboardInterrupt:
            logger.info("Shutting down...")
        except Exception as e:
            logger.error(f"Runtime error: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.at_serial:
                self.at_serial.close()
            if self.call_serial:
                self.call_serial.close()
            if self.audio_serial:
                self.audio_serial.close()

            logger.info("Cleanup complete")

        except Exception as e:
            logger.error(f"Cleanup error: {e}")

def main():
    """Main entry point"""
    bot = SIM7600VoiceBot()
    bot.run()

if __name__ == "__main__":
    main()