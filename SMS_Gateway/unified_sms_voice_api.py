#!/usr/bin/env python3
"""
Unified Communication API for VPS
Handles SMS sending and Phone Call TTS commands
Uses binary UTF-16-BE encoding for Unicode messages
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import time
import logging
import subprocess
import threading
import queue
import sys
import numpy as np
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, '/home/rom')
sys.path.insert(0, '/home/rom/SMS_Gateway')

# Import phone number normalization
from normalize_phone import normalize_phone_number, get_gateway_country_code

# Import voice modules (loaded on demand)
voice_config_loaded = False
tts_provider = None
tts_processor = None
tts_queue = queue.Queue()
hangup_queue = queue.Queue()
response_stats = {}
voice_config = None

# SMS queuing system for async processing
sms_queue = queue.Queue()
sms_processor = None

# Set up logging (writes to RAM disk)
from logging.handlers import RotatingFileHandler

log_file_path = '/var/log/voice_bot_ram/unified_api.log'
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# File handler (RAM disk)
file_handler = RotatingFileHandler(
    log_file_path,
    maxBytes=10*1024*1024,  # 10MB
    backupCount=3
)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

# Console handler (for systemd journal)
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Only add handlers if not already present (prevents duplicates)
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

logger.info("Unified API logging initialized (RAM disk + journal)")

# Monitoring functions removed - moved to port 8070 monitoring webhook
# All modem monitoring should be done via port 8070, not the SMS gateway

def split_sms_intelligently(message, max_length=70):
    """
    Split SMS message intelligently at natural boundaries

    NOTE: This function was implemented because the SIM7600G-H modem firmware
    has a critical bug with multipart UCS-2 messages. The modem hangs when
    SMSTools3 tries to send concatenated SMS (using UDH headers). To work around
    this, we split long messages at the API level and send them as separate
    single-part SMS with 2-second delays between parts.

    Splitting algorithm:
    Step 0: PRIORITY SPLIT - Split at '?', '\n', '\r', ' 1.', ' 2.', etc. ANYWHERE in message
            - '?', '\n', '\r' - delimiter stays with PRECEDING text
            - ' 1.', ' 2.', ' 3.' (space+digit+dot) - delimiter stays with FOLLOWING text
            After splitting, check each part for length and apply Steps 1-4 if needed
    Step 1: Look backwards from chr 70 to chr 15 for punctuation (., !, ;)
            - EXCLUDE dots preceded by digits (e.g., "30.00" or "1.")
    Step 2: If not found, look backwards from chr 70 to chr 15 for comma (,)
    Step 3: If not found, look backwards from chr 70 to chr 15 for space
    Step 4: If nothing found, hard split at max_length

    Args:
        message: Text to split
        max_length: Max characters per part (default 70 for UCS2)
    Returns:
        List of message parts
    """
    if len(message) <= max_length:
        return [message]

    # Step 0: PRIORITY SPLIT on '?', '\n', '\r', ' 1.', ' 2.', etc. anywhere in message
    import re
    # Pattern explanation:
    # - (\s\d\.) matches space+digit+dot for numbered lists (e.g., ' 1.', ' 2.')
    # - ([\n\r?]) matches newline/carriage return/question mark
    priority_chunks = re.split(r'(\s\d\.|\n|\r|\?)', message)

    # Reconstruct chunks with delimiters
    # - For \n, \r, ?: delimiter stays with PRECEDING text
    # - For ' 1.', ' 2.', etc.: delimiter stays with FOLLOWING text
    initial_parts = []
    temp = ""
    for i, part in enumerate(priority_chunks):
        if part in ['\n', '\r', '?']:
            # These delimiters stay with PRECEDING text
            temp += part
            if temp.strip():  # Only add non-empty parts
                initial_parts.append(temp)
            temp = ""
        elif part and re.match(r'\s\d\.', part):
            # Numbered list delimiter (e.g., ' 1.', ' 2.') stays with FOLLOWING text
            if temp.strip():
                initial_parts.append(temp)
            temp = part  # Start new part WITH the delimiter
        else:
            # Regular text
            temp += part

    if temp.strip():  # Add any remaining text
        initial_parts.append(temp)

    # If no priority split happened, use the whole message
    if not initial_parts:
        initial_parts = [message]

    # Now apply length-based splitting (Steps 1-4) to each chunk
    final_parts = []
    for chunk in initial_parts:
        final_parts.extend(_split_by_length(chunk.strip(), max_length))

    return final_parts


def _split_by_length(text, max_length):
    """
    Split text by length at intelligent boundaries (Steps 1-4)
    Helper function for split_sms_intelligently
    """
    if len(text) <= max_length:
        return [text]

    parts = []
    remaining = text
    min_search_pos = 15  # Don't split too early

    while remaining:
        if len(remaining) <= max_length:
            parts.append(remaining)
            break

        chunk = remaining[:max_length]
        split_pos = -1

        # Step 1: Look backwards for punctuation (., !, ;)
        # EXCLUDE dots preceded by digits (30.00, 1., etc.)
        for i in range(len(chunk) - 1, min_search_pos - 1, -1):
            if chunk[i] in ['.', '!', ';']:
                # Special handling for dots
                if chunk[i] == '.':
                    # Check if preceded by a digit (skip if it's part of a number)
                    if i > 0 and chunk[i-1].isdigit():
                        continue  # Skip this dot, it's in a number like "30.00" or "1."
                split_pos = i + 1  # Include the punctuation
                break

        # Step 2: Look backwards for comma
        if split_pos == -1:
            for i in range(len(chunk) - 1, min_search_pos - 1, -1):
                if chunk[i] == ',':
                    split_pos = i + 1
                    break

        # Step 3: Look backwards for space
        if split_pos == -1:
            for i in range(len(chunk) - 1, min_search_pos - 1, -1):
                if chunk[i] == ' ':
                    split_pos = i + 1
                    break

        # Step 4: Hard split at max_length
        if split_pos == -1:
            split_pos = max_length

        parts.append(remaining[:split_pos].rstrip())
        remaining = remaining[split_pos:].lstrip()

    return parts

def load_voice_config():
    """Load voice configuration for phone call handling"""
    global voice_config_loaded, tts_provider, voice_config

    try:
        # Load config with API key
        config_file = '/home/rom/voice_config.json'
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                voice_config = json.load(f)
                logger.info(f"Loaded voice config: {voice_config.get('tts_model')} for {voice_config.get('language')}")
        else:
            # Try runtime config as fallback
            with open('/home/rom/runtime_voice_config.json', 'r') as f:
                voice_config = json.load(f)
                logger.warning("Using runtime config (may lack API key)")

        # Initialize TTS provider
        from voice_config_manager import VoiceConfigManager
        manager = VoiceConfigManager()
        manager.config = voice_config
        tts_provider = manager.get_tts_provider()

        if tts_provider:
            voice_config_loaded = True
            logger.info("Voice configuration loaded successfully")
            return True
        else:
            logger.error("Failed to initialize TTS provider")
            return False

    except Exception as e:
        logger.error(f"Failed to load voice config: {e}")
        return False

class SMSProcessor(threading.Thread):
    """Background thread for async processing of SMS messages"""

    def __init__(self):
        super().__init__(daemon=True)
        self.running = True

    def run(self):
        """Process SMS queue with delays between parts"""
        logger.info("SMS processor thread started")

        while self.running:
            try:
                # Get request with timeout
                request = sms_queue.get(timeout=1)

                recipient = request['recipient']
                message_parts = request['message_parts']
                needs_unicode = request['needs_unicode']
                timestamp = request['timestamp']
                pid = request['pid']

                logger.info(f"Processing {len(message_parts)} SMS parts for {recipient}")

                files_created = []

                for part_num, part_text in enumerate(message_parts, 1):
                    # Create filename with part number if multipart
                    if len(message_parts) > 1:
                        filename = f"/var/spool/sms/outgoing/api_{timestamp}_{pid}_part{part_num}"
                    else:
                        filename = f"/var/spool/sms/outgoing/api_{timestamp}_{pid}"

                    if needs_unicode:
                        # Write with binary UTF-16-BE for Unicode
                        with open(filename, 'wb') as f:
                            f.write(f"To: {recipient}\n".encode('ascii'))
                            f.write(b"Alphabet: UCS2\n\n")
                            f.write(part_text.encode('utf-16-be'))
                    else:
                        # ASCII only - use text mode
                        with open(filename, 'w') as f:
                            f.write(f"To: {recipient}\n\n{part_text}")

                    os.chmod(filename, 0o666)
                    files_created.append(filename)

                    # Save message to cache file for sms_watch.sh to display
                    cache_dir = "/tmp/sms_msg_cache"
                    os.makedirs(cache_dir, exist_ok=True)
                    cache_filename = os.path.basename(filename) + ".txt"
                    cache_path = os.path.join(cache_dir, cache_filename)
                    with open(cache_path, 'w', encoding='utf-8') as f:
                        f.write(part_text)
                    os.chmod(cache_path, 0o666)

                    # Log more chars (100) so each part shows unique content in monitoring
                    logger.info(f"SMS queued: {recipient} - Part {part_num}/{len(message_parts)} - {part_text[:100]} (Unicode: {needs_unicode})")

                    # Add 1.5-second delay between parts (except after last part)
                    if part_num < len(message_parts):
                        time.sleep(1.5)

                logger.info(f"SMS processing complete for {recipient}: {len(files_created)} files created")

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in SMS processing: {e}")

    def stop(self):
        """Stop processor thread"""
        self.running = False

class TTSProcessor(threading.Thread):
    """Background thread for processing TTS requests"""

    def __init__(self, tts_provider):
        super().__init__(daemon=True)
        self.tts_provider = tts_provider
        self.running = True

    def run(self):
        """Process TTS queue"""
        logger.info("TTS processor thread started")

        while self.running:
            try:
                # Get request with timeout
                request = tts_queue.get(timeout=1)

                call_id = request['call_id']
                text = request['text']
                language = request.get('language')

                # Update language if needed
                if language and language != self.tts_provider.language:
                    self.tts_provider.language = language

                logger.info(f"Processing TTS for call {call_id}: {text[:50]}...")

                # Stream synthesis
                start_time = time.time()
                chunk_count = 0
                audio_chunks = []
                for audio_chunk in self.tts_provider.synthesize_stream(text):
                    audio_chunks.append(audio_chunk)
                    chunk_count += 1

                total_time = time.time() - start_time
                logger.info(f"TTS complete: {chunk_count} chunks in {total_time:.2f}s")

                # Save audio to file for voice bot to play
                if audio_chunks:
                    # Convert float32 numpy arrays to int16 PCM
                    audio_float32 = np.concatenate(audio_chunks)  # Combine all chunks
                    audio_int16 = (audio_float32 * 32767).astype(np.int16)  # Convert to int16
                    audio_bytes = audio_int16.tobytes()  # Convert to bytes

                    tts_file = f"/tmp/tts_{call_id}_{int(time.time()*1000)}.raw"
                    with open(tts_file, 'wb') as f:
                        f.write(audio_bytes)
                    logger.info(f"TTS audio saved to {tts_file} for playback ({len(audio_bytes)} bytes)")

                # Update stats
                if call_id in response_stats:
                    response_stats[call_id]['last_tts_time'] = total_time

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in TTS processing: {e}")

    def stop(self):
        """Stop processor thread"""
        self.running = False

class SMSHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/phone_call':
            # Handle phone call TTS commands
            self.handle_phone_call()
        elif self.path == '/phone_call/status':
            # Handle status request for phone calls
            self.handle_phone_status()
        elif self.path == '/send' or self.path == '/send_sms' or self.path == '/pi_send_message':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                recipient = data.get('to', '')  # Keep the + prefix for all numbers (portable across countries)
                message = data.get('message', '')

                # Normalize phone number using gateway's country code
                if recipient:
                    original_recipient = recipient
                    default_cc = get_gateway_country_code()
                    recipient = normalize_phone_number(recipient, default_cc)

                    if recipient != original_recipient:
                        logger.info(f"Phone normalized: {original_recipient} → {recipient} (using {default_cc})")

                if not recipient or not message:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'success': False,
                        'error': 'Missing recipient or message'
                    }).encode())
                    return
                
                # Check if Unicode is needed
                needs_unicode = False
                try:
                    message.encode('ascii')
                except UnicodeEncodeError:
                    needs_unicode = True

                # Smart split for long messages (70 chars for UCS2, 160 for GSM7)
                # SIM7600G-H modem cannot handle UCS-2 multipart - split at API level
                max_length = 70 if needs_unicode else 160
                message_parts = split_sms_intelligently(message, max_length)

                # Generate timestamp and file identifiers
                timestamp = int(time.time() * 1000)
                pid = os.getpid()

                # Queue SMS for async processing (instant response!)
                sms_request = {
                    'recipient': recipient,
                    'message_parts': message_parts,
                    'needs_unicode': needs_unicode,
                    'timestamp': timestamp,
                    'pid': pid
                }
                sms_queue.put(sms_request)

                logger.info(f"SMS request queued: {recipient} - {len(message_parts)} parts - will process asynchronously")

                # Respond immediately without waiting for file creation
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'message_id': timestamp,
                    'encoding': 'UCS2' if needs_unicode else 'GSM7',
                    'parts': len(message_parts),
                    'queued': True,
                    'processing': 'async'
                }).encode())
                
            except Exception as e:
                logger.error(f"Error processing SMS: {e}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'error': str(e)
                }).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def handle_phone_call(self):
        """Process phone call TTS command from VPS"""
        # Config is loaded at startup, just verify it's available
        if not voice_config_loaded:
            logger.error("Voice config not loaded - cannot handle phone call")
            self.send_response(503)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'error': 'Voice configuration not available'
            }).encode())
            return

        try:
            # Read request data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            # Extract fields
            call_id = data.get('callId')
            session_id = data.get('sessionId')
            text = data.get('text', '')
            language = data.get('language', voice_config.get('language', 'en') if voice_config else 'en')
            voice_settings = data.get('voice_settings', {})
            action = data.get('action', 'speak')
            priority = data.get('priority', 'normal')

            logger.info(f"Phone call command: callId={call_id}, action={action}, priority={priority}")
            logger.info(f"Text: {text[:100]}..." if len(text) > 100 else f"Text: {text}")

            # Track statistics
            if call_id not in response_stats:
                response_stats[call_id] = {
                    'start_time': time.time(),
                    'responses': 0,
                    'total_chars': 0
                }

            response_stats[call_id]['responses'] += 1
            response_stats[call_id]['total_chars'] += len(text)

            # Process based on action
            if action == 'speak':
                # Queue TTS request
                tts_request = {
                    'call_id': call_id,
                    'session_id': session_id,
                    'text': text,
                    'language': language,
                    'voice_settings': voice_settings,
                    'priority': priority,
                    'timestamp': time.time()
                }

                # Priority queue handling
                if priority == 'high':
                    # Clear queue for high priority
                    while not tts_queue.empty():
                        try:
                            tts_queue.get_nowait()
                        except:
                            break

                tts_queue.put(tts_request)
                logger.info(f"Queued TTS for call {call_id}")

            elif action == 'hangup':
                # Signal to hang up call
                hangup_queue.put({
                    'call_id': call_id,
                    'timestamp': time.time()
                })
                logger.info(f"Queued hangup for call {call_id}")

            # Send success response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'message': f'Command {action} queued',
                'call_id': call_id,
                'queue_size': tts_queue.qsize()
            }).encode())

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'error': 'Invalid JSON format'
            }).encode())

        except Exception as e:
            logger.error(f"Error processing phone call: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'error': str(e)
            }).encode())

    def handle_phone_status(self):
        """Return phone call status information"""
        try:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            status = {
                'tts_queue_size': tts_queue.qsize(),
                'active_calls': len(response_stats),
                'tts_provider': voice_config.get('tts_model') if voice_config else 'not_configured',
                'language': voice_config.get('language') if voice_config else 'not_configured',
                'voice_configured': voice_config_loaded,
                'stats': response_stats
            }

            self.wfile.write(json.dumps(status, indent=2).encode())

        except Exception as e:
            logger.error(f"Error getting phone status: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'error': str(e)
            }).encode())

    def do_GET(self):
        if self.path == '/phone_call/status':
            # Return phone call status
            self.handle_phone_status()
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        logger.info(f"{self.client_address[0]} - {format % args}")

if __name__ == '__main__':
    print("="*60)
    print("Starting Unified Communication API on port 8088")
    print("="*60)
    print("SMS Endpoints:")
    print("  POST /send - Send SMS (JSON: {to: '+number', message: 'text'})")
    print("  POST /pi_send_message - Send SMS (same as /send)")
    print("")
    print("Phone Call Endpoints:")
    print("  POST /phone_call - Receive TTS commands from VPS")
    print("  GET /phone_call/status - Get phone call processing status")
    print("")

    # Start SMS processor for async message handling
    logger.info("Starting SMS processor for async message handling...")
    sms_processor = SMSProcessor()
    sms_processor.start()
    logger.info("✅ SMS processor started - messages will be processed asynchronously")
    print("✅ SMS async processor started")

    # Load voice config at startup, not lazily
    logger.info("Loading voice configuration at startup...")
    if load_voice_config():
        # Start TTS processor at startup
        tts_processor = TTSProcessor(tts_provider)
        tts_processor.start()
        logger.info("✅ TTS processor started at startup")
        print("✅ Voice configuration loaded successfully")
    else:
        print("⚠️  Voice configuration failed to load")

    print("="*60)

    server = HTTPServer(('0.0.0.0', 8088), SMSHandler)
    server.serve_forever()