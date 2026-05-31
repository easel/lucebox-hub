#include "common/dflash_target.h"
#include "common/model_backend.h"
#include "common/mtp_chain_runner.h"
#include "common/mtp_interface.h"
#include "common/mtp_orchestrator.h"

#include <cassert>
#include <cstdio>
#include <string>
#include <vector>

namespace {

struct StubBackend : public dflash::common::ModelBackend {
    bool supports_mtp_value = false;

    void print_ready_banner() const override {}
    bool park(const std::string &) override { return true; }
    bool unpark(const std::string &) override { return true; }
    bool is_target_parked() const override { return false; }
    dflash::common::GenerateResult generate_impl(
            const dflash::common::GenerateRequest &,
            const dflash::common::DaemonIO &) override {
        return {};
    }
    bool snapshot_save(int) override { return false; }
    void snapshot_free(int) override {}
    bool snapshot_used(int) const override { return false; }
    int snapshot_cur_pos(int) const override { return 0; }
    dflash::common::GenerateResult restore_and_generate_impl(
            int,
            const dflash::common::GenerateRequest &,
            const dflash::common::DaemonIO &) override {
        return {};
    }
    bool handle_compress(const std::string &,
                         const dflash::common::DaemonIO &) override {
        return false;
    }
    void free_drafter() override {}
    bool supports_mtp() const override { return supports_mtp_value; }
    dflash::common::mtp::IMtpModule * mtp() override { return nullptr; }
    void shutdown() override {}
};

struct StubMtpModule : public dflash::common::mtp::INativeMtp {
    int reset_chain_calls = 0;
    int set_initial_hidden_calls = 0;
    int effective_gamma_value = 3;

    int max_gamma() const override { return 3; }
    int effective_gamma() const override { return effective_gamma_value; }
    void set_effective_gamma(int gamma) override { effective_gamma_value = gamma; }
    int hidden_size() const override { return 4; }
    bool attach(dflash::common::DFlashTarget *) override { return true; }
    void reset_chain() override { ++reset_chain_calls; }
    void shutdown() override {}
    int num_heads() const override { return 3; }
    bool step_batch(int32_t, int,
                    std::vector<dflash::common::mtp::StepOutput> &) override {
        return true;
    }
    void set_initial_hidden(const float *, int) override {
        ++set_initial_hidden_calls;
    }
};

struct StubTarget : public dflash::common::DFlashTarget {
    int verify_batch_calls = 0;

    bool verify_batch(const std::vector<int32_t> &, int, int &,
                      std::vector<int32_t> *) override {
        ++verify_batch_calls;
        return false;
    }
    bool snapshot_kv() override { return false; }
    bool restore_kv() override { return false; }
    bool is_eos(int) const override { return false; }
    bool embed_tokens(const int32_t *, int, float *) const override {
        return false;
    }
    bool project_hidden_to_tokens(const float *, int,
                                  std::vector<int32_t> &) override {
        return false;
    }
    int hidden_size() const override { return 4; }
    int mask_token_id() const override { return 0; }
    const std::vector<int> & capture_layer_ids() const override {
        static const std::vector<int> empty;
        return empty;
    }
};

struct FullStubBackend : public StubBackend {
    StubMtpModule mtp_module;
    StubTarget target;

    FullStubBackend() { supports_mtp_value = true; }
    dflash::common::mtp::IMtpModule * mtp() override { return &mtp_module; }
    dflash::common::DFlashTarget * dflash_target() override { return &target; }
};

struct SuccessStubTarget : public dflash::common::DFlashTarget {
    int argmax_token = 42;
    int accept_n = 0;
    int eos_token_id = -1;
    int verify_calls = 0;
    int hidden_sz = 4;
    int restore_kv_at_chain_calls = 0;
    mutable std::vector<float> hidden_seq_buf;
    mutable int hidden_seq_n = 0;

