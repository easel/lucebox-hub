#include "draft_config_json.h"

#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>

namespace dflash27b {

int parse_json_int(const std::string & cfg, const char * key) {
    std::string needle = std::string("\"") + key + "\"";
    auto p = cfg.find(needle);
    if (p == std::string::npos) return -1;
    auto colon = cfg.find(':', p + needle.size());
    if (colon == std::string::npos) return -1;
    return std::atoi(cfg.c_str() + colon + 1);
}

DraftConfigJson read_draft_config_json(const std::string & model_path) {
    DraftConfigJson d;

    std::string dir;
    auto slash = model_path.find_last_of('/');
    if (slash != std::string::npos) {
        dir = model_path.substr(0, slash);
    } else {
        dir = ".";  // bare filename — look in CWD
    }
    std::string cfg_path = dir + "/config.json";
    FILE * f = std::fopen(cfg_path.c_str(), "r");
    if (!f) return d;
    std::fseek(f, 0, SEEK_END);
    long flen = std::ftell(f);
    std::fseek(f, 0, SEEK_SET);
    if (flen <= 0) { std::fclose(f); return d; }
    std::string cfg((size_t)flen, '\0');
    std::fread(&cfg[0], 1, (size_t)flen, f);
    std::fclose(f);

    d.n_embd     = parse_json_int(cfg, "hidden_size");
    d.n_head     = parse_json_int(cfg, "num_attention_heads");
    d.n_head_kv  = parse_json_int(cfg, "num_key_value_heads");
    d.head_dim   = parse_json_int(cfg, "head_dim");
    d.n_ff       = parse_json_int(cfg, "intermediate_size");
    d.swa_window = parse_json_int(cfg, "sliding_window");

    // layer_types: ["sliding_attention", "full_attention", ...]
    auto lt_pos = cfg.find("\"layer_types\"");
    if (lt_pos != std::string::npos) {
        auto arr_start = cfg.find('[', lt_pos);
        auto arr_end   = cfg.find(']', arr_start);
        if (arr_start != std::string::npos && arr_end != std::string::npos) {
            std::string arr = cfg.substr(arr_start, arr_end - arr_start + 1);
            size_t search_pos = 0;
            while (search_pos < arr.size()) {
                auto q1 = arr.find('"', search_pos);
                if (q1 == std::string::npos) break;
                auto q2 = arr.find('"', q1 + 1);
                if (q2 == std::string::npos) break;
                std::string lt = arr.substr(q1 + 1, q2 - q1 - 1);
                d.layer_is_swa.push_back(lt == "sliding_attention");
                search_pos = q2 + 1;
            }
        }
    }
    return d;
}

int pick_draft_dim(int from_cfg, int from_target, int fallback) {
    if (from_cfg    > 0) return from_cfg;
    if (from_target > 0) return from_target;
    return fallback;
}

}  // namespace dflash27b
