#!/usr/bin/env python3
"""
Check the transcribe() method signature and available parameters
for runtime phrase/hotword passing
"""
import nemo.collections.asr as nemo_asr
import inspect

MODEL_PATH = "/models/parakeet-tdt-0.6b-v3.nemo"

print("=" * 80)
print("Loading Parakeet-TDT-0.6B-v3 model...")
print("=" * 80)

model = nemo_asr.models.ASRModel.restore_from(MODEL_PATH)

print("\n" + "=" * 80)
print("TRANSCRIBE METHOD SIGNATURE")
print("=" * 80)
sig = inspect.signature(model.transcribe)
print(f"Method: model.transcribe{sig}")

print("\n" + "=" * 80)
print("TRANSCRIBE METHOD DOCSTRING")
print("=" * 80)
if model.transcribe.__doc__:
    print(model.transcribe.__doc__)
else:
    print("No docstring available")

print("\n" + "=" * 80)
print("CHECKING FOR WORD/PHRASE BOOSTING PARAMETERS")
print("=" * 80)

# Get the actual method
transcribe_method = model.transcribe

# Check if it's the parent class method
print(f"Method defined in: {transcribe_method.__qualname__}")
print(f"Module: {transcribe_method.__module__}")

# Try to get source code
print("\nAttempting to get method source...")
try:
    source = inspect.getsource(transcribe_method)
    # Look for relevant keywords
    keywords = ['hotword', 'phrase', 'bias', 'context', 'boost']
    print("\nSearching for relevant keywords in source:")
    for keyword in keywords:
        if keyword.lower() in source.lower():
            print(f"  ✓ Found '{keyword}' in source")
            # Show lines containing the keyword
            for i, line in enumerate(source.split('\n')):
                if keyword.lower() in line.lower():
                    print(f"    Line {i}: {line.strip()}")
        else:
            print(f"  ✗ '{keyword}' not found")
except Exception as e:
    print(f"Could not retrieve source: {e}")

print("\n" + "=" * 80)
print("CHECKING DECODING OBJECT FOR RUNTIME CONFIGURATION")
print("=" * 80)

# Check if decoding object has methods for setting phrases
decoding_obj = model.decoding
print(f"Decoding object type: {type(decoding_obj)}")

print("\nMethods containing 'bias', 'phrase', 'context', or 'boost':")
for attr in dir(decoding_obj):
    if any(keyword in attr.lower() for keyword in ['bias', 'phrase', 'context', 'boost']):
        print(f"  - {attr}")
        obj = getattr(decoding_obj, attr)
        if callable(obj):
            try:
                sig = inspect.signature(obj)
                print(f"    Signature: {attr}{sig}")
            except:
                pass

print("\n" + "=" * 80)
print("CHECKING FOR BEAM SEARCH WITH WORD BOOSTING")
print("=" * 80)

# Check beam search configuration
from omegaconf import OmegaConf
print("Beam configuration:")
print(OmegaConf.to_yaml(model.cfg.decoding.beam))

# Try to find rnnt_decoding module documentation
print("\n" + "=" * 80)
print("RNNT DECODING MODULE INSPECTION")
print("=" * 80)

import nemo.collections.asr.parts.submodules.rnnt_decoding as rnnt_dec_module
print(f"Module: {rnnt_dec_module}")

# Check what classes are available
print("\nAvailable classes in rnnt_decoding:")
for item in dir(rnnt_dec_module):
    if not item.startswith('_') and item[0].isupper():
        print(f"  - {item}")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
