#pragma once

// Parser for the draft model's `config.json` (next to model.safetensors)
// and the precedence picker for dim resolution.
//
// Extracted from draft_safetensors_loader.cpp so the pure parts can be
// unit-tested without a CUDA backend or real model files. See
// `test/test_draft_config.cpp`.
//
// The hand-rolled JSON parser keeps the no-dep style of safetensors_loader.
// If we ever depend on a real JSON library this whole file should fold into
// a thin adapter.

#include <string>
#include <vector>

namespace dflash27b {

// Fields parsed out of config.json. Unset fields keep the sentinel -1 (and
// empty `layer_is_swa` vector); callers fall back to target metadata or
// compile-time defaults.
struct DraftConfigJson {
    int n_embd        = -1;  // "hidden_size"
    int n_head        = -1;  // "num_attention_heads"
    int n_head_kv     = -1;  // "num_key_value_heads"
    int head_dim      = -1;  // "head_dim"
    int n_ff          = -1;  // "intermediate_size"
    int swa_window    = -1;  // "sliding_window"
    std::vector<bool> layer_is_swa;  // per-layer; "sliding_attention" → true
};

// Pull a top-level integer field from a JSON string. Returns -1 if the key
// is absent. Limitation: the parser is greedy on the first occurrence of
// the quoted key, so a key appearing as a string *value* before the real
// key-value pair can shadow it. No real configs we serve trigger this; the
// test suite documents the limitation.
int parse_json_int(const std::string & cfg, const char * key);

// Read the draft's adjacent config.json. Looks next to `model_path`
// (a bare filename falls back to CWD). Returns a `DraftConfigJson` with
// sentinels for any field not present in the file. Never throws.
DraftConfigJson read_draft_config_json(const std::string & model_path);

// Choose a draft dim with precedence: config.json > target metadata > fallback.
// Treats non-positive values from the first two sources as "unset". The
// fallback is assumed sensible by the caller (no sentinel check).
int pick_draft_dim(int from_cfg, int from_target, int fallback);

}  // namespace dflash27b