    bool verify_batch(const std::vector<int32_t> & tokens,
                      int,
                      int & last_tok,
                      std::vector<int32_t> * all_argmax) override {
        ++verify_calls;
        last_tok = argmax_token;
        if (all_argmax) {
            all_argmax->resize(tokens.size());
            for (int i = 0; i < (int)tokens.size(); ++i) {
                if (i < accept_n && i + 1 < (int)tokens.size()) {
                    (*all_argmax)[i] = tokens[(size_t)i + 1];
                } else {
                    (*all_argmax)[i] = argmax_token;
                }
            }
        }
        hidden_seq_n = (int)tokens.size();
        hidden_seq_buf.assign((size_t)hidden_seq_n * hidden_sz, 0.1f);
        return true;
    }
    bool snapshot_kv() override { return true; }
    bool restore_kv() override { return true; }
    bool restore_kv_at_chain(int) override {
        ++restore_kv_at_chain_calls;
        return false;
    }
    void enable_chain_capture(bool) override {}
    void capture_topology_for_chain(int, int) override {}
    bool is_eos(int tok) const override {
        return eos_token_id >= 0 && tok == eos_token_id;
    }
    bool embed_tokens(const int32_t *, int, float *) const override {
        return false;
    }
    bool project_hidden_to_tokens(const float *, int,
                                  std::vector<int32_t> &) override {
        return false;
    }
    int hidden_size() const override { return hidden_sz; }
    int mask_token_id() const override { return 0; }
    const std::vector<int> & capture_layer_ids() const override {
        static const std::vector<int> empty;
        return empty;
    }
    const float * last_hidden_seq(int * out_n) const override {
        if (out_n) *out_n = hidden_seq_n;
        return hidden_seq_n > 0 ? hidden_seq_buf.data() : nullptr;
    }
    const float * last_hidden() const override {
        return hidden_seq_buf.empty() ? nullptr : hidden_seq_buf.data();
    }
};

struct DraftStubMtpModule : public StubMtpModule {
    int32_t draft_token = 99;
    int warm_head_kv_calls = 0;

    bool step_batch(int32_t, int,
                    std::vector<dflash::common::mtp::StepOutput> & out) override {
        dflash::common::mtp::StepOutput step;
        step.draft_token = draft_token;
        out.push_back(step);
        return true;
    }
    bool step_chain(int32_t, int, int chain_depth,
                    std::vector<dflash::common::mtp::StepOutput> & out) override {
        for (int i = 0; i < chain_depth; ++i) {
            dflash::common::mtp::StepOutput step;
            step.draft_token = draft_token + i;
            out.push_back(step);
        }
        return true;
    }
    bool warm_head_kv(const int32_t *, int, int32_t, const float *) override {
        ++warm_head_kv_calls;
        return true;
    }
};

struct FailStepChainMtpModule : public StubMtpModule {
    bool step_chain(int32_t, int, int,
                    std::vector<dflash::common::mtp::StepOutput> &) override {
        return false;
    }
};

struct LiveStubBackend : public StubBackend {
    DraftStubMtpModule mtp_mod;
    SuccessStubTarget target;

    LiveStubBackend() { supports_mtp_value = true; }
    dflash::common::mtp::IMtpModule * mtp() override { return &mtp_mod; }
    dflash::common::DFlashTarget * dflash_target() override { return &target; }
};

struct StubExternalDrafter : public dflash::common::mtp::IExternalDrafterMtp {
    int max_gamma_value = 2;
    int effective_gamma_value = 2;
    int hidden_size_value = 8;
    int set_capture_row_calls = 0;
    int set_capture_row_last_arg = -1;
    int consume_calls = 0;
    bool consume_after_set_capture = false;
    std::vector<int> donor_layers_value{0, 1};

    int max_gamma() const override { return max_gamma_value; }
    int effective_gamma() const override { return effective_gamma_value; }
    void set_effective_gamma(int gamma) override { effective_gamma_value = gamma; }
    int hidden_size() const override { return hidden_size_value; }
    bool attach(dflash::common::DFlashTarget *) override { return true; }
    void reset_chain() override {}
    void shutdown() override {}
    bool step(const dflash::common::mtp::StepInput & in,
              dflash::common::mtp::StepOutput & out) override {
        out.draft_token = 100 + in.gamma_index;
        out.next_hidden.assign((size_t)hidden_size_value, 0.5f);
        return true;
    }
    const std::vector<int> & donor_layers() const override {
        return donor_layers_value;
    }
    bool enable_target_hidden_capture(bool, int) override { return true; }
    void set_capture_row(int row) override {
        ++set_capture_row_calls;
        set_capture_row_last_arg = row;
    }
    bool consume_captured_hidden(float * out, int dim) override {
        ++consume_calls;
        consume_after_set_capture = set_capture_row_calls > 0;
        for (int i = 0; i < dim; ++i) out[i] = 1.0f;
        return true;
    }
};

struct ExternalPartialTarget : public SuccessStubTarget {
    static constexpr int32_t kDivergeToken = 999;

    bool verify_batch(const std::vector<int32_t> & tokens,
                      int base_pos,
                      int & last_tok,
                      std::vector<int32_t> * all_argmax) override {
        SuccessStubTarget::verify_batch(tokens, base_pos, last_tok, all_argmax);
        if (all_argmax && all_argmax->size() >= 2) {
            (*all_argmax)[0] = 100;
            (*all_argmax)[1] = kDivergeToken;
        }
        last_tok = kDivergeToken;
        return true;
    }
};

}  // namespace

