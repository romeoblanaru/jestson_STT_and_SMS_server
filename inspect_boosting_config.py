#!/usr/bin/env python3
"""
Inspect Parakeet model's boosting tree configuration
to understand available parameters and their current values
"""
import nemo.collections.asr as nemo_asr
from omegaconf import OmegaConf, open_dict
import os

MODEL_PATH = "/models/parakeet-tdt-0.6b-v3.nemo"

print("=" * 80)
print("Loading Parakeet-TDT-0.6B-v3 model...")
print("=" * 80)

model = nemo_asr.models.ASRModel.restore_from(MODEL_PATH)
model.eval()

print("\n" + "=" * 80)
print("FULL DECODING CONFIGURATION")
print("=" * 80)
print(OmegaConf.to_yaml(model.cfg.decoding))

print("\n" + "=" * 80)
print("GREEDY DECODER ATTRIBUTES")
print("=" * 80)
if hasattr(model.cfg.decoding, 'greedy'):
    greedy_cfg = model.cfg.decoding.greedy
    print(f"Greedy config type: {type(greedy_cfg)}")
    print("\nAvailable attributes in greedy:")
    for attr in dir(greedy_cfg):
        if not attr.startswith('_'):
            try:
                value = getattr(greedy_cfg, attr)
                if not callable(value):
                    print(f"  {attr}: {value}")
            except:
                pass

print("\n" + "=" * 80)
print("BOOSTING TREE CONFIGURATION (if available)")
print("=" * 80)
if hasattr(model.cfg.decoding.greedy, 'boosting_tree'):
    boost_cfg = model.cfg.decoding.greedy.boosting_tree
    print(f"Boosting tree config found!")
    print(f"Type: {type(boost_cfg)}")
    print("\nYAML representation:")
    print(OmegaConf.to_yaml(boost_cfg))

    print("\nAll attributes:")
    for attr in dir(boost_cfg):
        if not attr.startswith('_'):
            try:
                value = getattr(boost_cfg, attr)
                if not callable(value):
                    print(f"  {attr}: {value}")
            except:
                pass
else:
    print("No boosting_tree configuration found in greedy decoder")

print("\n" + "=" * 80)
print("CHECKING FOR BOOSTING_TREE_ALPHA")
print("=" * 80)
if hasattr(model.cfg.decoding.greedy, 'boosting_tree_alpha'):
    print(f"boosting_tree_alpha exists: {model.cfg.decoding.greedy.boosting_tree_alpha}")
else:
    print("boosting_tree_alpha NOT found in greedy decoder")

print("\n" + "=" * 80)
print("DECODER OBJECT INSPECTION")
print("=" * 80)
if hasattr(model, 'decoding'):
    print(f"Model has 'decoding' attribute")
    print(f"Type: {type(model.decoding)}")
    print(f"Dir: {[x for x in dir(model.decoding) if not x.startswith('_')]}")

print("\n" + "=" * 80)
print("TESTING BOOSTING TREE CONFIGURATION")
print("=" * 80)

# Try to set boosting tree parameters like in parakeet_wrapper.py
test_phrases = ["test phrase one", "test phrase two"]

try:
    with open_dict(model.cfg.decoding):
        model.cfg.decoding.greedy.boosting_tree.key_phrases_list = test_phrases
        model.cfg.decoding.greedy.boosting_tree.context_score = 4.0
        model.cfg.decoding.greedy.boosting_tree.use_triton = True
        model.cfg.decoding.greedy.boosting_tree_alpha = 1.0

    print("✓ Successfully set boosting tree parameters")
    print("\nUpdated boosting tree config:")
    print(OmegaConf.to_yaml(model.cfg.decoding.greedy.boosting_tree))
    print(f"\nboosting_tree_alpha: {model.cfg.decoding.greedy.boosting_tree_alpha}")

    # Try to apply the configuration
    print("\nApplying configuration via change_decoding_strategy...")
    model.change_decoding_strategy(model.cfg.decoding)
    print("✓ change_decoding_strategy() succeeded")

    # Check if the configuration persisted
    print("\nVerifying configuration after change_decoding_strategy:")
    print(f"key_phrases_list length: {len(model.cfg.decoding.greedy.boosting_tree.key_phrases_list) if hasattr(model.cfg.decoding.greedy.boosting_tree, 'key_phrases_list') else 'NOT SET'}")
    print(f"context_score: {model.cfg.decoding.greedy.boosting_tree.context_score if hasattr(model.cfg.decoding.greedy.boosting_tree, 'context_score') else 'NOT SET'}")
    print(f"use_triton: {model.cfg.decoding.greedy.boosting_tree.use_triton if hasattr(model.cfg.decoding.greedy.boosting_tree, 'use_triton') else 'NOT SET'}")
    print(f"boosting_tree_alpha: {model.cfg.decoding.greedy.boosting_tree_alpha if hasattr(model.cfg.decoding.greedy, 'boosting_tree_alpha') else 'NOT SET'}")

except Exception as e:
    print(f"✗ Error setting boosting tree parameters: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("INSPECTION COMPLETE")
print("=" * 80)
