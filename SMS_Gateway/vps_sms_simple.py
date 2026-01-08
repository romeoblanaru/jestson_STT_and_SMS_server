#!/usr/bin/env python3
"""
Simple SMS sender for VPS - No auth needed (VPN secured)
"""

import requests
import json

# Your Pi's IP on the VPN
PI_IP = "10.100.0.10"

def send_sms(to, message):
    """Send SMS through Pi gateway"""
    url = f"http://{PI_IP}:8088/send_sms"
    data = {
        "to": to,
        "message": message
    }
    
    try:
        response = requests.post(url, json=data)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# Example usage
if __name__ == "__main__":
    # Send a test SMS
    result = send_sms("+447123456789", "Test from VPS - no auth needed!")
    print(json.dumps(result, indent=2))