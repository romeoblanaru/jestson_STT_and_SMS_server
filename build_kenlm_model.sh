#!/bin/bash
# Build KenLM n-gram language model from hotwords for domain-specific biasing

set -e

LANGUAGE=${1:-ro}
HOTWORDS_FILE="/home/rom/hotwords_${LANGUAGE}.txt"
OUTPUT_DIR="/home/rom/lm_models"
ARPA_FILE="${OUTPUT_DIR}/${LANGUAGE}_hotwords.arpa"
BINARY_FILE="${OUTPUT_DIR}/${LANGUAGE}_hotwords.bin"

echo "=========================================="
echo "Building KenLM Model for ${LANGUAGE}"
echo "=========================================="

# Check if hotwords file exists
if [ ! -f "$HOTWORDS_FILE" ]; then
    echo "Error: Hotwords file not found: $HOTWORDS_FILE"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Prepare training corpus by expanding hotwords
# Repeat each phrase multiple times to give it weight
CORPUS_FILE="${OUTPUT_DIR}/${LANGUAGE}_corpus.txt"
echo "Preparing training corpus..."
> "$CORPUS_FILE"  # Clear file

while IFS= read -r phrase; do
    # Skip empty lines
    [ -z "$phrase" ] && continue

    # Add each phrase 10 times to give it strong weight
    for i in {1..10}; do
        echo "$phrase" >> "$CORPUS_FILE"
    done
done < "$HOTWORDS_FILE"

PHRASE_COUNT=$(wc -l < "$HOTWORDS_FILE" | tr -d ' ')
CORPUS_LINES=$(wc -l < "$CORPUS_FILE" | tr -d ' ')
echo "✓ Created corpus with $CORPUS_LINES lines from $PHRASE_COUNT unique phrases"

# Build ARPA format n-gram model using KenLM
echo "Building ARPA n-gram model (3-gram)..."
docker run --rm \
    -v "$OUTPUT_DIR:/data" \
    -v "$CORPUS_FILE:/corpus.txt:ro" \
    kensho/kenlm:latest \
    lmplz -o 3 --discount_fallback < /corpus.txt > "$ARPA_FILE"

echo "✓ ARPA model created: $ARPA_FILE"

# Convert ARPA to binary format for faster loading
echo "Converting to binary format..."
docker run --rm \
    -v "$OUTPUT_DIR:/data" \
    kensho/kenlm:latest \
    build_binary /data/$(basename "$ARPA_FILE") /data/$(basename "$BINARY_FILE")

echo "✓ Binary model created: $BINARY_FILE"

# Show model stats
echo ""
echo "=========================================="
echo "Model Statistics"
echo "=========================================="
ls -lh "$ARPA_FILE" "$BINARY_FILE"
echo ""
echo "✓ KenLM model ready for NeMo ASR fusion"
echo ""
echo "Model files:"
echo "  ARPA:   $ARPA_FILE"
echo "  Binary: $BINARY_FILE"
echo ""
echo "Next: Update parakeet_wrapper.py to use this model with fusion_models parameter"
