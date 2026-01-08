#!/usr/bin/env python3
"""
Audio Recorder - Direct PCM to OGG Opus conversion
Records audio streams without introducing latency to real-time processing
Converts PCM directly to Opus OGG (no intermediate WAV files)
"""

import threading
import queue
import time
import logging
import numpy as np
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

def pcm_to_opus_ogg(pcm_data, sample_rate=16000, output_path=None):
    """
    Convert raw PCM bytes directly to Opus OGG format (no WAV intermediate)

    Args:
        pcm_data: bytes - raw PCM audio (16-bit signed little-endian)
        sample_rate: int - sample rate (8000 or 16000 Hz)
        output_path: Path - optional output file path (if None, returns bytes)

    Returns:
        bytes - OGG Opus compressed audio (if output_path is None)
        Path - Path to saved OGG file (if output_path provided)
        None - if conversion failed
    """
    try:
        # Build ffmpeg command for direct PCM → OGG conversion
        cmd = [
            'ffmpeg',
            '-f', 's16le',              # Input format: signed 16-bit little-endian
            '-ar', str(sample_rate),    # Sample rate
            '-ac', '1',                 # Mono
            '-i', 'pipe:0',             # Read from stdin
            '-c:a', 'libopus',          # Codec: Opus
            '-b:a', '24k',              # Bitrate: 24 kbps
            '-application', 'voip',     # Optimize for voice
            '-vbr', 'on',               # Variable bitrate
            '-compression_level', '0',  # Fast encoding (90x real-time)
            '-f', 'ogg',                # Output format: OGG container
        ]

        # Output to file or stdout
        if output_path:
            cmd.append(str(output_path))
            cmd.append('-y')  # Overwrite if exists
        else:
            cmd.append('pipe:1')  # Write to stdout

        # Run ffmpeg with PCM data as stdin
        result = subprocess.run(
            cmd,
            input=pcm_data,
            capture_output=True,
            timeout=10
        )

        if result.returncode == 0:
            pcm_size = len(pcm_data)

            if output_path:
                # Return path to saved file
                if Path(output_path).exists():
                    ogg_size = Path(output_path).stat().st_size
                    compression_ratio = pcm_size / ogg_size if ogg_size > 0 else 0
                    logger.debug(f"PCM→OGG: {pcm_size/1024:.1f}KB → {ogg_size/1024:.1f}KB [{compression_ratio:.1f}x]")
                    return output_path
                else:
                    logger.error(f"OGG file not created: {output_path}")
                    return None
            else:
                # Return OGG bytes
                ogg_data = result.stdout
                compression_ratio = pcm_size / len(ogg_data) if len(ogg_data) > 0 else 0
                logger.debug(f"PCM→OGG: {pcm_size/1024:.1f}KB → {len(ogg_data)/1024:.1f}KB [{compression_ratio:.1f}x]")
                return ogg_data
        else:
            logger.error(f"FFmpeg PCM→OGG failed: {result.stderr.decode()}")
            return None

    except subprocess.TimeoutExpired:
        logger.error("PCM→OGG conversion timeout")
        return None
    except Exception as e:
        logger.error(f"Error in PCM→OGG conversion: {e}")
        return None

