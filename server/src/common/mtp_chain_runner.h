// Generic gamma-loop for MTP speculative decoding.

#pragma once

#include "model_backend.h"
#include "mtp_interface.h"
#include "sampler.h"

#include <vector>

namespace dflash::common {

struct DFlashTarget;

namespace mtp {

struct MtpChainStats {
    int total_iters    = 0;
    int total_proposed = 0;
    int total_accepted = 0;
    int total_emitted  = 0;
    int eos_hits       = 0;
};

class MtpChainRunner {
public:
    MtpChainRunner(IMtpModule & mtp,
                   DFlashTarget & target,
                   const SamplerCfg & sampler);

    GenerateResult run(const GenerateRequest & req,
                       const DaemonIO & io,
                       int32_t last_prefill_token,
                       int committed_pos,
                       int gamma);

    const MtpChainStats & stats() const { return stats_; }

private:
    IMtpModule   & mtp_;
    DFlashTarget & target_;
    SamplerCfg     sampler_cfg_;
    MtpChainStats  stats_;

    bool propose_drafts_(int32_t current_token,
                         int base_pos,
                         int gamma,
                         const float * prev_hidden,
                         int prev_hidden_dim,
                         std::vector<int32_t> & drafts_out,
                         std::vector<float> & next_hidden_out);
};

}  // namespace mtp
}  // namespace dflash::common
