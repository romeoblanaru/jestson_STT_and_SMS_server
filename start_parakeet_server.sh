#!/bin/bash
#
# Start Parakeet-TDT-0.6B-v3 ASR Server
# Uses pre-built Docker image with NeMo ASR for fast startup (~30s)
#
# Usage: ./start_parakeet_server.sh
#

echo "============================================================"
echo "Starting Parakeet-TDT-0.6B-v3 ASR Server"
echo "============================================================"
echo ""
echo "Image: parakeet-server (pre-built with NeMo ASR)"
echo "Port: 9001"
echo "Model: /home/rom/parakeet-tdt-0.6b-v3/parakeet-tdt-0.6b-v3.nemo"
echo ""
echo "Press Ctrl+C to stop the server"
echo "============================================================"
echo ""

docker run --rm \
  --runtime nvidia \
  --network host \
  --env-file /home/rom/.env \
  -v /home/rom/parakeet-tdt-0.6b-v3:/models \
  -v /home/rom:/workspace \
  parakeet-server
