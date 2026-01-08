#!/usr/bin/env python3
"""
SMS Gateway API for sending SMS via smstools3
Allows external apps to send SMS through this gateway
"""

from flask import Flask, request, jsonify
import os
import time
import hashlib
import logging
from datetime import datetime

app = Flask(__name__)

# Configuration
SMS_OUTGOING = "/var/spool/sms/outgoing"
API_TOKEN = "your-secret-token-here"  # Change this!
LOG_FILE = "/var/log/sms_api.log"

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def verify_token(token):
    """Verify API token"""
    return token == API_TOKEN

def create_sms_file(recipient, message):
    """Create SMS file for smstools3"""
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_str = hashlib.md5(f"{timestamp}{recipient}".encode()).hexdigest()[:8]
    filename = f"sms_{timestamp}_{random_str}"
    filepath = os.path.join(SMS_OUTGOING, filename)
    
    # Create SMS file content
    sms_content = f"""To: {recipient}

{message}"""
    
    # Write file
    try:
        with open(filepath, 'w') as f:
            f.write(sms_content)
        os.chmod(filepath, 0o666)
        return True, filename
    except Exception as e:
        return False, str(e)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "service": "SMS Gateway API",
        "time": datetime.now().isoformat()
    })

@app.route('/send_sms', methods=['POST'])
def send_sms():
    """Send SMS endpoint"""
    # Check token
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not verify_token(token):
        logging.warning(f"Unauthorized access attempt from {request.remote_addr}")
        return jsonify({"error": "Unauthorized"}), 401
    
    # Get request data
    data = request.json
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    recipient = data.get('to')
    message = data.get('message')
    
    # Validate inputs
    if not recipient or not message:
        return jsonify({"error": "Missing 'to' or 'message' field"}), 400
    
    # Clean recipient number (ensure it starts with country code)
    if not recipient.startswith('+'):
        recipient = '+' + recipient
    
    # Create SMS file
    success, result = create_sms_file(recipient, message)
    
    if success:
        logging.info(f"SMS queued: To={recipient}, From={request.remote_addr}")
        return jsonify({
            "status": "queued",
            "to": recipient,
            "message_length": len(message),
            "queue_file": result
        }), 200
    else:
        logging.error(f"Failed to queue SMS: {result}")
        return jsonify({"error": f"Failed to queue SMS: {result}"}), 500

@app.route('/send_bulk', methods=['POST'])
def send_bulk_sms():
    """Send SMS to multiple recipients"""
    # Check token
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not verify_token(token):
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    recipients = data.get('recipients', [])
    message = data.get('message')
    
    if not recipients or not message:
        return jsonify({"error": "Missing 'recipients' or 'message' field"}), 400
    
    results = []
    for recipient in recipients:
        if not recipient.startswith('+'):
            recipient = '+' + recipient
        
        success, result = create_sms_file(recipient, message)
        results.append({
            "to": recipient,
            "status": "queued" if success else "failed",
            "detail": result
        })
    
    return jsonify({
        "total": len(recipients),
        "results": results
    }), 200

if __name__ == '__main__':
    # Create log file if it doesn't exist
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    print("SMS Gateway API starting...")
    print(f"Outgoing SMS directory: {SMS_OUTGOING}")
    print("Remember to change the API_TOKEN!")
    
    # Run on all interfaces so VPS can access
    app.run(host='0.0.0.0', port=8088, debug=False)