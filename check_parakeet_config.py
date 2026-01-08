#!/usr/bin/env python3
"""
Check Parakeet-TDT-0.6B-v3 configuration options for character/vocabulary filtering
"""
import nemo.collections.asr as nemo_asr
from omegaconf import OmegaConf

print("=" * 60)
print("Loading Parakeet-TDT-0.6B-v3 model...")
print("=" * 60)

model = nemo_asr.models.ASRModel.restore_from('/models/parakeet-tdt-0.6b-v3.nemo')

print("\n" + "=" * 60)
print("DECODING CONFIGURATION")
print("=" * 60)
print(OmegaConf.to_yaml(model.cfg.decoding))

print("\n" + "=" * 60)
print("TOKENIZER INFORMATION")
print("=" * 60)
print(f"Tokenizer type: {type(model.tokenizer).__name__}")
if hasattr(model.tokenizer, 'vocab_size'):
    print(f"Vocab size: {model.tokenizer.vocab_size}")

print("\n" + "=" * 60)
print("DECODER CONFIGURATION")
print("=" * 60)
if hasattr(model.cfg, 'decoder'):
    print(OmegaConf.to_yaml(model.cfg.decoder))
else:
    print("No separate decoder config found")

print("\n" + "=" * 60)
print("MODEL CONFIGURATION (Full)")
print("=" * 60)
print(OmegaConf.to_yaml(model.cfg))
