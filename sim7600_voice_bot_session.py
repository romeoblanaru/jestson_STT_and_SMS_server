#!/usr/bin/env python3
"""
SIM7600 Voice Bot - Session Mode
Called by SMSTools eventhandler to handle a single incoming call
Restarts SMSTools when done
"""

import sys
import time
import os
import logging
import subprocess
from logging.handlers import RotatingFileHandler

# Setup logging
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_file_path = '/var/log/voice_bot_ram/sim7600_voice_bot.log'

file_handler = RotatingFileHandler(
    log_file_path,
    maxBytes=10*1024*1024,
    backupCount=5
)
file_handler.setFormatter(log_formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

# Import the main voice bot class
sys.path.insert(0, '/home/rom')
from sim7600_voice_bot import SIM7600VoiceBot

def main():
    """Handle single call in session mode"""
    caller_number = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    logger.info("="*60)
    logger.info("SIM7600 Voice Bot - SESSION MODE")
    logger.info(f"Handling call from: {caller_number}")
    logger.info("="*60)

    try:
        # Create voice bot instance
        bot = SIM7600VoiceBot()

        # Pre-load VAD (fast from cache)
        logger.info("Loading VAD model...")
        bot.load_vad_model()

        # Open serial port (SMSTools already released it)
        bot.stop_smstools()  # Just to be safe
        if not bot.init_modem():
            logger.error("Failed to initialize modem")
            restart_smstools()
            return 1

        # Answer the call (it's ringing right now)
        logger.info("Answering incoming call...")
        bot.send_at_command("ATA")
        time.sleep(0.5)

        # Handle the call
        bot.handle_incoming_call(caller_number)

        # Wait for call to end (monitor for NO CARRIER)
        logger.info("Call active - waiting for end...")
        while bot.in_call:
            try:
                if bot.ser and bot.ser.in_waiting:
                    line = bot.ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        logger.debug(f"Modem: {line}")
                        if "NO CARRIER" in line or "BUSY" in line:
                            logger.info("Call ended")
                            bot.cleanup_call()
                            bot.notify_vps('call_ended', {})
                            break
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error monitoring call: {e}")
                break

        logger.info("Call handling complete")

    except Exception as e:
        logger.error(f"Error in session mode: {e}")
        return 1
    finally:
        # CRITICAL: Always restart SMSTools
        logger.info("Restarting SMSTools...")
        restart_smstools()

    return 0

def restart_smstools():
    """Restart SMSTools to resume SMS functionality"""
    try:
        result = subprocess.run(
            ['sudo', 'systemctl', 'start', 'smstools'],
            timeout=5
        )
        if result.returncode == 0:
            logger.info("✅ SMSTools restarted - SMS functionality restored")
        else:
            logger.error("❌ Failed to restart SMSTools")
    except Exception as e:
        logger.error(f"Error restarting SMSTools: {e}")

if __name__ == "__main__":
    sys.exit(main())
