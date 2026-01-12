#!/usr/bin/env python3
"""
Simple webhook server to trigger monitoring reports from VPS
Listens on port 8070 for monitoring requests
"""

from flask import Flask, request, jsonify
import subprocess
import os
import threading

app = Flask(__name__)

MONITORING_SCRIPT = "/home/rom/pi_send_message.sh"

def run_monitoring_async(script, args):
    """Run monitoring script asynchronously in background"""
    try:
        subprocess.run(
            [script] + args,
            capture_output=True,
            text=True,
            timeout=180  # Increased from 120s for comprehensive status checks
        )
    except Exception as e:
        print(f"Background task error: {e}")

@app.route('/monitor/<action>/sync', methods=['POST', 'GET'])
def trigger_monitor_sync(action):
    """Run monitoring script synchronously and return full output"""

    valid_actions = [
        'vpn', 'system', 'system-full', 'network',
        'ec25', 'sim7600', 'tts', 'test', 'logs'
    ]

    if action not in valid_actions:
        return jsonify({
            'status': 'error',
            'message': f'Invalid action. Valid actions: {", ".join(valid_actions)}'
        }), 400

    try:
        # Prepare script arguments
        if action == 'logs':
            script = '/home/rom/log_monitor.sh'
            args = ['check']
        elif action == 'sim7600':
            script = '/home/rom/check_sim7600_status.sh'
            args = []
        elif action == 'tts':
            script = '/home/rom/monitor_tts_health.sh'
            args = []
        else:
            script = MONITORING_SCRIPT
            args = [action]

        # Run synchronously with timeout
        result = subprocess.run(
            [script] + args,
            capture_output=True,
            text=True,
            timeout=180
        )

        # Return full output
        return jsonify({
            'status': 'success',
            'action': action,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'return_code': result.returncode
        })

    except subprocess.TimeoutExpired:
        return jsonify({
            'status': 'error',
            'message': 'Script execution timed out (180s)'
        }), 504
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/monitor/<action>', methods=['POST', 'GET'])
def trigger_monitor(action):
    """Trigger monitoring script with specified action"""

    valid_actions = [
        'vpn', 'system', 'system-full', 'network',
        'ec25', 'sim7600', 'tts', 'test', 'custom', 'logs'
    ]

    if action not in valid_actions:
        return jsonify({
            'status': 'error',
            'message': f'Invalid action. Valid actions: {", ".join(valid_actions)}'
        }), 400

    try:
        # Prepare script arguments
        if action == 'custom':
            message = request.json.get('message', 'Custom monitoring request') if request.is_json else 'Custom monitoring request'
            severity = request.json.get('severity', 'info') if request.is_json else 'info'
            args = [message, severity]
            script = MONITORING_SCRIPT
        elif action == 'logs':
            args = ['check']
            script = '/home/rom/log_monitor.sh'
        elif action == 'sim7600':
            args = []
            script = '/home/rom/check_sim7600_status.sh'
        elif action == 'tts':
            args = []
            script = '/home/rom/monitor_tts_health.sh'
        else:
            args = [action]
            script = MONITORING_SCRIPT

        # Start monitoring script in background thread
        thread = threading.Thread(target=run_monitoring_async, args=(script, args), daemon=True)
        thread.start()

        # Return immediate success response
        return jsonify({
            'status': 'success',
            'action': action,
            'message': f'Monitoring task started in background'
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/monitor/service/<service_name>', methods=['POST', 'GET'])
def check_service(service_name):
    """Check specific service status"""
    try:
        # Start monitoring script in background thread
        thread = threading.Thread(
            target=run_monitoring_async,
            args=(MONITORING_SCRIPT, ['service', service_name]),
            daemon=True
        )
        thread.start()

        return jsonify({
            'status': 'success',
            'service': service_name,
            'message': 'Service check started in background'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/monitor/help', methods=['GET'])
def show_help():
    """Show available monitoring endpoints"""
    return jsonify({
        'endpoints': {
            '/monitor/vpn': 'Check VPN connectivity (async)',
            '/monitor/system': 'Quick system health check (async)',
            '/monitor/system-full': 'Comprehensive system report (async)',
            '/monitor/network': 'Check network connectivity (async)',
            '/monitor/ec25': 'Check EC25 modem status (async)',
            '/monitor/sim7600': 'Check SIM7600 modem status (async)',
            '/monitor/sim7600/sync': 'Check SIM7600 modem status (sync - returns full output)',
            '/monitor/tts': 'Check TTS queue and voice call status (async)',
            '/monitor/tts/sync': 'Check TTS status (sync - returns full output)',
            '/monitor/test': 'Send test message',
            '/monitor/custom': 'Send custom message (POST with JSON: {"message": "...", "severity": "info"})',
            '/monitor/service/<name>': 'Check specific service status',
            '/monitor/services': 'List all available services',
            '/monitor/logs': 'Check for recent errors and service restarts (async)',
            '/monitor/logs/sync': 'Check logs (sync - returns full output)',
            '/monitor/modem_reset': 'Software reset modem via USB unbind/bind (async)'
        },
        'methods': ['GET', 'POST'],
        'note': 'All endpoints support both GET and POST methods. /sync endpoints return full output in HTTP response.'
    })

@app.route('/monitor/services', methods=['GET'])
def list_services():
    """List all available systemd services - triggers monitoring script"""
    try:
        # Start monitoring script in background thread
        thread = threading.Thread(
            target=run_monitoring_async,
            args=('/home/rom/list_all_services.sh', []),
            daemon=True
        )
        thread.start()

        return jsonify({
            'status': 'success',
            'action': 'services',
            'message': 'Services status check started in background'
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/monitor/modem_reset', methods=['POST', 'GET'])
def modem_reset():
    """Reset the modem via USB unbind/bind (software reset)"""
    try:
        # Start modem reset script in background thread
        thread = threading.Thread(
            target=run_monitoring_async,
            args=('/home/rom/modem_usb_reset.sh', []),
            daemon=True
        )
        thread.start()

        return jsonify({
            'status': 'success',
            'action': 'modem_reset',
            'message': 'Modem USB reset started in background. Check logs at /var/log/modem_usb_reset.log'
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    # Run on all interfaces so VPS can access via VPN
    app.run(host='0.0.0.0', port=8070, debug=False)