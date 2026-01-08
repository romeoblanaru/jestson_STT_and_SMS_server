#!/usr/bin/env python3
"""
Call Profiler - Performance timing and event tracking for voice calls
"""
import time
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict


class CallProfiler:
    """Profile timing and events during a voice call"""

    def __init__(self, call_id):
        self.call_id = call_id
        self.start_time = time.time()
        self.start_timestamp = datetime.now().isoformat()

        # Event tracking
        self.events = []
        self.timers = {}  # Active timers

        # Summary data
        self.vad_chunks = 0

        # Output directory
        self.output_dir = Path('/home/rom/timing_analysis')
        self.output_dir.mkdir(exist_ok=True)

    def start_timer(self, name):
        """Start a timer for an operation"""
        self.timers[name] = time.time()

    def stop_timer(self, name, event_name, extra_details=None):
        """Stop a timer and log the event with duration"""
        if name not in self.timers:
            return

        start = self.timers[name]
        duration = time.time() - start
        del self.timers[name]

        details = {'duration': duration}
        if extra_details:
            details.update(extra_details)

        self.log_event(event_name, details)

    def log_event(self, event_name, details=None):
        """Log an event with timestamp"""
        timestamp = time.time()
        elapsed = timestamp - self.start_time

        event = {
            'name': event_name,
            'time': elapsed,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }

        self.events.append(event)

    def set_vad_chunks(self, count):
        """Set VAD chunk count for summary"""
        self.vad_chunks = count

    def save(self):
        """Save profiling data to JSON file"""
        # Calculate total duration
        duration = time.time() - self.start_time

        # Build output data
        data = {
            'call_id': self.call_id,
            'start_time': self.start_timestamp,
            'duration': duration,
            'summary': {
                'vad_chunks': self.vad_chunks
            },
            'events': self.events
        }

        # Save to file
        output_file = self.output_dir / f"{self.call_id}.json"
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        # Also save as "latest.json" for easy access
        latest_file = self.output_dir / "latest.json"
        with open(latest_file, 'w') as f:
            json.dump(data, f, indent=2)

        return output_file