class AsyncAudioRecorder:
    """Asynchronously records audio streams to OGG Opus files (direct PCM conversion)"""

    def __init__(self, call_id, stream_name, sample_rate=8000, channels=1, gain=1.0):
        self.call_id = call_id
        self.stream_name = stream_name
        self.sample_rate = sample_rate
        self.channels = channels
        self.sample_width = 2  # 16-bit = 2 bytes
        self.gain = gain  # Audio amplification factor (1.0 = no change, 1.5 = 50% louder)

        # Output directory (persistent storage, not RAM disk)
        self.output_dir = Path("/home/rom/audio_wav")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Output file (OGG, not WAV)
        timestamp = int(time.time())
        self.output_file = self.output_dir / f"{call_id}_{stream_name}_{timestamp}.ogg"

        # Audio buffer queue (async)
        self.audio_queue = queue.Queue(maxsize=1000)  # Max 1000 chunks buffered

        # Recording state
        self.is_recording = False
        self.writer_thread = None

        # PCM data accumulator (accumulate all PCM chunks, convert to OGG at end)
        self.pcm_chunks = []

        # Stats
        self.total_frames = 0
        self.total_bytes = 0

    def start(self):
        """Start recording"""
        if self.is_recording:
            logger.warning(f"Recorder {self.stream_name} already started")
            return

        self.is_recording = True

        # Start writer thread
        self.writer_thread = threading.Thread(
            target=self._writer_loop,
            daemon=True,
            name=f"AudioRecorder-{self.stream_name}"
        )
        self.writer_thread.start()

        logger.info(f"✅ Audio recorder started: {self.stream_name} → {self.output_file}")

    def write_chunk(self, audio_data):
        """Write audio chunk (called from real-time thread - MUST be fast!)"""
        if not self.is_recording:
            return

        # Validate audio data
        if audio_data is None or not isinstance(audio_data, bytes) or len(audio_data) == 0:
            return

        try:
            # Non-blocking put - drop chunk if queue is full (prevents latency)
            self.audio_queue.put_nowait(audio_data)
        except queue.Full:
            logger.warning(f"Audio queue full for {self.stream_name} - dropping chunk (no latency impact)")

    def _writer_loop(self):
        """Background thread that accumulates PCM chunks and converts to OGG at end"""
        try:
            logger.info(f"PCM accumulator started: {self.stream_name}")

            while self.is_recording:
                try:
                    # Wait for audio chunk (1 second timeout)
                    audio_data = self.audio_queue.get(timeout=1.0)

                    # Apply gain if needed (amplify audio)
                    if self.gain != 1.0:
                        # Convert bytes to int16 array
                        audio_array = np.frombuffer(audio_data, dtype=np.int16)
                        # Apply gain and clip to prevent overflow
                        audio_amplified = np.clip(audio_array * self.gain, -32768, 32767).astype(np.int16)
                        # Convert back to bytes
                        audio_data = audio_amplified.tobytes()

                    # Accumulate PCM chunk in memory (no disk I/O during call)
                    self.pcm_chunks.append(audio_data)

                    # Update stats
                    self.total_bytes += len(audio_data)
                    self.total_frames += len(audio_data) // self.sample_width

                except queue.Empty:
                    # No data for 1 second - check if we should continue
                    continue

            # Flush remaining data
            logger.info(f"Flushing remaining PCM chunks for {self.stream_name}...")
            while not self.audio_queue.empty():
                try:
                    audio_data = self.audio_queue.get_nowait()

                    # Apply gain if needed (same as above)
                    if self.gain != 1.0:
                        audio_array = np.frombuffer(audio_data, dtype=np.int16)
                        audio_amplified = np.clip(audio_array * self.gain, -32768, 32767).astype(np.int16)
                        audio_data = audio_amplified.tobytes()

                    self.pcm_chunks.append(audio_data)
                    self.total_bytes += len(audio_data)
                    self.total_frames += len(audio_data) // self.sample_width
                except queue.Empty:
                    break

            # Concatenate all PCM chunks
            full_pcm_data = b''.join(self.pcm_chunks)

            duration_sec = self.total_frames / self.sample_rate
            logger.info(f"✅ PCM accumulated: {self.stream_name}")
            logger.info(f"   Duration: {duration_sec:.2f}s, Size: {self.total_bytes / 1024:.1f}KB")

            # Convert PCM → OGG Opus directly (no WAV intermediate)
            logger.info(f"Converting PCM → OGG Opus: {self.stream_name}...")
            ogg_path = pcm_to_opus_ogg(full_pcm_data, self.sample_rate, self.output_file)

            if ogg_path:
                ogg_size = Path(ogg_path).stat().st_size
                logger.info(f"✅ OGG saved: {self.output_file.name} ({ogg_size / 1024:.1f}KB)")
            else:
                logger.error(f"❌ OGG conversion failed for {self.stream_name}")

        except Exception as e:
            logger.error(f"Error in audio writer thread for {self.stream_name}: {e}")

    def stop(self):
        """Stop recording"""
        if not self.is_recording:
            return

        logger.info(f"Stopping audio recorder: {self.stream_name}")
        self.is_recording = False

        # Wait for writer thread to finish
        if self.writer_thread and self.writer_thread.is_alive():
            self.writer_thread.join(timeout=5.0)

        logger.info(f"Audio recorder stopped: {self.stream_name}")


