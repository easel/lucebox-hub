#include "mtp_chain_runner.h"

#include "dflash_target.h"

#include <algorithm>
#include <chrono>
#include <cstdio>

namespace dflash::common::mtp {

MtpChainRunner::MtpChainRunner(IMtpModule & mtp,
                               DFlashTarget & target,
                               const SamplerCfg & sampler)
    : mtp_(mtp), target_(target), sampler_cfg_(sampler) {}

bool MtpChainRunner::propose_drafts_(int32_t current_token,
                                     int base_pos,
                                     int gamma,
                                     const float * prev_hidden,
                                     int prev_hidden_dim,
                                     std::vector<int32_t> & drafts_out,
                                     std::vector<float> & next_hidden_out) {
    drafts_out.clear();
    drafts_out.reserve(gamma);

    if (mtp_.flavor() == MtpFlavor::NativeHeads) {
        auto & native = static_cast<INativeMtp &>(mtp_);
        std::vector<StepOutput> outs;
        if (!native.step_chain(current_token, base_pos, gamma, outs)) return false;
        const int take = std::min(gamma, (int)outs.size());
        for (int i = 0; i < take; ++i) drafts_out.push_back(outs[i].draft_token);
        next_hidden_out.clear();
        return true;
    }

    auto & ext = static_cast<IExternalDrafterMtp &>(mtp_);
    const int hidden = mtp_.hidden_size();

    std::vector<float> running_hidden;
    if (prev_hidden && prev_hidden_dim == hidden) {
        running_hidden.assign(prev_hidden, prev_hidden + hidden);
    }

    int32_t cur = current_token;
    for (int g = 0; g < gamma; ++g) {
        StepInput in;
        in.current_token = cur;
        in.base_pos = base_pos;
        in.gamma_index = g;
        in.prev_hidden = running_hidden.empty() ? nullptr : running_hidden.data();
        in.prev_hidden_dim = (int)running_hidden.size();

        StepOutput out;
        if (!ext.step(in, out)) return false;

        drafts_out.push_back(out.draft_token);
        cur = out.draft_token;
        if (!out.next_hidden.empty()) running_hidden = std::move(out.next_hidden);
    }

    next_hidden_out = std::move(running_hidden);
    return true;
}

GenerateResult MtpChainRunner::run(const GenerateRequest & req,
                                   const DaemonIO & io,
                                   int32_t last_prefill_token,
                                   int committed_pos,
                                   int gamma) {
    GenerateResult result;
    if (req.n_gen <= 0) {
        result.ok = true;
        return result;
    }

    const int gamma_max = std::max(1, mtp_.max_gamma());
    if (gamma > gamma_max) {
        std::fprintf(stderr,
            "[mtp_chain_runner] gamma=%d > module max_gamma=%d; clamping.\n",
            gamma, gamma_max);
        gamma = gamma_max;
    }
    if (gamma < 1) gamma = 1;

    const auto t0 = std::chrono::steady_clock::now();
    result.tokens.reserve(req.n_gen);

    int32_t cur_tok = last_prefill_token;
    int base_pos = committed_pos;
    std::vector<float> running_hidden;
    bool hit_eos = false;

    struct ChainCaptureGuard {
        DFlashTarget & target;
        ~ChainCaptureGuard() { target.enable_chain_capture(false); }
    };
    target_.enable_chain_capture(true);
    ChainCaptureGuard guard{target_};

    while ((int)result.tokens.size() < req.n_gen && !hit_eos) {
        const int remaining = req.n_gen - (int)result.tokens.size();
        const int g_iter = std::min(gamma, remaining);

        std::vector<int32_t> drafts;
        std::vector<float> next_hidden;
        if (!propose_drafts_(cur_tok, base_pos, g_iter,
                             running_hidden.empty() ? nullptr : running_hidden.data(),
                             (int)running_hidden.size(),
                             drafts, next_hidden)) {
            result.error = "mtp.propose";
            return result;
        }

        const int g_actual = (int)drafts.size();
        stats_.total_proposed += g_actual;

        std::vector<int32_t> candidate;
        candidate.reserve((size_t)g_actual + 1);
        candidate.push_back(cur_tok);
        for (int32_t draft : drafts) candidate.push_back(draft);

        if (!target_.snapshot_kv()) {
            result.error = "snapshot_kv";
            return result;
        }

        target_.capture_topology_for_chain((int)candidate.size(), base_pos);

        int last_argmax = -1;
        std::vector<int32_t> all_argmax;
        if (!target_.verify_batch(candidate, base_pos, last_argmax, &all_argmax)) {
            target_.restore_kv();
            result.error = "verify_batch";
            return result;
        }
        if ((int)all_argmax.size() < (int)candidate.size()) {
            target_.restore_kv();
            result.error = "verify_batch_short";
            return result;
        }

        int accept_n = 0;
        for (int i = 0; i < g_actual; ++i) {
            if (drafts[i] == all_argmax[i]) ++accept_n;
            else break;
        }

        const int total_this_iter = accept_n + 1;

        if (accept_n < g_actual) {
            if (!target_.restore_kv_at_chain(accept_n)) {
                if (!target_.restore_kv()) {
                    result.error = "restore_kv";
                    return result;
                }

                std::vector<int32_t> commit_seq;
                commit_seq.reserve((size_t)accept_n + 1);
                commit_seq.push_back(cur_tok);
                for (int i = 0; i < accept_n; ++i) commit_seq.push_back(drafts[i]);

                int discard = -1;
                if (!target_.verify_batch(commit_seq, base_pos, discard, nullptr)) {
                    result.error = "recommit";
                    return result;
                }
            }
        }

        const int emit_cap = std::min(total_this_iter,
                                      req.n_gen - (int)result.tokens.size());
        int emitted = 0;
        for (int i = 0; i < accept_n && emitted < emit_cap; ++i) {
            result.tokens.push_back(drafts[i]);
            if (req.stream) io.emit(drafts[i]);
            ++emitted;
            if (target_.is_eos(drafts[i])) {
                hit_eos = true;
                break;
            }
        }
        if (!hit_eos && emitted < emit_cap) {
            const int32_t bonus = all_argmax[accept_n];
            result.tokens.push_back(bonus);
            if (req.stream) io.emit(bonus);
            ++emitted;
            if (target_.is_eos(bonus)) hit_eos = true;
            cur_tok = bonus;
        } else {
            cur_tok = result.tokens.empty() ? cur_tok : result.tokens.back();
        }

        base_pos += total_this_iter;
        stats_.total_iters += 1;
        stats_.total_accepted += accept_n;
        stats_.total_emitted += emitted;

        if (mtp_.flavor() == MtpFlavor::ExternalDrafter && !next_hidden.empty()) {
            auto & ext = static_cast<IExternalDrafterMtp &>(mtp_);
            const int hidden = mtp_.hidden_size();
            ext.set_capture_row(accept_n);
            std::vector<float> boundary_hidden((size_t)hidden);
            if (ext.consume_captured_hidden(boundary_hidden.data(), hidden)) {
                running_hidden = std::move(boundary_hidden);
            } else {
                running_hidden = std::move(next_hidden);
            }
        } else {
            running_hidden = std::move(next_hidden);
        }
    }

    if (hit_eos) ++stats_.eos_hits;
    if (req.stream) io.emit(-1);

    result.decode_s = std::chrono::duration<double>(
        std::chrono::steady_clock::now() - t0).count();
    result.ok = true;
    return result;
}

}  // namespace dflash::common::mtp