static void t1_null_backend() {
    dflash::common::GenerateRequest req;
    dflash::common::DaemonIO io;
    auto res = dflash::common::mtp::warm_and_decode(nullptr, req, io);
    assert(!res.ok);
    assert(res.error.find("backend") != std::string::npos);
    std::puts("T1 null_backend PASS");
}

static void t2_backend_without_mtp() {
    StubBackend b;
    dflash::common::GenerateRequest req;
    dflash::common::DaemonIO io;
    auto res = dflash::common::mtp::warm_and_decode(&b, req, io);
    assert(!res.ok);
    assert(res.error.find("MTP") != std::string::npos);
    std::puts("T2 backend_without_mtp PASS");
}

static void t3_empty_prompt() {
    StubBackend b;
    b.supports_mtp_value = true;
    dflash::common::GenerateRequest req;
    req.n_gen = 8;
    dflash::common::DaemonIO io;
    auto res = dflash::common::mtp::warm_and_decode(&b, req, io);
    assert(!res.ok);
    assert(res.error.find("prompt") != std::string::npos);
    std::puts("T3 empty_prompt PASS");
}

static void t4_generic_backend_dispatch() {
    FullStubBackend b;
    dflash::common::GenerateRequest req;
    req.prompt = {1, 2, 3, 4};
    req.n_gen = 4;
    dflash::common::DaemonIO io;
    auto res = dflash::common::mtp::warm_and_decode(&b, req, io);
    assert(!res.ok);
    assert(res.error.find("verify_batch") != std::string::npos);
    assert(b.target.verify_batch_calls >= 1);
    std::puts("T4 generic_backend_dispatch PASS");
}

static void t5_gamma_propagation() {
    DraftStubMtpModule mod1;
    mod1.effective_gamma_value = 1;
    SuccessStubTarget tgt1;
    dflash::common::SamplerCfg sampler;
    dflash::common::mtp::MtpChainRunner runner1(mod1, tgt1, sampler);
    dflash::common::GenerateRequest req1;
    req1.n_gen = 1;
    dflash::common::DaemonIO io;
    auto res1 = runner1.run(req1, io, 10, 4, 1);
    assert(res1.ok);

    DraftStubMtpModule mod2;
    mod2.effective_gamma_value = 2;
    SuccessStubTarget tgt2;
    dflash::common::mtp::MtpChainRunner runner2(mod2, tgt2, sampler);
    dflash::common::GenerateRequest req2;
    req2.n_gen = 2;
    auto res2 = runner2.run(req2, io, 10, 4, 2);
    assert(res2.ok);
    assert(runner2.stats().total_proposed >= runner1.stats().total_proposed);
    std::puts("T5 gamma_propagation PASS");
}

static void t6_eos_termination() {
    DraftStubMtpModule mod;
    SuccessStubTarget tgt;
    tgt.argmax_token = 42;
    tgt.eos_token_id = 42;
    dflash::common::mtp::MtpChainRunner runner(mod, tgt, {});
    dflash::common::GenerateRequest req;
    req.n_gen = 100;
    dflash::common::DaemonIO io;
    auto res = runner.run(req, io, 10, 4, 1);
    assert(res.ok);
    assert(runner.stats().eos_hits == 1);
    assert(runner.stats().total_emitted == 1);
    std::puts("T6 eos_termination PASS");
}

static void t7_partial_accept_rollback() {
    DraftStubMtpModule mod;
    SuccessStubTarget tgt;
    tgt.accept_n = 1;
    tgt.argmax_token = 55;
    dflash::common::mtp::MtpChainRunner runner(mod, tgt, {});
    dflash::common::GenerateRequest req;
    req.n_gen = 2;
    dflash::common::DaemonIO io;
    auto res = runner.run(req, io, 10, 4, 2);
    assert(res.ok);
    assert(runner.stats().total_accepted >= 1);
    assert(tgt.restore_kv_at_chain_calls >= 1);
    std::puts("T7 partial_accept_rollback PASS");
}

static void t8_n_gen_termination() {
    DraftStubMtpModule mod;
    SuccessStubTarget tgt;
    tgt.argmax_token = 77;
    dflash::common::mtp::MtpChainRunner runner(mod, tgt, {});
    dflash::common::GenerateRequest req;
    req.n_gen = 5;
    dflash::common::DaemonIO io;
    auto res = runner.run(req, io, 10, 4, 1);
    assert(res.ok);
    assert((int)res.tokens.size() == 5);
    assert(runner.stats().total_emitted == 5);
    std::puts("T8 n_gen_termination PASS");
}

