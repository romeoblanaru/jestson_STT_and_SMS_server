#!/bin/bash

# SIM7600 System Monitor Script
# Shows comprehensive status of all components

echo "============================================================"
echo "                 SIM7600 SYSTEM STATUS"
echo "============================================================"
echo ""

# Check logging mode
LOG_MODE=$(grep LOG_MODE /home/rom/.env | cut -d'=' -f2)
echo "📋 LOGGING MODE: $LOG_MODE"
echo ""

# Check services
echo "🔧 SERVICES STATUS:"
echo "-------------------"
echo -n "  SMS Tools:          "
systemctl is-active smstools
echo -n "  Unified API:        "
systemctl is-active sms-api
echo -n "  SIM7600 Detector:   "
systemctl is-active sim7600-detector
echo -n "  SIM7600 Voice Bot:  "
systemctl is-active sim7600-voice-bot
echo ""

# Check USB devices
echo "📱 USB DEVICES:"
echo "---------------"
ls /dev/ttyUSB* 2>/dev/null || echo "  No USB devices detected"
echo ""

# Check if port mapping exists
if [ -f /home/rom/sim7600_ports.json ]; then
    echo "🔌 PORT MAPPING:"
    echo "----------------"
    cat /home/rom/sim7600_ports.json | jq -r 'to_entries[] | "  \(.key): \(.value // "Not found")"'
    echo ""
fi

# Check recent logs
echo "📝 RECENT DETECTOR LOGS:"
echo "------------------------"
tail -5 /var/log/sim7600_detector.log 2>/dev/null | sed 's/^/  /'
echo ""

# Check API status
echo "🌐 API ENDPOINTS:"
echo "-----------------"
echo -n "  SMS API:     "
curl -s http://localhost:8088/status >/dev/null 2>&1 && echo "✅ Running" || echo "❌ Not responding"
echo -n "  Voice API:   "
curl -s http://localhost:8088/phone_call/status >/dev/null 2>&1 && echo "✅ Running" || echo "❌ Not responding"
echo ""

# Show voice config status
if [ -f /home/rom/voice_config.json ]; then
    echo "🎤 VOICE CONFIG:"
    echo "----------------"
    echo "  TTS Model: $(jq -r .tts_model /home/rom/voice_config.json)"
    echo "  Language:  $(jq -r .language /home/rom/voice_config.json)"
    echo "  Has API Key: $(jq -r 'if .tts_secret_key then "✅ Yes" else "❌ No" end' /home/rom/voice_config.json)"
fi

echo ""
echo "============================================================"
echo "To monitor live logs:"
echo "  Detector:  tail -f /var/log/sim7600_detector.log"
echo "  Voice Bot: sudo journalctl -f -u sim7600-voice-bot"
echo "============================================================"