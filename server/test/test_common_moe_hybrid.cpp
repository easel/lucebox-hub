#include "../src/common/moe_hybrid_placement.h"
#include "../src/common/moe_hybrid_routing_stats.h"
#include "../src/common/moe_hybrid_swap_manager.h"

#include <cstdio>
#include <cstdlib>
#include <filesystem>
#include <string>
#include <vector>

using namespace dflash::common;

static void expect(bool cond, const char * msg) {
    if (!cond) {
        std::fprintf(stderr, "FAIL: %s\n", msg);
        std::exit(1);
    }
}

int main() {
    MoeHybridRoutingStats stats;
    expect(stats.init(2, 4, 2), "stats init");
    const int32_t layer0_a[] = {2, 1};
    const int32_t layer0_b[] = {2, 3};
    const int32_t layer1_a[] = {0, 0};
    expect(stats.observe(0, layer0_a, 2), "observe layer0_a");
    expect(stats.observe(0, layer0_b, 2), "observe layer0_b");
    expect(stats.observe(1, layer1_a, 2), "observe layer1_a");
    expect(stats.count(0, 2) == 2, "layer0 expert2 count");
    expect(stats.layer_totals[0] == 4, "layer0 total");

    const auto csv_tmp = std::filesystem::temp_directory_path() / "moe-hybrid-routing-stats-test.csv";
    std::string err;
    expect(stats.save_csv(csv_tmp.string(), &err), err.c_str());
    MoeHybridRoutingStats loaded;
    expect(MoeHybridRoutingStats::load_csv(csv_tmp.string(), loaded, &err), err.c_str());
    expect(loaded.matches(2, 4, 2), "loaded dimensions");
    expect(loaded.count(0, 2) == 2, "loaded count");
    std::filesystem::remove(csv_tmp);

    MoeHybridPlacement placement;
    expect(MoeHybridPlacement::build_from_stats(stats, 2, 1, placement, &err), err.c_str());
    expect(placement.matches(2, 4, 2), "placement dimensions");
    expect(placement.total_hot == 2, "placement hot budget");
    expect(placement.is_hot(0, 2), "layer0 hot expert");
    expect(placement.is_hot(1, 0), "layer1 hot expert");

    const auto json_tmp = std::filesystem::temp_directory_path() / "moe-hybrid-placement-test.json";
    expect(placement.save_json(json_tmp.string(), "moe_hybrid_test", &err), err.c_str());
    MoeHybridPlacement loaded_placement;
    expect(MoeHybridPlacement::load_json(json_tmp.string(), loaded_placement, &err), err.c_str());
    expect(loaded_placement.matches(2, 4, 2), "loaded placement dimensions");
    expect(loaded_placement.is_hot(0, 2), "loaded placement hot expert");
    std::filesystem::remove(json_tmp);

    MoeHybridSwapPolicy policy;
    policy.max_swaps_total = 1;
    policy.min_promote_gain = 1;

    MoeHybridPlacement current;
    current.n_layer = 2;
    current.n_expert = 4;
    current.n_expert_used = 2;
    current.total_hot = 2;
    current.hot_counts = {1, 1};
    current.hot_expert_ids = {{1}, {0}};

    MoeHybridSwapPlan plan;
    expect(build_moe_hybrid_swap_plan(current, stats, policy, plan, &err), err.c_str());
    expect(plan.actions.size() == 1, "one swap planned");
    expect(plan.actions[0].layer_idx == 0, "swap layer");
    expect(plan.actions[0].evict_expert == 1, "evict weaker hot expert");
    expect(plan.actions[0].promote_expert == 2, "promote hottest cold expert");

    std::printf("OK\n");
    return 0;
}
