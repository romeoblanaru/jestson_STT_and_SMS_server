#!/bin/bash

# TTS Health Monitor Script
# Checks TTS queue status and alerts if stuck

# Get TTS status from API
STATUS=$(curl -s http://localhost:8088/phone_call/status 2>/dev/null)

if [ -z "$STATUS" ]; then
    /home/rom/pi_send_message.sh "⚠️ TTS API not responding on port 8088" "warning"
    exit 1
fi

# Parse JSON response
QUEUE_SIZE=$(echo "$STATUS" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tts_queue_size', 0))" 2>/dev/null)
ACTIVE_CALLS=$(echo "$STATUS" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('active_calls', 0))" 2>/dev/null)
VOICE_CONFIGURED=$(echo "$STATUS" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('voice_configured', False))" 2>/dev/null)
TTS_PROVIDER=$(echo "$STATUS" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tts_provider', 'unknown'))" 2>/dev/null)
LANGUAGE=$(echo "$STATUS" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('language', 'unknown'))" 2>/dev/null)

# Get call stats if available
CALL_STATS=$(echo "$STATUS" | python3 -c "
import sys, json
d = json.load(sys.stdin)
stats = d.get('stats', {})
if stats:
    for call_id, info in stats.items():
        responses = info.get('responses', 0)
        total_chars = info.get('total_chars', 0)
        last_tts_time = info.get('last_tts_time', 0)
        print(f'Call {call_id}: {responses} responses, {total_chars} chars, last TTS: {last_tts_time:.1f}s')
else:
    print('No active call stats')
" 2>/dev/null)

# Build status message
STATUS_MSG="**📞 TTS HEALTH STATUS:**"$'\n'
STATUS_MSG+="━━━━━━━━━━━━━━━━━━━━━━━━━━"$'\n'
STATUS_MSG+="**Queue Size:** ${QUEUE_SIZE} messages"$'\n'
STATUS_MSG+="**Active Calls:** ${ACTIVE_CALLS}"$'\n'
STATUS_MSG+="**Voice Configured:** ${VOICE_CONFIGURED}"$'\n'
STATUS_MSG+="**TTS Provider:** ${TTS_PROVIDER}"$'\n'
STATUS_MSG+="**Language:** ${LANGUAGE}"$'\n'

# Add call stats if available
if [ "$ACTIVE_CALLS" -gt 0 ]; then
    STATUS_MSG+=""$'\n'
    STATUS_MSG+="<blue>**Call Stats:**</blue>"$'\n'
    while IFS= read -r line; do
        STATUS_MSG+="  └ ${line}"$'\n'
    done <<< "$CALL_STATS"
fi

# Check for issues
ISSUES_FOUND=false
SEVERITY="info"

# Add blank line before issues section
if [ "$QUEUE_SIZE" -gt 10 ] || [ "$VOICE_CONFIGURED" = "False" ] || [ "$VOICE_CONFIGURED" = "false" ]; then
    STATUS_MSG+=""$'\n'
    STATUS_MSG+="<red>**⚠️ ISSUES DETECTED:**</red>"$'\n'
fi

# Check 1: Queue stuck (too many items)
if [ "$QUEUE_SIZE" -gt 10 ]; then
    STATUS_MSG+="├ ⚠️ Queue has ${QUEUE_SIZE} items (>10)"$'\n'
    STATUS_MSG+="│  └ TTS may be stuck or VPS sending too fast"$'\n'
    ISSUES_FOUND=true
    SEVERITY="warning"
fi

# Check 2: Voice not configured
if [ "$VOICE_CONFIGURED" = "False" ] || [ "$VOICE_CONFIGURED" = "false" ]; then
    STATUS_MSG+="├ ❌ Voice system not configured!"$'\n'
    STATUS_MSG+="│  └ Check voice_config.json and API keys"$'\n'
    ISSUES_FOUND=true
    SEVERITY="error"
fi

# Check 3: Long TTS processing time
LONG_TTS=$(echo "$STATUS" | python3 -c "
import sys, json
d = json.load(sys.stdin)
stats = d.get('stats', {})
for call_id, info in stats.items():
    last_tts_time = info.get('last_tts_time', 0)
    if last_tts_time > 30:
        print(f'{last_tts_time:.1f}')
        break
" 2>/dev/null)

if [ ! -z "$LONG_TTS" ]; then
    STATUS_MSG+="├ ⚠️ Last TTS took ${LONG_TTS}s (>30s)"$'\n'
    STATUS_MSG+="│  └ Possible network issue or TTS API timeout"$'\n'
    ISSUES_FOUND=true
    SEVERITY="warning"
fi

# Final status
STATUS_MSG+=""$'\n'
STATUS_MSG+="━━━━━━━━━━━━━━━━━━━━━━━━━━"$'\n'

if [ "$ISSUES_FOUND" = true ]; then
    STATUS_MSG+="<red>**🔴 Status: ISSUES DETECTED**</red>"
else
    STATUS_MSG+="<blue>**✅ Status: HEALTHY**</blue>"
fi

# Send to VPS
/home/rom/pi_send_message.sh "$STATUS_MSG" "$SEVERITY"

# Also print to stdout
echo "$STATUS_MSG"

# Exit with error code if issues found
if [ "$ISSUES_FOUND" = true ]; then
    exit 1
else
    exit 0
fi