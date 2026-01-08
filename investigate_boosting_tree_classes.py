#!/usr/bin/env python3
"""
Investigate BoostingTreeModelConfig and GPUBoostingTreeModel classes
to understand how to properly enable phrase boosting for RNNT models
"""
import nemo.collections.asr as nemo_asr
from nemo.collections.asr.parts.submodules.rnnt_decoding import (
    BoostingTreeModelConfig,
    GPUBoostingTreeModel,
    RNNTBPEDecodingConfig
)
import inspect
from omegaconf import OmegaConf

MODEL_PATH = "/models/parakeet-tdt-0.6b-v3.nemo"

print("=" * 80)
print("BOOSTING TREE MODEL CONFIG")
print("=" * 80)

# Check BoostingTreeModelConfig
print(f"Class: {BoostingTreeModelConfig}")
print(f"\nSignature: {inspect.signature(BoostingTreeModelConfig)}")

if BoostingTreeModelConfig.__doc__:
    print(f"\nDocstring:\n{BoostingTreeModelConfig.__doc__}")

# Try to create an instance
try:
    print("\nAttempting to create BoostingTreeModelConfig instance...")
    config = BoostingTreeModelConfig()
    print(f"✓ Created: {config}")
    print(f"Config attributes:")
    for attr in dir(config):
        if not attr.startswith('_'):
            try:
                val = getattr(config, attr)
                if not callable(val):
                    print(f"  {attr}: {val}")
            except:
                pass
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 80)
print("GPU BOOSTING TREE MODEL")
print("=" * 80)

print(f"Class: {GPUBoostingTreeModel}")
print(f"\nSignature: {inspect.signature(GPUBoostingTreeModel)}")

if GPUBoostingTreeModel.__doc__:
    print(f"\nDocstring:\n{GPUBoostingTreeModel.__doc__}")

print("\n" + "=" * 80)
print("RNNT BPE DECODING CONFIG")
print("=" * 80)

print(f"Class: {RNNTBPEDecodingConfig}")
print(f"\nSignature: {inspect.signature(RNNTBPEDecodingConfig)}")

# Try to inspect the source
try:
    source = inspect.getsource(RNNTBPEDecodingConfig)
    print("\nSearching for 'boosting' in RNNTBPEDecodingConfig source:")
    for i, line in enumerate(source.split('\n')[:50]):  # First 50 lines
        if 'boosting' in line.lower() or 'bias' in line.lower():
            print(f"  Line {i}: {line}")
except Exception as e:
    print(f"Could not get source: {e}")

print("\n" + "=" * 80)
print("CHECKING MODEL'S CURRENT DECODING CONFIG")
print("=" * 80)

model = nemo_asr.models.ASRModel.restore_from(MODEL_PATH)

print("\nModel's decoding object type:")
print(f"  {type(model.decoding)}")

print("\nModel's decoding config type:")
print(f"  {type(model.cfg.decoding)}")

# Check if there's a way to add GPUBoostingTreeModel to the decoder
print("\nChecking decoder for boosting tree integration...")
if hasattr(model.decoding, 'decoding'):
    inner_decoding = model.decoding.decoding
    print(f"Inner decoding type: {type(inner_decoding)}")
    print(f"Inner decoding attributes containing 'boost':")
    for attr in dir(inner_decoding):
        if 'boost' in attr.lower():
            print(f"  - {attr}")

# Try to access the actual greedy decoder
print("\nChecking for greedy decoder instance...")
for attr in ['greedy_decoder', '_greedy_decoder', 'decoder_greedy', 'greedy']:
    if hasattr(model.decoding, attr):
        print(f"✓ Found: {attr}")
        obj = getattr(model.decoding, attr)
        print(f"  Type: {type(obj)}")
        print(f"  Attributes with 'boost': {[x for x in dir(obj) if 'boost' in x.lower()]}")

print("\n" + "=" * 80)
print("TRYING TO CREATE DECODING CONFIG WITH BOOSTING TREE")
print("=" * 80)

try:
    # Try to create a decoding config with boosting tree
    from omegaconf import OmegaConf, open_dict

    print("\nAttempting to create greedy config with boosting_tree...")
    greedy_cfg = OmegaConf.create({
        'max_symbols': 10,
        'boosting_tree': {
            'key_phrases_list': ['test phrase'],
            'context_score': 4.0,
            'use_triton': True
        },
        'boosting_tree_alpha': 1.0
    })
    print(f"✓ Created config:\n{OmegaConf.to_yaml(greedy_cfg)}")

    print("\nTrying to apply this to model...")
    with open_dict(model.cfg.decoding):
        model.cfg.decoding.greedy = greedy_cfg

    print("Calling change_decoding_strategy...")
    model.change_decoding_strategy(model.cfg.decoding)
    print("✓ Strategy changed")

    print("\nVerifying configuration persisted:")
    if hasattr(model.cfg.decoding.greedy, 'boosting_tree'):
        print(f"✓ boosting_tree exists: {model.cfg.decoding.greedy.boosting_tree}")
    else:
        print("✗ boosting_tree was not persisted")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("INVESTIGATION COMPLETE")
print("=" * 80)
