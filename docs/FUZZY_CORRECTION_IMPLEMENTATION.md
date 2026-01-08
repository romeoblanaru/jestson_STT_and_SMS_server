# Fuzzy Correction Post-Processing Implementation

**Date:** November 22, 2025
**Purpose:** Improve professional transcription quality for domain-specific jargon and names
**Latency Target:** < 2ms (monitoring required)

## Executive Summary

Implemented **fast fuzzy matching post-processing** to correct transcription errors using your hotword lists. This provides professional-quality transcriptions for domain-specific terms (beauty salon jargon, proper names, service names) with minimal latency impact.

### Why This Solution?

- **ASR-level phrase boosting doesn't work** - TDT greedy decoder lacks support (see BOOSTING_TREE_INVESTIGATION.md)
- **N-gram LM fusion adds 5-15ms** - Violates your "zero latency" requirement
- **Fast post-processing:** 1-2ms typical, provides good correction quality
- **Fully monitorable:** Detailed logs show what's being corrected and timing

## What Was Implemented

### 1. RapidFuzz Library
- **Fast fuzzy string matching** - Optimized C++ backend
- **~1ms processing time** for 42 phrases
- **Similarity threshold:** 85% (configurable)

### 2. Post-Processing Function
Location: `parakeet_wrapper.py:37-101`

```python
def fuzzy_correct_transcription(text, hotwords, threshold=85):
    """
    Apply fuzzy matching to correct transcription using hotword list

    - Finds similar phrases in transcription
    - Matches against hotword list
    - Only corrects if similarity > 85%
    - Preserves original casing from hotwords
    """
```

### 3. Monitoring System
Comprehensive logging tracks:
- Input/output transcriptions
- Corrections made (original → corrected)
- Similarity scores for each correction
- Processing time in milliseconds

##Usage

### Enabling/Disabling

Edit `/home/rom/.env`:
```bash
# Enable fuzzy correction (default)
ENABLE_FUZZY_CORRECTION=true

# Disable if it causes problems
ENABLE_FUZZY_CORRECTION=false
```

### Rebuilding Docker Image

After modifying code:
```bash
docker build -t parakeet-server -f /home/rom/Dockerfile.parakeet /home/rom
docker ps -q | xargs -r docker stop
/home/rom/start_parakeet_server.sh
```

### Hotwords Files

Located at:
- `/home/rom/hotwords_ro.txt` (42 Romanian phrases)
- `/home/rom/hotwords_lt.txt` (42 Lithuanian phrases)

To add/modify terms:
1. Edit the appropriate file
2. Rebuild Docker image
3. Restart server

## Monitoring Output

### Example: No Corrections Needed

```
[CORRECTION] 2025-11-22 14:23:45 | Lang: ro | No corrections needed | Time: 0.82ms
[LATENCY] 2025-11-22 14:23:45 | Lang: ro | Size: 12.3KB | ASR: 0.245s | Correction: 0.001s | Total: 0.256s | Text: bună ziua aș dori o programare...
```

### Example: Corrections Applied

```
[CORRECTION] 2025-11-22 14:25:12 | Lang: ro | Corrections: 1 | Time: 1.23ms
[CORRECTION] Input:  'a jorí o programare'
[CORRECTION] Output: 'aș dori o programare'
[CORRECTION]   #1: 'a jorí' -> 'aș dori' (score: 88.5%)
[LATENCY] 2025-11-22 14:25:12 | Lang: ro | Size: 15.1KB | ASR: 0.312s | Correction: 0.001s | Total: 0.325s | Text: aș dori o programare...
```

### Log Analysis

**Check if correction is working:**
```bash
# See recent corrections
docker logs $(docker ps -q --filter ancestor=parakeet-server) 2>&1 | grep CORRECTION | tail -20

# Monitor latency impact
docker logs $(docker ps -q --filter ancestor=parakeet-server) 2>&1 | grep LATENCY | tail -20
```

**Watch for issues:**
- If `Correction:` time exceeds 3ms consistently → investigate
- If corrections are wrong → review similarity threshold or hotwords
- If no corrections when expected → check hotwords file loaded correctly

## JSON Response Format

Transcription response now includes correction details:

