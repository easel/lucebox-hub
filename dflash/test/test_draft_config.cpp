// Unit tests for draft_config_json.{h,cpp} — pure functions, no GPU and no
// real model files required. Exits 0 on success, 1 on first failure.
//
// Build:
//   cmake --build build --target test_draft_config -j
// Run:
//   ./build/test_draft_config

#include "draft_config_json.h"

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>

namespace dflash27b {

#define CHECK(cond) do { \
    if (!(cond)) { \
        std::fprintf(stderr, "FAIL %s:%d: %s\n", __FILE__, __LINE__, #cond); \
        std::exit(1); \
    } \
} while (0)

#define CHECK_EQ(a, b) do { \
    auto _av = (a); auto _bv = (b); \
    if (_av != _bv) { \
        std::fprintf(stderr, "FAIL %s:%d: %s != %s (%lld != %lld)\n", \
                     __FILE__, __LINE__, #a, #b, (long long)_av, (long long)_bv); \
        std::exit(1); \
    } \
} while (0)

// ─── Layer 1a: parse_json_int ─────────────────────────────────────

static void test_parse_simple() {
    std::string cfg = R"({"head_dim": 128, "hidden_size": 5120})";
    CHECK_EQ(parse_json_int(cfg, "head_dim"),    128);
    CHECK_EQ(parse_json_int(cfg, "hidden_size"), 5120);
    CHECK_EQ(parse_json_int(cfg, "missing_key"), -1);
}

static void test_parse_whitespace_and_commas() {
    std::string cfg = "{\n  \"head_dim\"   :    128 ,\n  \"x\": 0\n}";
    CHECK_EQ(parse_json_int(cfg, "head_dim"), 128);
    // "x": 0 — atoi returns 0; callers (pick_draft_dim) treat 0 as unset.
    CHECK_EQ(parse_json_int(cfg, "x"), 0);
}

static void test_parse_partial_key_no_false_match() {
    // The needle includes both quotes — "head" must NOT match "head_dim" or
    // "head_count" because their closing quote is past `head`.
    std::string cfg = R"({"head_dim": 128, "head_count": 24})";
    CHECK_EQ(parse_json_int(cfg, "head"),       -1);
    CHECK_EQ(parse_json_int(cfg, "head_dim"),   128);
    CHECK_EQ(parse_json_int(cfg, "head_count"), 24);
}

static void test_parse_malformed_no_crash() {
    // Missing colon — parser bails out cleanly.
    std::string cfg = R"({"foo" 128})";
    CHECK_EQ(parse_json_int(cfg, "foo"), -1);

    // Truncated file
    std::string cfg2 = R"({"head_dim":)";
    // atoi of empty/whitespace tail = 0. Acceptable: caller treats 0 as unset.
    CHECK_EQ(parse_json_int(cfg2, "head_dim"), 0);
}

static void test_parse_documented_limitation_string_value_shadow() {
    // Known limitation of the no-real-parser approach: if a string VALUE
    // matches the quoted key earlier in the JSON, the next ':' found is the
    // wrong field's colon. No real config we serve triggers this, but the
    // test documents the behavior so anyone switching to json-c notices.
    std::string cfg = R"({"foo": "head", "head_dim": 128})";
    // Current: returns 128 (wrong — grabbed head_dim's value while looking for "head").
    CHECK_EQ(parse_json_int(cfg, "head"), 128);
}

// ─── Layer 1b: read_draft_config_json (uses tmpfiles) ─────────────

static std::string make_tmp_dir() {
    char tmpl[] = "/tmp/dflash_test_cfg_XXXXXX";
    char * d = mkdtemp(tmpl);
    CHECK(d != nullptr);
    return std::string(d);
}

static void write_file(const std::string & path, const std::string & content) {
    FILE * f = std::fopen(path.c_str(), "w");
    CHECK(f != nullptr);
    std::fwrite(content.data(), 1, content.size(), f);
    std::fclose(f);
}

static void test_read_zlab_qwen36_shape_config() {
    // Mirrors the actual z-lab Qwen3.6-27B-DFlash config.json fields we read.
    std::string dir = make_tmp_dir();
    std::string model_path = dir + "/model.safetensors";  // file need not exist
    write_file(dir + "/config.json", R"({
        "block_size": 16,
        "head_dim": 128,
        "hidden_size": 5120,
        "intermediate_size": 17408,
        "num_attention_heads": 32,
        "num_key_value_heads": 8,
        "sliding_window": 2048,
        "use_sliding_window": true,
        "layer_types": [
            "sliding_attention",
            "sliding_attention",
            "sliding_attention",
            "sliding_attention",
            "full_attention"
        ]
    })");