static void t9_propose_failure() {
    FailStepChainMtpModule mod;
    SuccessStubTarget tgt;
    dflash::common::mtp::MtpChainRunner runner(mod, tgt, {});
    dflash::common::GenerateRequest req;
    req.n_gen = 4;
    dflash::common::DaemonIO io;
    auto res = runner.run(req, io, 10, 4, 1);
    assert(!res.ok);
    assert(res.error.find("propose") != std::string::npos);
    std::puts("T9 propose_failure PASS");
}

static void t10_stats_accounting() {
    DraftStubMtpModule mod;
    SuccessStubTarget tgt;
    tgt.accept_n = 1;
    dflash::common::mtp::MtpChainRunner runner(mod, tgt, {});
    dflash::common::GenerateRequest req;
    req.n_gen = 6;
    dflash::common::DaemonIO io;
    auto res = runner.run(req, io, 10, 4, 2);
    assert(res.ok);
    const auto & st = runner.stats();
    assert(st.total_emitted == st.total_accepted + st.total_iters);
    std::puts("T10 stats_accounting PASS");
}

static void t11_reset_chain_before_drive() {
    LiveStubBackend b;
    b.mtp_mod.effective_gamma_value = 1;
    dflash::common::GenerateRequest req;
    req.prompt = {1, 2, 3};
    req.n_gen = 2;
    dflash::common::DaemonIO io;
    auto res = dflash::common::mtp::warm_and_decode(&b, req, io);
    assert(res.ok);
    assert(b.mtp_mod.reset_chain_calls >= 1);
    std::puts("T11 reset_chain_before_drive PASS");
}

static void t12_set_initial_hidden_plumbing() {
    LiveStubBackend b;
    b.mtp_mod.effective_gamma_value = 1;
    dflash::common::GenerateRequest req;
    req.prompt = {5, 6, 7, 8};
    req.n_gen = 1;
    dflash::common::DaemonIO io;
    auto res = dflash::common::mtp::warm_and_decode(&b, req, io);
    assert(res.ok);
    assert(b.mtp_mod.set_initial_hidden_calls >= 1);
    std::puts("T12 set_initial_hidden_plumbing PASS");
}

static void t13_gamma_derived_from_module() {
    LiveStubBackend b;
    b.mtp_mod.effective_gamma_value = 2;
    dflash::common::GenerateRequest req;
    req.prompt = {1, 2};
    req.n_gen = 3;
    dflash::common::DaemonIO io;
    auto res = dflash::common::mtp::warm_and_decode(&b, req, io);
    assert(res.ok);
    assert(res.tokens.size() >= 1);
    std::puts("T13 gamma_derived_from_module PASS");
}

static void t14_zero_gamma_rejected() {
    LiveStubBackend b;
    b.mtp_mod.effective_gamma_value = 0;
    dflash::common::GenerateRequest req;
    req.prompt = {1, 2, 3};
    req.n_gen = 4;
    dflash::common::DaemonIO io;
    auto res = dflash::common::mtp::warm_and_decode(&b, req, io);
    assert(!res.ok);
    assert(res.error.find("effective_gamma") != std::string::npos);
    std::puts("T14 zero_gamma_rejected PASS");
}

static void t15_external_drafter_partial_accept_threads_committed_row() {
    StubExternalDrafter ext;
    ExternalPartialTarget target;
    target.argmax_token = ExternalPartialTarget::kDivergeToken;
    target.hidden_sz = ext.hidden_size_value;
    dflash::common::mtp::MtpChainRunner runner(ext, target, {});
    dflash::common::GenerateRequest req;
    req.n_gen = 2;
    dflash::common::DaemonIO io;
    auto res = runner.run(req, io, 10, 4, 2);
    assert(res.ok);
    assert(ext.set_capture_row_calls > 0);
    assert(ext.set_capture_row_last_arg == 1);
    assert(ext.consume_calls > 0);
    assert(ext.consume_after_set_capture);
    std::puts("T15 external_drafter_partial_accept_threads_committed_row PASS");
}

int main() {
    t1_null_backend();
    t2_backend_without_mtp();
    t3_empty_prompt();
    t4_generic_backend_dispatch();
    t5_gamma_propagation();
    t6_eos_termination();
    t7_partial_accept_rollback();
    t8_n_gen_termination();
    t9_propose_failure();
    t10_stats_accounting();
    t11_reset_chain_before_drive();
    t12_set_initial_hidden_plumbing();
    t13_gamma_derived_from_module();
    t14_zero_gamma_rejected();
    t15_external_drafter_partial_accept_threads_committed_row();
    std::puts("ALL PASS");
    return 0;
}
