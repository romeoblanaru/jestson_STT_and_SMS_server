#!/usr/bin/env python3
"""
Deep inspection of decoder hierarchy to find where the boosting tree model is
"""
import requests
import json

print("=" * 80)
print("QUERYING DIAGNOSTIC ENDPOINT")
print("=" * 80)

response = requests.get("http://192.168.1.9:9001/diagnostic")
data = response.json()

print("\nConfiguration summary:")
print(f"  Config has boosting_tree: {data['config']['boosting_tree']['exists']}")
print(f"  Config phrases count: {data['config']['boosting_tree']['key_phrases_count']}")
print(f"  Config boosting_tree_alpha: {data['config']['boosting_tree_alpha']}")

print("\nDecoder state summary:")
print(f"  Decoder type: {data['decoder_state']['inner_decoder_type']}")
print(f"  Has boosting_tree_model: {data['decoder_state']['boosting_tree_model']['exists']}")
print(f"  boosting_tree_alpha: {data['decoder_state']['boosting_tree_alpha']}")

print("\nDecoder attributes (searching for 'boost', 'tree', 'context', 'bias'):")
for attr in data['decoder_state']['decoder_attributes']:
    if any(keyword in attr.lower() for keyword in ['boost', 'tree', 'context', 'bias']):
        print(f"  - {attr}")

print("\n" + "=" * 80)
print("ANALYZING THE PROBLEM")
print("=" * 80)

print("""
ISSUE IDENTIFIED:
- Configuration (model.cfg.decoding.greedy) has boosting_tree properly configured
- But the actual decoder object (GreedyBatchedTDTInfer) does NOT have boosting_tree_model
- This means change_decoding_strategy() created the GPUBoostingTreeModel but didn't attach it

POSSIBLE CAUSES:
1. GreedyBatchedTDTInfer (TDT greedy decoder) may not support boosting tree
2. Boosting tree might only work with beam search for TDT models
3. There might be a NeMo bug where TDT + CUDA graphs + boosting tree are incompatible
4. The boosting tree model might be stored in a different location we're not checking

NEXT STEPS TO INVESTIGATE:
1. Check if RNNTBPEDecoding (parent) stores the boosting tree model
2. Try disabling CUDA graphs to see if boosting tree works then
3. Check NeMo source code for TDT + boosting tree compatibility
4. Try beam search instead of greedy to see if it supports boosting tree
""")