```json
{
  "success": true,
  "transcription": "aș dori o programare",
  "language": "ro",
  "latency": {
    "transcription_ms": 245.3,
    "correction_ms": 1.2,
    "total_ms": 256.8
  },
  "corrections": {
    "applied": 1,
    "details": [
      {
        "original": "a jorí",
        "corrected": "aș dori",
        "score": 88.5,
        "position": 0
      }
    ]
  }
}
```

If no corrections: `"corrections": null`

## Performance Targets

| Metric | Target | Acceptable | Action Required |
|--------|--------|------------|-----------------|
| Correction time | < 1ms | 1-2ms | > 2ms: Investigate |
| Total added latency | < 2ms | 2-5ms | > 5ms: Consider disabling |
| False corrections | 0% | < 1% | > 1%: Adjust threshold |

## Verification Steps

### 1. Check Server Startup

```bash
docker logs $(docker ps -q --filter ancestor=parakeet-server) 2>&1 | grep "phrases for post-processing"
```

Expected output:
```
Loaded 42 phrases for post-processing fuzzy correction
```

### 2. Test Transcription

```bash
# Use test audio with known phrase
curl -X POST -F "audio=@test.ogg" -F "language=ro" http://192.168.1.9:9001/transcribe
```

### 3. Monitor Logs

```bash
# Real-time monitoring
docker logs -f $(docker ps -q --filter ancestor=parakeet-server) 2>&1 | grep -E "CORRECTION|LATENCY"
```

## Troubleshooting

### Issue: Correction time > 3ms

**Possible causes:**
- Too many hotwords (> 100)
- Very long transcription text
- Threshold too low (checking too many matches)

**Solutions:**
1. Reduce hotwords to most important terms
2. Increase threshold to 90% for stricter matching
3. Temporarily disable to confirm impact

### Issue: Wrong corrections being made

**Example:** "bună dimineața" → "bună ziua" (incorrect)

**Solutions:**
1. Increase similarity threshold (85% → 90%)
2. Review hotwords for overlapping similar phrases
3. Check logs to see actual similarity scores

**Edit threshold in code:**
```python
# parakeet_wrapper.py line 288
transcription, corrections_made, correction_details = fuzzy_correct_transcription(
    transcription,
    hotwords_phrases,
    threshold=90  # Change from 85 to 90
)
```

### Issue: No corrections happening

**Possible causes:**
- Hotwords file not loaded
- ENABLE_FUZZY_CORRECTION=false
- Transcription doesn't match any hotwords above threshold

**Check:**
```bash
# Verify hotwords loaded
docker logs $(docker ps -q --filter ancestor=parakeet-server) 2>&1 | grep "Loaded.*phrases"

# Check environment variable
docker exec $(docker ps -q --filter ancestor=parakeet-server) env | grep ENABLE_FUZZY_CORRECTION
```

### Issue: Adding latency concerns

**Monitor actual impact:**
```bash
# Extract correction times from logs
docker logs $(docker ps -q --filter ancestor=parakeet-server) 2>&1 | grep "Correction:" | grep -oP "Correction: \K[0-9.]+" | tail -100
```

If consistently > 2ms:
1. Set `ENABLE_FUZZY_CORRECTION=false` in `.env`
2. Rebuild and restart
3. Report findings for alternative solution

## Files Modified

1. **Dockerfile.parakeet** - Added rapidfuzz library
2. **parakeet_wrapper.py** - Added fuzzy correction function and integration
3. **.env** - Added ENABLE_FUZZY_CORRECTION flag
4. **BOOSTING_TREE_INVESTIGATION.md** - Updated with implementation status

## Next Steps

1. **Monitor for 1 week** - Track correction quality and latency
2. **Review logs** - Identify patterns in corrections
3. **Adjust threshold** - If needed based on false corrections
4. **Update hotwords** - Add new terms as business needs evolve

## Future Considerations

If fuzzy correction proves insufficient:

1. **N-gram LM Fusion** - Documented in BOOSTING_TREE_INVESTIGATION.md
   - Pros: Better statistical accuracy
   - Cons: Adds 5-15ms latency
   - When: If accuracy becomes critical requirement

2. **Fine-tune Model** - Train Parakeet on Romanian beauty salon data
   - Pros: Best possible accuracy, no latency penalty
   - Cons: Requires transcribed data and training infrastructure
   - When: Long-term solution for production deployment

3. **Wait for NeMo Fix** - Monitor GitHub Issue #14772
   - When phrase boosting works for TDT greedy, it will be ideal
   - Provides 0-2ms latency with excellent accuracy
