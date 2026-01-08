#!/usr/bin/env python3
"""
Verify that boosting tree is actually active in the running model
by inspecting the decoder's internal state
"""
import requests
import json

# First, check server health
print("=" * 80)
print("CHECKING SERVER HEALTH")
print("=" * 80)
response = requests.get("http://192.168.1.9:9001/health")
print(f"Health check: {response.status_code}")
print(json.dumps(response.json(), indent=2))

# Now create a diagnostic endpoint check
print("\n" + "=" * 80)
print("CREATING DIAGNOSTIC SCRIPT TO RUN INSIDE CONTAINER")
print("=" * 80)

diagnostic_script = """
import sys
sys.path.insert(0, '/workspace')

# Import the running model from the Flask app
from parakeet_wrapper import model

print("=" * 80)
print("CHECKING BOOSTING TREE IN RUNNING MODEL")
print("=" * 80)

# Check if model has decoding object
if hasattr(model, 'decoding'):
    decoding = model.decoding
    print(f"✓ Model has decoding object: {type(decoding)}")

    # Check if decoding has the greedy decoder
    if hasattr(decoding, 'decoding'):
        greedy_decoder = decoding.decoding
        print(f"✓ Greedy decoder type: {type(greedy_decoder)}")

        # Check for boosting tree model
        if hasattr(greedy_decoder, 'boosting_tree_model'):
            boost_model = greedy_decoder.boosting_tree_model
            print(f"✓ Boosting tree model exists: {type(boost_model)}")

            # Get boosting tree details
            if boost_model is not None:
                print(f"  - Model is active: YES")
                if hasattr(boost_model, 'cfg'):
                    cfg = boost_model.cfg
                    print(f"  - Config type: {type(cfg)}")
                    if hasattr(cfg, 'key_phrases_list'):
                        phrases = cfg.key_phrases_list
                        print(f"  - Number of phrases: {len(phrases) if phrases else 0}")
                        if phrases:
                            print(f"  - First phrase: {phrases[0]}")
                            print(f"  - Context score: {cfg.context_score if hasattr(cfg, 'context_score') else 'N/A'}")
                            print(f"  - Use Triton: {cfg.use_triton if hasattr(cfg, 'use_triton') else 'N/A'}")
                    else:
                        print(f"  - Config attributes: {[x for x in dir(cfg) if not x.startswith('_')]}")
            else:
                print(f"  - Model is active: NO (None)")
        else:
            print(f"✗ No boosting_tree_model attribute found")
            print(f"  Available attributes: {[x for x in dir(greedy_decoder) if not x.startswith('_')][:20]}")

        # Check for boosting_tree_alpha
        if hasattr(greedy_decoder, 'boosting_tree_alpha'):
            print(f"✓ boosting_tree_alpha: {greedy_decoder.boosting_tree_alpha}")
        else:
            print(f"✗ No boosting_tree_alpha attribute")
    else:
        print(f"✗ No inner decoding object found")
else:
    print(f"✗ Model has no decoding object")

# Check configuration
print("\\n" + "=" * 80)
print("CHECKING MODEL CONFIGURATION")
print("=" * 80)

if hasattr(model, 'cfg'):
    if hasattr(model.cfg, 'decoding'):
        if hasattr(model.cfg.decoding, 'greedy'):
            greedy_cfg = model.cfg.decoding.greedy
            print(f"Greedy config type: {type(greedy_cfg)}")

            if hasattr(greedy_cfg, 'boosting_tree'):
                boost_cfg = greedy_cfg.boosting_tree
                print(f"✓ Boosting tree config exists")
                print(f"  - key_phrases_list length: {len(boost_cfg.key_phrases_list) if hasattr(boost_cfg, 'key_phrases_list') and boost_cfg.key_phrases_list else 0}")
                print(f"  - context_score: {boost_cfg.context_score if hasattr(boost_cfg, 'context_score') else 'N/A'}")
                print(f"  - use_triton: {boost_cfg.use_triton if hasattr(boost_cfg, 'use_triton') else 'N/A'}")
                print(f"  - source_lang: {boost_cfg.source_lang if hasattr(boost_cfg, 'source_lang') else 'N/A'}")
            else:
                print(f"✗ No boosting_tree in greedy config")

            if hasattr(greedy_cfg, 'boosting_tree_alpha'):
                print(f"✓ boosting_tree_alpha: {greedy_cfg.boosting_tree_alpha}")
            else:
                print(f"✗ No boosting_tree_alpha")

print("\\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
"""

# Write diagnostic script
with open('/tmp/check_boosting_tree.py', 'w') as f:
    f.write(diagnostic_script)

print("Diagnostic script created at /tmp/check_boosting_tree.py")
print("\nRunning diagnostic inside container...")
