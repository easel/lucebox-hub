// Generic MTP (Multi-Token Prediction) module interface.

#pragma once

#include <cstdint>
#include <vector>

namespace dflash::common {

struct DFlashTarget;

namespace mtp {

enum class MtpFlavor {
    ExternalDrafter,
    NativeHeads,
};

struct StepInput {
    int32_t       current_token   = -1;
    int           base_pos        = 0;
    int           gamma_index     = 0;
    const float * prev_hidden     = nullptr;
    int           prev_hidden_dim = 0;
};

struct StepOutput {
    int32_t              draft_token = -1;
    float                draft_logit = 0.0f;
    std::vector<float>   next_hidden;
    std::vector<float>   topk_logprobs;
    std::vector<int32_t> topk_ids;
};

struct IMtpModule {
    virtual ~IMtpModule() = default;

    virtual MtpFlavor flavor() const = 0;
    virtual int max_gamma() const = 0;
    virtual int  effective_gamma() const = 0;
    virtual void set_effective_gamma(int gamma) = 0;
    virtual int hidden_size() const = 0;
    virtual bool attach(DFlashTarget * target) = 0;
    virtual void reset_chain() = 0;
    virtual void shutdown() = 0;

    virtual void set_initial_hidden(const float * /*h_prev*/, int /*dim*/) {}
};

struct IExternalDrafterMtp : IMtpModule {
    MtpFlavor flavor() const final { return MtpFlavor::ExternalDrafter; }

    virtual bool step(const StepInput & in, StepOutput & out) = 0;
    virtual const std::vector<int> & donor_layers() const = 0;
    virtual bool enable_target_hidden_capture(bool batch_mode, int gamma_max) = 0;
    virtual void set_capture_row(int row) = 0;
    virtual bool consume_captured_hidden(float * out, int dim) = 0;
};

struct INativeMtp : IMtpModule {
    MtpFlavor flavor() const final { return MtpFlavor::NativeHeads; }

    virtual int num_heads() const = 0;

    virtual bool step_batch(int32_t current_token,
                            int base_pos,
                            std::vector<StepOutput> & out) = 0;

    virtual void set_draft_topk(int /*k*/) {}

    virtual bool step_chain(int32_t current_token,
                            int base_pos,
                            int /*chain_depth*/,
                            std::vector<StepOutput> & out) {
        return step_batch(current_token, base_pos, out);
    }

    virtual bool warm_head_kv(const int32_t * /*prompt*/, int /*n_prompt*/,
                              int32_t /*prefill_next*/, const float * /*hiddens*/) {
        return true;
    }
};

}  // namespace mtp
}  // namespace dflash::common