    DraftConfigJson cfg = read_draft_config_json(model_path);
    CHECK_EQ(cfg.head_dim,    128);
    CHECK_EQ(cfg.n_embd,      5120);
    CHECK_EQ(cfg.n_ff,        17408);
    CHECK_EQ(cfg.n_head,      32);
    CHECK_EQ(cfg.n_head_kv,   8);
    CHECK_EQ(cfg.swa_window,  2048);
    CHECK_EQ((int)cfg.layer_is_swa.size(), 5);
    CHECK(cfg.layer_is_swa[0] == true);
    CHECK(cfg.layer_is_swa[1] == true);
    CHECK(cfg.layer_is_swa[2] == true);
    CHECK(cfg.layer_is_swa[3] == true);
    CHECK(cfg.layer_is_swa[4] == false);
}

static void test_read_missing_config_returns_sentinels() {
    // No config.json in the directory → struct stays at defaults.
    std::string dir = make_tmp_dir();
    DraftConfigJson cfg = read_draft_config_json(dir + "/model.safetensors");
    CHECK_EQ(cfg.head_dim,                 -1);
    CHECK_EQ(cfg.n_embd,                   -1);
    CHECK_EQ(cfg.n_head,                   -1);
    CHECK_EQ(cfg.n_head_kv,                -1);
    CHECK_EQ(cfg.n_ff,                     -1);
    CHECK_EQ(cfg.swa_window,               -1);
    CHECK_EQ((int)cfg.layer_is_swa.size(), 0);
}

static void test_read_bare_filename_no_crash() {
    // Bare filename → look in CWD. CWD has no config.json in CI's checkout;
    // verify the function returns sentinels without crashing on missing file.
    DraftConfigJson cfg = read_draft_config_json("nonexistent_model.safetensors");
    CHECK_EQ(cfg.head_dim, -1);
}

static void test_read_partial_config() {
    // Only some fields present — the rest stay at -1.
    std::string dir = make_tmp_dir();
    write_file(dir + "/config.json", R"({"head_dim": 128, "num_attention_heads": 32})");
    DraftConfigJson cfg = read_draft_config_json(dir + "/model.safetensors");
    CHECK_EQ(cfg.head_dim,   128);
    CHECK_EQ(cfg.n_head,     32);
    CHECK_EQ(cfg.n_embd,     -1);
    CHECK_EQ(cfg.n_head_kv,  -1);
    CHECK_EQ((int)cfg.layer_is_swa.size(), 0);
}

// ─── Layer 2: pick_draft_dim precedence ───────────────────────────

static void test_pick_cfg_wins_over_target_the_actual_bug() {
    // This is the bug case: target was inheriting head_dim=256 into the draft,
    // overriding the draft's true value 128. With pick_draft_dim, cfg wins.
    CHECK_EQ(pick_draft_dim(/*cfg=*/128, /*target=*/256, /*fallback=*/64), 128);
}

static void test_pick_target_when_no_cfg() {
    // No config.json field → fall back to target. (Legitimate for n_embd/n_ff
    // which are shared with the verifier.)
    CHECK_EQ(pick_draft_dim(-1, 256, 64), 256);
}

static void test_pick_fallback_when_no_cfg_no_target() {
    // No config, no target → compile-time default.
    CHECK_EQ(pick_draft_dim(-1, -1, 64), 64);
}

static void test_pick_zero_is_unset() {
    // A zero dim is never legitimate (rank-0 tensor). Treat as unset so atoi
    // failure ("foo": null, or absent → atoi returns 0) falls through cleanly.
    CHECK_EQ(pick_draft_dim(0, 256, 64), 256);
    CHECK_EQ(pick_draft_dim(0,   0, 64), 64);
}

static void test_pick_negative_is_unset() {
    CHECK_EQ(pick_draft_dim(-1, 256, 64), 256);
    CHECK_EQ(pick_draft_dim(-1,  -1, 64), 64);
}

// ─── Driver ───────────────────────────────────────────────────────

static int run_tests() {
    test_parse_simple();
    test_parse_whitespace_and_commas();
    test_parse_partial_key_no_false_match();
    test_parse_malformed_no_crash();
    test_parse_documented_limitation_string_value_shadow();
    test_read_zlab_qwen36_shape_config();
    test_read_missing_config_returns_sentinels();
    test_read_bare_filename_no_crash();
    test_read_partial_config();
    test_pick_cfg_wins_over_target_the_actual_bug();
    test_pick_target_when_no_cfg();
    test_pick_fallback_when_no_cfg_no_target();
    test_pick_zero_is_unset();
    test_pick_negative_is_unset();
    std::printf("test_draft_config: 14 tests passed\n");
    return 0;
}

}  // namespace dflash27b

int main() { return dflash27b::run_tests(); }
