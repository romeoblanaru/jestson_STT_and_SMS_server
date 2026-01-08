#!/bin/bash

cd /home/rom/audio_wav

for file in call_1761507557_vad_chunk_*.wav; do
  output="${file%.wav}.ogg"
  echo "Converting $file to $output..."
  ffmpeg -i "$file" -c:a libopus -b:a 20k -ar 16000 -ac 1 -frame_duration 20 -application voip -vbr off "$output" -y 2>&1 | grep -E "(Input|Output|Duration|Stream|bitrate)"
done

echo ""
echo "=== Size Comparison ==="
for file in call_1761507557_vad_chunk_*.wav; do
  ogg="${file%.wav}.ogg"
  if [ -f "$ogg" ]; then
    wav_size=$(stat -c%s "$file")
    ogg_size=$(stat -c%s "$ogg")
    ratio=$(echo "scale=2; $wav_size / $ogg_size" | bc)
    echo "$file: $(ls -lh "$file" | awk '{print $5}') → $ogg: $(ls -lh "$ogg" | awk '{print $5}') (${ratio}x compression)"
  fi
done
