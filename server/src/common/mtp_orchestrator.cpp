#include "mtp_orchestrator.h"

#include "dflash_target.h"
#include "mtp_chain_runner.h"

#include <algorithm>
#include <chrono>
#include <cstdlib>
#include <cstring>
#include <vector>

namespace dflash::common::mtp {

namespace {

constexpr int kDefaultPrefillUbatch = 512;

int env_int(const char * name, int defv) {
    if (const char * s = std::getenv(name)) {
        const int v = std::atoi(s);
        if (v > 0) return v;
    }
    return defv;
}

}  // namespace

GenerateResult warm_and_decode(ModelBackend * backend,
                                const GenerateRequest & req,
                                const DaemonIO & io_in) {
    const DaemonIO io = io_in.with_token_callback(req.on_token);

    GenerateResult result;
    if (!backend) {
        result.error = "warm_and_decode: backend pointer is null";
        return result;
    }
    if (!backend->supports_mtp()) {
        result.error = "warm_and_decode: backend does not support MTP";
        return result;
    }
    if (req.prompt.empty()) {
        result.error = "warm_and_decode: prompt is empty";
        return result;
    }

    IMtpModule * module = backend->mtp();
    DFlashTarget * target = backend->dflash_target();
    if (!module || !target) {
        result.error = "warm_and_decode: backend missing mtp() or dflash_target()";
        return result;
    }

    const int hidden = target->hidden_size();
    const int prompt_len = (int)req.prompt.size();
    const int prefill_ubatch = env_int("DFLASH27B_PREFILL_UBATCH",
                                       kDefaultPrefillUbatch);

    target->enable_hidden_seq_capture(true);

    std::vector<float> all_prefill_hidden((size_t)prompt_len * hidden);
    int32_t last_tok = -1;

    const auto t_prefill0 = std::chrono::steady_clock::now();
    for (int start = 0; start < prompt_len;) {
        const int n = std::min(prefill_ubatch, prompt_len - start);
        std::vector<int32_t> chunk(req.prompt.begin() + start,
                                   req.prompt.begin() + start + n);
        if (!target->verify_batch(chunk, start, last_tok, nullptr)) {
            target->enable_hidden_seq_capture(false);
            result.error = "warm_and_decode: verify_batch failed during prefill";
            io.emit(-1);
            return result;
        }

        int n_chunk = 0;
        const float * h_seq = target->last_hidden_seq(&n_chunk);
        if (!h_seq || n_chunk != n) {
            target->enable_hidden_seq_capture(false);
            result.error = "warm_and_decode: hidden seq capture invariant violated";
            io.emit(-1);
            return result;
        }

        std::memcpy(all_prefill_hidden.data() + (size_t)start * hidden,
                    h_seq, sizeof(float) * (size_t)n * hidden);
        start += n;
    }

    result.prefill_s = std::chrono::duration<double>(
        std::chrono::steady_clock::now() - t_prefill0).count();

    if (last_tok < 0) {
        target->enable_hidden_seq_capture(false);
        result.error = "warm_and_decode: prefill produced invalid argmax";
        io.emit(-1);
        return result;
    }

    module->reset_chain();
    if (target->last_hidden()) {
        module->set_initial_hidden(target->last_hidden(), hidden);
    }

    if (module->flavor() == MtpFlavor::NativeHeads) {
        auto * native = static_cast<INativeMtp *>(module);
        if (!native->warm_head_kv(req.prompt.data(), prompt_len,
                                  last_tok, all_prefill_hidden.data())) {
            target->enable_hidden_seq_capture(false);
            result.error = "warm_and_decode: warm_head_kv failed";
            io.emit(-1);
            return result;
        }
    }

    result.tokens.push_back(last_tok);
    io.emit(last_tok);
    if (target->is_eos(last_tok) || req.n_gen <= 1) {
        target->enable_hidden_seq_capture(false);
        io.emit(-1);
        result.ok = true;
        return result;
    }

    const int gamma = module->effective_gamma();
    if (gamma <= 0) {
        target->enable_hidden_seq_capture(false);
        result.error = "warm_and_decode: module->effective_gamma() == 0";
        io.emit(-1);
        return result;
    }

    GenerateRequest inner = req;
    inner.n_gen = req.n_gen - 1;
    inner.stream = true;
    inner.do_sample = false;

    const auto t_decode0 = std::chrono::steady_clock::now();
    MtpChainRunner runner(*module, *target, req.sampler);
    GenerateResult inner_res = runner.run(inner, io, last_tok, prompt_len, gamma);
    result.decode_s = std::chrono::duration<double>(
        std::chrono::steady_clock::now() - t_decode0).count();

    target->enable_hidden_seq_capture(false);

    if (!inner_res.ok) {
        result.error = "warm_and_decode: chain runner failed: " + inner_res.error;
        io.emit(-1);
        return result;
    }

    for (int32_t token : inner_res.tokens) result.tokens.push_back(token);
    result.ok = true;
    return result;
}

}  // namespace dflash::common::mtp