class CallAudioRecorder:
    """Manages all audio recorders for a call"""

    def __init__(self, call_id, sample_rate=8000, vps_queue=None):
        self.call_id = call_id
        self.sample_rate = sample_rate
        self.vad_chunk_counter = 0  # Track VAD chunk numbers
        self.vps_queue = vps_queue  # Queue for async VPS transcription

        # Output directory for VAD chunks (persistent storage)
        self.output_dir = Path("/home/rom/audio_wav")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create recorders (no gain - natural audio levels)
        # NOTE: incoming_vad_chunks is NOT used - we save each chunk as separate file
        self.recorders = {
            'incoming_raw': AsyncAudioRecorder(call_id, 'incoming_raw', sample_rate),
            'outgoing_tts': AsyncAudioRecorder(call_id, 'outgoing_tts', sample_rate)
        }

    def start_all(self):
        """Start all recorders"""
        for name, recorder in self.recorders.items():
            recorder.start()
        logger.info(f"✅ All audio recorders started for call {self.call_id}")

    def stop_all(self):
        """Stop all recorders"""
        for name, recorder in self.recorders.items():
            recorder.stop()
        logger.info(f"✅ All audio recorders stopped for call {self.call_id}")

    def record_incoming_raw(self, audio_data):
        """Record incoming raw audio (before VAD)"""
        self.recorders['incoming_raw'].write_chunk(audio_data)

    def record_incoming_vad_chunk(self, audio_data):
        """
        Record VAD-detected chunk
        - If vps_queue provided: Send to VPS async (non-blocking)
        - Always save OGG locally for backup/debugging
        """
        if audio_data is None or not isinstance(audio_data, bytes) or len(audio_data) == 0:
            return

        try:
            # Increment chunk counter
            self.vad_chunk_counter += 1
            chunk_num = self.vad_chunk_counter
            timestamp = int(time.time())

            # Calculate duration
            duration_sec = len(audio_data) / (self.sample_rate * 2)  # 2 bytes per sample

            # If VPS queue available, send PCM chunk for async processing (INSTANT, non-blocking)
            if self.vps_queue:
                try:
                    chunk_info = {
                        'pcm_data': audio_data,
                        'chunk_num': chunk_num,
                        'timestamp': timestamp,
                        'sample_rate': self.sample_rate,
                        'duration': duration_sec
                    }
                    self.vps_queue.put_nowait(chunk_info)
                    logger.debug(f"📤 VAD chunk #{chunk_num} queued for VPS ({duration_sec:.2f}s)")
                except queue.Full:
                    logger.warning(f"⚠️ VPS queue full - chunk #{chunk_num} dropped")

            # Also save locally as OGG for backup/debugging (async in background thread)
            # This happens in parallel with VPS processing
            ogg_file = self.output_dir / f"{self.call_id}_vad_chunk_{chunk_num}_{timestamp}.ogg"

            # Spawn background thread to save OGG (doesn't block main thread)
            def save_ogg_async():
                try:
                    ogg_path = pcm_to_opus_ogg(audio_data, self.sample_rate, ogg_file)
                    if ogg_path:
                        ogg_size = Path(ogg_path).stat().st_size
                        logger.debug(f"💾 VAD chunk #{chunk_num} saved locally: {ogg_path.name} ({ogg_size/1024:.1f}KB)")
                except Exception as e:
                    logger.error(f"Error saving OGG chunk #{chunk_num}: {e}")

            save_thread = threading.Thread(target=save_ogg_async, daemon=True, name=f"SaveOGG-{chunk_num}")
            save_thread.start()

        except Exception as e:
            logger.error(f"Error processing VAD chunk: {e}")

    def record_outgoing_tts(self, audio_data):
        """Record outgoing TTS audio (from Azure)"""
        self.recorders['outgoing_tts'].write_chunk(audio_data)
